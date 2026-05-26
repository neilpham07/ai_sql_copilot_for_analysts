---
description: >
  Automated QA skill for Finviet CDP / QueryMind AI. Runs the full pytest
  suite (excluding e2e by default), intercepts results, and activates a
  3-loop self-healing cycle on failure: proposes a git-diff style patch,
  waits for human approval, applies it, then re-runs. Aborts after 3
  failed loops and generates an emergency debugging summary.
  Trigger keywords: "Chạy test dự án", "Kiểm tra lỗi code", "Run tests",
  "run_qa_tests". E2E mode: "Chạy test e2e", "Run tests --e2e",
  "Test live connection".
---

# Skill: run_qa_tests

## Trigger Keywords

### Standard mode (zero API cost — default)
Activate when the user's message contains **any** of:
- `Chạy test dự án`
- `Kiểm tra lỗi code`
- `Run tests`
- `/run_qa_tests`
- `Chạy pytest`
- `Test hệ thống`

### E2E mode (real Anthropic API — costs money)
Activate E2E mode **only** when the user's message contains **any** of:
- `Chạy test e2e`
- `Run tests --e2e`
- `Test live connection`
- `Test Anthropic API thực`

**E2E mode requires an explicit, unambiguous keyword match. Never infer it.**

---

## Safety Constraints (Non-negotiable)

| Rule | Detail |
|---|---|
| **Never patch silently** | Every proposed code change MUST be shown as a diff proposal and require explicit `y` approval before being written to disk. |
| **3-loop hard cap** | The self-healing cycle may run at most 3 times per invocation. On the 3rd failure, abort immediately and emit the emergency summary. |
| **Preserve state on abort** | On emergency abort, do NOT revert any approved patches. Leave the codebase in its current state and document exactly what changed. |
| **Never touch `.env` or credentials** | Even if a test references env vars, do not create or modify any file containing secrets. |
| **Mock boundary is sacred** | Never remove or bypass `patch.object(local_dev, "call_claude", ...)` in test files. If a test is failing because `call_claude` is not mocked, the fix is to ADD the mock — never to remove it. |
| **E2E default exclusion** | Always add `--ignore=tests/test_e2e.py` unless E2E mode is explicitly triggered. |

---

## Environment — Known Configuration

| Item | Value |
|---|---|
| Python binary | `python` (Python 3.14, no venv) |
| pytest binary | `$env:APPDATA\Python\Python314\Scripts\pytest.exe` (add to PATH if needed) |
| Required packages | `pytest`, `pytest-asyncio`, `httpx` |
| `pytest.ini` location | Project root |
| `asyncio_mode` | `auto` (already set in `pytest.ini`) |
| Mock API key for tests | `test-mock-gemini-key-do-not-use` |
| Test files | `tests/test_sql_builder.py`, `tests/test_parsers.py`, `tests/test_cdp_api.py`, `tests/test_core_api.py` |
| E2E file | `tests/test_e2e.py` (excluded by default) |

---

## Pre-flight Checks

Before running any test, execute these checks in sequence:

### Check 1 — pytest is accessible

```powershell
python -m pytest --version
```

If this fails, run:
```powershell
pip install pytest pytest-asyncio httpx
```
Then retry. If still failing, report and stop.

### Check 2 — Mock API key is set

```powershell
$env:GEMINI_API_KEY = "test-mock-gemini-key-do-not-use"
$env:PYTHONIOENCODING = "utf-8"
$env:PATH = "$env:APPDATA\Python\Python314\Scripts;$env:PATH"
```

Set these in every PowerShell command block that runs pytest.

### Check 3 — conftest.py exists

Verify `conftest.py` exists in the project root. If missing, stop and inform
the user — the test suite cannot run without shared fixtures.

---

## Step 1 — Run Pytest and Capture Full Output

### Standard mode command:
```powershell
$env:GEMINI_API_KEY = "test-mock-gemini-key-do-not-use"
$env:PYTHONIOENCODING = "utf-8"
$env:PATH = "$env:APPDATA\Python\Python314\Scripts;$env:PATH"
python -m pytest tests/ --ignore=tests/test_e2e.py -v --tb=long 2>&1
```

### E2E mode command (only when explicitly triggered):
```powershell
$env:PYTHONIOENCODING = "utf-8"
$env:PATH = "$env:APPDATA\Python\Python314\Scripts;$env:PATH"
python -m pytest tests/test_e2e.py -m e2e -v --tb=long 2>&1
```

Capture the **complete** terminal output including:
- Every test ID and its PASSED / FAILED / ERROR / SKIPPED status
- The full traceback for every failure (`--tb=long` ensures this)
- The final summary line (`X passed, Y failed in Zs`)

---

## Step 2 — Intercept and Parse Results

From the captured output, extract:

1. **Total counts**: passed, failed, error, skipped
2. **Failing test list**: each failing test's full ID
   (e.g., `tests/test_cdp_api.py::TestCdpSegmentEstimateEndpoint::test_cdp008_sql_injection_is_blocked`)
3. **Per-failure data**:
   - File path + line number of the `AssertionError` or exception
   - The assertion that failed (what was expected vs what was received)
   - The full traceback

---

## Step 3 — Smart Branch

### Branch A — ALL TESTS PASS ✅

Print this report and stop:

```
╔══════════════════════════════════════════════════════════════╗
║  ✅  ALL TESTS PASSED — System is healthy                    ║
╠══════════════════════════════════════════════════════════════╣
║  Suite       : Standard (e2e excluded)                       ║
║  Passed      : XX / XX                                       ║
║  Duration    : X.XXs                                         ║
║  Self-healing: Not required                                  ║
╚══════════════════════════════════════════════════════════════╝

Test file summary:
  tests/test_sql_builder.py  — XX passed
  tests/test_parsers.py      — XX passed
  tests/test_cdp_api.py      — XX passed
  tests/test_core_api.py     — XX passed

No files were modified. Codebase is clean. ✓
```

---

### Branch B — ONE OR MORE TESTS FAIL ❌ → Self-Healing Loop

Initialize:
```
loop_number   = 1      (counts up to 3)
patched_files = []     (accumulates every file that gets patched)
```

Repeat the following cycle while `loop_number ≤ 3` AND there are still
failing tests:

---

#### Loop Step B1 — Diagnose Root Cause

For **each** failing test, read:
- The test file at the failing line
- The source file referenced in the traceback (usually `app.py` or `local_dev.py`)

Classify the failure into **one** of these categories:

| Code | Category | Typical cause |
|---|---|---|
| `TC` | Test code wrong | Wrong assertion value, stale mock response, wrong fixture |
| `SC` | Source code wrong | Logic bug in `app.py` / `local_dev.py` — test is correct |
| `ENV` | Environment issue | Missing dependency, wrong env var, import error |
| `MOCK` | Mock boundary broken | `call_claude` not patched, or patched at wrong target |
| `UNK` | Unknown | Cannot determine without more context |

`ENV` and `UNK` failures **skip the patch proposal** — report them immediately
and stop the loop. These require human investigation.

---

#### Loop Step B2 — Generate Patch Proposal

For `TC` and `SC` failures, generate a proposal in this exact format for
**each** affected file:

```
┌─────────────────────────────────────────────────────────────────────┐
│  🔧 PATCH PROPOSAL — Loop N/3                                       │
├─────────────────────────────────────────────────────────────────────┤
│  Failing test : tests/test_xxx.py::ClassName::test_method_name      │
│  Failure type : TC  (Test code wrong)                               │
│  Root cause   : [one clear sentence explaining why it fails]        │
├─────────────────────────────────────────────────────────────────────┤
│  File : tests/test_xxx.py                                           │
│  Line : 45                                                          │
├──────────────── OLD ────────────────────────────────────────────────┤
│  -     assert res.status_code == 200                                │
├──────────────── NEW ────────────────────────────────────────────────┤
│  +     assert res.status_code in (200, 201)                         │
└─────────────────────────────────────────────────────────────────────┘

If multiple files need changes, show one block per file.
```

After showing ALL proposals for the current batch of failures, ask:

```
Apply these N fix(es)? [y / n / skip <test_id>]

  y           — Apply all patches and re-run
  n           — Reject all, abort, emit emergency summary
  skip <id>   — Skip this specific test (add @pytest.mark.skip), apply others
```

**Wait for the user's response. Do not proceed until a response is given.**

---

#### Loop Step B3 — Apply Approved Patches

If the user responds `y`:
1. Use the Edit tool to apply each patch exactly as proposed.
2. Append each modified file path to `patched_files`.
3. Confirm each edit with: `  ✓ Patched: <filepath>:<line>`

If the user responds `n`:
- Immediately jump to the **Emergency Abort** section.

If the user responds `skip <test_id>`:
- Add `@pytest.mark.skip(reason="manual skip during run_qa_tests loop N")` to
  that test.
- Apply remaining patches normally.
- Append the test file to `patched_files`.

---

#### Loop Step B4 — Re-Run Tests

After applying patches, re-run the full suite:

```powershell
$env:GEMINI_API_KEY = "test-mock-gemini-key-do-not-use"
$env:PYTHONIOENCODING = "utf-8"
$env:PATH = "$env:APPDATA\Python\Python314\Scripts;$env:PATH"
python -m pytest tests/ --ignore=tests/test_e2e.py -v --tb=long 2>&1
```

Show a brief between-loop status:
```
  ↻ Loop N/3 complete — re-running tests...
  Result: X passed, Y failed
```

- If `Y == 0`: exit the loop → go to Branch A (all-pass report).
- If `Y > 0` AND `loop_number < 3`: increment `loop_number`, return to B1.
- If `Y > 0` AND `loop_number == 3`: jump to **Emergency Abort**.

---

## Emergency Abort — 3 Loops Exhausted

Emit this report and stop. Do NOT attempt any further edits.

```
╔══════════════════════════════════════════════════════════════════════╗
║  🚨 EMERGENCY ABORT — Self-healing failed after 3 loops             ║
╠══════════════════════════════════════════════════════════════════════╣
║  Loops attempted : 3 / 3                                            ║
║  Final state     : X tests still failing                            ║
╚══════════════════════════════════════════════════════════════════════╝

── STILL FAILING ──────────────────────────────────────────────────────
[List each remaining failing test ID]

── PATCHES APPLIED DURING THIS SESSION ───────────────────────────────
[List each file:line that was patched, with a one-line description]
If no patches were applied: "None — codebase is unchanged."

── FINAL ERROR LOG ────────────────────────────────────────────────────
[Paste the full --tb=long traceback from the last pytest run]

── ROOT CAUSE ASSESSMENT ──────────────────────────────────────────────
[Your best diagnosis of why all 3 loops failed to fix this.
 Be specific: mention file names, function names, and the exact
 assertion or exception that persists.]

── RECOMMENDED NEXT STEPS ─────────────────────────────────────────────
1. [Specific action the developer should take]
2. [Second action if applicable]
3. Run: git diff   — to review all changes made during this session
4. Run: git stash  — to discard all session patches if you want to reset
```

---

## Final Summary Report (all-pass path)

After a successful run (either on first attempt or after self-healing),
print:

```
══════════════════════════════════════════════════════════════════════
  QA RUN SUMMARY — Finviet CDP / QueryMind AI
══════════════════════════════════════════════════════════════════════
  Mode          : Standard (e2e excluded)
  Result        : ✅ ALL PASSED
  Total tests   : XX
  Duration      : X.XXs
  Self-healing  : N loop(s) used
══════════════════════════════════════════════════════════════════════

  Test file breakdown:
  ┌────────────────────────────┬────────┬────────┬────────┐
  │ File                       │ Passed │ Failed │ Skipped│
  ├────────────────────────────┼────────┼────────┼────────┤
  │ test_sql_builder.py        │   XX   │    0   │    0   │
  │ test_parsers.py            │   XX   │    0   │    0   │
  │ test_cdp_api.py            │   XX   │    0   │    0   │
  │ test_core_api.py           │   XX   │    0   │    0   │
  └────────────────────────────┴────────┴────────┴────────┘

  Files auto-patched this session:
  [List each file:line — or "None" if first run was clean]

══════════════════════════════════════════════════════════════════════
```

---

## Failure Classification Cheat Sheet

Use this table to speed up root-cause analysis in Loop Step B1:

| Symptom in traceback | Category | Where to look |
|---|---|---|
| `AssertionError: assert 400 == 200` | `TC` or `SC` | Compare API handler logic vs test expectation |
| `AssertionError: assert 'key' in {}` | `TC` or `SC` | Check response shape in handler + test assertion |
| `ModuleNotFoundError` | `ENV` | `pip install <package>` |
| `AttributeError: MagicMock...` | `MOCK` | Check `patch.object(local_dev, "call_claude", ...)` target |
| `ValueError: Unknown field:` | `SC` | Field missing from `CDP_CRITERIA_FIELDS` in `app.py` |
| `ValueError: disallowed characters` | `SC` or `TC` | SQL injection guard in `_check_string_value()` |
| `RuntimeError: no running event loop` | `ENV` | Ensure `asyncio_mode = auto` in `pytest.ini` |
| `httpx.ConnectError` | `ENV` | ASGITransport misconfigured in `conftest.py` |
| `SystemExit: 1` on import | `ENV` | `GEMINI_API_KEY` not set before import |

---

## Immutable Files (Never Patch Without Extra Warning)

The following files require **double confirmation** before patching — show the
normal proposal AND add a warning banner:

```
⚠️  WARNING: You are about to modify a protected file.
    This file affects ALL tests and the production deployment.
    Are you absolutely sure? [yes / no]
```

Protected files:
- `conftest.py` — shared fixture definitions
- `pytest.ini` — test runner configuration
- `app.py` — single deployable artifact (Modal production)

Changes to `local_dev.py` follow the normal single-confirmation flow.
