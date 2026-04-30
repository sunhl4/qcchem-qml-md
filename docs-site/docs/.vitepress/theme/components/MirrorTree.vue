<script setup lang="ts">
import { computed, ref } from "vue";
import data from "../../mirror-data.json";
import StatusBadge from "./StatusBadge.vue";

const props = defineProps<{
  locale?: "zh" | "en";
  /** Restrict the tree to a single top-level section, e.g. "manual" */
  section?: string;
  filterStatus?: string;
}>();

const allEntries = (data as any).entries as Array<any>;
const counts = (data as any).counts;

const filter = ref<string>(props.filterStatus ?? "all");
const pillarFilter = ref<string>("all");
const query = ref<string>("");
const collapsed = ref<Record<string, boolean>>({});

const sectionScoped = computed(() =>
  props.section
    ? allEntries.filter((e) => e.breadcrumb[0] === props.section)
    : allEntries
);

const visible = computed(() => {
  const q = query.value.trim().toLowerCase();
  return sectionScoped.value.filter((e) => {
    if (filter.value !== "all" && e.status !== filter.value) return false;
    if (pillarFilter.value !== "all" && e.pillar !== pillarFilter.value) return false;
    if (!q) return true;
    const haystack = [
      e.title_zh,
      e.title_en,
      e.qchem,
      e.breadcrumb.join("/"),
    ].filter(Boolean).join(" ").toLowerCase();
    return haystack.includes(q);
  });
});

// Group visible entries by their top-level section, then by the second-level
// breadcrumb segment if any. Class leaves (depth 4 with `classes` segment) are
// listed under their parent group.
type Group = {
  key: string;
  title: string;
  rows: any[];
  subgroups?: Group[];
  counts: Record<string, number>;
};

function getCountsFor(rows: any[]) {
  const c: Record<string, number> = { shipped: 0, partial: 0, placeholder: 0, "not-applicable": 0, total: rows.length };
  for (const r of rows) c[r.status] = (c[r.status] ?? 0) + 1;
  return c;
}

const SECTION_TITLES: Record<string, { zh: string; en: string }> = {
  introduction: { zh: "Introduction · 介绍", en: "Introduction" },
  manual: { zh: "Manual · 用户手册", en: "Manual" },
  tutorials: { zh: "Tutorials · 教程", en: "Tutorials" },
  extensions: { zh: "Extensions · 扩展", en: "Extensions" },
  api: { zh: "API · 参考", en: "API reference" },
  misc: { zh: "Misc · 杂项", en: "Misc" },
};

const grouped = computed<Group[]>(() => {
  const sections: Record<string, any[]> = {};
  for (const e of visible.value) {
    const top = e.breadcrumb[0];
    sections[top] = sections[top] ?? [];
    sections[top].push(e);
  }
  const out: Group[] = [];
  for (const [topKey, rows] of Object.entries(sections)) {
    // Within each section, build subgroups by second-level breadcrumb.
    const subMap: Record<string, any[]> = {};
    const directRows: any[] = [];
    for (const r of rows) {
      if (r.breadcrumb.length === 1) {
        directRows.push(r);
        continue;
      }
      const subKey = r.breadcrumb[1];
      subMap[subKey] = subMap[subKey] ?? [];
      subMap[subKey].push(r);
    }
    const subgroups: Group[] = Object.entries(subMap).map(([k, rs]) => ({
      key: `${topKey}:${k}`,
      title: rs[0]
        ? (props.locale ?? "zh") === "zh"
          ? rs.find((r: any) => r.breadcrumb.length === 2)?.title_zh ?? k
          : rs.find((r: any) => r.breadcrumb.length === 2)?.title_en ?? k
        : k,
      rows: rs,
      counts: getCountsFor(rs),
    }));
    out.push({
      key: topKey,
      title: (SECTION_TITLES[topKey] ?? { zh: topKey, en: topKey })[(props.locale ?? "zh")],
      rows: directRows,
      subgroups,
      counts: getCountsFor(rows),
    });
  }
  return out;
});

function isCollapsed(key: string) {
  if (collapsed.value[key] === undefined) return false; // expanded by default
  return collapsed.value[key];
}
function toggle(key: string) {
  collapsed.value[key] = !isCollapsed(key);
}

function label(e: any) {
  return (props.locale ?? "zh") === "zh" ? e.title_zh : e.title_en;
}

function href(e: any) {
  const base = (props.locale ?? "zh") === "zh" ? "" : "/en";
  return `${base}/mirror/${e.breadcrumb.join("/")}/`;
}

const totalsByPillar = computed(() => {
  const m: Record<string, Record<string, number>> = {};
  for (const e of sectionScoped.value) {
    const pk = e.pillar;
    m[pk] = m[pk] ?? { shipped: 0, partial: 0, placeholder: 0, "not-applicable": 0, total: 0 };
    m[pk][e.status] = (m[pk][e.status] ?? 0) + 1;
    m[pk].total += 1;
  }
  return m;
});

const STATUS_KEYS = ["shipped", "partial", "placeholder", "not-applicable"];
const PILLAR_LABELS: Record<string, { zh: string; en: string }> = {
  P1: { zh: "P1 化学与嵌入", en: "P1 Chemistry & embedding" },
  P2: { zh: "P2 算法与协议", en: "P2 Algorithms & protocols" },
  P3: { zh: "P3 执行与分析", en: "P3 Execution & analysis" },
  P4: { zh: "P4 作业与可复现", en: "P4 Jobs & reproducibility" },
  meta: { zh: "Meta（导航/元）", en: "Meta (navigation)" },
};
</script>

<template>
  <div class="qcs-mirror">
    <!-- 仪表盘 -->
    <section class="qcs-dash" v-if="!props.section">
      <div class="qcs-dash__totals">
        <div class="qcs-dash__total-card" v-for="s in STATUS_KEYS" :key="s">
          <StatusBadge :status="s" :locale="props.locale ?? 'zh'" />
          <strong>{{ counts[s] ?? 0 }}</strong>
        </div>
        <div class="qcs-dash__total-card qcs-dash__total-card--sum">
          <span class="muted">{{ (props.locale ?? 'zh') === 'zh' ? '总计' : 'Total' }}</span>
          <strong>{{ counts.total ?? 0 }}</strong>
        </div>
      </div>

      <table class="qcs-dash__matrix">
        <thead>
          <tr>
            <th>{{ (props.locale ?? "zh") === "zh" ? "柱" : "Pillar" }}</th>
            <th v-for="s in STATUS_KEYS" :key="s">
              <StatusBadge :status="s" :locale="props.locale ?? 'zh'" />
            </th>
            <th>{{ (props.locale ?? "zh") === "zh" ? "小计" : "Total" }}</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(c, pk) in totalsByPillar" :key="pk">
            <th class="pillar-cell">{{ (PILLAR_LABELS[pk] ?? { zh: pk, en: pk })[(props.locale ?? 'zh')] }}</th>
            <td v-for="s in STATUS_KEYS" :key="s">{{ c[s] ?? 0 }}</td>
            <td><strong>{{ c.total ?? 0 }}</strong></td>
          </tr>
        </tbody>
      </table>
    </section>

    <!-- 工具条 -->
    <div class="qcs-mirror__bar">
      <input
        v-model="query"
        type="search"
        :placeholder="(props.locale ?? 'zh') === 'zh' ? '过滤标题、模块、路径…' : 'Filter title, module, path…'"
      />
      <div class="qcs-mirror__filters">
        <button
          v-for="s in ['all', ...STATUS_KEYS]"
          :key="s"
          :data-active="filter === s"
          @click="filter = s"
        >
          {{ s === "all" ? ((props.locale ?? "zh") === "zh" ? "全部" : "All") : s }}
          <span v-if="s !== 'all'" class="count">{{ counts[s] ?? 0 }}</span>
        </button>
      </div>
      <div class="qcs-mirror__filters">
        <button
          v-for="p in ['all','P1','P2','P3','P4','meta']"
          :key="p"
          :data-active="pillarFilter === p"
          @click="pillarFilter = p"
        >
          {{ p === "all" ? ((props.locale ?? "zh") === "zh" ? "全柱" : "All pillars") : p }}
        </button>
      </div>
    </div>

    <!-- 折叠树 -->
    <div class="qcs-tree" v-if="grouped.length">
      <details
        v-for="g in grouped"
        :key="g.key"
        class="qcs-tree__section"
        :open="!isCollapsed(g.key)"
        @toggle="toggle(g.key)"
      >
        <summary>
          <span class="title">{{ g.title }}</span>
          <span class="qcs-tree__chips">
            <StatusBadge v-for="s in STATUS_KEYS" :key="s" :status="s" :locale="props.locale ?? 'zh'" v-show="g.counts[s] > 0" />
            <span class="qcs-tree__total">{{ g.counts.total }}</span>
          </span>
        </summary>

        <ul v-if="g.rows.length" class="qcs-tree__rows">
          <li v-for="e in g.rows" :key="e.breadcrumb.join('/')">
            <a :href="href(e)">{{ label(e) }}</a>
            <StatusBadge :status="e.status" :locale="props.locale ?? 'zh'" />
            <code v-if="e.qchem" class="muted">{{ e.qchem }}</code>
          </li>
        </ul>

        <details
          v-for="sub in g.subgroups"
          :key="sub.key"
          class="qcs-tree__subgroup"
          :open="!isCollapsed(sub.key)"
          @toggle="toggle(sub.key)"
        >
          <summary>
            <span class="title">{{ sub.title }}</span>
            <span class="qcs-tree__chips">
              <StatusBadge v-for="s in STATUS_KEYS" :key="s" :status="s" :locale="props.locale ?? 'zh'" v-show="sub.counts[s] > 0" />
              <span class="qcs-tree__total">{{ sub.counts.total }}</span>
            </span>
          </summary>
          <ul class="qcs-tree__rows">
            <li v-for="e in sub.rows" :key="e.breadcrumb.join('/')">
              <a :href="href(e)">{{ label(e) }}</a>
              <StatusBadge :status="e.status" :locale="props.locale ?? 'zh'" />
              <code v-if="e.qchem" class="muted">{{ e.qchem }}</code>
              <span v-if="e.isClassLeaf" class="qcs-tree__leaf-tag">class</span>
            </li>
          </ul>
        </details>
      </details>
    </div>

    <p v-else class="muted">
      {{ (props.locale ?? "zh") === "zh" ? "没有匹配的节点。" : "No matching nodes." }}
    </p>
  </div>
</template>

<style scoped>
.qcs-mirror { margin: 1rem 0 2rem; }
.qcs-dash { margin-bottom: 1.5rem; }
.qcs-dash__totals {
  display: flex;
  flex-wrap: wrap;
  gap: 0.6rem;
  margin-bottom: 1rem;
}
.qcs-dash__total-card {
  display: inline-flex;
  align-items: center;
  gap: 0.4em;
  padding: 0.35em 0.7em 0.35em 0.4em;
  border: 1px solid var(--vp-c-divider);
  border-radius: 10px;
  background: var(--vp-c-bg-soft);
  font-variant-numeric: tabular-nums;
}
.qcs-dash__total-card strong { font-size: 1.05em; }
.qcs-dash__total-card--sum { background: color-mix(in srgb, var(--vp-c-brand-1) 12%, transparent); }
.qcs-dash__matrix {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.9em;
}
.qcs-dash__matrix th, .qcs-dash__matrix td {
  padding: 0.4em 0.7em;
  border-bottom: 1px solid var(--vp-c-divider-light);
  text-align: right;
  font-variant-numeric: tabular-nums;
}
.qcs-dash__matrix th { text-align: center; }
.qcs-dash__matrix .pillar-cell { text-align: left; font-weight: 500; }
.qcs-mirror__bar {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem 0.9rem;
  align-items: center;
  margin-bottom: 0.9rem;
}
.qcs-mirror__bar input[type="search"] {
  flex: 1 1 220px;
  min-width: 220px;
  padding: 0.45em 0.7em;
  border: 1px solid var(--vp-c-divider);
  border-radius: 8px;
  background: var(--vp-c-bg-soft);
  color: inherit;
}
.qcs-mirror__filters {
  display: flex;
  gap: 0.35rem;
  flex-wrap: wrap;
}
.qcs-mirror__filters button {
  padding: 0.25em 0.65em;
  border-radius: 999px;
  border: 1px solid var(--vp-c-divider);
  background: transparent;
  cursor: pointer;
  font-size: 0.82em;
  color: inherit;
  display: inline-flex;
  align-items: center;
  gap: 0.4em;
}
.qcs-mirror__filters button[data-active="true"] {
  background: color-mix(in srgb, var(--vp-c-brand-1) 18%, transparent);
  border-color: color-mix(in srgb, var(--vp-c-brand-1) 55%, transparent);
  color: var(--vp-c-brand-1);
  font-weight: 600;
}
.count {
  font-variant-numeric: tabular-nums;
  background: color-mix(in srgb, var(--vp-c-text-1) 10%, transparent);
  border-radius: 6px;
  padding: 0 0.4em;
  font-size: 0.85em;
}
.qcs-tree__section, .qcs-tree__subgroup {
  border: 1px solid var(--vp-c-divider);
  border-radius: 10px;
  margin-bottom: 0.6rem;
  background: var(--vp-c-bg-alt);
  overflow: hidden;
}
.qcs-tree__subgroup { margin: 0.4rem 0.5rem 0.6rem; background: var(--vp-c-bg); }
.qcs-tree summary {
  cursor: pointer;
  padding: 0.6em 0.9em;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.7em;
  font-weight: 600;
  list-style: none;
}
.qcs-tree summary::-webkit-details-marker { display: none; }
.qcs-tree summary::before {
  content: "▸";
  color: var(--vp-c-text-2);
  margin-right: 0.4em;
  transition: transform 0.15s ease;
  display: inline-block;
}
.qcs-tree__section[open] > summary::before,
.qcs-tree__subgroup[open] > summary::before {
  transform: rotate(90deg);
}
.qcs-tree__chips {
  display: inline-flex;
  align-items: center;
  gap: 0.3em;
  flex-wrap: wrap;
}
.qcs-tree__total {
  background: color-mix(in srgb, var(--vp-c-text-1) 10%, transparent);
  border-radius: 6px;
  padding: 0 0.45em;
  font-size: 0.85em;
  font-variant-numeric: tabular-nums;
  color: var(--vp-c-text-2);
}
.qcs-tree__rows {
  list-style: none;
  padding: 0.2em 0.9em 0.6em 1.7em;
  margin: 0;
}
.qcs-tree__rows li {
  display: flex;
  align-items: center;
  gap: 0.5em;
  padding: 0.3em 0;
  border-top: 1px dashed var(--vp-c-divider-light);
}
.qcs-tree__rows li:first-child { border-top: none; }
.qcs-tree__rows li a {
  font-weight: 500;
  text-decoration: none;
  color: var(--vp-c-text-1);
}
.qcs-tree__rows li a:hover { color: var(--vp-c-brand-1); }
.qcs-tree__leaf-tag {
  font-size: 0.7em;
  text-transform: uppercase;
  letter-spacing: 0.07em;
  color: var(--vp-c-text-3);
  border: 1px solid var(--vp-c-divider);
  border-radius: 4px;
  padding: 0 0.3em;
}
.muted { color: var(--vp-c-text-3); font-size: 0.88em; }
</style>
