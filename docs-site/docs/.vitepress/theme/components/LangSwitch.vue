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
  gap: 0.25em;
  padding: 0.2em 0.55em;
  border-radius: 999px;
  border: 1px solid var(--vp-c-divider);
  font-size: 0.85em;
  text-decoration: none;
  color: var(--vp-c-text-2);
}
.qcs-langswitch [data-active="true"] {
  color: var(--vp-c-brand-1);
  font-weight: 700;
}
.qcs-langswitch .sep {
  color: var(--vp-c-text-3);
}
</style>
