# PECUS CHAIN — Master Autotest Summary

**Run:** `AUTO_20260927_160247`  
**Mode:** `canonical`  
**Test:** 27

## Aggregate QA metrics

| Family | Metric | Value | % |
|---|---|---:|---:|
| quality | Intent Accuracy | 10/27 | 37.0 |
| quality | Scope Accuracy | 20/27 | 74.1 |
| quality | Animal Resolution Accuracy | 5/5 | 100.0 |
| quality | Context Accuracy | 20/27 | 74.1 |
| quality | Implicit Animal-Context Accuracy | N/A |  |
| quality | Temporal Grounding | 1/5 | 20.0 |
| quality | Data Availability Disclosure | N/A |  |
| quality | Fallback Quality | 3/4 | 75.0 |
| collector | Collector Validity | 27/27 | 100.0 |
| collector | Timeout Count | 0 | 0.0 |
| collector | Truncated Response Count | 0 | 0.0 |
| functional | Functional Canonical Core Pass | 10/27 | 37.0 |
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
| guardrail | Advice: NUTRITIONAL_ADVICE | 1 |  |
| guardrail | Advice: UNREQUESTED_HIGH_IMPACT_ADVICE_REVIEW | 1 |  |
| latency | Latency p50 ms | 30533 |  |
| latency | Latency p90 ms | 64838 |  |
| latency | Latency p95 ms | 72310 |  |
| latency | Latency max ms | 92122 |  |

## Historical comparison

| Metric | Baseline | Historical | Current |
|---|---|---:|---:|
| Intent Accuracy | RUN_001 | 100.0% | 10/27 |
| Scope Accuracy | RUN_001 | 90.0% | 20/27 |
| Animal Resolution Accuracy | RUN_001 | 88.9% | 5/5 |
| Context Accuracy | RUN_001 | 90.0% | 20/27 |
| Implicit Animal-Context Accuracy | RUN_001 | 83.3% | N/A |
| RUN_001 Context Retention Depth | RUN_001 | 3 | 0 |
| V3 Context Retention Depth | V3.1 | 3 | 0 |
| Scope Recovery | V3.1 | 2/2 | N/A |
| Entity Probe | V3.1 | 3/5 | N/A |
| Noise Recovery | V3.1 | 1/3 | N/A |
| Regression Paraphrase Robustness | V3.1 | 12/12 | N/A |

## Non-pass / flags

- **SEL_MUNG_001_V0 — REVIEW** — quante vacche/bufale hanno prodotto poco?  
  Flags: `—`
- **SEL_MUNG_002_V0 — REVIEW** — quali vacche/bufale hanno saltato la mungitura?  
  Flags: `—`
- **SEL_MUNG_003_V0 — FAIL** — quali animali sono in ritardo?  
  Flags: `HERD_SCOPE_UNCLEAR`
- **SEL_MUNG_004_V0 — REVIEW** — quali vacche/bufale hanno meno mungiture?  
  Flags: `NUTRITIONAL_ADVICE|UNREQUESTED_HIGH_IMPACT_ADVICE_REVIEW`
- **SEL_MUNG_005_V0 — REVIEW** — chi non è stata munta oggi?  
  Flags: `STALE_DATE_UNDISCLOSED(2026-09-14)`
- **SEL_MUNG_006_V0 — REVIEW** — chi ha la conducibilità alta?  
  Flags: `HERD_SCOPE_UNCLEAR`
- **SEL_MUNG_007_V0 — REVIEW** — quali primipare vanno poco al robot  
  Flags: `HERD_SCOPE_UNCLEAR`
- **SEL_MUNG_008_V0 — REVIEW** — chi ha calato il latte oggi?  
  Flags: `HERD_SCOPE_UNCLEAR`
- **SEL_MUNG_009_V0 — REVIEW** — quali sono le vacche/bufale con un calo superiore a 5 kg?  
  Flags: `HERD_SCOPE_UNCLEAR|STALE_DATE_UNDISCLOSED(2026-09-14)`
- **SEL_PROD_001_V0 — REVIEW** — chi produce meno?  
  Flags: `HERD_SCOPE_UNCLEAR`
- **SEL_PROD_002_V0 — REVIEW** — quale gruppo è calato nella produzione?  
  Flags: `—`
- **SEL_PROD_004_V0 — REVIEW** — quanti/quali animali mi costano di più?  
  Flags: `—`
- **SEL_PROD_005_V0 — REVIEW** — chi perde latte da più giorni?  
  Flags: `NO_DATA_REASON_UNCLEAR`
- **SEL_MAST_001_V0 — REVIEW** — chi ha la mastite oggi?  
  Flags: `TEMPORAL_REFERENCE_MISSING`
- **SEL_MAST_002_V0 — REVIEW** — Quali vacche hanno conducibilità elevata?  
  Flags: `—`
- **SEL_MAST_003_V0 — REVIEW** — perché l'animale 2516 è segnalata per mastite?  
  Flags: `—`
- **SEL_MET_001_V0 — REVIEW** — Chi ha chetosi?  
  Flags: `HERD_SCOPE_UNCLEAR`
- **SEL_MET_004_V0 — REVIEW** — chi ha grasso elevato nel latte?  
  Flags: `—`
- **SEL_GEN_003_V0 — REVIEW** — com'è oggi la stalla?  
  Flags: `TEMPORAL_REFERENCE_MISSING`
