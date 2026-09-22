# GitHub Codebase Intelligence Agent — Software Requirements Specification (SRS)

**Version:** 1.0  
**Status:** Initial project specification  
**Project type:** Portfolio / interview project  
**Primary goal:** Demonstrate practical RAG, agent/tool-calling, vector search, LLM integration, and full-stack engineering using technologies the developer already knows.

---

## 1. Project Overview

### 1.1 Project Name

**GitHub Codebase Intelligence Agent**

### 1.2 One-line description

An AI-powered assistant that ingests a GitHub repository, indexes its code and documentation, and uses RAG plus an agent with code-analysis tools to answer questions about the codebase with file-level source references.

### 1.3 Problem Statement

Understanding an unfamiliar codebase requires manually navigating files, searching for symbols, reading related modules, and tracing how components interact.

The project will provide a conversational interface where a developer can ask questions such as:

- "Where is authentication implemented?"
- "Explain how user registration works."
- "Where is the database connection created?"
- "What happens when `/users/:id` is called?"
- "Which files are responsible for authentication?"
- "Explain this error using the repository."
- "How do I run this project?"
- "What dependencies does this project use?"

The system should retrieve relevant repository content and, when necessary, let an agent decide which tools to invoke before producing the final answer.

---

# 2. Goals and Objectives

## 2.1 Primary Goals

1. Accept a public GitHub repository URL.
2. Retrieve repository files and metadata.
3. Filter irrelevant/binary/generated files.
4. Parse source code and documentation.
5. Split content into useful chunks.
6. Generate embeddings using HuggingFace.
7. Store vectors and metadata in Qdrant.
8. Implement basic RAG retrieval.
9. Implement an agent capable of selecting tools.
10. Provide at least three useful agent tools.
11. Support both:
   - Local Ollama LLM
   - Groq API LLM
12. Provide a React chat interface.
13. Show sources/file references for generated answers.
14. Keep the architecture simple enough to explain completely in an interview.

## 2.2 Secondary Goals

- Allow re-indexing of a repository.
- Show repository/file structure in the UI.
- Show retrieved source files beside answers.
- Maintain conversation context during a session.
- Make the LLM provider replaceable without changing the RAG architecture.
- Provide useful error messages when indexing or answering fails.

## 2.3 Non-goals for Version 1

The first version will NOT attempt to:

- Automatically modify repository files.
- Push commits to GitHub.
- Execute arbitrary repository code.
- Run shell commands from user prompts.
- Deploy repositories.
- Support private repositories unless authentication is explicitly added later.
- Build a multi-agent swarm.
- Use unnecessary databases/services.
- Guarantee perfect code understanding.
- Replace a full IDE.

---

# 3. Target Users

## Primary User

Developers who need to understand an unfamiliar GitHub repository.

## Secondary User

Interviewers evaluating knowledge of:

- RAG
- Vector databases
- Embeddings
- LLMs
- Agents
- Tool calling
- REST APIs
- React
- Backend architecture

---

# 4. Technology Stack

| Layer | Technology |
|---|---|
| Frontend | React |
| Main backend | Node.js + Express |
| AI backend | Python + FastAPI |
| Agent/RAG framework | LangChain |
| Vector database | Qdrant |
| Embeddings | HuggingFace |
| Local LLM | Ollama |
| Local model | Mistral 7B or another locally available model |
| Cloud LLM | Groq API |
| Repository source | GitHub API / GitHub repository contents |
| Communication | REST / JSON |
| Version control | Git + GitHub |

## 4.1 Why Two Backends?

Express will act as the application backend and GitHub-facing API layer.

FastAPI will expose the Python-based AI pipeline because the project already uses Python libraries for:

- LangChain
- HuggingFace embeddings
- Qdrant integration
- Agent implementation
- LLM integration

Architecture:

```text
React
  |
  v
Express
  |
  +---- GitHub integration
  |
  +---- Repository/session APIs
  |
  +---- Chat request forwarding
              |
              v
          FastAPI AI Service
              |
              +---- Agent
              +---- RAG
              +---- Qdrant
              +---- HuggingFace
              +---- Ollama/Groq
```

---

# 5. High-Level Architecture

```text
                         +----------------------+
                         |      React UI        |
                         |                      |
                         | Chat / Repo Explorer |
                         | Sources / Status     |
                         +----------+-----------+
                                    |
                               HTTP / JSON
                                    |
                                    v
                         +----------------------+
                         |    Express Server    |
                         |                      |
                         | GitHub integration   |
                         | Repo management      |
                         | Session management   |
                         | Chat API             |
                         +----------+-----------+
                                    |
                         +----------+-----------+
                         |                      |
                         v                      v
                +----------------+     +----------------+
                |   GitHub API   |     |  FastAPI AI    |
                |                |     |    Service     |
                +----------------+     +-------+--------+
                                               |
                                    +----------+----------+
                                    |                     |
                                    v                     v
                              +-----------+         +-----------+
                              |   Agent   |         |   RAG     |
                              +-----+-----+         +-----+-----+
                                    |                     |
                         +----------+---------+           |
                         |          |         |           v
                         v          v         v       +--------+
                    search_code  read_file  search_docs |Qdrant|
                         |          |         |       +--------+
                         +----------+---------+           |
                                    |                     |
                                    +----------+----------+
                                               |
                                               v
                                       +---------------+
                                       | LLM Provider  |
                                       +-------+-------+
                                               |
                                  +------------+------------+
                                  |                         |
                                  v                         v
                              Ollama                      Groq
```

---

# 6. Core System Components

## 6.1 React Frontend

Responsibilities:

- Repository URL input
- Indexing status
- Repository file explorer
- Chat interface
- Conversation display
- Source display
- Error/status messages
- LLM provider selection
- Loading states

The UI should not directly communicate with Qdrant or the LLM.

---

## 6.2 Express Backend

Responsibilities:

- Validate GitHub URLs
- Start repository ingestion
- Communicate with GitHub
- Maintain repository metadata
- Forward AI/chat requests to FastAPI
- Manage session-level application state
- Provide frontend-friendly REST endpoints

Express should not contain the core Python RAG implementation.

---

## 6.3 FastAPI AI Service

Responsibilities:

- Receive AI requests from Express
- Run ingestion pipeline when requested
- Create embeddings
- Store/retrieve vectors
- Execute RAG pipeline
- Execute agent
- Invoke tools
- Call Ollama or Groq
- Return generated answer and sources

---

# 7. Repository Ingestion Pipeline

## 7.1 Input

Example:

```text
https://github.com/username/repository
```

## 7.2 Processing Flow

```text
GitHub URL
    |
    v
Validate repository
    |
    v
Fetch repository tree/files
    |
    v
Filter files
    |
    v
Load supported files
    |
    v
Add metadata
    |
    v
Code-aware/document chunking
    |
    v
HuggingFace embeddings
    |
    v
Qdrant
```

## 7.3 Supported Initial File Types

Initial support:

```text
.js
.jsx
.ts
.tsx
.py
.java
.cpp
.c
.h
.html
.css
.json
.md
.txt
.yml
.yaml
.xml
```

This list can expand later.

## 7.4 Files to Ignore

At minimum:

```text
.git/
node_modules/
venv/
.venv/
dist/
build/
__pycache__/
coverage/
.env
*.lock
large binaries
images
videos
archives
```

The exact ignore policy should be configurable later.

---

# 8. Chunking Strategy

The system should avoid treating an entire repository as one document.

For source code:

- Prefer function/class/module-aware chunks where practical.
- Preserve filename and language metadata.
- Preserve line ranges when available.
- Keep related code together where possible.

For Markdown/text:

- Use heading-aware and recursive text splitting.

Example chunk metadata:

```json
{
  "repository": "my-project",
  "file_path": "routes/users.js",
  "language": "javascript",
  "chunk_type": "code",
  "symbol": "router.post",
  "start_line": 12,
  "end_line": 27
}
```

---

# 9. Embedding Layer

Use:

**HuggingFace embedding model**

The initial familiar model may be:

```text
sentence-transformers/all-MiniLM-L6-v2
```

Responsibilities:

- Convert chunks into vectors.
- Convert user queries into vectors.
- Ensure the same embedding model is used for indexing and retrieval.

Important requirement:

> The embedding model used for repository ingestion and query retrieval must remain compatible.

---

# 10. Qdrant Vector Database

Qdrant will store:

- Vector embeddings
- Chunk text
- Repository identifier
- File path
- Language
- Chunk type
- Symbol/function/class metadata
- Line range
- Optional commit/version information

Conceptual payload:

```json
{
  "repository_id": "owner/repo",
  "file_path": "middleware/auth.js",
  "language": "javascript",
  "chunk_type": "code",
  "start_line": 1,
  "end_line": 30,
  "content": "..."
}
```

Each repository should be logically isolated.

Possible strategy:

```text
Collection:
github_codebase

Payload:
repository_id = owner/repo
```

or separate collections per repository.

For Version 1, a single collection with repository filtering is sufficient.

---

# 11. RAG Pipeline

## 11.1 Query Flow

```text
User question
      |
      v
Create query embedding
      |
      v
Qdrant similarity search
      |
      v
Filter by repository
      |
      v
Top-K relevant chunks
      |
      v
Construct context
      |
      v
LLM
      |
      v
Answer + sources
```

## 11.2 Retrieval Requirements

The retriever should:

- Search only the selected repository.
- Return configurable Top-K results.
- Include metadata.
- Return source file paths.
- Avoid exposing unrelated repositories.

Initial Top-K:

```text
k = 5
```

This can be tuned later.

---

# 12. Agent Architecture

The agent is not simply a chatbot with retrieval.

The agent receives a user request and decides whether it needs tools.

## 12.1 Initial Tools

### Tool 1: `search_code`

Purpose:

Perform semantic search across indexed repository content.

Input:

```text
query
repository_id
```

Output:

Relevant chunks + metadata.

---

### Tool 2: `read_file`

Purpose:

Retrieve a complete or bounded section of a repository file.

Input:

```text
repository_id
file_path
```

Output:

File content.

This is important because semantic retrieval may only return fragments.

---

### Tool 3: `search_docs`

Purpose:

Search README/documentation/configuration content.

Input:

```text
repository_id
query
```

Output:

Relevant documentation chunks.

---

# 13. Example Agent Execution

User:

> "Explain how authentication works."

Possible agent workflow:

```text
User question
      |
      v
Agent
      |
      v
Needs code investigation
      |
      v
search_code(
  "authentication JWT login middleware"
)
      |
      v
Find:
middleware/auth.js
controllers/auth.js
routes/auth.js
      |
      v
read_file("middleware/auth.js")
      |
      v
read_file("controllers/auth.js")
      |
      v
Generate answer
```

The agent should only call additional tools when needed.

---

# 14. LLM Provider Abstraction

The project supports two providers.

## 14.1 Ollama

Use when:

- Running locally
- Offline/private demonstration is desired
- Avoiding API costs
- Demonstrating local LLM usage

Example:

```text
Ollama
  |
  v
Mistral 7B
```

## 14.2 Groq

Use when:

- Faster responses are desired
- Local hardware is insufficient
- Demonstrating cloud LLM integration

The application should expose a provider setting:

```text
LLM_PROVIDER=ollama
```

or:

```text
LLM_PROVIDER=groq
```

The RAG and agent code should not be duplicated for each provider.

---

# 15. API Design

## Express APIs

### `POST /api/repositories`

Register a repository.

Request:

```json
{
  "url": "https://github.com/owner/repo"
}
```

Response:

```json
{
  "repositoryId": "owner/repo",
  "status": "registered"
}
```

---

### `POST /api/repositories/:id/index`

Start indexing.

Response:

```json
{
  "repositoryId": "owner/repo",
  "status": "indexing"
}
```

---

### `GET /api/repositories/:id/status`

Returns indexing status.

Example:

```json
{
  "status": "completed",
  "files": 82,
  "chunks": 643
}
```

---

### `GET /api/repositories/:id/files`

Returns indexed repository file structure.

---

### `POST /api/chat`

Request:

```json
{
  "repositoryId": "owner/repo",
  "message": "Where is authentication implemented?",
  "provider": "ollama"
}
```

Response:

```json
{
  "answer": "...",
  "sources": [
    {
      "file": "middleware/auth.js",
      "startLine": 1,
      "endLine": 30
    }
  ]
}
```

---

# 16. FastAPI APIs

FastAPI is an internal AI service.

### `POST /ai/index`

Receives repository content/metadata or an ingestion request and runs the indexing pipeline.

### `POST /ai/chat`

Runs the RAG/agent pipeline.

### `POST /ai/search`

Runs direct semantic retrieval.

### `GET /ai/health`

Returns AI service status.

Example:

```json
{
  "status": "ok",
  "qdrant": true,
  "llm": "ollama"
}
```

---

# 17. Source Attribution

Every RAG-generated answer should attempt to return source information.

Example:

```text
Answer:
Authentication is implemented using JWT middleware...

Sources:
1. middleware/auth.js
2. controllers/authController.js
3. routes/auth.js
```

The source panel should be clickable in the UI.

Future improvement:

- Show exact line range.
- Show code preview.
- Highlight relevant lines.

---

# 18. Error Handling

The system must handle:

### Invalid GitHub URL

Return:

```text
Invalid GitHub repository URL.
```

### Repository not found

Return:

```text
Repository could not be found.
```

### Unsupported/private repository

Return an informative message.

### Indexing failure

Store/log the failure and expose status:

```text
failed
```

### Empty repository

Do not attempt to run RAG.

### LLM unavailable

For Ollama:

```text
Ollama is unavailable. Start the Ollama service or switch to Groq.
```

### Qdrant unavailable

Return a clear infrastructure error.

### No relevant information

The model should say that the repository does not contain enough relevant information rather than inventing an answer.

---

# 19. Security Requirements

Do not execute repository code.

Never pass arbitrary user-generated strings directly into a shell command.

Do not expose:

```text
.env
API keys
secrets
tokens
credentials
```

Do not allow the model to execute arbitrary commands in Version 1.

If private repositories are supported later, use proper GitHub OAuth/token handling.

---

# 20. Performance Requirements

Version 1 targets reasonable portfolio/demo usage rather than production scale.

Targets:

- UI should provide immediate indexing status.
- Chat response should show a loading state.
- Retrieval should normally complete within a few seconds.
- Avoid embedding unchanged content unnecessarily.
- Cache repository metadata where practical.
- Limit context sent to the LLM.

---

# 21. Functional Requirements

## FR-01 Repository Input

The user shall be able to enter a GitHub repository URL.

## FR-02 Repository Validation

The system shall validate the URL and repository availability.

## FR-03 Repository Indexing

The system shall retrieve and index supported repository files.

## FR-04 File Filtering

The system shall ignore generated, binary, secret, and irrelevant files.

## FR-05 Embedding

The system shall generate HuggingFace embeddings.

## FR-06 Vector Storage

The system shall store embeddings and metadata in Qdrant.

## FR-07 Semantic Search

The system shall retrieve relevant repository chunks.

## FR-08 Agent Tool Calling

The agent shall be able to select relevant tools.

## FR-09 File Reading

The system shall retrieve complete/partial files when requested by the agent.

## FR-10 Documentation Search

The system shall search repository documentation separately when appropriate.

## FR-11 LLM Provider

The system shall support Ollama and Groq.

## FR-12 Chat

The user shall be able to ask natural-language questions about the repository.

## FR-13 Sources

The system shall return source file information with answers.

## FR-14 Status

The system shall expose repository indexing status.

---

# 22. Non-functional Requirements

### Maintainability

Keep frontend, application backend, and AI service separated.

### Explainability

The user should be able to see where an answer came from.

### Modularity

LLM provider should be replaceable.

### Security

Do not expose secrets or execute repository code.

### Usability

A user should be able to:

```text
Paste URL
→ Index
→ Ask question
→ Receive answer + sources
```

without technical setup beyond the project environment.

---

# 23. Suggested Repository Structure

```text
github-codebase-agent/
│
├── client/
│   └── React application
│
├── server/
│   ├── src/
│   │   ├── routes/
│   │   ├── controllers/
│   │   ├── services/
│   │   ├── middleware/
│   │   └── app.js
│   └── package.json
│
├── ai-service/
│   ├── app/
│   │   ├── main.py
│   │   ├── routes/
│   │   ├── agent/
│   │   │   ├── agent.py
│   │   │   └── tools.py
│   │   ├── rag/
│   │   │   ├── loader.py
│   │   │   ├── chunker.py
│   │   │   ├── embeddings.py
│   │   │   ├── retriever.py
│   │   │   └── vectorstore.py
│   │   ├── llm/
│   │   │   ├── ollama.py
│   │   │   ├── groq.py
│   │   │   └── provider.py
│   │   └── config.py
│   └── requirements.txt
│
├── docs/
│   ├── architecture.md
│   └── api.md
│
├── .env.example
├── .gitignore
└── README.md
```

---

# 24. Future Enhancements

After Version 1:

1. GitHub OAuth for private repositories.
2. Incremental indexing based on commits.
3. Git diff analysis.
4. "Explain this file" action.
5. "Find usages" tool.
6. Dependency graph.
7. Error/debugging workflow.
8. Code comparison between commits.
9. Pull request analysis.
10. Test-generation suggestions.
11. Repository-wide architecture diagram.
12. Streaming responses.
13. Conversation persistence.
14. Better code-aware chunking.
15. Reranking.

These should not be implemented until the basic system works.

---

# 25. Interview Explanation

A concise explanation:

> "I built a GitHub Codebase Intelligence Agent using React, Express, FastAPI, LangChain, Qdrant, HuggingFace embeddings, and Ollama/Groq. The system ingests a GitHub repository, filters and chunks its source code and documentation, embeds the chunks, and stores them in Qdrant. When a developer asks a question, an agent can choose between semantic code search, documentation search, and direct file retrieval. The retrieved context is then passed to the selected LLM to generate an answer with source file references."

The important distinction from a basic chatbot is:

> **The LLM is not simply answering from a retrieved context. It can decide which repository tools to use to investigate the question.**

---

# 26. Definition of Done

Version 1 is complete when:

- [ ] React application runs.
- [ ] Express server runs.
- [ ] FastAPI service runs.
- [ ] Qdrant is connected.
- [ ] GitHub repository can be provided.
- [ ] Repository can be indexed.
- [ ] Unsupported/irrelevant files are filtered.
- [ ] HuggingFace embeddings are generated.
- [ ] Vectors are stored in Qdrant.
- [ ] Basic RAG works.
- [ ] Agent works.
- [ ] `search_code` works.
- [ ] `read_file` works.
- [ ] `search_docs` works.
- [ ] Ollama works.
- [ ] Groq works.
- [ ] LLM provider can be switched.
- [ ] Chat UI works.
- [ ] Sources are displayed.
- [ ] Error handling works.
- [ ] README explains setup and architecture.
- [ ] A complete demo repository can be analyzed.

