# System Architecture — SIH-26227

This document describes the component-level architecture of the Semantic Retrieval & Multi-Temporal Change Analysis platform.

---

## Component Inventory

| # | Component | Module | Owner |
| :--- | :--- | :--- | :--- |
| 1 | Data Ingestion & File Watching | `project_code/ingestion/` | Backend team |
| 2 | Geospatial Preprocessing & Tiling | `project_code/datasets/` | Backend team |
| 3 | Neural Change Detection | `project_code/models/` | ML team |
| 4 | False-Alarm Suppression Pipeline | `project_code/false_alarm/` | ML team |
| 5 | Vision-Language Embedding Engine | `project_code/retrieval/remoteclip_encoder.py` | ML team |
| 6 | Vector / Geospatial Index | `project_code/retrieval/qdrant_indexer.py` | Backend team |
| 7 | Semantic Retrieval & NL Search | `project_code/retrieval/search_engine.py` | ML team |
| 8 | Multi-Temporal Change Analysis | `project_code/temporal/` | ML team |
| 9 | Discovery Clustering | `project_code/clustering/` | ML team |
| 10 | Provenance & Audit Logging | `project_code/provenance/` | Backend team |
| 11 | Offline Tactical Chat Engine | `project_code/chat/` | ML team |
| 12 | REST API | `project_code/api/` | Backend team |
| 13 | Analyst GEOINT C2 Dashboard | `frontend/` | Frontend team |
| 14 | Evaluation & Benchmarking | `project_code/evaluation/` | ML team |

---

## Integration Principle

Every component must define:
- **Input schema** — types, shapes, coordinate reference systems (CRS)
- **Output schema** — types, shapes, uncertainties
- **Owner** — responsible team member
- **Automated test** — at minimum one pytest smoke test

Do not integrate only at the end. A mock end-to-end pipeline (`/api/health` → `/api/change-detect`) was running by Day 1.

---

## Data Flow

```
GeoTIFF / PNG Scene (T1, T2)
       │
       ▼
[Ingestion Watcher]   ← project_code/ingestion/watcher.py
       │ lazy 256×256 patch extraction
       ▼
[Preprocessing]       ← project_code/datasets/patch_extractor.py
  - normalize [0,1]
  - CRS validation
  - cloud fraction check
       │
       ├──────────────────────────────────────────┐
       ▼                                          ▼
[Change Detection Pipeline]             [Embedding Engine]
  registration check                      RemoteCLIP 512-dim
  cloud/shadow mask                       Qdrant insert
  neural inference (sliding window)       active learning
  VARI spectral filter                          │
  morphological cleaning                  [Semantic Search]
       │                                  text → cosine rank
       ▼
[Binary Change Mask + Probability Map]
       │
       ├─── [Multi-Temporal Timeline Builder]
       │         O(log N) bisection → earliest onset
       │
       ├─── [Discovery Clustering]
       │         UMAP + HDBSCAN
       │
       └─── [Provenance Audit Logger]
                 SHA-256 hash chain
                 RFC 7946 GeoJSON
```

---

## Inference Architecture: Native-Resolution Sliding Window

For 1024×1024 scenes the system applies an adaptive sliding window approach:

- **Small scenes (≤ 256×256)**: padded single forward pass.
- **Large scenes (> 256×256)**: 256×256 sliding window at stride 224 (32 px overlap), batch size 2, probability maps averaged via weighted blending.

This prevents destructive resolution squashing that loses fine building boundary information.

**Peak VRAM**: 720 MB (RTX 3050 4 GB has > 3 GB headroom during inference).

---

## False-Alarm Suppression Stage

Four sequential filters applied before the change mask is returned:

| Stage | Method | Purpose |
| :--- | :--- | :--- |
| 1. Registration | 2D Phase Correlation (sub-pixel) | Detect mis-aligned acquisition pairs |
| 2. Radiometric Quality | Luminance histogram threshold | Flag cloudy, saturated, or shadowed imagery |
| 3. Spectral Consistency | VARI index ($\frac{G - R}{G + R - B}$) | Suppress seasonal vegetation change false alarms |
| 4. Morphological Cleaning | Opening + Closing + CC filtering | Remove isolated noise pixels, fill building contour holes |

---

## Cryptographic Provenance

Every analyst review event (CONFIRM / REJECT / NEEDS_REVIEW) produces an immutable log record:

```json
{
  "timestamp": "2026-09-29T15:41:07.881Z",
  "analyst_id": "analyst_primary",
  "action": "CONFIRM",
  "tile_id": "levir_test_10",
  "model_version": "SiameseResNet18-CBAM-v1.0",
  "threshold": 0.50,
  "change_percentage": 9.72,
  "record_hash": "78693fad062f..."
}
```

Each `record_hash` is `SHA-256(record_string + previous_record_hash)` — forming a tamper-evident chain analogous to blockchain audit logs.
