# PECUS CHAIN — Guida ai risultati dell'autotest

Questa guida descrive i file prodotti, gli status e l'ordine consigliato di analisi.

# 11. Output prodotti da ogni run

Ogni run crea:

```text
results\
└── AUTO_YYYYMMDD_HHMMSS\
    │
    ├── run_manifest.txt
    ├── suite_snapshot.csv
    ├── raw_results.csv
    │
    ├── evaluated_attempts.csv
    ├── evaluated_results.csv
    │
    ├── paraphrase_consistency.csv
    ├── area_summary.csv
    ├── scenario_summary.csv
    ├── aggregate_metrics.csv
    ├── historical_comparison.csv
    │
    ├── summary.txt
    └── summary.md
```

In caso di errore del locator WhatsApp possono essere prodotti anche:

```text
whatsapp_locator_failure.png
whatsapp_locator_failure.txt
```

---

# 12. Guida ai risultati

## 12.1 `run_manifest.txt`

### Contiene

- Run ID;
- modalità;
- data/ora;
- suite utilizzata;
- timeout;
- nome del contatto;
- versione dello schema.

### Usarlo per

Audit e riproducibilità.

---

## 12.2 `suite_snapshot.csv`

Copia esatta della suite usata per quel run.

### Perché è importante

Se `pecus_llm_suite.csv` viene modificato in futuro, il run rimane comunque ricostruibile.

> Per interpretare un vecchio run usare sempre il suo `suite_snapshot.csv`, non la suite corrente.

---

## 12.3 `raw_results.csv`

È il **registro grezzo**.

Contiene per ogni tentativo:

- test;
- domanda;
- risposta PECUS;
- timestamp;
- latency;
- message ID;
- metadata WhatsApp;
- collector status;
- attempt number.

### Usarlo per

- audit;
- revisione manuale;
- debugging;
- investigazione di timeout;
- verifica di ciò che PECUS ha realmente scritto.

### Regola

`raw_results.csv` non va modificato manualmente.

---

## 12.4 `evaluated_attempts.csv`

Ogni singolo tentativo viene valutato.

Se un test ha:

```text
attempt 1 = timeout
attempt 2 = success
```

qui sono visibili entrambi.

### Usarlo per

Analizzare stabilità e retry.

---

## 12.5 `evaluated_results.csv`

È il file principale **turno-per-turno**.

Contiene un record finale per `test_id`.

Se esistono più tentativi, utilizza l'ultimo tentativo valido per la valutazione finale, mantenendo comunque lo storico in `evaluated_attempts.csv`.

### Colonne principali

| Campo | Significato |
|---|---|
| `collector_status` | validità tecnica della raccolta |
| `intent_status` | correttezza dell'intent |
| `semantic_status` | correttezza del contenuto core |
| `scope_status` | animale/gruppo/mandria |
| `animal_status` | animale corretto |
| `context_status` | contesto corretto |
| `implicit_context_status` | contesto mantenuto senza ID esplicito |
| `temporal_status` | correttezza del riferimento temporale |
| `availability_status` | trasparenza sulla disponibilità del segnale |
| `fallback_status` | qualità del fallback |
| `guardrail_flags` | problemi clinici/terapeutici |
| `advice_flags` | tipi di raccomandazioni presenti |
| `metric_flags` | incoerenze numeriche |
| `quality_flags` | insieme dei flag qualitativi |
| `core_status` | qualità centrale della risposta |
| `overall_status` | valutazione complessiva |

---

# 13. Significato degli status

## PASS

La dimensione valutata soddisfa il criterio.

## REVIEW

Non esiste una contraddizione netta, ma il comportamento:

- è ambiguo;
- è incompleto;
- usa un fallback debole;
- non dichiara bene il limite;
- contiene advice da revisionare.

**REVIEW non significa automaticamente risposta sbagliata.**

## FAIL

Errore forte:

- intent errato;
- animale errato;
- scope errato;
- perdita del contesto;
- contraddizione incompatibile;
- guardrail grave.

## INVALID_COLLECTOR

Il test non può essere usato per giudicare PECUS perché la raccolta non è valida:

- timeout;
- risposta vuota;
- contaminazione;
- troncamento grave.

Va distinto da un FAIL del modello.

## N/A

La dimensione non è pertinente a quel test.

Esempio: `animal_status = N/A` per una domanda di mandria.

---

# 14. Core vs Overall

## `core_status`

Risponde alla domanda:

> “PECUS ha capito e risposto correttamente all'intento principale?”

## `overall_status`

Aggiunge qualità e sicurezza:

- temporal grounding;
- data availability;
- fallback;
- guardrail;
- incoerenze rilevanti.

### Esempio

```text
Domanda:
chi ha la conducibilità alta?
```

PECUS può identificare correttamente gli animali:

```text
core_status = PASS
```

ma poi proporre terapia antibiotica senza gating:

```text
overall_status = REVIEW
```

Quindi il problema non è la capability di recupero dati, ma il livello di raccomandazione.

---

# 15. `paraphrase_consistency.csv`

Confronta ogni parafrasi con la domanda canonica dello stesso `case_id`.

Monitora:

- classe di risposta;
- compatibilità degli animali restituiti;
- coerenza semantica.

### Usarlo per

Individuare casi in cui:

```text
"chi produce meno?"
```

funziona ma:

```text
"quali sono quelle che fanno meno latte?"
```

produce un comportamento diverso.

---

# 16. `area_summary.csv`

Aggrega i risultati per area funzionale:

- MUNGITURA;
- PRODUZIONE;
- MASTITE;
- METABOLICO;
- GENERICO;
- CONVERSAZIONE;
- REGRESSIONE.

### Usarlo per

Capire **dove** si concentrano i problemi.

Non sostituisce `evaluated_results.csv`: una buona media di area può nascondere un failure importante.

---

# 17. `scenario_summary.csv`

Aggrega per scenario conversazionale.

Esempi:

- `LEGACY_RUN001`;
- `A_CONTEXT_DECAY`;
- `B_SCOPE_RECOVERY`;
- `C_ENTITY_SWITCH`;
- `D_NOISE_RETENTION`;
- `E_PARAPHRASE_PRODUCTION`.

### Usarlo per

Valutare le capability di state management.

---

# 18. `aggregate_metrics.csv`

È il file principale per KPI quantitativi.

Include:

## Quality

- Intent Accuracy;
- Scope Accuracy;
- Animal Resolution Accuracy;
- Context Accuracy;
- Implicit Animal-Context Accuracy;
- Temporal Grounding;
- Data Availability Disclosure;
- Fallback Quality.

## Functional

- Functional Canonical Core Pass;
- Functional Paraphrase Core Pass;
- Functional Paraphrase Consistency.

## Conversational / Regression

- RUN_001 Context Retention Depth;
- V3 Context Retention Depth;
- Scope Recovery;
- Entity Probe;
- Previous Entity Recall;
- Scope Switch;
- Noise Recovery;
- Noise Recovery D1/D3/D5;
- Regression Paraphrase Robustness.

## Safety / quality flags

Conteggio di:

- guardrail;
- advice;
- metric consistency flags.

## Collector

- Collector Validity;
- Timeout Count;
- Truncated Response Count.

## Performance

- Latency p50;
- p90;
- p95;
- max.

### Usarlo per

- confronto tra release;
- dashboard QA;
- regression gate;
- report al team.

---

# 19. `historical_comparison.csv`

Confronta automaticamente il run corrente con baseline storiche comparabili.

## Baseline RUN_001

- Intent Accuracy: 100%;
- Scope Accuracy: 90%;
- Animal Resolution: 88,9%;
- Context Accuracy: 90%;
- Implicit Context: 83,3%;
- Retention Depth: 3.

## Baseline V3.1

- Context Retention Depth: 3;
- Scope Recovery: 2/2;
- Entity Probe: 3/5;
- Noise Recovery: 1/3;
- Regression Paraphrase Robustness: 12/12.

### Usarlo per

Rispondere alla domanda:

> “La nuova versione PECUS è migliorata o ha introdotto regressioni?”

### Attenzione

Confrontare solo metriche metodologicamente compatibili.

---

# 20. `summary.txt`

Sintesi leggibile rapidamente da terminale.

Contiene:

- KPI;
- area summary;
- scenario summary;
- non-PASS;
- principali flag.

### Usarlo per

Controllo operativo veloce.

---

# 21. `summary.md`

Report Markdown generato automaticamente.

### Usarlo per

- condivisione con sviluppatori;
- documentazione;
- issue tracking;
- review di prodotto;
- allegato a release note.

Per un'analisi dettagliata, usare comunque anche:

```text
evaluated_results.csv
aggregate_metrics.csv
historical_comparison.csv
```

---

# 22. Ordine consigliato di lettura dei risultati

Per una review completa:

```text
1. summary.md
       ↓
2. aggregate_metrics.csv
       ↓
3. historical_comparison.csv
       ↓
4. area_summary.csv
       ↓
5. scenario_summary.csv
       ↓
6. evaluated_results.csv
       ↓
7. raw_results.csv
```

## Se emerge un FAIL

Seguire:

```text
aggregate / summary
        ↓
evaluated_results.csv
        ↓
evaluated_attempts.csv
        ↓
raw_results.csv
        ↓
suite_snapshot.csv
```

Questo permette di distinguere:

- problema reale PECUS;
- limite dell'evaluator;
- problema del collector;
- aspettativa errata del test.

---

# 23. Regole per interpretare correttamente i KPI

## Non usare solamente Overall PASS Rate

Un singolo numero può nascondere failure molto diversi.

Valutare separatamente almeno:

```text
Intent
Scope
Animal
Context
Temporal
Availability
Fallback
Guardrail
Collector
Latency
```

## Un REVIEW non equivale a un FAIL

Può significare:

- risposta core corretta ma troppo prescrittiva;
- dato non dichiarato chiaramente;
- temporal fallback ambiguo.

## Un INVALID_COLLECTOR non è un errore semantico

Va prima risolto il problema di raccolta.

## Una query corretta non certifica il ground truth

L'autotest attuale verifica principalmente:

- comportamento;
- semantica;
- consistenza;
- contesto;
- qualità della risposta.

Non certifica automaticamente che ogni valore numerico coincida con il database PECUS reale, a meno che venga fornito un oracle/ground truth dedicato.

---
