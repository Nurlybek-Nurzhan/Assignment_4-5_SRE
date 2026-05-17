import { useState, useEffect, useCallback } from 'react'
import { getProducts } from '../api/client'

export default function Products() {
  const [products, setProducts] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [lastRefresh, setLastRefresh] = useState(null)

  const load = useCallback(async () => {
    try {
      const data = await getProducts()
      setProducts(data.products ?? [])
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

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-100">Products</h1>
          <p className="text-slate-500 text-sm mt-1">Product catalog from Product Service (port 8002)</p>
        </div>
        <div className="flex items-center gap-3">
          {lastRefresh && (
            <span className="text-slate-500 text-xs">
              Updated {lastRefresh.toLocaleTimeString()}
            </span>
          )}
          <button onClick={load} className="btn-secondary">Refresh</button>
        </div>
      </div>

      <div className="card p-0 overflow-hidden">
        <div className="px-5 py-4 border-b border-slate-700 flex items-center justify-between">
          <h2 className="text-sky-400 font-semibold">Product Catalog</h2>
          {!loading && !error && (
            <span className="text-slate-500 text-xs">{products.length} products</span>
          )}
        </div>

        {loading ? (
          <LoadingRows cols={4} />
        ) : error ? (
          <ErrorRow cols={4} message={error} />
        ) : products.length === 0 ? (
          <EmptyRow cols={4} />
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr>
                  <th className="table-th">ID</th>
                  <th className="table-th">Name</th>
                  <th className="table-th">Price</th>
                  <th className="table-th">Stock</th>
                </tr>
              </thead>
              <tbody>
                {products.map(p => (
                  <tr key={p.id}>
                    <td className="table-td text-slate-500">{p.id}</td>
                    <td className="table-td font-medium">{p.name}</td>
                    <td className="table-td text-green-400">${Number(p.price).toFixed(2)}</td>
                    <td className="table-td">
                      <StockBadge stock={p.stock} />
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  )
}

function StockBadge({ stock }) {
  if (stock === 0) return <span className="text-xs px-2 py-0.5 rounded-full bg-red-900 text-red-300">Out of stock</span>
  if (stock < 10) return <span className="text-xs px-2 py-0.5 rounded-full bg-amber-900 text-amber-300">{stock} left</span>
  return <span className="text-xs px-2 py-0.5 rounded-full bg-green-900 text-green-300">{stock} in stock</span>
}

export function LoadingRows({ cols }) {
  return (
    <div className="px-5 py-6 text-slate-500 text-sm animate-pulse">
      Loading...
    </div>
  )
}

export function ErrorRow({ cols, message }) {
  return (
    <div className="px-5 py-6 text-red-400 text-sm">
      Service unavailable: {message}
    </div>
  )
}

export function EmptyRow({ cols }) {
  return (
    <div className="px-5 py-6 text-slate-500 text-sm">
      No data found.
    </div>
  )
}
