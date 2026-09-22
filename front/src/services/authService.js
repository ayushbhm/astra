import BASE_URL from './api'

export const authService = {
  getUser() {
    const user = localStorage.getItem('user')
    return user ? JSON.parse(user) : null
  },

  async loginWithGoogle(credential) {
    const res = await fetch(`${BASE_URL}/auth/google`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        credential
      })
    })

    const data = await res.json()

    if (!res.ok) {
      throw new Error(data.message || 'Google login failed')
    }

    localStorage.setItem('user', JSON.stringify(data.user))

    return data.user
  },

  logout() {
    localStorage.removeItem('token')
    localStorage.removeItem('user')
  }
}