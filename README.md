# PECUS CHAIN - Master LLM Autotest

Pipeline unica per testare automaticamente il chatbot PECUS CHAIN tramite WhatsApp Web.

Il sistema invia a PECUS le domande definite nella master suite, raccoglie le risposte via WhatsApp Web, salva i risultati grezzi e produce valutazioni multidimensionali su qualita, contesto, robustezza conversazionale, fallback, guardrail e performance.

La presenza di una domanda nella suite non significa che il relativo segnale sia disponibile in ogni stalla. Il test verifica anche che PECUS dichiari correttamente quando un dato e non monitorato, non integrato, non aggiornato o non disponibile.

## Documenti di riferimento

Il README resta la guida principale per preparare il sistema ed eseguire la suite. Per approfondire:

- [PECUS_AUTOTEST_MASTER_SPEC.md](PECUS_AUTOTEST_MASTER_SPEC.md): specifica master della pipeline.
- [01_GUIDA_PARAMETRI_MONITORATI.md](01_GUIDA_PARAMETRI_MONITORATI.md): cosa misura l'evaluator e quali domini di stalla vengono interrogati.
- [02_COMANDI_MASTER_SUITE.md](02_COMANDI_MASTER_SUITE.md): riferimento rapido dei comandi.
- [03_GUIDA_RISULTATI.md](03_GUIDA_RISULTATI.md): guida dettagliata ai file di output e ai KPI.
- [README_PECUS_AUTOTEST_CLEAN.txt](README_PECUS_AUTOTEST_CLEAN.txt): documento storico della pipeline precedente.

## Struttura del progetto

```text
pecus_chatbot_test/
|-- pecus_autotest.py
|-- tests/
|   |-- pecus_llm_suite.csv
|   |-- pecus_suite_coverage.csv
|   `-- pecus_historical_baselines.csv
|-- results/
|-- results_archive/
|-- whatsapp_profile/
|-- PECUS_AUTOTEST_MASTER_SPEC.md
|-- 01_GUIDA_PARAMETRI_MONITORATI.md
|-- 02_COMANDI_MASTER_SUITE.md
|-- 03_GUIDA_RISULTATI.md
|-- README_PECUS_AUTOTEST_CLEAN.txt
|-- requirements.txt
`-- README.md
```

## File principali

`pecus_autotest.py`

Runner unico della pipeline. Gestisce:

- selezione dei test;
- filtro dei record attivi tramite `enabled`;
- apertura di WhatsApp Web con Playwright;
- invio automatico delle domande;
- raccolta delle risposte;
- salvataggio progressivo del raw;
- resume dopo timeout o interruzione;
- valutazione automatica;
- generazione dei report.

`tests/pecus_llm_suite.csv`

Catalogo master dei test. La versione corrente contiene 186 record:

| Layer | Test | Stato |
|---|---:|---|
| Functional canoniche | 27 | attivi |
| Functional parafrasi | 52 | attivi |
| RUN_001 legacy | 10 | attivi |
| V3 regression | 53 | attivi |
| V2 deprecated reference | 44 | conservati, non usati come gate |
| Totale catalogo | 186 | |
| Totale attivo `full` | 142 | |

Colonne importanti:

- `test_id`: identificativo univoco del test.
- `case_id`: identificativo del caso logico.
- `area`: area funzionale, per esempio `MUNGITURA`, `PRODUZIONE`, `MASTITE`, `METABOLICO`, `GENERICO`.
- `suite_type`: layer del test, per esempio `functional`, `legacy`, `regression`, `deprecated_reference`.
- `scenario` e `scenario_turn`: scenario e ordine nei test conversazionali.
- `variant_type`: domanda canonica o parafrasi.
- `question`: domanda inviata al bot.
- `evaluation_profile`: profilo usato dall'evaluator.
- `expected_scope`, `expected_animal`, `expected_behavior`, `expected_fields`: aspettative valutate.
- `fallback`, `guardrail`, `support_current`: limiti e note operative attese.
- `enabled`: include o esclude il record dai run attivi.
- `origin`, `methodology_status`, `test_layer`, `legacy_test_id`, `animal_explicit`, `evaluator_dimensions`: metadati metodologici.

`tests/pecus_suite_coverage.csv`

Vista di copertura della suite functional: per ogni `case_id` riporta domanda canonica, numero di parafrasi e varianti associate.

`tests/pecus_historical_baselines.csv`

Baseline RUN_001 e V3.1 usate per confrontare i run correnti con i benchmark storici.

`results/`

Cartella dei run correnti. Ogni esecuzione crea `results/AUTO_YYYYMMDD_HHMMSS/`.

`results_archive/`

Archivio dei risultati precedenti. Il comando `clean` sposta qui la vecchia cartella `results/`.

`whatsapp_profile/`

Profilo Chromium persistente usato da Playwright per mantenere la sessione WhatsApp Web. Questa cartella resta locale e non va caricata in repository.

## Preparazione del sistema

### Prerequisiti

Servono:

- Python 3 installato;
- accesso a WhatsApp sul telefono;
- possibilita di usare WhatsApp Web;
- chat o contatto del bot PECUS da testare;
- repository scaricata localmente.

### Installazione dipendenze

Da PowerShell, nella cartella della repository:

```powershell
cd "D:\Pecus Chain\pecus_chatbot_test"
py -m pip install -r requirements.txt
py -m playwright install chromium
```

La dipendenza principale e Playwright. Chromium viene installato con il secondo comando.

### Verifica rapida

Controllare che lo script parta e mostri le modalita disponibili:

```powershell
py pecus_autotest.py run --help
```

Le modalita previste sono:

```text
smoke, canonical, functional, legacy, regression, full, all, deprecated_reference
```

## Collegamento a WhatsApp Web

Il collegamento a WhatsApp Web avviene tramite Playwright. Lo script apre una finestra Chromium non headless e usa il profilo persistente `whatsapp_profile/`.

Questo profilo funziona come un browser dedicato ai test: dopo il primo accesso salva la sessione WhatsApp Web e consente ai run successivi di ripartire senza scansionare ogni volta il QR code.

### Prima del primo run

Verificare che:

- il telefono con WhatsApp sia acceso e connesso;
- l'account WhatsApp abbia accesso alla chat del bot;
- il nome del contatto o della chat del bot sia noto;
- non ci siano altri run che usano la stessa cartella `whatsapp_profile/`;
- le dipendenze siano installate.

### Primo collegamento

1. Avviare un run breve:

   ```powershell
   py pecus_autotest.py run --mode canonical
   ```

   `canonical` e consigliato per il primo collegamento perche esegue solo le 27 domande canoniche. Anche `smoke` e equivalente.

2. Attendere l'apertura della finestra Chromium controllata da Playwright.

3. Se WhatsApp Web mostra il QR code:

   - aprire WhatsApp sul telefono;
   - entrare in dispositivi collegati;
   - scegliere l'opzione per collegare un nuovo dispositivo;
   - scansionare il QR code mostrato nella finestra Chromium.

4. Attendere il caricamento completo di WhatsApp Web.

5. Aprire manualmente la chat del bot PECUS nella finestra Chromium.

6. Verificare che in basso sia visibile la casella di scrittura del messaggio.

7. Lasciare la finestra aperta e non usare quella finestra per altre conversazioni mentre il run e in corso.

Quando la casella di scrittura e visibile, lo script inizia a inviare le domande della suite. Per ogni test compila il messaggio, preme `Enter`, attende la risposta del bot e salva il risultato.

### Nome del bot

Il bot cercato di default e:

```text
Marica Marches
```

Per usare un nome diverso:

```powershell
py pecus_autotest.py run --mode canonical --bot-name "Nome Bot"
```

Lo script identifica le risposte del bot tramite il nome presente nei metadati WhatsApp (`data-pre-plain-text`). Il valore passato con `--bot-name` deve corrispondere al nome visualizzato da WhatsApp nella chat.

### Avvii successivi

Se la sessione WhatsApp Web e ancora valida:

1. avviare il comando desiderato;
2. attendere l'apertura automatica di WhatsApp Web;
3. verificare che la chat del bot sia aperta;
4. lasciare lavorare lo script fino alla fine del run.

Se WhatsApp Web apre una chat diversa, selezionare manualmente la chat corretta prima che lo script inizi a inviare domande.

### Durante il run

Durante l'esecuzione:

- non chiudere la finestra Chromium;
- non cambiare chat;
- non scrivere manualmente nella casella messaggi;
- evitare di usare WhatsApp Web dallo stesso profilo in un'altra finestra;
- tenere il telefono connesso se WhatsApp lo richiede;
- non modificare `tests/pecus_llm_suite.csv` fino alla fine del run.

Lo script salva progressivamente i risultati in `raw_results.csv`. Se un test va in timeout o la risposta non viene raccolta, il run si ferma in modo protettivo e stampa il comando da usare per riprendere.

### Problemi comuni

Se compare di nuovo il QR code:

- la sessione salvata in `whatsapp_profile/` non e piu valida;
- scansionare di nuovo il QR code;
- riaprire la chat del bot;
- rilanciare o riprendere il run.

Se lo script resta fermo prima di inviare domande:

- controllare che WhatsApp Web sia caricato;
- controllare che la chat del bot sia aperta;
- controllare che la casella di scrittura sia visibile;
- chiudere manualmente eventuali popup o schermate iniziali.

Se le risposte non vengono raccolte:

- verificare che `--bot-name` corrisponda esattamente al nome mostrato da WhatsApp;
- controllare che il bot stia rispondendo nella stessa chat;
- aumentare il timeout:

```powershell
py pecus_autotest.py run --mode canonical --timeout 300
```

Se si vuole ripartire da un login pulito:

1. chiudere tutte le finestre Chromium aperte dallo script;
2. eliminare la cartella locale `whatsapp_profile/`;
3. rilanciare un run;
4. scansionare nuovamente il QR code.

Attenzione: `whatsapp_profile/` puo contenere dati locali e informazioni di sessione. Non va caricato nella repository e non va condiviso.

## Utilizzo della suite

### Pulire i risultati correnti

```powershell
py pecus_autotest.py clean
```

Il comando non cancella i risultati. Sposta `results/` in:

```text
results_archive/results_YYYYMMDD_HHMMSS/
```

e crea una nuova cartella `results/` vuota.

### Solo domande canoniche - 27 test

```powershell
py pecus_autotest.py run --mode canonical
```

Alias:

```powershell
py pecus_autotest.py run --mode smoke
```

Usarlo per debug rapido, controllo di una nuova build o verifica minima prima di un run piu lungo.

### Functional - 79 test

```powershell
py pecus_autotest.py run --mode functional
```

Esegue:

```text
27 canoniche
52 parafrasi
= 79 test
```

Usarlo per verificare coverage funzionale, robustezza linguistica e consistenza canonica/parafrasi.

### Legacy RUN_001 - 10 test

```powershell
py pecus_autotest.py run --mode legacy
```

Usarlo per confronti con la baseline conversazionale storica RUN_001.

### Regression V3 - 53 test

```powershell
py pecus_autotest.py run --mode regression
```

Scenari coperti:

```text
A_CONTEXT_DECAY
B_SCOPE_RECOVERY
C_ENTITY_SWITCH
D_NOISE_RETENTION
E_PARAPHRASE_PRODUCTION
```

Usarlo quando cambiano memoria conversazionale, state management, scope o gestione di parafrasi.

### Full - 142 test attivi

Comando consigliato per una baseline completa:

```powershell
py pecus_autotest.py run --mode full
```

Alias:

```powershell
py pecus_autotest.py run --mode all
```

Esegue:

```text
79 functional
10 RUN_001 legacy
53 V3 regression
= 142 test
```

`full` e la modalita di default se `--mode` non viene specificato.

### V2 deprecated - 44 test

```powershell
py pecus_autotest.py run --mode deprecated_reference
```

Questa modalita serve solo per audit o indagine storica. Non usarla come acceptance gate.

### Timeout personalizzato

```powershell
py pecus_autotest.py run --mode full --timeout 300
```

Default:

```text
240 s
```

### Suite, risultati e bot personalizzati

```powershell
py pecus_autotest.py run --mode full --suite "tests\pecus_llm_suite.csv"
py pecus_autotest.py run --mode full --results-dir "results_test"
py pecus_autotest.py run --mode full --bot-name "Marica Marches"
```

### Riprendere un run interrotto

```powershell
py pecus_autotest.py resume "results\AUTO_YYYYMMDD_HHMMSS"
```

Con timeout personalizzato:

```powershell
py pecus_autotest.py resume "results\AUTO_YYYYMMDD_HHMMSS" --timeout 300
```

Il resume:

1. legge `raw_results.csv`;
2. legge `suite_snapshot.csv`;
3. individua i `test_id` gia raccolti con successo;
4. preserva tutti i tentativi;
5. aumenta `attempt_no`;
6. riparte dal primo test non valido;
7. rivaluta il run.

### Rivalutare senza inviare messaggi

```powershell
py pecus_autotest.py evaluate "results\AUTO_YYYYMMDD_HHMMSS"
```

Usarlo quando cambia solo l'evaluator, quando vengono aggiunte nuove rubric o quando si vuole rivalutare lo stesso raw senza ripetere la conversazione WhatsApp.

## Workflow consigliato

Sviluppo quotidiano:

```powershell
py pecus_autotest.py run --mode canonical
```

Modifiche a NLU, prompt o generazione risposta:

```powershell
py pecus_autotest.py run --mode functional
```

Modifiche a memoria, state management o scope:

```powershell
py pecus_autotest.py run --mode regression
```

Nuova baseline o pre-release:

```powershell
py pecus_autotest.py clean
py pecus_autotest.py run --mode full
```

## Parametri monitorati

L'evaluator master misura dimensioni separate, tra cui:

- Intent Accuracy;
- Scope Accuracy;
- Animal Resolution Accuracy;
- Context Accuracy;
- Implicit Animal-Context Accuracy;
- Context Retention Depth;
- Scope Recovery;
- Entity Probe;
- Previous Entity Recall;
- Noise Recovery;
- Functional Paraphrase Consistency;
- Regression Paraphrase Robustness;
- Temporal Grounding;
- Data Availability Disclosure;
- Fallback Quality;
- Guardrail clinici e terapeutici;
- Advice overreach;
- Metric Consistency;
- Collector Validity;
- latenze p50, p90, p95 e max.

Per il dettaglio completo consultare [01_GUIDA_PARAMETRI_MONITORATI.md](01_GUIDA_PARAMETRI_MONITORATI.md).

## Output prodotti da ogni run

Ogni run crea:

```text
results/
`-- AUTO_YYYYMMDD_HHMMSS/
    |-- run_manifest.txt
    |-- suite_snapshot.csv
    |-- raw_results.csv
    |-- evaluated_attempts.csv
    |-- evaluated_results.csv
    |-- paraphrase_consistency.csv
    |-- area_summary.csv
    |-- scenario_summary.csv
    |-- aggregate_metrics.csv
    |-- historical_comparison.csv
    |-- summary.txt
    `-- summary.md
```

In caso di errore del locator WhatsApp possono essere prodotti anche:

```text
whatsapp_locator_failure.png
whatsapp_locator_failure.txt
```

### File principali di output

`run_manifest.txt`

Manifest del run: ID, modalita, data/ora, suite, timeout, nome bot e versione schema.

`suite_snapshot.csv`

Copia esatta della suite usata per il run. Per interpretare un vecchio run usare sempre questo file, non la suite corrente.

`raw_results.csv`

Registro grezzo. Contiene per ogni tentativo domanda, risposta PECUS, timestamp, latenza, message ID, metadati WhatsApp, collector status e attempt number. Non va modificato manualmente.

`evaluated_attempts.csv`

Valutazione di ogni singolo tentativo. Utile per analizzare retry, timeout e stabilita.

`evaluated_results.csv`

File principale turno-per-turno. Contiene un record finale per `test_id` e usa l'ultimo tentativo valido quando esistono retry.

`paraphrase_consistency.csv`

Confronta ogni parafrasi con la domanda canonica dello stesso `case_id`.

`area_summary.csv`

Aggrega i risultati per area funzionale.

`scenario_summary.csv`

Aggrega i risultati per scenario conversazionale.

`aggregate_metrics.csv`

File principale per KPI quantitativi: quality, collector, functional, legacy, regression, guardrail, metric consistency e latency.

`historical_comparison.csv`

Confronta il run corrente con baseline storiche RUN_001 e V3.1.

`summary.txt`

Sintesi leggibile da terminale: KPI, area summary, scenario summary, non-pass e flag principali.

`summary.md`

Report Markdown condivisibile con sviluppatori, team prodotto o release note.

Per una guida estesa ai risultati consultare [03_GUIDA_RISULTATI.md](03_GUIDA_RISULTATI.md).

## Lettura dei risultati

Ordine consigliato per una review completa:

```text
1. summary.md
2. aggregate_metrics.csv
3. historical_comparison.csv
4. area_summary.csv
5. scenario_summary.csv
6. evaluated_results.csv
7. raw_results.csv
```

Se emerge un `FAIL`, seguire:

```text
summary / aggregate
evaluated_results.csv
evaluated_attempts.csv
raw_results.csv
suite_snapshot.csv
```

Questo permette di distinguere:

- problema reale PECUS;
- limite dell'evaluator;
- problema del collector;
- aspettativa errata del test.

## Status

`PASS`

La dimensione valutata soddisfa il criterio.

`REVIEW`

Il comportamento richiede revisione umana. Non significa automaticamente risposta sbagliata: puo indicare ambiguita, incompletezza, fallback debole, limite non dichiarato o advice da controllare.

`FAIL`

Errore forte: intent errato, animale errato, scope errato, perdita del contesto, contraddizione incompatibile o guardrail grave.

`INVALID_COLLECTOR`

Il test non puo essere usato per giudicare PECUS perche la raccolta non e valida: timeout, risposta vuota, contaminazione o troncamento grave.

`N/A`

La dimensione non e pertinente a quel test.

## Core vs Overall

`core_status`

Risponde alla domanda: PECUS ha capito e risposto correttamente all'intento principale?

`overall_status`

Aggiunge qualita e sicurezza: temporal grounding, data availability, fallback, guardrail e incoerenze rilevanti.

Esempio: PECUS puo identificare correttamente gli animali con conducibilita alta (`core_status = PASS`) ma proporre terapia senza gating (`overall_status = REVIEW`).

## Regole operative

- Un timeout interrompe il run in modo protettivo.
- Il comando `resume` riparte solo dai test senza raccolta valida.
- La chat WhatsApp non viene resettata automaticamente tra i test.
- `whatsapp_profile/` e locale e non va committato.
- `results/` e `results_archive/` sono inclusi nella repository come artefatti di confronto e audit.
- Il gate consigliato della versione master e `py pecus_autotest.py run --mode full`.
- I 44 test V2 `deprecated_reference` sono mantenuti per audit, ma non devono essere usati come acceptance gate.

## Obiettivo del sistema

L'autotest non deve dimostrare soltanto che PECUS sa rispondere. Deve verificare che PECUS:

1. capisca la domanda;
2. interroghi il dominio corretto;
3. mantenga animale e scope;
4. sia robusto alle parafrasi;
5. dichiari quale periodo sta usando;
6. dichiari quando un dato non e monitorato;
7. non inventi informazioni;
8. mantenga distinto rischio da diagnosi;
9. non trasformi automaticamente un risk score in terapia;
10. restituisca valori semanticamente coerenti;
11. mantenga una conversazione stabile;
12. risponda con performance compatibili con un uso operativo in stalla.

Il risultato finale deve essere un decision-support layer affidabile sui dati disponibili, non semplicemente un chatbot capace di generare testo.
