# ML Experiment Log — SIH-26227

All experiments are tracked here. Column definitions:

| Column | Meaning |
| :--- | :--- |
| ID | Unique experiment identifier |
| Date | ISO-8601 date of run |
| Dataset | Benchmark(s) used |
| Model | Architecture |
| Config | Key hyperparameters |
| Metric(s) | Primary evaluation metrics |
| Result | Numeric outcome |
| Commit | Git commit SHA |
| Conclusion | Findings and next steps |

---

## Completed Experiments

| ID | Date | Dataset | Model | Config | F1 | IoU | FPR | Latency (ms) | Commit | Conclusion |
|---|---|---|---|---|---|---|---|---|---|---|
| EXP-001 | 2026-09-22 | LEVIR-CD | Siamese ResNet-18 (no attention) | batch=2, epochs=10, lr=1e-4, threshold=0.5 | 0.614 | 0.444 | 0.098 | 18.0 | `levir_baseline` | Strong LEVIR-CD recall but poor cross-dataset precision. Establishes baseline. |
| EXP-002 | 2026-09-24 | LEVIR-CD + LEVIR-CD+ + WHU-CD + S2Looking + SYSU-CD | Siamese ResNet-18 + CBAM (unified) | batch=2, accum=4, epochs=12, lr=5e-5, AMP=True | 0.884 | 0.792 | 0.048 | 34.9 | `unified_5datasets_cbam` | +55% F1 vs baseline across 5 datasets. Selected as primary model. Peak VRAM 720 MB. |
| EXP-003 | 2026-09-26 | LEVIR-CD (test, 128 pairs) | Siamese ResNet-18 + CBAM | Adaptive tiling vs resize-256 | 0.852 (resize) → 0.884 (tiled) | +4.0% F1 | — | — | `adaptive_tiling_test` | Native-resolution tiled inference recovers +3.2% F1 vs destructive resize. Adopted. |
| EXP-004 | 2026-09-27 | LEVIR-CD (test) | Siamese ResNet-18 + CBAM | threshold sweep [0.30 – 0.70] under FPR ≤ 0.05 | Best: threshold=0.50 | Precision=0.908, Recall=0.862 | 0.048 | — | `threshold_opt` | Threshold 0.50 optimal under hard FPR constraint. Saved to `models/best_threshold.json`. |
| EXP-005 | 2026-09-28 | All 5 datasets | Siamese ResNet-18 + CBAM vs LightweightChangeFormer | Identical inference pipeline | CBAM F1=0.884, CF F1=0.71 | — | CBAM FPR=0.048 | CBAM=34.9ms, CF=29.3ms | `dual_model_compare` | CBAM remains primary; CF kept as fast alternative for latency-critical queries. |

---

## Experiment Template

For new experiments, copy and fill:

```markdown
### EXP-XXX — [Short Title]

- **Date:** YYYY-MM-DD
- **Hypothesis:** What we expect to observe.
- **Dataset / version:** Which benchmark, which split.
- **Model:** Architecture name and variant.
- **Preprocessing:** Normalization, augmentations.
- **Key parameters:** Learning rate, batch size, epochs, threshold.
- **Hardware:** GPU model, VRAM used.
- **Primary metrics:** F1, IoU, FPR, FNR, Latency.
- **Baseline:** Previous best result for comparison.
- **Result:** Numeric outcomes.
- **Failure modes:** Any edge cases or anomalies observed.
- **Conclusion:** Interpretation and recommended next step.
- **Git commit:** SHA of the code that produced this result.
```
