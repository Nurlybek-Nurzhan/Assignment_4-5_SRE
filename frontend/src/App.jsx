import { BrowserRouter, Routes, Route } from 'react-router-dom'
import { AuthProvider } from './context/AuthContext'
import Navbar from './components/Navbar'
import Dashboard from './pages/Dashboard'
import Products from './pages/Products'
import Orders from './pages/Orders'
import Users from './pages/Users'
import Chat from './pages/Chat'
import Payments from './pages/Payments'

export default function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <div className="min-h-screen bg-slate-900">
          <Navbar />
          <main className="max-w-screen-xl mx-auto px-4 py-8">
            <Routes>
              <Route path="/"         element={<Dashboard />} />
              <Route path="/products" element={<Products />} />
              <Route path="/orders"   element={<Orders />} />
              <Route path="/users"    element={<Users />} />
              <Route path="/chat"     element={<Chat />} />
              <Route path="/payments" element={<Payments />} />
            </Routes>
          </main>
        </div>
      </BrowserRouter>
    </AuthProvider>
  )
}
