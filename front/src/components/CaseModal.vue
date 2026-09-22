<template>
  <div v-if="chart" class="modal-overlay" @click.self="$emit('close')">
    <article class="modal-box">
      <button class="btn-close" @click="$emit('close')" aria-label="Close">×</button>
      <span class="eyebrow">CHART RECORD</span>
      <h2>{{ chart.title || `Chart #${chart.id}` }}</h2>
      <p class="details">Born {{ chart.dob }}<template v-if="chart.tob"> at {{ chart.tob }}</template> · {{ chart.place }}, {{ chart.state }}</p>
      <p>{{ chart.story }}</p>
      <div class="tags"><span v-for="tag in chart.tags" :key="tag">{{ tag }}</span></div>
    </article>
  </div>
</template>

<script setup>
defineProps({ chart: { type: Object, default: null } })
defineEmits(['close'])
</script>

<style scoped>
.modal-overlay { position: fixed; inset: 0; z-index: 1000; display: grid; place-items: center; padding: 20px; background: rgb(0 0 0 / 45%); }
.modal-box { position: relative; width: min(620px, 100%); padding: 30px; border-radius: 5px; background: #fff; color: #241f1a; }
.btn-close { position: absolute; right: 14px; top: 10px; border: 0; background: none; font-size: 24px; cursor: pointer; }
.eyebrow { color: #7e2222; font-size: 11px; font-weight: 700; letter-spacing: .12em; }
h2 { margin: 8px 30px 10px 0; font-family: var(--font-serif); }
.details { color: #78716c; font-size: 13px; }.tags { display: flex; flex-wrap: wrap; gap: 6px; margin-top: 18px; }.tags span { padding: 3px 8px; background: #f5f0e8; font-size: 11px; }
</style>
