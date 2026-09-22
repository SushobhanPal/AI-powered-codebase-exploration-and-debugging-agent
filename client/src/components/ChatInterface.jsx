import { useState, useRef, useEffect } from 'react'
import { chatWithAgent } from '../services/apiEngine'

function ChatInterface({ repoId }) {
    const [messages, setMessages] = useState([
        { role: 'assistant', text: `Connected to ${repoId}. Ask me anything about this codebase.` }
    ])
    const [input, setInput] = useState('')
    const [isTyping, setIsTyping] = useState(false)
    const endOfMessagesRef = useRef(null)

    const scrollToBottom = () => {
        endOfMessagesRef.current?.scrollIntoView({ behavior: 'smooth' })
    }

    useEffect(() => {
        scrollToBottom()
    }, [messages])

    const handleSend = async (e) => {
        e.preventDefault()
        if (!input.trim() || isTyping) return
        
        const userMessage = input.trim()
        setInput('')
        setMessages(prev => [...prev, { role: 'user', text: userMessage }])
        setIsTyping(true)
        
        const response = await chatWithAgent(repoId, userMessage)
        
        setMessages(prev => [...prev, { role: 'assistant', text: response.answer }])
        setIsTyping(false)
    }

    return (
        <div className="chat-container">
            <div className="chat-header">
                <h3>Agent Conversation</h3>
                <span className="repo-badge">{repoId}</span>
            </div>
            
            <div className="chat-history">
                {messages.map((msg, idx) => (
                    <div key={idx} className={`message-row ${msg.role}`}>
                        <div className={`message-bubble ${msg.role}`}>
                            <div className="message-role">{msg.role === 'user' ? 'You' : 'Agent'}</div>
                            <pre className="message-content">{msg.text}</pre>
                        </div>
                    </div>
                ))}
                {isTyping && (
                    <div className="message-row assistant">
                        <div className="message-bubble assistant loading">
                            <span className="dot">.</span><span className="dot">.</span><span className="dot">.</span>
                        </div>
                    </div>
                )}
                <div ref={endOfMessagesRef} />
            </div>

            <form onSubmit={handleSend} className="chat-input-area">
                <input 
                    type="text" 
                    placeholder="Ask about the architecture, functions, or files..." 
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    disabled={isTyping}
                    className="input-field"
                />
                <button type="submit" disabled={isTyping || !input.trim()} className="primary-btn">
                    Send
                </button>
            </form>
        </div>
    )
}

export default ChatInterface
