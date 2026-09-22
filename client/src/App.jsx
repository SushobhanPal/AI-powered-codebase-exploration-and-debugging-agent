import { useState } from 'react'
import RepoConfig from './components/RepoConfig'
import ChatInterface from './components/ChatInterface'

function App() {
    const [activeRepoId, setActiveRepoId] = useState(null)

    return (
        <div className="app-container">
            <header className="app-header">
                <h1>GitHub Intelligence Agent</h1>
                <p>AI-powered semantic exploration of your codebases</p>
            </header>
            
            <main className="main-content">
                {!activeRepoId ? (
                    <RepoConfig onRepoIndexed={setActiveRepoId} />
                ) : (
                    <ChatInterface repoId={activeRepoId} />
                )}
            </main>
        </div>
    )
}

export default App
