# Claude Code Master Prompt - Sudarshan SIH 26227 Frontend Execution

Copy this entire prompt into Claude Code when you want the UI implementation to be executed as one controlled job.

```text
You are the lead frontend engineer for the Sudarshan SIH 2026 Problem Statement 26227 project.

Repository:
- existing React + Vite frontend
- reference screenshots are in /reference-ui
- detailed demo storyline is in /docs/DEMO_STORYLINE.md
- sequential implementation prompts are in /docs/UI_BUILD_PROMPTS.md
- fast-build rules are in /docs/FAST_UI_BUILD_PLAYBOOK.md

MISSION
Build a polished, judge-ready, desktop-first geospatial intelligence workstation named "Sudarshan" that visually follows the supplied reference screens and implements the complete analyst journey for SIH PS 26227.

PRIMARY DEMO STORY
The analyst enters:
"newly built structures near a river"

Sudarshan searches a tiny local imagery archive, returns ranked candidates, lets the analyst select SITE-A, shows before/after imagery, temporal evidence, earliest supported change, quality/false-alarm evidence, similar sites, analyst review, and complete provenance/export.

SECONDARY DEMO STORY
The analyst can then run:
"large vehicle concentrations on open ground"

DATA LIMIT
The first demo must use a very small local imagery set: target 30-38 image items. Do not build or download a large regional archive just to populate the UI.

Suggested grouping:
- SITE-A: 10 observations, target construction change near river
- SITE-B: 7 observations, similar-site case
- SITE-C: 7 observations, seasonal/no-change control
- SITE-D: 6 observations, haze/cloud/shadow/illumination/registration confounder
- optional secondary-query controls: up to 8 observations only when necessary

DATA HONESTY
- Public or organiser-approved imagery only.
- Preserve actual source metadata and licence information.
- Never invent acquisition dates, coordinates, sensors, confidence, model metrics, latency, or processing history.
- Do not represent deterministic fixtures as live AI inference.
- Keep a persistent badge: DEMO MODE - LOCAL PRECOMPUTED ARCHIVE while fixture mode is active.
- Change the badge to OFFLINE - LOCAL INFERENCE only after the real local inference/index services are connected and verified.

ARCHITECTURE RULES
- Keep React + Vite unless an actual build issue requires change.
- Use reusable UI primitives and shared data types.
- Keep all demo data behind a service/data adapter abstraction.
- Make future backend integration a replacement of data adapters, not a UI rewrite.
- Do not add a cloud backend.
- Do not add external runtime APIs.
- The evaluation/demo must remain functional when network access is disabled after local staging.

REQUIRED NAVIGATION
- Dashboard
- Search & Explore
  - Text Search
  - Image Search
  - Polygon Search
  - Advanced Filters
- Change Analysis
  - Before / After
  - Change Mask
  - Temporal Evidence
  - False-Alarm Analysis
- Similar Sites
- Clustering
- Temporal Viewer
- Review Queue
- Data Ingestion
  - GeoTIFF / COG
  - Incremental Update
  - Quality Control
- Data Catalog
- Analytics
- Export & Provenance
- System Status
- Settings

REQUIRED CORE COMPONENTS
1. Trust header: Sudarshan, organisation context, offline state, archive state, analyst state.
2. Workflow stepper for Ingest -> AOI -> Index/Embed -> Cluster/Analyze -> Explore/Review where relevant.
3. Search workspace with semantic text, image, polygon and filters.
4. AOI control with draw/upload/select states.
5. Date range and sensor filters.
6. Ranked result list/grid and map.
7. Selected site evidence panel.
8. Before/after comparison.
9. Temporal timeline with earliest supported change.
10. Change mask view.
11. Quality and false-alarm assessment.
12. Why-this-result explanation.
13. Similar sites discovery.
14. Clustering view.
15. Analyst review queue with confirm/reject.
16. Data ingestion and incremental index UI.
17. Data catalog.
18. Analytics that separate measured values from demo placeholders.
19. Provenance drawer/report.
20. System status.
21. Settings.

VISUAL DIRECTION
Use the supplied screenshots as the visual reference:
- dark navy/near-black background
- cool white text
- restrained blue primary accents
- thin blue-gray borders
- dense but legible desktop layout
- subtle glow only where meaningful
- GIS-style cards and evidence panels
- professional, not gaming-like
- no oversized decorative charts that do not support the analyst task
- no fake map tiles fetched from the internet

MAP RULE
For this frontend stage, a local demo map can be a deterministic visual component with AOI polygon, river, candidate points, legend and scale. Do not use an online map tile service during the demo.

DEMO INTERACTIONS
The critical path must be fully clickable using local fixtures:
Dashboard -> Search & Explore -> query primary string -> ranked candidates -> SITE-A -> Before/After -> Temporal Evidence -> False-Alarm Analysis -> Similar Sites -> Review Queue -> Confirm Change -> Provenance -> Export.

SITE-A DEMO EVIDENCE
The UI must support showing:
- construction/new structure change
- river proximity context
- before/after dates from actual staged data or clearly labelled fixture data
- earliest supported change
- multiple usable observations
- quality checks

SITE-C DEMO EVIDENCE
Must show a seasonal/no-change case that is suppressed rather than treated as construction.

SITE-D DEMO EVIDENCE
Must show a quality-confounded candidate that is suppressed or marked insufficient evidence.

EXPLANATION-FIRST CONFIDENCE
Never show "94%" or any confidence number by itself.
Always show the contributing evidence categories, for example:
- semantic match
- temporal persistence
- spatial relation
- image quality
- registration quality
- sensor consistency

If a value is a fixture, label it as fixture/demo.

PROVENANCE
Every selected result needs a provenance view containing:
- source scene or asset identifier
- acquisition time/date
- sensor/source
- product type
- geographic context
- processing version
- model origin/version/licence when a model is referenced
- index version
- analyst decision
- local file/manifest reference where applicable

INGESTION
The UI must communicate GeoTIFF/COG ingestion, metadata preservation, AOI selection and incremental index updates without requiring a full rebuild. For the frontend demo, this is a local simulation with explicit demo labels until the actual pipeline is integrated.

NO FAKE PRODUCTION CLAIMS
Do not display fabricated metrics such as millions of indexed tiles, measured latency, GPU throughput, or accuracy unless those metrics are actually computed and stored. Use "not measured in fixture mode" when necessary.

CODING STYLE
- Prefer small, composable React components.
- Centralize demo data.
- Use lucide-react for icons if already installed.
- Avoid duplicating CSS rules.
- Keep accessibility basics: labels, button states, keyboard focus, useful aria labels.
- Keep the console clean.

EXECUTION ORDER
Execute in this order:
1. Inspect repository and reference screenshots.
2. Freeze scope in docs/UI_IMPLEMENTATION_PLAN.md.
3. Build shared shell/navigation.
4. Build Search & Explore.
5. Build Site Analysis.
6. Build Temporal Viewer.
7. Build False-Alarm Analysis.
8. Build Similar Sites/Clustering.
9. Build Review Queue.
10. Build Ingestion/Data Catalog.
11. Build Analytics/System Status/Provenance/Settings.
12. Stage the minimal imagery pack.
13. Replace local CSS-only placeholders where verified imagery exists.
14. Perform visual and functional polish.
15. Rehearse the exact demo path.
16. Run npm run build.
17. Produce docs/UI_INTEGRATION_CONTRACT.md and docs/FRONTEND_FREEZE_CHECKLIST.md.

BUILD GATE
After every meaningful implementation phase run:
- npm run build

At the end run:
- npm run build

Do not finish with known build failures.

FINAL ACCEPTANCE TEST
A fresh local run must allow an operator to:
- open Sudarshan
- see offline/demo status
- enter the primary query
- get ranked local results
- open SITE-A
- inspect before/after evidence
- inspect temporal evidence
- inspect false-alarm factors
- find similar sites
- confirm/reject a result
- view provenance
- export the evidence state
- run the secondary query

Do all of this without network access and without depending on a large dataset.

IMPORTANT
Do not silently invent missing data. If a required real imagery field cannot be verified, keep the field explicitly marked "not available in demo" rather than fabricating a realistic-looking value.

Use the supplied files as the source of truth for the UI scope. Keep the implementation focused on the defined demo and do not expand scope until the critical path is stable.
```
