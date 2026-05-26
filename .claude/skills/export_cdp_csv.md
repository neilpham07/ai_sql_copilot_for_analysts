---
description: >
  Export CDP merchant segments to CSV using a live Docker Postgres instance
  (cdp-postgres on port 5433). Auto-initialises the cdp_merchant_profile_flat
  table (DDL derived from CDP_CRITERIA_FIELDS) and seeds 5,000 synthetic rows
  on first run. Resolves segment filters from the CDP library or a raw SQL
  WHERE clause, then writes the result to downloads/.
  Trigger keywords: "Xuất CSV tệp", "Export tệp", "export cdp csv", "/export_cdp_csv"
---

# Skill: export_cdp_csv

## Trigger Keywords

Activate this skill whenever the user's message contains any of:
- `Xuất CSV tệp ...`
- `Export tệp ...`
- `export cdp csv`
- `/export_cdp_csv`

---

## Environment Contract

| Variable | Value |
|---|---|
| Docker container | `cdp-postgres` |
| Host / Port | `localhost:5433` (isolated from Airflow Postgres on 5432) |
| Default `CDP_DATABASE_URL` | `postgresql://postgres:finviet2026@localhost:5433/postgres` |
| Override | `$env:CDP_DATABASE_URL = "postgresql://..."` before running |
| Required pip package | `psycopg2-binary` |
| Runner script | `scripts/export_cdp_csv.py` |
| Output directory | `downloads/` (auto-created if absent) |

---

## Procedure — Follow These Steps Exactly

### Step 1 — Parse the user's request

Extract two pieces of information from the user's message:

**A. Segment identifier** — one of:
- A named segment from the CDP library (e.g. `"active_champions"`, `"loan_whitelist_tier1"`)
- A free-form Vietnamese description (e.g. `"merchant TP HCM có GMV > 50M"`)
- The literal string `"all"` to export without filtering

**B. Raw WHERE clause** (optional) — if the user provides an explicit SQL condition
(e.g. `"gmv_30d > 50000000 AND merchant_region = 'Ha Noi'"`), capture it for
the `--where` argument. If none is provided, the runner resolves it from the
CDP segment library automatically.

Construct the `--segment` and optional `--where` arguments before proceeding.

---

### Step 2 — Verify the runner script exists

Check that `scripts/export_cdp_csv.py` exists in the project root.

- **If it exists:** proceed to Step 3.
- **If it is missing:** inform the user and stop. Do not attempt to recreate it —
  the file must be restored from git (`git checkout HEAD scripts/export_cdp_csv.py`).

---

### Step 3 — Verify psycopg2-binary is installed

```powershell
python -c "import psycopg2; print('psycopg2 OK:', psycopg2.__version__)"
```

If the import fails, install it:

```powershell
pip install psycopg2-binary
```

---

### Step 4 — Verify the Docker container is reachable

```powershell
python -c "
import psycopg2, sys
try:
    c = psycopg2.connect('postgresql://postgres:finviet2026@localhost:5433/postgres', connect_timeout=5)
    c.close()
    print('Connection OK')
except Exception as e:
    print(f'Connection FAILED: {e}')
    sys.exit(1)
"
```

If the connection fails:
1. Tell the user the exact error message.
2. Suggest: `docker ps | grep cdp-postgres` to confirm the container is running.
3. Suggest: `docker start cdp-postgres` if the container exists but is stopped.
4. **Stop here — do not proceed with the export.**

---

### Step 5 — Run the export script

Construct the command based on Step 1:

**Case A — Named segment from library:**
```powershell
$env:PYTHONIOENCODING = "utf-8"
python scripts/export_cdp_csv.py --segment <segment_id>
```

**Case B — Named segment with explicit WHERE override:**
```powershell
$env:PYTHONIOENCODING = "utf-8"
python scripts/export_cdp_csv.py --segment <label> --where "<SQL WHERE clause>"
```

**Case C — Export all merchants:**
```powershell
$env:PYTHONIOENCODING = "utf-8"
python scripts/export_cdp_csv.py --segment all
```

The script handles first-run table creation automatically:
- Checks if `cdp_merchant_profile_flat` exists in the `public` schema
- If missing: derives DDL from all 27 `CDP_CRITERIA_FIELDS` entries and creates the table
- If empty: seeds 5,000 synthetic merchant rows (deterministic, seed=42)
- Then executes the resolved WHERE clause and writes the CSV

---

### Step 6 — Report the result

After the script completes, report to the user:

```
✓ Export complete

  File  : downloads/cdp_export_<segment_id>_<YYYYMMDD>.csv
  Rows  : <N> merchants matched
  Size  : <KB>

  Preview (first 5 rows):
  ──────────────────────────────────────────────────────────────────
  COLUMNS (32): merchant_id, merchant_name, segment_tag, cdp_status, gmv_30d...
  ──────────────────────────────────────────────────────────────────
  Row 1: 1  |  Tạp Hóa Nguyễn...  |  Active Champion  |  Excellent  |  82450000...
  Row 2: ...
  ...
  ──────────────────────────────────────────────────────────────────
```

If the script exits with code 1 (0 rows matched), inform the user and suggest
broadening the filter.

---

## File Naming Convention

```
downloads/cdp_export_<segment_id>_<YYYYMMDD>.csv
```

| Token | Example |
|---|---|
| `<segment_id>` | `active_champions`, `custom`, `all` |
| `<YYYYMMDD>` | `20260526` |

Full example: `downloads/cdp_export_active_champions_20260526.csv`

---

## First-Run Table Schema

The `cdp_merchant_profile_flat` table is built programmatically by the runner.
The DDL template (for reference):

```sql
CREATE TABLE IF NOT EXISTS cdp_merchant_profile_flat (
  merchant_id          BIGSERIAL        PRIMARY KEY,
  merchant_name        VARCHAR(255)     NOT NULL,
  segment_tag          VARCHAR(100),
  cdp_status           VARCHAR(50),
  created_at           TIMESTAMPTZ      DEFAULT NOW(),
  -- 27 CDP criteria columns (derived from CDP_CRITERIA_FIELDS):
  app_installed_state  VARCHAR(100),
  app_last_active_days NUMERIC(15,2),
  gmv_30d              NUMERIC(15,2),
  merchant_region      VARCHAR(100),
  credit_score_tier    VARCHAR(100),
  -- ... (all 27 fields follow the same pattern)
);
```

Column type mapping:

| CDP field type | PostgreSQL type |
|---|---|
| `numeric` | `NUMERIC(15,2)` |
| `categorical` | `VARCHAR(100)` |
| `boolean` | `VARCHAR(10)` — stores `'Yes'` / `'No'` |
| `duration` | `INTEGER` — stores months |

---

## Synthetic Data Rules (Seed = 42)

The 5,000 seeded rows use deterministic `random.Random(42)` so re-seeding
produces the same data:

| Field pattern | Synthetic range |
|---|---|
| `*gmv*`, `*amount*` | `100,000 – 180,000,000` VND |
| `*rate*`, `*growth*` | `−40.0 – 150.0` % |
| `*days*` | `0 – 365` |
| `*count*`, `*orders*`, `*tenure*` | `0 – 200` |
| `categorical` / `boolean` | random choice from `values[]` in `CDP_CRITERIA_FIELDS` |
| `duration` | `1 – 24` months |

---

## Error Handling Cheat Sheet

| Error | Likely cause | Fix |
|---|---|---|
| `connection refused :5433` | Container stopped | `docker start cdp-postgres` |
| `psycopg2 not found` | Missing dep | `pip install psycopg2-binary` |
| `0 rows matched` | Filter too strict | Broaden the WHERE clause |
| `Unknown field: xyz` | Typo in `--where` | Check column names against `CDP_CRITERIA_FIELDS` |
| `permission denied: downloads/` | Directory permissions | `mkdir downloads` manually |

---

## Quick Reference — Available Segment IDs

These IDs resolve automatically without `--where`:

| Segment ID | Category |
|---|---|
| `active_champions` | Core Loyalty Tiers |
| `loan_whitelist_tier1` | Credit & Financial Health |
| `high_risk_default` | Credit & Financial Health |
| `deal_hunters` | Promo & App Engagement |

For the full list, run:
```powershell
python -c "
import os, sys
os.environ.setdefault('ANTHROPIC_API_KEY','sk-test')
sys.path.insert(0,'.')
from scripts.export_cdp_csv import CDP_SEGMENTS_LIBRARY
for s in CDP_SEGMENTS_LIBRARY:
    print(f'{s[\"id\"]:<35} {s[\"category\"]}')
"
```
