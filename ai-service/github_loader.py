import os
import requests
from typing import List, Dict, Any

# Files and directories to ignore based on SRS requirements
IGNORED_DIRS = {
    ".git", "node_modules", "venv", ".venv", "dist", "build", 
    "__pycache__", "coverage", "out"
}
IGNORED_FILES = {
    ".env", "package-lock.json", "yarn.lock", "pnpm-lock.yaml"
}
IGNORED_EXTENSIONS = {
    ".png", ".jpg", ".jpeg", ".gif", ".ico", ".svg", ".pdf",
    ".zip", ".tar", ".gz", ".mp4", ".mov", ".woff", ".woff2", ".ttf", ".eot"
}

def parse_github_url(url: str) -> tuple[str, str]:
    """
    Extracts owner and repo from a standard GitHub URL.
    Example: https://github.com/owner/repo -> (owner, repo)
    """
    url = url.rstrip("/")
    parts = url.split("/")
    if len(parts) >= 2:
        return parts[-2], parts[-1]
    raise ValueError("Invalid GitHub URL provided.")

def should_ignore_file(filepath: str) -> bool:
    """
    Determines if a file should be ignored based on its path or extension.
    """
    parts = filepath.split("/")
    
    # Check if any directory in the path should be ignored
    for part in parts[:-1]:
        if part in IGNORED_DIRS:
            return True
            
    filename = parts[-1]
    if filename in IGNORED_FILES:
        return True
        
    _, ext = os.path.splitext(filename)
    if ext.lower() in IGNORED_EXTENSIONS:
        return True
        
    return False

def get_headers() -> Dict[str, str]:
    """Returns headers with GitHub token if available to avoid rate limits."""
    headers = {"Accept": "application/vnd.github.v3+json"}
    token = os.getenv("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"token {token}"
    return headers

def fetch_repo_tree(owner: str, repo: str) -> List[Dict[str, Any]]:
    """
    Retrieves the repository tree using the GitHub API (recursive).
    """
    headers = get_headers()
    
    # First, get the default branch
    repo_url = f"https://api.github.com/repos/{owner}/{repo}"
    repo_response = requests.get(repo_url, headers=headers)
    
    if repo_response.status_code != 200:
        raise Exception(f"Failed to fetch repository metadata: {repo_response.text}")
        
    default_branch = repo_response.json().get("default_branch", "main")
    
    # Fetch the recursive tree
    tree_url = f"https://api.github.com/repos/{owner}/{repo}/git/trees/{default_branch}?recursive=1"
    tree_response = requests.get(tree_url, headers=headers)
    
    if tree_response.status_code != 200:
        raise Exception(f"Failed to fetch repository tree: {tree_response.text}")
        
    tree_data = tree_response.json().get("tree", [])
    
    # Filter files
    files = []
    for item in tree_data:
        if item["type"] == "blob":
            filepath = item["path"]
            if not should_ignore_file(filepath):
                files.append(item)
                
    return files

def fetch_file_content(owner: str, repo: str, file_path: str) -> str:
    """
    Retrieves the raw content of a file from GitHub.
    """
    headers = get_headers()
    raw_url = f"https://raw.githubusercontent.com/{owner}/{repo}/HEAD/{file_path}"
    
    response = requests.get(raw_url, headers=headers)
    if response.status_code == 200:
        return response.text
    else:
        # Fallback to API if raw content isn't accessible (e.g. strict enterprise policies)
        api_url = f"https://api.github.com/repos/{owner}/{repo}/contents/{file_path}"
        api_response = requests.get(api_url, headers=headers)
        if api_response.status_code == 200:
            import base64
            content_b64 = api_response.json().get("content", "")
            return base64.b64decode(content_b64).decode('utf-8', errors='ignore')
        
    raise Exception(f"Failed to fetch file {file_path}: {response.status_code}")

if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))
    
    print("Testing GitHub Loader...")
    test_url = "https://github.com/expressjs/express"
    owner, repo = parse_github_url(test_url)
    
    print(f"Fetching tree for {owner}/{repo}...")
    try:
        files = fetch_repo_tree(owner, repo)
        print(f"Found {len(files)} valid files.")
        
        if files:
            sample_file = files[0]["path"]
            print(f"Fetching content for sample file: {sample_file}")
            content = fetch_file_content(owner, repo, sample_file)
            print("Content sample (first 200 chars):")
            print("-" * 40)
            print(content[:200])
            print("-" * 40)
            
    except Exception as e:
        print(f"Error: {e}")
