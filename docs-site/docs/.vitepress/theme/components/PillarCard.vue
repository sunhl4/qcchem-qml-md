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
  <a class="qcs-pillar" :href="link" :data-pillar="id">
    <div class="qcs-pillar__head">
      <span class="qcs-pillar__id">{{ id }}</span>
      <span class="qcs-pillar__icon" v-if="icon" aria-hidden="true">{{ icon }}</span>
    </div>
    <h3 class="qcs-pillar__title">{{ title }}</h3>
    <p class="qcs-pillar__subtitle" v-if="subtitle">{{ subtitle }}</p>
    <span class="qcs-pillar__cta">{{ cta ?? "→" }}</span>
  </a>
</template>

<style scoped>
.qcs-pillar {
  --pillar-line: var(--vp-c-brand-1);
  display: flex;
  flex-direction: column;
  gap: 0.55rem;
  padding: 1.25rem 1.35rem 1.15rem;
  border-radius: 14px;
  border: 1px solid var(--vp-c-divider);
  border-left: 3px solid var(--pillar-line);
  background: var(--vp-c-bg-soft);
  text-decoration: none;
  color: inherit;
  transition: transform 0.18s ease, box-shadow 0.18s ease, border-color 0.18s ease,
    background 0.18s ease;
  min-height: 158px;
  box-shadow: 0 1px 0 rgba(255, 255, 255, 0.03) inset;
}

.qcs-pillar[data-pillar="P1"] {
  --pillar-line: #22d3ee;
}
.qcs-pillar[data-pillar="P2"] {
  --pillar-line: #a78bfa;
}
.qcs-pillar[data-pillar="P3"] {
  --pillar-line: #34d399;
}
.qcs-pillar[data-pillar="P4"] {
  --pillar-line: #fbbf24;
}

.qcs-pillar:hover {
  transform: translateY(-2px);
  background: var(--vp-c-bg-alt);
  box-shadow: 0 20px 44px -28px rgba(0, 0, 0, 0.85);
  border-color: color-mix(in srgb, var(--pillar-line) 28%, var(--vp-c-divider));
}

.qcs-pillar__head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  min-height: 1.5em;
}

.qcs-pillar__id {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 2.25rem;
  padding: 0.2em 0.5em;
  border-radius: 6px;
  font-size: 0.72rem;
  font-weight: 800;
  letter-spacing: 0.06em;
  color: var(--vp-c-text-1);
  background: color-mix(in srgb, var(--pillar-line) 22%, var(--vp-c-bg-elv));
  border: 1px solid color-mix(in srgb, var(--pillar-line) 35%, transparent);
}

.qcs-pillar__icon {
  font-size: 1.45em;
  line-height: 1;
  opacity: 0.9;
}

.qcs-pillar__title {
  margin: 0;
  font-size: 1.08rem;
  font-weight: 700;
  letter-spacing: -0.02em;
  line-height: 1.25;
}

.qcs-pillar__subtitle {
  margin: 0;
  font-size: 0.9rem;
  line-height: 1.5;
  color: var(--vp-c-text-2);
  flex: 1;
}

.qcs-pillar__cta {
  margin-top: 0.25rem;
  align-self: flex-start;
  font-size: 0.82rem;
  color: var(--vp-c-brand-1);
  font-weight: 600;
  letter-spacing: 0.01em;
}

.qcs-pillar:hover .qcs-pillar__cta {
  color: var(--vp-c-brand-2);
}
</style>
