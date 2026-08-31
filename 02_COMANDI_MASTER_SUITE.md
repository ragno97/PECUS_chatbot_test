# PECUS CHAIN — Comandi Master Autotest

Riferimento rapido per l'esecuzione della suite corrente.

# 9. Comandi completi

## 9.1 Archiviare i risultati precedenti

```powershell
py pecus_autotest.py clean
```

Sposta `results\` in:

```text
results_archive\results_YYYYMMDD_HHMMSS\
```

e crea una nuova `results\` vuota.

### Directory personalizzate

```powershell
py pecus_autotest.py clean --results-dir results --archive-dir results_archive
```

---

## 9.2 Solo domande canoniche — 27 test

```powershell
py pecus_autotest.py run --mode canonical
```

Alias:

```powershell
py pecus_autotest.py run --mode smoke
```

### Quando usarlo

- debug rapido;
- controllo di una nuova build;
- verifica minima prima di un run più lungo.

Non misura tutte le parafrasi e non è una baseline completa.

---

## 9.3 Functional — 79 test

```powershell
py pecus_autotest.py run --mode functional
```

Esegue:

```text
27 canoniche
+
52 parafrasi
=
79 test
```

### Quando usarlo

Per verificare:

- coverage delle domande operative;
- robustness linguistica;
- consistenza canonica ↔ parafrasi;
- aree Mungitura, Produzione, Mastite, Metabolico e Generico.

---

## 9.4 Legacy RUN_001 — 10 test

```powershell
py pecus_autotest.py run --mode legacy
```

### Misura principalmente

- Intent Accuracy;
- Scope Accuracy;
- Animal Resolution;
- Context Accuracy;
- implicit context;
- retention depth storico.

---

## 9.5 Regression V3 — 53 test

```powershell
py pecus_autotest.py run --mode regression
```

Scenari:

```text
A_CONTEXT_DECAY
B_SCOPE_RECOVERY
C_ENTITY_SWITCH
D_NOISE_RETENTION
E_PARAPHRASE_PRODUCTION
```

### Misura

- decadimento del contesto;
- recovery dopo scope switch;
- cambio animale;
- previous entity;
- rumore conversazionale;
- 12 parafrasi storiche sulla produzione animale.

---

## 9.6 Full — 142 test attivi

### Comando consigliato per la baseline completa

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
+
10 RUN_001 legacy
+
53 V3 regression
=
142 test
```

### Quando usarlo

- baseline ufficiale;
- pre-release;
- confronto tra build;
- regression completa;
- validazione dopo modifiche a prompt, router, state management o backend.

---

## 9.7 V2 deprecated — 44 test

```powershell
py pecus_autotest.py run --mode deprecated_reference
```

### Attenzione

Questa modalità è disponibile **solo per audit o indagine storica**.

Il V2 non deve essere usato come acceptance gate perché era stato sostituito dal V3 dopo problemi metodologici:

- contaminazione da virtualizzazione DOM;
- timeout con possible phase shift;
- prompt ambigui;
- cascade errors.

---

## 9.8 Impostare un timeout diverso

```powershell
py pecus_autotest.py run --mode full --timeout 300
```

Default:

```text
240 s
```

---

## 9.9 Specificare una suite diversa

```powershell
py pecus_autotest.py run --mode full --suite "tests\pecus_llm_suite.csv"
```

---

## 9.10 Specificare il nome del contatto WhatsApp

```powershell
py pecus_autotest.py run --mode full --bot-name "Marica Marches"
```

---

## 9.11 Specificare una cartella risultati diversa

```powershell
py pecus_autotest.py run --mode full --results-dir "results_test"
```

---

## 9.12 Riprendere un run interrotto

```powershell
py pecus_autotest.py resume "results\AUTO_YYYYMMDD_HHMMSS"
```

Con timeout personalizzato:

```powershell
py pecus_autotest.py resume "results\AUTO_YYYYMMDD_HHMMSS" --timeout 300
```

Il resume:

1. legge `raw_results.csv`;
2. individua i `test_id` già raccolti con successo;
3. preserva tutti i tentativi;
4. aumenta `attempt_no`;
5. riparte dal primo test non valido;
6. rivaluta il run.

---

## 9.13 Rivalutare un run senza inviare messaggi

```powershell
py pecus_autotest.py evaluate "results\AUTO_YYYYMMDD_HHMMSS"
```

Da usare quando:

- cambia solo l'evaluator;
- vengono aggiunte nuove rubric;
- si vuole rivalutare lo stesso raw;
- non si vogliono ripetere le conversazioni WhatsApp.

---

# 10. Workflow consigliato

## Sviluppo quotidiano

```powershell
py pecus_autotest.py run --mode canonical
```

## Modifica a NLU / prompt / response generation

```powershell
py pecus_autotest.py run --mode functional
```

## Modifica a memoria / state management / scope

```powershell
py pecus_autotest.py run --mode regression
```

## Nuova baseline / pre-release

```powershell
py pecus_autotest.py clean
py pecus_autotest.py run --mode full
```

---
