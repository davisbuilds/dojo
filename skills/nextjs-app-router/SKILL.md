---
name: nextjs-app-router
description: Next.js App Router expert guidance. Use when building, debugging, or architecting Next.js applications — routing, Server Components, Server Actions, layouts, data fetching, rendering strategies, metadata, image/font optimization, error handling, and hydration debugging. Triggers on tasks involving Next.js pages, app directory structure, RSC boundaries, or App Router migration.
skill-type: reference
version: 1.0.0
license: MIT
metadata:
  author: vercel
  version: "1.0.0"
---

# Next.js App Router Best Practices

Comprehensive reference for building Next.js applications with the App Router. Contains 20 reference docs covering architecture, patterns, and common pitfalls.

## When to Apply

Reference these guidelines when:
- Building or modifying Next.js App Router pages and layouts
- Choosing between Server and Client Components
- Implementing data fetching or caching strategies
- Debugging hydration errors or RSC boundary issues
- Configuring metadata, images, fonts, or scripts
- Migrating from Pages Router to App Router
- Setting up error handling or parallel routes

## Reference Docs

### Project Structure

| Reference | What it covers |
|-----------|---------------|
| [file-conventions.md](references/file-conventions.md) | Special files, route segments, dynamic/catch-all/group routes, parallel and intercepting routes |
| [app-router-files.md](references/app-router-files.md) | App Router file hierarchy and conventions |
| [directives.md](references/directives.md) | `'use client'`, `'use server'`, `'use cache'` directives |

### Components and Rendering

| Reference | What it covers |
|-----------|---------------|
| [rsc-boundaries.md](references/rsc-boundaries.md) | Server/Client Component boundaries, invalid patterns, serialization rules |
| [suspense-boundaries.md](references/suspense-boundaries.md) | Suspense placement, CSR bailout with `useSearchParams`/`usePathname` |
| [hydration-error.md](references/hydration-error.md) | Common hydration error causes and fixes |
| [parallel-routes.md](references/parallel-routes.md) | Modal patterns, `@slot` interceptors, `default.tsx` fallbacks |

### Data and Fetching

| Reference | What it covers |
|-----------|---------------|
| [data-patterns.md](references/data-patterns.md) | Server Components vs Server Actions vs Route Handlers, avoiding waterfalls |
| [async-patterns.md](references/async-patterns.md) | Next.js 15+ async `params`, `searchParams`, `cookies()`, `headers()` |
| [route-handlers.md](references/route-handlers.md) | `route.ts` basics, GET/POST handlers, when to use vs Server Actions |
| [functions.md](references/functions.md) | Navigation hooks, server functions, generate functions |

### Optimization

| Reference | What it covers |
|-----------|---------------|
| [bundling.md](references/bundling.md) | Server-incompatible packages, CSS imports, ESM/CJS, bundle analysis |
| [image.md](references/image.md) | `next/image`, remote config, responsive sizes, blur placeholders, LCP priority |
| [font.md](references/font.md) | `next/font` setup, Google/local fonts, Tailwind integration |
| [scripts.md](references/scripts.md) | `next/script` strategies, inline scripts, Google Analytics |
| [metadata.md](references/metadata.md) | Static/dynamic metadata, `generateMetadata`, OG images with `next/og` |
| [runtime-selection.md](references/runtime-selection.md) | Node.js vs Edge runtime selection |

### Error Handling and Debugging

| Reference | What it covers |
|-----------|---------------|
| [error-handling.md](references/error-handling.md) | `error.tsx`, `global-error.tsx`, `not-found.tsx`, `redirect`, `unstable_rethrow` |
| [debug-tricks.md](references/debug-tricks.md) | MCP endpoint for AI debugging, `--debug-build-paths` |

### Deployment

| Reference | What it covers |
|-----------|---------------|
| [self-hosting.md](references/self-hosting.md) | `output: 'standalone'` for Docker, cache handlers, multi-instance ISR |

## Boundaries

- Not for React performance optimization patterns — use `vercel-react-best-practices` instead
- Not for component composition/architecture — use `vercel-composition-patterns` instead
- Not for Vercel deployment or CLI — use `vercel-deploy` instead
- Not for React Native — use `vercel-react-native-skills` instead
- Reference docs are point-in-time snapshots; check official docs for breaking changes

## Verification

- Server Components do not import `useState`, `useEffect`, or other client hooks without `'use client'`
- `params` and `searchParams` are awaited in Next.js 15+ page/layout components
- `cookies()` and `headers()` are awaited in server code
- Error boundaries exist at appropriate route segment levels
- Metadata uses `generateMetadata` for dynamic values, not `next/head`

## Sibling skills

Vercel/React reference layer — App Router-focused. Sibling references at different axes:

- `vercel-react-best-practices` — perf optimization (waterfalls, server-component data shaping). Pair with this skill on perf-sensitive routes.
- `vercel-composition-patterns` — component composition patterns. Orthogonal axis.
- `vercel-deploy` / `vercel-preview-logs` — runtime side.
