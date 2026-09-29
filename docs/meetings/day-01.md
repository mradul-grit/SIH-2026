# Meeting Notes — Day 01

**Date:** 2026-09-20  
**Attendees:** Full team  
**Duration:** 2 hours

---

## Agenda & Outcomes

### 1. Problem Understanding

- Read and decomposed SIH-26227 problem statement from MoD / DGIS.
- Key challenge identified: satellite archives are metadata-only searchable. Analysts need *semantic* queryability.
- Three core deliverables agreed: (a) semantic NL retrieval, (b) bi-temporal change detection, (c) analyst provenance workflow.

### 2. Dataset Selection

Shortlisted 5 benchmark datasets covering aerial and satellite optical change detection:
- LEVIR-CD (0.5 m GSD, building change, 637 pairs)
- LEVIR-CD+ (extended version, 985 pairs)
- WHU-CD (aerial orthophoto, 0.2 m GSD, Christchurch NZ, 1950 pairs)
- S2Looking (side-looking VHR satellites, multi-class mask, 3918 pairs)
- SYSU-CD (aerial optical RGB, 256×256 tiles, 12000 pairs)

**Total: 19,490 image pairs, 24.82 GB.**

### 3. Architecture Decisions

- Primary model: Siamese U-Net + ResNet-18. Justification: proven on LEVIR-CD, runs on 4 GB VRAM.
- Semantic retrieval: RemoteCLIP vision-language embeddings + Qdrant local vector DB.
- API: FastAPI (async, auto-docs, pydantic validation).
- Frontend: React 19 + Vite (single-page tactical dashboard).
- No external cloud APIs — full offline operation mandatory.

### 4. Task Assignment

| Task | Owner | Deadline |
| :--- | :--- | :--- |
| Repository setup & CI skeleton | Mradul | Day 01 |
| Dataset ingestion adapters (5 datasets) | ML Team | Day 02 |
| Siamese model implementation | ML Team | Day 02 |
| FastAPI endpoint skeleton | Backend Team | Day 02 |
| React dashboard skeleton | Frontend Team | Day 03 |
| False-alarm pipeline | ML Team | Day 03 |
| Training launcher | ML Team | Day 04 |
| End-to-end integration | All | Day 05 |
| Benchmarks & evaluation | ML Team | Day 06 |
| Demo + polish | All | Day 07 |

### 5. Environment & Tooling

- Python 3.11, PyTorch 2.2+, CUDA 12.6
- Development on Windows (primary) + Linux (CI/server)
- Git branching: `main` protected; feature branches per task; mandatory peer review

### 6. Open Questions

- [ ] Which CLIP variant is best suited for satellite imagery without a download budget? → Resolved: implement offline ResNet-18 visual backbone with pre-calibrated semantic anchors.
- [ ] Qdrant vs FAISS vs ChromaDB? → Resolved: Qdrant (ADR-003).
