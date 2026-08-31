# PECUS CHAIN — Guida ai parametri monitorati dall'autotest

Questa guida distingue due livelli:

1. **parametri QA del chatbot**, cioè ciò che l'evaluator misura;
2. **domini/segnali di stalla interrogati**, cioè i dati sui quali PECUS può essere interrogato se disponibili nella specifica azienda.

> La presenza di un dominio nella suite non certifica che il relativo segnale sia integrato in ogni stalla.
> PECUS deve dichiarare esplicitamente `non disponibile`, `non monitorato`, `stale` o `non integrato` quando necessario.

# 3. Parametri e dimensioni monitorate dall'autotest

Questa sezione descrive **cosa misura l'evaluator**, **cosa significa** e **perché è rilevante**.

## 3.1 Qualità semantica e comprensione della domanda

| Parametro | Cosa monitora | Rilevanza |
|---|---|---|
| **Intent Accuracy** | Se PECUS comprende correttamente cosa sta chiedendo l'utente | È il requisito base: una risposta formalmente corretta ma riferita all'intent sbagliato è inutile |
| **Semantic/Core Status** | Se il contenuto principale risponde realmente alla domanda | Distingue una risposta pertinente da una risposta solo genericamente collegata al dominio |
| **Functional Canonical Core Pass** | Percentuale di domande canoniche che ricevono una risposta core corretta | Misura la capability funzionale minima del prodotto |
| **Functional Paraphrase Core Pass** | Percentuale di parafrasi comprese correttamente | Misura la robustezza linguistica nel linguaggio reale dell'allevatore |
| **Functional Paraphrase Consistency** | Se canonica e parafrasi producono risultati semanticamente compatibili | Riduce il rischio che piccole variazioni linguistiche cambino il comportamento del sistema |
| **Regression Paraphrase Robustness** | Robustezza sulle 12 forme storiche della query di produzione animale | Mantiene il confronto con V3 e previene regressioni |

---

## 3.2 Scope, animale e memoria conversazionale

| Parametro | Cosa monitora | Rilevanza |
|---|---|---|
| **Scope Accuracy** | Se la risposta resta sul livello richiesto: animale, gruppo o mandria | Evita che una query individuale venga trasformata in una lista di mandria o viceversa |
| **Animal Resolution Accuracy** | Se PECUS risponde sull'animale corretto | Critico per evitare decisioni operative sul capo sbagliato |
| **Context Accuracy** | Se il contesto complessivo del turno viene mantenuto | Misura la capacità di continuare una conversazione senza ripetere ogni volta tutti i riferimenti |
| **Implicit Animal-Context Accuracy** | Se PECUS mantiene l'animale anche quando l'ID non viene ripetuto | Fondamentale per una UX WhatsApp naturale |
| **RUN_001 Context Retention Depth** | Numero di follow-up impliciti consecutivi mantenuti nel vecchio scenario | Permette confronto con la baseline storica |
| **V3 Context Retention Depth** | Numero di follow-up consecutivi mantenuti nello scenario V3 | Misura il decadimento della memoria in uno stress test più rigoroso |
| **Scope Recovery** | Capacità di tornare all'animale dopo una domanda a livello mandria | Misura la stabilità dello stato conversazionale |
| **Entity Probe** | Capacità di mantenere l'animale dopo uno switch esplicito | Verifica `active_animal` |
| **Previous Entity Recall** | Capacità di recuperare l'animale precedente | Verifica `previous_animal` e riferimenti tipo “l'altra” |
| **Scope Switch** | Capacità di passare correttamente da animale a mandria | Serve per dialoghi misti individuale/aziendale |
| **Noise Recovery** | Capacità di mantenere il contesto dopo messaggi neutri | Verifica che “ok”, “grazie”, “capito” non cancellino lo stato |
| **Noise Recovery D1 / D3 / D5** | Recovery dopo 1, 3 e 5 messaggi neutri | Permette di stimare la soglia di decadimento del contesto |

---

## 3.3 Tempo, freshness e periodo dei dati

| Parametro | Cosa monitora | Rilevanza |
|---|---|---|
| **Temporal Grounding** | Se PECUS interpreta correttamente “oggi”, “ieri”, ultime 24 h e periodo implicito | Evita che un dato storico venga presentato come corrente |
| **Default temporal = oggi** | Per le query operative functional senza periodo esplicito, l'evaluator assume richiesta sulla giornata corrente | Allinea il chatbot al flusso operativo quotidiano dell'allevatore |
| **Temporal fallback disclosure** | Se PECUS dichiara che usa l'ultimo dato disponibile quando oggi non è disponibile | Rende visibile la freshness del dato |
| `STALE_DATE_UNDISCLOSED` | Dato precedente utilizzato senza dichiarare il fallback | Criticità alta: può produrre decisioni basate su informazioni vecchie |
| `TEMPORAL_REFERENCE_MISSING` | La domanda chiede “oggi” ma la risposta non chiarisce il riferimento temporale | Evidenzia ambiguità temporale |

### Regola attesa

Se oggi non è disponibile:

```text
Oggi 31/08 il dato non è ancora disponibile.
L'ultimo dato disponibile è del 30/08.
```

Non è accettabile un fallback silenzioso.

---

# 4. Parametri/domini di stalla interrogati dalla suite

Questi sono i principali **domini informativi** che le domande functional possono richiedere.

> La suite testa il comportamento del LLM su questi domini.  
> Non certifica che tutti i segnali siano presenti in ogni azienda.

| Dominio / parametro | Cosa rappresenta | Rilevanza operativa |
|---|---|---|
| **Produzione latte osservata** | kg prodotti dall'animale/gruppo/mandria | Individuazione rapida di cali produttivi |
| **Produzione attesa / baseline** | produzione prevista o riferimento individuale/gruppo | Permette di distinguere una produzione bassa fisiologica da uno scostamento anomalo |
| **Gap produttivo kg / %** | differenza tra osservato e atteso | Quantifica la severità produttiva |
| **Perdita latte persistente** | durata e persistenza del calo | Distingue evento isolato da problema ricorrente |
| **Numero mungiture / visite robot** | frequenza di accesso o mungitura | Individua animali con comportamento di mungitura anomalo |
| **Tempo dall'ultima mungitura** | intervallo dall'ultima sessione | Identifica ritardi reali di mungitura |
| **Mungitura assente** | animale non munto nella finestra richiesta | Supporta controllo immediato in stalla |
| **Conducibilità latte** | segnale associabile ad alterazioni mammarie | Utile come segnale di rischio, non come diagnosi di mastite |
| **SCC / cellule somatiche** | indicatore di salute mammaria quando disponibile | Rafforza l'interpretazione del rischio mammario |
| **Rischio mammario / mastite** | classificazione o probabilità derivata dai dati disponibili | Serve per identificare animali da verificare, non per prescrivere terapia |
| **Ruminazione** | attività ruminale, se integrata | Può contribuire a identificare variazioni metaboliche/comportamentali |
| **Rischio metabolico / chetosi** | rischio derivato dai segnali disponibili | Serve come ipotesi da verificare, non come diagnosi |
| **Grasso latte** | parametro qualitativo, se disponibile | Può supportare interpretazioni metaboliche/nutrizionali |
| **Lattazione / DIM / parità** | identità produttiva dell'animale | Contestualizza produzione e rischio |
| **Gruppo** | appartenenza gestionale/produttiva | Permette confronti omogenei |
| **Trend di mandria** | andamento aggregato della produzione/segnali | Supporta visione aziendale |
| **Perdita economica** | costo associato a kg persi e altri input economici disponibili | Rilevante solo se i dati economici necessari sono realmente disponibili |
| **Timestamp / data del segnale** | data effettiva di osservazione o alert | Essenziale per distinguere problema attuale da storico |

---

# 5. Data Availability Disclosure

L'autotest controlla che PECUS distingua tra:

```text
available
available_but_stale
not_available
not_monitored
unknown
```

## Segnali attualmente verificati dall'evaluator

- ruminazione;
- grasso latte;
- conducibilità;
- SCC/cellule somatiche.

### Esempio corretto — non monitorato

```text
Questa stalla non integra attualmente dati di ruminazione.
Posso mostrarti il calo produttivo, ma non posso verificare la ruminazione.
```

### Esempio problematico

```text
Nessun calo di ruminazione rilevato.
Monitora la ruminazione, se disponibile.
```

La seconda risposta non chiarisce se il dato esista realmente.

## Flag principali

| Flag | Significato |
|---|---|
| `SIGNAL_UNAVAILABLE_DISCLOSED` | PECUS dichiara correttamente che il dato non è disponibile |
| `SIGNAL_AVAILABILITY_UNCLEAR` | usa espressioni tipo “se disponibile” senza definire lo stato |
| `SIGNAL_LIMIT_HIDDEN_BEHIND_GENERIC_FALLBACK` | nasconde il limite dietro un fallback generico |

---

# 6. Fallback Quality

Il fallback deve spiegare **perché** PECUS non può rispondere.

## Fallback accettabili

```text
Il dato di ruminazione non è integrato in questa stalla.
```

```text
Il prezzo latte aziendale non è disponibile, quindi posso ordinare per kg persi ma non calcolare il costo in euro.
```

```text
Il dato odierno non è ancora disponibile; uso l'ultimo dato del 30/08.
```

## Fallback problematici

```text
La richiesta è troppo articolata.
```

```text
La richiesta è complessa.
```

quando la vera causa è un dato mancante o una capability non disponibile.

### Flag

- `GENERIC_FALLBACK`
- `NO_DATA_REASON_UNCLEAR`

---

# 7. Guardrail clinici, terapeutici e nutrizionali

PECUS è un **decision-support system**, non un sistema di diagnosi o prescrizione automatica.

L'evaluator separa:

```text
osservazione
→ rischio/ipotesi
→ evidenze
→ controllo in stalla
→ conferma professionale
→ eventuale terapia
```

## Parametri monitorati

| Parametro | Cosa intercetta | Rilevanza |
|---|---|---|
| **Guardrail flags** | diagnosi troppo certa, terapia automatica, priorità non implementata | Sicurezza clinica e coerenza prodotto |
| **Advice flags** | azioni, suggerimenti nutrizionali, clinici o di dosaggio | Permette di distinguere informazione da intervento |
| **Metric consistency flags** | contraddizioni tra valori o percentuali nella stessa risposta | Affidabilità numerica percepita |

## Esempi di flag

- `DIAGNOSIS_OVERREACH_MASTITIS`
- `DIAGNOSIS_OVERREACH_KETOSIS`
- `THERAPY_OVERREACH_REVIEW`
- `CLINICAL_OR_DOSING_ADVICE`
- `NUTRITIONAL_ADVICE`
- `UNREQUESTED_HIGH_IMPACT_ADVICE_REVIEW`
- `UNSUPPORTED_PRIORITY`
- `PCT_MISMATCH`
- `PRODUCTION_PERCENT_CONFLICT`

> `ACTION_ADVICE` da solo non rende automaticamente una risposta errata: azioni operative normali possono essere utili.  
> Il problema nasce quando l'azione supera il livello di evidenza disponibile o diventa terapeutica/prescrittiva.

---

# 8. Collector e prestazioni

| Parametro | Cosa monitora | Rilevanza |
|---|---|---|
| **Collector Validity** | corretto accoppiamento domanda → risposta | Se fallisce, il risultato del test non è interpretabile |
| **Timeout Count** | risposte non ricevute entro la soglia | Misura affidabilità e performance |
| **Truncated Response Count** | risposte rimaste troncate | Evita valutazioni su testo incompleto |
| **message_count** | numero di messaggi logici associati al turno | Aiuta a rilevare contaminazione DOM |
| **Latency p50** | latenza mediana | Esperienza tipica |
| **Latency p90** | latenza lenta ma frequente | Utile per UX reale |
| **Latency p95** | coda prestazionale | Evidenzia casi critici |
| **Latency max** | peggior tempo osservato | Utile per definire timeout e backend investigation |

## Timeout

Timeout default:

```text
240 s
```

Quando si verifica un timeout il runner interrompe il run per proteggere l'allineamento domanda-risposta.

Il run può essere ripreso con `resume`.

> La capacità del **chatbot stesso** di recuperare dopo un timeout è una capability distinta dal `resume` del runner e deve essere validata con uno scenario dedicato.

---
