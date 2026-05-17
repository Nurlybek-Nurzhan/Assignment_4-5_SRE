import { useState } from 'react'
import { processPayment } from '../api/client'

export default function Payments() {
  const [form, setForm] = useState({
    order_id: '',
    amount: '',
    currency: 'USD',
    card_last4: '4242',
  })
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState(null)
  const [error, setError] = useState(null)

  function set(field) {
    return e => setForm(f => ({ ...f, [field]: e.target.value }))
  }

  async function handleSubmit(e) {
    e.preventDefault()
    setLoading(true)
    setResult(null)
    setError(null)
    try {
      const data = await processPayment(
        Number(form.order_id),
        parseFloat(form.amount),
        form.currency,
        form.card_last4,
      )
      setResult(data)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  function reset() {
    setResult(null)
    setError(null)
    setForm(f => ({ ...f, order_id: '', amount: '' }))
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-100">Payments</h1>
        <p className="text-slate-500 text-sm mt-1">Process payments via Payment Service (port 8006)</p>
      </div>

      <div className="max-w-lg">
        <div className="card">
          <h2 className="text-sky-400 font-semibold mb-5">Process Payment</h2>

          <form onSubmit={handleSubmit} className="space-y-4">
            <label className="flex flex-col gap-1">
              <span className="text-xs text-slate-500 uppercase tracking-wider">Order ID</span>
              <input
                type="number"
                min="1"
                value={form.order_id}
                onChange={set('order_id')}
                placeholder="e.g. 1"
                className="w-full"
                required
              />
            </label>

            <label className="flex flex-col gap-1">
              <span className="text-xs text-slate-500 uppercase tracking-wider">Amount</span>
              <input
                type="number"
                step="0.01"
                min="0.01"
                value={form.amount}
                onChange={set('amount')}
                placeholder="e.g. 29.99"
                className="w-full"
                required
              />
            </label>

            <label className="flex flex-col gap-1">
              <span className="text-xs text-slate-500 uppercase tracking-wider">Currency</span>
              <select
                value={form.currency}
                onChange={set('currency')}
                className="w-full"
              >
                <option value="USD">USD</option>
                <option value="EUR">EUR</option>
                <option value="GBP">GBP</option>
                <option value="KZT">KZT</option>
              </select>
            </label>

            <label className="flex flex-col gap-1">
              <span className="text-xs text-slate-500 uppercase tracking-wider">Card Last 4 Digits</span>
              <input
                type="text"
                maxLength={4}
                pattern="\d{4}"
                value={form.card_last4}
                onChange={set('card_last4')}
                placeholder="4242"
                className="w-full"
                required
              />
              <span className="text-xs text-slate-600">Use 4242 for test payments</span>
            </label>

            <div className="flex gap-3 pt-2">
              <button type="submit" disabled={loading} className="btn-primary flex-1">
                {loading ? 'Processing...' : 'Process Payment'}
              </button>
              {(result || error) && (
                <button type="button" onClick={reset} className="btn-secondary">
                  Clear
                </button>
              )}
            </div>
          </form>
        </div>

        {/* Result */}
        {result && (
          <div className="mt-4 card bg-green-900/20 border-green-700">
            <h3 className="text-green-400 font-semibold mb-3 flex items-center gap-2">
              <span className="inline-block w-2.5 h-2.5 rounded-full bg-green-400"></span>
              Payment Successful
            </h3>
            <dl className="space-y-1.5 text-sm">
              <ResultRow label="Transaction ID" value={result.transaction_id} mono />
              <ResultRow label="Order ID" value={result.order_id} />
              <ResultRow label="Amount" value={`${result.amount} ${result.currency}`} />
              <ResultRow label="Status" value={result.status} highlight="green" />
            </dl>
          </div>
        )}

        {error && (
          <div className="mt-4 card bg-red-900/20 border-red-700">
            <h3 className="text-red-400 font-semibold mb-2 flex items-center gap-2">
              <span className="inline-block w-2.5 h-2.5 rounded-full bg-red-400"></span>
              Payment Failed
            </h3>
            <p className="text-red-300 text-sm">{error}</p>
          </div>
        )}
      </div>
    </div>
  )
}

function ResultRow({ label, value, mono, highlight }) {
  return (
    <div className="flex gap-2">
      <dt className="text-slate-500 min-w-[120px]">{label}:</dt>
      <dd className={`font-medium ${mono ? 'font-mono text-xs' : ''} ${highlight === 'green' ? 'text-green-400' : 'text-slate-200'}`}>
        {value ?? '—'}
      </dd>
    </div>
  )
}
