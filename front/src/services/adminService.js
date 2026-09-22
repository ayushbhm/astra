import { demoStore } from './demoStore'
import { api } from './api'

export const adminService = {
  // User records are intentionally fetched from the API. Do not substitute
  // local/demo records here: the administrator must only see real accounts.
  async getUsers() {
    return api('/admin/users')
  },

  // All cases for admin
  async getAllCases(search = '') {
    const query = search.toLowerCase()
    return demoStore.all().filter(chart => !query || [chart.title, chart.place, chart.state, chart.story].join(' ').toLowerCase().includes(query))
  },

  // Add chart (no limit)
  async addCase(data) {
    return demoStore.create(data, 1, true)
  },

  // Update any chart
  async updateCase(id, data) {
    return demoStore.update(id, data)
  },

  // Delete any chart
  async deleteCase(id) {
    return demoStore.remove(id)
  },

  // Approve pending chart
  async approveCase(id) {
    return demoStore.setStatus(id, 'APPROVED')
  },

  // Reject pending chart
  async rejectCase(id) {
    return demoStore.setStatus(id, 'REJECTED')
  },

  // Toggle verified badge
  async toggleVerified(id) { return demoStore.toggleVerification(id) },
  createCase(data) { return this.addCase(data) },
  toggleVerification(id) { return this.toggleVerified(id) }
}
