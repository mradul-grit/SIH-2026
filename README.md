# Semantic Retrieval & Multi-Temporal Change Analysis of Satellite Imagery

> An offline, provenance-aware AI/ML system for semantic satellite-image retrieval, image-to-image similarity search, and multi-temporal change analysis.

**SIH Problem ID:** 26227  
**Organization:** Ministry of Defence (MoD)  
**Department:** Indian Army (DGIS)  
**Category:** Software  
**Theme:** Space Technology

---

## 1. Problem

Earth-observation archives are increasingly multi-temporal, multi-spectral and multi-sensor. Traditional catalogues mainly search by metadata such as coordinates, acquisition date, platform and product type. Analysts still need to know where and when to look before inspecting imagery.

This project aims to make satellite imagery queryable by **meaning and change over time**, while retaining spatial, temporal and sensor filtering.

The system must operate locally/on-premises and preserve geospatial provenance.

## 2. Proposed Solution

The prototype will combine:

1. **Semantic retrieval** — natural-language search over satellite-image tiles.
2. **Image-to-image retrieval** — find visually/semantically similar locations.
3. **Multi-temporal change analysis** — identify meaningful appearance, disappearance, expansion and contraction.
4. **False-alarm suppression** — handle clouds, haze, seasonality, illumination, view angle and registration differences.
5. **Discovery & clustering** — group similar sites using embeddings.
6. **Analyst workflow & provenance** — ranked review queue with before/after evidence and processing history.
7. **Incremental ingestion** — add new GeoTIFF/COG imagery without rebuilding the entire index.
8. **Offline operation** — approved models, libraries and datasets staged locally; no external APIs during evaluation.

## 3. MVP

### Must Have
- GeoTIFF/COG ingestion
- Metadata preservation
- Tile generation/indexing
- Text → image semantic retrieval
- Image → image similarity retrieval
- Before/after change detection for a selected AOI
- Confidence/quality handling
- Map/result interface
- Provenance for every result
- Offline inference
- Reproducible evaluation

### Stretch Goals
- Site clustering
- Analyst feedback → reranking
- Multi-sensor fusion
- Advanced change-type classification
- Incremental index update benchmark

## 4. Architecture

```text
                     ANALYST
                        |
                        v
                +----------------+
                | Web Interface  |
                +----------------+
                        |
                        v
                +----------------+
                | Search / API   |
                +----------------+
                  /      |       \
                 /       |        \
                v        v         v
          Semantic   Change     Metadata
          Retrieval  Analysis    Filters
              |         |          |
              +---------+----------+
                        |
                        v
              +--------------------+
              | Vector / Geo Index |
              +--------------------+
                        |
                        v
              +--------------------+
              | EO Data & Metadata |
              +--------------------+

Offline AI/ML:
  imagery -> preprocessing -> embeddings -> vector index
                       |
                       +-> temporal pairs -> change model -> quality/confidence
```

## 5. Repository Structure

```text
.
├── README.md
├── LICENSE
├── .gitignore
├── .env.example
├── requirements.txt
├── pyproject.toml
│
├── docs/
│   ├── research/
│   │   ├── problem-understanding.md
│   │   ├── existing-solutions.md
│   │   ├── ml-approaches.md
│   │   ├── data.md
│   │   ├── technical-feasibility.md
│   │   └── product-and-mvp.md
│   ├── architecture/
│   │   ├── system-architecture.md
│   │   ├── api-contract.md
│   │   ├── data-contract.md
│   │   └── decisions.md
│   ├── experiments/
│   │   └── experiment-log.md
│   ├── evaluation/
│   │   └── evaluation-plan.md
│   └── meetings/
│       └── day-01.md
│
├── src/
│   ├── data/
│   ├── preprocessing/
│   ├── retrieval/
│   ├── change_detection/
│   ├── embeddings/
│   ├── indexing/
│   └── evaluation/
│
├── backend/
├── frontend/
├── tests/
├── configs/
├── scripts/
├── data/
│   └── README.md
├── models/
│   └── README.md
└── .github/
    ├── workflows/ci.yml
    ├── ISSUE_TEMPLATE/feature.md
    ├── ISSUE_TEMPLATE/research.md
    └── PULL_REQUEST_TEMPLATE.md
```

## 6. Team

| Member | Primary Ownership | Integration Responsibility |
|---|---|---|
| M1 | Tech Lead / Architecture | Contracts, integration, reviews |
| M2 | Data / Geospatial Pipeline | Imagery, tiling, metadata |
| M3 | ML / Embeddings | Semantic model, retrieval experiments |
| M4 | Change Detection / ML | Temporal comparison, quality handling |
| M5 | Backend / API | Search, inference, metadata APIs |
| M6 | Frontend / DevOps / QA | UI, CI, testing, deployment |

Roles can overlap, but every component has one accountable owner.

## 7. Integration Contract

The team will agree on interfaces before implementation.

```text
Frontend
   |
   | HTTP/JSON
   v
Backend API
   |
   | typed request
   v
Retrieval / Change services
   |
   | standard internal result
   v
Models + Vector Index
```

Example retrieval result:

```json
{
  "tile_id": "tile_001",
  "score": 0.91,
  "geometry": {},
  "acquisition_time": "YYYY-MM-DDTHH:MM:SS",
  "sensor": "Sentinel-2",
  "source_scene": "scene_id",
  "processing_version": "v0.1",
  "confidence": 0.88
}
```

The exact schema is maintained in `docs/architecture/api-contract.md`.

## 8. Data Sources

The supplied problem statement identifies:
- Copernicus Sentinel-2 optical imagery
- Sentinel-1 SAR
- USGS Landsat Collection 2
- NRSC/ISRO Bhuvan open Earth-observation data

All datasets/models must have provenance and applicable licence information recorded before use.

## 9. 25-Day Prototype Roadmap

| Days | Goal | Exit Criteria |
|---|---|---|
| 1–2 | Research | Problem, gaps, data, models, risks documented |
| 3 | MVP + architecture | Contracts and scope frozen |
| 4–5 | Foundation | Repo, environments, data pipeline skeleton |
| 6–7 | End-to-end skeleton | UI → API → mock model → result works |
| 8–12 | Real ML | Real embeddings/change pipeline integrated |
| 13–15 | Model/data improvement | Baseline + experiments + evaluation |
| 16–18 | Full integration | Retrieval + change + provenance connected |
| 19–21 | Product polish | UX, robustness, latency, errors |
| 22–23 | Testing | Unit/integration/evaluation tests |
| 24 | Freeze | Deployment, docs, demo data, presentation |
| 25 | Final | Regression test + final demo rehearsal |

## 10. Git Workflow

```text
main
  ^
  | release PR
develop
  ^
  | PR + review + CI
feature/*
```

Rules:
- No direct pushes to `main`.
- Every task gets an issue.
- Every implementation gets a branch.
- Every branch becomes a pull request.
- At least one teammate reviews a PR.
- CI must pass before merge.
- Do not commit secrets, raw datasets or unnecessary model artifacts.
- Keep contracts stable; changes to contracts require team agreement.
- Merge small, focused PRs.

Recommended branch names:

```text
feature/data-ingestion
feature/semantic-retrieval
feature/change-detection
feature/backend-api
feature/frontend-map
feature/evaluation
fix/registration-error
docs/research-update
```

## 11. Research Rule

Every research finding should answer:

- What question were we investigating?
- What did we find?
- What is the source?
- Why does it matter?
- What decision does it support?
- What is our confidence?

Research belongs in `docs/research/`, not as random links in chat.

## 12. ML Experiment Rule

Every meaningful experiment records:

- Experiment ID
- Date
- Dataset/version
- Model
- Parameters
- Hardware
- Metrics
- Baseline comparison
- Conclusion
- Code commit

See `docs/experiments/experiment-log.md`.

## 13. Evaluation

The problem statement calls for reproducible reporting of:
- Indexed area
- Number of scenes/tiles
- Index build time
- Storage footprint
- Query latency
- Hardware used

Retrieval should be evaluated on held-out semantic queries and relevance judgements.

Change analysis should be evaluated on held-out labelled change/no-change cases.

See `docs/evaluation/evaluation-plan.md`.

## 14. Offline/Sovereignty Requirement

The evaluation environment must work after network access is disabled, once approved models, libraries and datasets have been staged locally.

Every pretrained model must record:
- Origin
- Licence
- Version
- Weight filename/checksum
- Offline loading procedure

## 15. Current Status

**Project phase:** Research / repository setup  
**MVP:** To be frozen on Day 3  
**Model:** TBD after research  
**Dataset:** TBD after licence/availability verification  
**Deployment:** TBD

## 16. Documentation

- [Research](docs/research/problem-understanding.md)
- [Architecture](docs/architecture/system-architecture.md)
- [API Contract](docs/architecture/api-contract.md)
- [Decision Log](docs/architecture/decisions.md)
- [Experiment Log](docs/experiments/experiment-log.md)
- [Evaluation Plan](docs/evaluation/evaluation-plan.md)
