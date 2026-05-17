import { useState, useEffect, useCallback } from 'react'
import { getOrders, createOrder } from '../api/client'

export default function Orders() {
  const [orders, setOrders] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [lastRefresh, setLastRefresh] = useState(null)

  // Create order form state
  const [form, setForm] = useState({ user_id: '1', product_id: '1', quantity: '2' })
  const [creating, setCreating] = useState(false)
  const [createResult, setCreateResult] = useState(null)
  const [createError, setCreateError] = useState(null)

  const load = useCallback(async () => {
    try {
      const data = await getOrders()
      setOrders(data.orders ?? [])
      setError(null)
      setLastRefresh(new Date())
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    load()
    const id = setInterval(load, 10000)
    return () => clearInterval(id)
  }, [load])

  async function handleCreate(e) {
    e.preventDefault()
    setCreating(true)
    setCreateResult(null)
    setCreateError(null)
    try {
      const data = await createOrder(
        Number(form.user_id),
        Number(form.product_id),
        Number(form.quantity),
      )
      setCreateResult(data)
      await load()
    } catch (err) {
      setCreateError(err.message)
    } finally {
      setCreating(false)
    }
  }

  const statusColor = s => {
    if (!s) return 'text-slate-400'
    const lower = s.toLowerCase()
    if (lower === 'pending') return 'text-amber-400'
    if (lower === 'completed' || lower === 'ok') return 'text-green-400'
    if (lower === 'failed' || lower === 'error') return 'text-red-400'
    return 'text-slate-400'
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-100">Orders</h1>
          <p className="text-slate-500 text-sm mt-1">Order management from Order Service (port 8003)</p>
        </div>
        <div className="flex items-center gap-3">
          {lastRefresh && (
            <span className="text-slate-500 text-xs">Updated {lastRefresh.toLocaleTimeString()}</span>
          )}
          <button onClick={load} className="btn-secondary">Refresh</button>
        </div>
      </div>

      {/* Orders table */}
      <div className="card p-0 overflow-hidden">
        <div className="px-5 py-4 border-b border-slate-700 flex items-center justify-between">
          <h2 className="text-sky-400 font-semibold">Recent Orders</h2>
          {!loading && !error && (
            <span className="text-slate-500 text-xs">{orders.length} orders</span>
          )}
        </div>

        {loading ? (
          <div className="px-5 py-6 text-slate-500 text-sm animate-pulse">Loading...</div>
        ) : error ? (
          <div className="px-5 py-6 text-red-400 text-sm">Service unavailable: {error}</div>
        ) : orders.length === 0 ? (
          <div className="px-5 py-6 text-slate-500 text-sm">No orders yet.</div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr>
                  <th className="table-th">Order ID</th>
                  <th className="table-th">User ID</th>
                  <th className="table-th">Product ID</th>
                  <th className="table-th">Quantity</th>
                  <th className="table-th">Status</th>
                </tr>
              </thead>
              <tbody>
                {orders.map(o => (
                  <tr key={o.id}>
                    <td className="table-td text-slate-500">{o.id}</td>
                    <td className="table-td">{o.user_id}</td>
                    <td className="table-td">{o.product_id}</td>
                    <td className="table-td">{o.quantity}</td>
                    <td className="table-td">
                      <span className={`text-xs font-medium px-2 py-0.5 rounded-full bg-slate-900 ${statusColor(o.status)}`}>
                        {o.status}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Create order form */}
      <div className="card">
        <h2 className="text-sky-400 font-semibold mb-4">Create Order</h2>
        <form onSubmit={handleCreate} className="flex flex-wrap gap-3 items-end">
          <label className="flex flex-col gap-1">
            <span className="text-xs text-slate-500 uppercase tracking-wider">User ID</span>
            <input
              type="number"
              min="1"
              value={form.user_id}
              onChange={e => setForm(f => ({ ...f, user_id: e.target.value }))}
              className="w-24"
              required
            />
          </label>
          <label className="flex flex-col gap-1">
            <span className="text-xs text-slate-500 uppercase tracking-wider">Product ID</span>
            <input
              type="number"
              min="1"
              value={form.product_id}
              onChange={e => setForm(f => ({ ...f, product_id: e.target.value }))}
              className="w-24"
              required
            />
          </label>
          <label className="flex flex-col gap-1">
            <span className="text-xs text-slate-500 uppercase tracking-wider">Quantity</span>
            <input
              type="number"
              min="1"
              value={form.quantity}
              onChange={e => setForm(f => ({ ...f, quantity: e.target.value }))}
              className="w-24"
              required
            />
          </label>
          <button type="submit" disabled={creating} className="btn-primary">
            {creating ? 'Creating...' : '+ Create Order'}
          </button>
        </form>

        {createResult && (
          <div className="mt-4 p-3 bg-green-900/30 border border-green-700 rounded-lg text-green-300 text-sm">
            Order created! ID: <span className="font-semibold">{createResult.order_id}</span>
            {createResult.status && <> · Status: <span className="font-semibold">{createResult.status}</span></>}
          </div>
        )}
        {createError && (
          <div className="mt-4 p-3 bg-red-900/30 border border-red-700 rounded-lg text-red-300 text-sm">
            Failed to create order: {createError}
          </div>
        )}
      </div>
    </div>
  )
}
