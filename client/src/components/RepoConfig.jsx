import { useState, useEffect } from 'react'
import { getRepositories, deleteRepository } from '../services/apiEngine'

function RepoConfig({ onRepoIndexed }) {
    const [githubUrl, setGithubUrl] = useState('')
    const [isIndexing, setIsIndexing] = useState(false)
    const [error, setError] = useState(null)
    const [successMsg, setSuccessMsg] = useState(null)
    const [history, setHistory] = useState([])

    useEffect(() => {
        loadHistory()
    }, [])

    const loadHistory = async () => {
        const result = await getRepositories()
        if (result.success) {
            setHistory(result.repositories)
        }
    }

    const handleDelete = async (repoId, e) => {
        e.stopPropagation()
        const result = await deleteRepository(repoId)
        if (result.success) {
            loadHistory()
        } else {
            setError(`Failed to delete ${repoId}`)
        }
    }

    const handleSelectHistory = (repoId) => {
        onRepoIndexed(repoId)
    }

    const handleSubmit = async (e) => {
        e.preventDefault()
        if (!githubUrl.trim()) return
        
        setIsIndexing(true)
        setError(null)
        setSuccessMsg(null)
        
        // Dynamic import of the service function
        const { indexRepository } = await import('../services/apiEngine')
        const result = await indexRepository(githubUrl.trim())
        
        if (result.success) {
            setSuccessMsg(result.message || 'Repository successfully indexed.')
            loadHistory()
            onRepoIndexed(result.repoId)
        } else {
            setError(result.error || 'Failed to index repository.')
        }
        
        setIsIndexing(false)
    }

    return (
        <div className="repo-config-container">
            <h2>Connect Repository</h2>
            <p className="subtitle">Enter a public GitHub URL to index the codebase.</p>
            
            <form onSubmit={handleSubmit} className="repo-form">
                <input 
                    type="url" 
                    placeholder="https://github.com/expressjs/express" 
                    value={githubUrl}
                    onChange={(e) => setGithubUrl(e.target.value)}
                    required
                    disabled={isIndexing}
                    className="input-field"
                />
                <button type="submit" disabled={isIndexing} className="primary-btn">
                    {isIndexing ? 'Indexing...' : 'Index Repository'}
                </button>
            </form>
            
            {error && <div className="feedback-banner error">{error}</div>}
            {successMsg && <div className="feedback-banner success">{successMsg}</div>}
            
            {history.length > 0 && (
                <div className="repo-history">
                    <h3>Previously Indexed</h3>
                    <ul className="history-list">
                        {history.map((repo) => (
                            <li key={repo} className="history-item" onClick={() => handleSelectHistory(repo)}>
                                <span className="repo-name">{repo}</span>
                                <button 
                                    className="delete-btn" 
                                    onClick={(e) => handleDelete(repo, e)}
                                    title="Delete from database"
                                >
                                    Remove
                                </button>
                            </li>
                        ))}
                    </ul>
                </div>
            )}
        </div>
    )
}

export default RepoConfig
