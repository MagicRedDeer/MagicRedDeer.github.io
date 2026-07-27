---
title: "Converting 10,000 messy assets without lying about it"
description: "A converter that works on a clean test asset is a demo. Running unattended over ten-thousand-plus real, decade-old assets is a different program — mostly about the mess you didn't design for, and reporting coverage you can defend."
date: 2026-07-14
tags: ["automation", "scale", "robustness", "OpenUSD", "ops"]
series: "Engineering an OpenUSD asset pipeline"
seriesOrder: 4
---

A converter that works on a clean test asset is a demo. A converter that runs unattended across a
library of ten-thousand-plus real, decade-old assets is a different kind of program — and the
gap between the two is almost entirely about the assets you didn't design for.

This is about that gap: the mess that scale surfaces, and the discipline of reporting coverage
numbers you can actually stand behind.

## Scale is a discovery mechanism

The clean asset converts on the first try. It's asset number 6,000 that teaches you things:
components that are corrupt or truncated, top-resolution textures simply absent, on-disk layouts
that don't match any convention you'd been coding against, the occasional file that's a fraction
of the size it claims to be. None of these throw a tidy exception — left alone, they fail
*silently*, or worse, produce a plausible-looking but wrong asset.

So the first job at scale isn't converting; it's **triage**.

## Detect the corruption cheaply, before you spend on it

The cheapest signal turned out to be size. Before committing any compute to an asset, a scan
compares each component's storage size against what it should be, with calibrated thresholds, and
flags the tell-tales: a missing top-resolution map, a component under a kilobyte, a file well
below its declared size. Catching "this asset is broken" from object metadata — before decoding a
single pixel — keeps the expensive path clear for assets that can actually succeed.

## Reject on purpose, with a reason you can query

Not every asset *should* convert, and "didn't convert" must never be a mystery. Every asset that
doesn't go through is routed into a **rejection pipeline with an explicit, auditable reason**, so
the question "why isn't this asset in the output?" is a one-line lookup, not an investigation.

The reasons split into two very different buckets, and keeping them separate matters:

- **Deliberate exclusions** — asset *types* that were out of scope by design. These were the
  large majority of rejections, and counting them as "failures" would badly misrepresent the
  system.
- **Genuine data problems** — corruption, missing records, unsupported legacy structures. A much
  smaller slice, and the only slice that actually reflects on the pipeline.

Conflating those two is how a healthy pipeline ends up *looking* broken in a status report.
Separating them is the difference between an honest number and a scary-wrong one.

## Normalise the weird-but-valid

Some odd layouts aren't broken, just old. Rather than reject them, a set of **normalisation
pre-passes** reshapes them into something the converter understands — falling back to a lower
format when a tier's preferred one is absent, mirroring a structure for assets that only ever had
a lower-resolution form, resolving resolution-tier collisions. Every one of these was a specific
lesson from a specific family of assets that would otherwise have been thrown away for no good
reason.

## Make long runs survivable

Early batches kept dying part-way through, and a naive design would simply lose all the work. The
fixes were unglamorous and decisive:

- **Idempotent relaunch.** Every asset's result is logged; a relaunch skips anything already done
  and picks up where it stopped. Re-running is always safe.
- **A reconciliation invariant.** After classification, the counts have to add up —
  every asset is in exactly one class and exactly one status — and the run **fails loudly** if
  they don't. A silent accounting drift is treated as a bug, not rounded away.
- **A strict single-writer rule.** Two batches must never write the same output location at once;
  overlapping writes corrupt shared files. Better to serialise than to debug a half-written asset.
- **Fail fast, and clean up.** A texture that can't be processed stops its asset immediately
  rather than limping onward, and interrupting a run tears down the whole subprocess tree instead
  of leaking orphans.

## The tracker that lied under load

My favourite bug in this whole effort: coverage looked *terrible* on big runs, and it wasn't. The
asset tracker we queried returns a **404 when it's rate-limiting** — and a naive fetch reads
"404" as "this asset doesn't exist," so under load the pipeline cheerfully reported huge swathes
of the library as missing. The data was fine; the *measurement* was wrong.

The fix was a **rate-limit-aware, multi-pass gather**: treat a 404-under-load as "ask again
later," not "gone," and re-sweep the gaps. On one run that took apparent coverage from roughly
four-fifths of the library to nearly complete — not by converting anything new, but by
**measuring honestly**.

That bug crystallised the theme of the whole exercise. At scale, a wrong *number* is as dangerous
as a wrong *asset* — and often harder to notice.

## Reporting you can defend

By the end, every coverage claim had to survive a simple test: could I explain, per asset, why it
was in the bucket it was in? Converted, or rejected-with-a-reason, or genuinely still to do — and
never "failed" when it was really "excluded by design." When the pipeline bounds its own coverage,
it says so out loud, because **silent truncation reads as "we covered everything" when you
didn't.**

## What it demonstrates

Robustness at scale is mostly idempotency, cheap early triage, and refusing to lose work. But the
part I care about most is the reporting integrity: a big system earns trust not by claiming a
gaudy coverage number, but by being able to account for **every** asset it *didn't* cover.

---

*Part of a series on engineering problems from building an OpenUSD asset-conversion pipeline.
Next: [the pattern that let the converter read assets that actively fought back](/blog/provider-model-bad-metadata/)
— providers, and a metadata auto-repair registry.*
