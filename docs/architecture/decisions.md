# Architecture Decision Log — SIH-26227

Decisions are recorded here to preserve rationale for reviewers and future team members.

---

## ADR-001 — Siamese U-Net with ResNet-18 as Primary Architecture

**Date:** 2026-09-20  
**Status:** Accepted  
**Owner:** ML Team

### Context
We need a change detection model that can run on 4 GB VRAM without quality degradation on 1024×1024 optical satellite imagery.

### Decision
Siamese U-Net with shared ResNet-18 encoder backbone, CBAM bottleneck attention, and multi-scale difference feature fusion: `Concat(F1, F2, |F1 − F2|)`.

### Alternatives
- **ChangeFormer (full transformer)**: Exceeds 4 GB VRAM at native resolution. Kept as lightweight variant only.
- **FC-EF (Fully Convolutional Early Fusion)**: Misses long-range building edge features. Rejected.
- **SiamCRNN**: Complex temporal RNN overhead not justified for bi-temporal pairs.

### Reason
ResNet-18 has a small parameter count (~11 M) while the difference feature fusion and CBAM attention recover boundary precision lost by smaller backbones. Validated with F1=0.884, IoU=0.792 on 5 benchmarks, 720 MB peak VRAM.

---

## ADR-002 — Native-Resolution Sliding Window Inference

**Date:** 2026-09-21  
**Status:** Accepted  
**Owner:** ML Team

### Context
Naively resizing 1024×1024 satellite imagery to 256×256 for batch inference destroys fine building edge information causing >12% F1 degradation.

### Decision
Adaptive tiling: scenes ≤ 256×256 → single padded forward pass; scenes > 256×256 → 256×256 sliding window at stride 224 (32 px overlap) with probability-map averaging.

### Reason
Maintains native spatial resolution. Batch size kept at 2 to respect < 1.2 GB VRAM during inference, compatible with RTX 3050 4 GB.

---

## ADR-003 — Qdrant Local Engine for Vector Indexing

**Date:** 2026-09-22  
**Status:** Accepted  
**Owner:** Backend Team

### Context
The system must perform sub-second semantic retrieval over potentially 100,000+ satellite tile embeddings without any external cloud service.

### Decision
Qdrant Local Engine with on-disk persistence at `database/qdrant_storage/`. Falls back to an in-memory cosine-search store if `qdrant-client` is not installed.

### Alternatives
- **FAISS**: Less ergonomic metadata handling and no native HTTP server option for future scaling.
- **ChromaDB**: Heavier runtime dependencies.
- **PostgreSQL + pgvector**: Requires database server setup not suitable for edge deployment.

### Reason
Qdrant operates as a single embedded library with no daemon process. Zero external dependencies for offline use. Supports cosine similarity, metadata filtering, and UPSERT without rebuilding the index.

---

## ADR-004 — SHA-256 Hash Chaining for Audit Provenance

**Date:** 2026-09-23  
**Status:** Accepted  
**Owner:** Backend Team

### Context
Defense use case requires tamper-evident, cryptographically verifiable audit trails for every analyst decision.

### Decision
Each log record's hash is computed as `SHA-256(JSON(record) + previous_record_hash)`, forming a chain analogous to a blockchain commit structure. Stored as JSONL (`logs/audit_provenance.jsonl`).

### Reason
Simple to implement, independently verifiable by any SHA-256 tool, zero external dependencies. RFC-compliant ISO-8601 UTC timestamps included.

---

## ADR-005 — Project Root Dynamic Path Resolution

**Date:** 2026-09-29  
**Status:** Accepted  
**Owner:** Backend Team

### Context
The project was originally developed on Windows with hardcoded drive letters (`g:/natraj26227/`). It needs to run identically on Linux, macOS, and Windows without manual configuration.

### Decision
Created `project_code/config.py` which resolves `PROJECT_ROOT` dynamically using `Path(__file__).resolve().parents[N]`, with `PROJECT_ROOT` environment variable override support. All modules import path constants from this single config.

### Reason
Eliminates all platform-specific path assumptions. One `export PROJECT_ROOT=/custom/path` environment variable covers all deployment scenarios.
