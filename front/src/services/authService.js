import BASE_URL from './api'

const API_ROOT = BASE_URL.replace(/\/+$/, '')

async function requestJson(url, options = {}, timeoutMs = 12000) {
  const controller = new AbortController()
  let timedOut = false
  const timer = setTimeout(() => {
    timedOut = true
    controller.abort()
  }, timeoutMs)

  try {
    const response = await fetch(url, { ...options, signal: controller.signal })
    const data = await response.json().catch(() => ({}))
    return { response, data }
  } catch (error) {
    if (timedOut || error.name === 'AbortError' || error.name === 'TimeoutError') {
      throw new Error('Flask did not respond in time. Check that the backend is running, then retry sign-in.')
    }
    if (error instanceof TypeError) {
      throw new Error(`Cannot reach Flask at ${API_ROOT}. Start the backend and check VITE_API_URL if it uses a different address.`)
    }
    throw error
  } finally {
    clearTimeout(timer)
  }
}

export const authService = {
  async checkBackend() {
    const { response } = await requestJson(`${API_ROOT}/health`, { cache: 'no-store' }, 3000)
    if (!response.ok) {
      throw new Error('Flask is running but not ready yet. Wait a few seconds and retry sign-in.')
    }
    return true
  },

  getUser() {
    const user = localStorage.getItem('user')

    if (!user) {
      return null
    }

    try {
      return JSON.parse(user)
    } catch {
      // A prior build saved `data.user`, but the API returns the user directly.
      // That left the literal string "undefined" in storage.
      localStorage.removeItem('user')
      return null
    }
  },

  async loginWithGoogle(credential) {
    // Fail fast with a useful message if Flask (or its database) is unavailable.
    await this.checkBackend()
    const { response: res, data } = await requestJson(`${API_ROOT}/google`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ credential })
    })

    if (!res.ok) {
      throw new Error(data.message || `Google login failed (${res.status})`)
    }

    if (!data || typeof data !== 'object' || !data.id) {
      throw new Error('Google login returned an invalid user')
    }

    // /google returns the user object itself, not { user: ... }.
    localStorage.setItem(
      'user',
      JSON.stringify(data)
    )
    localStorage.setItem('token', data.token)

    return data
  },

  logout() {
    localStorage.removeItem('user')
    localStorage.removeItem('token')
  }
}
