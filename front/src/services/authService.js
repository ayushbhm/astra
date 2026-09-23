import BASE_URL from './api'

export const authService = {
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
    const res = await fetch(`${BASE_URL}/google`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        credential
      })
    })

    const data = await res.json().catch(() => ({}))

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
