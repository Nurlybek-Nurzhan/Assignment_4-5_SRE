const BASE = ''

async function req(url, options = {}) {
  const res = await fetch(BASE + url, {
    ...options,
    signal: options.signal ?? AbortSignal.timeout(5000),
  })
  if (!res.ok) {
    let msg = `HTTP ${res.status}`
    try {
      const body = await res.json()
      msg = body.detail || body.error || body.message || msg
    } catch (_) { /* ignore */ }
    throw new Error(msg)
  }
  return res.json()
}

function authHeaders(token) {
  return { Authorization: `Bearer ${token}` }
}

// Auth
export async function login(username, password) {
  return req('/api/auth/login', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username, password }),
  })
}

// Health
export async function checkHealth(service) {
  const paths = {
    auth: '/api/auth/health',
    products: '/api/products/health',
    orders: '/api/orders/health',
    users: '/api/users/health',
    chat: '/api/chat/health',
    payments: '/api/payments/health',
  }
  const url = paths[service]
  if (!url) throw new Error(`Unknown service: ${service}`)
  return req(url)
}

// Products
export async function getProducts() {
  return req('/api/products/products')
}

// Orders
export async function getOrders() {
  return req('/api/orders/orders')
}

export async function createOrder(user_id, product_id, quantity) {
  return req('/api/orders/orders', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ user_id, product_id, quantity }),
  })
}

// Users
export async function getUsers(token) {
  return req('/api/users/users', {
    headers: authHeaders(token),
  })
}

// Chat
export async function getMessages(token) {
  return req('/api/chat/messages', {
    headers: authHeaders(token),
  })
}

export async function sendMessage(token, from_user, to_user, text) {
  return req('/api/chat/messages', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      ...authHeaders(token),
    },
    body: JSON.stringify({ from_user, to_user, text }),
  })
}

// Payments
export async function processPayment(order_id, amount, currency, card_last4) {
  return req('/api/payments/pay', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ order_id, amount, currency, card_last4 }),
  })
}
