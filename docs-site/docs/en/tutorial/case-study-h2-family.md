---
title: Case study — H₂ family, chained quantum / backend edits
description: A vol-03-style “change one knob, read the whole repro” practice order
---

This page is a **reading order**, not a single runnable script; keys and allowed values stay authoritative in repo YAML and [Workflow & YAML](/en/tutorial/workflow-overview).

## Baseline

Start from **`configs/example_h2.yaml`**: note top-level blocks (`molecule`, `scf`, `active_space`, `quantum`, `backend`, `compiler` / `mitigation` / `embedding`) and capture **baseline energy + repro** locally.

## Chained variants (suggested)

1. **Edit `backend` only** — follow [Compare backends](/en/tutorial/switch-backend-compare) file pairs; compare `repro` and resource summaries.  
2. **With a fixed backend, change the `quantum.algorithm` story** (VQE / ADAPT, etc.): one class of toggles per run; keep molecule + SCF fixed.  
3. **Excited / QPE smoke** — use `example_h2_excited_smoke.yaml`, `example_h2_qpe_track.yaml`, and watch **multi-stage** entries in `pipeline_profile`.  
4. **Chain tutorial YAML** — open **`configs/tutorial_inquanto_chain_h2.yaml`** next to the workflow overview.

## Wrap-up

Archive **`experiment_id` / `random_seed`** plus **`repro`** slices per run for CI or [Parity matrix](/en/parity/public-matrix) exports if you own acceptance.
