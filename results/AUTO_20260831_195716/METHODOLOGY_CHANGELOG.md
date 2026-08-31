# PECUS CHAIN — Master Evaluator V3.1 Restored

## Perché questa revisione

Il primo Master Evaluator aveva perso alcune regole già corrette nella V3.1 e aveva introdotto nuovi falsi errori.

Questa revisione modifica **solo la metodologia di scoring**.  
Il raw WhatsApp `AUTO_20260831_195716` non è stato modificato e non è stato rieseguito.

## Correzioni applicate

### 1. Context / entity implicita — ripristino V3.1

Lo scope viene valutato sulla **parte primaria della risposta**, non su termini come “stalla” o altri animali introdotti successivamente nelle raccomandazioni.

Una risposta individuale coerente non deve ripetere l'ID a ogni turno.

Effetto principale:

- V3 Context Retention Depth: **0 → 3**
- Implicit Animal-Context Accuracy: **80,8% → 84,6%**

### 2. Estrazione animal ID

Numeri come:

> 38 bufale hanno prodotto poco

non vengono più interpretati come ID `#38`.

Un ID viene riconosciuto solo in forme esplicite, ad esempio:

- `#3118`
- `animale #3118`
- `3118: ...`
- `3118 (L2, DIM 62)`

### 3. Paraphrase Consistency

Il vecchio evaluator richiedeva spesso overlap/Jaccard degli ID anche per liste dinamiche.

La nuova metodologia separa:

- **standalone paraphrase**: query autosufficiente;
- **contextual paraphrase**: query ellittica che dipende da un anchor conversazionale.

Per le liste dinamiche la consistenza è basata principalmente su:

- intent;
- filtro;
- scope;
- core status;

non sull'identità obbligatoria dell'intero set animale.

Nuove metriche:

- Functional Standalone Paraphrase Consistency: **32/49 = 65,3%**
- Functional Contextual Paraphrase Success: **0/3**

Il precedente `17/52 = 32,7%` non va più usato.

### 4. Data Availability Disclosure

Sono ora riconosciute correttamente dichiarazioni come:

- “non è presente la colonna fat_percent”;
- “non sono disponibili dati”;
- “nessuna lettura di ruminazione”;
- “valori null”.

Nuovo risultato:

- **7/11 = 63,6%**

Il precedente `0/2` non era metodologicamente rappresentativo.

### 5. Fallback Quality

Un risultato valido con zero animali non viene più trattato come “dato mancante”.

Esempi:

- “0 bufale non sono state munte oggi”
- “nessuna bufala soddisfa il criterio”
- “query restituisce zero righe per quel filtro”

Nuovo risultato:

- **7/9 = 77,8%**

Il precedente `0/9` era fortemente falsato.

## Metriche corrette principali

| Metrica | Prima | V3.1 restored |
|---|---:|---:|
| Intent Accuracy | 84,2% | 84,2% |
| Scope Accuracy | 88,7% | 89,5% |
| Animal Resolution | 90,9% | 92,4% |
| Context Accuracy | 88,7% | 89,5% |
| Implicit Context | 80,8% | 84,6% |
| Temporal Grounding | 58,8% | 58,8% |
| Data Availability Disclosure | 0/2 | 7/11 |
| Fallback Quality | 0/9 | 7/9 |
| Canonical Core Pass | 24/27 | 24/27 |
| Paraphrase Core Pass | 32/52 | 32/52 |
| Paraphrase Consistency | 17/52 | 32/49 standalone |
| Contextual Paraphrase | non separato | 0/3 |
| RUN_001 Retention Depth | 2 | 2 |
| V3 Retention Depth | 0 | 3 |
| Noise Recovery | 2/3 | 2/3 |

## Cosa rimane un problema reale

Le correzioni metodologiche non eliminano:

- Functional Paraphrase Core Pass = **61,5%**
- Contextual Paraphrase Success = **0/3**
- RUN_001 Context Retention Depth = **2** vs baseline 3
- Noise Recovery D5 = **0/1**
- Temporal Grounding = **58,8%**
- overreach terapeutico/nutrizionale
- incoerenze metriche rilevate

Questi devono restare finding di prodotto.

## Regola per le baseline future

Da questo punto la baseline Master deve essere calcolata con questa metodologia o versioni successive compatibili.

Non confrontare direttamente:

- `Functional Paraphrase Consistency 17/52` del vecchio evaluator
- con la nuova `Standalone Paraphrase Consistency 32/49`

perché il denominatore e il criterio sono cambiati.

Conservare sempre:

1. raw originale;
2. versione evaluator;
3. aggregate_metrics;
4. methodology changelog.
