import { useState, useEffect, useCallback } from 'react'
import { checkHealth } from '../api/client'
import StatusDot from './StatusDot'

const SERVICE_META = {
  auth:     { name: 'Auth Service',     port: 8001, desc: '/health · /login' },
  products: { name: 'Product Service',  port: 8002, desc: '/health · /products' },
  orders:   { name: 'Order Service',    port: 8003, desc: '/health · /orders' },
  users:    { name: 'User Service',     port: 8004, desc: '/health · /users' },
  chat:     { name: 'Chat Service',     port: 8005, desc: '/health · /messages' },
  payments: { name: 'Payment Service',  port: 8006, desc: '/health · /pay' },
}

export default function ServiceCard({ service }) {
  const meta = SERVICE_META[service] ?? { name: service, port: '?', desc: '' }
  const [status, setStatus] = useState('loading')
  const [statusText, setStatusText] = useState('Checking...')

  const refresh = useCallback(async () => {
    try {
      const data = await checkHealth(service)
      setStatus('ok')
      setStatusText(data.db ? `OK · DB: ${data.db}` : 'OK')
    } catch (err) {
      setStatus('error')
      setStatusText(err.message ?? 'Unreachable')
    }
  }, [service])

  useEffect(() => {
    refresh()
    const id = setInterval(refresh, 10000)
    return () => clearInterval(id)
  }, [refresh])

  return (
    <div className="card flex flex-col gap-2 min-w-0">
      <div className="font-semibold text-slate-100 truncate">{meta.name}</div>
      <div className="flex items-center gap-2">
        <StatusDot status={status} />
        <span className={`text-sm truncate ${status === 'ok' ? 'text-green-400' : status === 'error' ? 'text-red-400' : 'text-amber-400'}`}>
          {statusText}
        </span>
      </div>
      <div className="text-xs text-slate-500">Port {meta.port} · {meta.desc}</div>
      <div className="flex gap-2 flex-wrap mt-1">
        <a
          href={`/api/${service}/health`}
          target="_blank"
          rel="noreferrer"
          className="text-xs text-sky-400 border border-slate-700 px-2 py-0.5 rounded hover:bg-slate-700 transition-colors"
        >
          Health
        </a>
        <a
          href={`/api/${service}/metrics`}
          target="_blank"
          rel="noreferrer"
          className="text-xs text-sky-400 border border-slate-700 px-2 py-0.5 rounded hover:bg-slate-700 transition-colors"
        >
          Metrics
        </a>
      </div>
    </div>
  )
}
