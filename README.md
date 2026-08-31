# Pecus Chain WhatsApp LLM Autotest

Repository per eseguire test automatici sul chatbot Pecus Chain via WhatsApp Web.

Lo script principale invia le domande definite nella suite CSV a una chat WhatsApp Web, raccoglie le risposte del bot, salva i risultati grezzi e genera file di valutazione leggibili.

## Struttura del progetto

```text
.
|-- pecus_autotest.py
|-- tests/
|   |-- pecus_llm_suite.csv
|   |-- pecus_historical_baselines.csv
|   `-- pecus_suite_coverage.csv
|-- results/
|-- results_archive/
|-- whatsapp_profile/
|-- PECUS_AUTOTEST_MASTER_SPEC.md
|-- README_PECUS_AUTOTEST_CLEAN.txt
|-- requirements.txt
`-- README.md
```

## File e cartelle

`pecus_autotest.py`

Script unico della pipeline. Contiene:

- selezione dei test da eseguire;
- filtro dei test attivi tramite colonna `enabled`;
- collegamento a WhatsApp Web tramite Playwright;
- invio delle domande;
- raccolta delle risposte del bot;
- salvataggio dei risultati raw;
- valutazione automatica dei risultati;
- generazione dei report finali;
- comandi CLI `clean`, `run`, `resume` ed `evaluate`.

`tests/pecus_llm_suite.csv`

Catalogo master dei test in formato CSV con separatore `;`. La versione corrente contiene 186 record:

- 79 test `functional` attivi;
- 10 test `legacy` attivi;
- 53 test `regression` attivi;
- 44 test `deprecated_reference` disattivati, conservati per audit.

Ogni riga rappresenta un caso o una variante. Le colonne principali sono:

- `test_id`: identificativo univoco del test;
- `case_id`: identificativo del caso logico;
- `area`: area funzionale, ad esempio `MUNGITURA`, `PRODUZIONE`, `MASTITE`, `METABOLICO`, `GENERICO`;
- `suite_type`: tipo di suite, ad esempio `functional`, `legacy`, `regression` o `deprecated_reference`;
- `scenario` e `scenario_turn`: scenario e ordine nei test multi-turn;
- `variant_type`: variante canonica o parafrasi;
- `question`: domanda inviata al bot;
- `evaluation_profile`: profilo usato dalla valutazione automatica;
- `expected_scope`, `expected_animal`, `expected_behavior`, `expected_fields`: aspettative usate per verificare la risposta;
- `fallback`, `guardrail`, `support_current`: note su fallback, limiti attesi e stato di supporto;
- `enabled`: include o esclude il test dai run attivi;
- `origin`: provenienza del test;
- `methodology_status`: stato metodologico, per esempio `active` o `deprecated_superseded_by_V3`;
- `test_layer`: livello logico del test;
- `legacy_test_id`: riferimento al test storico quando disponibile;
- `animal_explicit`: indica se la domanda nomina esplicitamente un animale;
- `evaluator_dimensions`: dimensioni di valutazione attese.

`tests/pecus_historical_baselines.csv`

Baseline storiche usate come riferimento per il confronto dei risultati. Contiene metriche RUN_001 e V3.1, per esempio accuratezza intent, scope, risoluzione animale, profondita di retention del contesto, noise recovery e latenze.

`tests/pecus_suite_coverage.csv`

Vista di copertura della suite funzionale. Per ogni `case_id` riporta domanda canonica, numero di varianti e parafrasi associate.

`PECUS_AUTOTEST_MASTER_SPEC.md`

Specifica master della nuova pipeline. Descrive catalogo, modalita di esecuzione, aree funzionali, dimensioni dell'evaluator, file prodotti e regole metodologiche principali.

`results/`

Cartella generata dai run correnti. Ogni esecuzione crea una sottocartella `AUTO_YYYYMMDD_HHMMSS`.

`results_archive/`

Archivio dei risultati precedenti. Il comando `clean` sposta il contenuto di `results/` dentro questa cartella invece di cancellarlo.

`whatsapp_profile/`

Profilo browser persistente usato da Playwright per WhatsApp Web. Serve a mantenere la sessione dopo il login con QR code.

Questa cartella non deve essere versionata: puo contenere dati locali, cache e informazioni di sessione.

`README_PECUS_AUTOTEST_CLEAN.txt`

Documento storico con le istruzioni operative della pipeline precedente. Resta utile per audit, ma la documentazione principale e `README.md` insieme a `PECUS_AUTOTEST_MASTER_SPEC.md`.

`requirements.txt`

Dipendenze Python minime del progetto. Attualmente contiene Playwright.

## Installazione

Prerequisiti:

- Python 3 installato;
- accesso a WhatsApp Web nel browser;
- chat WhatsApp gia disponibile con il bot da testare.

Installare le dipendenze:

```powershell
py -m pip install -r requirements.txt
py -m playwright install chromium
```

## Collegamento a WhatsApp Web

Il collegamento avviene tramite Playwright, che apre una finestra Chromium non headless e usa un profilo browser persistente nella cartella `whatsapp_profile/`.

Questo profilo funziona come un browser dedicato ai test: dopo il primo accesso salva la sessione WhatsApp Web e permette ai run successivi di ripartire senza scansionare ogni volta il QR code.

### Preparazione iniziale

Prima di avviare i test verificare che:

- il telefono con WhatsApp sia acceso e connesso;
- l'account WhatsApp abbia accesso alla chat del bot da testare;
- il nome della chat o del contatto del bot sia noto;
- nessun altro run dello script stia usando la stessa cartella `whatsapp_profile/`;
- le dipendenze siano installate:

```powershell
py -m pip install -r requirements.txt
py -m playwright install chromium
```

### Primo collegamento

1. Avviare uno smoke test. E consigliato usare `smoke` per il primo collegamento perche esegue meno casi:

   ```powershell
   py pecus_autotest.py run --mode smoke
   ```

2. Lo script apre una finestra Chromium controllata da Playwright e carica:

   ```text
   https://web.whatsapp.com
   ```

3. Se compare il QR code, collegare WhatsApp Web dal telefono:

   - aprire WhatsApp sul telefono;
   - entrare nella sezione dispositivi collegati;
   - scegliere l'opzione per collegare un nuovo dispositivo;
   - scansionare il QR code mostrato nella finestra Chromium.

4. Attendere il caricamento completo di WhatsApp Web.

5. Aprire manualmente la chat del bot da testare nella finestra Chromium.

6. Verificare che in basso sia visibile la casella di scrittura del messaggio.

7. Lasciare la finestra aperta e non usare quella finestra per altre conversazioni mentre il run e in corso.

Quando la casella di scrittura e visibile, lo script la rileva e inizia a inviare le domande della suite. Per ogni test compila il messaggio, preme `Enter`, attende la risposta del bot e salva il risultato.

### Avvii successivi

Dagli avvii successivi, se la sessione WhatsApp e ancora valida, il profilo `whatsapp_profile/` permette di rientrare senza ripetere il QR code.

La procedura diventa:

1. avviare il comando desiderato;
2. attendere l'apertura automatica di WhatsApp Web;
3. verificare che la chat del bot sia aperta;
4. lasciare lavorare lo script fino alla fine del run.

Se WhatsApp Web apre una chat diversa, selezionare manualmente la chat corretta prima che lo script inizi a inviare domande.

### Nome del bot

Il bot cercato di default e:

```text
Marica Marches
```

Per usare un nome diverso:

```powershell
py pecus_autotest.py run --mode smoke --bot-name "Nome Bot"
```

Nota operativa: lo script identifica i messaggi del bot tramite il nome presente nei metadati WhatsApp (`data-pre-plain-text`). Il nome passato con `--bot-name` deve quindi corrispondere al nome visualizzato da WhatsApp nella chat.

Esempio:

```powershell
py pecus_autotest.py run --mode functional --bot-name "Marica Marches"
```

### Durante il run

Durante l'esecuzione:

- non chiudere la finestra Chromium;
- non cambiare chat;
- non scrivere manualmente nella casella messaggi;
- evitare di usare WhatsApp Web dallo stesso profilo in un'altra finestra;
- tenere il telefono connesso se WhatsApp lo richiede;
- non modificare `tests/pecus_llm_suite.csv` fino alla fine del run.

Lo script salva progressivamente i risultati in `raw_results.csv`. Se un test va in timeout o la risposta non viene raccolta, il run si ferma in modo protettivo e stampa il comando da usare per riprendere.

### Ripresa dopo timeout o interruzione

Se il run si interrompe, non cancellare la cartella del run. Riprendere con:

```powershell
py pecus_autotest.py resume "results\AUTO_YYYYMMDD_HHMMSS"
```

Il resume:

- rilegge `raw_results.csv`;
- rilegge `suite_snapshot.csv`;
- identifica i test gia raccolti con successo;
- riparte solo dai test pendenti;
- mantiene il conteggio dei tentativi con `attempt_no` e `attempt_uid`.

All'avvio del resume lo script attende alcuni secondi prima di ripartire, cosi eventuali risposte tardive nella chat hanno il tempo di stabilizzarsi.

### Problemi comuni

Se compare di nuovo il QR code:

- la sessione salvata in `whatsapp_profile/` non e piu valida;
- scansionare di nuovo il QR code;
- poi riaprire la chat del bot e rilanciare o riprendere il run.

Se lo script resta fermo prima di inviare domande:

- controllare che WhatsApp Web sia caricato;
- controllare che la chat del bot sia aperta;
- controllare che la casella di scrittura sia visibile;
- se c'e un popup o una schermata iniziale, chiuderla manualmente.

Se le risposte non vengono raccolte:

- verificare che `--bot-name` corrisponda esattamente al nome mostrato da WhatsApp;
- controllare che il bot stia rispondendo nella stessa chat;
- aumentare il timeout, per esempio:

```powershell
py pecus_autotest.py run --mode smoke --timeout 300
```

Se WhatsApp Web e gia aperto altrove:

- chiudere altri browser o finestre che usano lo stesso account per i test;
- usare solo la finestra aperta da Playwright durante il run.

Se si vuole ripartire da un login pulito:

1. chiudere tutte le finestre Chromium aperte dallo script;
2. eliminare la cartella locale `whatsapp_profile/`;
3. rilanciare un run;
4. scansionare nuovamente il QR code.

Attenzione: `whatsapp_profile/` puo contenere dati locali e informazioni di sessione. Non va caricato nella repository e non va condiviso.

## Comandi principali

Pulire la cartella dei risultati correnti:

```powershell
py pecus_autotest.py clean
```

Il comando non cancella i risultati: sposta `results/` in `results_archive/results_YYYYMMDD_HHMMSS/` e ricrea una nuova `results/` vuota.

Eseguire uno smoke test:

```powershell
py pecus_autotest.py run --mode smoke
```

Esegue le 27 domande canoniche funzionali. `canonical` e un alias equivalente:

```powershell
py pecus_autotest.py run --mode canonical
```

Eseguire la suite funzionale:

```powershell
py pecus_autotest.py run --mode functional
```

Esegue 79 test: 27 canoniche e 52 parafrasi funzionali.

Eseguire la suite legacy RUN_001:

```powershell
py pecus_autotest.py run --mode legacy
```

Esegue i 10 test storici RUN_001.

Eseguire la suite di regressione:

```powershell
py pecus_autotest.py run --mode regression
```

Esegue 53 scenari di regressione V3, inclusi contesto, cambio entita, rumore e produzione di parafrasi.

Eseguire tutto il gate attivo:

```powershell
py pecus_autotest.py run --mode full
```

Esegue 142 test attivi: functional, legacy e regression. `full` e anche la modalita di default se `--mode` non viene specificato.

Alias equivalente:

```powershell
py pecus_autotest.py run --mode all
```

Eseguire i test V2 storici disattivati:

```powershell
py pecus_autotest.py run --mode deprecated_reference
```

Questa modalita serve solo per audit o confronto storico. Non usarla come acceptance gate.

Riprendere un run interrotto:

```powershell
py pecus_autotest.py resume "results\AUTO_YYYYMMDD_HHMMSS"
```

Rivalutare un run senza inviare nuovi messaggi:

```powershell
py pecus_autotest.py evaluate "results\AUTO_YYYYMMDD_HHMMSS"
```

Cambiare timeout di attesa risposta:

```powershell
py pecus_autotest.py run --mode smoke --timeout 300
```

## Output di un run

Ogni run crea una cartella:

```text
results/AUTO_YYYYMMDD_HHMMSS/
```

Dentro si trovano questi file.

`run_manifest.txt`

Manifest del run. Riporta:

- `run_id`;
- modalita eseguita;
- data e ora di creazione;
- suite usata;
- timeout;
- nome del bot;
- versione dello schema raw.

`suite_snapshot.csv`

Copia della suite usata al momento del run. Serve a rendere riproducibile la valutazione anche se in seguito `tests/pecus_llm_suite.csv` cambia.

`raw_results.csv`

Risultati grezzi raccolti da WhatsApp Web. Contiene una riga per ogni tentativo, inclusi timeout o retry.

Colonne importanti:

- `run_id`, `run_mode`, `sequence_no`: contesto del run e ordine di esecuzione;
- `attempt_no`, `attempt_uid`: numero e identificativo del tentativo;
- `test_id`, `case_id`, `area`, `suite_type`, `scenario`: metadati del test;
- `question`: domanda inviata al bot;
- `response`: risposta raccolta;
- `latency_ms`: tempo di risposta in millisecondi;
- `message_count`: numero di messaggi raccolti per la risposta;
- `response_truncated`: indica se la risposta e stata troncata o espansa;
- `message_ids`, `whatsapp_metadata`: riferimenti ai messaggi WhatsApp;
- `send_system_timestamp`, `system_timestamp`: timestamp di invio e raccolta;
- `collector_success`: esito della raccolta;
- `collector_note`: note del collector, per esempio timeout o risposta vuota;
- `enabled`, `origin`, `methodology_status`, `test_layer`, `legacy_test_id`, `animal_explicit`, `evaluator_dimensions`: metadati master copiati dalla suite.

`evaluated_attempts.csv`

Valutazione di ogni singolo tentativo presente nel raw. Aggiunge colonne derivate come:

- `collector_status`;
- `intent_status`;
- `scope_status`;
- `animal_status`;
- `context_status`;
- `implicit_context_status`;
- `temporal_status`;
- `availability_status`;
- `fallback_status`;
- `detected_scope`;
- `detected_animals`;
- `response_class`;
- `guardrail_flags`;
- `advice_flags`;
- `metric_flags`;
- `quality_flags`;
- `core_status`;
- `overall_status`;
- `error_flags`.

Questo file e utile per capire se un retry ha migliorato o peggiorato il risultato.

`evaluated_results.csv`

Risultato finale per ogni test. Se ci sono piu tentativi, seleziona il tentativo valido finale secondo la logica dello script.

Rispetto a `evaluated_attempts.csv`, include anche:

- `attempts_total`: quanti tentativi esistono per quel test;
- `chosen_attempt_no`: quale tentativo e stato scelto come finale.

Questo e il file principale da usare per KPI e confronto tra run.

`paraphrase_consistency.csv`

Report di coerenza tra domanda canonica e varianti/parafrasi. Le colonne principali sono:

- `case_id`;
- `area`;
- `test_id`;
- `variant_type`;
- `canonical_test_id`;
- `canonical_class`;
- `response_class`;
- `animal_jaccard`;
- `consistency_status`.

Serve a verificare se formulazioni diverse della stessa richiesta producono risposte coerenti.

`area_summary.csv`

Aggregazione per area funzionale. Contiene:

- numero di test per area;
- collector validi;
- conteggi `PASS`, `REVIEW`, `FAIL` per `core_status`;
- conteggi `PASS`, `REVIEW`, `FAIL` per `overall_status`;
- numero di collector invalidi.

`scenario_summary.csv`

Aggregazione per scenario multi-turn. Riporta test, collector validi, core pass, context pass e overall pass per ogni scenario.

`aggregate_metrics.csv`

Metriche aggregate dell'evaluator master. Include famiglie come:

- `quality`;
- `collector`;
- `functional`;
- `legacy`;
- `regression`;
- `guardrail`;
- `metric_consistency`;
- `latency`.

Esempi di metriche: Intent Accuracy, Scope Accuracy, Animal Resolution Accuracy, Context Accuracy, Temporal Grounding, Data Availability Disclosure, Functional Paraphrase Consistency, Context Retention Depth, Scope Recovery, Noise Recovery e latenze p50/p90/p95/max.

`historical_comparison.csv`

Confronto tra metriche correnti e baseline storiche RUN_001 / V3.1. Serve per capire se la nuova versione migliora, peggiora o mantiene il comportamento rispetto ai run di riferimento.

`summary.txt`

Report leggibile del run. Riporta:

- KPI complessivi;
- KPI core;
- KPI overall;
- metriche aggregate QA;
- riepilogo per area;
- riepilogo per scenario;
- statistiche di latenza;
- elenco dei test non-pass o con flag.

`summary.md`

Versione Markdown del report, piu comoda da condividere o leggere in GitHub. Contiene tabella delle metriche aggregate, confronto storico e lista non-pass/flag.

## Interpretazione degli stati

`PASS`

La risposta soddisfa le aspettative per il profilo di valutazione.

`REVIEW`

La risposta non e necessariamente errata, ma richiede revisione umana. Tipicamente succede quando il bot usa formulazioni ambigue, amplia troppo il perimetro, o attiva guardrail come terapia, diagnosi o prescrizione nutrizionale.

`FAIL`

La risposta viola un requisito atteso o non contiene le informazioni essenziali.

`INVALID_COLLECTOR`

Il problema non e la qualita della risposta, ma la raccolta: timeout, risposta vuota, messaggio non intercettato o altro problema tecnico.

`core_status`

Esito centrale della risposta: intent, perimetro richiesto, riferimenti attesi e dimensioni principali della qualita.

`overall_status`

Esito piu prudente: include anche guardrail e condizioni che possono trasformare un pass tecnico in un risultato da rivedere.

## Note importanti

- Un timeout interrompe il run in modo protettivo.
- Il comando `resume` riparte solo dai test senza raccolta valida.
- La chat WhatsApp non viene resettata automaticamente tra i test.
- Il profilo `whatsapp_profile/` e locale e non va committato.
- Gli output in `results/` e `results_archive/` sono inclusi nella repository come artefatti di confronto e audit.
- La suite snapshot rende ogni run riproducibile anche se la suite sorgente cambia.
- Il gate consigliato della versione master e `py pecus_autotest.py run --mode full`.
