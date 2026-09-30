# Sudarshan - Sequential UI Build Prompts for Claude Code

Paste these prompts into Claude Code **one at a time and in order**. After each prompt, make Claude run the relevant checks and stop so the next prompt can be pasted separately.

## PROMPT 01 - Freeze scope and inspect the existing frontend

```text
You are working inside the existing Sudarshan SIH 26227 frontend repository.

First inspect the entire frontend before changing code. Read the existing source files, package.json, README, docs, and the four reference screenshots in /reference-ui.

Objective:
- Preserve the current React + Vite stack unless there is a concrete reason not to.
- Do not rewrite the repository blindly.
- Do not add a backend.
- Do not add cloud APIs.
- Do not download a large dataset.
- Treat the reference screenshots as the visual target.
- The product name everywhere must be Sudarshan.
- The UI must support a complete analyst flow: Dashboard -> Search & Explore -> Site Analysis -> Temporal Evidence -> False-Alarm Analysis -> Similar Sites -> Review Queue -> Data Provenance / Export.

Create a short implementation checklist in docs/UI_IMPLEMENTATION_PLAN.md and then stop. Do not implement the checklist yet.
```

## PROMPT 02 - Build the application shell and navigation

```text
Implement the Sudarshan application shell from the approved checklist.

Build:
- dark navy geospatial-intelligence visual system
- top trust bar with Sudarshan, Ministry of Defence / Indian Army (DGIS), offline status, local archive status, and analyst session
- left navigation with:
  Dashboard
  Search & Explore
  Change Analysis
  Similar Sites
  Clustering
  Temporal Viewer
  Review Queue
  Data Ingestion
  Data Catalog
  Analytics
  Export & Provenance
  System Status
  Settings
- persistent demo status badge:
  DEMO MODE - LOCAL PRECOMPUTED ARCHIVE

Do not fake a production connection. Do not claim live inference.
Make navigation functional with React state/routing.
Keep responsive behavior stable for desktop demonstration.
Run npm build after implementation and fix all build errors.
Stop after the build passes.
```

## PROMPT 03 - Build Search & Explore exactly around the demo storyline

```text
Implement the Search & Explore screen using the supplied reference layout as the target.

Primary query:
newly built structures near a river

Secondary query:
large vehicle concentrations on open ground

The screen must include:
- Text Query
- Image Search tab
- Polygon Search tab
- Advanced Filters
- AOI controls
- date range
- sensor controls
- quality / cloud filter
- ranked results
- map preview
- quick/example queries
- saved query control
- grid/list toggle

When the user runs the primary query, load local deterministic fixture data for the demo. Do not call a remote model or API.

Every result card must show:
- site ID
- relevance score
- change/category label
- location
- date coverage
- sensor/source when available

Make cards clickable so the selected candidate opens Site Analysis.

Run npm build and stop.
```

## PROMPT 04 - Build Site Analysis and evidence-first change analysis

```text
Build the selected-site workstation for SITE-A.

Required panels:
- selected site header
- confidence / evidence summary
- before / after comparison
- optical and SAR tabs
- change mask
- temporal timeline
- earliest supported change
- Why this result?
- quality and false-alarm assessment
- location context
- analyst tools
- provenance

Use evidence-first wording. Never show a bare confidence score without reasons.

The demo should clearly distinguish:
- supported physical change
- possible change
- suppressed / false alarm
- insufficient evidence

Add actions:
- Add to Review Queue
- Confirm Change
- Reject / False Alarm
- Find Similar Sites
- Export Evidence

Run npm build and stop.
```

## PROMPT 05 - Add the temporal viewer

```text
Implement Temporal Viewer as a first-class module, but reuse the same selected-site data and visual components from Site Analysis.

Show:
- chronological image strip
- acquisition dates
- usable / unusable observation state
- selected observation
- first supported change marker
- play / pause control for the local demo sequence
- change mask preview
- before / after comparison
- observation quality flags

Do not create fake live playback. Playback is only over the local demo sequence.

Run npm build and stop.
```

## PROMPT 06 - Add false-alarm suppression UI and control examples

```text
Implement the False-Alarm Analysis experience.

Create explicit local demo cases:
- SITE-A = supported construction change
- SITE-C = seasonal/no-change control
- SITE-D = quality-confounded candidate

The UI must show a factor-by-factor assessment for:
- cloud/haze
- seasonal variation
- shadow
- viewing geometry
- registration error
- sensor inconsistency
- temporal persistence

For SITE-C, show that the system suppresses the apparent difference.
For SITE-D, show that low evidence quality suppresses the alert.

Never turn a confounder into a real change merely because pixel values differ.

Run npm build and stop.
```

## PROMPT 07 - Add Similar Sites and Clustering

```text
Implement Similar Sites and Clustering as visible analyst modules using the local demo feature records.

Required UI:
- similarity result cards
- similarity score
- shared visual/semantic attributes
- spatial context
- cluster overview
- cluster filters
- selected site -> find similar action

Use the same local fixture/index abstraction that can later be connected to a real embedding service.
Do not introduce an external vector database for this frontend-only stage.

Run npm build and stop.
```

## PROMPT 08 - Add Review Queue and audit trail

```text
Implement a working local Review Queue.

Each candidate must support:
- pending
- confirmed
- rejected / false alarm
- needs review

When an analyst clicks Confirm or Reject:
- update local application state
- show the decision on the selected result
- record a local audit event with timestamp, site ID, decision, and current demo evidence state

Add filters and sorting to the queue.
Do not persist secrets. Local browser/session state is fine for demo behavior, but backend-ready contracts must remain explicit.

Run npm build and stop.
```

## PROMPT 09 - Add Data Ingestion, Catalog and incremental update screens

```text
Implement the data workflow screens.

Data Ingestion must show:
- GeoTIFF / COG / SAFE support messaging
- upload drop zone
- staged files
- provenance fields
- AOI selection
- incremental update state
- existing index preserved

Data Catalog must show a compact table/grid of the locally staged demo assets with:
- asset ID
- date
- sensor
- bounds
- quality state
- checksum / manifest reference when available

For the demo, use only the small staged archive described in docs/DEMO_STORYLINE.md.
Never show a fabricated multi-million-tile archive.

Run npm build and stop.
```

## PROMPT 10 - Add Analytics, System Status and Provenance

```text
Implement:
- Analytics
- System Status
- Export & Provenance
- Settings

Analytics must distinguish measured metrics from demo placeholders.
For the frontend-only demo, use labels such as:
Demo archive size: 32 items
Measured query latency: not available in fixture-only mode
Measured index build time: not available in fixture-only mode

System Status must show:
- network state
- local model/index state
- archive state
- provenance status

Export & Provenance must show:
- source scene
- acquisition time
- sensor/source
- processing version
- model origin/version/license fields
- index version
- analyst decision

Run npm build and stop.
```

## PROMPT 11 - Replace weak placeholders with the small imagery pack

```text
Now stage the smallest approved imagery pack needed by the demo.

Target approximately 30-38 image items total.
Do not download a large regional archive.
Do not use classified or operational imagery.
Use only public or organiser-approved imagery.

Use this grouping:
- SITE-A target: 10 observations
- SITE-B similar: 7 observations
- SITE-C no-change: 7 observations
- SITE-D quality-confounded: 6 observations
- optional secondary-query controls: up to 8 observations only if necessary

For each item, preserve and record actual metadata. Create or update:
- public/imagery/README.md
- data/demo_manifest.json

The manifest must contain actual values for every collected image. Never invent source dates, coordinates, sensors or licences.

If a suitable image cannot be verified, leave the item out rather than fabricating it.

Run npm build and stop.
```

## PROMPT 12 - Final UI polish and evidence-based interaction

```text
Perform a UI polish pass against the four supplied screenshots.

Keep the visual language consistent:
- dark navy background
- restrained blue accents
- white/cool-gray typography
- compact cards
- professional GIS workstation density
- strong hierarchy
- no decorative dashboard clutter

Improve:
- spacing
- alignment
- typography
- hover/focus states
- empty states
- loading states
- error states
- keyboard focus
- button consistency
- evidence labels
- provenance drawers

Do not add fabricated operational statistics.
Do not remove the DEMO MODE disclosure while the pipeline is fixture-only.

Run npm build and stop.
```

## PROMPT 13 - QA and demo rehearsal

```text
Perform a complete local demo rehearsal.

Test this exact path:
Dashboard
-> Search & Explore
-> query: newly built structures near a river
-> select SITE-A
-> Before / After
-> Temporal Viewer
-> Earliest supported change
-> False-Alarm Analysis
-> Similar Sites
-> Review Queue
-> Confirm Change
-> Export & Provenance

Then test:
query: large vehicle concentrations on open ground

Verify:
- no broken navigation
- no console errors
- all buttons have visible outcomes
- all fixture imagery resolves locally
- no network call is required during the demo
- all provenance fields are visible
- demo mode is clearly labelled

Run npm build. Fix everything you find. Stop only after the build and rehearsal pass.
```

## PROMPT 14 - Freeze the frontend for integration

```text
Freeze the frontend as the integration target.

Create:
- docs/UI_INTEGRATION_CONTRACT.md
- docs/DEMO_SCRIPT.md
- docs/FRONTEND_FREEZE_CHECKLIST.md

Define the exact data shapes the future backend must return for:
- search results
- site detail
- temporal observations
- change analysis
- quality / false-alarm factors
- similar sites
- review decision
- provenance

Do not connect the backend yet.
Keep the local demo fixtures as the fallback mode.

Run npm build one final time and stop.
```
