import { api } from './api'

export const userService = {
  async getCases() {
    return api('/cases')
  },

  async searchCases(q) {
    if (!q.trim()) return api('/cases')
    const controller = new AbortController()
    const timeout = setTimeout(() => controller.abort(), 22000)
    try {
      return await api(`/cases/search?q=${encodeURIComponent(q.trim())}`, {
        signal: controller.signal
      })
    } catch (error) {
      if (error.name === 'AbortError') {
        throw new Error('Smart search timed out. Please try again in a moment.')
      }
      throw error
    } finally {
      clearTimeout(timeout)
    }
  },


  // Cases submitted by the logged-in user
  async getMyCases() {
    return api('/user/cases')
  },

  // Submit a new chart (max 5 enforced)
  async addCase(data) {
    return api('/user/cases', { method: 'POST', body: JSON.stringify(data) })
  },

  // Update own chart
  async updateCase(id, data) {
    return api(`/user/cases/${id}`, { method: 'PUT', body: JSON.stringify(data) })
  },

  // Delete own chart
  async deleteCase(id) {
    await api(`/user/cases/${id}`, { method: 'DELETE' })
  },

  getMyQuota() {
    return api('/user/quota')
  },

  updateMyCase(id, data) { return this.updateCase(id, data) },
  deleteMyCase(id) { return this.deleteCase(id) }
}
