# Sudarshan - Live Demo Storyline

## 1. Demo objective

Demonstrate one complete analyst workflow for SIH PS 26227 using a very small, locally staged imagery archive. The UI should feel like a real workstation, but every value shown in demo mode must come from local fixtures or actual locally staged imagery. Do not present precomputed fixture values as live ML inference.

## 2. Primary investigation

Primary query:

> newly built structures near a river

The analyst is asking Sudarshan to discover candidate locations from imagery, constrain the search with an AOI/date/sensor filter, inspect one selected site through time, identify a supported physical change, estimate the earliest supported observation, check false-alarm factors, discover similar sites, record an analyst decision, and export provenance.

## 3. Secondary investigation

Secondary query:

> large vehicle concentrations on open ground

Use this only after the primary path is demonstrated. It proves that the search workflow is not hard-coded to one phrase and demonstrates a second semantic concept with optical/SAR cross-checking.

## 4. Minimal imagery pack

Target approximately 30-38 local image tiles/items. Prefer the smallest set that covers every visible demo state.

| Demo set | Suggested observations | Purpose |
|---|---:|---|
| SITE-A target | 10 | Real or organiser-generated temporal sequence with a construction-type change near a river |
| SITE-B similar | 7 | Similar-site discovery / embedding or visual similarity |
| SITE-C no-change control | 7 | Seasonal/environmental variation that should not become a reported construction change |
| SITE-D quality control | 6 | Haze/cloud/shadow/illumination/registration confounder example |
| Secondary-query controls | 0-8 | Optional small extension for the vehicle-concentration query |

Do not download an entire regional archive. Every collected image must have a reason to exist in the demo.

## 5. Metadata that must stay with every image

- source scene or asset identifier
- acquisition date/time
- sensor/source
- product type
- geographic bounds / geometry
- CRS/georeferencing
- spatial resolution when available
- quality information used by the demo
- source URL or catalogue identifier
- licence / usage note
- local file path / checksum once staged

Never invent acquisition dates, sensor names, coordinates, licence information, confidence values, or processing metrics.

## 6. UI demo sequence

### Step 1 - Launch

Open Dashboard. Show:

- Sudarshan branding
- Ministry of Defence / Indian Army (DGIS) context shown in the reference UI
- Offline status
- local archive status
- analyst session
- small demo dataset count

Say:

> "This is the Sudarshan analyst workstation. The demo archive is staged locally so the same workflow can run without network access."

### Step 2 - Semantic search

Open Search & Explore.

Enter:

`newly built structures near a river`

Keep the AOI and date range visible. Show the result count, ranked cards, semantic relevance, location, and temporal coverage.

Say:

> "The analyst starts with meaning rather than a scene ID. Sudarshan combines the text query with spatial, temporal, sensor, and quality filters."

### Step 3 - Select candidate

Select SITE-A.

Show:

- map location
- candidate type
- score / confidence
- selected imagery dates
- provenance summary

### Step 4 - Before / after

Open Change Analysis for SITE-A.

Show a before image and an after image from actual local imagery or clearly labelled demo imagery.

Then show the change mask.

### Step 5 - Temporal evidence

Move across the timeline. Identify the first observation where the change is supported by usable imagery.

The key output is:

`Earliest supported change`

Do not claim a date earlier than the first supported usable observation.

### Step 6 - False-alarm analysis

Show the evidence panel for:

- cloud/haze
- seasonal variation
- shadow effect
- viewing geometry
- registration quality
- sensor consistency
- temporal persistence

For SITE-C, explicitly demonstrate that seasonal variation does not become a false construction alert.

For SITE-D, demonstrate suppression of a low-quality change candidate.

### Step 7 - Similar-site discovery

From SITE-A, click `Find Similar Sites`.

Show SITE-B and other local matches. Explain that these are retrieved from the same local feature/index layer and are not additional network searches.

### Step 8 - Analyst review

Add SITE-A to the review queue.

Use:

`Confirm Change`

or

`Reject / False Alarm`

The UI should immediately show the decision status and retain the event in the audit trail.

### Step 9 - Provenance

Open Data Provenance / Export & Reports.

Show source scene, acquisition time, sensor/source, processing version, model version/origin, index version, and analyst decision record.

### Step 10 - Optional secondary query

Run:

`large vehicle concentrations on open ground`

Show the second ranked set. Select a candidate and demonstrate that the same UI workflow can be reused.

## 7. What the demo must visibly prove

1. Free-text semantic retrieval exists as a first-class workflow.
2. Results are rank ordered and filterable.
3. A selected site can be examined across time.
4. Change is evidenced with before/after and a change mask.
5. Earliest supported change is derived from usable observations.
6. Quality and false-alarm factors are explicit rather than hidden.
7. Similar-site discovery is a first-class action.
8. Analyst confirmation/rejection creates a review record.
9. Provenance is visible and exportable.
10. The demo archive is small, local, reproducible, and offline-ready.

## 8. Dataset rule for the builder

Use the smallest imagery set that can demonstrate every screen. The initial target is 30-38 image items. If a screen can be demonstrated using a tile already in the pack, do not collect another tile.

The official PS allows public or organiser-generated imagery for the demonstration and requires offline operation after local staging; the UI plan therefore treats the small local archive as a deliberate demo design, not as a full production archive.
