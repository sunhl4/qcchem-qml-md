<script setup lang="ts">
import { useRoute } from "vitepress";
import { computed } from "vue";

const route = useRoute();
const segments = computed(() => {
  const parts = route.path.replace(/\/+$/, "").split("/").filter(Boolean);
  const acc: { text: string; href: string }[] = [];
  let cursor = "";
  for (const seg of parts) {
    cursor += "/" + seg;
    acc.push({ text: decodeURIComponent(seg), href: cursor + "/" });
  }
  return acc;
});
</script>

<template>
  <nav v-if="segments.length" class="qcs-breadcrumbs" aria-label="breadcrumb">
    <a href="/">~</a>
    <template v-for="(s, i) in segments" :key="s.href">
      <span class="sep">/</span>
      <a :href="s.href">{{ s.text }}</a>
    </template>
  </nav>
</template>

<style scoped>
.qcs-breadcrumbs {
  font-size: 0.85em;
  color: var(--vp-c-text-2);
  margin: 0 0 0.6rem;
}
.qcs-breadcrumbs a {
  color: inherit;
  text-decoration: none;
}
.qcs-breadcrumbs a:hover {
  color: var(--vp-c-brand-1);
}
.qcs-breadcrumbs .sep {
  margin: 0 0.4em;
  color: var(--vp-c-text-3);
}
</style>
