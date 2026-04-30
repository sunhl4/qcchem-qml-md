<script setup lang="ts">
import { computed } from "vue";
import data from "../../mirror-data.json";
import StatusBadge from "./StatusBadge.vue";

/**
 * Lists descendants of a given breadcrumb prefix from the mirror manifest.
 * Used by section / sub-section landing pages so the listing is always
 * synchronized with the manifest (no hand-maintained child lists).
 */
const props = defineProps<{
  /** Breadcrumb prefix as an array of slugs, e.g. ["manual"] or ["api","ansatzes"] */
  prefix: string[];
  locale?: "zh" | "en";
  /** When true, group descendants by their next-level segment */
  grouped?: boolean;
}>();

const allEntries = (data as any).entries as Array<any>;

const descendants = computed(() => {
  const p = props.prefix;
  return allEntries.filter((e) => {
    if (e.breadcrumb.length <= p.length) return false;
    for (let i = 0; i < p.length; i++) {
      if (e.breadcrumb[i] !== p[i]) return false;
    }
    return true;
  });
});

const counts = computed(() => {
  const c: Record<string, number> = { shipped: 0, partial: 0, placeholder: 0, "not-applicable": 0, total: descendants.value.length };
  for (const e of descendants.value) c[e.status] = (c[e.status] ?? 0) + 1;
  return c;
});

const groups = computed(() => {
  if (!props.grouped) return null;
  const map: Record<string, any[]> = {};
  for (const e of descendants.value) {
    const k = e.breadcrumb[props.prefix.length];
    map[k] = map[k] ?? [];
    map[k].push(e);
  }
  return Object.entries(map).map(([k, rows]) => ({
    key: k,
    title: rows.find((r) => r.breadcrumb.length === props.prefix.length + 1)
      ? ((props.locale ?? "zh") === "zh"
        ? rows.find((r) => r.breadcrumb.length === props.prefix.length + 1)?.title_zh
        : rows.find((r) => r.breadcrumb.length === props.prefix.length + 1)?.title_en) ?? k
      : k,
    rows,
    counts: rows.reduce<Record<string, number>>((acc, r) => {
      acc[r.status] = (acc[r.status] ?? 0) + 1;
      acc.total = (acc.total ?? 0) + 1;
      return acc;
    }, { shipped: 0, partial: 0, placeholder: 0, "not-applicable": 0, total: 0 }),
  }));
});

function href(e: any) {
  const base = (props.locale ?? "zh") === "zh" ? "" : "/en";
  return `${base}/mirror/${e.breadcrumb.join("/")}/`;
}

function label(e: any) {
  return (props.locale ?? "zh") === "zh" ? e.title_zh : e.title_en;
}

const STATUS_KEYS = ["shipped", "partial", "placeholder", "not-applicable"];
</script>

<template>
  <section class="qcs-branch">
    <p class="qcs-branch__counts">
      <span v-for="s in STATUS_KEYS" :key="s" class="qcs-branch__count">
        <StatusBadge :status="s" :locale="props.locale ?? 'zh'" />
        <strong>{{ counts[s] ?? 0 }}</strong>
      </span>
      <span class="qcs-branch__count qcs-branch__count--sum">
        {{ (props.locale ?? "zh") === "zh" ? "总计" : "Total" }}
        <strong>{{ counts.total }}</strong>
      </span>
    </p>

    <template v-if="groups">
      <details v-for="g in groups" :key="g.key" class="qcs-branch__group" open>
        <summary>
          <span class="title">{{ g.title }}</span>
          <span class="qcs-branch__chips">
            <StatusBadge v-for="s in STATUS_KEYS" :key="s" :status="s" :locale="props.locale ?? 'zh'" v-show="g.counts[s] > 0" />
            <span class="qcs-branch__total">{{ g.counts.total }}</span>
          </span>
        </summary>
        <ul>
          <li v-for="e in g.rows" :key="e.breadcrumb.join('/')">
            <a :href="href(e)">{{ label(e) }}</a>
            <StatusBadge :status="e.status" :locale="props.locale ?? 'zh'" />
            <code v-if="e.qchem" class="muted">{{ e.qchem }}</code>
            <span v-if="e.isClassLeaf" class="qcs-branch__leaf">class</span>
          </li>
        </ul>
      </details>
    </template>

    <ul v-else class="qcs-branch__flat">
      <li v-for="e in descendants" :key="e.breadcrumb.join('/')">
        <a :href="href(e)">{{ label(e) }}</a>
        <StatusBadge :status="e.status" :locale="props.locale ?? 'zh'" />
        <code v-if="e.qchem" class="muted">{{ e.qchem }}</code>
        <span class="qcs-branch__path">{{ e.breadcrumb.join(" / ") }}</span>
      </li>
    </ul>
  </section>
</template>

<style scoped>
.qcs-branch { margin: 1.2rem 0; }
.qcs-branch__counts {
  display: flex;
  flex-wrap: wrap;
  gap: 0.6em;
  font-size: 0.9em;
  margin: 0 0 0.7rem;
}
.qcs-branch__count {
  display: inline-flex;
  align-items: center;
  gap: 0.35em;
  padding: 0.1em 0.6em 0.1em 0.3em;
  border: 1px solid var(--vp-c-divider);
  border-radius: 999px;
  background: var(--vp-c-bg-soft);
  font-variant-numeric: tabular-nums;
}
.qcs-branch__count--sum {
  background: color-mix(in srgb, var(--vp-c-brand-1) 14%, transparent);
  color: var(--vp-c-brand-1);
  font-weight: 600;
  border-color: color-mix(in srgb, var(--vp-c-brand-1) 50%, transparent);
}
.qcs-branch__group {
  border: 1px solid var(--vp-c-divider);
  border-radius: 10px;
  background: var(--vp-c-bg-alt);
  margin-bottom: 0.6rem;
  overflow: hidden;
}
.qcs-branch__group summary {
  cursor: pointer;
  padding: 0.55em 0.9em;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.7em;
  font-weight: 600;
  list-style: none;
}
.qcs-branch__group summary::-webkit-details-marker { display: none; }
.qcs-branch__group summary::before {
  content: "▸";
  color: var(--vp-c-text-2);
  margin-right: 0.4em;
  transition: transform 0.15s ease;
  display: inline-block;
}
.qcs-branch__group[open] > summary::before { transform: rotate(90deg); }
.qcs-branch__chips {
  display: inline-flex;
  align-items: center;
  gap: 0.3em;
  flex-wrap: wrap;
}
.qcs-branch__total {
  background: color-mix(in srgb, var(--vp-c-text-1) 10%, transparent);
  border-radius: 6px;
  padding: 0 0.45em;
  font-size: 0.85em;
  font-variant-numeric: tabular-nums;
  color: var(--vp-c-text-2);
}
.qcs-branch__group ul, .qcs-branch__flat {
  list-style: none;
  margin: 0;
  padding: 0.2em 0.9em 0.6em 1.7em;
}
.qcs-branch__flat { padding-left: 0; }
.qcs-branch__group li, .qcs-branch__flat li {
  display: flex;
  align-items: center;
  gap: 0.5em;
  padding: 0.3em 0;
  border-top: 1px dashed var(--vp-c-divider-light);
  flex-wrap: wrap;
}
.qcs-branch__group li:first-child, .qcs-branch__flat li:first-child {
  border-top: none;
}
.qcs-branch__group li a, .qcs-branch__flat li a {
  font-weight: 500;
  text-decoration: none;
  color: var(--vp-c-text-1);
}
.qcs-branch__group li a:hover, .qcs-branch__flat li a:hover {
  color: var(--vp-c-brand-1);
}
.qcs-branch__path {
  color: var(--vp-c-text-3);
  font-size: 0.82em;
}
.qcs-branch__leaf {
  font-size: 0.7em;
  text-transform: uppercase;
  letter-spacing: 0.07em;
  color: var(--vp-c-text-3);
  border: 1px solid var(--vp-c-divider);
  border-radius: 4px;
  padding: 0 0.3em;
}
.muted { color: var(--vp-c-text-3); font-size: 0.85em; }
</style>
