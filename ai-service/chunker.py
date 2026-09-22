import os
from typing import List, Dict, Any
from langchain_text_splitters import RecursiveCharacterTextSplitter, Language
from langchain_core.documents import Document
from github_loader import fetch_repo_tree, fetch_file_content, parse_github_url

# Map file extensions to LangChain Language enum
EXTENSION_TO_LANGUAGE = {
    ".js": Language.JS,
    ".jsx": Language.JS,
    ".ts": Language.TS,
    ".tsx": Language.TS,
    ".py": Language.PYTHON,
    ".java": Language.JAVA,
    ".cpp": Language.CPP,
    ".c": Language.CPP,
    ".h": Language.CPP,
    ".html": Language.HTML,
    ".md": Language.MARKDOWN,
    ".php": Language.PHP,
    ".go": Language.GO,
    ".rs": Language.RUST,
    ".rb": Language.RUBY,
}

def get_language_for_extension(ext: str) -> Language:
    return EXTENSION_TO_LANGUAGE.get(ext.lower())

def calculate_line_numbers(full_text: str, chunk_text: str, start_search_index: int = 0) -> tuple[int, int, int]:
    """
    Finds the approximate start and end line of chunk_text within full_text.
    Returns (start_line, end_line, next_search_index)
    """
    # Find where the chunk starts in the original string
    chunk_index = full_text.find(chunk_text, start_search_index)
    
    if chunk_index == -1:
        # Fallback if text was somehow heavily modified by the splitter
        chunk_index = full_text.find(chunk_text)
        if chunk_index == -1:
            return 1, 1, start_search_index
            
    # Calculate start line by counting newlines before the chunk
    start_line = full_text.count("\n", 0, chunk_index) + 1
    
    # Calculate end line by counting newlines within the chunk
    end_line = start_line + chunk_text.count("\n")
    
    return start_line, end_line, chunk_index + len(chunk_text)

def chunk_file(content: str, repository_id: str, file_path: str) -> List[Document]:
    """
    Splits file content into chunks, preserving line numbers and metadata.
    """
    _, ext = os.path.splitext(file_path)
    lang = get_language_for_extension(ext)
    
    # Determine chunk type
    chunk_type = "doc" if ext.lower() in [".md", ".txt"] else "code"
    
    # Initialize the appropriate text splitter
    if lang:
        splitter = RecursiveCharacterTextSplitter.from_language(
            language=lang,
            chunk_size=1000,
            chunk_overlap=200
        )
    else:
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200
        )
        
    # Split the text
    texts = splitter.split_text(content)
    documents = []
    
    start_search_index = 0
    for text in texts:
        start_line, end_line, start_search_index = calculate_line_numbers(content, text, start_search_index)
        
        # Build metadata payload matching SRS requirements
        metadata = {
            "repository_id": repository_id,
            "file_path": file_path,
            "language": lang.value if lang else "unknown",
            "chunk_type": chunk_type,
            "start_line": start_line,
            "end_line": end_line
        }
        
        documents.append(Document(page_content=text, metadata=metadata))
        
    return documents

def process_repository(url: str) -> List[Document]:
    """
    Orchestrates the fetching and chunking of an entire repository.
    """
    owner, repo = parse_github_url(url)
    repository_id = f"{owner}/{repo}"
    
    print(f"Fetching repository tree for {repository_id}...")
    files = fetch_repo_tree(owner, repo)
    print(f"Found {len(files)} files to process.")
    
    all_documents = []
    
    for i, file_item in enumerate(files):
        file_path = file_item["path"]
        print(f"[{i+1}/{len(files)}] Processing {file_path}...")
        
        try:
            content = fetch_file_content(owner, repo, file_path)
            chunks = chunk_file(content, repository_id, file_path)
            all_documents.extend(chunks)
        except Exception as e:
            print(f"Failed to process {file_path}: {e}")
            
    return all_documents

if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))
    
    test_url = "https://github.com/expressjs/express"
    
    try:
        # In this test we will just process one file instead of the whole repo
        # to avoid long wait times.
        owner, repo = parse_github_url(test_url)
        files = fetch_repo_tree(owner, repo)
        
        if files:
            sample_file = files[0]["path"]
            print(f"Fetching and chunking sample file: {sample_file}")
            
            content = fetch_file_content(owner, repo, sample_file)
            chunks = chunk_file(content, f"{owner}/{repo}", sample_file)
            
            print(f"Generated {len(chunks)} chunks.")
            if chunks:
                print("\nSample Chunk Metadata:")
                print(chunks[0].metadata)
                print("\nSample Chunk Content (first 200 chars):")
                print("-" * 40)
                print(chunks[0].page_content[:200])
                print("-" * 40)
                
    except Exception as e:
        print(f"Error: {e}")
