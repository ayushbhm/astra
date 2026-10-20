import { api } from './api'

export const adminService = {
  // User records are intentionally fetched from the API. Do not substitute
  // local/demo records here: the administrator must only see real accounts.
  async getUsers() {
    return api('/admin/users')
  },

  // All cases for admin
  async getAllCases(search = '') {
    const cases = await api('/admin/cases')
    const query = search.trim().toLowerCase()
    return cases.filter(chart => !query || [chart.title, chart.place, chart.state, chart.story].join(' ').toLowerCase().includes(query))
  },

  async syncSearchIndex() {
    return api('/admin/search/index', { method: 'POST' })
  },

  async searchCases(query) {
    return api('/admin/search', { method: 'POST', body: JSON.stringify({ query }) })
  },

  // Add chart (no limit)
  async addCase(data) {
    return api('/admin/cases', { method: 'POST', body: JSON.stringify(data) })
  },

  // Update any chart
  async updateCase(id, data) {
    return api(`/admin/cases/${id}`, { method: 'PUT', body: JSON.stringify(data) })
  },

  // Delete any chart
  async deleteCase(id) {
    return api(`/admin/cases/${id}`, { method: 'DELETE' })
  },

  // Approve pending chart
  async approveCase(id) {
    return api(`/admin/cases/${id}/status`, { method: 'PUT', body: JSON.stringify({ status: 'APPROVED' }) })
  },

  // Reject pending chart
  async rejectCase(id) {
    return api(`/admin/cases/${id}/status`, { method: 'PUT', body: JSON.stringify({ status: 'REJECTED' }) })
  },

  // Toggle verified badge
  async toggleVerified(id) { return api(`/admin/cases/${id}/verification`, { method: 'PUT' }) },
  createCase(data) { return this.addCase(data) },
  toggleVerification(id) { return this.toggleVerified(id) }
}
