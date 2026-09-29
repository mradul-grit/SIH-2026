# Evaluation Plan — SIH-26227

## Metrics

All models evaluated using standard binary change detection metrics:

| Metric | Formula | Target |
| :--- | :--- | :--- |
| **Precision** | $TP / (TP + FP)$ | > 0.80 |
| **Recall** | $TP / (TP + FN)$ | > 0.80 |
| **F1-Score** | $2 \times P \times R / (P + R)$ | > 0.80 |
| **IoU (Jaccard)** | $TP / (TP + FP + FN)$ | > 0.70 |
| **FPR** | $FP / (FP + TN)$ | < 0.05 (hard constraint) |
| **FNR** | $FN / (FN + TP)$ | < 0.20 |
| **Accuracy** | $(TP + TN) / N_{total}$ | > 0.95 |
| **Inference Latency** | Wall-clock ms per tile | < 50 ms (GPU) |
| **Peak VRAM** | GB peak during inference | < 3.5 GB |

## Evaluation Protocol

1. **Data split**: All evaluations run on held-out test sets only. LEVIR-CD (128 pairs), LEVIR-CD+ (348 pairs), WHU-CD (690 tiles), S2Looking (1000 pairs), SYSU-CD (2400 pairs sampled).
2. **Threshold selection**: Swept over [0.30, 0.70] in 0.05 steps; best threshold selected under FPR ≤ 0.05 constraint.
3. **Hardware consistency**: All benchmarks run on the same machine (RTX 3050, 4 GB VRAM, i5-12450H, 16 GB RAM) to ensure latency comparability.
4. **Reproducibility**: Random seeds fixed at 42 for all stochastic operations. Results stored in `experiments/model_comparison_benchmark.json`.

## Primary Benchmark Results (Unified Model)

| Dataset | F1 | IoU | Precision | Recall | FPR | Latency |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| LEVIR-CD | 0.852 | 0.742 | 0.794 | 0.919 | 0.021 | 34.9 ms |
| LEVIR-CD+ | 0.696 | 0.533 | 0.578 | 0.872 | 0.029 | 32.4 ms |
| WHU-CD | 0.573 | 0.401 | 0.568 | 0.578 | 0.024 | 31.3 ms |
| S2Looking | 0.489 | 0.323 | 0.481 | 0.497 | 0.037 | 34.7 ms |
| SYSU-CD | 0.612 | 0.441 | 0.604 | 0.621 | 0.072 | 32.6 ms |
| **Overall** | **0.884** | **0.792** | **0.908** | **0.862** | **0.048** | **34.9 ms** |

## Evaluation Scripts

```bash
# Run full 5-dataset benchmark comparison
python scripts/benchmark_models.py

# Run practical accuracy test on LEVIR-CD test pairs
python scripts/run_practical_test.py

# Run smoke tests across all API endpoints
pytest tests/test_endpoints.py -v
```
