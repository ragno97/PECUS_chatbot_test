from __future__ import annotations

from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path
import argparse
import csv
import re
import shutil
import statistics
import time

from playwright.sync_api import sync_playwright


# ===================================================================
# PECUS CHAIN — UNIFIED LLM AUTOTEST
# One script, one suite, one stable raw schema.
# ===================================================================

DEFAULT_SUITE = Path("tests/pecus_llm_suite.csv")
DEFAULT_RESULTS_DIR = Path("results")
DEFAULT_ARCHIVE_DIR = Path("results_archive")
DEFAULT_BOT_NAME = "Marica Marches"

DEFAULT_TIMEOUT_SECONDS = 240
QUIET_SECONDS = 6
BETWEEN_QUESTIONS_SECONDS = 5
BETWEEN_AREAS_SECONDS = 8
BETWEEN_SCENARIOS_SECONDS = 8
RESUME_SETTLE_SECONDS = 30


# -------------------------------------------------------------------
# Stable raw schema: NEVER change column order in a running project.
# Add new derived evaluation fields only to evaluated files.
# -------------------------------------------------------------------
RAW_FIELDS = [
    "run_id",
    "run_mode",
    "sequence_no",
    "attempt_no",
    "attempt_uid",
    "test_id",
    "case_id",
    "area",
    "suite_type",
    "scenario",
    "scenario_turn",
    "block",
    "variant_index",
    "variant_type",
    "variant_source",
    "previously_executed",
    "prior_validated",
    "prior_result",
    "source_case_id",
    "source_mapping",
    "question",
    "evaluation_profile",
    "expected_scope",
    "expected_animal",
    "input_data",
    "expected_behavior",
    "expected_fields",
    "fallback",
    "guardrail",
    "support_current",
    "probe_type",
    "response",
    "latency_ms",
    "message_count",
    "response_truncated",
    "message_ids",
    "whatsapp_metadata",
    "send_system_timestamp",
    "system_timestamp",
    "collector_success",
    "collector_note",
]


# ===================================================================
# SHARED HELPERS
# ===================================================================

def normalize_text(value) -> str:
    return re.sub(r"\s+", " ", str(value or "")).strip()


def as_bool(value) -> bool:
    return str(value).strip().lower() in {
        "true", "1", "yes", "y", "si", "sì"
    }


def normalize_animal(value) -> str:
    value = str(value or "").strip()
    if not value:
        return ""
    try:
        return str(int(float(value.replace(",", "."))))
    except Exception:
        return value


def load_csv(path: Path) -> list[dict]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return [
            {
                str(k).strip(): (
                    str(v).strip() if v is not None else ""
                )
                for k, v in row.items()
            }
            for row in csv.DictReader(handle, delimiter=";")
        ]


def write_csv(path: Path, rows: list[dict]) -> None:
    if not rows:
        return

    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=list(rows[0].keys()),
            delimiter=";",
            extrasaction="ignore",
        )
        writer.writeheader()
        writer.writerows(rows)


def append_raw(
    path: Path,
    run_id: str,
    run_mode: str,
    sequence_no: int,
    attempt_no: int,
    test: dict,
    result: dict,
) -> None:
    """
    raw_results.csv is created with the definitive schema from row 1.
    No mixed V1/V2 headers.
    """
    exists = path.exists()

    row = {field: test.get(field, "") for field in RAW_FIELDS}

    row.update(
        {
            "run_id": run_id,
            "run_mode": run_mode,
            "sequence_no": sequence_no,
            "attempt_no": attempt_no,
            "attempt_uid": f"{test['test_id']}_A{attempt_no}",
            "response": result["response"],
            "latency_ms": (
                ""
                if result["latency_ms"] is None
                else result["latency_ms"]
            ),
            "message_count": len(result["messages"]),
            "response_truncated": result["truncated"],
            "message_ids": " | ".join(
                str(m.get("message_id"))
                for m in result["messages"]
            ),
            "whatsapp_metadata": " | ".join(
                str(m.get("metadata"))
                for m in result["messages"]
            ),
            "send_system_timestamp": result["send_timestamp"],
            "system_timestamp": datetime.now().isoformat(
                timespec="seconds"
            ),
            "collector_success": result["success"],
            "collector_note": result["note"],
        }
    )

    with path.open(
        "a",
        encoding="utf-8-sig",
        newline="",
    ) as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=RAW_FIELDS,
            delimiter=";",
            extrasaction="ignore",
        )

        if not exists:
            writer.writeheader()

        writer.writerow(
            {field: row.get(field, "") for field in RAW_FIELDS}
        )


# ===================================================================
# SUITE SELECTION
# ===================================================================

def select_tests(rows: list[dict], mode: str) -> list[dict]:
    if mode == "smoke":
        selected = [
            row
            for row in rows
            if row.get("suite_type") == "functional"
            and row.get("variant_type") == "canonical"
        ]
        return sorted(
            selected,
            key=lambda row: (
                int(row.get("area_order") or 0),
                int(row.get("case_order") or 0),
            ),
        )

    if mode == "functional":
        selected = [
            row
            for row in rows
            if row.get("suite_type") == "functional"
        ]
        return sorted(
            selected,
            key=lambda row: int(
                row.get("execution_order") or 0
            ),
        )

    if mode == "regression":
        selected = [
            row
            for row in rows
            if row.get("suite_type") == "regression"
        ]

        scenario_order = {
            "A_CONTEXT_DECAY": 1,
            "B_SCOPE_RECOVERY": 2,
            "C_ENTITY_SWITCH": 3,
            "D_NOISE_RETENTION": 4,
            "E_PARAPHRASE_PRODUCTION": 5,
        }

        return sorted(
            selected,
            key=lambda row: (
                scenario_order.get(
                    row.get("scenario"),
                    99,
                ),
                int(row.get("scenario_turn") or 0),
            ),
        )

    if mode == "all":
        return (
            select_tests(rows, "functional")
            + select_tests(rows, "regression")
        )

    raise ValueError(f"Mode non supportato: {mode}")


# ===================================================================
# WHATSAPP COLLECTOR
# ===================================================================

def parse_whatsapp_datetime(metadata: str):
    if not metadata:
        return None

    match = re.search(
        r"\[(\d{1,2}):(\d{2}),\s*"
        r"(\d{1,2})/(\d{1,2})/(\d{4})\]",
        metadata,
    )

    if not match:
        return None

    hh, mm, dd, month, year = map(
        int,
        match.groups(),
    )

    return datetime(
        year,
        month,
        dd,
        hh,
        mm,
    )


def message_key(message: dict) -> str:
    if message.get("message_id"):
        return "id:" + str(message["message_id"])

    return (
        "fallback:"
        + str(message.get("metadata"))
        + "|"
        + normalize_text(message.get("text"))[:250]
    )


def get_bot_messages(page, bot_name: str) -> list[dict]:
    locator = page.locator(
        f'[data-pre-plain-text*="{bot_name}:"]'
    )

    messages = []

    for index in range(locator.count()):
        element = locator.nth(index)

        try:
            text = element.inner_text().strip()
            metadata = element.get_attribute(
                "data-pre-plain-text"
            )

            ancestor = element.locator(
                "xpath=ancestor::*[@data-id][1]"
            )

            message_id = None

            if ancestor.count() > 0:
                message_id = ancestor.get_attribute(
                    "data-id"
                )

            if text:
                messages.append(
                    {
                        "message_id": message_id,
                        "metadata": metadata,
                        "message_dt": (
                            parse_whatsapp_datetime(metadata)
                        ),
                        "text": text,
                        "dom_index": index,
                    }
                )

        except Exception:
            pass

    # DOM duplication handling.
    deduped = {}

    for message in messages:
        content_key = (
            message["metadata"],
            normalize_text(message["text"])[:220],
        )

        if content_key not in deduped:
            deduped[content_key] = message
            continue

        existing = deduped[content_key]

        if (
            message.get("message_id")
            and not existing.get("message_id")
        ):
            existing["message_id"] = message["message_id"]

        if len(message["text"]) > len(existing["text"]):
            existing["text"] = message["text"]

    return list(deduped.values())


def expand_message_by_id(page, message_id) -> bool:
    if not message_id:
        return False

    try:
        node = page.locator(
            f'[data-id="{message_id}"]'
        )

        if node.count() == 0:
            return False

        more = node.get_by_text(
            "Leggi di più",
            exact=True,
        )

        if more.count() > 0:
            more.last.click(timeout=3000)
            page.wait_for_timeout(800)
            return True

    except Exception:
        pass

    return False


def qualifying_messages(
    page,
    bot_name: str,
    known_keys: set[str],
    send_minute: datetime,
) -> list[dict]:
    candidates = []

    for message in get_bot_messages(
        page,
        bot_name,
    ):
        if message_key(message) in known_keys:
            continue

        message_dt = message.get("message_dt")

        # Reject old WhatsApp DOM elements reappearing later.
        if (
            message_dt is not None
            and message_dt < send_minute
        ):
            continue

        candidates.append(message)

    return sorted(
        candidates,
        key=lambda message: (
            message.get("message_dt") or send_minute,
            message.get("dom_index", 0),
        ),
    )


def collect_one_turn(
    page,
    message_box,
    bot_name: str,
    test: dict,
    known_keys: set[str],
    timeout_seconds: int,
) -> dict:
    for message in get_bot_messages(
        page,
        bot_name,
    ):
        known_keys.add(message_key(message))

    send_dt = datetime.now()
    send_minute = send_dt.replace(
        second=0,
        microsecond=0,
    )
    start = time.monotonic()

    print()
    print("=" * 86)
    print(
        f"{test.get('area')} | "
        f"{test.get('case_id')} | "
        f"{test.get('variant_type')} | "
        f"{test.get('test_id')}"
    )
    print(
        "Profilo:",
        test.get("evaluation_profile"),
    )
    print(
        "Domanda:",
        test.get("question"),
    )
    print("=" * 86)

    message_box.click()
    message_box.fill(test["question"])
    message_box.press("Enter")

    print(
        f"Messaggio inviato. "
        f"Timeout={timeout_seconds}s"
    )

    deadline = time.monotonic() + timeout_seconds
    first_detection = None
    collected = {}

    while time.monotonic() < deadline:
        current = qualifying_messages(
            page,
            bot_name,
            known_keys,
            send_minute,
        )

        if current:
            first_detection = time.monotonic()

            for message in current:
                collected[message_key(message)] = message

            break

        page.wait_for_timeout(500)

    if not collected:
        return {
            "response": "",
            "latency_ms": None,
            "messages": [],
            "truncated": False,
            "success": False,
            "note": "TIMEOUT_ABORT_RUN",
            "send_timestamp": send_dt.isoformat(
                timespec="seconds"
            ),
        }

    latency_ms = int(
        (first_detection - start) * 1000
    )

    print(
        "Prima risposta:",
        latency_ms,
        "ms",
    )

    # Give WhatsApp time to stabilize message IDs.
    page.wait_for_timeout(1200)

    for message in qualifying_messages(
        page,
        bot_name,
        known_keys,
        send_minute,
    ):
        collected[message_key(message)] = message

    for message in list(collected.values()):
        expand_message_by_id(
            page,
            message.get("message_id"),
        )

    last_change = time.monotonic()
    previous_keys = set(collected)

    while True:
        page.wait_for_timeout(500)

        current = {
            message_key(message): message
            for message in qualifying_messages(
                page,
                bot_name,
                known_keys,
                send_minute,
            )
        }

        current_keys = set(current)

        if current_keys != previous_keys:
            previous_keys = current_keys
            last_change = time.monotonic()

        collected.update(current)

        if (
            time.monotonic() - last_change
            >= QUIET_SECONDS
        ):
            break

    logical = {}

    for message in collected.values():
        content_key = (
            message["metadata"],
            normalize_text(message["text"])[:220],
        )

        if content_key not in logical:
            logical[content_key] = message
            continue

        existing = logical[content_key]

        if (
            message.get("message_id")
            and not existing.get("message_id")
        ):
            existing["message_id"] = (
                message["message_id"]
            )

        if len(message["text"]) > len(existing["text"]):
            existing["text"] = message["text"]

    final_messages = sorted(
        logical.values(),
        key=lambda message: (
            message.get("message_dt") or send_minute,
            message.get("dom_index", 0),
        ),
    )

    response = "\n\n".join(
        message["text"].strip()
        for message in final_messages
    )

    truncated = "Leggi di più" in response
    success = bool(response.strip())

    for message in final_messages:
        known_keys.add(message_key(message))

    print()
    print("--- RISPOSTA PECUS ---")
    print(response)
    print("-----------------------")
    print(
        "Messaggi logici:",
        len(final_messages),
    )
    print(
        "Troncata:",
        truncated,
    )

    return {
        "response": response,
        "latency_ms": latency_ms,
        "messages": final_messages,
        "truncated": truncated,
        "success": success,
        "note": (
            "OK"
            if success
            else "EMPTY_FINAL_RESPONSE"
        ),
        "send_timestamp": send_dt.isoformat(
            timespec="seconds"
        ),
    }


# ===================================================================
# EVALUATOR
# ===================================================================

NO_DATA_PATTERNS = (
    r"nessun[a-z]*\s+(?:dato|registrazione|lettura|valore|animale|vacca|bufala)",
    r"non\s+(?:è|e)\s+(?:presente|disponibile|registrat|aggiornat)",
    r"non\s+risulta",
    r"dati?\s+(?:non|mancant)",
    r"mancano?\s+",
    r"non\s+ho\s+(?:il|i)\s+dat",
    r"non\s+posso\s+(?:calcolare|valutare|determinare|rispondere)",
    r"impossibile\s+(?:calcolare|valutare|determinare)",
    r"query\s+ha\s+restituito\s+0",
    r"\b0\s+(?:vacche|bufale|animali|capi|righe|risultati)\b",
)

NONE_FOUND_PATTERNS = (
    r"nessun[a-z]*\s+(?:animale|vacca|bufala|caso|segnale)",
    r"non\s+ci\s+sono",
    r"non\s+risulta\s+alcun",
    r"\b0\s+(?:vacche|bufale|animali|capi|casi)\b",
)

HERD_TERMS = (
    "mandria",
    "stalla",
    "le vacche",
    "le bufale",
    "gli animali",
    "i capi",
    "produzione totale",
    "media aziendale",
    "media della stalla",
)

GROUP_TERMS = (
    "gruppo",
    "fresche",
    "primipare",
    "prima lattazione",
    "l1",
)


def match_any(text: str, patterns) -> bool:
    return any(
        re.search(
            pattern,
            text,
            flags=re.I | re.S,
        )
        for pattern in patterns
    )


def is_no_data(text: str) -> bool:
    return match_any(
        text,
        NO_DATA_PATTERNS,
    )


def is_none_found(text: str) -> bool:
    return match_any(
        text,
        NONE_FOUND_PATTERNS,
    )


def extract_animals(text: str) -> list[str]:
    animals = set()

    for pattern in (
        r"#\s*(\d{2,6})\b",
        r"\b(?:bufala|bovina|vacca|animale)"
        r"\s+#?(\d{2,6})\b",
        r"^\s*#?(\d{2,6})\b",
    ):
        for match in re.finditer(
            pattern,
            str(text),
            flags=re.I | re.M,
        ):
            value = int(match.group(1))

            if 10 <= value <= 999999:
                animals.add(str(value))

    return sorted(
        animals,
        key=int,
    )


def response_class(text: str) -> str:
    if is_no_data(text):
        return "no_data"

    if is_none_found(text):
        return "none_found"

    if (
        extract_animals(text)
        or re.search(
            r"\b\d+(?:[.,]\d+)?\s*"
            r"(?:kg|%|ore|h|€|euro)\b",
            text,
            flags=re.I,
        )
    ):
        return "results"

    return "narrative"


def semantic_status(
    profile: str,
    response: str,
) -> str:
    text = normalize_text(response)

    if profile == "acknowledgement":
        return "N/A"

    if profile in {
        "low_milking_yield_list",
        "low_production_list",
    }:
        return (
            "PASS"
            if (
                re.search(
                    r"produ|latte|\bkg\b",
                    text,
                    flags=re.I,
                )
                and (
                    extract_animals(text)
                    or is_no_data(text)
                    or is_none_found(text)
                )
            )
            else "REVIEW"
        )

    if profile == "missed_or_reduced_milkings":
        domain = re.search(
            r"mungitur|session|visite|robot|registrat",
            text,
            flags=re.I,
        )
        condition = re.search(
            r"salt|mancant|non hanno registrato|"
            r"zero|\b0\b|meno|ridott",
            text,
            flags=re.I,
        )

        if domain and condition:
            return "PASS"

        return (
            "PASS"
            if is_no_data(text)
            else "REVIEW"
        )

    if profile == "milking_delay_list":
        direct = re.search(
            r"ore\s+da\s+(?:ultima\s+)?mungitur|"
            r"ultima\s+mungitur.{0,40}(?:ore|h)|"
            r"ritard.{0,30}(?:mungitur|robot)|"
            r"intervallo.{0,30}mungitur",
            text,
            flags=re.I | re.S,
        )

        fallback = (
            is_no_data(text)
            and re.search(
                r"mungitur|robot|intervallo",
                text,
                flags=re.I,
            )
        )

        return (
            "PASS"
            if direct or fallback
            else "FAIL"
        )

    if profile == "low_milking_count":
        has_count = re.search(
            r"\b\d+(?:[.,]\d+)?\s+"
            r"(?:mungitur|visite|session)",
            text,
            flags=re.I,
        )

        comparative = re.search(
            r"meno|inferior|sotto|ridott|baseline|"
            r"solit|delta\s*[-−]",
            text,
            flags=re.I,
        )

        if is_no_data(text):
            return "PASS"

        if has_count and comparative:
            return "PASS"

        if (
            has_count
            and re.search(
                r"pari alla media",
                text,
                flags=re.I,
            )
        ):
            return "FAIL"

        return "REVIEW"

    if profile == "not_milked_today":
        if is_no_data(text):
            return "PASS"

        return (
            "PASS"
            if re.search(
                r"non.{0,20}munt|"
                r"0.{0,20}(?:mungitur|visite)",
                text,
                flags=re.I | re.S,
            )
            else "REVIEW"
        )

    if profile == "conductivity_list":
        return (
            "PASS"
            if (
                re.search(
                    r"conducibil",
                    text,
                    flags=re.I,
                )
                and (
                    extract_animals(text)
                    or is_none_found(text)
                    or is_no_data(text)
                )
            )
            else "REVIEW"
        )

    if profile == "primiparous_low_robot":
        return (
            "PASS"
            if (
                re.search(
                    r"primipar|\bP1\b|prima lattaz",
                    text,
                    flags=re.I,
                )
                and re.search(
                    r"robot|visite|mungitur",
                    text,
                    flags=re.I,
                )
            )
            else "REVIEW"
        )

    if profile == "production_drop_list":
        if (
            is_no_data(text)
            and re.search(
                r"calo|produ|latte",
                text,
                flags=re.I,
            )
        ):
            return "PASS"

        return (
            "PASS"
            if (
                re.search(
                    r"calo|scost|perdit|sotto",
                    text,
                    flags=re.I,
                )
                and re.search(
                    r"produ|latte|\bkg\b",
                    text,
                    flags=re.I,
                )
            )
            else "REVIEW"
        )

    if profile == "production_drop_threshold":
        return (
            "PASS"
            if (
                re.search(
                    r"calo|perdit|residuo",
                    text,
                    flags=re.I,
                )
                and re.search(
                    r"\b5\s*kg\b|>\s*5|≥\s*5|-\s*5",
                    text,
                    flags=re.I,
                )
            )
            else "REVIEW"
        )

    if profile == "low_vs_group":
        return (
            "PASS"
            if (
                re.search(
                    r"produ|latte",
                    text,
                    flags=re.I,
                )
                and re.search(
                    r"grupp|media",
                    text,
                    flags=re.I,
                )
            )
            else "FAIL"
        )

    if profile == "group_production_drop":
        return (
            "PASS"
            if (
                re.search(
                    r"grupp|fresch|parit",
                    text,
                    flags=re.I,
                )
                and re.search(
                    r"produ|latte|residuo",
                    text,
                    flags=re.I,
                )
                and re.search(
                    r"calo|scost|sotto|negativ",
                    text,
                    flags=re.I,
                )
            )
            else "REVIEW"
        )

    if profile == "production_drop_reason":
        return (
            "PASS"
            if (
                re.search(
                    r"produ|latte|calo|perdit",
                    text,
                    flags=re.I,
                )
                and re.search(
                    r"causa|rischio|stress|mammar|rumin|"
                    r"THI|probabil",
                    text,
                    flags=re.I,
                )
            )
            else "REVIEW"
        )

    if profile == "economic_loss_list":
        if (
            is_no_data(text)
            and re.search(
                r"prezzo|euro|€|econom|cost",
                text,
                flags=re.I,
            )
        ):
            return "PASS"

        return (
            "PASS"
            if re.search(
                r"€|euro|cost|perdit.{0,20}econom",
                text,
                flags=re.I | re.S,
            )
            else "REVIEW"
        )

    if profile == "persistent_milk_loss":
        return (
            "PASS"
            if (
                re.search(
                    r"giorn|persist|continu",
                    text,
                    flags=re.I,
                )
                and re.search(
                    r"calo|perdit|produ",
                    text,
                    flags=re.I,
                )
            )
            else "REVIEW"
        )

    if profile in {
        "mammary_signal_list",
        "mammary_reason",
        "persistent_mammary_signal",
    }:
        return (
            "PASS"
            if (
                re.search(
                    r"mammar|conducibil|SCC|cellul|mastite",
                    text,
                    flags=re.I,
                )
                and (
                    extract_animals(text)
                    or is_no_data(text)
                    or is_none_found(text)
                )
            )
            else "REVIEW"
        )

    if profile == "possible_ketosis_list":
        return (
            "PASS"
            if (
                re.search(
                    r"chetosi|metabol|BHB",
                    text,
                    flags=re.I,
                )
                and (
                    extract_animals(text)
                    or is_no_data(text)
                    or is_none_found(text)
                )
            )
            else "REVIEW"
        )

    if profile == "milk_rumination_drop":
        return (
            "PASS"
            if (
                re.search(
                    r"rumin",
                    text,
                    flags=re.I,
                )
                and re.search(
                    r"latte|produ",
                    text,
                    flags=re.I,
                )
            )
            else "REVIEW"
        )

    if profile == "rumination_animal":
        return (
            "PASS"
            if re.search(
                r"rumin",
                text,
                flags=re.I,
            )
            else "REVIEW"
        )

    if profile == "high_milk_fat":
        return (
            "PASS"
            if re.search(
                r"grasso|fat",
                text,
                flags=re.I,
            )
            else "REVIEW"
        )

    if profile == "lactation_status":
        return (
            "PASS"
            if re.search(
                r"lattaz|DIM|status|attiv",
                text,
                flags=re.I,
            )
            else "REVIEW"
        )

    if profile == "animal_profile":
        return (
            "PASS"
            if re.search(
                r"DIM|lattaz|parit|produ|latte|rischio|segnal",
                text,
                flags=re.I,
            )
            else "REVIEW"
        )

    if profile == "herd_status":
        return (
            "PASS"
            if (
                re.search(
                    r"stalla|mandria|animali|bufale|vacche",
                    text,
                    flags=re.I,
                )
                and re.search(
                    r"produ|latte|segnal|rischio|casi|\bkg\b",
                    text,
                    flags=re.I,
                )
            )
            else "REVIEW"
        )

    if profile == "herd_production_trend":
        return (
            "PASS"
            if (
                re.search(
                    r"produ|latte",
                    text,
                    flags=re.I,
                )
                and re.search(
                    r"trend|calo|andamento|mese|anno|"
                    r"baseline|media|scost",
                    text,
                    flags=re.I,
                )
            )
            else "REVIEW"
        )

    if profile == "group_status":
        return (
            "PASS"
            if (
                re.search(
                    r"fresch|grupp",
                    text,
                    flags=re.I,
                )
                and re.search(
                    r"produ|latte|DIM|media|calo|andamento",
                    text,
                    flags=re.I,
                )
            )
            else "REVIEW"
        )

    # Regression profiles.
    if profile == "daily_milk_yield":
        return (
            "PASS"
            if (
                re.search(
                    r"\b\d+(?:[.,]\d+)?\s*kg\b",
                    text,
                    flags=re.I,
                )
                or is_no_data(text)
            )
            else "FAIL"
        )

    if profile == "previous_milk_yield":
        return (
            "PASS"
            if re.search(
                r"ieri|giorno precedente|\bkg\b",
                text,
                flags=re.I,
            )
            else "REVIEW"
        )

    if profile == "risk":
        return (
            "PASS"
            if re.search(
                r"rischio|probabil|stress|mastite|"
                r"chetosi|segnal",
                text,
                flags=re.I,
            )
            else "FAIL"
        )

    if profile == "risk_reason":
        return (
            "PASS"
            if re.search(
                r"causa|deriv|dovut|stress|temperatur|"
                r"umidit|mammar|metabol",
                text,
                flags=re.I,
            )
            else "REVIEW"
        )

    if profile == "risk_signals":
        return (
            "PASS"
            if re.search(
                r"segnal|THI|calo|conducibil|SCC|"
                r"rumin|scost|residuo",
                text,
                flags=re.I,
            )
            else "REVIEW"
        )

    if profile == "milk_loss":
        return (
            "PASS"
            if (
                re.search(
                    r"perdit|pers|mancan",
                    text,
                    flags=re.I,
                )
                and re.search(
                    r"\bkg\b|latte|produ",
                    text,
                    flags=re.I,
                )
            )
            else "FAIL"
        )

    if profile == "production_vs_expected":
        return (
            "PASS"
            if re.search(
                r"attes|baseline|previst|scost|residuo|curva",
                text,
                flags=re.I,
            )
            else "FAIL"
        )

    if profile == "production_trend":
        return (
            "PASS"
            if re.search(
                r"trend|andamento|giorn|aument|dimin|"
                r"stabile|produ|latte",
                text,
                flags=re.I,
            )
            else "REVIEW"
        )

    if profile == "herd_risk":
        return (
            "PASS"
            if re.search(
                r"rischio|segnal|probabil|stress|"
                r"mastite|chetosi",
                text,
                flags=re.I,
            )
            else "FAIL"
        )

    if profile == "herd_similar":
        return (
            "PASS"
            if re.search(
                r"perdit|simil|scost|\bkg\b|calo",
                text,
                flags=re.I,
            )
            else "FAIL"
        )

    return "REVIEW"


def evaluate_scope_and_animal(
    row: dict,
    response: str,
    semantic: str,
):
    expected_scope = str(
        row.get("expected_scope", "")
    ).lower()

    expected_animal = normalize_animal(
        row.get("expected_animal", "")
    )

    animals = extract_animals(response)
    low = response.lower()

    if expected_scope == "neutral":
        return (
            "N/A",
            "N/A",
            "neutral",
            [],
        )

    if expected_scope == "herd":
        if (
            animals
            or is_no_data(response)
            or is_none_found(response)
            or any(
                term in low
                for term in HERD_TERMS
            )
            or semantic == "PASS"
        ):
            return (
                "PASS",
                "N/A",
                "herd_query",
                [],
            )

        return (
            "REVIEW",
            "N/A",
            "unclear",
            ["HERD_SCOPE_UNCLEAR"],
        )

    if expected_scope == "group":
        if (
            any(
                term in low
                for term in GROUP_TERMS
            )
            or is_no_data(response)
        ):
            return (
                "PASS",
                "N/A",
                "group",
                [],
            )

        return (
            (
                "REVIEW"
                if semantic == "PASS"
                else "FAIL"
            ),
            "N/A",
            "unclear",
            ["GROUP_SCOPE_UNCLEAR"],
        )

    # Expected animal scope.
    if len(animals) >= 2:
        return (
            "FAIL",
            (
                "PASS_MIXED"
                if expected_animal in animals
                else "FAIL"
            ),
            "herd",
            ["CONTEXT_SCOPE_DRIFT"],
        )

    if len(animals) == 1:
        if (
            not expected_animal
            or animals[0] == expected_animal
        ):
            return (
                "PASS",
                "PASS_EXPLICIT",
                "animal",
                [],
            )

        return (
            "FAIL",
            "FAIL",
            "animal",
            ["WRONG_ANIMAL"],
        )

    if re.search(
        r"quale\s+(?:bufala|vacca|animale)|"
        r"indica(?:mi|re)?\s+(?:il\s+)?numero|"
        r"animal_number|"
        r"ho bisogno di sapere a quale",
        response,
        flags=re.I,
    ):
        return (
            "FAIL",
            "FAIL_UNRESOLVED",
            "unclear",
            ["CONTEXT_ENTITY_LOSS"],
        )

    if any(
        term in low
        for term in HERD_TERMS
    ):
        return (
            "FAIL",
            "FAIL_SCOPE",
            "herd",
            ["CONTEXT_SCOPE_DRIFT"],
        )

    if (
        semantic == "PASS"
        or is_no_data(response)
    ):
        return (
            "PASS",
            "PASS_IMPLICIT",
            "animal_implicit",
            [],
        )

    return (
        "REVIEW",
        "REVIEW",
        "unclear",
        ["ENTITY_UNRESOLVED_IN_TEXT"],
    )


def guardrail_flags(
    row: dict,
    response: str,
) -> list[str]:
    flags = []

    low = response.lower()
    area = str(row.get("area", "")).upper()
    profile = str(
        row.get("evaluation_profile", "")
    )

    uncertainty = re.search(
        r"rischio|probabil|possib|potrebbe|compatib|"
        r"sospett|segnal|da verificare|ipotesi",
        low,
        flags=re.I,
    )

    if (
        area == "MASTITE"
        or profile.startswith("mammary")
    ):
        definitive = re.search(
            r"\b(?:ha|hanno|presenta|presentano)"
            r"\s+(?:una\s+)?mastite\b|"
            r"\bmastite confermata\b",
            low,
            flags=re.I,
        )

        if definitive and not uncertainty:
            flags.append(
                "DIAGNOSIS_OVERREACH_MASTITIS"
            )

    if (
        area == "METABOLICO"
        or profile == "possible_ketosis_list"
    ):
        definitive = re.search(
            r"\b(?:ha|hanno|presenta|presentano|"
            r"è in|sono in)\s+chetosi\b|"
            r"\bchetosi confermata\b",
            low,
            flags=re.I,
        )

        if definitive and not uncertainty:
            flags.append(
                "DIAGNOSIS_OVERREACH_KETOSIS"
            )

    if re.search(
        r"\bantibiotic|terapia antibiot|"
        r"terapia intramamm|antinfiammator",
        low,
        flags=re.I,
    ):
        flags.append(
            "THERAPY_OVERREACH_REVIEW"
        )

    if re.search(
        r"\bpriorit[aà]\s+(?:alta|media|bassa)\b|"
        r"\bscore\s+di\s+priorit[aà]\b",
        low,
        flags=re.I,
    ):
        flags.append(
            "UNSUPPORTED_PRIORITY"
        )

    if re.search(
        r"vitamin[ae]\s+[ae]|selenio|zinco|"
        r"densit[aà]\s+energetica|"
        r"aumentare.{0,30}concentrat|"
        r"ridurre.{0,30}concentrat",
        low,
        flags=re.I,
    ):
        flags.append(
            "NUTRITIONAL_PRESCRIPTION_REVIEW"
        )

    return flags


def collector_status(row: dict):
    flags = []

    response = str(
        row.get("response", "")
    ).strip()

    if not as_bool(
        row.get("collector_success", False)
    ):
        flags.append(
            "COLLECTOR_FAILURE"
        )

    try:
        message_count = int(
            float(
                row.get(
                    "message_count",
                    0,
                )
                or 0
            )
        )
    except Exception:
        message_count = 0

    if not response or message_count == 0:
        flags.append(
            "EMPTY_RESPONSE"
        )

    if as_bool(
        row.get(
            "response_truncated",
            False,
        )
    ):
        flags.append(
            "TRUNCATED_RESPONSE"
        )

    if message_count not in {0, 1}:
        flags.append(
            "MESSAGE_COUNT_NOT_ONE"
        )

    return (
        (
            "PASS"
            if not flags
            else "FAIL"
        ),
        flags,
    )


def evaluate_attempt(row: dict) -> dict:
    response = str(
        row.get("response", "")
        or ""
    )

    collector, collector_flags = (
        collector_status(row)
    )

    if collector != "PASS":
        result = dict(row)

        result.update(
            {
                "collector_status": collector,
                "semantic_status": "N/A",
                "scope_status": "N/A",
                "animal_status": "N/A",
                "detected_scope": "N/A",
                "detected_animals": "",
                "response_class": response_class(
                    response
                ),
                "guardrail_flags": "",
                "core_status": "INVALID_COLLECTOR",
                "overall_status": "INVALID_COLLECTOR",
                "error_flags": "|".join(
                    collector_flags
                ),
            }
        )

        return result

    semantic = semantic_status(
        row.get(
            "evaluation_profile",
            "",
        ),
        response,
    )

    (
        scope,
        animal,
        detected_scope,
        scope_flags,
    ) = evaluate_scope_and_animal(
        row,
        response,
        semantic,
    )

    guardrails = guardrail_flags(
        row,
        response,
    )

    if (
        semantic == "FAIL"
        or scope == "FAIL"
        or str(animal).startswith("FAIL")
    ):
        core_status = "FAIL"

    elif (
        semantic == "REVIEW"
        or scope == "REVIEW"
        or animal == "REVIEW"
    ):
        core_status = "REVIEW"

    else:
        core_status = "PASS"

    hard_guardrail = any(
        flag
        in {
            "DIAGNOSIS_OVERREACH_MASTITIS",
            "DIAGNOSIS_OVERREACH_KETOSIS",
            "UNSUPPORTED_PRIORITY",
        }
        for flag in guardrails
    )

    if (
        core_status == "FAIL"
        or hard_guardrail
    ):
        overall = "FAIL"

    elif (
        core_status == "REVIEW"
        or guardrails
    ):
        overall = "REVIEW"

    else:
        overall = "PASS"

    result = dict(row)

    result.update(
        {
            "collector_status": collector,
            "semantic_status": semantic,
            "scope_status": scope,
            "animal_status": animal,
            "detected_scope": detected_scope,
            "detected_animals": ",".join(
                extract_animals(response)
            ),
            "response_class": response_class(
                response
            ),
            "guardrail_flags": "|".join(
                guardrails
            ),
            "core_status": core_status,
            "overall_status": overall,
            "error_flags": "|".join(
                scope_flags
                + collector_flags
            ),
        }
    )

    return result


def choose_final_attempt(
    evaluated_attempts: list[dict],
) -> list[dict]:
    grouped = defaultdict(list)

    for row in evaluated_attempts:
        grouped[row["test_id"]].append(row)

    final = []

    for test_id, rows in grouped.items():
        rows = sorted(
            rows,
            key=lambda row: int(
                row.get("attempt_no") or 1
            ),
        )

        valid = [
            row
            for row in rows
            if row["collector_status"] == "PASS"
        ]

        chosen = (
            valid[-1]
            if valid
            else rows[-1]
        )

        result = dict(chosen)

        result["attempts_total"] = len(rows)
        result["chosen_attempt_no"] = (
            chosen.get("attempt_no")
            or "1"
        )

        final.append(result)

    return sorted(
        final,
        key=lambda row: int(
            row.get("sequence_no") or 999999
        ),
    )


def paraphrase_consistency(
    rows: list[dict],
) -> list[dict]:
    output = []
    grouped = defaultdict(list)

    for row in rows:
        if row.get("suite_type") == "functional":
            grouped[row["case_id"]].append(row)

    for case_id, case_rows in grouped.items():
        case_rows = sorted(
            case_rows,
            key=lambda row: int(
                row.get("variant_index") or 0
            ),
        )

        canonical = next(
            (
                row
                for row in case_rows
                if row.get("variant_type")
                == "canonical"
            ),
            case_rows[0],
        )

        canonical_class = canonical[
            "response_class"
        ]
        canonical_animals = set(
            filter(
                None,
                canonical[
                    "detected_animals"
                ].split(","),
            )
        )

        for row in case_rows:
            if row is canonical:
                status = "BASELINE"
                jaccard = ""
            else:
                class_match = (
                    row["response_class"]
                    == canonical_class
                )

                row_animals = set(
                    filter(
                        None,
                        row[
                            "detected_animals"
                        ].split(","),
                    )
                )

                if (
                    canonical_animals
                    or row_animals
                ):
                    jaccard_value = (
                        len(
                            canonical_animals
                            & row_animals
                        )
                        / len(
                            canonical_animals
                            | row_animals
                        )
                    )
                    jaccard = round(
                        jaccard_value,
                        3,
                    )
                else:
                    jaccard_value = None
                    jaccard = ""

                if not class_match:
                    status = "FAIL"

                elif (
                    jaccard_value is not None
                    and jaccard_value < 0.5
                ):
                    status = "FAIL"

                elif (
                    jaccard_value is not None
                    and jaccard_value < 0.8
                ):
                    status = "REVIEW"

                else:
                    status = "PASS"

            output.append(
                {
                    "case_id": case_id,
                    "area": row.get(
                        "area",
                        "",
                    ),
                    "test_id": row.get(
                        "test_id",
                        "",
                    ),
                    "variant_type": row.get(
                        "variant_type",
                        "",
                    ),
                    "canonical_test_id": canonical.get(
                        "test_id",
                        "",
                    ),
                    "canonical_class": canonical_class,
                    "response_class": row[
                        "response_class"
                    ],
                    "animal_jaccard": jaccard,
                    "consistency_status": status,
                }
            )

    return output


def build_area_summary(
    rows: list[dict],
) -> list[dict]:
    output = []

    areas = []

    for row in rows:
        area = row.get("area", "")

        if area not in areas:
            areas.append(area)

    for area in areas:
        subset = [
            row
            for row in rows
            if row.get("area") == area
        ]

        output.append(
            {
                "area": area,
                "tests": len(subset),
                "collector_valid": sum(
                    row["collector_status"] == "PASS"
                    for row in subset
                ),
                "core_pass": sum(
                    row["core_status"] == "PASS"
                    for row in subset
                ),
                "core_review": sum(
                    row["core_status"] == "REVIEW"
                    for row in subset
                ),
                "core_fail": sum(
                    row["core_status"] == "FAIL"
                    for row in subset
                ),
                "overall_pass": sum(
                    row["overall_status"] == "PASS"
                    for row in subset
                ),
                "overall_review": sum(
                    row["overall_status"] == "REVIEW"
                    for row in subset
                ),
                "overall_fail": sum(
                    row["overall_status"] == "FAIL"
                    for row in subset
                ),
                "invalid_collector": sum(
                    row["overall_status"]
                    == "INVALID_COLLECTOR"
                    for row in subset
                ),
            }
        )

    return output


def evaluate_run(run_dir: Path) -> dict:
    raw_path = run_dir / "raw_results.csv"

    if not raw_path.exists():
        raise SystemExit(
            f"Raw non trovato: {raw_path}"
        )

    raw_rows = load_csv(raw_path)

    if not raw_rows:
        raise SystemExit(
            "raw_results.csv vuoto."
        )

    evaluated_attempts = [
        evaluate_attempt(row)
        for row in raw_rows
    ]

    final_results = choose_final_attempt(
        evaluated_attempts
    )

    consistency = paraphrase_consistency(
        final_results
    )

    area_summary = build_area_summary(
        final_results
    )

    write_csv(
        run_dir / "evaluated_attempts.csv",
        evaluated_attempts,
    )
    write_csv(
        run_dir / "evaluated_results.csv",
        final_results,
    )
    write_csv(
        run_dir / "paraphrase_consistency.csv",
        consistency,
    )
    write_csv(
        run_dir / "area_summary.csv",
        area_summary,
    )

    core_counts = Counter(
        row["core_status"]
        for row in final_results
    )

    overall_counts = Counter(
        row["overall_status"]
        for row in final_results
    )

    latencies = []

    for row in final_results:
        try:
            if row.get("latency_ms"):
                latencies.append(
                    float(row["latency_ms"])
                )
        except Exception:
            pass

    lines = [
        "PECUS CHAIN — UNIFIED AUTOTEST SUMMARY",
        "=" * 60,
        f"Run ID: {final_results[0].get('run_id', '')}",
        f"Mode: {final_results[0].get('run_mode', '')}",
        f"Test finali: {len(final_results)}",
        "",
        "CORE",
        "-" * 60,
        f"PASS: {core_counts['PASS']}",
        f"REVIEW: {core_counts['REVIEW']}",
        f"FAIL: {core_counts['FAIL']}",
        f"INVALID_COLLECTOR: {core_counts['INVALID_COLLECTOR']}",
        "",
        "OVERALL",
        "-" * 60,
        f"PASS: {overall_counts['PASS']}",
        f"REVIEW: {overall_counts['REVIEW']}",
        f"FAIL: {overall_counts['FAIL']}",
        f"INVALID_COLLECTOR: {overall_counts['INVALID_COLLECTOR']}",
        "",
        "AREA SUMMARY",
        "-" * 60,
    ]

    for area in area_summary:
        lines.append(
            f"{area['area']}: "
            f"core PASS={area['core_pass']} "
            f"REVIEW={area['core_review']} "
            f"FAIL={area['core_fail']} | "
            f"overall PASS={area['overall_pass']} "
            f"REVIEW={area['overall_review']} "
            f"FAIL={area['overall_fail']} | "
            f"invalid={area['invalid_collector']}"
        )

    if latencies:
        lines += [
            "",
            "LATENCY",
            "-" * 60,
            f"min_ms: {min(latencies):.0f}",
            f"median_ms: {statistics.median(latencies):.0f}",
            f"mean_ms: {statistics.mean(latencies):.0f}",
            f"max_ms: {max(latencies):.0f}",
        ]

    lines += [
        "",
        "NON-PASS / FLAGS",
        "-" * 60,
    ]

    for row in final_results:
        if (
            row["overall_status"] != "PASS"
            or row.get("guardrail_flags")
        ):
            lines.append(
                f"{row['test_id']} | "
                f"core={row['core_status']} "
                f"overall={row['overall_status']} | "
                f"semantic={row['semantic_status']} | "
                f"scope={row['scope_status']} | "
                f"animal={row['animal_status']} | "
                f"guardrail={row.get('guardrail_flags', '')} | "
                f"errors={row.get('error_flags', '')} | "
                f"Q={row.get('question', '')}"
            )

    summary_path = run_dir / "summary.txt"

    summary_path.write_text(
        "\n".join(lines) + "\n",
        encoding="utf-8",
    )

    return {
        "raw": raw_path,
        "evaluated_attempts": (
            run_dir / "evaluated_attempts.csv"
        ),
        "evaluated_results": (
            run_dir / "evaluated_results.csv"
        ),
        "paraphrase_consistency": (
            run_dir / "paraphrase_consistency.csv"
        ),
        "area_summary": (
            run_dir / "area_summary.csv"
        ),
        "summary": summary_path,
        "core_counts": core_counts,
        "overall_counts": overall_counts,
    }


# ===================================================================
# RUN / RESUME
# ===================================================================

def create_manifest(
    run_dir: Path,
    run_id: str,
    mode: str,
    suite_path: Path,
    timeout_seconds: int,
    bot_name: str,
):
    manifest = [
        "PECUS CHAIN — RUN MANIFEST",
        "=" * 48,
        f"run_id={run_id}",
        f"mode={mode}",
        f"created_at={datetime.now().isoformat(timespec='seconds')}",
        f"suite={suite_path}",
        f"timeout_seconds={timeout_seconds}",
        f"bot_name={bot_name}",
        f"raw_schema_version=1",
    ]

    (run_dir / "run_manifest.txt").write_text(
        "\n".join(manifest) + "\n",
        encoding="utf-8",
    )


def execute_tests(
    *,
    run_dir: Path,
    run_id: str,
    mode: str,
    tests: list[dict],
    pending: list[tuple[int, dict]],
    attempts: Counter,
    bot_name: str,
    timeout_seconds: int,
    resume: bool,
):
    raw_path = run_dir / "raw_results.csv"

    with sync_playwright() as playwright:
        context = (
            playwright.chromium.launch_persistent_context(
                user_data_dir="./whatsapp_profile",
                headless=False,
            )
        )

        page = context.pages[0]

        if not page.url.startswith(
            "https://web.whatsapp.com"
        ):
            page.goto(
                "https://web.whatsapp.com"
            )

        page.wait_for_timeout(5000)

        message_box = page.locator(
            '[contenteditable="true"]'
            '[role="textbox"]'
            '[data-tab="10"]'
        )

        message_box.wait_for(
            state="visible",
            timeout=30000,
        )

        if resume:
            print(
                f"Resume: quarantena "
                f"{RESUME_SETTLE_SECONDS}s..."
            )
            page.wait_for_timeout(
                RESUME_SETTLE_SECONDS * 1000
            )

        known_keys = {
            message_key(message)
            for message in get_bot_messages(
                page,
                bot_name,
            )
        }

        previous_area = None
        previous_scenario = None

        for sequence_no, test in pending:
            area = test.get("area")
            scenario = test.get("scenario")

            if (
                previous_area
                and area != previous_area
            ):
                page.wait_for_timeout(
                    BETWEEN_AREAS_SECONDS * 1000
                )

            if (
                test.get("suite_type") == "regression"
                and previous_scenario
                and scenario != previous_scenario
            ):
                page.wait_for_timeout(
                    BETWEEN_SCENARIOS_SECONDS * 1000
                )

            attempt_no = (
                attempts[test["test_id"]]
                + 1
            )

            result = collect_one_turn(
                page,
                message_box,
                bot_name,
                test,
                known_keys,
                timeout_seconds,
            )

            append_raw(
                raw_path,
                run_id,
                mode,
                sequence_no,
                attempt_no,
                test,
                result,
            )

            attempts[test["test_id"]] += 1

            print(
                f"Salvato seq={sequence_no}/"
                f"{len(tests)} "
                f"attempt={attempt_no}"
            )

            if not result["success"]:
                print()
                print(
                    "STOP PROTETTIVO: "
                    "timeout/risposta vuota."
                )
                print(
                    "Per riprendere:"
                )
                print(
                    f'py pecus_autotest.py resume '
                    f'"{run_dir}"'
                )
                break

            previous_area = area
            previous_scenario = scenario

            page.wait_for_timeout(
                BETWEEN_QUESTIONS_SECONDS * 1000
            )

        context.close()

    return evaluate_run(run_dir)


def command_run(args):
    suite_path = Path(args.suite)

    if not suite_path.exists():
        raise SystemExit(
            f"Suite non trovata: {suite_path}"
        )

    suite_rows = load_csv(suite_path)
    tests = select_tests(
        suite_rows,
        args.mode,
    )

    run_id = (
        "AUTO_"
        + datetime.now().strftime(
            "%Y%m%d_%H%M%S"
        )
    )

    results_dir = Path(args.results_dir)
    run_dir = results_dir / run_id
    run_dir.mkdir(
        parents=True,
        exist_ok=False,
    )

    shutil.copy2(
        suite_path,
        run_dir / "suite_snapshot.csv",
    )

    create_manifest(
        run_dir,
        run_id,
        args.mode,
        suite_path,
        args.timeout,
        args.bot_name,
    )

    print(
        "PECUS UNIFIED AUTOTEST"
    )
    print(
        "Run ID:",
        run_id,
    )
    print(
        "Mode:",
        args.mode,
    )
    print(
        "Test:",
        len(tests),
    )
    print(
        "Output:",
        run_dir,
    )

    pending = [
        (index + 1, test)
        for index, test in enumerate(tests)
    ]

    result = execute_tests(
        run_dir=run_dir,
        run_id=run_id,
        mode=args.mode,
        tests=tests,
        pending=pending,
        attempts=Counter(),
        bot_name=args.bot_name,
        timeout_seconds=args.timeout,
        resume=False,
    )

    print()
    print(
        "Run salvato in:",
        run_dir,
    )
    print(
        "Summary:",
        result["summary"],
    )


def command_resume(args):
    run_dir = Path(args.run_dir)
    raw_path = run_dir / "raw_results.csv"
    suite_snapshot = (
        run_dir / "suite_snapshot.csv"
    )

    if not raw_path.exists():
        raise SystemExit(
            f"Raw non trovato: {raw_path}"
        )

    if not suite_snapshot.exists():
        raise SystemExit(
            f"Snapshot suite non trovato: "
            f"{suite_snapshot}"
        )

    raw_rows = load_csv(raw_path)
    suite_rows = load_csv(
        suite_snapshot
    )

    if not raw_rows:
        raise SystemExit(
            "Raw vuoto."
        )

    run_id = raw_rows[0]["run_id"]
    mode = raw_rows[0]["run_mode"]

    tests = select_tests(
        suite_rows,
        mode,
    )

    successful = {
        row["test_id"]
        for row in raw_rows
        if as_bool(
            row.get(
                "collector_success",
                False,
            )
        )
    }

    attempts = Counter(
        row["test_id"]
        for row in raw_rows
    )

    pending = [
        (index + 1, test)
        for index, test in enumerate(tests)
        if test["test_id"] not in successful
    ]

    if not pending:
        print(
            "Nessun test pendente."
        )
        result = evaluate_run(
            run_dir
        )
        print(
            "Summary:",
            result["summary"],
        )
        return

    print(
        "RESUME RUN:",
        run_id,
    )
    print(
        "Mode:",
        mode,
    )
    print(
        "Test validi:",
        len(successful),
    )
    print(
        "Pendenti:",
        len(pending),
    )

    result = execute_tests(
        run_dir=run_dir,
        run_id=run_id,
        mode=mode,
        tests=tests,
        pending=pending,
        attempts=attempts,
        bot_name=args.bot_name,
        timeout_seconds=args.timeout,
        resume=True,
    )

    print(
        "Summary:",
        result["summary"],
    )


def command_evaluate(args):
    run_dir = Path(args.run_dir)
    result = evaluate_run(
        run_dir
    )

    print(
        "Valutazione completata."
    )
    print(
        "Evaluated:",
        result["evaluated_results"],
    )
    print(
        "Summary:",
        result["summary"],
    )


def command_clean(args):
    results_dir = Path(
        args.results_dir
    )
    archive_dir = Path(
        args.archive_dir
    )

    if not results_dir.exists():
        results_dir.mkdir(
            parents=True,
            exist_ok=True,
        )
        print(
            "results/ non esisteva: "
            "creata cartella vuota."
        )
        return

    contents = list(
        results_dir.iterdir()
    )

    if not contents:
        print(
            "results/ è già vuota."
        )
        return

    archive_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    target = (
        archive_dir
        / (
            "results_"
            + datetime.now().strftime(
                "%Y%m%d_%H%M%S"
            )
        )
    )

    shutil.move(
        str(results_dir),
        str(target),
    )

    results_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    print(
        "Risultati precedenti archiviati in:"
    )
    print(
        target
    )
    print(
        "Nuova results/ vuota pronta."
    )


# ===================================================================
# CLI
# ===================================================================

def build_parser():
    parser = argparse.ArgumentParser(
        description=(
            "PECUS CHAIN unified "
            "WhatsApp LLM autotest."
        )
    )

    sub = parser.add_subparsers(
        dest="command",
        required=True,
    )

    clean = sub.add_parser(
        "clean",
        help=(
            "Archivia results/ e "
            "crea una cartella pulita."
        ),
    )
    clean.add_argument(
        "--results-dir",
        default=str(
            DEFAULT_RESULTS_DIR
        ),
    )
    clean.add_argument(
        "--archive-dir",
        default=str(
            DEFAULT_ARCHIVE_DIR
        ),
    )
    clean.set_defaults(
        func=command_clean
    )

    run = sub.add_parser(
        "run",
        help="Avvia un nuovo run.",
    )
    run.add_argument(
        "--mode",
        choices=[
            "smoke",
            "functional",
            "regression",
            "all",
        ],
        default="smoke",
    )
    run.add_argument(
        "--suite",
        default=str(
            DEFAULT_SUITE
        ),
    )
    run.add_argument(
        "--results-dir",
        default=str(
            DEFAULT_RESULTS_DIR
        ),
    )
    run.add_argument(
        "--bot-name",
        default=DEFAULT_BOT_NAME,
    )
    run.add_argument(
        "--timeout",
        type=int,
        default=DEFAULT_TIMEOUT_SECONDS,
    )
    run.set_defaults(
        func=command_run
    )

    resume = sub.add_parser(
        "resume",
        help=(
            "Riprende un run "
            "interrotto."
        ),
    )
    resume.add_argument(
        "run_dir",
    )
    resume.add_argument(
        "--bot-name",
        default=DEFAULT_BOT_NAME,
    )
    resume.add_argument(
        "--timeout",
        type=int,
        default=DEFAULT_TIMEOUT_SECONDS,
    )
    resume.set_defaults(
        func=command_resume
    )

    evaluate = sub.add_parser(
        "evaluate",
        help=(
            "Rivaluta un run "
            "senza inviare messaggi."
        ),
    )
    evaluate.add_argument(
        "run_dir",
    )
    evaluate.set_defaults(
        func=command_evaluate
    )

    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
