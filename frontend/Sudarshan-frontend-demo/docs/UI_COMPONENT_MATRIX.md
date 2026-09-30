# Sudarshan UI Component Matrix

This matrix is the implementation checklist behind the four reference screens.

| Component | Required behavior | Demo state | Future integration point |
|---|---|---|---|
| Trust Header | Product, organisation, offline, archive, analyst state | Local demo | Runtime/system health service |
| Sidebar | Navigate all analyst workflows | Fully clickable | Router |
| Workflow Stepper | Show data-to-review pipeline | 5 steps | Pipeline status API |
| Natural Language Query | Accept free text | Two fixed demo queries + editable input | Semantic retrieval service |
| Image Search | Upload/select image | Local demo selector | Image embedding service |
| Polygon Search | AOI-based search | Demo AOI polygon | Geospatial query service |
| Advanced Filters | Date, sensor, cloud/quality, region, resolution | Local filter state | Metadata index |
| Ranked Results | Score + evidence + metadata | Deterministic fixtures | Retrieval API |
| Map View | AOI, sites, candidate changes, legend | Local deterministic map | GIS/map renderer |
| Site Header | Site ID, type, confidence, location | SITE-A | Site detail API |
| Before/After | Compare two observations | Local image pair | Temporal imagery service |
| Change Mask | Highlight changed footprint | Demo evidence | Change detection service |
| Temporal Evidence | Timeline and earliest supported change | Local sequence | Change analysis service |
| Why this result | Explain confidence factors | Evidence fixture | Model explanation output |
| Quality / False Alarm | Factor-by-factor suppression evidence | SITE-C / SITE-D cases | Quality pipeline |
| Similar Sites | Ranked similarity | Local feature records | Vector/embedding search |
| Clustering | Visual/semantic grouping | Local cluster fixture | Clustering service |
| Review Queue | Confirm/reject/needs-review | Local state + audit event | Review API/audit store |
| Data Ingestion | Stage GeoTIFF/COG and metadata | Simulated local upload | Ingestion service |
| Incremental Update | Add new data without full rebuild | Demo progress state | Indexing service |
| Data Catalog | Assets + provenance | 30-38 demo assets | STAC/catalog service |
| Analytics | Retrieval/change/system metrics | Fixture-aware | Evaluation service |
| System Status | Network/model/index/archive status | Offline + local | Runtime diagnostics |
| Provenance | Source, process, model, index, decision | Local manifest | Provenance service |
| Export | Evidence package | Local report simulation | Export/report service |
| Settings | Demo configuration and display controls | Local state | Config service |
