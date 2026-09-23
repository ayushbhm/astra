import { api } from './api'

export const userService = {
  async getCases(search = '') {
    const cases = await api('/cases')
    const query = search.trim().toLowerCase()
    return query
      ? cases.filter(chart => [chart.title, chart.place, chart.state, chart.story, ...chart.tags]
        .join(' ').toLowerCase().includes(query))
      : cases
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
