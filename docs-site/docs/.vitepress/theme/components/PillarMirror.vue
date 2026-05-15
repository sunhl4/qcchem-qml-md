<script setup lang="ts">
import { computed, ref } from "vue";
import data from "../../mirror-data.json";
import StatusBadge from "./StatusBadge.vue";

const props = defineProps<{
  pillar: "P1" | "P2" | "P3" | "P4" | "meta";
  locale?: "zh" | "en";
  /** Cap rows shown initially; user can expand to show all */
  initial?: number;
}>();

const allEntries = (data as any).entries as Array<any>;

const inPillar = computed(() => allEntries.filter((e) => e.pillar === props.pillar));

const counts = computed(() => {
  const c: Record<string, number> = { shipped: 0, partial: 0, placeholder: 0, "not-applicable": 0, total: inPillar.value.length };
  for (const e of inPillar.value) c[e.status] = (c[e.status] ?? 0) + 1;
  return c;
});

const expanded = ref(false);
const cap = computed(() => props.initial ?? 12);
const visible = computed(() =>
  expanded.value ? inPillar.value : inPillar.value.slice(0, cap.value)
);

function href(e: any) {
  const base = (props.locale ?? "zh") === "zh" ? "" : "/en";
  return `${base}/mirror/${e.breadcrumb.join("/")}/`;
}

function label(e: any) {
  return (props.locale ?? "zh") === "zh" ? e.title_zh : e.title_en;
}

function pathLabel(e: any) {
  return e.breadcrumb.slice(0, -1).join(" / ");
}

const STATUS_KEYS = ["shipped", "partial", "placeholder", "not-applicable"];
</script>

<template>
  <section class="qcs-pmirror">
    <header>
      <h3 v-if="(props.locale ?? 'zh') === 'zh'">本柱在参考文档镜像中的对应节点</h3>
      <h3 v-else>Reference-doc mirror nodes in this pillar</h3>
      <p class="qcs-pmirror__counts">
        <StatusBadge v-for="s in STATUS_KEYS" :key="s" :status="s" :locale="props.locale ?? 'zh'" />
        <span class="qcs-pmirror__count" v-for="s in STATUS_KEYS" :key="`c-${s}`">
          <strong>{{ counts[s] ?? 0 }}</strong> {{ s }}
        </span>
        <span class="qcs-pmirror__count qcs-pmirror__count--sum">
          {{ (props.locale ?? "zh") === "zh" ? "总计" : "Total" }} <strong>{{ counts.total }}</strong>
        </span>
      </p>
    </header>

    <ul class="qcs-pmirror__list">
      <li v-for="e in visible" :key="e.breadcrumb.join('/')">
        <a :href="href(e)">{{ label(e) }}</a>
        <StatusBadge :status="e.status" :locale="props.locale ?? 'zh'" />
        <span class="qcs-pmirror__path">{{ pathLabel(e) }}</span>
        <code v-if="e.qchem" class="qcs-pmirror__module">{{ e.qchem }}</code>
      </li>
    </ul>

    <button v-if="inPillar.length > cap" class="qcs-pmirror__toggle" @click="expanded = !expanded">
      <template v-if="(props.locale ?? 'zh') === 'zh'">
        {{ expanded ? "收起" : `展开剩余 ${inPillar.length - cap} 条` }}
      </template>
      <template v-else>
        {{ expanded ? "Collapse" : `Show ${inPillar.length - cap} more` }}
      </template>
    </button>
  </section>
</template>

<style scoped>
.qcs-pmirror {
  margin: 1.4rem 0;
  border: 1px solid var(--vp-c-divider);
  border-radius: 12px;
  background: var(--vp-c-bg-soft);
  padding: 1rem 1.1rem;
}
.qcs-pmirror header {
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
  margin-bottom: 0.6rem;
}
.qcs-pmirror header h3 {
  margin: 0;
  font-size: 1.05em;
  border: none;
  padding: 0;
}
.qcs-pmirror__counts {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5em;
  align-items: center;
  font-size: 0.85em;
  color: var(--vp-c-text-2);
  margin: 0;
}
.qcs-pmirror__count {
  font-variant-numeric: tabular-nums;
  padding: 0.05em 0.5em;
  border-radius: 6px;
  background: color-mix(in srgb, var(--vp-c-text-1) 6%, transparent);
}
.qcs-pmirror__count--sum {
  background: color-mix(in srgb, var(--vp-c-brand-1) 14%, transparent);
  color: var(--vp-c-brand-1);
  font-weight: 600;
}
.qcs-pmirror__list {
  list-style: none;
  margin: 0;
  padding: 0;
}
.qcs-pmirror__list li {
  display: flex;
  align-items: center;
  gap: 0.5em;
  padding: 0.4em 0;
  border-top: 1px dashed var(--vp-c-divider-light);
  flex-wrap: wrap;
}
.qcs-pmirror__list li:first-child { border-top: none; }
.qcs-pmirror__list li a {
  font-weight: 500;
  text-decoration: none;
  color: var(--vp-c-text-1);
}
.qcs-pmirror__list li a:hover { color: var(--vp-c-brand-1); }
.qcs-pmirror__path {
  color: var(--vp-c-text-3);
  font-size: 0.82em;
  margin-left: 0.2em;
}
.qcs-pmirror__module {
  color: var(--vp-c-text-2);
  font-size: 0.8em;
  background: var(--vp-c-bg);
  border: 1px solid var(--vp-c-divider-light);
  border-radius: 4px;
  padding: 0 0.35em;
}
.qcs-pmirror__toggle {
  margin-top: 0.7rem;
  background: transparent;
  border: 1px solid var(--vp-c-divider);
  border-radius: 999px;
  padding: 0.25em 0.9em;
  cursor: pointer;
  color: var(--vp-c-brand-1);
  font-size: 0.85em;
  font-weight: 600;
}
.qcs-pmirror__toggle:hover {
  background: color-mix(in srgb, var(--vp-c-brand-1) 12%, transparent);
}
</style>
