# Day1–Day90 执行日历：差距收口 + Tangelo 设计参考（2026）

本文件落实仓库计划「三个月逐日计划（差距 + Tangelo 参考）」：**每日最小产出 + 周闸门**，与 [`day91_day120_daily_breakdown_2026Q3.md`](day91_day120_daily_breakdown_2026Q3.md) 口径一致。

## 差距清单快照（执行入口）

| 来源 | 要点 |
|------|------|
| [`docs/技术分析_Vendor platform_PySCF_vs_原生PySCF_及工程借鉴.md`](../技术分析_Vendor platform_PySCF_vs_原生PySCF_及工程借鉴.md) §4–§8 | 能量账本、`from_mf`、decomposition 产品契约、AVAS、量子 RDM→AC0 等 |
| [`docs/竞争定位与路线图_对标Quantinuum产品与技术路线.md`](../竞争定位与路线图_对标Quantinuum产品与技术路线.md) §3–§4 | Tangelo：分解、映射、ansatz/solver、mitigation、examples 生态 |

## 三条主线与月份

| 区间 | 主线 | 代表交付 |
|------|------|----------|
| Day 1–30 | Chem 契约 | `energy_components_v1`；`decomposition_plugin_contract_v1`；parity 抽样加固 |
| Day 31–60 | Tangelo 对齐 | ansatz/映射 registry 注释；`classical_shadows` mitigation stub；`avas_stub` 活性空间钩子 |
| Day 61–90 | 产品收口 | QMEF trainer smoke；三条用户路径；契约稳定周；Day90 签字 |

## 逐日日历（Day 1–90）

| Day | 主题 | Tangelo/差距映射 | 主要输入 | 当日最小输出 | 验收 |
|-----|------|------------------|----------|--------------|------|
| 1 | D01-设计契约草案-Chem_contract | 技术分析§5.5；PhaseB-plugin；Tangelo-decomposition | pipeline/protocol/export | contract草稿与字段命名 | 无命名冲突 |
| 2 | D02-export镜像-Chem_contract | 技术分析§5.5；PhaseB-plugin；Tangelo-decomposition | pipeline/protocol/export | export脚本config-only路径 | 键可导出 |
| 3 | D03-pytest-Chem_contract | 技术分析§5.5；PhaseB-plugin；Tangelo-decomposition | pipeline/protocol/export | tests断言与失败路径 | 定位清晰 |
| 4 | D04-YAML示例-Chem_contract | 技术分析§5.5；PhaseB-plugin；Tangelo-decomposition | pipeline/protocol/export | configs最小样例 | 可载入 |
| 5 | D05-文档同步-Chem_contract | 技术分析§5.5；PhaseB-plugin；Tangelo-decomposition | pipeline/protocol/export | docs与docusaurus-site | 互链有效 |
| 6 | D06-集成parity-Chem_contract | 技术分析§5.5；PhaseB-plugin；Tangelo-decomposition | pipeline/protocol/export | parity-sample与子集pytest | 通过或可解释skip |
| 7 | D07-周复盘闸门-Chem_contract | 技术分析§5.5；PhaseB-plugin；Tangelo-decomposition | pipeline/protocol/export | 周小结与遗留登记 | 滚动下一周 |
| 8 | D08-设计契约草案-Chem_contract | 技术分析§5.5；PhaseB-plugin；Tangelo-decomposition | pipeline/protocol/export | contract草稿与字段命名 | 无命名冲突 |
| 9 | D09-export镜像-Chem_contract | 技术分析§5.5；PhaseB-plugin；Tangelo-decomposition | pipeline/protocol/export | export脚本config-only路径 | 键可导出 |
| 10 | D10-pytest-Chem_contract | 技术分析§5.5；PhaseB-plugin；Tangelo-decomposition | pipeline/protocol/export | tests断言与失败路径 | 定位清晰 |
| 11 | D11-YAML示例-Chem_contract | 技术分析§5.5；PhaseB-plugin；Tangelo-decomposition | pipeline/protocol/export | configs最小样例 | 可载入 |
| 12 | D12-文档同步-Chem_contract | 技术分析§5.5；PhaseB-plugin；Tangelo-decomposition | pipeline/protocol/export | docs与docusaurus-site | 互链有效 |
| 13 | D13-集成parity-Chem_contract | 技术分析§5.5；PhaseB-plugin；Tangelo-decomposition | pipeline/protocol/export | parity-sample与子集pytest | 通过或可解释skip |
| 14 | D14-周复盘闸门-Chem_contract | 技术分析§5.5；PhaseB-plugin；Tangelo-decomposition | pipeline/protocol/export | 周小结与遗留登记 | 滚动下一周 |
| 15 | D15-设计契约草案-Chem_contract | 技术分析§5.5；PhaseB-plugin；Tangelo-decomposition | pipeline/protocol/export | contract草稿与字段命名 | 无命名冲突 |
| 16 | D16-export镜像-Chem_contract | 技术分析§5.5；PhaseB-plugin；Tangelo-decomposition | pipeline/protocol/export | export脚本config-only路径 | 键可导出 |
| 17 | D17-pytest-Chem_contract | 技术分析§5.5；PhaseB-plugin；Tangelo-decomposition | pipeline/protocol/export | tests断言与失败路径 | 定位清晰 |
| 18 | D18-YAML示例-Chem_contract | 技术分析§5.5；PhaseB-plugin；Tangelo-decomposition | pipeline/protocol/export | configs最小样例 | 可载入 |
| 19 | D19-文档同步-Chem_contract | 技术分析§5.5；PhaseB-plugin；Tangelo-decomposition | pipeline/protocol/export | docs与docusaurus-site | 互链有效 |
| 20 | D20-集成parity-Chem_contract | 技术分析§5.5；PhaseB-plugin；Tangelo-decomposition | pipeline/protocol/export | parity-sample与子集pytest | 通过或可解释skip |
| 21 | D21-周复盘闸门-Chem_contract | 技术分析§5.5；PhaseB-plugin；Tangelo-decomposition | pipeline/protocol/export | 周小结与遗留登记 | 滚动下一周 |
| 22 | D22-设计契约草案-Chem_contract | 技术分析§5.5；PhaseB-plugin；Tangelo-decomposition | pipeline/protocol/export | contract草稿与字段命名 | 无命名冲突 |
| 23 | D23-export镜像-Chem_contract | 技术分析§5.5；PhaseB-plugin；Tangelo-decomposition | pipeline/protocol/export | export脚本config-only路径 | 键可导出 |
| 24 | D24-pytest-Chem_contract | 技术分析§5.5；PhaseB-plugin；Tangelo-decomposition | pipeline/protocol/export | tests断言与失败路径 | 定位清晰 |
| 25 | D25-YAML示例-Chem_contract | 技术分析§5.5；PhaseB-plugin；Tangelo-decomposition | pipeline/protocol/export | configs最小样例 | 可载入 |
| 26 | D26-文档同步-Chem_contract | 技术分析§5.5；PhaseB-plugin；Tangelo-decomposition | pipeline/protocol/export | docs与docusaurus-site | 互链有效 |
| 27 | D27-集成parity-Chem_contract | 技术分析§5.5；PhaseB-plugin；Tangelo-decomposition | pipeline/protocol/export | parity-sample与子集pytest | 通过或可解释skip |
| 28 | D28-周复盘闸门-Chem_contract | 技术分析§5.5；PhaseB-plugin；Tangelo-decomposition | pipeline/protocol/export | 周小结与遗留登记 | 滚动下一周 |
| 29 | D29-设计契约草案-Chem_contract | 技术分析§5.5；PhaseB-plugin；Tangelo-decomposition | pipeline/protocol/export | contract草稿与字段命名 | 无命名冲突 |
| 30 | D30-export镜像-Chem_contract | 技术分析§5.5；PhaseB-plugin；Tangelo-decomposition | pipeline/protocol/export | export脚本config-only路径 | 键可导出 |
| 31 | D31-pytest-Tangelo_align | 路线图§3-4；Tangelo-mapping/solver/mitigation | pipeline/protocol/export | tests断言与失败路径 | 定位清晰 |
| 32 | D32-YAML示例-Tangelo_align | 路线图§3-4；Tangelo-mapping/solver/mitigation | pipeline/protocol/export | configs最小样例 | 可载入 |
| 33 | D33-文档同步-Tangelo_align | 路线图§3-4；Tangelo-mapping/solver/mitigation | pipeline/protocol/export | docs与docusaurus-site | 互链有效 |
| 34 | D34-集成parity-Tangelo_align | 路线图§3-4；Tangelo-mapping/solver/mitigation | pipeline/protocol/export | parity-sample与子集pytest | 通过或可解释skip |
| 35 | D35-周复盘闸门-Tangelo_align | 路线图§3-4；Tangelo-mapping/solver/mitigation | pipeline/protocol/export | 周小结与遗留登记 | 滚动下一周 |
| 36 | D36-设计契约草案-Tangelo_align | 路线图§3-4；Tangelo-mapping/solver/mitigation | pipeline/protocol/export | contract草稿与字段命名 | 无命名冲突 |
| 37 | D37-export镜像-Tangelo_align | 路线图§3-4；Tangelo-mapping/solver/mitigation | pipeline/protocol/export | export脚本config-only路径 | 键可导出 |
| 38 | D38-pytest-Tangelo_align | 路线图§3-4；Tangelo-mapping/solver/mitigation | pipeline/protocol/export | tests断言与失败路径 | 定位清晰 |
| 39 | D39-YAML示例-Tangelo_align | 路线图§3-4；Tangelo-mapping/solver/mitigation | pipeline/protocol/export | configs最小样例 | 可载入 |
| 40 | D40-文档同步-Tangelo_align | 路线图§3-4；Tangelo-mapping/solver/mitigation | pipeline/protocol/export | docs与docusaurus-site | 互链有效 |
| 41 | D41-集成parity-Tangelo_align | 路线图§3-4；Tangelo-mapping/solver/mitigation | pipeline/protocol/export | parity-sample与子集pytest | 通过或可解释skip |
| 42 | D42-周复盘闸门-Tangelo_align | 路线图§3-4；Tangelo-mapping/solver/mitigation | pipeline/protocol/export | 周小结与遗留登记 | 滚动下一周 |
| 43 | D43-设计契约草案-Tangelo_align | 路线图§3-4；Tangelo-mapping/solver/mitigation | pipeline/protocol/export | contract草稿与字段命名 | 无命名冲突 |
| 44 | D44-export镜像-Tangelo_align | 路线图§3-4；Tangelo-mapping/solver/mitigation | pipeline/protocol/export | export脚本config-only路径 | 键可导出 |
| 45 | D45-pytest-Tangelo_align | 路线图§3-4；Tangelo-mapping/solver/mitigation | pipeline/protocol/export | tests断言与失败路径 | 定位清晰 |
| 46 | D46-YAML示例-Tangelo_align | 路线图§3-4；Tangelo-mapping/solver/mitigation | pipeline/protocol/export | configs最小样例 | 可载入 |
| 47 | D47-文档同步-Tangelo_align | 路线图§3-4；Tangelo-mapping/solver/mitigation | pipeline/protocol/export | docs与docusaurus-site | 互链有效 |
| 48 | D48-集成parity-Tangelo_align | 路线图§3-4；Tangelo-mapping/solver/mitigation | pipeline/protocol/export | parity-sample与子集pytest | 通过或可解释skip |
| 49 | D49-周复盘闸门-Tangelo_align | 路线图§3-4；Tangelo-mapping/solver/mitigation | pipeline/protocol/export | 周小结与遗留登记 | 滚动下一周 |
| 50 | D50-设计契约草案-Tangelo_align | 路线图§3-4；Tangelo-mapping/solver/mitigation | pipeline/protocol/export | contract草稿与字段命名 | 无命名冲突 |
| 51 | D51-export镜像-Tangelo_align | 路线图§3-4；Tangelo-mapping/solver/mitigation | pipeline/protocol/export | export脚本config-only路径 | 键可导出 |
| 52 | D52-pytest-Tangelo_align | 路线图§3-4；Tangelo-mapping/solver/mitigation | pipeline/protocol/export | tests断言与失败路径 | 定位清晰 |
| 53 | D53-YAML示例-Tangelo_align | 路线图§3-4；Tangelo-mapping/solver/mitigation | pipeline/protocol/export | configs最小样例 | 可载入 |
| 54 | D54-文档同步-Tangelo_align | 路线图§3-4；Tangelo-mapping/solver/mitigation | pipeline/protocol/export | docs与docusaurus-site | 互链有效 |
| 55 | D55-集成parity-Tangelo_align | 路线图§3-4；Tangelo-mapping/solver/mitigation | pipeline/protocol/export | parity-sample与子集pytest | 通过或可解释skip |
| 56 | D56-周复盘闸门-Tangelo_align | 路线图§3-4；Tangelo-mapping/solver/mitigation | pipeline/protocol/export | 周小结与遗留登记 | 滚动下一周 |
| 57 | D57-设计契约草案-Tangelo_align | 路线图§3-4；Tangelo-mapping/solver/mitigation | pipeline/protocol/export | contract草稿与字段命名 | 无命名冲突 |
| 58 | D58-export镜像-Tangelo_align | 路线图§3-4；Tangelo-mapping/solver/mitigation | pipeline/protocol/export | export脚本config-only路径 | 键可导出 |
| 59 | D59-pytest-Tangelo_align | 路线图§3-4；Tangelo-mapping/solver/mitigation | pipeline/protocol/export | tests断言与失败路径 | 定位清晰 |
| 60 | D60-YAML示例-Tangelo_align | 路线图§3-4；Tangelo-mapping/solver/mitigation | pipeline/protocol/export | configs最小样例 | 可载入 |
| 61 | D61-文档同步-Product_wrap | P2-W6-W7；竞争定位-MDML-教程 | pipeline/protocol/export | docs与docusaurus-site | 互链有效 |
| 62 | D62-集成parity-Product_wrap | P2-W6-W7；竞争定位-MDML-教程 | pipeline/protocol/export | parity-sample与子集pytest | 通过或可解释skip |
| 63 | D63-周复盘闸门-Product_wrap | P2-W6-W7；竞争定位-MDML-教程 | pipeline/protocol/export | 周小结与遗留登记 | 滚动下一周 |
| 64 | D64-设计契约草案-Product_wrap | P2-W6-W7；竞争定位-MDML-教程 | pipeline/protocol/export | contract草稿与字段命名 | 无命名冲突 |
| 65 | D65-export镜像-Product_wrap | P2-W6-W7；竞争定位-MDML-教程 | pipeline/protocol/export | export脚本config-only路径 | 键可导出 |
| 66 | D66-pytest-Product_wrap | P2-W6-W7；竞争定位-MDML-教程 | pipeline/protocol/export | tests断言与失败路径 | 定位清晰 |
| 67 | D67-YAML示例-Product_wrap | P2-W6-W7；竞争定位-MDML-教程 | pipeline/protocol/export | configs最小样例 | 可载入 |
| 68 | D68-文档同步-Product_wrap | P2-W6-W7；竞争定位-MDML-教程 | pipeline/protocol/export | docs与docusaurus-site | 互链有效 |
| 69 | D69-集成parity-Product_wrap | P2-W6-W7；竞争定位-MDML-教程 | pipeline/protocol/export | parity-sample与子集pytest | 通过或可解释skip |
| 70 | D70-周复盘闸门-Product_wrap | P2-W6-W7；竞争定位-MDML-教程 | pipeline/protocol/export | 周小结与遗留登记 | 滚动下一周 |
| 71 | D71-设计契约草案-Product_wrap | P2-W6-W7；竞争定位-MDML-教程 | pipeline/protocol/export | contract草稿与字段命名 | 无命名冲突 |
| 72 | D72-export镜像-Product_wrap | P2-W6-W7；竞争定位-MDML-教程 | pipeline/protocol/export | export脚本config-only路径 | 键可导出 |
| 73 | D73-pytest-Product_wrap | P2-W6-W7；竞争定位-MDML-教程 | pipeline/protocol/export | tests断言与失败路径 | 定位清晰 |
| 74 | D74-YAML示例-Product_wrap | P2-W6-W7；竞争定位-MDML-教程 | pipeline/protocol/export | configs最小样例 | 可载入 |
| 75 | D75-文档同步-Product_wrap | P2-W6-W7；竞争定位-MDML-教程 | pipeline/protocol/export | docs与docusaurus-site | 互链有效 |
| 76 | D76-集成parity-Product_wrap | P2-W6-W7；竞争定位-MDML-教程 | pipeline/protocol/export | parity-sample与子集pytest | 通过或可解释skip |
| 77 | D77-周复盘闸门-Product_wrap | P2-W6-W7；竞争定位-MDML-教程 | pipeline/protocol/export | 周小结与遗留登记 | 滚动下一周 |
| 78 | D78-设计契约草案-Product_wrap | P2-W6-W7；竞争定位-MDML-教程 | pipeline/protocol/export | contract草稿与字段命名 | 无命名冲突 |
| 79 | D79-export镜像-Product_wrap | P2-W6-W7；竞争定位-MDML-教程 | pipeline/protocol/export | export脚本config-only路径 | 键可导出 |
| 80 | D80-pytest-Product_wrap | P2-W6-W7；竞争定位-MDML-教程 | pipeline/protocol/export | tests断言与失败路径 | 定位清晰 |
| 81 | D81-YAML示例-Product_wrap | P2-W6-W7；竞争定位-MDML-教程 | pipeline/protocol/export | configs最小样例 | 可载入 |
| 82 | D82-文档同步-Product_wrap | P2-W6-W7；竞争定位-MDML-教程 | pipeline/protocol/export | docs与docusaurus-site | 互链有效 |
| 83 | D83-集成parity-Product_wrap | P2-W6-W7；竞争定位-MDML-教程 | pipeline/protocol/export | parity-sample与子集pytest | 通过或可解释skip |
| 84 | D84-周复盘闸门-Product_wrap | P2-W6-W7；竞争定位-MDML-教程 | pipeline/protocol/export | 周小结与遗留登记 | 滚动下一周 |
| 85 | D85-设计契约草案-Product_wrap | P2-W6-W7；竞争定位-MDML-教程 | pipeline/protocol/export | contract草稿与字段命名 | 无命名冲突 |
| 86 | D86-export镜像-Product_wrap | P2-W6-W7；竞争定位-MDML-教程 | pipeline/protocol/export | export脚本config-only路径 | 键可导出 |
| 87 | D87-pytest-Product_wrap | P2-W6-W7；竞争定位-MDML-教程 | pipeline/protocol/export | tests断言与失败路径 | 定位清晰 |
| 88 | D88-YAML示例-Product_wrap | P2-W6-W7；竞争定位-MDML-教程 | pipeline/protocol/export | configs最小样例 | 可载入 |
| 89 | D89-文档同步-Product_wrap | P2-W6-W7；竞争定位-MDML-教程 | pipeline/protocol/export | docs与docusaurus-site | 互链有效 |
| 90 | D90-集成parity-Product_wrap | P2-W6-W7；竞争定位-MDML-教程 | pipeline/protocol/export | parity-sample与子集pytest | 通过或可解释skip |

## 每周固定闸门

1. `pytest`（当周相关子集；月末倾向全量）。
2. `python scripts/check_parity_export_sample.py`
3. [`src/qchem_stack/protocols/product_contract.py`](../../src/qchem_stack/protocols/product_contract.py)（**`qchem_stack.protocols.product_contract`**：`product_gap_categories()`、export 稳定键 — [CONTRIBUTING](../../CONTRIBUTING.md#product-contracts-and-workflow-preview-stable-imports)） / [`scripts/export_parity_criteria_table.py`](../../scripts/export_parity_criteria_table.py) / `RUN_SUMMARY_DOCUMENTED_KEYS` 同源。
4. `docs/` 与 `docusaurus-site/` 入口互链抽检。
5. 新增能力：**示例 YAML + 最小测试**。

## Day90 封板清单（指向）

见 [`day090_tangelo_calendar_closeout.md`](day090_tangelo_calendar_closeout.md)。

## 不做清单

- 闭源 Nexus/HQC/Qermit/cuTensorNet **L0** 等价宣称。
- Psi4 整条 driver 等产品级集成（本周期仅允许 spike，默认不进主分支承诺）。
