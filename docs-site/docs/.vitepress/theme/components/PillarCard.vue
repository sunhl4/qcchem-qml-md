<script setup lang="ts">
defineProps<{
  id: string;
  title: string;
  subtitle?: string;
  link: string;
  cta?: string;
  icon?: string;
}>();
</script>

<template>
  <a class="qcs-pillar" :href="link">
    <div class="qcs-pillar__head">
      <span class="qcs-pillar__id">{{ id }}</span>
      <span class="qcs-pillar__icon" v-if="icon">{{ icon }}</span>
    </div>
    <h3 class="qcs-pillar__title">{{ title }}</h3>
    <p class="qcs-pillar__subtitle" v-if="subtitle">{{ subtitle }}</p>
    <span class="qcs-pillar__cta">{{ cta ?? "→" }}</span>
  </a>
</template>

<style scoped>
.qcs-pillar {
  display: flex;
  flex-direction: column;
  gap: 0.6rem;
  padding: 1.2rem 1.3rem 1.1rem;
  border-radius: 14px;
  border: 1px solid var(--vp-c-divider);
  background: linear-gradient(180deg,
    color-mix(in srgb, var(--vp-c-brand-1) 6%, transparent),
    transparent 60%);
  text-decoration: none;
  color: inherit;
  transition: transform 0.2s ease, box-shadow 0.2s ease, border-color 0.2s ease;
  min-height: 170px;
}
.qcs-pillar:hover {
  transform: translateY(-3px);
  box-shadow: 0 16px 32px -20px color-mix(in srgb, var(--vp-c-brand-1) 70%, transparent);
  border-color: color-mix(in srgb, var(--vp-c-brand-1) 60%, var(--vp-c-divider));
}
.qcs-pillar__head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-size: 0.85em;
  font-weight: 600;
  letter-spacing: 0.04em;
}
.qcs-pillar__id {
  color: var(--vp-c-brand-1);
}
.qcs-pillar__icon {
  font-size: 1.6em;
  line-height: 1;
}
.qcs-pillar__title {
  margin: 0;
  font-size: 1.18em;
  font-weight: 700;
  letter-spacing: -0.01em;
}
.qcs-pillar__subtitle {
  margin: 0;
  font-size: 0.95em;
  line-height: 1.5;
  color: var(--vp-c-text-2);
}
.qcs-pillar__cta {
  margin-top: auto;
  align-self: flex-start;
  color: var(--vp-c-brand-1);
  font-weight: 600;
}
</style>
