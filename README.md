# Pecus Chain WhatsApp LLM Autotest

Repository per eseguire test automatici sul chatbot Pecus Chain via WhatsApp Web.

Lo script principale invia le domande definite nella suite CSV a una chat WhatsApp Web, raccoglie le risposte del bot, salva i risultati grezzi e genera file di valutazione leggibili.

## Struttura del progetto

```text
.
|-- pecus_autotest.py
|-- tests/
|   `-- pecus_llm_suite.csv
|-- results/
|-- results_archive/
|-- whatsapp_profile/
|-- README_PECUS_AUTOTEST_CLEAN.txt
|-- requirements.txt
`-- README.md
```

## File e cartelle

`pecus_autotest.py`

Script unico della pipeline. Contiene:

- selezione dei test da eseguire;
- collegamento a WhatsApp Web tramite Playwright;
- invio delle domande;
- raccolta delle risposte del bot;
- salvataggio dei risultati raw;
- valutazione automatica dei risultati;
- generazione dei report finali;
- comandi CLI `clean`, `run`, `resume` ed `evaluate`.

`tests/pecus_llm_suite.csv`

Suite di test in formato CSV con separatore `;`. Ogni riga rappresenta un caso o una variante. Le colonne principali sono:

- `test_id`: identificativo univoco del test;
- `case_id`: identificativo del caso logico;
- `area`: area funzionale, ad esempio `MUNGITURA`, `PRODUZIONE`, `MASTITE`, `METABOLICO`, `GENERICO`;
- `suite_type`: tipo di suite, ad esempio `functional` o `regression`;
- `scenario` e `scenario_turn`: scenario e ordine nei test multi-turn;
- `variant_type`: variante canonica o parafrasi;
- `question`: domanda inviata al bot;
- `evaluation_profile`: profilo usato dalla valutazione automatica;
- `expected_scope`, `expected_animal`, `expected_behavior`, `expected_fields`: aspettative usate per verificare la risposta;
- `fallback`, `guardrail`, `support_current`: note su fallback, limiti attesi e stato di supporto.

`results/`

Cartella generata dai run correnti. Ogni esecuzione crea una sottocartella `AUTO_YYYYMMDD_HHMMSS`.

`results_archive/`

Archivio dei risultati precedenti. Il comando `clean` sposta il contenuto di `results/` dentro questa cartella invece di cancellarlo.

`whatsapp_profile/`

Profilo browser persistente usato da Playwright per WhatsApp Web. Serve a mantenere la sessione dopo il login con QR code.

Questa cartella non deve essere versionata: puo contenere dati locali, cache e informazioni di sessione.

`README_PECUS_AUTOTEST_CLEAN.txt`

Documento storico con le istruzioni operative essenziali della pipeline pulita.

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

Il collegamento avviene tramite un profilo Chromium persistente nella cartella `whatsapp_profile/`.

Al primo avvio:

1. Eseguire un run, per esempio:

   ```powershell
   py pecus_autotest.py run --mode smoke
   ```

2. Si apre una finestra Chromium controllata da Playwright.
3. Se WhatsApp Web mostra il QR code, scansionarlo dal telefono.
4. Aprire o selezionare la chat con il bot da testare.
5. Lasciare la finestra aperta: lo script usa quella sessione per inviare domande e leggere le risposte.

Dagli avvii successivi, se la sessione WhatsApp e ancora valida, il profilo `whatsapp_profile/` permette di rientrare senza ripetere il QR code.

Il bot cercato di default e:

```text
Marica Marches
```

Per usare un nome diverso:

```powershell
py pecus_autotest.py run --mode smoke --bot-name "Nome Bot"
```

Nota operativa: lo script identifica i messaggi del bot tramite il nome presente nei metadati WhatsApp (`data-pre-plain-text`). Il nome passato con `--bot-name` deve quindi corrispondere al nome visualizzato da WhatsApp nella chat.

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

Esegue le domande canoniche funzionali.

Eseguire la suite funzionale:

```powershell
py pecus_autotest.py run --mode functional
```

Esegue domande canoniche e parafrasi funzionali.

Eseguire la suite di regressione:

```powershell
py pecus_autotest.py run --mode regression
```

Esegue scenari di regressione, inclusi contesto, cambio entita, rumore e produzione di parafrasi.

Eseguire tutto:

```powershell
py pecus_autotest.py run --mode all
```

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
- `collector_note`: note del collector, per esempio timeout o risposta vuota.

`evaluated_attempts.csv`

Valutazione di ogni singolo tentativo presente nel raw. Aggiunge colonne derivate come:

- `collector_status`;
- `semantic_status`;
- `scope_status`;
- `animal_status`;
- `detected_scope`;
- `detected_animals`;
- `response_class`;
- `guardrail_flags`;
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

`summary.txt`

Report leggibile del run. Riporta:

- KPI complessivi;
- KPI core;
- KPI overall;
- riepilogo per area;
- statistiche di latenza;
- elenco dei test non-pass o con flag.

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

Esito centrale della risposta: semantica, perimetro richiesto e riferimenti attesi.

`overall_status`

Esito piu prudente: include anche guardrail e condizioni che possono trasformare un pass tecnico in un risultato da rivedere.

## Note importanti

- Un timeout interrompe il run in modo protettivo.
- Il comando `resume` riparte solo dai test senza raccolta valida.
- La chat WhatsApp non viene resettata automaticamente tra i test.
- Il profilo `whatsapp_profile/` e locale e non va committato.
- Gli output in `results/` e `results_archive/` sono generati e possono contenere risposte reali del bot: per questo sono esclusi da git.
- La suite snapshot rende ogni run riproducibile anche se la suite sorgente cambia.
