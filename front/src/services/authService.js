export const authService = {
  getUser() {
    const user = localStorage.getItem('user')
    return user ? JSON.parse(user) : null
  },

  async loginWithGoogle(role = 'user') {
    // Frontend demo mode. Replace this with the real identity-provider flow later.
    const dummyUser = {
      id: role === 'admin' ? 1 : 2,
      name: role === 'admin' ? 'Admin User' : 'Student User',
      email: role === 'admin' ? 'admin@astro.org' : 'student@astro.org',
      role
    }
    localStorage.setItem('token', 'demo-token')
    localStorage.setItem('user', JSON.stringify(dummyUser))
    return dummyUser
  },

  logout() {
    localStorage.removeItem('token')
    localStorage.removeItem('user')
  }
}
