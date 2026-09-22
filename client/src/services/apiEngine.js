// Extract business logic, API calls, and side effects into explicit service files
// as per AGENTS.md rules.

const BASE_URL = 'http://localhost:3005'

export const indexRepository = async (githubUrl) => {
    try {
        // Extract a simple ID from the URL (e.g. owner/repo)
        const parts = githubUrl.replace(/\/$/, '').split('/')
        const repoId = parts.length >= 2 ? `${parts[parts.length-2]}/${parts[parts.length-1]}` : 'unknown'
        
        // Encode the ID for the URL path
        const encodedId = encodeURIComponent(repoId)
        
        const response = await fetch(`${BASE_URL}/api/repositories/${encodedId}/index`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ github_url: githubUrl })
        })
        
        if (!response.ok) {
            const err = await response.json()
            throw new Error(err.detail || `Server error: ${response.status}`)
        }
        
        const data = await response.json()
        return { success: true, repoId, message: data.message }
    } catch (error) {
        console.error('Error indexing repository:', error)
        return { success: false, error: error.message }
    }
}

export const chatWithAgent = async (repositoryId, message) => {
    try {
        const response = await fetch(`${BASE_URL}/api/chat`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ repository_id: repositoryId, message })
        })
        
        if (!response.ok) {
            const err = await response.json()
            throw new Error(err.detail || `Server error: ${response.status}`)
        }
        
        const data = await response.json()
        return { success: true, answer: data.answer }
    } catch (error) {
        console.error('Error querying agent:', error)
        return { success: false, answer: 'Sorry, I encountered an error while reaching the AI Service.' }
    }
}

export const getRepositories = async () => {
    try {
        const response = await fetch(`${BASE_URL}/api/repositories`)
        if (!response.ok) throw new Error('Failed to fetch repositories')
        const data = await response.json()
        return { success: true, repositories: data.repositories || [] }
    } catch (error) {
        console.error('Error fetching tracked repositories:', error)
        return { success: false, repositories: [] }
    }
}

export const deleteRepository = async (repositoryId) => {
    try {
        const response = await fetch(`${BASE_URL}/api/delete`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ repository_id: repositoryId })
        })
        if (!response.ok) throw new Error('Failed to delete repository')
        return { success: true }
    } catch (error) {
        console.error('Error deleting repository:', error)
        return { success: false }
    }
}
