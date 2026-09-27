# PECUS CHAIN — Master Autotest Summary

**Run:** `AUTO_20260927_182339`  
**Mode:** `smoke`  
**Test:** 1

## Aggregate QA metrics

| Family | Metric | Value | % |
|---|---|---:|---:|
| quality | Intent Accuracy | N/A |  |
| quality | Scope Accuracy | N/A |  |
| quality | Animal Resolution Accuracy | N/A |  |
| quality | Context Accuracy | N/A |  |
| quality | Implicit Animal-Context Accuracy | N/A |  |
| quality | Temporal Grounding | N/A |  |
| quality | Data Availability Disclosure | N/A |  |
| quality | Fallback Quality | N/A |  |
| collector | Collector Validity | 0/1 | 0.0 |
| collector | Timeout Count | 1 | 100.0 |
| collector | Truncated Response Count | 0 | 0.0 |
| functional | Functional Canonical Core Pass | 0/1 | 0.0 |
| functional | Functional Paraphrase Core Pass | N/A |  |
| functional | Functional Paraphrase Consistency | N/A |  |
| legacy | RUN_001 Context Retention Depth | 0 |  |
| regression | V3 Context Retention Depth | 0 |  |
| regression | Scope Recovery | N/A |  |
| regression | Entity Probe | N/A |  |
| regression | Previous Entity Recall | N/A |  |
| regression | Scope Switch | N/A |  |
| regression | Noise Recovery | N/A |  |
| regression | Regression Paraphrase Robustness | N/A |  |

## Historical comparison

| Metric | Baseline | Historical | Current |
|---|---|---:|---:|
| Intent Accuracy | RUN_001 | 100.0% | N/A |
| Scope Accuracy | RUN_001 | 90.0% | N/A |
| Animal Resolution Accuracy | RUN_001 | 88.9% | N/A |
| Context Accuracy | RUN_001 | 90.0% | N/A |
| Implicit Animal-Context Accuracy | RUN_001 | 83.3% | N/A |
| RUN_001 Context Retention Depth | RUN_001 | 3 | 0 |
| V3 Context Retention Depth | V3.1 | 3 | 0 |
| Scope Recovery | V3.1 | 2/2 | N/A |
| Entity Probe | V3.1 | 3/5 | N/A |
| Noise Recovery | V3.1 | 1/3 | N/A |
| Regression Paraphrase Robustness | V3.1 | 12/12 | N/A |

## Non-pass / flags

- **SEL_MUNG_001_V0 — INVALID_COLLECTOR** — quante vacche/bufale hanno prodotto poco?  
  Flags: `COLLECTOR_FAILURE|EMPTY_RESPONSE`
