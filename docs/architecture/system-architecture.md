# System Architecture

## Components

1. Data ingestion
2. Geospatial preprocessing
3. Embedding generation
4. Vector/geospatial index
5. Semantic retrieval
6. Temporal change analysis
7. Quality/confidence layer
8. Backend API
9. Analyst frontend
10. Evaluation pipeline

## Integration Principle

Every component must define:
- Input
- Output
- Schema
- Owner
- Test

Do not integrate only at the end. A mock end-to-end pipeline must exist by Day 7.
