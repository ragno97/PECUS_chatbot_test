PECUS CHAIN — AUTOTEST CLEAN

STRUTTURA CONSIGLIATA
---------------------
D:\Pecus Chain\pecus_chatbot_test\
│
├── pecus_autotest.py
├── tests\
│   └── pecus_llm_suite.csv
│
├── results\
└── results_archive\

NON servono più:
- run_pecus_autotest_v2.py
- evaluate_pecus_autotest_v2.py
- repair_pecus_raw_v1_v2.py
- finalize_pecus_run.py
- vecchi runner V1/V2/V3
- vecchi evaluator V1/V2/V3

La nuova pipeline usa uno schema raw unico fin dalla prima riga.

============================================================
1. PULIZIA PRIMA DEL NUOVO RUN
============================================================

py pecus_autotest.py clean

Il comando NON cancella i vecchi risultati.
Sposta results\ dentro:

results_archive\results_YYYYMMDD_HHMMSS\

e ricrea una nuova results\ vuota.

============================================================
2. NUOVO SMOKE PULITO — CONSIGLIATO ADESSO
============================================================

py pecus_autotest.py run --mode smoke

Esegue solo le 27 domande canoniche selezionate.

Timeout default: 240 secondi.

Per cambiarlo:
py pecus_autotest.py run --mode smoke --timeout 300

============================================================
3. FUNCTIONAL
============================================================

py pecus_autotest.py run --mode functional

79 test:
27 canoniche + 52 parafrasi funzionali.

============================================================
4. REGRESSION
============================================================

py pecus_autotest.py run --mode regression

53 test:
context decay
scope recovery
entity switching
noise retention
paraphrase production

============================================================
5. ALL
============================================================

py pecus_autotest.py run --mode all

132 test totali.

============================================================
6. RESUME
============================================================

Se un run si ferma per timeout:

py pecus_autotest.py resume "results\AUTO_YYYYMMDD_HHMMSS"

Il raw mantiene attempt_no e attempt_uid fin dalla prima riga.
Non servono repair o conversioni.

============================================================
7. EVALUATE
============================================================

Per rivalutare senza inviare messaggi:

py pecus_autotest.py evaluate "results\AUTO_YYYYMMDD_HHMMSS"

============================================================
OUTPUT DI OGNI RUN
============================================================

results\AUTO_YYYYMMDD_HHMMSS\
│
├── run_manifest.txt
├── suite_snapshot.csv
├── raw_results.csv
├── evaluated_attempts.csv
├── evaluated_results.csv
├── paraphrase_consistency.csv
├── area_summary.csv
└── summary.txt

raw_results.csv:
tutti i tentativi, inclusi timeout/retry.

evaluated_attempts.csv:
valutazione di ciascun tentativo.

evaluated_results.csv:
un record finale per test; usa l'ultimo tentativo valido.

summary.txt:
KPI e non-pass leggibili.

============================================================
REGOLE
============================================================

- un timeout interrompe sempre il run;
- il resume riparte solo dai test non raccolti con successo;
- la chat WhatsApp non viene resettata;
- i risultati vecchi non vengono cancellati dal comando clean;
- rischio mastite/chetosi resta distinto da diagnosi;
- terapia viene marcata come review;
- la priorità non viene valutata come capability implementata;
- la suite_snapshot rende ogni run riproducibile.
