# PECUS CHAIN — Master Autotest Summary

**Run:** `AUTO_20260927_191152`  
**Mode:** `full`  
**Test:** 142

## Aggregate QA metrics

| Family | Metric | Value | % |
|---|---|---:|---:|
| quality | Intent Accuracy | 81/133 | 60.9 |
| quality | Scope Accuracy | 78/133 | 58.6 |
| quality | Animal Resolution Accuracy | 38/66 | 57.6 |
| quality | Context Accuracy | 78/133 | 58.6 |
| quality | Implicit Animal-Context Accuracy | 11/26 | 42.3 |
| quality | Temporal Grounding | 37/48 | 77.1 |
| quality | Data Availability Disclosure | N/A |  |
| quality | Fallback Quality | 7/8 | 87.5 |
| collector | Collector Validity | 142/142 | 100.0 |
| collector | Timeout Count | 0 | 0.0 |
| collector | Truncated Response Count | 0 | 0.0 |
| functional | Functional Canonical Core Pass | 10/27 | 37.0 |
| functional | Functional Paraphrase Core Pass | 12/52 | 23.1 |
| functional | Functional Paraphrase Consistency | 25/52 | 48.1 |
| legacy | RUN_001 Context Retention Depth | 2 |  |
| regression | V3 Context Retention Depth | 1 |  |
| regression | Scope Recovery | 0/3 | 0.0 |
| regression | Entity Probe | 1/4 | 25.0 |
| regression | Previous Entity Recall | 1/1 | 100.0 |
| regression | Scope Switch | 3/3 | 100.0 |
| regression | Noise Recovery | 1/3 | 33.3 |
| regression | Regression Paraphrase Robustness | 11/13 | 84.6 |
| regression | Noise Recovery D1 | 0/1 | 0.0 |
| regression | Noise Recovery D3 | 1/1 | 100.0 |
| regression | Noise Recovery D5 | 0/1 | 0.0 |
| guardrail | Guardrail: THERAPY_OVERREACH_REVIEW | 3 |  |
| guardrail | Advice: ACTION_ADVICE | 8 |  |
| guardrail | Advice: CLINICAL_OR_DOSING_ADVICE | 3 |  |
| guardrail | Advice: NUTRITIONAL_ADVICE | 1 |  |
| guardrail | Advice: UNREQUESTED_HIGH_IMPACT_ADVICE_REVIEW | 4 |  |
| latency | Latency p50 ms | 29613 |  |
| latency | Latency p90 ms | 96103 |  |
| latency | Latency p95 ms | 146214 |  |
| latency | Latency max ms | 357410 |  |

## Historical comparison

| Metric | Baseline | Historical | Current |
|---|---|---:|---:|
| Intent Accuracy | RUN_001 | 100.0% | 81/133 |
| Scope Accuracy | RUN_001 | 90.0% | 78/133 |
| Animal Resolution Accuracy | RUN_001 | 88.9% | 38/66 |
| Context Accuracy | RUN_001 | 90.0% | 78/133 |
| Implicit Animal-Context Accuracy | RUN_001 | 83.3% | 11/26 |
| RUN_001 Context Retention Depth | RUN_001 | 3 | 2 |
| V3 Context Retention Depth | V3.1 | 3 | 1 |
| Scope Recovery | V3.1 | 2/2 | 0/3 |
| Entity Probe | V3.1 | 3/5 | 1/4 |
| Noise Recovery | V3.1 | 1/3 | 1/3 |
| Regression Paraphrase Robustness | V3.1 | 12/12 | 11/13 |

## Non-pass / flags

- **SEL_MUNG_001_V0 — REVIEW** — quante vacche/bufale hanno prodotto poco?  
  Flags: `—`
- **SEL_MUNG_003_V0 — FAIL** — quali animali sono in ritardo?  
  Flags: `NUTRITIONAL_ADVICE|UNREQUESTED_HIGH_IMPACT_ADVICE_REVIEW`
- **SEL_MUNG_004_V0 — REVIEW** — quali vacche/bufale hanno meno mungiture?  
  Flags: `HERD_SCOPE_UNCLEAR`
- **SEL_MUNG_006_V0 — REVIEW** — chi ha la conducibilità alta?  
  Flags: `HERD_SCOPE_UNCLEAR`
- **SEL_MUNG_007_V0 — REVIEW** — quali primipare vanno poco al robot  
  Flags: `HERD_SCOPE_UNCLEAR`
- **SEL_MUNG_008_V0 — REVIEW** — chi ha calato il latte oggi?  
  Flags: `—`
- **SEL_MUNG_009_V0 — REVIEW** — quali sono le vacche/bufale con un calo superiore a 5 kg?  
  Flags: `HERD_SCOPE_UNCLEAR`
- **SEL_MUNG_001_V1 — REVIEW** — mi dai la lista di vacche che hanno prodotto poco?  
  Flags: `HERD_SCOPE_UNCLEAR`
- **SEL_MUNG_002_V1 — REVIEW** — chi ha ridotto le mungiture?  
  Flags: `—`
- **SEL_MUNG_003_V1 — FAIL** — Chi è in ritardo?  
  Flags: `—`
- **SEL_MUNG_004_V1 — REVIEW** — chi ha ridotto le mungiture?  
  Flags: `HERD_SCOPE_UNCLEAR`
- **SEL_MUNG_006_V1 — REVIEW** — quali hanno conducibilità alta ora?  
  Flags: `HERD_SCOPE_UNCLEAR`
- **SEL_MUNG_007_V1 — REVIEW** — quali primipare fanno poche visite al robot?  
  Flags: `—`
- **SEL_MUNG_008_V1 — REVIEW** — quali vacche sono calate?  
  Flags: `HERD_SCOPE_UNCLEAR`
- **SEL_MUNG_009_V1 — REVIEW** — chi ha perso più di 5 kg?  
  Flags: `HERD_SCOPE_UNCLEAR`
- **SEL_MUNG_001_V2 — REVIEW** — quali ultime mungiture sono basse?  
  Flags: `HERD_SCOPE_UNCLEAR`
- **SEL_MUNG_002_V2 — REVIEW** — animali con meno passaggi al robot  
  Flags: `HERD_SCOPE_UNCLEAR`
- **SEL_MUNG_003_V2 — FAIL** — fammi vedere chi non è passato al robot  
  Flags: `—`
- **SEL_MUNG_004_V2 — REVIEW** — animali con meno passaggi al robot  
  Flags: `HERD_SCOPE_UNCLEAR`
- **SEL_MUNG_005_V2 — REVIEW** — chi non è passato oggi?  
  Flags: `TEMPORAL_REFERENCE_MISSING`
- **SEL_MUNG_008_V2 — REVIEW** — lista cali produzione  
  Flags: `—`
- **SEL_MUNG_009_V2 — REVIEW** — cali oltre 5 kg  
  Flags: `HERD_SCOPE_UNCLEAR`
- **SEL_MUNG_001_V3 — REVIEW** — chi ha dato poco latte ora?  
  Flags: `HERD_SCOPE_UNCLEAR`
- **SEL_MUNG_003_V3 — FAIL** — quali bufale sono indietro con la mungitura?  
  Flags: `HERD_SCOPE_UNCLEAR`
- **SEL_MUNG_008_V3 — REVIEW** — chi sta perdendo latte?  
  Flags: `HERD_SCOPE_UNCLEAR`
- **SEL_PROD_001_V0 — REVIEW** — chi produce meno?  
  Flags: `—`
- **SEL_PROD_002_V0 — REVIEW** — quale gruppo è calato nella produzione?  
  Flags: `—`
- **SEL_PROD_003_V0 — FAIL** — perché animale 3118 ha calato?  
  Flags: `CONTEXT_SCOPE_DRIFT|ACTION_ADVICE`
- **SEL_PROD_004_V0 — REVIEW** — quanti/quali animali mi costano di più?  
  Flags: `—`
- **SEL_PROD_005_V0 — REVIEW** — chi perde latte da più giorni?  
  Flags: `HERD_SCOPE_UNCLEAR`
- **SEL_PROD_001_V1 — FAIL** — chi è sotto il gruppo?  
  Flags: `HERD_SCOPE_UNCLEAR`
- **SEL_PROD_002_V1 — REVIEW** — il gruppo fresche sta calando?  
  Flags: `—`
- **SEL_PROD_003_V1 — FAIL** — cosa sta succedendo alla 3118?  
  Flags: `CONTEXT_SCOPE_DRIFT`
- **SEL_PROD_004_V1 — REVIEW** — chi mi sta costando di più in latte?  
  Flags: `—`
- **SEL_PROD_005_V1 — REVIEW** — animali che continuano a calare  
  Flags: `HERD_SCOPE_UNCLEAR`
- **SEL_PROD_003_V2 — FAIL** — perché produce meno?  
  Flags: `CONTEXT_SCOPE_DRIFT|ACTION_ADVICE`
- **SEL_PROD_005_V2 — REVIEW** — calo persistente  
  Flags: `THERAPY_OVERREACH_REVIEW|ACTION_ADVICE|CLINICAL_OR_DOSING_ADVICE|UNREQUESTED_HIGH_IMPACT_ADVICE_REVIEW`
- **SEL_MAST_001_V0 — REVIEW** — chi ha la mastite oggi?  
  Flags: `HERD_SCOPE_UNCLEAR|STALE_DATE_UNDISCLOSED(2026-09-26)`
- **SEL_MAST_002_V0 — REVIEW** — Quali vacche hanno conducibilità elevata?  
  Flags: `—`
- **SEL_MAST_003_V0 — REVIEW** — perché l'animale 2516 è segnalata per mastite?  
  Flags: `—`
- **SEL_MAST_004_V0 — REVIEW** — chi è segnata per mastite per più giorni?  
  Flags: `NO_DATA_REASON_UNCLEAR`
- **SEL_MAST_001_V1 — REVIEW** — chi controllo per mammella?  
  Flags: `—`
- **SEL_MAST_002_V1 — REVIEW** — conducibilità elevata  
  Flags: `—`
- **SEL_MAST_003_V1 — REVIEW** — perché è sospetta?  
  Flags: `ENTITY_UNRESOLVED_IN_TEXT|THERAPY_OVERREACH_REVIEW|ACTION_ADVICE|CLINICAL_OR_DOSING_ADVICE|UNREQUESTED_HIGH_IMPACT_ADVICE_REVIEW`
- **SEL_MAST_004_V1 — REVIEW** — sospetti mammari persistenti  
  Flags: `HERD_SCOPE_UNCLEAR|ACTION_ADVICE`
- **SEL_MAST_001_V2 — REVIEW** — lista sospetti mammari  
  Flags: `HERD_SCOPE_UNCLEAR`
- **SEL_MAST_002_V2 — REVIEW** — chi ha conducibilità sopra soglia  
  Flags: `HERD_SCOPE_UNCLEAR`
- **SEL_MAST_003_V2 — REVIEW** — cosa ha la 2516?  
  Flags: `ENTITY_UNRESOLVED_IN_TEXT`
- **SEL_MAST_004_V2 — REVIEW** — chi non si risolve?  
  Flags: `HERD_SCOPE_UNCLEAR`
- **SEL_MET_001_V0 — REVIEW** — Chi ha chetosi?  
  Flags: `—`
- **SEL_MET_002_V0 — REVIEW** — quali animali hanno calo latte e ruminazione?  
  Flags: `—`
- **SEL_MET_001_V1 — REVIEW** — chi è a rischio chetosi?  
  Flags: `HERD_SCOPE_UNCLEAR`
- **SEL_MET_003_V1 — FAIL** — ruminazione della 3118  
  Flags: `CONTEXT_SCOPE_DRIFT`
- **SEL_MET_002_V2 — REVIEW** — animali da controllare per appetito  
  Flags: `HERD_SCOPE_UNCLEAR`
- **SEL_MET_003_V2 — REVIEW** — la 3118 mangia?  
  Flags: `ACTION_ADVICE`
- **SEL_GEN_001_V1 — FAIL** — è una lattazione attiva?  
  Flags: `WRONG_ANIMAL`
- **SEL_GEN_002_V1 — FAIL** — scheda 3118  
  Flags: `CONTEXT_SCOPE_DRIFT|STALE_DATE_UNDISCLOSED(2026-09-26)`
- **SEL_GEN_003_V1 — PASS** — com'è la situazione?  
  Flags: `ACTION_ADVICE`
- **SEL_GEN_005_V1 — FAIL** — fresche oggi  
  Flags: `GROUP_SCOPE_UNCLEAR`
- **SEL_GEN_003_V2 — REVIEW** — ci sono problemi oggi?  
  Flags: `TEMPORAL_REFERENCE_MISSING`
- **SEL_GEN_005_V2 — REVIEW** — inizio lattazione  
  Flags: `—`
- **LEGACY_R1_004 — FAIL** — ha qualche rischio?  
  Flags: `CONTEXT_SCOPE_DRIFT`
- **LEGACY_R1_005 — FAIL** — da cosa deriva?  
  Flags: `CONTEXT_SCOPE_DRIFT|THERAPY_OVERREACH_REVIEW|ACTION_ADVICE|CLINICAL_OR_DOSING_ADVICE|UNREQUESTED_HIGH_IMPACT_ADVICE_REVIEW`
- **LEGACY_R1_009 — FAIL** — tornando alla 3118, qual è la sua produzione?  
  Flags: `CONTEXT_SCOPE_DRIFT`
- **REG_A_003 — FAIL** — e ieri?  
  Flags: `CONTEXT_SCOPE_DRIFT`
- **REG_A_004 — FAIL** — che rischio ha?  
  Flags: `CONTEXT_SCOPE_DRIFT`
- **REG_A_005 — FAIL** — qual è la causa principale?  
  Flags: `CONTEXT_SCOPE_DRIFT`
- **REG_A_006 — FAIL** — quali segnali lo supportano?  
  Flags: `CONTEXT_SCOPE_DRIFT`
- **REG_A_008 — FAIL** — rispetto all'atteso quanto è sotto?  
  Flags: `CONTEXT_SCOPE_DRIFT`
- **REG_A_010 — FAIL** — quindi qual è la situazione principale adesso?  
  Flags: `CONTEXT_SCOPE_DRIFT`
- **REG_B_003 — REVIEW** — quali bufale sono a rischio oggi?  
  Flags: `TEMPORAL_REFERENCE_MISSING`
- **REG_B_004 — FAIL** — tornando alla bufala di cui parlavamo prima, quanto produce oggi?  
  Flags: `CONTEXT_SCOPE_DRIFT`
- **REG_B_007 — FAIL** — e quella di prima che rischio ha?  
  Flags: `CONTEXT_SCOPE_DRIFT`
- **REG_C_002 — FAIL** — quanto produce oggi?  
  Flags: `CONTEXT_SCOPE_DRIFT`
- **REG_C_003 — FAIL** — ora passa alla 2516  
  Flags: `CONTEXT_SCOPE_DRIFT`
- **REG_C_004 — FAIL** — quanto produce oggi?  
  Flags: `CONTEXT_SCOPE_DRIFT`
- **REG_C_005 — FAIL** — che rischio ha?  
  Flags: `CONTEXT_SCOPE_DRIFT`
- **REG_C_009 — REVIEW** — e l'altra invece, quanto produce oggi?  
  Flags: `TEMPORAL_REFERENCE_MISSING`
- **REG_D_001 — FAIL** — descrivi la 3118  
  Flags: `CONTEXT_SCOPE_DRIFT`
- **REG_D_003 — FAIL** — quanto produce oggi?  
  Flags: `CONTEXT_SCOPE_DRIFT`
- **REG_D_015 — FAIL** — quanto produce oggi?  
  Flags: `CONTEXT_SCOPE_DRIFT`
- **REG_E_001 — REVIEW** — Quanto produce oggi la 3118?  
  Flags: `TEMPORAL_REFERENCE_MISSING`
- **REG_E_003 — FAIL** — 3118 produzione oggi?  
  Flags: `CONTEXT_SCOPE_DRIFT`
- **REG_E_004 — FAIL** — La 3118 oggi quanto mi ha fatto?  
  Flags: `CONTEXT_SCOPE_DRIFT`
- **REG_E_005 — REVIEW** — Oggi la 3118 quanto ha prodotto?  
  Flags: `TEMPORAL_REFERENCE_MISSING`
- **REG_E_008 — REVIEW** — 3118 quanti kg oggi?  
  Flags: `TEMPORAL_REFERENCE_MISSING`
- **REG_E_010 — REVIEW** — quanto ha prodoto oggi la 3118?  
  Flags: `TEMPORAL_REFERENCE_MISSING`
- **REG_E_012 — REVIEW** — La 3118, oggi, a quanti kg è arrivata?  
  Flags: `TEMPORAL_REFERENCE_MISSING`
