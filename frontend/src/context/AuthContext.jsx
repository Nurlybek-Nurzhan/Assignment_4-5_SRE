import { createContext, useContext, useState, useCallback } from 'react'
import { login as apiLogin } from '../api/client'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [token, setToken] = useState(() => localStorage.getItem('ms_token') || null)
  const [username, setUsername] = useState(() => localStorage.getItem('ms_username') || null)
  const [loginError, setLoginError] = useState(null)
  const [loginLoading, setLoginLoading] = useState(false)

  const login = useCallback(async (user, pass) => {
    setLoginLoading(true)
    setLoginError(null)
    try {
      const data = await apiLogin(user, pass)
      setToken(data.token)
      setUsername(data.username)
      localStorage.setItem('ms_token', data.token)
      localStorage.setItem('ms_username', data.username)
      return true
    } catch (err) {
      setLoginError(err.message || 'Login failed')
      return false
    } finally {
      setLoginLoading(false)
    }
  }, [])

  const logout = useCallback(() => {
    setToken(null)
    setUsername(null)
    localStorage.removeItem('ms_token')
    localStorage.removeItem('ms_username')
  }, [])

  return (
    <AuthContext.Provider value={{ token, username, login, logout, loginError, loginLoading, isAuthenticated: !!token }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth must be used within AuthProvider')
  return ctx
}
