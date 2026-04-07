# Frontend Stack Justifications

Status: current
Scope: rationale for the first real CodeBlue frontend stack, including why each tool is chosen and why nearby alternatives are not the default
Last meaningful change: 2026-04-07

Purpose: record the reasoning behind the frontend stack so implementation decisions stay coherent and can be revisited later without losing the original tradeoffs.

This note owns the frontend stack decision for the first real CodeBlue frontend.

## Recommended Stack

The recommended frontend stack is:

- `React`
- `TypeScript`
- `Vite`
- `React Router`
- `TanStack Query`
- `Zustand`
- hand-authored CSS with design tokens and CSS modules

Recommended supporting tools once implementation starts:

- `Vitest`
- `React Testing Library`
- `Playwright`

## Selection Principles

The stack should optimize for:

- fast implementation by one engineer;
- strong contract alignment with the typed backend;
- good support for stateful operational screens;
- low framework overhead;
- easy local development;
- and enough flexibility to keep the product visually distinctive.

The frontend should not be chosen as if this were:

- a content-heavy marketing site;
- a mobile-first consumer app;
- or a generic admin panel.

It is an operational clinical dashboard with review workflows and traceability requirements.

## `React`

Why choose it:

- the product has multiple synchronized stateful surfaces;
- component composition is a good fit for dashboards, drawers, workspaces, and detail panels;
- the ecosystem is mature and predictable;
- it is the safest choice for a solo engineer who needs speed without novelty risk.

Why not `Vue` by default:

- Vue would also work, but React has a stronger default ecosystem for the exact combination of routing, query state, and dashboard-style composition likely needed here;
- it reduces hiring and collaboration risk later because the pool is larger.

Why not `Svelte` or `Solid` by default:

- both can produce elegant apps, but they increase ecosystem and architectural novelty for a project that already has enough domain complexity;
- the product problem is not “framework performance,” it is “clear operational UX with reliable typed state.”

Conclusion:

React is not chosen because alternatives are weak. It is chosen because it is the lowest-risk, highest-support option for this kind of product.

## `TypeScript`

Why choose it:

- the backend is already strongly typed;
- the frontend will consume structured contracts like actions, assessments, state snapshots, and review decisions;
- a typed frontend reduces contract drift and integration mistakes;
- it is especially important for a product where subtle data-shape errors can create misleading operational displays.

Why not plain `JavaScript`:

- plain JavaScript would increase speed only in the very short term;
- it would make the action, risk, and trace surfaces much easier to break silently;
- it would weaken the discipline that is already a strength of the backend.

Conclusion:

TypeScript is the right default because CodeBlue depends on stable interfaces between layers.

## `Vite`

Why choose it:

- fast startup;
- fast rebuilds;
- minimal configuration burden;
- works naturally with a separate Python API backend;
- well suited to a dashboard-style SPA.

Why not `Next.js`:

- server-side rendering is not the core problem of this product;
- the repository already has a separate backend and should not be forced into a full-stack React framework prematurely;
- adding Next.js now would increase conceptual surface without solving the most important product problems.

Why not `Create React App`:

- it is no longer the best default and would be a step backward in tooling.

Why not `Astro`:

- Astro is excellent for content-heavy and marketing-heavy sites, but CodeBlue is an application surface first.

Conclusion:

Vite is the best lightweight foundation for the first real frontend.

## `React Router`

Why choose it:

- the product clearly has route-worthy surfaces;
- Command Center, Actions, and Ward Detail are easier to reason about when they are explicit routes rather than internal tab state;
- it supports deep-linking later when specific actions or wards need shareable URLs.

Why not keep everything inside one route:

- the UI already has more than one meaningful surface;
- route-less view switching becomes brittle as the product grows.

Why not file-based routing right now:

- file-based routing is not necessary to get the benefits of clear route structure;
- the goal is explicitness, not framework magic.

Conclusion:

React Router is the simplest routing layer that matches the current product shape.

## `TanStack Query`

Why choose it:

- the frontend will frequently fetch and refresh server state;
- it handles loading, caching, invalidation, and refetching cleanly;
- it separates server data from local UI state, which is important for a dashboard.

Why not manual `fetch` everywhere:

- manual fetch logic would spread loading, error, and refresh code across screens;
- it would make the first frontend harder to keep consistent.

Why not `SWR` as the default:

- SWR is solid, but TanStack Query gives broader and more explicit control for the operational workflows this product will likely need.

Conclusion:

TanStack Query is the right server-state layer for a backend-driven operational UI.

## `Zustand`

Why choose it:

- it is small and easy to reason about;
- it fits the limited amount of global UI state expected at first;
- it is well suited for selected action state, selected ward state, drawers, and filters.

Why not `Redux Toolkit`:

- Redux is powerful, but the current frontend does not need that much ceremony;
- introducing it now would add conceptual weight without solving a real current problem.

Why not React Context alone:

- Context is useful, but once selection state and cross-screen UI coordination grow, it can become awkward if used as the only global state mechanism.

Conclusion:

Zustand is the right size for the first real frontend.

## CSS Strategy: Tokens Plus CSS Modules

Why choose it:

- the product should feel visually intentional, not generic;
- design tokens create a reusable visual system without requiring a large styling framework;
- CSS modules or similarly scoped styling keep components manageable without creating a global cascade mess.

Why not `Tailwind` as the primary styling system:

- Tailwind is productive, but it would make it too easy to drift toward a generic dashboard look;
- the project needs a more deliberate visual language than utility-class assembly usually encourages by default.

Why not `Material UI`, `Ant Design`, or similar full component kits:

- those libraries would accelerate basic scaffolding;
- but they would also heavily bias the product toward a commodity enterprise-admin visual identity;
- CodeBlue should not look interchangeable with a finance ops console.

Why not raw global CSS only:

- pure global CSS would become harder to manage once the screens and component count increase.

Conclusion:

The frontend should be styled with a small in-house system, not a heavy off-the-shelf visual language.

## Supporting Test Stack

These are not the core runtime libraries, but they should be part of the frontend stack once implementation begins.

### `Vitest`

Why choose it:

- it fits naturally with Vite;
- it is fast;
- setup is straightforward.

Why not `Jest` by default:

- Jest would work, but it is no longer the lightest default in a Vite-based app.

### `React Testing Library`

Why choose it:

- it encourages testing user-visible behavior rather than implementation detail;
- that is appropriate for screens like action review and trace display.

Why not shallow-render-style testing:

- shallow testing is less valuable for a product whose risk lies in workflow behavior and visible states.

### `Playwright`

Why choose it:

- the product has multi-screen flows that benefit from end-to-end verification;
- it is especially useful for confirming that review workflows, routing, and trace drawers behave correctly.

Why not Cypress as the default:

- Cypress would also work;
- Playwright is the more flexible default for modern cross-browser end-to-end testing, especially if the product later needs richer automation.

## Why This Stack Fits The Current Backend

The backend already exposes structured routes for:

- health
- events
- runs
- state
- risk
- actions
- review
- explainability

The frontend therefore needs:

- strong typed API consumption;
- reliable refetching after mutations;
- clear route structure;
- and a UI architecture that can display multiple synchronized operational views.

The recommended stack matches that shape directly.

## Relationship To The HTML Prototype

The real frontend should be close to the HTML prototype in:

- information architecture;
- screen hierarchy;
- major interaction flow;
- visual tone;
- and the idea of an operations-first command surface.

It should not be expected to match the prototype exactly in:

- spacing;
- final typography choices;
- exact card sizes;
- responsive behavior;
- empty and error states;
- and data density after real backend integration.

So the right expectation is:

**same product shape and same visual direction, but not pixel-perfect identical.**

The prototype is a design target, not a frozen final layout.
