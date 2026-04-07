# Architecture Decisions

Status: current
Scope: short architecture decision records for CodeBlue
Last meaningful change: 2026-04-05

Purpose: define where concise architecture decision records live and what they should contain.

This directory is the home for concise architecture decision records.

Use it when a change answers a question such as:

- which architectural option was chosen;
- why that option was selected;
- which alternative approaches were rejected; or
- what the decision now constrains or enables.

Decision notes should be short and structured. A good default template is:

```md
# Decision Title

Status: accepted | draft | superseded
Date: YYYY-MM-DD
Scope: affected layer or module

## Decision

What was chosen.

## Why

Why it was chosen.

## Alternatives Considered

- option A
- option B

## Consequences

- what this enables
- what this constrains
- what follow-up work it implies
```

The goal is not to replace the main architecture notes. It is to preserve the reasoning behind significant choices so future changes can build on them instead of rediscovering them.
