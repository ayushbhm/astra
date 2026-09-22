<template>
  <div v-if="isOpen" class="modal-overlay" @click.self="$emit('close')">
    <div class="modal-box">
      <div class="modal-head">
        <h3>{{ isEdit ? 'Edit Chart' : 'Add Astrological Chart' }}</h3>
        <button class="btn-close" @click="$emit('close')">✕</button>
      </div>

      <form @submit.prevent="submit" class="modal-body">
        <div class="field">
          <label>Case Title / Headline *</label>
          <input type="text" v-model="form.title" required placeholder="e.g. Career Pivot to Vedic Counseling" />
        </div>

        <div class="row">
          <div class="field">
            <label>DOB *</label>
            <input type="date" v-model="form.dob" required />
          </div>
          <div class="field">
            <label>TOB</label>
            <input type="time" v-model="form.tob" />
          </div>
        </div>

        <div class="row">
          <div class="field">
            <label>Place / City *</label>
            <input type="text" v-model="form.place" required placeholder="e.g. Pune" />
          </div>
          <div class="field">
            <label>State *</label>
            <input type="text" v-model="form.state" required placeholder="e.g. Maharashtra" />
          </div>
        </div>

        <div class="field">
          <label>Gender *</label>
          <select v-model="form.gender" required>
            <option value="Female">Female</option>
            <option value="Male">Male</option>
            <option value="Other">Other</option>
          </select>
        </div>

        <div class="field">
          <label>Life Story &amp; Events *</label>
          <textarea v-model="form.story" rows="4" required placeholder="Life story and verified chronological events..."></textarea>
        </div>

        <div class="field">
          <label>Tags (comma separated)</label>
          <input type="text" v-model="tagsInput" placeholder="e.g. Career Pivot, Rahu Dasha, Foreign Travel" />
        </div>

        <div class="modal-foot">
          <button type="button" class="btn-cancel" @click="$emit('close')">Cancel</button>
          <button type="submit" class="btn-save">{{ isEdit ? 'Update' : 'Submit Chart' }}</button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, watch } from 'vue'

const props = defineProps({
  isOpen: Boolean,
  initialData: Object,
  isEdit: Boolean
})

const emit = defineEmits(['close', 'save'])

const tagsInput = ref('')
const form = reactive({
  title: '',
  dob: '',
  tob: '',
  gender: 'Female',
  place: '',
  state: '',
  story: ''
})

watch(() => props.initialData, (val) => {
  if (val) {
    Object.assign(form, val)
    tagsInput.value = val.tags ? val.tags.join(', ') : ''
  } else {
    Object.assign(form, { title: '', dob: '', tob: '', gender: 'Female', place: '', state: '', story: '' })
    tagsInput.value = ''
  }
}, { immediate: true })

const submit = () => {
  const tags = tagsInput.value.split(',').map(t => t.trim()).filter(Boolean)
  emit('save', { ...form, tags })
}
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(0, 0, 0, 0.4);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 16px;
  z-index: 1000;
}

.modal-box {
  background: #ffffff;
  border: 1px solid #e7e0d5;
  border-radius: 4px;
  width: 100%;
  max-width: 500px;
  padding: 20px;
}

.modal-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid #eee;
  padding-bottom: 8px;
  margin-bottom: 14px;
}

.modal-head h3 { margin: 0; font-size: 16px; }
.btn-close { background: none; border: none; font-size: 16px; cursor: pointer; }

.field {
  margin-bottom: 12px;
}

.field label {
  display: block;
  font-size: 11px;
  font-weight: 600;
  margin-bottom: 4px;
  color: #57534e;
}

.field input, .field select, .field textarea {
  width: 100%;
  padding: 8px;
  border: 1px solid #d6d3d1;
  border-radius: 4px;
  font-size: 13px;
  box-sizing: border-box;
}

.row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
}

.modal-foot {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
  margin-top: 16px;
}

.btn-cancel {
  background: none;
  border: 1px solid #d6d3d1;
  padding: 6px 14px;
  border-radius: 4px;
  cursor: pointer;
}

.btn-save {
  background: #7e2222;
  color: white;
  border: none;
  padding: 6px 16px;
  border-radius: 4px;
  cursor: pointer;
}
</style>
