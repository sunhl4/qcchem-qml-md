<script setup lang="ts">
import { computed } from "vue";

const props = defineProps<{
  status?: string;
  locale?: "zh" | "en";
}>();

const LABELS: Record<string, { zh: string; en: string; tone: string }> = {
  shipped: { zh: "已落地", en: "Shipped", tone: "ok" },
  partial: { zh: "部分对齐", en: "Partial", tone: "warn" },
  placeholder: { zh: "占位", en: "Placeholder", tone: "info" },
  "not-applicable": { zh: "刻意不做", en: "Not applicable", tone: "muted" },
};

const meta = computed(() => LABELS[props.status ?? ""] ?? null);
const label = computed(() => {
  if (!meta.value) return props.status ?? "";
  return (props.locale ?? "zh") === "zh" ? meta.value.zh : meta.value.en;
});
const tone = computed(() => meta.value?.tone ?? "muted");
</script>

<template>
  <span v-if="meta" class="qcs-status" :data-tone="tone" :title="status">
    <span class="dot" />
    {{ label }}
  </span>
</template>

<style scoped>
.qcs-status {
  display: inline-flex;
  align-items: center;
  gap: 0.4em;
  padding: 0.15em 0.6em;
  border-radius: 999px;
  font-size: 0.8em;
  font-weight: 600;
  letter-spacing: 0.02em;
  border: 1px solid var(--qcs-border, rgba(120, 120, 120, 0.25));
  background: var(--qcs-bg, rgba(120, 120, 120, 0.08));
  color: var(--qcs-fg, var(--vp-c-text-1));
  vertical-align: middle;
  margin-left: 0.35em;
}
.dot {
  width: 0.5em;
  height: 0.5em;
  border-radius: 50%;
  background: currentColor;
  display: inline-block;
}
.qcs-status[data-tone="ok"] {
  --qcs-bg: color-mix(in srgb, #16a34a 16%, transparent);
  --qcs-border: color-mix(in srgb, #16a34a 50%, transparent);
  --qcs-fg: #15803d;
}
.qcs-status[data-tone="warn"] {
  --qcs-bg: color-mix(in srgb, #f59e0b 18%, transparent);
  --qcs-border: color-mix(in srgb, #f59e0b 55%, transparent);
  --qcs-fg: #b45309;
}
.qcs-status[data-tone="info"] {
  --qcs-bg: color-mix(in srgb, #3b82f6 18%, transparent);
  --qcs-border: color-mix(in srgb, #3b82f6 50%, transparent);
  --qcs-fg: #1d4ed8;
}
.qcs-status[data-tone="muted"] {
  --qcs-bg: color-mix(in srgb, #6b7280 18%, transparent);
  --qcs-border: color-mix(in srgb, #6b7280 45%, transparent);
  --qcs-fg: #4b5563;
}
.dark .qcs-status[data-tone="ok"] {
  --qcs-fg: #4ade80;
}
.dark .qcs-status[data-tone="warn"] {
  --qcs-fg: #fbbf24;
}
.dark .qcs-status[data-tone="info"] {
  --qcs-fg: #60a5fa;
}
.dark .qcs-status[data-tone="muted"] {
  --qcs-fg: #cbd5f5;
}
</style>
