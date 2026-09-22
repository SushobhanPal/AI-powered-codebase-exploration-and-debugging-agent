# GitHub Codebase Intelligence Agent

An AI-powered assistant that ingests a GitHub repository, indexes its code and documentation, and uses RAG plus an agent with code-analysis tools to answer questions about the codebase with file-level source references.

## Architecture

- **React Client (`client/`)**: Chat UI and Repo Explorer
- **Express Server (`server/`)**: Backend API that talks to the React client and FastAPI
- **FastAPI AI Service (`ai-service/`)**: AI Core handling LangChain, LLM queries, and Vector DB (Qdrant) logic.

## Environment Variables

Check `.env.example` to see which environment variables are required.

## Getting Started

*(Instructions on running Qdrant, Express, FastAPI, and React will go here)*
