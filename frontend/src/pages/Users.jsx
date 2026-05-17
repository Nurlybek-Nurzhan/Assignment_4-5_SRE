import { useState, useEffect, useCallback } from 'react'
import { useAuth } from '../context/AuthContext'
import { getUsers } from '../api/client'

export default function Users() {
  const { isAuthenticated, token } = useAuth()
  const [users, setUsers] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [lastRefresh, setLastRefresh] = useState(null)

  const load = useCallback(async () => {
    if (!token) return
    setLoading(true)
    try {
      const data = await getUsers(token)
      setUsers(data.users ?? [])
      setError(null)
      setLastRefresh(new Date())
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }, [token])

  useEffect(() => {
    if (!isAuthenticated) return
    load()
    const id = setInterval(load, 10000)
    return () => clearInterval(id)
  }, [isAuthenticated, load])

  if (!isAuthenticated) {
    return <AuthRequired page="Users" />
  }

  const roleColor = role => {
    if (!role) return 'text-slate-400'
    if (role === 'admin') return 'text-sky-400'
    if (role === 'user') return 'text-slate-300'
    return 'text-slate-400'
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-100">Users</h1>
          <p className="text-slate-500 text-sm mt-1">User list from User Service (port 8004)</p>
        </div>
        <div className="flex items-center gap-3">
          {lastRefresh && (
            <span className="text-slate-500 text-xs">Updated {lastRefresh.toLocaleTimeString()}</span>
          )}
          <button onClick={load} className="btn-secondary">Refresh</button>
        </div>
      </div>

      <div className="card p-0 overflow-hidden">
        <div className="px-5 py-4 border-b border-slate-700 flex items-center justify-between">
          <h2 className="text-sky-400 font-semibold">User List</h2>
          {!loading && !error && (
            <span className="text-slate-500 text-xs">{users.length} users</span>
          )}
        </div>

        {loading ? (
          <div className="px-5 py-6 text-slate-500 text-sm animate-pulse">Loading...</div>
        ) : error ? (
          <div className="px-5 py-6 text-red-400 text-sm">Error: {error}</div>
        ) : users.length === 0 ? (
          <div className="px-5 py-6 text-slate-500 text-sm">No users found.</div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr>
                  <th className="table-th">ID</th>
                  <th className="table-th">Username</th>
                  <th className="table-th">Email</th>
                  <th className="table-th">Role</th>
                </tr>
              </thead>
              <tbody>
                {users.map(u => (
                  <tr key={u.id}>
                    <td className="table-td text-slate-500">{u.id}</td>
                    <td className="table-td font-medium">{u.username}</td>
                    <td className="table-td text-slate-400">{u.email ?? '—'}</td>
                    <td className="table-td">
                      <span className={`text-xs font-medium px-2 py-0.5 rounded-full bg-slate-900 ${roleColor(u.role)}`}>
                        {u.role ?? 'user'}
                      </span>
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

export function AuthRequired({ page }) {
  return (
    <div className="flex flex-col items-center justify-center py-24 space-y-4">
      <div className="text-5xl">🔒</div>
      <h2 className="text-xl font-semibold text-slate-200">{page} — Login Required</h2>
      <p className="text-slate-500 text-sm text-center max-w-xs">
        You need to be logged in to access this page. Use the Login button in the top navbar.
      </p>
    </div>
  )
}
