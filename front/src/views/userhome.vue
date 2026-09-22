<template>
  <div class="user-page">
    <!-- Header with Quota Notice -->
    <div class="user-header">
      <div>
        <span class="eyebrow-label">STUDENT CONTRIBUTIONS</span>
        <h1 class="page-title">My Submitted Charts</h1>
        <p class="page-subtitle">
          Submit verified birth horoscopes for admin evaluation and inclusion in the public library.
        </p>
      </div>

      <!-- Quota Meter (Max 5 charts allowed) -->
      <div class="quota-meter-box">
        <div class="quota-text">
          <span class="quota-label">Submission Quota:</span>
          <span class="quota-count" :class="{ 'quota-full': quota.count >= 5 }">
            {{ quota.count }} / {{ quota.max }}
          </span>
        </div>
        <div class="quota-progress-bar">
          <div 
            class="quota-fill" 
            :style="{ width: `${(quota.count / quota.max) * 100}%` }"
            :class="{ 'fill-full': quota.count >= 5 }"
          ></div>
        </div>
        <span class="quota-hint">
          {{ quota.canAdd ? `${quota.remaining} submission slot(s) remaining` : 'Maximum limit reached (5 charts max)' }}
        </span>
      </div>
    </div>

    <!-- Action Bar -->
    <div class="user-actions-bar">
      <button 
        class="btn-primary" 
        :disabled="!quota.canAdd"
        @click="openAddModal"
      >
        <span>＋</span> Add New Chart ({{ quota.remaining }} remaining)
      </button>

      <span v-if="!quota.canAdd" class="quota-limit-msg">
        ⚠️ You have reached the maximum allowed 5 charts. You can edit or delete your existing charts below.
      </span>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="loading-state">
      <p>Loading your charts...</p>
    </div>

    <!-- Empty State -->
    <div v-else-if="myCases.length === 0" class="empty-state">
      <div class="empty-icon">📜</div>
      <h3>No charts submitted yet</h3>
      <p>You can contribute up to 5 verified real-life cases for inclusion in the Jyotish Library.</p>
      <button class="btn-primary" @click="openAddModal">Add Your First Chart</button>
    </div>

    <!-- User Charts Grid -->
    <div v-else class="my-cases-grid">
      <CaseCard 
        v-for="c in myCases" 
        :key="c.id" 
        :chart="c"
        :can-manage="true"
        :show-status="true"
        @view="openViewModal"
        @edit="openEditModal"
        @delete="handleDelete"
      />
    </div>

    <!-- Add / Edit Modal -->
    <CaseFormModal 
      :is-open="isFormOpen"
      :initial-data="editingCase"
      :is-edit="!!editingCase"
      :is-admin="false"
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
import { userService } from '../services/userService'

const loading = ref(false)
const saving = ref(false)
const myCases = ref([])
const quota = ref({ count: 0, max: 5, canAdd: true, remaining: 5 })

const isFormOpen = ref(false)
const editingCase = ref(null)
const viewingCase = ref(null)

const loadUserData = async () => {
  loading.value = true
  try {
    myCases.value = await userService.getMyCases()
    quota.value = await userService.getMyQuota()
  } catch (err) {
    console.error('Failed to load user cases:', err)
  } finally {
    loading.value = false
  }
}

const openAddModal = () => {
  if (!quota.value.canAdd) {
    alert('You have reached the maximum allowed limit of 5 charts.')
    return
  }
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
      await userService.updateMyCase(editingCase.value.id, formData)
    } else {
      await userService.addCase(formData)
    }
    isFormOpen.value = false
    await loadUserData()
  } catch (err) {
    alert(err.message || 'Failed to save chart')
  } finally {
    saving.value = false
  }
}

const handleDelete = async (chart) => {
  if (!confirm(`Are you sure you want to remove your chart "${chart.title}"?`)) return
  try {
    await userService.deleteMyCase(chart.id)
    await loadUserData()
  } catch (err) {
    alert(err.message || 'Failed to delete chart')
  }
}

onMounted(() => {
  loadUserData()
})
</script>

<style scoped>
.user-page {
  max-width: 1200px;
  margin: 0 auto;
  padding: 40px 24px 80px;
}

.user-header {
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

.quota-meter-box {
  background: #ffffff;
  border: 1px solid var(--border-color);
  border-radius: var(--radius-sm);
  padding: 12px 18px;
  min-width: 220px;
}

.quota-text {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 6px;
}

.quota-label {
  font-size: 11px;
  font-family: var(--font-serif);
  font-weight: 700;
  color: var(--text-muted);
}

.quota-count {
  font-size: 13px;
  font-weight: 700;
  color: #15803d;
}

.quota-count.quota-full {
  color: #b91c1c;
}

.quota-progress-bar {
  height: 6px;
  background: #f0ebe3;
  border-radius: 9999px;
  overflow: hidden;
  margin-bottom: 4px;
}

.quota-fill {
  height: 100%;
  background: #15803d;
  transition: width 0.3s ease;
}

.quota-fill.fill-full {
  background: #b91c1c;
}

.quota-hint {
  font-size: 10px;
  color: var(--text-light);
  display: block;
  text-align: right;
}

.user-actions-bar {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 32px;
}

.quota-limit-msg {
  font-size: 12px;
  color: #b45309;
  font-weight: 500;
}

.my-cases-grid {
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
  .my-cases-grid { grid-template-columns: repeat(2, 1fr); }
}

@media (max-width: 640px) {
  .user-header { flex-direction: column; align-items: flex-start; gap: 14px; }
  .my-cases-grid { grid-template-columns: 1fr; }
}
</style>