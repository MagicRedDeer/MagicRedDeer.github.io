---
title: "The FBX importer that flattened my pivots — and the two-pass reader that fixed it"
description: "A standard FBX import bakes transforms into world space and quietly throws away per-node pivots. Here's why the fix had to move upstream, and the small two-pass reader that got them back."
date: 2026-06-02
tags: ["OpenUSD", "FBX", "Houdini", "C++", "pipeline"]
series: "Engineering an OpenUSD asset pipeline"
seriesOrder: 1
---

Every asset pipeline has a stage so ordinary nobody thinks about it: *read the geometry in*.
On a project converting a large library of 3D scan assets into [OpenUSD](https://openusd.org),
that unglamorous first step turned into one of the more interesting problems I solved — because
the standard tool for it was quietly throwing away information the rest of the pipeline needed.

This is the story of why, and of the small reader I wrote to get it back.

## A one-paragraph primer on pivots

A 3D object's transform — where it sits, how it's rotated, its scale — is expressed *relative to
a pivot*, a local origin. In a hierarchy (a tree trunk with branches, a prop with moving parts),
each node has its **own** local transform and pivot, and a child's final position is its local
transform composed with all of its parents'. That per-node local information is what lets a
downstream tool re-articulate the object, keep components addressable, and place them correctly
in a scene graph. USD, in particular, wants that hierarchy preserved as `Xform` prims with their
own `xformOp` stacks.

## The symptom

Single, static meshes converted fine. But **hierarchical, multi-pivot assets** came out wrong:
the shape was there, yet every component had lost its pivot, and the local transforms had
collapsed into one flat world-space soup. In USD terms, the prim hierarchy was intact but the
per-node transform data that should hang off it was gone.

## Why you can't fix this after import

The cause wasn't a bug I could patch downstream. The DCC's standard FBX import **evaluates the
node graph into world space as it reads** — it multiplies each node's transform down the chain
and bakes the result into the geometry. That's a perfectly reasonable default for "give me the
final shape," and it's lossy by design: once transforms are composed into vertices, the
individual pivots are unrecoverable. No amount of post-processing brings them back, because the
information no longer exists in the data you were handed.

So the fix had to move **upstream, to read time** — which meant not using the convenience
importer at all, and going to the [FBX SDK](https://www.autodesk.com/products/fbx/overview)
directly, where each node still exposes its *local* transform components before anything is
evaluated.

## The idea: two passes, opposite orders

The insight that made it tractable is that geometry and transforms want **opposite traversal
orders**:

- To build **geometry**, you want to work bottom-up — a node's local-space mesh doesn't depend
  on its parents, so visit **children before parents** (post-order) and lay each mesh down in
  its own local coordinate system.
- To apply **transforms**, you want to work top-down — a child's placement depends on its
  parents already existing, so visit **parents before children** (pre-order) and attach each
  node's local transform to the hierarchy.

Trying to do both in one traversal is where the naive approach ties itself in knots. Splitting
them into two passes makes each pass simple and correct.

```
FBX node tree           Pass 1 (post-order)         Pass 2 (pre-order)
                        build geometry LOCAL        apply transforms
     root                    ┌── leafA                 root
     ├── groupX              ├── leafB                  ├── groupX
     │   ├── leafA           ├── groupX                 │   ├── leafA
     │   └── leafB           ├── leafC                  │   └── leafB
     └── groupY              ├── groupY                 └── groupY
         └── leafC           └── root                       └── leafC
                        (children first)            (parents first)
```

In pseudocode, stripped of the host-application specifics:

```python
# Pass 1 — geometry, children before parents
for node in postorder(fbx_root):
    if node.is_mesh:
        create_usd_mesh(node.path, geometry=node.local_geometry())   # NO transform applied
        derive_geomsubsets_from_material_groups(node)
    else:
        create_usd_xform(node.path)                                  # structural node

# Pass 2 — transforms, parents before children
for node in preorder(fbx_root):
    xform = node.local_transform()          # translate / rotate (+ pre-rotation) / scale
    set_xform(node.path,
              translate = xform.translation,
              rotate    = xform.rotation + xform.pre_rotation,
              scale     = xform.scale,
              pivot     = xform.rotation_pivot,   # -> xformOp:translate:pivot in USD
              in_world_space = False)              # the whole point: keep it LOCAL
```

Two details worth calling out, because they're the kind of thing you only learn by reading the
format rather than assuming it matches your mental model:

- **FBX pre-rotation is separate from rotation.** FBX stores a `pre_rotation` alongside the
  node's rotation; if you don't add it in, oriented components come out subtly (or not so
  subtly) wrong. USD has no separate concept, so it folds into the rotation you author.
- **Not every FBX pivot has a USD analogue.** FBX distinguishes a rotation pivot from a scaling
  pivot; USD's `xformOp:translate:pivot` maps cleanly to the rotation pivot, and the scaling
  pivot has no direct equivalent. Knowing which one to carry (and that the other can be dropped
  for these assets) came straight from the spec.

## The subtlety that only real data reveals: names

With pivots preserved, one more problem surfaced — and it's a good example of a bug that never
appears on your clean test asset and always appears on the messy real one.

Each mesh needs a canonical, unique name in USD. The obvious design is to name meshes from the
converter's parameters (asset id, tier, LOD, variation). That works for a single-mesh asset. On
a **hierarchical asset with several named components**, it's a disaster: every component gets the
*same* parameter-derived name and they collapse into one identity.

The fix was a clear precedence rule: **the name embedded in the FBX node wins; the converter's
parameters are only fallbacks** for whatever the FBX didn't specify. A small regex pulls the
structured fields out of the FBX node name when they're present, and the parameters fill the
gaps. One rule, but it's the difference between a tree with addressable `trunk` and `branches`
prims and a tree that's just six things all called the same word.

## The unglamorous edge cases (where the real work lives)

Two more that shipped with it, because "read the geometry in" is never as small as it sounds:

- **A `world_root` wrapper.** Some files nest everything under a top node that only carries a
  global transform. Rather than emit a redundant prim, the reader *absorbs* it — folds its
  transform into the import prefix and strips the prefix from every USD path — so the output
  hierarchy stays clean.
- **Empty UV sets.** FBX files sometimes declare UV channels that were never populated. Left in,
  they become empty primvars that fail geometry validation later. The reader drops any UV set
  that's present-but-all-zero (while leaving genuinely empty declarations alone), and then
  fails **fast** if no valid UV set remains — better a loud error at read time than an invalid
  asset discovered three stages downstream.

## What I took from it

The technical result is easy to state: hierarchical assets convert with their per-node pivots
and unique component identities intact, on standard USD `Xform` prims.

The transferable lessons are the part I actually value:

1. **When a black box is lossy by design, stop trying to patch its output.** The leverage was
   moving the work upstream to where the information still existed.
2. **Read the format, don't assume it.** Pre-rotation and the two pivot types weren't in my
   mental model of a transform; they were in the spec.
3. **Design for the messy case, not the clean one.** The naming rule and the edge cases were
   invisible on a single test mesh and decisive on real, hierarchical, decade-old data.

None of this is exotic. It's the ordinary discipline of taking a boring-sounding stage
seriously enough to get it exactly right — which, in a pipeline that has to run unattended over a
very large library, is where reliability actually comes from.

---

*Part of a series on engineering problems from building an OpenUSD asset-conversion pipeline.
Next: [how do you prove two independent backends produce the same thing](/blog/dual-backends-qa-arbiter/)
when your reference data is already stale?*
