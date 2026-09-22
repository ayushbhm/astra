<template>
  <div class="admin-page">
    <!-- Admin Header -->
    <div class="admin-header">
      <div>
        <span class="eyebrow-label">CHIEF ARCHIVIST GATEWAY</span>
        <h1 class="page-title">Admin Management Dashboard</h1>
        <p class="page-subtitle">
          Full CRUD authority over all case records, unlimited additions, peer review, and verification badging.
        </p>
      </div>

      <div class="admin-top-actions">
        <button class="btn-primary" @click="openAddModal">
          <span>＋</span> Add Chart (Unlimited)
        </button>
      </div>
    </div>

    <section class="users-section" aria-labelledby="users-heading">
      <div class="section-heading">
        <div>
          <span class="eyebrow-label">ACCOUNT DIRECTORY</span>
          <h2 id="users-heading">All users</h2>
          <p>Live account information from the server.</p>
        </div>
        <button class="btn-secondary" :disabled="usersLoading" @click="loadUsers">
          {{ usersLoading ? 'Refreshing…' : 'Refresh users' }}
        </button>
      </div>

      <div v-if="usersLoading" class="users-state">Loading user accounts…</div>
      <div v-else-if="usersError" class="users-state users-error" role="alert">
        {{ usersError }}
      </div>
      <div v-else-if="users.length === 0" class="users-state">
        No user accounts have been returned by the server.
      </div>
      <div v-else class="users-table-wrap">
        <table class="users-table">
          <thead>
            <tr>
              <th scope="col">ID</th>
              <th scope="col">Name</th>
              <th scope="col">Email</th>
              <th scope="col">Phone</th>
              <th scope="col">Role</th>
              <th scope="col">Account status</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="user in users" :key="user.id">
              <td>{{ displayValue(user.id) }}</td>
              <td>{{ displayValue(user.name) }}</td>
              <td>{{ displayValue(user.email) }}</td>
              <td>{{ displayValue(user.phone) }}</td>
              <td><span class="role-badge">{{ displayValue(user.role) }}</span></td>
              <td>
                <span v-if="typeof user.is_active === 'boolean'" :class="['status-badge', user.is_active ? 'active' : 'inactive']">
                  {{ user.is_active ? 'Active' : 'Inactive' }}
                </span>
                <span v-else>—</span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </section>

    <!-- Filter Bar (Status & Search) -->
    <div class="admin-filter-bar">
      <div class="status-tabs">
        <button 
          v-for="s in statusOptions" 
          :key="s.value"
          class="status-tab-btn"
          :class="{ active: currentStatusFilter === s.value }"
          @click="setStatusFilter(s.value)"
        >
          <span>{{ s.label }}</span>
          <span class="tab-count">{{ getCountByStatus(s.value) }}</span>
        </button>
      </div>

      <div class="admin-search-wrap">
        <input 
          type="text" 
          placeholder="Filter by title, place, state..."
          v-model="adminSearch"
          @input="applyFilters"
        />
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="loading-state">
      <p>Loading database records...</p>
    </div>

    <!-- Empty State -->
    <div v-else-if="filteredCases.length === 0" class="empty-state">
      <div class="empty-icon">📂</div>
      <h3>No charts found for the selected filter</h3>
      <p>Try switching to "All Records" or clear your search input.</p>
    </div>

    <!-- Admin Cases Grid -->
    <div v-else class="admin-cases-grid">
      <CaseCard 
        v-for="c in filteredCases" 
        :key="c.id" 
        :chart="c"
        :can-manage="true"
        :show-status="true"
        :is-admin-mode="true"
        @view="openViewModal"
        @edit="openEditModal"
        @delete="handleDelete"
        @approve="handleApprove"
        @reject="handleReject"
        @toggle-verified="handleToggleVerified"
      />
    </div>

    <!-- Add / Edit Modal (Admin Mode: No limits, controls status) -->
    <CaseFormModal 
      :is-open="isFormOpen"
      :initial-data="editingCase"
      :is-edit="!!editingCase"
      :is-admin="true"
      :saving="saving"
      @close="isFormOpen = false"
      @save="handleSave"
    />

    <!-- View Modal -->
    <CaseModal 
      :chart="viewingCase"
      @close="viewingCase = null"
    />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import CaseCard from '../components/CaseCard.vue'
import CaseFormModal from '../components/CaseFormModal.vue'
import CaseModal from '../components/CaseModal.vue'
import { adminService } from '../services/adminService'

const loading = ref(false)
const saving = ref(false)
const allCases = ref([])
const filteredCases = ref([])
const users = ref([])
const usersLoading = ref(false)
const usersError = ref('')

const currentStatusFilter = ref('ALL')
const adminSearch = ref('')

const isFormOpen = ref(false)
const editingCase = ref(null)
const viewingCase = ref(null)

const statusOptions = [
  { label: 'All Records', value: 'ALL' },
  { label: 'Pending Review', value: 'PENDING' },
  { label: 'Approved', value: 'APPROVED' },
  { label: 'Rejected', value: 'REJECTED' }
]

const displayValue = (value) => value === null || value === undefined || value === '' ? '—' : value

const loadUsers = async () => {
  usersLoading.value = true
  usersError.value = ''
  try {
    const result = await adminService.getUsers()
    users.value = Array.isArray(result) ? result : []
  } catch (err) {
    users.value = []
    usersError.value = err.message || 'Unable to load user accounts.'
  } finally {
    usersLoading.value = false
  }
}

const loadAdminCases = async () => {
  loading.value = true
  try {
    allCases.value = await adminService.getAllCases()
    applyFilters()
  } catch (err) {
    console.error('Failed to load admin cases:', err)
  } finally {
    loading.value = false
  }
}

const applyFilters = () => {
  let result = [...allCases.value]

  if (currentStatusFilter.value !== 'ALL') {
    result = result.filter(c => c.status === currentStatusFilter.value)
  }

  if (adminSearch.value.trim()) {
    const s = adminSearch.value.trim().toLowerCase()
    result = result.filter(c =>
      (c.title && c.title.toLowerCase().includes(s)) ||
      (c.place && c.place.toLowerCase().includes(s)) ||
      (c.state && c.state.toLowerCase().includes(s)) ||
      (c.story && c.story.toLowerCase().includes(s))
    )
  }

  filteredCases.value = result
}

const setStatusFilter = (val) => {
  currentStatusFilter.value = val
  applyFilters()
}

const getCountByStatus = (status) => {
  if (status === 'ALL') return allCases.value.length
  return allCases.value.filter(c => c.status === status).length
}

const openAddModal = () => {
  editingCase.value = null
  isFormOpen.value = true
}

const openEditModal = (chart) => {
  editingCase.value = { ...chart }
  isFormOpen.value = true
}

const openViewModal = (chart) => {
  viewingCase.value = chart
}

const handleSave = async (formData) => {
  saving.value = true
  try {
    if (editingCase.value) {
      await adminService.updateCase(editingCase.value.id, formData)
    } else {
      await adminService.createCase(formData)
    }
    isFormOpen.value = false
    await loadAdminCases()
  } catch (err) {
    alert(err.message || 'Failed to save chart')
  } finally {
    saving.value = false
  }
}

const handleDelete = async (chart) => {
  if (!confirm(`ADMIN ACTION: Permanently remove case #${chart.id} ("${chart.title}") from database?`)) return
  try {
    await adminService.deleteCase(chart.id)
    await loadAdminCases()
  } catch (err) {
    alert(err.message || 'Failed to delete case')
  }
}

const handleApprove = async (chart) => {
  try {
    await adminService.approveCase(chart.id)
    await loadAdminCases()
  } catch (err) {
    alert(err.message || 'Failed to approve case')
  }
}

const handleReject = async (chart) => {
  try {
    await adminService.rejectCase(chart.id)
    await loadAdminCases()
  } catch (err) {
    alert(err.message || 'Failed to reject case')
  }
}

const handleToggleVerified = async (chart) => {
  try {
    await adminService.toggleVerification(chart.id, chart.verification_status)
    await loadAdminCases()
  } catch (err) {
    alert(err.message || 'Failed to toggle verification')
  }
}

onMounted(() => {
  loadAdminCases()
  loadUsers()
})
</script>

<style scoped>
.admin-page {
  max-width: 1200px;
  margin: 0 auto;
  padding: 40px 24px 80px;
}

.admin-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  border-bottom: 1px solid #e7e0d5;
  padding-bottom: 20px;
  margin-bottom: 24px;
}

.eyebrow-label {
  font-family: var(--font-serif);
  font-size: 10px;
  font-weight: 700;
  letter-spacing: 0.16em;
  color: #7e2222;
  display: block;
  margin-bottom: 6px;
}

.page-title {
  font-size: 28px;
  margin-bottom: 6px;
}

.page-subtitle {
  font-size: 13px;
  color: var(--text-muted);
  margin: 0;
}

.users-section {
  background: #ffffff;
  border: 1px solid var(--border-color);
  border-radius: var(--radius-sm);
  padding: 20px;
  margin-bottom: 24px;
}

.section-heading {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 16px;
}

.section-heading .eyebrow-label { margin-bottom: 4px; }
.section-heading h2 { font-size: 20px; margin: 0 0 4px; }
.section-heading p { color: var(--text-muted); font-size: 13px; margin: 0; }

.btn-secondary {
  background: #faf8f5;
  border: 1px solid #cfc4b3;
  border-radius: var(--radius-sm);
  color: #57534e;
  cursor: pointer;
  font-size: 12px;
  font-weight: 600;
  padding: 7px 12px;
  white-space: nowrap;
}

.btn-secondary:disabled { cursor: wait; opacity: 0.65; }
.users-state { color: var(--text-muted); padding: 20px 4px; text-align: center; }
.users-error { color: #9d2020; }
.users-table-wrap { overflow-x: auto; }
.users-table { border-collapse: collapse; font-size: 13px; min-width: 720px; width: 100%; }
.users-table th, .users-table td { border-bottom: 1px solid #eee8df; padding: 12px; text-align: left; }
.users-table th { color: #6b6257; font-size: 11px; letter-spacing: 0.06em; text-transform: uppercase; }
.role-badge, .status-badge { border-radius: 999px; display: inline-block; font-size: 11px; font-weight: 700; padding: 3px 8px; text-transform: capitalize; }
.role-badge { background: #f1ece4; color: #57534e; }
.status-badge.active { background: #e4f3e7; color: #276233; }
.status-badge.inactive { background: #f9e5e5; color: #982b2b; }

/* Filter Bar */
.admin-filter-bar {
  background: #ffffff;
  border: 1px solid var(--border-color);
  border-radius: var(--radius-sm);
  padding: 12px 16px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 16px;
  margin-bottom: 32px;
  flex-wrap: wrap;
}

.status-tabs {
  display: flex;
  gap: 6px;
}

.status-tab-btn {
  background: #faf8f5;
  border: 1px solid #e7e0d5;
  color: #57534e;
  padding: 6px 12px;
  border-radius: var(--radius-sm);
  font-size: 12px;
  font-weight: 600;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  gap: 6px;
  transition: all 0.15s ease;
}

.status-tab-btn:hover {
  border-color: #c89b3c;
}

.status-tab-btn.active {
  background: #7e2222;
  color: #ffffff;
  border-color: #7e2222;
}

.tab-count {
  background: rgba(0, 0, 0, 0.08);
  font-size: 10px;
  padding: 1px 6px;
  border-radius: 9999px;
}

.status-tab-btn.active .tab-count {
  background: rgba(255, 255, 255, 0.25);
  color: #ffffff;
}

.admin-search-wrap input {
  padding: 7px 12px;
  border: 1px solid var(--border-color);
  border-radius: var(--radius-sm);
  font-size: 12px;
  min-width: 240px;
  outline: none;
}

.admin-cases-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 24px;
}

.loading-state, .empty-state {
  text-align: center;
  padding: 60px 20px;
  color: var(--text-muted);
}

.empty-icon {
  font-size: 32px;
  margin-bottom: 12px;
}

@media (max-width: 960px) {
  .admin-cases-grid { grid-template-columns: repeat(2, 1fr); }
}

@media (max-width: 640px) {
  .admin-header { flex-direction: column; align-items: flex-start; gap: 14px; }
  .section-heading { flex-direction: column; }
  .admin-cases-grid { grid-template-columns: 1fr; }
  .admin-filter-bar { flex-direction: column; align-items: stretch; }
}
</style>
