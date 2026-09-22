const express = require('express')
const app = express()
const path = require('node:path')
const cors = require('cors')

app.use(cors())
app.use(express.static('public'))
app.use(express.urlencoded({ extended: true }))
app.use(express.json())

app.get('/', (req, res) => {
    res.json({ message: 'GitHub Codebase Intelligence Agent API is running.' })
})

// Proxy for Chat
app.post('/api/chat', async (req, res) => {
    try {
        const response = await fetch('http://localhost:8001/api/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(req.body)
        })
        const data = await response.json()
        if (!response.ok) return res.status(response.status).json(data)
        res.json(data)
    } catch (error) {
        console.error('Chat proxy error:', error)
        res.status(500).json({ detail: 'Failed to connect to AI Service' })
    }
})

// Proxy for Indexing Repository
app.post('/api/repositories/:id/index', async (req, res) => {
    try {
        const { github_url } = req.body
        const response = await fetch('http://localhost:8001/ai/index', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ github_url })
        })
        const data = await response.json()
        if (!response.ok) return res.status(response.status).json(data)
        res.json(data)
    } catch (error) {
        console.error('Index proxy error:', error)
        res.status(500).json({ detail: 'Failed to connect to AI Service' })
    }
})
// Proxy for Getting Tracked Repositories
app.get('/api/repositories', async (req, res) => {
    try {
        const response = await fetch('http://localhost:8001/ai/repositories')
        const data = await response.json()
        if (!response.ok) return res.status(response.status).json(data)
        res.json(data)
    } catch (error) {
        console.error('List repos proxy error:', error)
        res.status(500).json({ detail: 'Failed to connect to AI Service' })
    }
})

// Proxy for Deleting a Repository
app.post('/api/delete', async (req, res) => {
    try {
        const { repository_id } = req.body
        const response = await fetch('http://localhost:8001/ai/delete', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ repository_id })
        })
        const data = await response.json()
        if (!response.ok) return res.status(response.status).json(data)
        res.json(data)
    } catch (error) {
        console.error('Delete proxy error:', error)
        res.status(500).json({ detail: 'Failed to connect to AI Service' })
    }
})

const PORT = process.env.PORT || 3005
app.listen(PORT, () => {
    console.log(`Express server running on port ${PORT}`)
})
