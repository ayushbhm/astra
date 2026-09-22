<template>
  <div class="cases-page">
    <!-- Page Header -->
    <div class="cases-header">
      <div>
        <span class="eyebrow-label">ARCHIVAL CATALOG</span>
        <h1 class="page-title">Astrological Charts Library</h1>
        <p class="page-subtitle">
          Real-life verified horoscopes and biographical timelines.
        </p>
      </div>

      <div class="stats-counter">
        <span class="counter-num">{{ filteredCases.length }}</span>
        <span class="counter-label">Charts Displayed</span>
      </div>
    </div>

    <!-- Search & Filter Controls -->
    <div class="filter-controls-bar">
      <div class="search-input-wrap">
        <span class="search-icon">🔍</span>
        <input 
          type="text" 
          placeholder="Search by topic, city, keyword, or planetary position (e.g. Pune, Rahu, Marriage)..." 
          v-model="searchQuery"
          @input="handleSearch"
        />
        <button v-if="searchQuery" class="btn-clear" @click="searchQuery = ''; handleSearch()">✕</button>
      </div>

      <!-- Tag Filters -->
      <div class="tag-filters-row">
        <button 
          class="tag-filter-btn" 
          :class="{ active: selectedTag === '' }"
          @click="setTag('')"
        >
          All Topics
        </button>
        <button 
          v-for="t in availableTags" 
          :key="t" 
          class="tag-filter-btn"
          :class="{ active: selectedTag === t }"
          @click="setTag(t)"
        >
          {{ t }}
        </button>

        <!-- Verified Only Toggle -->
        <button 
          class="verified-toggle-btn" 
          :class="{ active: verifiedOnly }"
          @click="toggleVerifiedOnly"
        >
          <span>{{ verifiedOnly ? '✓' : '○' }}</span>
          <span>Verified Only</span>
        </button>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="loading-state">
      <span class="loading-spinner"></span>
      <p>Loading charts from repository...</p>
    </div>

    <!-- Empty State -->
    <div v-else-if="filteredCases.length === 0" class="empty-state">
      <div class="empty-icon">✦</div>
      <h3>No matching astrological charts found</h3>
      <p>Try adjusting your search keywords or clearing tag filters.</p>
      <button class="btn-outline btn-sm" @click="resetFilters">Reset Filters</button>
    </div>

    <!-- Cards Grid -->
    <div v-else class="cases-grid">
      <CaseCard 
        v-for="c in filteredCases" 
        :key="c.id" 
        :chart="c"
        @view="openCaseModal"
      />
    </div>

    <!-- Case Detail Modal -->
    <CaseModal 
      :chart="selectedCase" 
      @close="selectedCase = null" 
    />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import CaseCard from '../components/CaseCard.vue'
import CaseModal from '../components/CaseModal.vue'
import { userService } from '../services/userService'

const loading = ref(false)
const cases = ref([])
const filteredCases = ref([])

const searchQuery = ref('')
const selectedTag = ref('')
const verifiedOnly = ref(false)
const selectedCase = ref(null)

const availableTags = [
  'Career Pivot',
  'Marriage',
  'Foreign Travel',
  'Business',
  'Health',
  'Rahu Dasha'
]

const loadCases = async () => {
  loading.value = true
  try {
    const data = await userService.getCases()
    cases.value = data
    applyFilters()
  } catch (err) {
    console.error('Failed to load charts:', err)
  } finally {
    loading.value = false
  }
}

const applyFilters = () => {
  let result = [...cases.value]

  if (searchQuery.value.trim()) {
    const q = searchQuery.value.trim().toLowerCase()
    result = result.filter(c => 
      (c.title && c.title.toLowerCase().includes(q)) ||
      (c.place && c.place.toLowerCase().includes(q)) ||
      (c.state && c.state.toLowerCase().includes(q)) ||
      (c.story && c.story.toLowerCase().includes(q)) ||
      (c.tags && c.tags.some(t => t.toLowerCase().includes(q)))
    )
  }

  if (selectedTag.value) {
    result = result.filter(c => c.tags && c.tags.includes(selectedTag.value))
  }

  if (verifiedOnly.value) {
    result = result.filter(c => c.verification_status === 'VERIFIED')
  }

  filteredCases.value = result
}

const handleSearch = () => {
  applyFilters()
}

const setTag = (tag) => {
  selectedTag.value = tag
  applyFilters()
}

const toggleVerifiedOnly = () => {
  verifiedOnly.value = !verifiedOnly.value
  applyFilters()
}

const resetFilters = () => {
  searchQuery.value = ''
  selectedTag.value = ''
  verifiedOnly.value = false
  applyFilters()
}

const openCaseModal = (chart) => {
  selectedCase.value = chart
}

onMounted(() => {
  loadCases()
})
</script>

<style scoped>
.cases-page {
  max-width: 1200px;
  margin: 0 auto;
  padding: 40px 24px 80px;
}

.cases-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  border-bottom: 1px solid #e7e0d5;
  padding-bottom: 20px;
  margin-bottom: 28px;
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

.stats-counter {
  text-align: right;
}

.counter-num {
  font-family: var(--font-serif);
  font-size: 24px;
  font-weight: 700;
  color: #b45309;
  display: block;
}

.counter-label {
  font-size: 10px;
  color: var(--text-light);
  letter-spacing: 0.05em;
  text-transform: uppercase;
}

/* Filter Controls */
.filter-controls-bar {
  background: #ffffff;
  border: 1px solid var(--border-color);
  border-radius: var(--radius-sm);
  padding: 16px;
  margin-bottom: 32px;
  box-shadow: 0 1px 3px rgba(36, 31, 26, 0.03);
}

.search-input-wrap {
  display: flex;
  align-items: center;
  gap: 10px;
  border-bottom: 1px solid #f0ebe3;
  padding-bottom: 12px;
  margin-bottom: 12px;
}

.search-icon {
  font-size: 14px;
  color: var(--text-light);
}

.search-input-wrap input {
  flex: 1;
  border: none;
  outline: none;
  font-family: var(--font-sans);
  font-size: 13px;
  color: var(--text-main);
  background: transparent;
}

.btn-clear {
  background: none;
  border: none;
  font-size: 12px;
  color: #9c9385;
  cursor: pointer;
}

.tag-filters-row {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

.tag-filter-btn {
  background: #faf8f5;
  border: 1px solid #e7e0d5;
  color: #57534e;
  padding: 5px 12px;
  border-radius: var(--radius-sm);
  font-size: 12px;
  cursor: pointer;
  transition: all 0.15s ease;
}

.tag-filter-btn:hover {
  border-color: #c89b3c;
}

.tag-filter-btn.active {
  background: #7e2222;
  color: #ffffff;
  border-color: #7e2222;
}

.verified-toggle-btn {
  margin-left: auto;
  background: #f0fdf4;
  border: 1px solid #bbf7d0;
  color: #15803d;
  padding: 5px 12px;
  border-radius: var(--radius-sm);
  font-size: 12px;
  font-weight: 600;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  gap: 6px;
}

.verified-toggle-btn.active {
  background: #15803d;
  color: #ffffff;
  border-color: #15803d;
}

/* Cases Grid */
.cases-grid {
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
  font-size: 28px;
  color: #c89b3c;
  margin-bottom: 12px;
}

@media (max-width: 960px) {
  .cases-grid { grid-template-columns: repeat(2, 1fr); }
}

@media (max-width: 640px) {
  .cases-grid { grid-template-columns: 1fr; }
  .cases-header { flex-direction: column; align-items: flex-start; gap: 12px; }
  .stats-counter { text-align: left; }
  .verified-toggle-btn { margin-left: 0; }
}
</style>
