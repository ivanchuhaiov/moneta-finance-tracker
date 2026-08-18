import { useEffect, useRef, useState } from 'react'
import { Sparkles, Send, RotateCcw } from 'lucide-react'
import TopBar from '../components/TopBar'
import { useCurrency } from '../context/CurrencyContext'
import { sendChatMessage, getChatMessages } from '../api/ai'
import { formatDateTime } from '../utils/format'

const STORAGE_KEY = 'moneta_ai_conversation_id'

export default function AIChat() {
  const { currency } = useCurrency()
  const [conversationId, setConversationId] = useState(() => {
    const stored = localStorage.getItem(STORAGE_KEY)
    return stored ? Number(stored) : null
  })
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState('')
  const [loadingHistory, setLoadingHistory] = useState(false)
  const [sending, setSending] = useState(false)
  const [error, setError] = useState('')
  const scrollRef = useRef(null)

  useEffect(() => {
    if (!conversationId) return
    setLoadingHistory(true)
    getChatMessages(conversationId)
      .then(setMessages)
      .catch(() => setError('Не удалось загрузить историю диалога'))
      .finally(() => setLoadingHistory(false))
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight
    }
  }, [messages, sending])

  async function handleSend(e) {
    e.preventDefault()
    const text = input.trim()
    if (!text || sending) return

    setError('')
    setSending(true)
    const userMessage = { role: 'user', content: text, created_at: new Date().toISOString() }
    setMessages((prev) => [...prev, userMessage])
    setInput('')

    try {
      const result = await sendChatMessage({ conversation_id: conversationId, message: text }, currency)
      setConversationId(result.conversation_id)
      localStorage.setItem(STORAGE_KEY, String(result.conversation_id))
      setMessages((prev) => [...prev, { role: 'assistant', content: result.reply, created_at: new Date().toISOString() }])
    } catch {
      setError('Не удалось отправить сообщение')
      setMessages((prev) => prev.slice(0, -1))
      setInput(text)
    } finally {
      setSending(false)
    }
  }

  function handleNewConversation() {
    localStorage.removeItem(STORAGE_KEY)
    setConversationId(null)
    setMessages([])
    setError('')
  }

  return (
    <>
      <TopBar
        title="AI-ассистент"
        subtitle="Задавайте вопросы о своих финансах на естественном языке"
        actions={
          <button className="btn btn-sm btn-secondary" onClick={handleNewConversation} disabled={sending}>
            <RotateCcw size={14} style={{ verticalAlign: 'middle', marginRight: 6 }} />
            Новый диалог
          </button>
        }
      />
      <div className="content">
        <div className="card chat-card">
          <div className="chat-window" ref={scrollRef}>
            {loadingHistory ? (
              <div className="page-loading"><div className="spinner" /></div>
            ) : messages.length === 0 ? (
              <div className="chat-empty">
                <Sparkles size={28} style={{ color: 'var(--accent-purple)' }} />
                <div style={{ fontWeight: 700, marginTop: 10 }}>Спросите что-нибудь о своих финансах</div>
                <div style={{ color: 'var(--text-secondary)', fontSize: 12.5, marginTop: 4 }}>
                  Например: «Сколько я потратил на еду в этом месяце?» или «Какая у меня норма сбережений?»
                </div>
              </div>
            ) : (
              messages.map((m, i) => (
                <div key={i} className={`chat-message ${m.role}`}>
                  <div className="chat-bubble">{m.content}</div>
                  <div className="chat-meta">{formatDateTime(m.created_at)}</div>
                </div>
              ))
            )}
            {sending && (
              <div className="chat-message assistant">
                <div className="chat-bubble chat-typing">
                  <span /><span /><span />
                </div>
              </div>
            )}
          </div>

          {error && <div className="alert alert-error" style={{ margin: '0 20px 12px' }}>{error}</div>}

          <form className="chat-input-row" onSubmit={handleSend}>
            <input
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Напишите сообщение..."
              disabled={sending}
            />
            <button className="btn btn-primary" type="submit" disabled={!input.trim() || sending}>
              <Send size={16} />
            </button>
          </form>
        </div>
      </div>
    </>
  )
}