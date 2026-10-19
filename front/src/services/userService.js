import { api } from './api'

export const userService = {
  async getCases() {
    return api('/cases')
  },

  async searchCases(q) {
    if (!q.trim()) return api('/cases')
    return api(`/cases/search?q=${encodeURIComponent(q.trim())}`)
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
