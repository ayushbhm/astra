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
    const contentType = res.headers.get('content-type') || ''
    let detail = ''

    if (contentType.includes('application/json')) {
      const error = await res.json().catch(() => ({}))
      // Flask-JWT-Extended returns `msg`; application routes usually return `message`.
      detail = error.message || error.msg || ''
    } else {
      detail = (await res.text().catch(() => '')).trim().slice(0, 200)
    }

    throw new Error(detail || `API request failed (${res.status})`)
  }

  return res.status === 204 ? null : res.json()
}
