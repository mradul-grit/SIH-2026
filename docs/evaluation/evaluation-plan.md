# Evaluation Plan

## Retrieval
Evaluate on held-out semantic queries and relevance judgements.

Track:
- Recall@K
- Precision@K
- MRR / ranking metric as appropriate
- Query latency
- Index size
- Build time

## Change Analysis
Evaluate on held-out labelled change/no-change cases.

Track:
- Precision
- Recall
- F1
- False-alarm rate
- Earliest supported observation accuracy where applicable

## System Benchmark
Record:
- Hardware
- Indexed area
- Number of scenes
- Number of tiles
- Index build time
- Storage footprint
- Median/p95 query latency
- Offline execution status

No metric should be claimed without a reproducible test.
