import { useState } from 'react'
import { NavLink } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'

const TABS = [
  { to: '/',         label: 'Dashboard' },
  { to: '/products', label: 'Products'  },
  { to: '/orders',   label: 'Orders'    },
  { to: '/users',    label: 'Users'     },
  { to: '/chat',     label: 'Chat'      },
  { to: '/payments', label: 'Payments'  },
]

export default function Navbar() {
  const { isAuthenticated, username, login, logout, loginError, loginLoading } = useAuth()
  const [user, setUser] = useState('nurzhan')
  const [pass, setPass] = useState('password123')
  const [showForm, setShowForm] = useState(false)

  async function handleLogin(e) {
    e.preventDefault()
    const ok = await login(user, pass)
    if (ok) setShowForm(false)
  }

  return (
    <nav className="bg-slate-800 border-b border-slate-700 sticky top-0 z-50">
      <div className="max-w-screen-xl mx-auto px-4">
        <div className="flex items-center justify-between h-14 gap-4">
          {/* Brand */}
          <div className="flex-shrink-0">
            <span className="text-sky-400 font-bold text-lg tracking-tight">MicroShop</span>
            <span className="hidden sm:inline text-slate-500 text-xs ml-2">SRE End Term</span>
          </div>

          {/* Tabs */}
          <div className="flex items-center gap-1 overflow-x-auto scrollbar-none">
            {TABS.map(({ to, label }) => (
              <NavLink
                key={to}
                to={to}
                end={to === '/'}
                className={({ isActive }) =>
                  `px-3 py-1.5 rounded-md text-sm font-medium whitespace-nowrap transition-colors ${
                    isActive
                      ? 'bg-sky-500 text-white'
                      : 'text-slate-400 hover:text-slate-200 hover:bg-slate-700'
                  }`
                }
              >
                {label}
              </NavLink>
            ))}
          </div>

          {/* Auth section */}
          <div className="flex-shrink-0 flex items-center gap-2">
            {isAuthenticated ? (
              <>
                <span className="text-green-400 text-sm hidden sm:inline">
                  {username}
                </span>
                <button onClick={logout} className="btn-danger text-xs px-3 py-1.5">
                  Logout
                </button>
              </>
            ) : (
              <div className="relative">
                <button
                  onClick={() => setShowForm(v => !v)}
                  className="btn-primary text-xs px-3 py-1.5"
                >
                  Login
                </button>
                {showForm && (
                  <form
                    onSubmit={handleLogin}
                    className="absolute right-0 top-10 bg-slate-800 border border-slate-700 rounded-xl p-4 w-64 shadow-2xl z-50 flex flex-col gap-3"
                  >
                    <p className="text-sm font-semibold text-slate-200">Sign in</p>
                    <input
                      type="text"
                      placeholder="Username"
                      value={user}
                      onChange={e => setUser(e.target.value)}
                      required
                      className="w-full"
                    />
                    <input
                      type="password"
                      placeholder="Password"
                      value={pass}
                      onChange={e => setPass(e.target.value)}
                      required
                      className="w-full"
                    />
                    {loginError && (
                      <p className="text-red-400 text-xs">{loginError}</p>
                    )}
                    <div className="flex gap-2">
                      <button
                        type="submit"
                        disabled={loginLoading}
                        className="btn-primary flex-1"
                      >
                        {loginLoading ? 'Signing in...' : 'Sign in'}
                      </button>
                      <button
                        type="button"
                        onClick={() => setShowForm(false)}
                        className="btn-secondary"
                      >
                        Cancel
                      </button>
                    </div>
                  </form>
                )}
              </div>
            )}
          </div>
        </div>
      </div>
    </nav>
  )
}
