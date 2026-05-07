"""
Equipment library service — MEX Safety Agent
SQLite-backed database of pre-rated safety devices.
Used to auto-enrich parsed components and review equipment lists.
"""

import json
import logging
import os
import re
import sqlite3

logger = logging.getLogger(__name__)

_HERE    = os.path.dirname(os.path.abspath(__file__))
DB_PATH  = os.path.normpath(os.path.join(_HERE, "..", "data", "equipment_library.db"))

# ── Manufacturer name normalisation map ───────────────────────────────────────
_MFR_ALIASES = {
    "sick ag":             "sick",
    "sick gmbh":           "sick",
    "pilz gmbh":           "pilz",
    "pilz gmbh & co":      "pilz",
    "allen-bradley":       "allen bradley",
    "allen bradley":       "allen bradley",
    "rockwell":            "allen bradley",
    "rockwell automation": "allen bradley",
    "ab":                  "allen bradley",
    "schneider":           "schneider electric",
    "telemecanique":       "schneider electric",
    "square d":            "schneider electric",
    "schmersal gmbh":      "schmersal",
    "k.a. schmersal":      "schmersal",
    "omron electronics":   "omron",
    "banner engineering":  "banner",
    "euchner gmbh":        "euchner",
    "siemens ag":          "siemens",
}

_TOKEN_SPLIT = re.compile(r"[\s\-\._/]+")


def _tokenise(s: str) -> set[str]:
    """Lowercase and split a string into tokens for fuzzy matching."""
    return {t for t in _TOKEN_SPLIT.split(s.lower()) if t}


def _normalise_manufacturer(s: str) -> str:
    """Return canonical lowercase manufacturer name."""
    if not s:
        return ""
    low = s.strip().lower()
    return _MFR_ALIASES.get(low, low)


# ── DB initialisation ─────────────────────────────────────────────────────────

def init_db() -> None:
    """Create schema and seed data if the DB does not exist or is empty."""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    con = sqlite3.connect(DB_PATH)
    con.execute("""
        CREATE TABLE IF NOT EXISTS equipment (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            manufacturer  TEXT NOT NULL,
            model         TEXT NOT NULL,
            model_aliases TEXT DEFAULT '[]',
            device_type   TEXT NOT NULL,
            category      TEXT,
            pl_rating     TEXT,
            sil_rating    TEXT,
            b10d          REAL,
            pfhd          REAL,
            mttfd_years   REAL,
            dc            TEXT,
            datasheet_ref TEXT,
            notes         TEXT,
            UNIQUE(manufacturer, model)
        )
    """)
    con.execute("CREATE INDEX IF NOT EXISTS idx_mfr  ON equipment(manufacturer COLLATE NOCASE)")
    con.execute("CREATE INDEX IF NOT EXISTS idx_type ON equipment(device_type)")
    con.commit()

    count = con.execute("SELECT COUNT(*) FROM equipment").fetchone()[0]
    if count == 0:
        _seed(con)
        count = con.execute("SELECT COUNT(*) FROM equipment").fetchone()[0]

    con.close()
    logger.info("Equipment library ready — %d devices", count)


def _seed(con: sqlite3.Connection) -> None:
    from data.seed_devices import SEED_DEVICES
    for d in SEED_DEVICES:
        con.execute(
            """INSERT OR IGNORE INTO equipment
               (manufacturer, model, model_aliases, device_type, category,
                pl_rating, sil_rating, b10d, pfhd, mttfd_years, dc, notes)
               VALUES (?,?,?,?,?,?,?,?,?,?,?,?)""",
            (
                d["manufacturer"],
                d["model"],
                json.dumps(d.get("model_aliases", [])),
                d["device_type"],
                d.get("category"),
                d.get("pl_rating"),
                d.get("sil_rating"),
                d.get("b10d"),
                d.get("pfhd"),
                d.get("mttfd_years"),
                d.get("dc"),
                d.get("notes"),
            ),
        )
    con.commit()
    logger.info("Equipment library seeded with %d devices", len(SEED_DEVICES))


# ── Core lookup ───────────────────────────────────────────────────────────────

FUZZY_THRESHOLD = 0.70


def lookup(manufacturer: str | None, model: str | None) -> tuple[dict, str, float] | None:
    """
    Look up a device by manufacturer + model.
    Returns (row_dict, match_type, score) or None.

    Match strategy:
      1. Exact — case-insensitive, checks model and aliases
      2. Fuzzy — token overlap score >= FUZZY_THRESHOLD
    Manufacturer match is required when provided.
    """
    if not model:
        return None

    mfr_norm   = _normalise_manufacturer(manufacturer or "")
    model_norm = model.strip().lower()

    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    rows = con.execute("SELECT * FROM equipment").fetchall()
    con.close()

    # Tier 1: exact model match (or alias)
    for row in rows:
        db_mfr    = _normalise_manufacturer(row["manufacturer"])
        if mfr_norm and db_mfr != mfr_norm:
            continue
        db_models = {row["model"].strip().lower()}
        for alias in json.loads(row["model_aliases"] or "[]"):
            db_models.add(alias.strip().lower())
        if model_norm in db_models:
            return dict(row), "exact", 1.0

    # Tier 2: token fuzzy match
    query_tokens = _tokenise(model_norm)
    if not query_tokens:
        return None

    best_score, best_row = 0.0, None
    for row in rows:
        db_mfr = _normalise_manufacturer(row["manufacturer"])
        if mfr_norm and db_mfr != mfr_norm:
            continue
        aliases_str  = " ".join(json.loads(row["model_aliases"] or "[]"))
        db_tokens    = _tokenise(row["model"] + " " + aliases_str)
        matched      = query_tokens & db_tokens
        if not matched:
            continue
        score = len(matched) / len(query_tokens)
        if score > best_score:
            best_score = score
            best_row   = row

    if best_row and best_score >= FUZZY_THRESHOLD:
        return dict(best_row), "fuzzy", best_score

    return None


# ── Enrichment helpers ────────────────────────────────────────────────────────

def enrich_component(component: dict) -> dict:
    """
    Enrich a parsed component dict in-place with library data.
    Only fills null fields — never overwrites values Claude already returned.
    """
    if component.get("pl_rating"):
        return component  # Claude already identified it

    result = lookup(component.get("manufacturer"), component.get("model") or component.get("label"))
    if result:
        row, match_type, score = result
        if row.get("pl_rating"):
            component["pl_rating"] = row["pl_rating"]
        logger.info(
            "Library: enriched '%s %s' → %s (%s %.0f%%)",
            component.get("manufacturer", ""), component.get("model", ""),
            row.get("pl_rating", "?"), match_type, score * 100,
        )
    return component


def enrich_equipment_item(item) -> object:
    """
    Return an enriched copy of an EquipmentItem.
    Uses model_copy() to avoid mutating the Pydantic model.
    Only fills pl_rating if it is currently unset.
    """
    if item.pl_rating:
        return item

    result = lookup(item.manufacturer, item.model)
    if result:
        row, match_type, score = result
        if row.get("pl_rating"):
            logger.info(
                "Library: enriched '%s %s' → %s (%s %.0f%%)",
                item.manufacturer, item.model,
                row["pl_rating"], match_type, score * 100,
            )
            return item.model_copy(update={"pl_rating": row["pl_rating"]})

    return item


# ── Query helpers (used by the library router) ────────────────────────────────

def get_all(manufacturer: str | None = None, device_type: str | None = None) -> list[dict]:
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    query  = "SELECT * FROM equipment WHERE 1=1"
    params = []
    if manufacturer:
        query  += " AND manufacturer LIKE ?"
        params.append(f"%{manufacturer}%")
    if device_type:
        query  += " AND device_type = ?"
        params.append(device_type)
    query += " ORDER BY manufacturer, model"
    rows = con.execute(query, params).fetchall()
    con.close()
    return [dict(r) for r in rows]


def get_by_id(device_id: int) -> dict | None:
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    row = con.execute("SELECT * FROM equipment WHERE id = ?", (device_id,)).fetchone()
    con.close()
    return dict(row) if row else None


def search(q: str) -> list[tuple[dict, str, float]]:
    """Return list of (row, match_type, score) for all matches above threshold."""
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    rows  = con.execute("SELECT * FROM equipment").fetchall()
    con.close()

    q_norm   = q.strip().lower()
    q_tokens = _tokenise(q_norm)
    results  = []

    for row in rows:
        # Exact check
        db_models = {row["model"].strip().lower()}
        for alias in json.loads(row["model_aliases"] or "[]"):
            db_models.add(alias.strip().lower())
        if q_norm in db_models:
            results.append((dict(row), "exact", 1.0))
            continue

        # Fuzzy
        if not q_tokens:
            continue
        aliases_str = " ".join(json.loads(row["model_aliases"] or "[]"))
        db_tokens   = _tokenise(row["model"] + " " + aliases_str)
        matched     = q_tokens & db_tokens
        if matched:
            score = len(matched) / len(q_tokens)
            if score >= FUZZY_THRESHOLD:
                results.append((dict(row), "fuzzy", score))

    results.sort(key=lambda x: x[2], reverse=True)
    return results
