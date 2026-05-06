<script setup lang="ts">
import { useRoute } from "vitepress";
import { computed } from "vue";

const route = useRoute();
const isEn = computed(() => route.path.startsWith("/en/") || route.path === "/en");
const otherHref = computed(() => {
  const p = route.path;
  return isEn.value ? p.replace(/^\/en/, "") || "/" : "/en" + p;
});
</script>

<template>
  <a class="qcs-langswitch" :href="otherHref" :aria-label="isEn ? '切换到中文' : 'Switch to English'">
    <span :data-active="!isEn">中</span>
    <span class="sep">|</span>
    <span :data-active="isEn">EN</span>
  </a>
</template>

<style scoped>
.qcs-langswitch {
  display: inline-flex;
  align-items: center;
  gap: 0.2em;
  padding: 0.28em 0.65em;
  border-radius: 999px;
  border: 1px solid var(--vp-c-divider);
  font-size: 0.8rem;
  font-weight: 500;
  text-decoration: none;
  color: var(--vp-c-text-2);
  background: var(--vp-c-bg-soft);
  transition: border-color 0.15s ease, background 0.15s ease, color 0.15s ease;
}

.qcs-langswitch:hover {
  border-color: color-mix(in srgb, var(--vp-c-brand-1) 40%, var(--vp-c-divider));
  color: var(--vp-c-text-1);
  background: var(--vp-c-bg-alt);
}

.qcs-langswitch [data-active="true"] {
  color: var(--vp-c-brand-1);
  font-weight: 800;
}

.qcs-langswitch .sep {
  color: var(--vp-c-text-3);
  font-weight: 400;
  user-select: none;
}
</style>
