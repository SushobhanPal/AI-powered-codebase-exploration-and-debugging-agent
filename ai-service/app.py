import os
import json
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from langchain_ollama import ChatOllama
import uvicorn

from agent import run_agent
from qdrant_db import index_repository, delete_repository

REPOS_FILE = "indexed_repos.json"

def get_tracked_repos():
    if not os.path.exists(REPOS_FILE): return []
    try:
        with open(REPOS_FILE, "r") as f:
            return json.load(f)
    except:
        return []

def track_repo(repo_id: str):
    repos = get_tracked_repos()
    if repo_id not in repos:
        repos.append(repo_id)
        with open(REPOS_FILE, "w") as f:
            json.dump(repos, f)

def untrack_repo(repo_id: str):
    repos = get_tracked_repos()
    if repo_id in repos:
        repos.remove(repo_id)
        with open(REPOS_FILE, "w") as f:
            json.dump(repos, f)

app = FastAPI(title="GitHub Codebase Intelligence Agent API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class HealthResponse(BaseModel):
    status: str
    qdrant: bool
    llm: str

class ChatRequest(BaseModel):
    repository_id: str
    message: str

class IndexRequest(BaseModel):
    github_url: str

@app.get("/ai/health", response_model=HealthResponse)
def health_check():
    return HealthResponse(
        status="ok",
        qdrant=True, # TODO: actual qdrant check
        llm=os.getenv("LLM_PROVIDER", "ollama")
    )

@app.post("/api/chat")
async def chat_endpoint(request: ChatRequest):
    repo_id = request.repository_id.strip()
    msg = request.message.strip()
    
    if not repo_id or not msg:
        raise HTTPException(status_code=400, detail="repository_id and message cannot be empty")
        
    try:
        # Run the LangChain ReAct agent
        answer = run_agent(repo_id, msg)
        return {"answer": answer}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"LLM execution failed: {str(e)}")

@app.post("/ai/index")
async def index_endpoint(request: IndexRequest):
    url = request.github_url.strip()
    if not url:
        raise HTTPException(status_code=400, detail="github_url cannot be empty")
        
    try:
        index_repository(url)
        
        # Extract repo id from github url and track it
        repo_id = url.replace("https://github.com/", "").strip("/")
        track_repo(repo_id)
        
        return {"status": "success", "message": f"Repository {url} indexed successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Indexing failed: {str(e)}")

@app.get("/ai/repositories")
def list_repositories():
    return {"repositories": get_tracked_repos()}

class DeleteRequest(BaseModel):
    repository_id: str

@app.post("/ai/delete")
async def delete_endpoint(request: DeleteRequest):
    repo_id = request.repository_id.strip()
    if not repo_id:
        raise HTTPException(status_code=400, detail="repository_id cannot be empty")
        
    try:
        delete_repository(repo_id)
        untrack_repo(repo_id)
        return {"status": "success", "message": f"Repository {repo_id} deleted successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Deletion failed: {str(e)}")

if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8001, reload=True)
