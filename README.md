# SIH-26227 — Semantic Retrieval & Multi-Temporal Change Analysis of Satellite Imagery

<p align="left">
  <img src="https://img.shields.io/badge/Status-Active-brightgreen" />
  <img src="https://img.shields.io/badge/SIH_Problem_ID-26227-blue" />
  <img src="https://img.shields.io/badge/Ministry-Ministry_of_Defence-red" />
  <img src="https://img.shields.io/badge/Department-Indian_Army_(DGIS)-orange" />
  <img src="https://img.shields.io/badge/Category-Software-lightgrey" />
  <img src="https://img.shields.io/badge/Theme-Space_Technology-purple" />
  <img src="https://img.shields.io/badge/Python-3.11+-blue" />
  <img src="https://img.shields.io/badge/PyTorch-2.2+-red" />
</p>

**Organisation:** Ministry of Defence (MoD) · Indian Army — Directorate General of Information Systems (DGIS)  
**Problem Statement ID:** 26227  
**Category:** Software · Space Technology

---

## Problem Statement

Earth-observation archives grow continuously — multi-temporal, multi-spectral, and multi-sensor. Traditional catalogues let analysts filter only by metadata: coordinates, acquisition date, platform, product type. Analysts must still know *where* and *when* to look before they can inspect anything.

**The gap:** satellite imagery is not yet queryable by *meaning* and *change over time*.

This system closes that gap. It makes archived satellite imagery semantically searchable by natural language and detects physically meaningful change between acquisitions — all while preserving geospatial provenance and running fully offline.

---

## Solution Overview

SIH-26227 is an end-to-end, air-gapped Earth Observation intelligence platform that unifies:

| Capability | Mechanism |
| :--- | :--- |
| **Semantic NL Retrieval** | RemoteCLIP 512-dim vision-language embeddings + Qdrant local vector search |
| **Bi-Temporal Change Detection** | Siamese U-Net / ResNet-18 + CBAM attention — native 1024×1024 resolution |
| **False-Alarm Suppression** | Phase-correlation registration, cloud masking, VARI vegetation filter, morphological cleaning |
| **Multi-Temporal Tracking** | $O(\log N)$ bisection search — pinpoints exact change onset timestamp |
| **Analyst Workflow & Provenance** | SHA-256 hash-chained audit log + RFC 7946 GeoJSON export |
| **Discovery Clustering** | UMAP + HDBSCAN — surfaces uncataloged change patterns without supervision |
| **Active Learning Feedback** | Rocchio relevance vector shift on analyst Confirm/Reject decisions |
| **Offline Air-Gapped Operation** | Zero external APIs. All models, embeddings, and vector indices run locally |

---

## Benchmark Results

Evaluation on **19,490 image pairs** across 5 satellite benchmarks:

| Architecture | Training | F1 | IoU | Precision | Recall | FPR | Latency |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| Siamese ResNet-18 Baseline | LEVIR-CD only | 0.330 | 0.198 | 0.340 | 0.321 | 0.047 | 30.8 ms |
| **Siamese ResNet-18 + CBAM** | **Unified 5-Dataset** | **0.884** | **0.792** | **0.908** | **0.862** | **0.048** | **34.9 ms** |

Peak VRAM consumption: **720 MB** — leaving over 3 GB headroom on RTX 3050 4 GB.

---

## Hardware Target

| Component | Specification |
| :--- | :--- |
| CPU | Intel Core i5-12450H |
| RAM | 16 GB DDR4 |
| GPU | NVIDIA GeForce RTX 3050 Laptop (4 GB VRAM) |
| CUDA | 12.6+ |
| OS | Linux (primary) / Windows 11 |

---

## Repository Structure

```text
SIH-2026/
├── backend/                  # FastAPI backend service
│   ├── app.py                # Production entrypoint
│   └── README.md             # API documentation & endpoint reference
│
├── data/                     # Dataset catalogs & metadata (no raw rasters committed)
│   ├── dataset_inventory.json
│   ├── dataset_manifest.json
│   ├── dataset_report.md
│   └── README.md
│
├── docs/                     # Technical documentation
│   ├── architecture/         # System design, API & data contracts, ADR log
│   ├── evaluation/           # Evaluation methodology & metrics plan
│   ├── experiments/          # ML experiment log
│   ├── meetings/             # Sprint meeting notes
│   └── research/             # Domain research: datasets, ML approaches, EO literature
│
├── experiments/              # Experiment artefacts & model checkpoints
│   ├── unified_5datasets_cbam/   # Primary model (61.8 MB, .pt gitignored)
│   ├── levir_baseline/           # Baseline model (gitignored)
│   ├── model_comparison_benchmark.json
│   ├── practical_test_results.json
│   └── results.csv
│
├── frontend/                 # React 19 + Vite GEOINT C2 Analyst Dashboard
│   ├── src/
│   │   ├── tabs/             # 9 operational workspaces (dashboard, chat, detection, ...)
│   │   └── components/       # Header, Sidebar
│   ├── server.js             # Production Node.js proxy
│   ├── vite.config.js
│   └── README.md
│
├── models/                   # Model cards & threshold registry
│   ├── best_threshold.json
│   └── README.md
│
├── project_code/             # Core Python source package
│   ├── api/                  # FastAPI app with all endpoints
│   ├── models/               # Siamese ResNet-18 + CBAM, LightweightChangeFormer, losses
│   ├── false_alarm/          # Phase correlation, cloud masking, VARI, morphology
│   ├── retrieval/            # RemoteCLIP encoder, Qdrant indexer, 4-bit quantizer
│   ├── temporal/             # Change timeline, O(log N) bisection search
│   ├── clustering/           # UMAP + HDBSCAN discovery
│   ├── provenance/           # SHA-256 audit logger
│   ├── chat/                 # 100% offline multimodal tactical chat engine
│   ├── training/             # Unified multi-dataset trainer + LEVIR baseline
│   ├── evaluation/           # Metrics, benchmark runner, threshold optimizer
│   ├── datasets/             # Dataset adapters and unified loader
│   ├── ingestion/            # File-system scene watcher
│   └── config.py             # Cross-platform dynamic path resolution
│
├── scripts/                  # Utility & diagnostic scripts
│   ├── run_training.py       # Full training launcher
│   ├── benchmark_models.py   # Head-to-head model comparison
│   ├── run_practical_test.py # Practical accuracy evaluation
│   ├── check_torch.py        # GPU/CUDA verification
│   └── diagnostic_ground_truth.py
│
├── tests/                    # Automated test suite
│   ├── test_smoke.py         # Import / sanity checks
│   ├── test_endpoints.py     # Full 13-endpoint API integration test
│   ├── test_dual_inference.py
│   ├── test_tiling.py
│   └── test_offline_chat.py
│
├── best_model.json           # Selected architecture + benchmark metrics
├── .env.example              # Environment variable reference
├── pyproject.toml            # Python project metadata
├── requirements.txt          # Pinned production dependencies
├── CONTRIBUTING.md           # Contribution guidelines
├── CODEOWNERS                # Ownership & review routing
└── LICENSE
```

---

## Quickstart

### 1. Clone & Install

```bash
git clone https://github.com/mradul-grit/SIH-2026.git
cd SIH-2026
python -m venv .venv && source .venv/bin/activate   # Linux / macOS
# .venv\Scripts\activate                             # Windows
pip install -r requirements.txt
```

For CUDA 12.6 (recommended for RTX 3050):
```bash
pip install torch torchvision --extra-index-url https://download.pytorch.org/whl/cu126
```

### 2. Configure Environment

```bash
cp .env.example .env
# Edit PROJECT_ROOT if your datasets live on a separate drive
```

### 3. Start the Backend API

```bash
python -m uvicorn backend.app:app --host 127.0.0.1 --port 8000
```

Interactive docs: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

### 4. Start the GEOINT Analyst Dashboard

```bash
cd frontend
node server.js     # Production: http://localhost:3000
# or
npm run dev        # Development HMR: http://localhost:5173
```

### 5. Run the Automated Test Suite

```bash
pytest tests/ -v
```

---

## System Architecture

```
                            ANALYST
                               │
                     ┌─────────▼─────────┐
                     │  React 19 GEOINT   │
                     │  C2 Dashboard       │  (9 Operational Tabs)
                     └─────────┬─────────┘
                               │ HTTP/REST
                     ┌─────────▼─────────┐
                     │   FastAPI Backend  │  (13 Endpoints)
                     └──┬──────┬──────┬──┘
                        │      │      │
          ┌─────────────┘      │      └─────────────┐
          ▼                    ▼                     ▼
  ┌───────────────┐   ┌────────────────┐   ┌──────────────────┐
  │ Change        │   │ Semantic       │   │ Temporal         │
  │ Detection     │   │ Retrieval      │   │ Bisection        │
  │ Pipeline      │   │ Engine         │   │ Engine           │
  └───────┬───────┘   └───────┬────────┘   └────────┬─────────┘
          │                   │                      │
  ┌───────▼───────┐   ┌───────▼────────┐   ┌────────▼─────────┐
  │ Siamese       │   │ RemoteCLIP     │   │ Change Timeline  │
  │ ResNet-18     │   │ Encoder        │   │ Builder          │
  │ + CBAM        │   │ + Qdrant DB    │   │ O(log N)         │
  └───────┬───────┘   └────────────────┘   └──────────────────┘
          │
  ┌───────▼───────┐
  │ False-Alarm   │  ← Phase correlation, cloud masking,
  │ Suppression   │    VARI filter, morphological cleaning
  └───────┬───────┘
          │
  ┌───────▼───────┐
  │ Provenance    │  ← SHA-256 audit chaining, GeoJSON export
  │ Audit Logger  │
  └───────────────┘
```

---

## Core Modules

### `project_code/models/` — Neural Architecture

| File | Description |
| :--- | :--- |
| `siamese_resnet18.py` | Siamese U-Net with shared ResNet-18 encoder, multi-scale difference fusion, CBAM/SE attention, binary & semantic heads |
| `lightweight_changeformer.py` | Transformer-based dual-stream change detection with cross-attention |
| `attention_modules.py` | CBAM (Channel + Spatial Attention) and SEBlock implementations |
| `losses.py` | Focal loss, Dice loss, and combined loss functions for class-imbalanced change masks |

### `project_code/false_alarm/` — Signal Integrity Pipeline

| File | Description |
| :--- | :--- |
| `registration.py` | 2D phase-correlation sub-pixel co-registration validator |
| `quality_mask.py` | Luminance histogram cloud & shadow masking |
| `spectral_check.py` | VARI optical vegetation change filter (suppresses seasonal greening false alarms) |
| `postprocess.py` | Morphological opening/closing, connected-component cleaning, hole-filling |

### `project_code/retrieval/` — Multimodal Semantic Search

| File | Description |
| :--- | :--- |
| `remoteclip_encoder.py` | Offline vision-language embedding (512-dim, ResNet-18 backbone, ImageNet-normalized) |
| `qdrant_indexer.py` | Qdrant local vector store; falls back to in-memory store if `qdrant-client` not installed |
| `quantizer_4bit.py` | 4-bit scalar quantization — 8× memory reduction for large tile catalogs |
| `search_engine.py` | Cosine-similarity search with Rocchio active learning relevance feedback |

### `project_code/temporal/` — Multi-Temporal Engine

| File | Description |
| :--- | :--- |
| `temporal_sequence.py` | Chronological sequence analyzer across $N$ acquisitions |
| `change_timeline.py` | Timeline narrative builder (no_change → construction_detected → expansion) + $O(\log N)$ bisection search |

---

## Environment Variables

See [`.env.example`](.env.example) for all configurable keys:

```bash
PROJECT_ROOT=/path/to/SIH-2026    # Override auto-detected project root
API_HOST=127.0.0.1                 # FastAPI bind address
API_PORT=8000                      # FastAPI bind port
```

---

## License

[MIT License](LICENSE)

---


