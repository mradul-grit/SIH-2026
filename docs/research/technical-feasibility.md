# Technical Feasibility

## Questions
- Can the full demo run offline?
- What hardware is required?
- How large will the vector index become?
- What is expected query latency?
- Can new scenes be indexed incrementally?
- Can all provenance be preserved?

## Risk Register

| Risk | Probability | Impact | Mitigation | Owner | Status |
|---|---|---|---|---|---|
| Model too large for hardware | Medium | High | Benchmark smaller candidates | M3 | Open |
| False positives from seasonality | High | High | Quality masks + temporal normalization | M4 | Open |
| Registration errors | Medium | High | Co-registration QA | M2/M4 | Open |
| Slow vector search | Medium | High | ANN index + tiling strategy | M3/M5 | Open |
| Data/licence issue | Medium | High | Maintain dataset register | M2 | Open |
