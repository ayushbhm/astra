const BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000'

export default BASE_URL

export async function api(endpoint, options = {}) {
  const token = localStorage.getItem('token')
  const headers = {
    'Content-Type': 'application/json',
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
    ...options.headers
  }

  const res = await fetch(`${BASE_URL}${endpoint}`, {
    ...options,
    headers
  })

  if (!res.ok) {
    const error = await res.json().catch(() => ({ message: res.statusText }))
    throw new Error(error.message || 'API request failed')
  }

  return res.status === 204 ? null : res.json()
}
