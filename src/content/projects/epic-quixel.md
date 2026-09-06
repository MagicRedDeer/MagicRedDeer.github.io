---
title: "Megascans → OpenUSD conversion & automation pipeline"
description: "Core developer & architect of Epic's Megascans → OpenUSD pipeline: 20,637 assets converted (~92% of the actionable library), a dual backend kept honest by an independent ~110-rule QA gate, and corpus-scale batch tooling that drained the conversion backlog to zero."
order: 1
featured: true
role: "Pipeline & Automation Engineer — Epic Games (Quixel)"
period: "Apr 2025 – Jul 2026 · Remote"
tech: ["OpenUSD", "MaterialX", "OpenPBR", "Houdini", "Python", "OpenImageIO", "AWS", "FastAPI", "FBX SDK"]
links:
  - { label: "Read the engineering series", url: "/blog" }
---

Core developer and architect of Epic's **Megascans → OpenUSD** conversion pipeline: converting the
Megascans library into self-contained USDZ / MaterialX packages on open interchange standards, in
a cross-functional team of management, engineers, and artists.

## What it did

Took the Megascans library of 3D scan assets and converted it into clean, self-contained
**OpenUSD** packages with high-fidelity **MaterialX / OpenPBR** materials — correct maps, sane
scene-graph organization, and maximum compatibility across Unreal Engine, Maya, Houdini, Blender,
and more.

- **20,637 assets converted** into OpenUSD with MaterialX / OpenPBR materials — about **92% of the
  actionable library** — across **six OpenPBR material types**, packaged per quality tier into
  USDZ / MaterialX. The conversion backlog went from **338 to 0**.

## Architecture highlights

- **Dual backend behind one Python API.** A **Houdini** engine (Solaris/LOPs, five custom HDAs
  driven in `hython`) for a validated, artist-editable path — plus a **pure-Python** backend with a
  vendored USD/MaterialX/OpenImageIO runtime that reproduces the same output with no DCC
  dependency. I drove the pure-Python backend to structural parity.
- **QA as the arbiter of "correct."** An independent, automated QA gate — **~110 rules across
  seven layers**, with crash-resilient Maya visual QA — validates geometry, materials, USD
  structure, and textures and decides ship-readiness for every output. The two backends stay in
  parity *by construction*, not by brittle image diffing. A "rule first, then fix" review loop
  turned every reported defect into a permanent regression test.
- **A provider-based asset model** with JSON-schema validation and an extensible metadata
  auto-repair registry, so the pipeline stays upright on messy, decade-old source data.
- **Corpus-scale operations tooling** that scans storage, classifies every asset, batches the
  convertibles, and runs unattended over the library — with corruption detection, an auditable
  rejection pipeline, idempotent relaunch, and a 404-aware multi-pass gather that recovered
  measured coverage from **78.7% to 98.9%** by reporting honestly.
- **An in-house FBX→USD reader** (Autodesk FBX SDK, two-pass local-space reconstruction) that
  preserves per-node pivots a standard import would flatten.

Development and documentation were accelerated with **AI/LLM agent tooling (Claude Code)**.

The engineering problems behind each of these are written up in detail in the
[writing section](/blog).