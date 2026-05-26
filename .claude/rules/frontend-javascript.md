---
description: All JavaScript behavior patterns for workspace and CDP pages. All JS must be inline in HTML strings — no external files.
globs: ["app.py", "workspace.html", "cdp.html"]
---

# Frontend JavaScript Behavior

All JavaScript must be inline `<script>` within the HTML strings. No external JS files.

## Auth Guard (all protected pages)

```javascript
// Place at top of <script> block
if (!sessionStorage.getItem('qm_auth')) { window.location.href = '/'; }
function doLogout() { sessionStorage.removeItem('qm_auth'); window.location.href = '/'; }
```

Credentials (login modal on index.html): `admin@email.com` / `admin123`

## Mode Tab Switching

```javascript
function switchMode(mode) {
  document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
  document.getElementById(`tab-${mode}`).classList.add('active');
  currentMode = mode;
  const placeholders = {
    translate: "Ví dụ: Lấy tổng doanh thu của từng merchant trong tháng này...",
    explain:   "Ví dụ: Dán SQL phức tạp vào đây để tôi giải thích từng bước..."
  };
  document.getElementById('main-input').placeholder = placeholders[mode];
}
```

## Generate Insight Button

```javascript
async function generateInsight() {
  const input = document.getElementById('main-input').value.trim();
  if (!input) return;
  setLoading(true);
  try {
    if (currentMode === 'translate') {
      const res = await fetch('/api/translate', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({question: input})
      });
      const data = await res.json();
      renderSQL(data.sql);
    } else {
      const res = await fetch('/api/explain', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({sql: input})
      });
      const data = await res.json();
      renderExplanation(data.steps);
    }
  } catch (err) {
    showError(err.message);
  } finally {
    setLoading(false);
  }
}
```

## Quick Query Tags

```javascript
const QUICK_QUERIES = {
  "Top Merchants by GMV":   "Cho tôi thấy top 10 merchant có tổng giá trị giao dịch (GMV) cao nhất trong tháng này",
  "Fast Growth List":       "Liệt kê các merchant có tốc độ tăng trưởng doanh thu nhanh nhất so với tháng trước",
  "Failure Rate Analysis":  "Phân tích tỷ lệ giao dịch thất bại theo từng merchant, sắp xếp từ cao đến thấp"
};

function fillQuery(label) {
  document.getElementById('main-input').value = QUICK_QUERIES[label];
  switchMode('translate');
}
```

## Copy & Download SQL

```javascript
function copySQL() {
  const code = document.getElementById('sql-output').innerText;
  navigator.clipboard.writeText(code).then(() => showToast('Copied to clipboard!'));
}

function downloadSQL() {
  const code = document.getElementById('sql-output').innerText;
  const blob = new Blob([code], {type: 'text/plain'});
  const a = document.createElement('a');
  a.href = URL.createObjectURL(blob);
  a.download = 'query_v1_insight.sql';
  a.click();
}
```

## CDP — Real-time Estimation (debounced)

```javascript
let estimateTimer = null;
function triggerEstimate() {
  clearTimeout(estimateTimer);
  estimateTimer = setTimeout(runEstimate, 500);
}

async function runEstimate() {
  const filters = buildFilters();
  const res = await fetch('/api/cdp/segment/estimate', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({filters, preview_rows: 5})
  });
  const data = await res.json();
  renderEstimate(data);
  renderPreview(data.merchant_preview);
}
```

Call `triggerEstimate()` on every criteria change event.

## CDP — NLP to Filters

```javascript
async function runNL() {
  const desc = document.getElementById('nl-input').value.trim();
  if (!desc) return;
  const res = await fetch('/api/cdp/nl_to_filters', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({description: desc})
  });
  const data = await res.json();
  // Populate criteria rows from data.filters
  loadFiltersIntoBuilder(data.filters);
  triggerEstimate();
}
```

## Toast Notification

```javascript
function showToast(msg) {
  const t = document.getElementById('toast');
  t.textContent = msg;
  t.style.opacity = '1';
  t.style.transform = 'translateY(0)';
  setTimeout(() => {
    t.style.opacity = '0';
    t.style.transform = 'translateY(8px)';
  }, 2500);
}
```

Toast element positioned: `bottom: 28px; right: 28px` (same on all pages).
