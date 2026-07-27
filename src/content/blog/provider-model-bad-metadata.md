---
title: "A provider model that survives bad metadata"
description: "On a decade-old library of tens of thousands of assets, 'read the asset in' was most of the reliability battle. Two patterns carried it: a provider abstraction for where an asset lives, and a validate-then-repair registry for how its metadata is broken."
date: 2026-07-21
tags: ["API-design", "validation", "Python", "OpenUSD", "patterns"]
series: "Engineering an OpenUSD asset pipeline"
seriesOrder: 5
---

The first thing an asset converter has to do is the thing nobody puts on a slide: *read the asset
in*. On a decade-old library of tens of thousands of assets, that unglamorous step turned out to
be most of the reliability battle — because the assets lived in different places, and their
metadata was broken in a hundred small ways.

Two patterns carried it: a **provider abstraction** for *where* an asset lives, and a **metadata
auto-repair registry** for *how* its description is broken.

## Providers: decouple "where" from "how"

The converter shouldn't know or care whether a texture is sitting on local disk, in cloud object
storage, or waiting in a downloaded marketplace package. So "where does this component come from?"
lives behind a small protocol — each source implements the same handful of methods
(`available`, `provide`, `get_size`, `validate`) and declares a **priority**.

```
component.fetch()
   │
   ├─ already on local disk and valid?  ──▶ use it        (validate = exists AND size matches
   │                                                        the declared content length)
   └─ otherwise, try providers by priority (high → low):
        local-directory (100) ──▶ cloud object store (90) ──▶ marketplace download (50 …)
                                   first one that reports available() supplies the file
```

Two things this buys you:

- **Local always wins.** The highest-priority provider is the local directory, so a component
  already on disk is never re-fetched — and the validity check is "exists *and* the size matches
  what the metadata declared," not merely "a file is present." A truncated download doesn't pass
  for a real one.
- **New sources plug in without touching the pipeline.** Adding a source is implementing the
  protocol and picking a priority; the conversion code never changes. Concurrency-safe fetching
  (read/write locks around shared components) lives in the same layer, so parallel batches don't
  trip over each other.

Fetching is also **tier-aware**: a given quality tier only pulls the components it actually needs,
rather than dragging the whole asset across the network to use a fraction of it.

## Metadata that breaks your code

Then there's the metadata itself, which in a legacy library is less a schema and more a fossil
record. Real examples that stopped conversions cold: apostrophes and periods in asset names that
turned into syntax errors and scene-open failures downstream; a missing tier field; colour-space
values in the wrong case; nulls where numbers belonged; legacy field names that no longer matched
the schema.

You can't hand-fix these across tens of thousands of assets, and you can't ignore them. So the
asset reader does two things.

**First, sanitise names.** Forbidden characters and reserved names are cleaned when constructing
on-disk and scene-graph names, so a stray apostrophe can't detonate three stages later.

**Second, validate then auto-repair.** Reading metadata runs it through a schema validator, and
then — this is the useful part — **for each validation error, it looks up a registered fix keyed
to that error** and applies it:

```python
def get_metadata():
    errors = validate(metadata, schema)
    for e in errors:
        fix = registry.lookup(e)          # matched to the specific validation error
        if fix:
            metadata = fix(metadata)
        else:
            raise InvalidMetadata(e)       # no registered fix → refuse, don't guess
```

The registry is **open for extension, closed for modification**: a new class of breakage is a new
registered fix (a small, self-contained function), not a change to the pipeline core. It grew
steadily as new legacy and QA assets surfaced new deviations — the mess became *data entries*, not
refactors. Representative fixes: infer a missing tier from the resolution or URI; default a
missing colour space by map type; normalise casing; accept an old field-name spelling; inject the
empty list a newer schema expects for a legacy asset.

One fix is worth singling out because it embodies the guiding principle: when a required block of
descriptive tags was missing, the fix synthesises it from a trusted cache **if** the cache has it —
and if it can't, it **fails validation rather than guessing**. Auto-repair is for *known,
determinate* corrections. The moment a "fix" would have to invent information, it stops and raises.
A repair registry that guesses is just a bug generator with good intentions.

## The consistency insight

Here's the payoff that ties it back to quality. The independent QA gate (from
[an earlier article](/blog/dual-backends-qa-arbiter/)) reads source metadata through the **exact
same repair path** the converter used. That's deliberate: if QA and the converter each "fixed" the
metadata their own way, QA would be validating against an input the converter never actually saw.
One repair path, shared — so the checker and the thing it checks agree about reality before either
one does anything.

## What it demonstrates

Two transferable habits. First, **put "where it comes from" behind a small, prioritised
interface** — it turns "support a new source" from surgery into a plug-in. Second, **validate,
then auto-repair against known errors, and refuse to guess** — it's what lets a pipeline stay
upright on messy real-world data without quietly manufacturing wrong answers. Boring on the
surface, and precisely the layer that decides whether the whole thing survives contact with a real
library.

---

*This closes the series on engineering problems from building an OpenUSD asset-conversion
pipeline: [rebuilding FBX import](/blog/fbx-two-pass-reader/),
[verifying two backends against an independent QA gate](/blog/dual-backends-qa-arbiter/),
[getting colour and displacement right](/blog/color-and-displacement/),
[scaling to a messy library](/blog/scaling-messy-assets/), and — here — reading assets that fight
back.*
