import { defineCollection, z } from 'astro:content';
import { glob } from 'astro/loaders';

const blog = defineCollection({
  loader: glob({ pattern: '**/*.md', base: './src/content/blog' }),
  schema: z.object({
    title: z.string(),
    description: z.string(),
    date: z.coerce.date(),
    tags: z.array(z.string()).default([]),
    draft: z.boolean().default(false),
    series: z.string().optional(),
    seriesOrder: z.number().optional(),
  }),
});

const projects = defineCollection({
  loader: glob({ pattern: '**/*.md', base: './src/content/projects' }),
  schema: z.object({
    title: z.string(),
    description: z.string(),
    order: z.number().default(99),
    featured: z.boolean().default(false),
    role: z.string().optional(),
    period: z.string().optional(),
    tech: z.array(z.string()).default([]),
    links: z.array(z.object({ label: z.string(), url: z.string() })).default([]),
  }),
});

export const collections = { blog, projects };
