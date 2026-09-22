# GitHub Codebase Intelligence Agent — Action Plan

**Project objective:** Build a simple but interview-ready GitHub Codebase Intelligence Agent using familiar technologies: React, Express, FastAPI, LangChain, Qdrant, HuggingFace embeddings, Ollama, and Groq.

---

# 0. Final Target

The user flow should eventually be:

```text
Paste GitHub URL
      ↓
Register repository
      ↓
Index repository
      ↓
View indexing status
      ↓
Open chat
      ↓
Ask codebase question
      ↓
Agent decides which tool(s) to use
      ↓
Qdrant / file retrieval
      ↓
Ollama OR Groq
      ↓
Answer
      ↓
Show source files + line ranges
```

---

# 1. Development Philosophy

Do NOT build the entire system at once.

Build vertically:

```text
GitHub
  ↓
Files
  ↓
Chunks
  ↓
Embeddings
  ↓
Qdrant
  ↓
RAG
  ↓
Agent
  ↓
FastAPI
  ↓
Express
  ↓
React
  ↓
Polish
```

At every stage, test the layer before adding another.

---

# 2. Phase 0 — Project Setup

## Goal

Create the monorepo structure and establish the three applications.

## Tasks

- [ ] Create root project.
- [ ] Create React client.
- [ ] Create Express server.
- [ ] Create Python AI service.
- [ ] Initialize Git.
- [ ] Create `.gitignore`.
- [ ] Create `.env.example`.
- [ ] Create README.
- [ ] Create `docs/`.

Suggested structure:

```text
github-codebase-agent/
├── client/
├── server/
├── ai-service/
├── docs/
├── .env.example
├── .gitignore
└── README.md
```

## Environment variables

Plan for:

```text
GITHUB_TOKEN=
GROQ_API_KEY=
QDRANT_URL=
QDRANT_API_KEY=
LLM_PROVIDER=ollama
OLLAMA_BASE_URL=
OLLAMA_MODEL=
GROQ_MODEL=
```

Do not commit `.env`.

## Exit condition

All three services can start independently.

---

# 3. Phase 1 — GitHub Repository Retrieval

## Goal

Given a GitHub URL, retrieve the repository's files.

## Tasks

- [ ] Validate GitHub URL.
- [ ] Extract owner/repository.
- [ ] Connect to GitHub API.
- [ ] Retrieve repository tree.
- [ ] Retrieve supported file contents.
- [ ] Implement recursive directory handling.
- [ ] Implement file filtering.
- [ ] Ignore `.git`.
- [ ] Ignore `node_modules`.
- [ ] Ignore generated build directories.
- [ ] Ignore binary files.
- [ ] Ignore secrets such as `.env`.

## Test

Use a small public repository.

Expected output:

```text
Repository:
owner/repo

Files:
README.md
package.json
src/app.js
src/routes/users.js
...
```

## Exit condition

A Python script can retrieve and print the repository files without involving React or Express.

---

# 4. Phase 2 — Document and Code Processing

## Goal

Convert repository files into documents suitable for RAG.

## Tasks

- [ ] Create a loader.
- [ ] Attach metadata.
- [ ] Detect programming language.
- [ ] Identify file type.
- [ ] Implement chunking.
- [ ] Preserve file path.
- [ ] Preserve line numbers where practical.
- [ ] Preserve repository ID.
- [ ] Preserve chunk type.

Example:

```text
content:
"router.post('/', createUser)"

metadata:
repository_id = owner/repo
file_path = routes/users.js
language = javascript
chunk_type = code
start_line = 10
end_line = 15
```

## Test

Print:

```text
Number of files
Number of documents
Number of chunks
Sample chunk
Sample metadata
```

## Exit condition

You can inspect chunks and verify they are meaningful.

---

# 5. Phase 3 — HuggingFace Embeddings

## Goal

Convert repository chunks into vectors.

## Tasks

- [ ] Install HuggingFace embedding dependencies.
- [ ] Load the embedding model.
- [ ] Generate an embedding for one chunk.
- [ ] Verify vector dimension.
- [ ] Batch embed repository chunks.
- [ ] Keep indexing and query embedding models identical.

## Test

Run:

```text
sample chunk
    ↓
embedding
    ↓
print vector shape
```

## Exit condition

A complete repository can be embedded without errors.

---

# 6. Phase 4 — Qdrant

## Goal

Persist embeddings and metadata in Qdrant.

## Tasks

- [ ] Start/connect to Qdrant.
- [ ] Create collection.
- [ ] Configure vector size based on the selected embedding model.
- [ ] Upload vectors.
- [ ] Store metadata payload.
- [ ] Add repository ID to every point.
- [ ] Implement repository filtering.
- [ ] Implement similarity search.

## Test

Query:

```text
"authentication middleware"
```

Expected:

```text
1. middleware/auth.js
2. routes/auth.js
3. controllers/auth.js
```

## Exit condition

Qdrant returns meaningful repository chunks for semantic queries.

---

# 7. Phase 5 — Basic RAG

## Goal

Get a working RAG system BEFORE introducing agents.

## Pipeline

```text
Question
   ↓
Embedding
   ↓
Qdrant
   ↓
Top-K chunks
   ↓
Prompt
   ↓
LLM
   ↓
Answer
```

## Tasks

- [ ] Create retriever.
- [ ] Retrieve Top-K chunks.
- [ ] Build context.
- [ ] Create RAG prompt.
- [ ] Connect Ollama.
- [ ] Generate answer.
- [ ] Return source metadata.
- [ ] Add "I don't know" behavior when context is insufficient.

## Test questions

```text
Where is authentication implemented?

How does user registration work?

Where is the database connected?

What dependencies does this project use?

How do I run the project?
```

## Exit condition

A command-line or Python test can answer questions using only indexed repository information.

---

# 8. Phase 6 — Implement `read_file`

## Goal

Allow the AI system to inspect a full file rather than only retrieved chunks.

## Tool

```text
read_file(repository_id, file_path)
```

## Tasks

- [ ] Implement file lookup.
- [ ] Return file contents.
- [ ] Add size limits.
- [ ] Return useful errors.
- [ ] Preserve source metadata.

## Test

```text
read_file(
  "owner/repo",
  "middleware/auth.js"
)
```

## Exit condition

The tool reliably returns the requested file.

---

# 9. Phase 7 — Implement `search_code`

## Goal

Turn Qdrant retrieval into an agent tool.

## Tool

```text
search_code(query, repository_id)
```

## Tasks

- [ ] Wrap retriever as a LangChain tool.
- [ ] Add repository filtering.
- [ ] Return relevant chunks and metadata.
- [ ] Add tool description that clearly tells the agent when to use it.

## Example

```text
search_code(
  "JWT authentication middleware"
)
```

## Exit condition

The agent can invoke the tool and receive useful results.

---

# 10. Phase 8 — Implement `search_docs`

## Goal

Give the agent a separate tool for README/documentation/configuration questions.

## Tool

```text
search_docs(query, repository_id)
```

## Tasks

- [ ] Tag documentation chunks during ingestion.
- [ ] Filter Qdrant search by document type.
- [ ] Expose it as an agent tool.

## Example

```text
"How do I run the application?"
```

Agent should be able to choose:

```text
search_docs()
```

## Exit condition

Documentation questions return documentation-first results.

---

# 11. Phase 9 — Build the Agent

## Goal

Combine the three tools.

```text
Agent
 ├── search_code
 ├── read_file
 └── search_docs
```

## Tasks

- [ ] Create agent.
- [ ] Create system prompt.
- [ ] Register tools.
- [ ] Connect LLM.
- [ ] Allow multiple tool calls.
- [ ] Return final answer.
- [ ] Capture tool/source information.
- [ ] Prevent unrelated repository access.

## Agent instructions should establish:

1. Use tools when repository information is required.
2. Do not invent repository details.
3. Prefer `search_docs` for documentation questions.
4. Prefer `search_code` for conceptual/code-location questions.
5. Use `read_file` when complete file context is required.
6. Cite relevant source files.
7. Say when information cannot be found.

## Exit condition

The agent can investigate a question using more than one tool before answering.

---

# 12. Phase 10 — Ollama and Groq Abstraction

## Goal

Allow the same agent/RAG system to use either LLM provider.

## Tasks

- [ ] Create LLM provider interface/factory.
- [ ] Implement Ollama provider.
- [ ] Implement Groq provider.
- [ ] Read provider from configuration.
- [ ] Test both providers.
- [ ] Ensure agent code doesn't duplicate provider-specific logic.

Conceptually:

```text
get_llm(provider)

if provider == "ollama":
    return OllamaLLM

if provider == "groq":
    return GroqLLM
```

## Exit condition

Changing configuration switches the model without changing RAG or agent code.

---

# 13. Phase 11 — FastAPI AI Service

## Goal

Expose the working AI system through HTTP.

## Endpoints

```text
GET  /ai/health
POST /ai/index
POST /ai/search
POST /ai/chat
```

## Tasks

- [ ] Create FastAPI app.
- [ ] Create Pydantic request/response models.
- [ ] Move ingestion into service layer.
- [ ] Move RAG into service layer.
- [ ] Move agent into service layer.
- [ ] Add health check.
- [ ] Add exception handling.
- [ ] Test using Postman/curl.

## Exit condition

The AI system works entirely through FastAPI endpoints.

---

# 14. Phase 12 — Express Backend

## Goal

Create the application-facing API.

## Endpoints

```text
POST /api/repositories
POST /api/repositories/:id/index
GET  /api/repositories/:id/status
GET  /api/repositories/:id/files
POST /api/chat
```

## Tasks

- [ ] Create Express routes.
- [ ] Add controllers.
- [ ] Add service layer.
- [ ] Validate GitHub URLs.
- [ ] Forward AI requests to FastAPI.
- [ ] Handle FastAPI errors.
- [ ] Return frontend-friendly JSON.
- [ ] Add CORS configuration.

## Exit condition

Express can act as the only backend endpoint exposed to React.

---

# 15. Phase 13 — React Frontend

## Goal

Create a clean developer-oriented UI.

## Main screens/components

```text
App
├── RepositoryInput
├── RepositoryStatus
├── FileExplorer
├── Chat
│   ├── MessageList
│   ├── ChatInput
│   └── LoadingState
└── SourcesPanel
```

## Initial flow

```text
1. Paste repository URL.
2. Click Index.
3. Show indexing progress/status.
4. Show file tree.
5. Enable chat after indexing.
6. Ask question.
7. Display answer.
8. Display sources.
```

## Exit condition

A user can complete the full workflow without Postman or command-line interaction.

---

# 16. Phase 14 — Sources and Code References

## Goal

Make answers trustworthy and demonstrable.

Each answer should show:

```text
Sources

routes/users.js
Lines 10-25

middleware/auth.js
Lines 1-30
```

## Tasks

- [ ] Return source metadata from FastAPI.
- [ ] Pass it through Express.
- [ ] Render sources in React.
- [ ] Add expandable source preview.
- [ ] Highlight relevant lines if practical.

---

# 17. Phase 15 — Repository Explorer

## Goal

Make the application feel like a developer tool rather than a generic chatbot.

## Tasks

- [ ] Build file tree.
- [ ] Display file names.
- [ ] Display language.
- [ ] Allow selecting a file.
- [ ] Display file content.
- [ ] Connect selected file to chat context if useful.

---

# 18. Phase 16 — Error Handling

Test all major failure cases.

## GitHub

- [ ] Invalid URL.
- [ ] Repository does not exist.
- [ ] Repository has no supported files.
- [ ] Rate limit.

## Qdrant

- [ ] Service unavailable.
- [ ] Collection missing.
- [ ] Search failure.

## LLM

- [ ] Ollama not running.
- [ ] Groq API key missing.
- [ ] Groq rate/API error.
- [ ] Model unavailable.

## AI

- [ ] No relevant chunks.
- [ ] Tool failure.
- [ ] Malformed agent output.

## Frontend

- [ ] Network error.
- [ ] Empty question.
- [ ] Indexing still in progress.
- [ ] Chat before indexing.

---

# 19. Phase 17 — Testing

## Unit-level tests

Test:

- GitHub URL parser
- File filtering
- Chunking
- Metadata creation
- Qdrant retrieval
- Tool functions
- Provider selection

## Integration tests

Test:

```text
GitHub → ingestion → Qdrant
```

```text
Question → retrieval → LLM
```

```text
Question → agent → tools → LLM
```

```text
React → Express → FastAPI → Qdrant/LLM
```

## Manual test questions

### Code search

```text
Where is authentication implemented?
```

### File investigation

```text
Explain middleware/auth.js.
```

### Multi-step reasoning

```text
Trace the user registration flow from the route to the database.
```

### Documentation

```text
How do I run this project?
```

### Negative test

```text
What is the weather today?
```

Expected behavior:

```text
This question is outside the repository context.
```

---

# 20. Phase 18 — Performance Improvements

Only after the basic system works.

## Improvements

- [ ] Batch embedding.
- [ ] Avoid duplicate indexing.
- [ ] Hash files to detect changes.
- [ ] Cache repository metadata.
- [ ] Limit context size.
- [ ] Tune Top-K.
- [ ] Add retrieval filtering.
- [ ] Add optional reranking later.

Do NOT prematurely optimize.

---

# 21. Phase 19 — UI Polish

## Design direction

Developer-focused:

- Dark theme.
- Clean code editor-like interface.
- Minimal animations.
- Clear source references.
- Clear repository status.
- Good empty/loading/error states.

## Important UI states

```text
No repository
Repository indexing
Index complete
Index failed
Chat loading
Answer generated
No relevant information
LLM unavailable
```

---

# 22. Phase 20 — Documentation

Create:

```text
README.md
docs/architecture.md
docs/api.md
```

README should include:

1. Project overview.
2. Features.
3. Architecture diagram.
4. Tech stack.
5. Installation.
6. Environment variables.
7. Running Qdrant.
8. Running Ollama.
9. Running FastAPI.
10. Running Express.
11. Running React.
12. Example questions.
13. Screenshots.
14. Limitations.
15. Future improvements.

---

# 23. Phase 21 — Interview Preparation

Be prepared to explain these topics.

## RAG

Know:

```text
Documents
→ chunks
→ embeddings
→ vector DB
→ similarity search
→ context
→ LLM
```

## Embeddings

Explain:

> Embeddings represent text as vectors so semantically related code/questions can be found through vector similarity.

## Qdrant

Explain:

> Qdrant stores embeddings and metadata and performs similarity search with repository-level filtering.

## Agent

Explain:

> The agent decides which tool to use based on the user's question instead of always performing the same retrieval operation.

## Tool Calling

Explain:

```text
Question
→ Agent decides
→ Tool
→ Tool result
→ Agent
→ Final answer
```

## Why FastAPI?

> The AI pipeline uses Python libraries, so FastAPI provides a clean service boundary around the Python RAG/agent system.

## Why Express?

> Express handles the application API, GitHub integration, repository/session operations, and frontend-facing backend responsibilities.

## Why Ollama?

> It allows local LLM inference and provides a private/local option.

## Why Groq?

> It provides a fast cloud LLM option without changing the rest of the RAG architecture.

## Why both?

> The system separates the LLM provider from retrieval and agent logic.

---

# 24. Interview Demo Script

Use a repository that you understand well.

Recommended demo:

```text
1. Open application.
2. Paste GitHub repository.
3. Start indexing.
4. Show file tree.
5. Ask:
   "Where is authentication implemented?"
6. Show agent-generated answer.
7. Show source files.
8. Ask:
   "Trace the user registration flow."
9. Explain that the agent performs multiple tool calls.
10. Switch Ollama → Groq.
11. Ask another question.
12. Explain the architecture.
```

The strongest demo is not a fancy UI.

The strongest demo is showing:

```text
Question
   ↓
Agent decision
   ↓
Tool call
   ↓
Retrieved code
   ↓
Final answer
   ↓
Source reference
```

---

# 25. Milestone Schedule

## Milestone 1 — RAG Core

Complete:

```text
GitHub
→ Loader
→ Chunking
→ HuggingFace
→ Qdrant
→ Retrieval
→ Ollama
→ Answer
```

This is the first major milestone.

---

## Milestone 2 — Agent

Complete:

```text
Agent
├── search_code
├── read_file
└── search_docs
```

This demonstrates the agentic part.

---

## Milestone 3 — Services

Complete:

```text
React
  ↓
Express
  ↓
FastAPI
  ↓
Agent/RAG
```

---

## Milestone 4 — Product UI

Complete:

```text
Repository input
File explorer
Chat
Sources
Status
Errors
```

---

## Milestone 5 — Interview Ready

Complete:

```text
Clean README
Architecture diagram
Screenshots
Demo repository
Provider switching
Error handling
Test cases
Interview explanation
```

---

# 26. Recommended Build Order

The exact order should be:

```text
[1] Create project folders
        ↓
[2] GitHub loader
        ↓
[3] File filtering
        ↓
[4] Chunking
        ↓
[5] HuggingFace embeddings
        ↓
[6] Qdrant
        ↓
[7] Basic retrieval
        ↓
[8] Ollama RAG
        ↓
[9] search_code tool
        ↓
[10] read_file tool
        ↓
[11] search_docs tool
        ↓
[12] Agent
        ↓
[13] Groq provider
        ↓
[14] FastAPI
        ↓
[15] Express
        ↓
[16] React
        ↓
[17] Sources
        ↓
[18] UI polish
        ↓
[19] Testing
        ↓
[20] Documentation
```

---

# 27. Rules to Keep the Project Simple

1. Start with one repository per active session.
2. Start with public repositories.
3. Use one Qdrant collection initially.
4. Use one embedding model.
5. Use three agent tools.
6. Use one agent.
7. Use one local model.
8. Add Groq as the second provider.
9. Do not build multi-agent workflows.
10. Do not allow code execution.
11. Do not add unnecessary databases.
12. Do not add authentication until the core project works.
13. Do not build advanced dependency graphs initially.
14. Do not optimize before measuring.
15. Do not add features merely to make the project look complicated.

---

# 28. Final Definition of Done

The project is interview-ready when a user can:

```text
Paste GitHub repository
        ↓
Index repository
        ↓
See indexing completion
        ↓
Ask:
"How does authentication work?"
        ↓
Agent searches code
        ↓
Agent reads relevant files
        ↓
LLM produces explanation
        ↓
UI shows source files
```

And the developer can explain every step from:

```text
GitHub API
→ file processing
→ chunking
→ embeddings
→ Qdrant
→ retrieval
→ agent
→ tools
→ LLM
→ FastAPI
→ Express
→ React
```

without relying on technologies they do not understand.
