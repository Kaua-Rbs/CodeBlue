# Frontend Demo Prototype

Status: current
Scope: standalone visual prototype for the first CodeBlue demo surface
Last meaningful change: 2026-04-07

Purpose: provide a portable visual prototype for the first demo before the real frontend stack is implemented.

The prototype lives at [frontend-prototype.html](/home/kauar/CodeBlue/docs/demo/frontend-prototype.html).

## What It Covers

The prototype visualizes the first frontend slice defined in the architecture notes:

- `Command Center`
- `Action Review Workspace`
- `Ward Detail`
- `Trace Drawer`

It uses realistic demo content and interaction patterns rather than generic placeholder copy.

## What It Is For

Use it to:

- present the product visually in the hackathon;
- align on screen hierarchy before frontend implementation;
- validate the narrative flow of the demo; and
- serve as a visual target for the eventual real frontend.

## What It Is Not

It is not:

- connected to the live backend;
- a production frontend;
- a final visual system;
- or a substitute for the real UI implementation.

It is a design prototype with lightweight interactivity.

## How Close The Real Frontend Should Be

The real frontend should stay close to this prototype in:

- screen hierarchy;
- user flow;
- operations-first information structure;
- and overall visual tone.

It should not be treated as a frozen pixel-perfect layout.

The final frontend will likely change:

- exact spacing;
- responsive behavior;
- data density;
- empty and error states;
- and some panel composition once the real backend payloads are wired in.

So the right expectation is:

- same product shape;
- same design direction;
- more robust and refined implementation.

## How To Open It

Open the HTML file directly in a browser:

- [frontend-prototype.html](/home/kauar/CodeBlue/docs/demo/frontend-prototype.html)

If needed, it can also be served locally with a simple static server.

## Current Demo Flow In The Prototype

The intended walkthrough is:

1. start on `Command Center`
2. inspect the summary cards and action queue
3. open the `Actions` workspace
4. review the top recommendation
5. open the `Trace` drawer
6. inspect the `Wards` view

That mirrors the recommended product story for the first demo.
