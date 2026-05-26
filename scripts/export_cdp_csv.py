#!/usr/bin/env python3
"""
CDP Export Runner — Finviet CDP Portal
Connects to Docker Postgres on port 5433. On first run, auto-creates
cdp_merchant_profile_flat (schema derived from CDP_CRITERIA_FIELDS) and seeds
5,000 synthetic merchant rows. Exports a filtered segment to CSV.

Dependencies: pip install psycopg2-binary

Usage:
    python scripts/export_cdp_csv.py --segment active_champions
    python scripts/export_cdp_csv.py --segment custom --where "gmv_30d > 50000000"
    python scripts/export_cdp_csv.py --segment "Q2 Promo" --where "merchant_region = 'Ha Noi'"
"""
from __future__ import annotations

import argparse
import csv
import datetime
import importlib.util
import os
import random
import sys
from pathlib import Path
from unittest.mock import MagicMock

try:
    import psycopg2
    import psycopg2.extras
except ImportError:
    print("ERROR: psycopg2-binary is required.\n  pip install psycopg2-binary")
    sys.exit(1)

# ── Paths ─────────────────────────────────────────────────────────────────────
ROOT      = Path(__file__).resolve().parent.parent
DOWNLOADS = ROOT / "downloads"
TABLE     = "cdp_merchant_profile_flat"
SEED_ROWS = 5_000

# ── DB connection (override via env var CDP_DATABASE_URL) ────────────────────
DB_URL = os.environ.get(
    "CDP_DATABASE_URL",
    "postgresql://postgres:finviet2026@localhost:5433/postgres",
)

# ── Load CDP artefacts from app.py via importlib (same pattern as local_dev) ─
def _load_cdp_module() -> tuple:
    mock = MagicMock()
    mock.App.return_value      = MagicMock()
    mock.Secret.from_name.return_value = MagicMock()
    mock.asgi_app.return_value = lambda f: f
    sys.modules.setdefault("modal", mock)
    spec = importlib.util.spec_from_file_location("_app", ROOT / "app.py")
    mod  = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.CDP_CRITERIA_FIELDS, mod.CDP_SEGMENTS_LIBRARY


CDP_CRITERIA_FIELDS, CDP_SEGMENTS_LIBRARY = _load_cdp_module()

# ── PostgreSQL type mapping ───────────────────────────────────────────────────
_PG_TYPE: dict[str, str] = {
    "numeric":     "NUMERIC(15,2)",
    "categorical": "VARCHAR(100)",
    "boolean":     "VARCHAR(10)",   # stores 'Yes' / 'No' — consistent with CDP filter values
    "duration":    "INTEGER",
}

# ── Synthetic data pools ──────────────────────────────────────────────────────
_SURNAMES  = ["Nguyễn", "Trần", "Lê", "Phạm", "Hoàng", "Vũ", "Đặng", "Bùi", "Đỗ", "Hồ",
               "Võ", "Đinh", "Lý", "Dương", "Mai", "Cao", "Phan", "Lâm", "Tống", "Chu"]
_GIVEN     = ["Thị Mai", "Văn Hùng", "Thị Lan", "Văn Nam", "Thị Hoa", "Minh Đức",
               "Quỳnh Anh", "Công Thành", "Thị Thu", "Văn Lợi", "Thị Phương", "Minh Tú",
               "Thị Ngọc", "Văn Khoa", "Thị Yến", "Công Dũng", "Thị Linh", "Bá Cường"]
_PREFIXES  = ["Tạp Hóa", "Cửa Hàng", "Siêu Thị Mini", "Quầy Tạp Hóa", "Điểm Bán",
               "Shop", "Cửa Hàng Tiện Lợi", "Đại Lý"]
_TAGS      = ["Active Champion", "Loyal", "Promising", "New", "Churning",
               "Deal Hunter", "High Risk", "Dormant", "Rising Star"]
_STATUSES  = ["Excellent", "Good", "Standard", "Watch", "At Risk"]


def _rand_store_name(rng: random.Random) -> str:
    return f"{rng.choice(_PREFIXES)} {rng.choice(_SURNAMES)} {rng.choice(_GIVEN)}"


def _rand_value(field_name: str, meta: dict, rng: random.Random):
    ftype = meta["type"]

    if ftype in ("boolean", "categorical"):
        choices = meta.get("values") or ["Yes", "No"]
        return rng.choice(choices)

    if ftype == "duration":
        return rng.randint(1, 24)

    # Numeric — realistic range per semantic
    if "gmv" in field_name or "ecopay_gmv" in field_name:
        return round(rng.uniform(100_000, 180_000_000), 2)
    if "amount" in field_name:  # average_order_value, outstanding_loan_amount
        return round(rng.uniform(50_000, 30_000_000), 2)
    if "growth" in field_name:  # gmv_mom_growth — can be negative
        return round(rng.uniform(-40.0, 150.0), 2)
    if "rate" in field_name:    # transaction_failure_rate, promo_response_rate, etc.
        return round(rng.uniform(0.0, 100.0), 2)
    if "sms_open_rate" in field_name or "repayment_rate" in field_name:
        return round(rng.uniform(0.0, 100.0), 2)
    if "days" in field_name:    # app_last_active_days, days_since_last_transaction, days_overdue
        return rng.randint(0, 365)
    if "count" in field_name or "orders" in field_name:
        return rng.randint(0, 200)
    if "tenure" in field_name:
        return rng.randint(1, 72)
    return round(rng.uniform(0, 1_000_000), 2)


# ── DDL ───────────────────────────────────────────────────────────────────────
def build_ddl() -> str:
    base_cols = [
        "merchant_id   BIGSERIAL        PRIMARY KEY",
        "merchant_name VARCHAR(255)     NOT NULL",
        "segment_tag   VARCHAR(100)",
        "cdp_status    VARCHAR(50)",
        "created_at    TIMESTAMPTZ      DEFAULT NOW()",
    ]
    field_cols = [
        f"{name:<36} {_PG_TYPE.get(meta['type'], 'TEXT')}"
        for name, meta in CDP_CRITERIA_FIELDS.items()
    ]
    all_cols = base_cols + field_cols
    return (
        f"CREATE TABLE IF NOT EXISTS {TABLE} (\n"
        + ",\n".join(f"  {c}" for c in all_cols)
        + "\n);"
    )


# ── First-run initialisation ──────────────────────────────────────────────────
def ensure_table(conn: "psycopg2.connection") -> None:
    with conn.cursor() as cur:
        cur.execute(
            "SELECT EXISTS ("
            "  SELECT 1 FROM information_schema.tables"
            "  WHERE table_schema = 'public' AND table_name = %s"
            ")",
            (TABLE,),
        )
        exists = cur.fetchone()[0]

        if not exists:
            print(f"  [INIT] Table '{TABLE}' not found — creating schema...")
            cur.execute(build_ddl())
            print(f"  [INIT] DDL applied. Seeding {SEED_ROWS:,} synthetic rows...")
            _seed(cur)
            conn.commit()
            print(f"  [INIT] First-run initialisation complete.")
            return

        cur.execute(f"SELECT COUNT(*) FROM {TABLE}")
        count = cur.fetchone()[0]
        if count == 0:
            print(f"  [INIT] Table exists but is empty — seeding {SEED_ROWS:,} rows...")
            _seed(cur)
            conn.commit()
        else:
            print(f"  [DB]   Table ready — {count:,} rows.")


def _seed(cur: "psycopg2.cursor") -> None:
    rng        = random.Random(42)
    field_names = list(CDP_CRITERIA_FIELDS.keys())
    col_list   = ", ".join(["merchant_name", "segment_tag", "cdp_status"] + field_names)
    placeholders = ", ".join(["%s"] * (3 + len(field_names)))
    sql        = f"INSERT INTO {TABLE} ({col_list}) VALUES ({placeholders})"

    batch: list[tuple] = []
    for _ in range(SEED_ROWS):
        row: list = [
            _rand_store_name(rng),
            rng.choice(_TAGS),
            rng.choice(_STATUSES),
        ]
        for fname in field_names:
            row.append(_rand_value(fname, CDP_CRITERIA_FIELDS[fname], rng))
        batch.append(tuple(row))
        if len(batch) == 500:
            psycopg2.extras.execute_batch(cur, sql, batch)
            batch.clear()

    if batch:
        psycopg2.extras.execute_batch(cur, sql, batch)

    print(f"  [SEED] {SEED_ROWS:,} synthetic merchant rows inserted (seed=42).")


# ── WHERE clause builder for flat table ──────────────────────────────────────
_FLAT_OP: dict[str, str] = {
    "greater than": ">", "less than": "<",
    "equals": "=", "is exactly": "=", "is not": "!=",
}


def _criterion_to_flat_sql(c: dict) -> str:
    field = c.get("field", "")
    op    = c.get("operator", "")
    val   = c.get("value")

    if op == "between":
        lo, hi = (val if isinstance(val, list) else [val, val])
        return f"({field} BETWEEN {lo} AND {hi})"
    if op == "is one of":
        items  = val if isinstance(val, list) else [val]
        quoted = ", ".join(f"'{v}'" for v in items)
        return f"({field} IN ({quoted}))"
    if op == "last consecutive":
        return f"({field} >= {val})"
    if op in _FLAT_OP:
        sql_op = _FLAT_OP[op]
        return f"({field} {sql_op} '{val}')" if isinstance(val, str) else f"({field} {sql_op} {val})"
    return "1=1"


def build_flat_where(filters: dict) -> str:
    """Translate CDP filter JSON to flat-table WHERE clause (no table aliases)."""
    group_clauses: list[str] = []
    for group in filters.get("groups", []):
        parts = [_criterion_to_flat_sql(c) for c in group.get("criteria", []) if c.get("field")]
        if parts:
            inner = f" {group.get('operator', 'AND')} ".join(parts)
            group_clauses.append(f"({inner})")
    if not group_clauses:
        return "1=1"
    return f" {filters.get('operator', 'AND')} ".join(group_clauses)


# ── Segment resolution ────────────────────────────────────────────────────────
def resolve_segment(segment_arg: str, custom_where: str | None) -> tuple[str, str]:
    """
    Returns (where_clause, safe_segment_id).
    Priority: explicit --where > library lookup by ID > export-all fallback.
    """
    if custom_where:
        safe_id = segment_arg.replace(" ", "_").lower()
        return custom_where, safe_id

    seg = next(
        (s for s in CDP_SEGMENTS_LIBRARY if s["id"].lower() == segment_arg.lower()),
        None,
    )
    if seg:
        where = build_flat_where(seg["filters"])
        print(f"  [SEG]  Matched library segment: '{seg['label']}' ({seg['category']})")
        print(f"  [SEG]  Filter: {where}")
        return where, seg["id"]

    print(f"  [WARN] Segment '{segment_arg}' not in library — exporting all merchants.")
    return "1=1", segment_arg.replace(" ", "_").lower() or "all"


# ── Export ────────────────────────────────────────────────────────────────────
def export_to_csv(where_clause: str, segment_id: str) -> Path | None:
    today    = datetime.date.today().strftime("%Y%m%d")
    safe_id  = "".join(c if c.isalnum() or c == "_" else "_" for c in segment_id)
    DOWNLOADS.mkdir(exist_ok=True)
    out_path = DOWNLOADS / f"cdp_export_{safe_id}_{today}.csv"

    query = f"SELECT * FROM {TABLE} WHERE {where_clause} ORDER BY merchant_id"

    conn = psycopg2.connect(DB_URL)
    try:
        ensure_table(conn)

        with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
            print(f"\n  [SQL]  {query[:120]}{'...' if len(query) > 120 else ''}")
            cur.execute(query)
            rows = cur.fetchall()

        if not rows:
            print("  [WARN] Query returned 0 rows — no CSV written.")
            return None

        col_names = [desc[0] for desc in cur.description]
    finally:
        conn.close()

    with open(out_path, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=col_names)
        writer.writeheader()
        writer.writerows([dict(r) for r in rows])

    return out_path


# ── Preview ───────────────────────────────────────────────────────────────────
def preview_csv(path: Path, n: int = 5) -> None:
    with open(path, "r", encoding="utf-8-sig") as f:
        reader  = csv.reader(f)
        header  = next(reader)
        preview = [next(reader, None) for _ in range(n)]

    sep = "─" * 68
    print(f"\n  {sep}")
    print(f"  COLUMNS ({len(header)}): {', '.join(header[:7])}{'...' if len(header) > 7 else ''}")
    print(f"  {sep}")
    for i, row in enumerate(preview, 1):
        if row:
            vals = "  |  ".join(str(v)[:18] for v in row[:5])
            print(f"  Row {i}: {vals}")
    print(f"  {sep}")


# ── Entry point ───────────────────────────────────────────────────────────────
def main() -> None:
    parser = argparse.ArgumentParser(
        description="Finviet CDP — Export merchant segment to CSV",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument(
        "--segment",
        required=True,
        metavar="SEGMENT_ID",
        help=(
            "Segment ID from the CDP library (e.g. 'active_champions'),\n"
            "or any label when used with --where."
        ),
    )
    parser.add_argument(
        "--where",
        default=None,
        metavar="SQL_WHERE",
        help="Raw SQL WHERE clause applied directly to cdp_merchant_profile_flat.\n"
             "Example: \"gmv_30d > 50000000 AND merchant_region = 'Ha Noi'\"",
    )
    args = parser.parse_args()

    bar = "=" * 68
    print(f"\n{bar}")
    print("  CDP EXPORT — Finviet CDP Portal")
    print(f"  DB     : {DB_URL}")
    print(f"  Segment: {args.segment}")
    if args.where:
        print(f"  WHERE  : {args.where}")
    print(bar)

    where_clause, resolved_id = resolve_segment(args.segment, args.where)
    out_path = export_to_csv(where_clause, resolved_id)

    if not out_path:
        sys.exit(1)

    row_count = sum(1 for _ in open(out_path, encoding="utf-8-sig")) - 1  # subtract header
    file_kb   = out_path.stat().st_size // 1024

    print(f"\n  ✓ Export complete")
    print(f"  Path  : {out_path}")
    print(f"  Rows  : {row_count:,}")
    print(f"  Size  : {file_kb} KB")
    preview_csv(out_path)
    print(f"\n{bar}\n")


if __name__ == "__main__":
    main()
