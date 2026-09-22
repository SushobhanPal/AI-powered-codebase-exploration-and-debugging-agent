# Coding Style Guidelines

Based on the user's past projects (MERN, React-Learning, and MP), the following coding style and structure MUST be followed across Python, Express, and React codebases.

## 1. General JavaScript/Node.js Guidelines
- **Semicolons:** Semicolons are optional and mostly omitted in the user's style, especially in modern React code. Do not strictly enforce them.
- **Quotes:** Prefer single quotes (`'`) for string literals and imports in React, though double quotes (`"`) are acceptable in Node.js setups.
- **Functions:** Use ES6 arrow functions (`() => {}`) extensively for callbacks, route handlers, and functional components.

## 2. Express.js Guidelines
- **Module System:** Use CommonJS (`require()`, `module.exports`).
- **Simplicity:** Keep the server setup simple without excessive boilerplate. Do not over-abstract the entry point.
- **Routing:** 
  - Define simple routes directly using `app.get()`, `app.post()`, etc.
  - For modular routes, use `express.Router()` and mount them (e.g., `app.use("/users", user)`).
- **Responses:** Prefer standard Express response methods like `res.send()`, `res.json()`, `res.sendFile()`, or `res.render()`.
- **Project Structure:** 
  - Place static files in a `public` directory.
  - Extract specific route logic into a `routes` directory (e.g., `routes/users.js`).
  - Keep view templates (if using ejs) in a `views` folder.

### Example Express Setup
```javascript
const express = require('express')
const app = express()
const path = require('node:path')

const userRoutes = require('./routes/users')

app.use(express.static('public'))
app.use(express.urlencoded({ extended: true }))
app.use(express.json())

app.use('/users', userRoutes)

app.get('/', (req, res) => {
    res.sendFile(path.join(__dirname, 'public/index.html'))
})

app.listen(3000)
```

## 3. React Guidelines
- **Architecture & Structure:** 
  - Strictly prefer **Functional Components** with **React Hooks** (`useState`, `useEffect`). Do not use Class components.
  - Separate concerns by keeping components in a `components/` directory.
- **Service Modules (Crucial):** 
  - Extract business logic, API calls (`fetch`), storage, and side effects into explicit service files inside a `services/` directory (e.g., `services/chatEngine.js`). 
  - Service functions should be exported as standalone async functions, handle their own `try/catch` logic gracefully, and return formatted data objects back to components.
- **State Management:** 
  - Use `useState` and `useEffect` appropriately.
  - Destructure state arrays cleanly (e.g., `const [items, setItems] = useState([])`).
- **JSX & Rendering:** 
  - Keep JSX clean and readable. 
  - Use implicit returns for `.map()` when rendering lists.
- **Styling:** 
  - Use Vanilla CSS (e.g., `App.css`, `index.css`).
  - Use data-attributes for application-level theming (e.g., `document.documentElement.setAttribute('data-theme', theme)`).
- **Exports:** Use `export default ComponentName` at the bottom of the file rather than inline exports.

### Example React Component and Service
```javascript
// services/apiEngine.js
export const fetchItems = async () => {
  try {
    const res = await fetch('http://localhost:8000/items')
    if (!res.ok) throw new Error(`Server returned status ${res.status}`)
    const data = await res.json()
    return data
  } catch (error) {
    console.error('Error fetching items:', error)
    return [] // Graceful degradation
  }
}

// components/ItemList.jsx
import React, { useState, useEffect } from 'react'
import { fetchItems } from '../services/apiEngine' 

function ItemList() {
    const [items, setItems] = useState([])

    useEffect(() => {
        fetchItems().then(data => setItems(data))
    }, [])

    const addItem = () => {
        setItems(prev => [
            ...prev,
            { id: prev.length, value: 'New Item' }
        ])
    }

    return (
        <div className="item-container">
            <button onClick={addItem}>Add Item</button>
            <ul>
                {items.map(item => (
                    <li key={item.id}>{item.value}</li>
                ))}
            </ul>
        </div>
    )
}

export default ItemList
```

## 4. Python & FastAPI Guidelines
- **Framework & Validation:** Use **FastAPI** for creating endpoints and **Pydantic** (`BaseModel`) for request/response validation.
- **Environment Variables:** Always use `os.getenv()` with sensible defaults for configuration (e.g., `os.getenv("QDRANT_URL", "http://localhost:6333")`). Do not hardcode connection strings.
- **Error Handling:** 
  - Wrap logic (especially LLM or Vector DB calls) in `try...except` blocks.
  - Raise `HTTPException` with appropriate status codes (e.g., 400, 500) and detailed string errors on failure.
- **Separation of Concerns:** 
  - Keep API route definitions in `app.py`.
  - Keep heavy processing scripts (like PDF indexing, loading, chunking) in separate standalone scripts like `index.py`.
  - Create separate CLI runner scripts (e.g., `chat.py`) for quick manual testing of LLM logic without starting the whole API server.
- **RAG & LangChain:** 
  - Use `langchain_ollama`, `langchain_huggingface`, and `langchain_qdrant` extensively for AI operations.
  - Build prompts cleanly using f-strings with multiline `"""` formatting.
- **Containerization:** Rely on tools like Docker Compose (e.g., `docker-compose.yml`) to quickly spin up dependencies like Qdrant or Ollama locally.

### Example FastAPI Setup
```python
import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from langchain_ollama import ChatOllama

app = FastAPI(title="Backend API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

llm_client = ChatOllama(
    model=os.getenv("OLLAMA_MODEL", "qwen3:8b"),
    temperature=0,
    base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
)

class QueryRequest(BaseModel):
    query: str

@app.post("/api/chat")
async def chat(request: QueryRequest):
    user_query = request.query.strip()
    if not user_query:
        raise HTTPException(status_code=400, detail="Query cannot be empty")

    try:
        # Example invocation
        response = llm_client.invoke(user_query)
        return {"answer": response.content}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"LLM execution failed: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
```
