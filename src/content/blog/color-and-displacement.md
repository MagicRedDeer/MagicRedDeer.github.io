---
title: "Getting colour and displacement right"
description: "The worst bugs don't crash — they just make the picture a little wrong, consistently. Two families of that bug on a texture pipeline, and the same shape of fix: stop trusting metadata, derive the truth in one place."
date: 2026-06-30
tags: ["OpenUSD", "MaterialX", "OpenPBR", "OpenImageIO", "color"]
series: "Engineering an OpenUSD asset pipeline"
seriesOrder: 3
---

Some bugs announce themselves with a crash. The worst ones just make the picture a little wrong,
consistently, in a way nobody can quite point at. On a texture pipeline converting a large
library of scan assets to [OpenUSD](https://openusd.org) with
[MaterialX](https://materialx.org) materials, two families of that second kind of bug cost me
more time than anything with a stack trace: **colour space** and **displacement range**.

Both had the same root cause and, eventually, the same shape of fix: stop trusting the metadata,
and derive the truth in exactly one place.

## Colour space: right answer, wrong assumption

The rule itself isn't exotic. In a physically based workflow, **colour-carrying maps** (base
colour, and a couple of others) are authored in **sRGB**; **data maps** — normal, roughness,
ambient occlusion, metalness, opacity, displacement — are **linear**; and floating-point EXRs are
linear regardless. Get one map's interpretation wrong and nothing errors — the asset just renders
subtly off, and you spend an afternoon squinting at a roughness map wondering why the highlights
are wrong.

The failure mode wasn't *knowing* the rule; it was **applying it in two places**. With two
conversion backends (see [the previous article](/blog/dual-backends-qa-arbiter/)), each reading
the rule independently, the two would inevitably drift.

The fix was to make colour space **correct by construction**: put the per-map rule in one small
piece of **shared, pure logic** — a table keyed by map type — and have *both* backends import it.
There's a default profile for the common case and an alternative profile for a
different (VFX-oriented) convention, but the point is that the decision lives in exactly one
function. Two callers, one source of truth; they can't disagree because there's nothing to
disagree about.

A related trap in the same area: **map-type aliasing**. The source data called its base-colour
map by an older name (`albedo`), which some pipelines treat as a different thing. Rather than
guess, I sampled the library and confirmed those maps were genuinely usable as base colour, then
canonicalised the name in one place — on both the input-selection and output-naming sides — so
the rest of the pipeline never has to know two names for one concept.

## Displacement: measure, don't trust

Displacement was the more interesting one. A displacement map's height channel needs to land in a
usable `[0, 1]` range, which the source **scale** and **bias** metadata are supposed to describe.
In practice that metadata was unreliable — and a displacement that's silently off by a scale
factor is exactly the kind of error that survives all the way to a confused artist.

So when the source file is actually on disk, the pipeline stops trusting the sidecar and
**measures the real thing** with OpenImageIO: read the red channel's actual min and max, and
recompute scale and bias from the pixels:

```python
minimum = (red.min() - bias) * scale
maximum = (red.max() - bias) * scale

output_scale = abs(maximum - minimum)
output_bias  = -minimum / output_scale        # renormalises the measured range into [0, 1]
```

Those recomputed values are what get written into the material. The number in the file wins over
the number in the metadata, because the pixels can't lie about themselves.

Two details worth keeping:

- **Float EXR displacement skips the recompute entirely.** EXR stores the full floating-point
  range natively, so there's nothing to renormalise — the values are already honest. That's also
  why **EXR is the preferred source** for displacement, and why a lossy 8-bit source is only ever
  admitted deliberately and never used to fabricate a float output.
- **Measuring costs an image read.** It's worth it. The alternative is trusting a field that has
  already been observed to be wrong, on a channel where "wrong" is invisible until it's in front
  of someone.

## The thread that connects them

Chasing an emerging shading standard (moving materials onto
[OpenPBR](https://academysoftwarefoundation.github.io/OpenPBR/)) forced a lot of this into the
open — a parameter migration that rippled through version constraints across the whole toolchain,
and a good reminder that "just update the shading model" is rarely just anything.

But the durable lesson is smaller and more portable than any of the specifics:

1. **A rule applied in two places is a bug waiting to happen.** Move it to one place both callers
   share, and the disagreement becomes structurally impossible.
2. **When metadata describes the data, prefer measuring the data.** The sidecar is a hint; the
   pixels are the fact. For anything where "wrong" is invisible, spend the read.

Neither is glamorous. Both are the difference between a library that renders right the first time
and one that generates a slow trickle of "this looks slightly off" tickets forever.

---

*Part of a series on engineering problems from building an OpenUSD asset-conversion pipeline.
Next: [what changes when you run this over ten thousand messy, decade-old assets](/blog/scaling-messy-assets/)
— and how to report coverage numbers you can actually defend.*
