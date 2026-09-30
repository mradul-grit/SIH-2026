# Sudarshan - Frontend Demo (SIH 26227)

Frontend-only, local deterministic demonstration of the Sudarshan analyst workflow for SIH PS 26227.

## Primary demo query

`newly built structures near a river`

## Secondary demo query

`large vehicle concentrations on open ground`

## Scope

The UI is intentionally built around a very small local archive target of 30-38 imagery items. The repository does not require a large satellite archive to render the complete judge workflow.

## Demo mode boundary

The application uses local fixtures in the current frontend-only stage. It is explicitly labelled:

`DEMO MODE - LOCAL PRECOMPUTED ARCHIVE`

Do not present fixture results as live ML inference. Replace the data adapters with the local retrieval/change services once those services are available.

## Run

```bash
npm install
npm run dev
```

## Build

```bash
npm run build
```

## Reference material

- `/reference-ui/` - the four supplied UI reference images with Sudarshan branding
- `/docs/DEMO_STORYLINE.md` - exact demo narrative and minimal dataset plan
- `/docs/UI_BUILD_PROMPTS.md` - sequential prompts for Claude Code
- `/docs/FAST_UI_BUILD_PLAYBOOK.md` - fast, phase-by-phase execution flow
- `/docs/CLAUDE_MASTER_PROMPT.md` - single master execution prompt
- `/docs/UI_COMPONENT_MATRIX.md` - UI component-to-service mapping
- `/data/demo_manifest.json` - minimal imagery pack manifest template
- `/docs/UI_COMPONENT_MATRIX.md` - component inventory and integration boundaries

## Future integration seam

The UI should be connected to real local services for:

- semantic retrieval
- image-to-image retrieval
- change detection
- false-alarm suppression / quality scoring
- clustering
- provenance
- incremental ingestion

No cloud runtime dependency is required by this frontend.
