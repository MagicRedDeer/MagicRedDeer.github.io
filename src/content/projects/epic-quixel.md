---
title: "3D-asset conversion & automation pipeline"
description: "Core developer & architect of a production pipeline that converts large 3D-asset libraries onto open interchange standards (OpenUSD, MaterialX/OpenPBR), with a dual backend kept honest by an independent QA gate."
order: 1
featured: true
role: "Pipeline & Automation Engineer — Epic Games (Quixel)"
period: "Apr 2025 – Jul 2026 · Remote"
tech: ["OpenUSD", "MaterialX", "OpenPBR", "Houdini", "Python", "OpenImageIO", "AWS", "FastAPI", "FBX SDK"]
links:
  - { label: "Read the engineering series", url: "/blog" }
---

Core developer and architect of a production 3D-asset conversion and automation system for
**Epic Games (Quixel)**, built on open interchange standards and delivered with a cross-functional
team of management, engineers, and artists. _(Some specifics are generalized here while the work
sits under NDA.)_

## What it does

Takes a large library of legacy 3D scan assets and converts them into clean, self-contained
**OpenUSD** packages with high-fidelity **MaterialX / OpenPBR** materials — correct maps, sane
scene-graph organization, and maximum compatibility across Unreal Engine, Maya, Houdini, Blender,
and more.

## Architecture highlights

- **Dual backend behind one Python API.** A **Houdini** engine (Solaris/LOPs, custom HDAs driven
  in `hython`) for a validated, artist-editable path — plus a **pure-Python** backend with a
  vendored USD/MaterialX/OpenImageIO runtime that reproduces the same output with no DCC dependency.
- **QA as the arbiter of "correct."** An independent, automated QA gate validates geometry,
  materials, USD structure, and textures (with optional DCC render smoke-tests) and decides
  ship-readiness for every output — so the two backends stay in parity by construction, not by
  brittle image diffing.
- **A provider-based asset model** with JSON-schema validation and an extensible metadata
  auto-repair registry, so the pipeline stays upright on messy, decade-old source data.
- **Corpus-scale operations tooling** that scans storage, classifies every asset, batches the
  convertibles, and runs unattended over tens of thousands of assets — with corruption detection,
  an auditable rejection pipeline, idempotent relaunch, and rate-limit-aware coverage measurement.
- **An in-house FBX→USD reader** (Autodesk FBX SDK, two-pass local-space reconstruction) that
  preserves per-node pivots a standard import would flatten.

Development and documentation were accelerated with **AI/LLM agent tooling (Claude Code)**.

The engineering problems behind each of these are written up in detail in the
[writing section](/blog).
