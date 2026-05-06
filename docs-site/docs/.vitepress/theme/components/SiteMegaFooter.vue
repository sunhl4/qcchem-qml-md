<script setup lang="ts">
import { computed } from "vue";
import { useRoute } from "vitepress";

const route = useRoute();
const en = computed(() => route.path.startsWith("/en"));

const INQUANTO_PUBLIC = "https://docs.quantinuum.com/inquanto/";
</script>

<template>
  <footer class="qcs-site-mega-footer" role="contentinfo">
    <div class="qcs-site-mega-footer__inner">
      <div class="qcs-site-mega-footer__grid">
        <div class="qcs-site-mega-footer__col">
          <h2 class="qcs-site-mega-footer__heading">{{ en ? "Site & compliance" : "站点与合规" }}</h2>
          <ul class="qcs-site-mega-footer__list">
            <li>
              <a :href="en ? '/en/meta/security-and-data' : '/meta/security-and-data'">{{
                en ? "Security & data" : "安全与数据"
              }}</a>
            </li>
            <li>
              <a :href="en ? '/en/meta/ia-mapping' : '/meta/ia-mapping'">{{ en ? "Site map (IA)" : "站点地图（IA）" }}</a>
            </li>
            <li>
              <a :href="en ? '/en/guide/principles-and-reading' : '/guide/principles-and-reading'">{{
                en ? "Principles & reading" : "原理与阅读建议"
              }}</a>
            </li>
          </ul>
        </div>

        <div class="qcs-site-mega-footer__col">
          <h2 class="qcs-site-mega-footer__heading">{{ en ? "Product" : "产品" }}</h2>
          <ul class="qcs-site-mega-footer__list">
            <li>
              <a :href="en ? '/en/product/features' : '/product/features'">{{ en ? "Features" : "产品功能" }}</a>
            </li>
            <li>
              <a :href="en ? '/en/product/' : '/product/'">{{ en ? "Positioning" : "定位与路线" }}</a>
            </li>
            <li>
              <a :href="en ? '/en/product/roadmap' : '/product/roadmap'">{{ en ? "Roadmap" : "路线图" }}</a>
            </li>
          </ul>
        </div>

        <div class="qcs-site-mega-footer__col">
          <h2 class="qcs-site-mega-footer__heading">{{ en ? "Learn" : "学习" }}</h2>
          <ul class="qcs-site-mega-footer__list">
            <li>
              <a :href="en ? '/en/guide/' : '/guide/'">{{ en ? "Guides" : "指南总览" }}</a>
            </li>
            <li>
              <a :href="en ? '/en/tutorial/quickstart' : '/tutorial/quickstart'">{{ en ? "Quickstart" : "快速开始" }}</a>
            </li>
            <li>
              <a :href="en ? '/en/reference/http-api-sqlite-jobs' : '/reference/http-api-sqlite-jobs'">{{
                en ? "Runs API (HTTP)" : "Runs API（HTTP）"
              }}</a>
            </li>
          </ul>
        </div>

        <div class="qcs-site-mega-footer__col">
          <h2 class="qcs-site-mega-footer__heading">{{ en ? "Reference & parity" : "参考与对标" }}</h2>
          <ul class="qcs-site-mega-footer__list">
            <li>
              <a :href="en ? '/en/reference/cli-and-scripts' : '/reference/cli-and-scripts'">{{
                en ? "CLI & scripts" : "命令行与脚本"
              }}</a>
            </li>
            <li>
              <a :href="en ? '/en/parity/public-matrix' : '/parity/public-matrix'">{{ en ? "Parity matrix" : "公开契约矩阵" }}</a>
            </li>
            <li>
              <a :href="en ? '/en/mirror/' : '/mirror/'">{{ en ? "Manual mirror (root)" : "手册镜像（根）" }}</a>
            </li>
            <li>
              <a :href="INQUANTO_PUBLIC" rel="noopener noreferrer">{{ en ? "Quantinuum InQuanto (external)" : "Quantinuum InQuanto（外部）" }}</a>
            </li>
          </ul>
        </div>

        <div class="qcs-site-mega-footer__col qcs-site-mega-footer__col--opensource">
          <h2 class="qcs-site-mega-footer__heading">{{ en ? "Open QC ecosystem (external)" : "开放量子生态（外部）" }}</h2>
          <ul class="qcs-site-mega-footer__list qcs-site-mega-footer__list--inline">
            <li><a href="https://tket.quantinuum.com/" rel="noopener noreferrer">pytket</a></li>
            <li><a href="https://docs.quantinuum.com/nexus/" rel="noopener noreferrer">Q Nexus</a></li>
            <li><a href="https://www.quantinuum.com/" rel="noopener noreferrer">Quantinuum</a></li>
          </ul>
          <p class="qcs-site-mega-footer__note">
            {{ en ? "External links are informational only." : "外链仅供查阅，不代表背书。" }}
          </p>
        </div>
      </div>

      <div class="qcs-site-mega-footer__slash-row" aria-label="Footer shortcuts">
        <a :href="en ? '/en/meta/security-and-data' : '/meta/security-and-data'">{{ en ? "Security & data" : "安全与数据" }}</a>
        <span class="qcs-site-mega-footer__sep" aria-hidden="true">/</span>
        <a :href="en ? '/en/meta/ia-mapping' : '/meta/ia-mapping'">{{ en ? "Site map" : "站点地图" }}</a>
        <span class="qcs-site-mega-footer__sep" aria-hidden="true">/</span>
        <a :href="en ? '/en/guide/principles-and-reading' : '/guide/principles-and-reading'">{{
          en ? "Principles & reading" : "原理与阅读建议"
        }}</a>
      </div>

      <p class="qcs-site-mega-footer__copyright">
        © 2026 qchem-stack documentation contributors. {{ en ? "All documentation content is licensed under project terms unless noted." : "文档内容除另有说明外遵循项目许可。" }}
      </p>
    </div>
  </footer>
</template>
