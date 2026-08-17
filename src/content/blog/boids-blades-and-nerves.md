---
title: "Boids, blades and nerves"
description: "In 2004 a handful of first-time programmers in Karachi built a boids crowd on sixteen blades for a scene most people never saw. The film flopped, and it hooked me anyway."
date: 2026-07-21
tags: ["simulation", "procedural-animation", "vfx"]
draft: false
---

## Opening

I joined Post Amazers looking for something different. It was the right place to be: the studio was abuzz. Kleiser-Walczak, a real VFX house, had just signed an MoU in Pakistan, and the rumour running through the corridors was that a Hollywood feature would be next for us, maybe with Tippett Studio on board. The film would carry names like that. ILM had a hand in it too, though not on the shot that was coming to us. For a young programmer this looked like our big break, our entry into the world of Hollywood VFX. I was one of several CGI programmers hired to lay down a technical pipeline for what was coming.

The first project was Son of the Mask. I loved the original and the cartoon series, so the excitement was real. Then we got our first sequence: a petri dish, an egg, and thousands of sperms, a scene that would be uncomfortable to describe to your parents and almost certainly a strain on a children's film. But we were new to this, and to us every problem looked like a nail for our newly acquired hammers.

## The scene

For a technical team, the task was a problem worth solving: how do you render thousands of sperms in one frame, each with its own variation and its own individual motion, all fighting their way across a petri dish toward an egg? Computationally this was a crowd problem, and it was 2004, early in the field for us. We had no existing resources to lean on, no readily available technology that did this job for us. We were learning the tools as we built with them, me included, learning Maya and RenderMan as I went. To us at the time it felt like being handed a big, gnarly problem and being told to solve it with what little we had.

## The build

The work split four ways, and each of us got a problem that matched what we were still learning.

Ali Ahsan, a touch more experienced than the rest of us, took the rig. Sperms are simple enough shapes that they can be animated procedurally, and he drove them with sinusoidal waveforms so each one swam with a plausible wiggle and never needed a hand-keyed cycle. Shahzad took the translucent shader, the business of making something that small read as wet and fleshy on screen. Bilal wrote the script that turned the cached particle simulation into rendered creatures, swapping each simulated particle for its geometry and assembling the full scene with material assignment, ready for the renderer. My job was the guidance: the flocking behaviour, the part that decided where all those little bodies actually went.

Ali Ahsan pointed me at Craig Reynolds' boids, and it was my first proper look at emergence. A few simple local rules, separation and alignment and cohesion, and a crowd of individuals moves like a school or a flock with no central control deciding any of it. I tried the rules out on everything I could think of, schools of fish, flocks of birds, swarms of bees, and the elegance of it was hard not to get drunk on. A handful of rules, written once, and out the other end came behaviour that looked decided.

Then came the complexity. These are local rules, but local means pairwise: every particle has to find every neighbour inside its radius, and doing that naively is n-squared work, a number that stops being funny the moment you multiply it by tens of thousands of particles. The fix I landed on was a spatial grid. Divide the space into cells, and each particle only ever looks up the few cells around it. It was the first real optimization I ever did on a real problem, and it was the moment I understood that algorithm choices write themselves on render bills weeks later.

That was the simulation side. The render side was a different kind of constraint: sixteen dual-Xeon blades with severe memory limits, and we were going to render thousands of individually animated creatures. The answers were two RenderMan features used together. We baked each sperm's animated geometry to its own RIB file, small renderable scene fragments, and we referenced them through delayed read archives, which load a fragment into memory only when it is actually in the view. Everything else waits on disk. That is how a scene with thousands of independently animated bodies fits in memory: never all of it at once.

Everything in that era was MEL and C++ and nothing was given to us, so alongside the crowd system I also wrote a noise deformer as a C++ plugin for the wall of the uterus in the background. It was my first deformer to reach production. It is not beautiful work by any later standard, but it held, and it shipped.

The capability we ended up with was thousands to tens of thousands of objects animating and rendering in a single frame. What did and did not make it into the final scene was a creative decision, not a technical one.

## The direction

The directions came over the internet, through messaging and email, and I only ever received them. Timing of the burst when the two super-sperms first tore through the petri dish. How much of the screen the creatures covered. The density of the sperms in the background at particular moments. Between those, I slid knobs, set keys, and pointed the behaviours from one state to another.

The creative team decided what the scene needed, and our job was to make the technology do what the direction required. We could have done more if the direction had asked for it; the capability was there. Creative decisions direct the tech; the tech does not decide the scene. That is the order I have kept with ever since.

## The aftermath

The movie came out in 2005 and did badly. Whatever I had shipped had made it into a film that was, to put it gently, a difficult watch, and in the US the sequence was deemed something the theatrical cut should not carry. It did end up releasing in other versions, though not the one most people saw. Our scene was easy to mock, and the internet obliged. Under the low-resolution upload that has survived on YouTube for seventeen years, the comments run a familiar handful of notes: someone remembers seeing it on Cartoon Network as a child and never understanding what it was about, and why their father looked embarrassed and disappointed. Someone calls it first-year CGI student work. Someone finds it disturbing. Someone asks whether the people who worked on it admit to it on their resumes.[^1] The punchline is that I would come to carry an effects programmer credit for Son of the Mask on [IMDb](https://www.imdb.com/name/nm1691839/), my first introduction to the database: it arrived long after the work was done, attached to a scene most audiences never saw.

[^1]: The clip lives on at [youtube.com/watch?v=x6Nb608AZVc](https://www.youtube.com/watch?v=x6Nb608AZVc). It deserves its comments.

These jabs are not entirely wrong. By the standards of the same year, Weta was rendering Helm's Deep with Massive, a full crowd system with agent brains and a decade of development behind it. Something like that takes a lot of effort, time, and money to execute. We were first-timers on our first feature shot, a handful of programmers in Karachi who had taught ourselves the tools a couple of years before. A comparison between that and a system that had grown for years inside one of the biggest VFX studios on earth is not warranted. The gap, however, is real, and seeing it plainly is part of the education.

And yet. When I watch that clip now, the little creatures swimming in the background of the two exaggerated super-sperms still pull something.

## The reflection

I have spent the years since building tools that sit at the same boundary, pipelines that give artists more control while taking less of it away. And whenever I look back, the crowd system is where I first learned to build for that boundary. It is the pattern I still reach for: make the mechanism honest, then make it answerable to a human.

If the film had been a success, I might have learned something smaller. The scene worked, but the film did not, and that failure taught me the thing that has kept me in this field. We took a tiny, insignificant scene no one outside a room in Karachi would ever think about, and we solved the problem in front of us with the best of our abilities, because we enjoyed the work. It did not win anything. It was not even in the version most people saw. And it is precisely that combination, the smallness of the thing and the seriousness we brought to it, that has made me appreciate the machinery behind every film, game, and project that entertains the masses. None of them are accidental. Someone, somewhere, took a small problem seriously once, for reasons that had nothing to do with whether it would be noticed.

There was nerve in that: a handful of learners betting months on a scene no one would ever praise. That is not a story about winning. It is a story about the way a group of people with no roadmap can build something from nothing, get it wrong, and still come away hooked. There is hope in that. I keep it with me.
