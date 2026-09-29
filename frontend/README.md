# GEOINT C2 Frontend: Analyst Tactical Dashboard (SIH-26227)

A mission-ready, air-gapped command and control interface built with **React 19** and **Vite**, engineered specifically for defense analysts inspecting satellite reconnaissance data.

---

## 1. System Capabilities & Tab Layout

The dashboard features 9 specialized operational workspaces accessible via rapid hotkeys `[1]` through `[9]`:

1. **Dashboard Overview (`[1]`)**: Operational readiness status, active hardware telemetry, benchmark dataset summary, and quick launcher.
2. **AI Tactical Assistant (`[2]`)**: 100% offline, air-gapped multimodal reasoning engine capable of answering tactical queries across uploaded bi-temporal imagery pairs.
3. **Change Detection Studio (`[3]`)**: Native-resolution sliding window change analysis with interactive threshold slider, model selector, false-alarm toggle, and polygon overlays.
4. **Semantic Natural Language Search (`[4]`)**: Natural language text retrieval over satellite scenes powered by RemoteCLIP embeddings and Rocchio relevance feedback (Active Learning).
5. **Multi-Temporal Sequence Studio (`[5]`)**: Historical progression timeline tracking ($T_1 \to T_n$) and $O(\log N)$ bisection search to pinpoint exact change appearance dates.
6. **Discovery & Unsupervised Clustering (`[6]`)**: UMAP + HDBSCAN 2D projection revealing uncataloged geographical change patterns without manual supervision.
7. **Analyst Review & Provenance Audit (`[7]`)**: Defense-grade audit verification queue with SHA-256 hash chaining on all Confirm/Reject actions and RFC 7946 GeoJSON export.
8. **Model Benchmark Lab (`[8]`)**: Head-to-head empirical metrics (Precision, Recall, F1, IoU, FPR, FNR, Latency, Peak VRAM) across all 5 benchmark datasets.
9. **Dataset Explorer (`[9]`)**: Comprehensive catalog viewer detailing LEVIR-CD, LEVIR-CD+, WHU-CD, S2Looking, and SYSU-CD specs.

---

## 2. Air-Gapped Offline Guarantee

* **Zero External CDNs**: All fonts, icons, styling tokens, and JavaScript libraries are bundled locally.
* **Security & Defense Compliance**: Does not phone home or transmit outbound HTTP/HTTPS packets outside the local network (`127.0.0.1` / `localhost`).

---

## 3. Running the Frontend

### Production Mode (Node Proxy):
```bash
cd frontend
node server.js
```
Serves the compiled production bundle on `http://localhost:3000` with automated proxying to the FastAPI backend on port 8000/8080.

### Development Mode (Vite HMR):
```bash
cd frontend
npm run dev
```
Runs the Vite development server with hot module replacement on `http://localhost:5173`.
