import { useState, useEffect, useCallback, useRef } from 'react'
import { useAuth } from '../context/AuthContext'
import { getMessages, sendMessage } from '../api/client'
import { AuthRequired } from './Users'

export default function Chat() {
  const { isAuthenticated, token, username } = useAuth()
  const [messages, setMessages] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  const [toUser, setToUser] = useState('admin')
  const [text, setText] = useState('')
  const [sending, setSending] = useState(false)
  const [sendError, setSendError] = useState(null)

  const bottomRef = useRef(null)

  const load = useCallback(async () => {
    if (!token) return
    try {
      const data = await getMessages(token)
      setMessages(data.messages ?? [])
      setError(null)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }, [token])

  useEffect(() => {
    if (!isAuthenticated) return
    setLoading(true)
    load()
    const id = setInterval(load, 10000)
    return () => clearInterval(id)
  }, [isAuthenticated, load])

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  if (!isAuthenticated) {
    return <AuthRequired page="Chat" />
  }

  async function handleSend(e) {
    e.preventDefault()
    if (!text.trim()) return
    setSending(true)
    setSendError(null)
    try {
      await sendMessage(token, username, toUser.trim() || 'admin', text.trim())
      setText('')
      await load()
    } catch (err) {
      setSendError(err.message)
    } finally {
      setSending(false)
    }
  }

  function formatTime(ts) {
    if (!ts) return ''
    try {
      return new Date(ts).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    } catch (_) { return ts.substring(11, 16) }
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-100">Chat</h1>
          <p className="text-slate-500 text-sm mt-1">Messages via Chat Service (port 8005)</p>
        </div>
        <button onClick={load} className="btn-secondary">Refresh</button>
      </div>

      <div className="card flex flex-col gap-4">
        <h2 className="text-sky-400 font-semibold border-b border-slate-700 pb-3">
          Messages
          <span className="text-slate-500 text-xs font-normal ml-2">(auto-refresh every 10s)</span>
        </h2>

        {/* Messages list */}
        <div className="min-h-[200px] max-h-96 overflow-y-auto space-y-2 pr-1">
          {loading ? (
            <p className="text-slate-500 text-sm animate-pulse">Loading messages...</p>
          ) : error ? (
            <p className="text-red-400 text-sm">Chat service error: {error}</p>
          ) : messages.length === 0 ? (
            <p className="text-slate-500 text-sm">No messages yet. Send the first one!</p>
          ) : (
            messages.map(m => (
              <div
                key={m.id}
                className={`flex gap-2 ${m.from_user === username ? 'justify-end' : 'justify-start'}`}
              >
                <div className={`max-w-[75%] rounded-xl px-3 py-2 text-sm ${
                  m.from_user === username
                    ? 'bg-sky-900/60 border border-sky-700'
                    : 'bg-slate-700/60 border border-slate-600'
                }`}>
                  <div className="flex items-baseline gap-2 mb-0.5">
                    <span className="text-xs font-semibold text-sky-400">{m.from_user}</span>
                    <span className="text-xs text-slate-500">→ {m.to_user}</span>
                    <span className="text-xs text-slate-600 ml-auto">{formatTime(m.timestamp)}</span>
                  </div>
                  <div className="text-slate-200">{m.text}</div>
                </div>
              </div>
            ))
          )}
          <div ref={bottomRef} />
        </div>

        {/* Send form */}
        <form onSubmit={handleSend} className="border-t border-slate-700 pt-4 flex flex-col gap-3">
          <div className="flex gap-3 items-center">
            <label className="flex items-center gap-2 text-xs text-slate-500">
              To:
              <input
                type="text"
                value={toUser}
                onChange={e => setToUser(e.target.value)}
                className="w-28"
                placeholder="recipient"
              />
            </label>
          </div>
          <div className="flex gap-2">
            <input
              type="text"
              value={text}
              onChange={e => setText(e.target.value)}
              placeholder="Type a message..."
              className="flex-1"
              disabled={sending}
            />
            <button type="submit" disabled={sending || !text.trim()} className="btn-primary">
              {sending ? 'Sending...' : 'Send'}
            </button>
          </div>
          {sendError && <p className="text-red-400 text-xs">{sendError}</p>}
        </form>
      </div>
    </div>
  )
}
