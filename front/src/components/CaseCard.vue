<template>
  <div class="case-card">
    <div class="card-header">
      <button class="card-title" @click="$emit('view', chart)">{{ chart.title || `Chart #${chart.id}` }}</button>
      <div class="badges">
        <span v-if="chart.verification_status === 'VERIFIED'" class="badge badge-verified">
          ✓ Verified
        </span>
        <span v-if="chart.status && chart.status !== 'APPROVED'" class="badge badge-pending">
          {{ chart.status }}
        </span>
      </div>
    </div>

    <!-- Details Grid -->
    <div class="details-row">
      <span><strong>Born:</strong> {{ chart.dob }} {{ chart.tob ? `@ ${chart.tob}` : '' }}</span>
      <span><strong>Place:</strong> {{ chart.place }}, {{ chart.state }}</span>
      <span><strong>Gender:</strong> {{ chart.gender }}</span>
    </div>

    <!-- Story with clean expand -->
    <p class="story-text" :class="{ clamp: !expanded }">
      {{ chart.story }}
    </p>
    <button v-if="chart.story && chart.story.length > 160" class="btn-toggle-story" @click="expanded = !expanded">
      {{ expanded ? 'Show less' : 'Read full story...' }}
    </button>

    <!-- Tags -->
    <div v-if="chart.tags && chart.tags.length" class="tags-list">
      <span v-for="t in chart.tags" :key="t" class="tag">{{ t }}</span>
    </div>

    <!-- Actions -->
    <div v-if="canManage || isAdmin" class="card-actions">
      <button v-if="canManage" class="btn-sm" @click="$emit('edit', chart)">Edit</button>
      <button v-if="canManage" class="btn-sm btn-del" @click="$emit('delete', chart)">Delete</button>

      <!-- Admin Specific Actions -->
      <template v-if="isAdmin">
        <button v-if="chart.status === 'PENDING'" class="btn-sm btn-appr" @click="$emit('approve', chart)">Approve</button>
        <button v-if="chart.status === 'PENDING'" class="btn-sm" @click="$emit('reject', chart)">Reject</button>
        <button class="btn-sm" @click="$emit('toggle-verified', chart)">
          {{ chart.verification_status === 'VERIFIED' ? 'Unverify' : 'Verify' }}
        </button>
      </template>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

defineProps({
  chart: { type: Object, required: true },
  canManage: { type: Boolean, default: false },
  isAdmin: { type: Boolean, default: false }
})

defineEmits(['view', 'edit', 'delete', 'approve', 'reject', 'toggle-verified'])

const expanded = ref(false)
</script>

<style scoped>
.case-card {
  background: #ffffff;
  border: 1px solid #e7e0d5;
  padding: 18px;
  border-radius: 4px;
}

.case-card:hover {
  border-color: #c89b3c;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 10px;
  margin-bottom: 8px;
}

.card-title {
  font-size: 16px;
  margin: 0;
  color: #241f1a;
  background: none;
  border: 0;
  padding: 0;
  text-align: left;
  cursor: pointer;
}

.badges {
  display: flex;
  gap: 4px;
  flex-shrink: 0;
}

.badge {
  font-size: 10px;
  font-weight: 700;
  padding: 2px 6px;
  border-radius: 3px;
}

.badge-verified { background: #dcfce7; color: #15803d; }
.badge-pending { background: #fef3c7; color: #b45309; }

.details-row {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  font-size: 12px;
  color: #57534e;
  background: #faf8f5;
  padding: 6px 10px;
  margin: 10px 0;
}

.story-text {
  font-size: 13px;
  color: #57534e;
  line-height: 1.6;
  margin: 8px 0 4px;
}

.story-text.clamp {
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.btn-toggle-story {
  background: none;
  border: none;
  color: #7e2222;
  font-size: 11px;
  cursor: pointer;
  padding: 0;
  margin-bottom: 8px;
}

.tags-list {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
  margin: 8px 0;
}

.tag {
  font-size: 10px;
  background: #f5f0e8;
  color: #6b6357;
  padding: 2px 6px;
  border-radius: 3px;
}

.card-actions {
  display: flex;
  gap: 6px;
  border-top: 1px solid #f0ebe3;
  padding-top: 10px;
  margin-top: 10px;
}

.btn-sm {
  padding: 4px 8px;
  font-size: 11px;
  cursor: pointer;
  background: #ffffff;
  border: 1px solid #d6d3d1;
  border-radius: 3px;
}

.btn-del { color: #b91c1c; }
.btn-appr { background: #15803d; color: #fff; border-color: #15803d; }
</style>
