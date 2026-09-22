import { demoStore } from './demoStore'

export const userService = {
  // Public cases list with optional search query
  async getCases(search = '') {
    const query = search.toLowerCase()
    return demoStore.all().filter(chart => chart.status === 'APPROVED').filter(chart =>
      !query || [chart.title, chart.place, chart.state, chart.story, ...chart.tags].join(' ').toLowerCase().includes(query)
    )
  },

  // Cases submitted by the logged-in user
  async getMyCases() {
    return demoStore.mine()
  },

  // Submit a new chart (max 5 enforced)
  async addCase(data) {
    if (demoStore.mine().length >= 5) throw new Error('Maximum of 5 charts reached')
    return demoStore.create(data)
  },

  // Update own chart
  async updateCase(id, data) {
    return demoStore.update(id, data)
  },

  // Delete own chart
  async deleteCase(id) {
    return demoStore.remove(id)
  },

  getMyQuota() {
    const count = demoStore.mine().length
    return { count, max: 5, canAdd: count < 5, remaining: Math.max(0, 5 - count) }
  },

  updateMyCase(id, data) { return this.updateCase(id, data) },
  deleteMyCase(id) { return this.deleteCase(id) }
}
