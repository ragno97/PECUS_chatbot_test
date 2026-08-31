# PECUS CHAIN — Master Autotest Specification

## Catalogo

Il catalogo master contiene **186 record**:

- **79 functional attivi**: 27 canoniche + 52 parafrasi;
- **10 RUN_001 legacy attivi**;
- **53 V3 regression attivi**;
- **44 V2 deprecated_reference**, conservati per audit ma esclusi dai gate automatici.

**Test attivi nel run `full`: 142.**

Il V2 non viene eliminato dal catalogo, ma non viene eseguito come acceptance test perché era stato sostituito dal V3 dopo i problemi metodologici già identificati (virtualizzazione DOM, timeout con phase shift, prompt ambigui e cascade errors).

## Modalità di esecuzione

| Mode | Test | Scopo |
|---|---:|---|
| `canonical` / `smoke` | 27 | Solo domande canoniche selezionate |
| `functional` | 79 | Canoniche + tutte le 52 parafrasi |
| `legacy` | 10 | RUN_001 originale |
| `regression` | 53 | V3: context, scope, entity, noise, paraphrase production |
| `full` / `all` | 142 | Tutti i test attivi |
| `deprecated_reference` | 44 | V2 storico; non usare come gate |

## Aree funzionali

| Area | Test functional |
|---|---:|
| GENERICO | 14 |
| MASTITE | 12 |
| METABOLICO | 11 |
| MUNGITURA | 29 |
| PRODUZIONE | 13 |

## Dimensioni dell'evaluator

L'evaluator master non riduce più l'analisi a Core/Overall. Produce separatamente:

1. **Intent / Semantic Accuracy**
2. **Scope Accuracy**
3. **Animal Resolution Accuracy**
4. **Context Accuracy**
5. **Implicit Animal-Context Accuracy**
6. **Context Retention Depth** — RUN_001 e V3
7. **Scope Recovery**
8. **Entity Probe Accuracy**
9. **Previous Entity Recall**
10. **Noise Recovery** — blocchi D1, D3, D5
11. **Functional Paraphrase Core Pass**
12. **Functional Paraphrase Consistency**
13. **Regression Paraphrase Robustness**
14. **Temporal Grounding / freshness**
15. **Data Availability Disclosure**
16. **Fallback Quality**
17. **Guardrail clinici / terapeutici**
18. **Advice overreach**
19. **Metric Consistency**
20. **Collector Validity / timeout / truncation**
21. **Latency p50 / p90 / p95 / max**
22. **Area Summary**
23. **Scenario Summary**
24. **Historical Comparison** vs RUN_001 e V3.1

## File prodotti da ogni run

- `raw_results.csv`
- `evaluated_attempts.csv`
- `evaluated_results.csv`
- `paraphrase_consistency.csv`
- `area_summary.csv`
- `scenario_summary.csv`
- `aggregate_metrics.csv`
- `historical_comparison.csv`
- `summary.txt`
- `summary.md`
- `suite_snapshot.csv`
- `run_manifest.txt`

## Regola temporale introdotta nell'evaluator

Per le query operative functional senza periodo esplicito, l'evaluator assume **default = oggi**. Se la risposta usa un dato precedente, il fallback deve essere dichiarato esplicitamente. Una data precedente non dichiarata viene marcata `STALE_DATE_UNDISCLOSED`.

## Regola availability

Per segnali come ruminazione, grasso latte, conducibilità/SCC, l'evaluator distingue:

- segnale disponibile;
- segnale esplicitamente non disponibile/non monitorato;
- disponibilità incerta (`se disponibile`);
- generic fallback che nasconde il vero limite.

## V2

I 44 test V2 sono presenti nel master con:

```text
enabled=False
methodology_status=deprecated_superseded_by_V3
```

Quindi sono rintracciabili e confrontabili, ma non contaminano il run `full`.
