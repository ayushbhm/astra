<template>
  <!-- Trigger button -->
  <button class="search-trigger" @click="open = true" title="Smart Search">
    ✦ Smart Search
  </button>

  <!-- Overlay -->
  <Teleport to="body">
    <div v-if="open" class="search-overlay" @click.self="close">
      <div class="search-panel">
        <div class="search-head">
          <span class="search-title">Smart Search</span>
          <span class="search-hint">Ranked by relevance across all fields</span>
          <button class="search-close" @click="close">✕</button>
        </div>

        <div class="search-input-row">
          <input
            ref="inputEl"
            v-model="query"
            type="text"
            placeholder="e.g. Rahu Dasha, Pune marriage, career abroad..."
            @input="debounceSearch"
          />
        </div>

        <!-- States -->
        <div v-if="loading" class="search-state">Searching...</div>
        <div v-else-if="searchError" class="search-state search-error" role="alert">{{ searchError }}</div>
        <div v-else-if="query && results.length === 0" class="search-state">No matching charts found.</div>
        <div v-else-if="results.length" class="search-results">
          <div
            v-for="c in results"
            :key="c.id"
            class="search-result-row"
            @click="emit('select', c); close()"
          >
            <div class="res-title">{{ c.title }}</div>
            <div class="res-meta">{{ c.place }}, {{ c.state }} · {{ c.dob }}</div>
            <div class="res-tags">
              <span v-for="t in c.tags" :key="t" class="res-tag">{{ t }}</span>
            </div>
          </div>
        </div>
        <div v-else class="search-state muted">Type to search across all case fields</div>
      </div>
    </div>
  </Teleport>
</template>

<script setup>
import { ref, nextTick, watch } from 'vue'
import { userService } from '../services/userService'

const emit = defineEmits(['select'])

const open = ref(false)
const query = ref('')
const results = ref([])
const loading = ref(false)
const searchError = ref('')
const inputEl = ref(null)

let timer = null

const debounceSearch = () => {
  clearTimeout(timer)
  searchError.value = ''
  if (!query.value.trim()) { results.value = []; return }
  timer = setTimeout(doSearch, 600)
}

const doSearch = async () => {
  loading.value = true
  try {
    results.value = await userService.searchCases(query.value)
  } catch (error) {
    results.value = []
    searchError.value = error.message || 'Smart search is unavailable. Please try again.'
  } finally {
    loading.value = false
  }
}

const close = () => {
  open.value = false
  query.value = ''
  results.value = []
  searchError.value = ''
}

watch(open, async (v) => {
  if (v) {
    await nextTick()
    inputEl.value?.focus()
  }
})
</script>

<style scoped>
.search-trigger {
  background: #faf8f5;
  border: 1px solid #e7e0d5;
  color: #7e2222;
  padding: 6px 14px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 700;
  cursor: pointer;
  letter-spacing: 0.04em;
  transition: background 0.15s;
}
.search-trigger:hover { background: #f0ebe3; }

.search-overlay {
  position: fixed;
  inset: 0;
  background: rgba(36, 31, 26, 0.45);
  z-index: 1000;
  display: flex;
  align-items: flex-start;
  justify-content: center;
  padding-top: 80px;
}

.search-panel {
  background: #fff;
  border-radius: 8px;
  width: 100%;
  max-width: 640px;
  box-shadow: 0 8px 40px rgba(36,31,26,0.18);
  overflow: hidden;
}

.search-head {
  display: flex;
  align-items: baseline;
  gap: 10px;
  padding: 16px 20px 12px;
  border-bottom: 1px solid #f0ebe3;
}
.search-title { font-weight: 700; font-size: 14px; color: #241f1a; }
.search-hint { font-size: 11px; color: #9c9385; flex: 1; }
.search-close {
  background: none; border: none; color: #9c9385;
  font-size: 14px; cursor: pointer; padding: 0;
}

.search-input-row {
  padding: 12px 20px;
  border-bottom: 1px solid #f0ebe3;
}
.search-input-row input {
  width: 100%;
  border: none;
  outline: none;
  font-size: 15px;
  color: #241f1a;
  background: transparent;
}

.search-state {
  padding: 24px 20px;
  text-align: center;
  font-size: 13px;
  color: #57534e;
}
.search-state.muted { color: #c4b9a8; }
.search-state.search-error { color: #b91c1c; }

.search-results { max-height: 400px; overflow-y: auto; }

.search-result-row {
  padding: 12px 20px;
  cursor: pointer;
  border-bottom: 1px solid #faf8f5;
  transition: background 0.1s;
}
.search-result-row:hover { background: #faf8f5; }

.res-title { font-weight: 600; font-size: 13px; color: #241f1a; }
.res-meta { font-size: 11px; color: #78716c; margin-top: 2px; }
.res-tags { display: flex; gap: 5px; flex-wrap: wrap; margin-top: 5px; }
.res-tag {
  background: #f5f0ea;
  color: #7e2222;
  font-size: 10px;
  padding: 2px 7px;
  border-radius: 9999px;
}
</style>
