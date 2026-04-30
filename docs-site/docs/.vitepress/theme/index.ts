import DefaultTheme from "vitepress/theme";
import { h } from "vue";
import StatusBadge from "./components/StatusBadge.vue";
import PillarCard from "./components/PillarCard.vue";
import MirrorTree from "./components/MirrorTree.vue";
import MirrorBranch from "./components/MirrorBranch.vue";
import PillarMirror from "./components/PillarMirror.vue";
import Breadcrumbs from "./components/Breadcrumbs.vue";
import LangSwitch from "./components/LangSwitch.vue";
import "./custom.css";

/** Stable slot fns + options object so Layout patches don't remount slots every parent render (avoids nav/doc flicker). */
const layoutSlots = {
  "nav-bar-content-after": () => h(LangSwitch),
  "doc-before": () => h(Breadcrumbs),
};

export default {
  ...DefaultTheme,
  Layout() {
    return h(DefaultTheme.Layout, null, layoutSlots);
  },
  enhanceApp({ app }) {
    app.component("StatusBadge", StatusBadge);
    app.component("PillarCard", PillarCard);
    app.component("MirrorTree", MirrorTree);
    app.component("MirrorBranch", MirrorBranch);
    app.component("PillarMirror", PillarMirror);
    app.component("Breadcrumbs", Breadcrumbs);
    app.component("LangSwitch", LangSwitch);
  },
};
