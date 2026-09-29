# Backend API Service (SIH-26227)

Production-grade, asynchronous REST API implementing Earth Observation change detection, multimodal semantic search, and provenance tracking.

---

## 1. Architecture Overview

The backend is built with **FastAPI** and **PyTorch**, structured to enforce sub-second latencies and strict air-gapped offline constraints.

* **Primary Neural Backbone**: Siamese U-Net + ResNet-18 with Convolutional Block Attention Modules (CBAM).
* **Secondary Candidate**: Lightweight ChangeFormer for transformer-based comparative benchmarking.
* **Vector Indexing Engine**: Qdrant Local Engine with 512-dimensional multimodal vision-language embeddings and 4-bit scalar quantization.
* **False-Alarm Mitigation**: 2D phase-correlation sub-pixel coregistration, radiometric cloud/shadow masking, VARI spectral vegetation filter, and morphological cleaning.
* **Multi-Temporal Modeling**: $O(\log N)$ bisection search algorithm to pinpoint earliest chronological appearance of ground changes.
* **Audit & Defense Provenance**: SHA-256 hash chaining on all analyst review events and RFC 7946 compliant GeoJSON export.

---

## 2. API Endpoints

| Method | Route | Description |
| :--- | :--- | :--- |
| `GET` | `/api/health` | System health, GPU availability, and active compute device |
| `GET` | `/api/datasets` | Registered benchmark dataset metadata and paths |
| `GET` | `/api/sample-pairs` | Curated benchmark test pairs for instant demonstration |
| `GET` | `/api/sample-pair/{id}` | High-resolution bi-temporal scene with ground-truth mask |
| `POST` | `/api/change-detect` | End-to-end change detection pipeline with false-alarm filtering |
| `POST` | `/api/chat-query` | 100% offline multimodal tactical chat analysis |
| `POST` | `/api/semantic-search` | Natural language text search over satellite tile index |
| `POST` | `/api/feedback` | Rocchio relevance feedback vector shift for active learning |
| `POST` | `/api/temporal-bisect` | $O(\log N)$ bisection search for change onset timestamp |
| `GET` | `/api/clusters` | UMAP + HDBSCAN discovery clustering for uncataloged sites |
| `POST` | `/api/review` | Analyst decision logging with cryptographic SHA-256 seal |
| `GET` | `/api/audit-logs` | Tamper-evident provenance history log (last 50 events) |
| `GET` | `/api/export-geojson/{id}` | RFC 7946 GeoJSON export with cryptographic audit hash |

---

## 3. Running the Backend

```bash
# Using uvicorn directly
python -m uvicorn backend.app:app --host 127.0.0.1 --port 8000

# Or using the python entrypoint
python backend/app.py
```

Interactive OpenAPI documentation is automatically served at:
* Swagger UI: `http://127.0.0.1:8000/docs`
* ReDoc: `http://127.0.0.1:8000/redoc`
