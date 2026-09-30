# Sudarshan - Fast UI Build Process

## Goal

Reach a judge-ready frontend quickly without wasting time on backend work, huge datasets, or speculative UI modules. The fastest route is to freeze one demonstrable analyst journey, implement the full shell, wire deterministic local fixtures, then replace fixtures with real local inference services later.

## Phase 0 - Start with the exact command

Paste this first into Claude Code:

```text
Open the existing Sudarshan repository. Do not create a second app. Do not rewrite the project from scratch. First inspect the current frontend, the four reference screenshots, and docs/DEMO_STORYLINE.md. Return a short implementation plan and wait.
```

## Phase 1 - Freeze the demo journey

Paste:

```text
Freeze the demo around this exact primary query: "newly built structures near a river". Use only the four sites and approximately 30-38 imagery items described in docs/DEMO_STORYLINE.md. Do not download anything yet. Implement the full clickable workflow with local fixtures first.
```

## Phase 2 - Build the shell before details

Paste:

```text
Build the complete Sudarshan desktop shell first: top trust bar, left navigation, page container, panel/card primitives, status pills, tabs, buttons, tables, maps, evidence cards, and responsive layout. Do not polish individual modules until the shared shell is stable. Run npm build.
```

## Phase 3 - Build the demo-critical path

Paste:

```text
Now implement only the critical judge path: Search & Explore -> SITE-A -> Before/After -> Temporal Evidence -> False-Alarm Analysis -> Similar Sites -> Review Queue -> Provenance/Export. Make every click work with local deterministic fixtures. Run npm build.
```

## Phase 4 - Add supporting screens

Paste:

```text
Add Dashboard, Clustering, Temporal Viewer, Data Ingestion, Data Catalog, Analytics, System Status and Settings. Reuse the same components and data abstractions instead of creating duplicate UI implementations. Run npm build.
```

## Phase 5 - Stage only the minimum imagery

Paste:

```text
Only now collect imagery. Target 30-38 image items maximum for the first demo. Use the site grouping in docs/DEMO_STORYLINE.md. Preserve real metadata and licensing information. Do not collect an archive larger than necessary for the UI walkthrough.
```

## Phase 6 - Replace CSS placeholders

Paste:

```text
Replace CSS-only satellite thumbnails with the locally staged imagery where available. Keep a graceful placeholder for any asset that has not been approved or staged. Never substitute a fake online map/API. Keep all assets local.
```

## Phase 7 - Evidence polish

Paste:

```text
Do a final evidence-first polish: every confidence score must have supporting factors, every change must have before/after evidence and a timeline, every suppressed candidate must explain why it was suppressed, and every export must show provenance. Keep DEMO MODE visible while fixture data is used.
```

## Phase 8 - Final freeze command

Paste:

```text
Run the full local demo rehearsal from docs/UI_BUILD_PROMPTS.md Prompt 13. Then run npm build. Fix all errors, warnings that affect the demo, broken links, console errors, and missing local assets. Do not add new scope after this point.
```

## Time-saving rules

- Do not build backend services before the frontend journey is clickable.
- Do not build a large imagery archive before the screens are stable.
- Do not create duplicate components for each page.
- Reuse one data model across Search, Site Analysis, Temporal Viewer, Similar Sites, Review Queue, and Provenance.
- Keep real model/index integration behind a service interface so fixture mode can be removed later without rewriting the UI.
- Treat `npm run build` as the exit gate after every meaningful prompt.
- Keep the four supplied screenshots as visual regression references.

## Definition of fast success

A new developer or AI coding agent should be able to run:

```text
npm install
npm run dev
```

and complete the primary demo without a network connection and without downloading a large dataset.
