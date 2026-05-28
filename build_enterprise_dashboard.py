import json
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
DATA_PATH = BASE_DIR / "patent_hypergraph_data.json"
OUT_PATH = BASE_DIR / "index.html"


data = json.loads(DATA_PATH.read_text(encoding="utf-8"))
data_json = json.dumps(data, ensure_ascii=False, separators=(",", ":"))


html = r'''<!doctype html>
<html lang="it">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Patent Hypergraph Explorer | ECO RED Technology Intelligence</title>
  <style>
    :root {
      --navy-950: #07111f;
      --navy-900: #0b1728;
      --navy-800: #12233a;
      --navy-700: #183557;
      --ink: #162033;
      --muted: #667085;
      --muted-2: #8a95a8;
      --bg: #f4f7fb;
      --surface: #ffffff;
      --surface-soft: #f8fafc;
      --line: #dbe3ee;
      --line-soft: #e8eef5;
      --teal: #0f766e;
      --cyan: #0284c7;
      --blue: #2563eb;
      --violet: #7c3aed;
      --orange: #f97316;
      --green: #16a34a;
      --yellow: #ca8a04;
      --red: #dc2626;
      --shadow: 0 18px 45px rgba(15, 23, 42, .08);
      --shadow-soft: 0 8px 24px rgba(15, 23, 42, .06);
      --radius-xl: 16px;
      --radius-lg: 12px;
      --radius-md: 10px;
      --sidebar: 328px;
      --detail: 390px;
    }

    * { box-sizing: border-box; }
    html, body { height: 100%; }
    body {
      margin: 0;
      color: var(--ink);
      background: var(--bg);
      font-family: Inter, "IBM Plex Sans", "Source Sans 3", "Segoe UI", system-ui, -apple-system, BlinkMacSystemFont, sans-serif;
      line-height: 1.48;
      letter-spacing: 0;
    }

    button, input, select, textarea {
      font: inherit;
      letter-spacing: 0;
    }

    button {
      cursor: pointer;
    }

    .app-shell {
      min-height: 100vh;
      display: flex;
      flex-direction: column;
    }

    .topbar {
      background: linear-gradient(135deg, var(--navy-950), var(--navy-800));
      color: #fff;
      padding: 20px 28px 16px;
      border-bottom: 1px solid rgba(255, 255, 255, .08);
    }

    .topbar-main {
      display: grid;
      grid-template-columns: minmax(280px, 1fr) auto;
      gap: 24px;
      align-items: start;
    }

    .eyebrow {
      display: inline-flex;
      align-items: center;
      gap: 7px;
      color: #9bd7ff;
      font-size: 12px;
      font-weight: 800;
      text-transform: uppercase;
      letter-spacing: .08em;
      margin-bottom: 7px;
    }

    .eyebrow::before {
      content: "";
      width: 8px;
      height: 8px;
      border-radius: 50%;
      background: #22d3ee;
      box-shadow: 0 0 0 4px rgba(34, 211, 238, .16);
    }

    .topbar h1 {
      margin: 0;
      font-size: clamp(24px, 2.2vw, 32px);
      line-height: 1.12;
      font-weight: 760;
      letter-spacing: -.01em;
    }

    .topbar .subtitle {
      max-width: 850px;
      margin-top: 8px;
      color: #c8d5e6;
      font-size: 15px;
    }

    .header-actions {
      display: flex;
      align-items: center;
      justify-content: flex-end;
      gap: 10px;
      flex-wrap: wrap;
    }

    .btn {
      min-height: 38px;
      border: 1px solid transparent;
      border-radius: 10px;
      padding: 0 13px;
      display: inline-flex;
      align-items: center;
      justify-content: center;
      gap: 8px;
      background: #fff;
      color: var(--navy-900);
      font-size: 13px;
      font-weight: 760;
      box-shadow: 0 1px 0 rgba(15, 23, 42, .05);
      transition: transform .16s ease, background .16s ease, border .16s ease, color .16s ease, box-shadow .16s ease;
    }

    .btn:hover {
      transform: translateY(-1px);
      box-shadow: 0 8px 18px rgba(15, 23, 42, .12);
    }

    .btn.primary {
      background: #0ea5e9;
      color: #fff;
      border-color: rgba(255,255,255,.14);
    }

    .btn.ghost {
      background: rgba(255, 255, 255, .08);
      color: #e5eef9;
      border-color: rgba(255, 255, 255, .16);
    }

    .btn.secondary {
      background: var(--surface-soft);
      color: var(--ink);
      border-color: var(--line);
      box-shadow: none;
    }

    .btn.small {
      min-height: 32px;
      padding: 0 10px;
      font-size: 12px;
      border-radius: 8px;
    }

    .header-kpis {
      display: grid;
      grid-template-columns: repeat(6, minmax(92px, 1fr));
      gap: 10px;
      margin-top: 18px;
    }

    .header-kpi {
      padding: 12px 13px;
      border: 1px solid rgba(255, 255, 255, .12);
      border-radius: 14px;
      background: rgba(255, 255, 255, .07);
      backdrop-filter: blur(8px);
    }

    .header-kpi strong {
      display: block;
      font-size: 21px;
      line-height: 1.1;
      font-weight: 800;
      color: #fff;
    }

    .header-kpi span {
      display: block;
      margin-top: 4px;
      color: #b8c7da;
      font-size: 12px;
      font-weight: 650;
    }

    .main-nav {
      display: flex;
      gap: 6px;
      padding: 0 28px;
      background: #fff;
      border-bottom: 1px solid var(--line);
      box-shadow: 0 1px 0 rgba(15, 23, 42, .03);
      overflow-x: auto;
    }

    .nav-btn {
      appearance: none;
      border: 0;
      border-bottom: 3px solid transparent;
      background: transparent;
      color: #536174;
      padding: 16px 11px 13px;
      white-space: nowrap;
      font-size: 14px;
      font-weight: 760;
    }

    .nav-btn:hover { color: var(--navy-900); }
    .nav-btn.active {
      color: var(--blue);
      border-bottom-color: var(--blue);
    }

    .page {
      display: none;
      padding: 26px 28px 34px;
      flex: 1;
    }

    .page.active { display: block; }

    .section-head {
      display: flex;
      align-items: flex-end;
      justify-content: space-between;
      gap: 20px;
      margin-bottom: 18px;
    }

    .section-head h2 {
      margin: 0;
      font-size: 24px;
      line-height: 1.2;
      color: var(--navy-950);
    }

    .section-head p {
      margin: 6px 0 0;
      max-width: 860px;
      color: var(--muted);
      font-size: 15px;
    }

    .grid {
      display: grid;
      gap: 16px;
    }

    .grid.cols-4 { grid-template-columns: repeat(4, minmax(0, 1fr)); }
    .grid.cols-3 { grid-template-columns: repeat(3, minmax(0, 1fr)); }
    .grid.cols-2 { grid-template-columns: repeat(2, minmax(0, 1fr)); }
    .grid.overview { grid-template-columns: 1.15fr .85fr; align-items: start; }
    .grid.wide-left { grid-template-columns: 1.35fr .65fr; align-items: start; }

    .card {
      background: var(--surface);
      border: 1px solid var(--line);
      border-radius: var(--radius-xl);
      box-shadow: var(--shadow-soft);
      padding: 18px;
      min-width: 0;
    }

    .card.flush { padding: 0; overflow: hidden; }

    .card-title {
      display: flex;
      justify-content: space-between;
      align-items: center;
      gap: 12px;
      margin-bottom: 13px;
    }

    .card-title h3 {
      margin: 0;
      font-size: 17px;
      line-height: 1.25;
      color: var(--navy-950);
    }

    .card-title p {
      margin: 3px 0 0;
      color: var(--muted);
      font-size: 13px;
    }

    .metric-card {
      position: relative;
      overflow: hidden;
      min-height: 126px;
    }

    .metric-card::after {
      content: "";
      position: absolute;
      right: -36px;
      top: -36px;
      width: 110px;
      height: 110px;
      border-radius: 50%;
      background: rgba(37, 99, 235, .08);
    }

    .metric-label {
      color: var(--muted);
      font-size: 12px;
      font-weight: 800;
      text-transform: uppercase;
      letter-spacing: .05em;
    }

    .metric-value {
      margin-top: 10px;
      font-size: 30px;
      line-height: 1;
      font-weight: 820;
      color: var(--navy-950);
    }

    .metric-note {
      margin-top: 8px;
      color: var(--muted);
      font-size: 13px;
    }

    .insight-list {
      display: grid;
      gap: 10px;
    }

    .insight {
      display: grid;
      grid-template-columns: 28px minmax(0, 1fr);
      gap: 10px;
      padding: 12px;
      background: #f8fafc;
      border: 1px solid var(--line-soft);
      border-radius: 12px;
      color: #334155;
      font-size: 14px;
    }

    .insight i {
      width: 28px;
      height: 28px;
      border-radius: 8px;
      background: #e0f2fe;
      color: #0369a1;
      display: grid;
      place-items: center;
      font-style: normal;
      font-weight: 900;
    }

    .chart-list {
      display: grid;
      gap: 10px;
    }

    .bar-row {
      display: grid;
      grid-template-columns: minmax(120px, 1fr) minmax(120px, 1.3fr) 42px;
      gap: 10px;
      align-items: center;
      font-size: 13px;
      color: #334155;
    }

    .bar-label {
      overflow: hidden;
      white-space: nowrap;
      text-overflow: ellipsis;
      font-weight: 700;
    }

    .bar-track {
      height: 10px;
      border-radius: 999px;
      background: #eef2f7;
      overflow: hidden;
    }

    .bar-fill {
      height: 100%;
      border-radius: inherit;
      background: linear-gradient(90deg, var(--blue), #22d3ee);
    }

    .bar-value {
      text-align: right;
      color: var(--muted);
      font-weight: 760;
    }

    .focus-grid {
      display: grid;
      grid-template-columns: repeat(4, minmax(0, 1fr));
      gap: 12px;
    }

    .focus-card {
      border: 1px solid var(--line);
      border-radius: 14px;
      background: #fbfdff;
      padding: 14px;
    }

    .focus-card strong {
      display: block;
      font-size: 23px;
      color: var(--navy-950);
      line-height: 1.1;
    }

    .focus-card span {
      display: block;
      margin-top: 5px;
      color: var(--muted);
      font-size: 13px;
      font-weight: 700;
    }

    .network-layout {
      display: grid;
      grid-template-columns: var(--sidebar) minmax(520px, 1fr) var(--detail);
      gap: 16px;
      min-height: calc(100vh - 230px);
    }

    .panel {
      background: var(--surface);
      border: 1px solid var(--line);
      border-radius: var(--radius-xl);
      box-shadow: var(--shadow-soft);
      min-width: 0;
    }

    .filter-panel, .context-panel {
      overflow: hidden;
      display: flex;
      flex-direction: column;
      max-height: calc(100vh - 212px);
    }

    .panel-scroll {
      overflow: auto;
      padding: 16px;
    }

    .filter-block {
      border: 1px solid var(--line-soft);
      border-radius: 14px;
      margin-bottom: 12px;
      background: #fff;
      overflow: hidden;
    }

    .filter-block summary {
      list-style: none;
      cursor: pointer;
      padding: 13px 14px;
      font-weight: 800;
      font-size: 13px;
      color: var(--navy-900);
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 8px;
    }

    .filter-block summary::-webkit-details-marker { display: none; }
    .filter-block summary::after {
      content: "+";
      width: 22px;
      height: 22px;
      border-radius: 8px;
      background: #f1f5f9;
      display: grid;
      place-items: center;
      color: #64748b;
      font-weight: 900;
    }

    .filter-block[open] summary::after { content: "−"; }

    .filter-content {
      border-top: 1px solid var(--line-soft);
      padding: 14px;
    }

    .field {
      display: grid;
      gap: 7px;
      margin-bottom: 13px;
    }

    .field:last-child { margin-bottom: 0; }

    label, .label {
      color: #344054;
      font-size: 12px;
      font-weight: 820;
    }

    select, input[type="text"], input[type="number"] {
      width: 100%;
      min-height: 38px;
      border: 1px solid #cdd6e3;
      border-radius: 10px;
      background: #fff;
      color: var(--ink);
      padding: 0 11px;
      outline: none;
      font-size: 14px;
      transition: border .16s ease, box-shadow .16s ease;
    }

    select {
      appearance: none;
      background-image:
        linear-gradient(45deg, transparent 50%, #667085 50%),
        linear-gradient(135deg, #667085 50%, transparent 50%);
      background-position:
        calc(100% - 17px) 16px,
        calc(100% - 12px) 16px;
      background-size: 5px 5px, 5px 5px;
      background-repeat: no-repeat;
      padding-right: 34px;
    }

    select:focus, input:focus {
      border-color: #60a5fa;
      box-shadow: 0 0 0 4px rgba(37, 99, 235, .10);
    }

    .range-line {
      display: grid;
      grid-template-columns: 1fr auto;
      gap: 10px;
      align-items: center;
    }

    input[type="range"] {
      width: 100%;
      accent-color: var(--blue);
    }

    .range-value {
      min-width: 42px;
      text-align: right;
      color: var(--blue);
      font-weight: 840;
      font-size: 13px;
    }

    .field-row {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 10px;
    }

    .check-grid {
      display: grid;
      gap: 8px;
    }

    .check-card {
      display: flex;
      align-items: center;
      gap: 10px;
      min-height: 36px;
      padding: 8px 10px;
      border: 1px solid var(--line-soft);
      border-radius: 10px;
      background: var(--surface-soft);
      color: #344054;
      font-size: 13px;
      font-weight: 700;
    }

    .check-card input {
      width: 16px;
      height: 16px;
      accent-color: var(--blue);
      flex: 0 0 auto;
    }

    .hint {
      color: var(--muted);
      font-size: 13px;
      line-height: 1.45;
    }

    .graph-card {
      display: grid;
      grid-template-rows: auto minmax(520px, 1fr);
      overflow: hidden;
      min-height: calc(100vh - 212px);
    }

    .graph-top {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 14px;
      padding: 15px 16px;
      border-bottom: 1px solid var(--line);
      background: #fff;
    }

    .graph-title h3 {
      margin: 0;
      font-size: 16px;
      color: var(--navy-950);
    }

    .graph-title p {
      margin: 3px 0 0;
      color: var(--muted);
      font-size: 13px;
    }

    .graph-actions {
      display: flex;
      gap: 8px;
      flex-wrap: wrap;
      justify-content: flex-end;
    }

    .canvas-wrap {
      position: relative;
      min-height: 520px;
      background:
        radial-gradient(circle at 18% 14%, rgba(14, 165, 233, .08), transparent 30%),
        linear-gradient(180deg, #fbfdff, #f6f9fc);
    }

    #graphCanvas {
      display: block;
      width: 100%;
      height: 100%;
      min-height: 520px;
      cursor: grab;
    }

    #graphCanvas.dragging { cursor: grabbing; }

    .graph-status {
      position: absolute;
      left: 16px;
      top: 14px;
      display: flex;
      gap: 8px;
      flex-wrap: wrap;
      pointer-events: none;
    }

    .status-pill {
      display: inline-flex;
      align-items: center;
      gap: 6px;
      min-height: 28px;
      padding: 0 10px;
      border: 1px solid rgba(203, 213, 225, .8);
      border-radius: 999px;
      background: rgba(255,255,255,.86);
      color: #344054;
      font-size: 12px;
      font-weight: 780;
      backdrop-filter: blur(10px);
    }

    .empty-state {
      display: none;
      position: absolute;
      inset: 22px;
      place-items: center;
      text-align: center;
      color: var(--muted);
      background: rgba(255,255,255,.74);
      border: 1px dashed #cbd5e1;
      border-radius: 16px;
      padding: 24px;
    }

    .empty-state.show { display: grid; }
    .empty-state strong {
      display: block;
      color: var(--navy-950);
      font-size: 18px;
      margin-bottom: 6px;
    }

    .tooltip {
      position: fixed;
      z-index: 50;
      display: none;
      max-width: 320px;
      padding: 10px 12px;
      border: 1px solid var(--line);
      border-radius: 12px;
      background: rgba(255,255,255,.96);
      box-shadow: var(--shadow);
      pointer-events: none;
      color: #334155;
      font-size: 13px;
    }

    .tooltip strong {
      display: block;
      color: var(--navy-950);
      margin-bottom: 3px;
    }

    .context-tabs {
      display: grid;
      grid-template-columns: repeat(4, 1fr);
      gap: 4px;
      padding: 10px;
      border-bottom: 1px solid var(--line);
      background: #fff;
    }

    .tab-btn {
      border: 0;
      border-radius: 9px;
      background: transparent;
      color: #667085;
      min-height: 34px;
      font-size: 12px;
      font-weight: 800;
    }

    .tab-btn.active {
      background: #eaf2ff;
      color: var(--blue);
    }

    .tab-pane { display: none; }
    .tab-pane.active { display: block; }

    .guide-card {
      border: 1px solid var(--line-soft);
      border-radius: 14px;
      padding: 14px;
      background: #fbfdff;
      font-size: 14px;
      color: #344054;
    }

    .guide-card h3 {
      margin: 0 0 6px;
      font-size: 16px;
      color: var(--navy-950);
    }

    .guide-card p { margin: 6px 0; }
    .guide-card ul { margin: 8px 0 0 18px; padding: 0; }
    .guide-card li { margin: 5px 0; }

    .badge-row {
      display: flex;
      flex-wrap: wrap;
      gap: 6px;
    }

    .badge {
      display: inline-flex;
      align-items: center;
      gap: 6px;
      min-height: 24px;
      padding: 2px 8px;
      border: 1px solid var(--line);
      border-radius: 999px;
      background: #f8fafc;
      color: #344054;
      font-size: 12px;
      font-weight: 760;
      max-width: 100%;
    }

    .badge.blue { background: #eff6ff; color: #1d4ed8; border-color: #bfdbfe; }
    .badge.cyan { background: #ecfeff; color: #0e7490; border-color: #a5f3fc; }
    .badge.green { background: #ecfdf3; color: #15803d; border-color: #bbf7d0; }
    .badge.red { background: #fef2f2; color: #b91c1c; border-color: #fecaca; }
    .badge.orange { background: #fff7ed; color: #c2410c; border-color: #fed7aa; }

    .legend-grid {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 8px;
    }

    .legend-item {
      display: flex;
      align-items: center;
      gap: 8px;
      color: #344054;
      font-size: 13px;
      font-weight: 700;
    }

    .dot {
      width: 10px;
      height: 10px;
      border-radius: 50%;
      flex: 0 0 auto;
      background: #94a3b8;
    }

    .detail-stack {
      display: grid;
      gap: 12px;
    }

    .detail-row {
      border-bottom: 1px solid var(--line-soft);
      padding-bottom: 9px;
      color: #344054;
      font-size: 13px;
    }

    .detail-row b {
      display: block;
      color: var(--navy-950);
      font-size: 12px;
      margin-bottom: 4px;
      text-transform: uppercase;
      letter-spacing: .04em;
    }

    .table-toolbar {
      display: flex;
      justify-content: space-between;
      align-items: center;
      gap: 12px;
      padding: 14px;
      border-bottom: 1px solid var(--line);
      background: #fff;
    }

    .table-toolbar input, .table-toolbar select {
      max-width: 280px;
    }

    .table-wrap {
      overflow: auto;
      max-height: 560px;
    }

    table {
      width: 100%;
      border-collapse: collapse;
      font-size: 13px;
    }

    th, td {
      padding: 11px 12px;
      border-bottom: 1px solid var(--line-soft);
      text-align: left;
      vertical-align: top;
    }

    th {
      position: sticky;
      top: 0;
      z-index: 2;
      background: #f8fafc;
      color: #475467;
      font-size: 12px;
      text-transform: uppercase;
      letter-spacing: .04em;
      font-weight: 850;
      cursor: pointer;
    }

    tbody tr {
      transition: background .15s ease;
    }

    tbody tr:hover {
      background: #f8fbff;
    }

    .actor-cards {
      display: grid;
      grid-template-columns: repeat(3, minmax(0, 1fr));
      gap: 12px;
    }

    .actor-card {
      border: 1px solid var(--line);
      border-radius: 14px;
      background: #fff;
      padding: 14px;
      box-shadow: var(--shadow-soft);
    }

    .actor-card h4 {
      margin: 0;
      font-size: 15px;
      color: var(--navy-950);
      line-height: 1.25;
    }

    .actor-meta {
      display: flex;
      gap: 8px;
      flex-wrap: wrap;
      margin: 10px 0;
      color: var(--muted);
      font-size: 12px;
      font-weight: 760;
    }

    .mini-canvas {
      width: 100%;
      height: 360px;
      display: block;
      border: 1px solid var(--line);
      border-radius: 14px;
      background: #fbfdff;
    }

    .heatmap {
      display: grid;
      gap: 3px;
      overflow: auto;
      padding-bottom: 4px;
    }

    .heat-row {
      display: grid;
      grid-template-columns: 160px repeat(8, 52px);
      gap: 3px;
      align-items: center;
      font-size: 11px;
      color: #475467;
    }

    .heat-label {
      overflow: hidden;
      white-space: nowrap;
      text-overflow: ellipsis;
      font-weight: 760;
    }

    .heat-cell {
      height: 24px;
      border-radius: 6px;
      background: #eef2f7;
      display: grid;
      place-items: center;
      color: #0f172a;
      font-weight: 800;
    }

    .timeline {
      display: flex;
      align-items: flex-end;
      gap: 5px;
      height: 190px;
      padding: 12px 4px 2px;
      border-bottom: 1px solid var(--line);
    }

    .timeline-bar {
      flex: 1;
      min-width: 12px;
      border-radius: 8px 8px 0 0;
      background: linear-gradient(180deg, #38bdf8, #2563eb);
      position: relative;
    }

    .timeline-bar span {
      position: absolute;
      left: 50%;
      bottom: -24px;
      transform: translateX(-50%) rotate(-42deg);
      transform-origin: top left;
      color: var(--muted);
      font-size: 10px;
      white-space: nowrap;
    }

    .strategy-grid {
      display: grid;
      grid-template-columns: repeat(3, minmax(0, 1fr));
      gap: 14px;
    }

    .strategy-card {
      border: 1px solid var(--line);
      border-radius: 16px;
      background: #fff;
      padding: 16px;
      box-shadow: var(--shadow-soft);
    }

    .strategy-card h3 {
      margin: 0 0 8px;
      font-size: 17px;
      color: var(--navy-950);
    }

    .strategy-card p {
      margin: 0 0 12px;
      color: var(--muted);
      font-size: 14px;
    }

    .drawer-backdrop {
      position: fixed;
      inset: 0;
      display: none;
      background: rgba(7, 17, 31, .38);
      z-index: 70;
    }

    .drawer-backdrop.show { display: block; }

    .patent-drawer {
      position: fixed;
      right: 0;
      top: 0;
      bottom: 0;
      width: min(620px, 92vw);
      background: #fff;
      box-shadow: -22px 0 50px rgba(15, 23, 42, .20);
      transform: translateX(105%);
      transition: transform .24s ease;
      z-index: 80;
      display: flex;
      flex-direction: column;
    }

    .patent-drawer.show { transform: translateX(0); }

    .drawer-head {
      padding: 20px;
      background: var(--navy-950);
      color: #fff;
      display: flex;
      justify-content: space-between;
      gap: 14px;
      align-items: flex-start;
    }

    .drawer-head h2 {
      margin: 0;
      font-size: 20px;
      line-height: 1.25;
    }

    .drawer-body {
      padding: 20px;
      overflow: auto;
      display: grid;
      gap: 14px;
    }

    .close-btn {
      border: 1px solid rgba(255,255,255,.22);
      background: rgba(255,255,255,.10);
      color: #fff;
      width: 36px;
      height: 36px;
      border-radius: 10px;
      font-size: 20px;
      line-height: 1;
    }

    .help-panel {
      position: fixed;
      right: 24px;
      top: 96px;
      width: min(420px, calc(100vw - 48px));
      display: none;
      z-index: 60;
      background: #fff;
      border: 1px solid var(--line);
      border-radius: 16px;
      box-shadow: var(--shadow);
      padding: 18px;
    }

    .help-panel.show { display: block; }
    .help-panel h3 { margin: 0 0 8px; font-size: 18px; }
    .help-panel p { margin: 8px 0; color: #475467; font-size: 14px; }

    .toast {
      position: fixed;
      left: 50%;
      bottom: 22px;
      transform: translate(-50%, 24px);
      opacity: 0;
      pointer-events: none;
      z-index: 100;
      min-width: min(420px, calc(100vw - 32px));
      max-width: calc(100vw - 32px);
      border: 1px solid rgba(15, 23, 42, .12);
      border-radius: 14px;
      background: rgba(7, 17, 31, .94);
      color: #fff;
      box-shadow: var(--shadow);
      padding: 12px 14px;
      font-size: 14px;
      font-weight: 720;
      text-align: center;
      transition: opacity .18s ease, transform .18s ease;
    }

    .toast.show {
      opacity: 1;
      transform: translate(-50%, 0);
    }

    @media (max-width: 1360px) {
      .network-layout { grid-template-columns: 300px minmax(420px, 1fr); }
      .context-panel { grid-column: 1 / -1; max-height: none; }
      .context-tabs { grid-template-columns: repeat(4, minmax(100px, 1fr)); }
    }

    @media (max-width: 1180px) and (min-width: 769px) {
      .page { padding: 22px 20px 30px; }
      .topbar { padding: 18px 20px 15px; }
      .main-nav { padding: 0 20px; }
      .network-layout {
        display: flex;
        flex-direction: column;
      }
      .graph-card { order: 1; min-height: 72vh; }
      .filter-panel { order: 2; }
      .context-panel { order: 3; }
      .filter-panel .panel-scroll {
        display: grid;
        grid-template-columns: repeat(2, minmax(0, 1fr));
        gap: 12px;
      }
      .filter-block { margin-bottom: 0; }
      .canvas-wrap, #graphCanvas { min-height: 62vh; }
      .table-wrap { max-height: 62vh; }
    }

    @media (max-width: 1060px) {
      .topbar-main { grid-template-columns: 1fr; }
      .header-actions { justify-content: flex-start; }
      .header-kpis { grid-template-columns: repeat(3, 1fr); }
      .network-layout { grid-template-columns: 1fr; }
      .filter-panel, .context-panel { max-height: none; }
      .grid.cols-4, .grid.cols-3, .grid.cols-2, .grid.overview, .grid.wide-left,
      .focus-grid, .strategy-grid, .actor-cards { grid-template-columns: 1fr; }
      .section-head { align-items: flex-start; flex-direction: column; }
      .page { padding: 20px 16px 28px; }
      .topbar { padding: 18px 16px 14px; }
      .main-nav { padding: 0 16px; }
    }

    @media (max-width: 640px) {
      body { font-size: 15px; }
      .topbar h1 { font-size: 24px; }
      .topbar .subtitle { font-size: 14px; }
      .header-actions {
        display: grid;
        grid-template-columns: 1fr 1fr;
        width: 100%;
      }
      .header-actions .btn { width: 100%; min-height: 42px; }
      .header-kpis { grid-template-columns: repeat(2, 1fr); }
      .header-kpi { padding: 10px; }
      .header-kpi strong { font-size: 18px; }
      .main-nav {
        gap: 2px;
        padding: 0 10px;
      }
      .nav-btn {
        padding: 13px 9px 10px;
        font-size: 13px;
      }
      .page { padding: 16px 10px 24px; }
      .section-head h2 { font-size: 21px; }
      .card, .panel { border-radius: 13px; }
      .network-layout {
        display: flex;
        flex-direction: column;
        gap: 12px;
      }
      .graph-card { order: 1; min-height: 68vh; }
      .filter-panel { order: 2; }
      .context-panel { order: 3; }
      .canvas-wrap, #graphCanvas { min-height: 58vh; }
      .graph-top { align-items: flex-start; flex-direction: column; }
      .graph-actions {
        display: grid;
        grid-template-columns: 1fr 1fr;
        width: 100%;
      }
      .graph-actions .btn { width: 100%; min-height: 40px; }
      .graph-status {
        left: 10px;
        right: 10px;
        top: 10px;
      }
      .status-pill { font-size: 11px; min-height: 26px; }
      .filter-block summary { padding: 14px; font-size: 14px; }
      select, input[type="text"], input[type="number"] { min-height: 44px; font-size: 16px; }
      .check-card { min-height: 42px; }
      .table-toolbar { flex-direction: column; align-items: stretch; }
      .context-tabs { grid-template-columns: 1fr 1fr; }
      .context-tabs .tab-btn { min-height: 40px; }
      .patent-drawer {
        width: 100vw;
      }
      .drawer-head { padding: 16px; }
      .drawer-head h2 { font-size: 18px; }
      .drawer-body { padding: 14px; }
      .bar-row {
        grid-template-columns: minmax(90px, 1fr) minmax(90px, 1fr) 34px;
      }
      .heat-row {
        grid-template-columns: 132px repeat(8, 46px);
      }
    }
  </style>
</head>
<body>
  <div class="app-shell">
    <header class="topbar">
      <div class="topbar-main">
        <div>
          <div class="eyebrow">Technology Intelligence</div>
          <h1>Patent Hypergraph Explorer</h1>
          <div class="subtitle">Dashboard enterprise per esplorare brevetti CO₂ electrolysis, attori, tecnologie, citazioni e focus ECO RED: MEA, AEM, GDE e catalizzatori non nobili.</div>
        </div>
        <div class="header-actions">
          <button class="btn ghost" id="globalResetBtn" type="button">Reset vista</button>
          <button class="btn ghost" id="globalExportBtn" type="button">Export CSV</button>
          <button class="btn primary" id="helpBtn" type="button">Help</button>
        </div>
      </div>
      <div class="header-kpis" id="headerKpis"></div>
    </header>

    <nav class="main-nav" aria-label="Sezioni dashboard">
      <button class="nav-btn active" data-page="overview" type="button">Executive Overview</button>
      <button class="nav-btn" data-page="network" type="button">Network Explorer</button>
      <button class="nav-btn" data-page="actors" type="button">Actor Intelligence</button>
      <button class="nav-btn" data-page="technology" type="button">Technology Map</button>
      <button class="nav-btn" data-page="ecored" type="button">ECO RED Focus</button>
    </nav>

    <main>
      <section class="page active" id="page-overview">
        <div class="section-head">
          <div>
            <h2>Executive Overview</h2>
            <p>Una lettura immediata del panorama brevettuale: scala del dataset, attori principali, aree tecniche presidiate e segnali strategici utili prima di entrare nel grafo.</p>
          </div>
          <button class="btn secondary" data-page-target="network" type="button">Apri Network Explorer</button>
        </div>
        <div class="grid cols-4" id="overviewMetrics"></div>
        <div class="grid overview" style="margin-top:16px;">
          <div class="grid">
            <div class="card">
              <div class="card-title">
                <div>
                  <h3>Mini insight automatici</h3>
                  <p>Segnali sintetici derivati dai metadati brevettuali.</p>
                </div>
              </div>
              <div class="insight-list" id="overviewInsights"></div>
            </div>
            <div class="card">
              <div class="card-title">
                <div>
                  <h3>Focus ECO RED</h3>
                  <p>Presenza brevettuale delle aree più vicine al caso aziendale.</p>
                </div>
              </div>
              <div class="focus-grid" id="overviewFocus"></div>
            </div>
          </div>
          <div class="grid">
            <div class="card">
              <div class="card-title"><div><h3>Top assignee</h3><p>Attori con più famiglie brevettuali.</p></div></div>
              <div class="chart-list" id="topAssigneeBars"></div>
            </div>
            <div class="card">
              <div class="card-title"><div><h3>Top CPC group</h3><p>Macro-classi tecniche più presenti.</p></div></div>
              <div class="chart-list" id="topCpcBars"></div>
            </div>
            <div class="card">
              <div class="card-title"><div><h3>Top domini tecnologici</h3><p>Aggregazioni tecnologiche dominanti.</p></div></div>
              <div class="chart-list" id="topDomainBars"></div>
            </div>
          </div>
        </div>
      </section>

      <section class="page" id="page-network">
        <div class="section-head">
          <div>
            <h2>Network Explorer</h2>
            <p>Esplora l’ipergrafo e le sue proiezioni. Il grafo mostra connessioni tra brevetti, attori, tecnologie, concetti e citazioni.</p>
          </div>
        </div>

        <div class="network-layout">
          <aside class="panel filter-panel">
            <div class="panel-scroll">
              <details class="filter-block" open>
                <summary>Scelta vista</summary>
                <div class="filter-content">
                  <div class="field">
                    <label for="viewSelect">Proiezione</label>
                    <select id="viewSelect"></select>
                    <div class="hint" id="viewHint"></div>
                  </div>
                </div>
              </details>

              <details class="filter-block" open>
                <summary>Filtro anni</summary>
                <div class="filter-content">
                  <div class="field-row">
                    <div class="field">
                      <label for="yearMin">Da</label>
                      <input type="number" id="yearMin" />
                    </div>
                    <div class="field">
                      <label for="yearMax">A</label>
                      <input type="number" id="yearMax" />
                    </div>
                  </div>
                  <div class="hint">Usa anno di priorità quando disponibile, altrimenti anno del brevetto.</div>
                </div>
              </details>

              <details class="filter-block" open>
                <summary>Focus tecnologico</summary>
                <div class="filter-content">
                  <div class="check-grid">
                    <label class="check-card"><input type="checkbox" id="focusMEA" /> MEA</label>
                    <label class="check-card"><input type="checkbox" id="focusAEM" /> AEM</label>
                    <label class="check-card"><input type="checkbox" id="focusGDE" /> GDE</label>
                    <label class="check-card"><input type="checkbox" id="focusNonNoble" /> Catalizzatori non nobili</label>
                  </div>
                  <div class="hint" style="margin-top:10px;">Selezionando più focus vengono inclusi i brevetti che soddisfano almeno uno dei criteri.</div>
                </div>
              </details>

              <details class="filter-block" open>
                <summary>Ricerca</summary>
                <div class="filter-content">
                  <div class="field">
                    <label for="searchInput">Nodo, assignee, brevetto o keyword</label>
                    <input type="text" id="searchInput" list="searchSuggestions" placeholder="es. TOPSOE, C25B, membrane..." />
                    <datalist id="searchSuggestions"></datalist>
                  </div>
                  <label class="check-card"><input type="checkbox" id="showLabels" checked /> Mostra etichette principali</label>
                  <label class="check-card"><input type="checkbox" id="focusMode" /> Modalità focus sul selezionato</label>
                </div>
              </details>

              <details class="filter-block" open>
                <summary>Opzioni visuali</summary>
                <div class="filter-content">
                  <div class="field">
                    <div class="range-line"><label for="maxNodes">Massimo nodi</label><span class="range-value" id="maxNodesLabel"></span></div>
                    <input type="range" id="maxNodes" min="40" max="520" step="20" value="220" />
                  </div>
                  <div class="field">
                    <div class="range-line"><label for="minWeight">Peso minimo archi</label><span class="range-value" id="minWeightLabel"></span></div>
                    <input type="range" id="minWeight" min="1" max="16" step="1" value="1" />
                  </div>
                  <div class="field-row">
                    <button class="btn secondary small" id="resetGraphBtn" type="button">Reset view</button>
                    <button class="btn secondary small" id="isolateBtn" type="button">Isola vicini</button>
                  </div>
                  <button class="btn secondary small" id="clearIsolationBtn" type="button" style="width:100%; margin-top:8px;">Mostra rete completa</button>
                </div>
              </details>
            </div>
          </aside>

          <section class="panel graph-card">
            <div class="graph-top">
              <div class="graph-title">
                <h3 id="graphViewTitle">Network view</h3>
                <p id="graphViewSubtitle">Caricamento rete...</p>
              </div>
              <div class="graph-actions">
                <button class="btn secondary small" id="pauseBtn" type="button">Pausa layout</button>
                <button class="btn secondary small" id="fitBtn" type="button">Centra</button>
                <button class="btn secondary small" id="exportGraphBtn" type="button">Export archi</button>
              </div>
            </div>
            <div class="canvas-wrap">
              <canvas id="graphCanvas"></canvas>
              <div class="graph-status" id="graphStatus"></div>
              <div class="empty-state" id="graphEmpty">
                <div>
                  <strong>Nessun collegamento visualizzabile</strong>
                  <span>Riduci il peso minimo, amplia gli anni o rimuovi alcuni filtri tecnologici.</span>
                </div>
              </div>
              <div class="tooltip" id="graphTooltip"></div>
            </div>
          </section>

          <aside class="panel context-panel">
            <div class="context-tabs">
              <button class="tab-btn active" data-tab="details" type="button">Dettagli nodo</button>
              <button class="tab-btn" data-tab="guide" type="button">Guida</button>
              <button class="tab-btn" data-tab="insights" type="button">Insight</button>
              <button class="tab-btn" data-tab="legend" type="button">Legenda</button>
            </div>
            <div class="panel-scroll">
              <div class="tab-pane active" id="tab-details"></div>
              <div class="tab-pane" id="tab-guide"></div>
              <div class="tab-pane" id="tab-insights"></div>
              <div class="tab-pane" id="tab-legend"></div>
            </div>
          </aside>
        </div>
      </section>

      <section class="page" id="page-actors">
        <div class="section-head">
          <div>
            <h2>Actor Intelligence</h2>
            <p>Analisi degli assignee: chi brevetta di più, chi presidia i focus ECO RED, quali attori sono trasversali e chi può essere competitor o partner.</p>
          </div>
        </div>
        <div class="grid wide-left">
          <div class="grid">
            <div class="card">
              <div class="card-title">
                <div><h3>Assignee da monitorare</h3><p>Card sintetiche sui principali attori per volume e copertura tecnologica.</p></div>
              </div>
              <div class="actor-cards" id="actorCards"></div>
            </div>
            <div class="card flush">
              <div class="table-toolbar">
                <div>
                  <strong>Tabella assignee</strong>
                  <div class="hint">Cerca, ordina ed esporta l’elenco degli attori.</div>
                </div>
                <div style="display:flex; gap:8px; flex-wrap:wrap;">
                  <input type="text" id="actorSearch" placeholder="Cerca assignee..." />
                  <select id="actorFocusFilter"></select>
                  <select id="actorCountryFilter"></select>
                  <button class="btn secondary small" id="exportActorsBtn" type="button">Export</button>
                </div>
              </div>
              <div class="table-wrap"><table id="actorTable"></table></div>
            </div>
          </div>
          <div class="grid">
            <div class="card">
              <div class="card-title"><div><h3>Mini-grafo attori × tecnologie</h3><p>Assignee principali collegati ai CPC group più ricorrenti.</p></div></div>
              <canvas class="mini-canvas" id="actorMiniGraph"></canvas>
            </div>
            <div class="card">
              <div class="card-title"><div><h3>Scheda assignee</h3><p>Seleziona un attore dalla tabella o dal grafo.</p></div></div>
              <div id="actorDetail" class="detail-stack"></div>
            </div>
          </div>
        </div>
      </section>

      <section class="page" id="page-technology">
        <div class="section-head">
          <div>
            <h2>Technology Map</h2>
            <p>Mappa delle tecnologie brevettate: CPC, domini, concetti tecnici, frequenza, attori associati ed evoluzione temporale.</p>
          </div>
        </div>
        <div class="grid cols-2">
          <div class="card">
            <div class="card-title"><div><h3>Top CPC group</h3><p>Classificazioni tecniche più ricorrenti.</p></div></div>
            <div class="chart-list" id="techCpcBars"></div>
          </div>
          <div class="card">
            <div class="card-title"><div><h3>Timeline brevetti</h3><p>Distribuzione temporale per anno di priorità/pubblicazione.</p></div></div>
            <div class="timeline" id="patentTimeline"></div>
          </div>
        </div>
        <div class="grid cols-2" style="margin-top:16px;">
          <div class="card">
            <div class="card-title"><div><h3>Heatmap assignee × CPC</h3><p>Intensità del presidio tecnologico sui principali attori.</p></div></div>
            <div class="heatmap" id="techHeatmap"></div>
          </div>
          <div class="card">
            <div class="card-title"><div><h3>Cluster tecnologici</h3><p>Lettura manageriale dei gruppi più presenti.</p></div></div>
            <div class="insight-list" id="techClusters"></div>
          </div>
        </div>
        <div class="card flush" style="margin-top:16px;">
          <div class="table-toolbar">
            <div>
              <strong>Tabella tecnologie</strong>
              <div class="hint">CPC, domini e concetti tecnici aggregati.</div>
            </div>
            <div style="display:flex; gap:8px; flex-wrap:wrap;">
              <input type="text" id="techSearch" placeholder="Cerca tecnologia..." />
              <select id="techTypeFilter"></select>
              <button class="btn secondary small" id="exportTechBtn" type="button">Export</button>
            </div>
          </div>
          <div class="table-wrap"><table id="techTable"></table></div>
        </div>
      </section>

      <section class="page" id="page-ecored">
        <div class="section-head">
          <div>
            <h2>ECO RED Focus</h2>
            <p>Vista strategica su MEA, AEM, GDE e catalizzatori non nobili per individuare attori vicini, competitor, partner e white spaces.</p>
          </div>
          <button class="btn secondary" id="applyEcoGraphBtn" type="button">Apri grafo filtrato ECO RED</button>
        </div>
        <div class="focus-grid" id="ecoFocusCards"></div>
        <div class="strategy-grid" style="margin-top:16px;" id="ecoStrategyCards"></div>
        <div class="grid cols-2" style="margin-top:16px;">
          <div class="card flush">
            <div class="table-toolbar">
              <div><strong>Brevetti più pertinenti</strong><div class="hint">Famiglie marcate con focus MEA/AEM/GDE/non-noble.</div></div>
              <button class="btn secondary small" id="exportEcoPatentsBtn" type="button">Export</button>
            </div>
            <div class="table-wrap"><table id="ecoPatentTable"></table></div>
          </div>
          <div class="card flush">
            <div class="table-toolbar">
              <div><strong>Brevetti potenzialmente fondazionali</strong><div class="hint">Ordinati per citazioni interne ricevute.</div></div>
            </div>
            <div class="table-wrap"><table id="foundationalTable"></table></div>
          </div>
        </div>
      </section>
    </main>
  </div>

  <div class="drawer-backdrop" id="drawerBackdrop"></div>
  <aside class="patent-drawer" id="patentDrawer" aria-label="Dettaglio brevetto">
    <div class="drawer-head">
      <div>
        <div class="eyebrow">Patent detail</div>
        <h2 id="drawerTitle">Brevetto</h2>
      </div>
      <button class="close-btn" id="closeDrawerBtn" type="button" aria-label="Chiudi">×</button>
    </div>
    <div class="drawer-body" id="drawerBody"></div>
  </aside>

  <div class="help-panel" id="helpPanel">
    <h3>Come usare la dashboard</h3>
    <p>Parti da Executive Overview per una lettura manageriale, poi usa Network Explorer per esplorare relazioni e proiezioni dell’ipergrafo.</p>
    <p>Nel grafo, un nodo grande o centrale indica un elemento molto connesso. Seleziona un nodo per evidenziare il vicinato e aprire i dettagli.</p>
    <p>Le proiezioni semplificano l’ipergrafo: sono utili per leggere pattern, ma il brevetto resta l’unità informativa che collega più dimensioni.</p>
  </div>

  <div class="toast" id="toast" role="status" aria-live="polite"></div>

  <script>
    const DATA = __DATA_JSON__;

    const TYPE_COLORS = {
      patent: "#2563eb",
      assignee: "#7c3aed",
      cpc_group: "#f97316",
      cpc_code: "#fb923c",
      ipc_group: "#a855f7",
      ipc_code: "#c084fc",
      domain: "#16a34a",
      concept: "#0f766e",
      country: "#64748b",
      priority_year: "#ca8a04",
      legal_state: "#dc2626",
      focus: "#0284c7",
      unknown: "#94a3b8"
    };

    const TYPE_LABELS = {
      patent: "Brevetto",
      assignee: "Assignee",
      cpc_group: "CPC group",
      cpc_code: "CPC specifico",
      ipc_group: "IPC group",
      ipc_code: "IPC specifico",
      domain: "Dominio",
      concept: "Concetto",
      country: "Paese",
      priority_year: "Anno",
      legal_state: "Stato legale",
      focus: "Focus ECO RED",
      unknown: "Altro"
    };

    const VIEW_CONFIG = {
      hypergraph: {
        label: "Ipergrafo completo",
        mode: "incidence",
        relations: ["patent_assignee","patent_domain","patent_cpc_group","patent_concept","patent_country","patent_priority_year","patent_legal_state","patent_focus"],
        short: "Vista completa dei brevetti come hyperedge: ogni brevetto collega attori, tecnologie, concetti, paesi e focus.",
        useful: ["Orientarsi nel dataset completo", "Vedere quali brevetti collegano molte dimensioni", "Capire la complessità prima delle proiezioni"],
        caution: "Vista molto ricca: usa filtri e peso minimo per ridurre il rumore."
      },
      patent_assignee: {
        label: "Brevetti - assignee",
        mode: "incidence",
        relations: ["patent_assignee"],
        short: "Mostra chi possiede o richiede i brevetti.",
        useful: ["Identificare attori principali", "Rilevare co-assegnazioni", "Esplorare portafogli brevettuali"],
        caution: "Misura presenza brevettuale, non qualità tecnologica."
      },
      patent_cpc: {
        label: "Brevetti - CPC group",
        mode: "incidence",
        relations: ["patent_cpc_group"],
        short: "Collega ogni brevetto alle macro-classi tecnologiche CPC.",
        useful: ["Leggere aree tecnologiche dominanti", "Capire il perimetro tecnico", "Passare dal brevetto alla classificazione ufficiale"],
        caution: "I CPC group sono utili ma aggregati."
      },
      patent_concept: {
        label: "Brevetti - concetti tecnici",
        mode: "incidence",
        relations: ["patent_concept"],
        short: "Mostra i concetti tecnici ricorrenti associati ai brevetti.",
        useful: ["Capire di cosa parlano i brevetti", "Cercare termini vicini a ECO RED", "Individuare temi trasversali"],
        caution: "I concetti testuali possono contenere sinonimi e rumore."
      },
      assignee_cpc_group: {
        label: "Assignee - CPC group",
        mode: "projection",
        source: "assignee_cpc_group",
        short: "Collega attori e macro-classi CPC quando compaiono negli stessi brevetti.",
        useful: ["Vedere chi lavora su quali tecnologie", "Identificare competitor", "Individuare specializzazioni e aree presidiate"],
        caution: "Il link è derivato: il brevetto specifico che lo genera resta nascosto finché non selezioni il nodo."
      },
      assignee_cpc_code: {
        label: "Assignee - CPC specifici",
        mode: "projection",
        source: "assignee_cpc_code",
        short: "Proiezione dettagliata tra assignee e codici CPC granulari.",
        useful: ["Approfondire sottosistemi tecnici", "Distinguere nicchie brevettuali", "Analizzare specializzazioni fini"],
        caution: "Più dettagliata e più densa: alza il peso minimo se necessario."
      },
      assignee_domain: {
        label: "Assignee - domini",
        mode: "projection",
        source: "assignee_domain",
        short: "Mostra quali attori presidiano domini tecnologici ampi.",
        useful: ["Vista introduttiva per non esperti", "Confrontare attori per dominio", "Capire convergenze tra energia, chimica e materiali"],
        caution: "I domini sono aggregati: perdono dettaglio tecnico."
      },
      domain_cpc_group: {
        label: "Domini - CPC group",
        mode: "projection",
        source: "domain_cpc_group",
        short: "Collega domini tecnologici e classificazioni CPC ufficiali.",
        useful: ["Tradurre domini descrittivi in CPC", "Leggere convergenze tecniche", "Spiegare dove si colloca CO₂-to-CO"],
        caution: "Non identifica direttamente competitor."
      },
      concept_cpc_group: {
        label: "Concetti - CPC group",
        mode: "projection",
        source: "concept_cpc_group",
        short: "Mostra quali concetti tecnici sono associati alle macro-classi CPC.",
        useful: ["Interpretare cluster tecnici", "Capire parole chiave caratterizzanti", "Individuare concetti trasversali"],
        caution: "Vista esplorativa basata anche su testo."
      },
      assignee_country: {
        label: "Assignee - paesi",
        mode: "projection",
        source: "assignee_country",
        short: "Collega assignee e paesi associati ai brevetti.",
        useful: ["Leggere geografia brevettuale", "Individuare mercati protetti", "Capire copertura internazionale"],
        caution: "Il paese non coincide sempre con il luogo produttivo."
      },
      focus_assignee: {
        label: "Focus ECO RED - assignee",
        mode: "projection",
        source: "focus_assignee",
        short: "Mostra quali attori sono collegati a MEA, AEM, GDE e catalizzatori non nobili.",
        useful: ["Trovare attori vicini a ECO RED", "Individuare competitor e partner", "Prioritizzare monitoraggio strategico"],
        caution: "I focus sono uno screening: verifica i brevetti rilevanti."
      },
      citation: {
        label: "Citazioni brevetto - brevetto",
        mode: "citation",
        short: "Mostra quali brevetti citano altri brevetti.",
        useful: ["Individuare brevetti fondazionali", "Leggere traiettorie tecnologiche", "Capire dipendenze tra invenzioni"],
        caution: "Le citazioni dipendono anche dalle pratiche brevettuali."
      }
    };

    const nodeMap = new Map(DATA.nodes.map(n => [n.id, n]));
    const hyperedgeMap = new Map(DATA.hyperedges.map(h => [h.id, h]));
    const patentNodeToHyperedge = new Map(DATA.hyperedges.map(h => [h.patent_node, h]));

    const app = {
      page: "overview",
      selectedNode: null,
      selectedActor: null,
      isolatedNodeId: null,
      graph: {
        nodes: [],
        edges: [],
        nodeIndex: new Map(),
        transform: { x: 0, y: 0, scale: 1 },
        draggingNode: null,
        panning: false,
        lastPointer: null,
        hovered: null,
        paused: false,
        didDrag: false
      },
      tables: {},
      stats: {}
    };

    const el = {};
    let canvas, ctx;

    function init() {
      cacheElements();
      app.stats = buildStats();
      setupControls();
      renderHeaderKpis();
      renderOverview();
      renderActorsPage();
      renderTechnologyPage();
      renderEcoPage();
      attachEvents();
      resizeCanvas();
      rebuildGraph();
      requestAnimationFrame(tick);
    }

    function cacheElements() {
      canvas = document.getElementById("graphCanvas");
      ctx = canvas.getContext("2d");
      [
        "headerKpis","overviewMetrics","overviewInsights","overviewFocus","topAssigneeBars","topCpcBars","topDomainBars",
        "viewSelect","viewHint","yearMin","yearMax","maxNodes","minWeight","maxNodesLabel","minWeightLabel",
        "focusMEA","focusAEM","focusGDE","focusNonNoble","searchInput","searchSuggestions","showLabels","focusMode",
        "graphStatus","graphViewTitle","graphViewSubtitle","graphEmpty","graphTooltip","tab-details","tab-guide","tab-insights","tab-legend",
        "actorCards","actorSearch","actorFocusFilter","actorCountryFilter","actorTable","actorDetail","actorMiniGraph",
        "techCpcBars","patentTimeline","techHeatmap","techClusters","techSearch","techTypeFilter","techTable",
        "ecoFocusCards","ecoStrategyCards","ecoPatentTable","foundationalTable","patentDrawer","drawerBackdrop","drawerTitle","drawerBody","helpPanel","toast"
      ].forEach(id => el[id] = document.getElementById(id));
    }

    function setupControls() {
      el.viewSelect.innerHTML = Object.entries(VIEW_CONFIG)
        .map(([key, v]) => `<option value="${key}">${escapeHtml(v.label)}</option>`).join("");
      el.yearMin.value = DATA.summary.year_min || "";
      el.yearMax.value = DATA.summary.year_max || "";
      updateRangeLabels();
      populateSearchSuggestions();
      populateActorFilters();
      populateTechnologyFilters();
    }

    function attachEvents() {
      document.querySelectorAll(".nav-btn").forEach(btn => btn.addEventListener("click", () => showPage(btn.dataset.page)));
      document.querySelectorAll("[data-page-target]").forEach(btn => btn.addEventListener("click", () => showPage(btn.dataset.pageTarget)));
      document.querySelectorAll(".tab-btn").forEach(btn => btn.addEventListener("click", () => activateContextTab(btn.dataset.tab)));
      ["viewSelect","yearMin","yearMax","maxNodes","minWeight","focusMEA","focusAEM","focusGDE","focusNonNoble","searchInput","showLabels","focusMode"]
        .forEach(id => el[id].addEventListener("input", () => {
          updateRangeLabels();
          if (id !== "showLabels") rebuildGraph();
        }));
      document.getElementById("resetGraphBtn").addEventListener("click", resetGraphView);
      document.getElementById("globalResetBtn").addEventListener("click", resetGraphView);
      document.getElementById("fitBtn").addEventListener("click", resetGraphView);
      document.getElementById("pauseBtn").addEventListener("click", () => {
        app.graph.paused = !app.graph.paused;
        document.getElementById("pauseBtn").textContent = app.graph.paused ? "Riprendi layout" : "Pausa layout";
      });
      document.getElementById("isolateBtn").addEventListener("click", isolateSelectedNode);
      document.getElementById("clearIsolationBtn").addEventListener("click", () => {
        app.isolatedNodeId = null;
        rebuildGraph();
      });
      document.getElementById("exportGraphBtn").addEventListener("click", () => exportRows(app.graph.edges, [
        {key:"source", label:"Source ID"},
        {key:"source_label", label:"Source", export: row => labelFor(row.source)},
        {key:"target", label:"Target ID"},
        {key:"target_label", label:"Target", export: row => labelFor(row.target)},
        {key:"weight", label:"Weight"},
        {key:"relation", label:"Relation"},
        {key:"patents", label:"Brevetti collegati", export: row => row.patents || []}
      ], "graph_edges.csv"));
      document.getElementById("globalExportBtn").addEventListener("click", () => exportRows(DATA.hyperedges, patentColumns(), "patents.csv"));
      document.getElementById("helpBtn").addEventListener("click", () => el.helpPanel.classList.toggle("show"));
      document.getElementById("applyEcoGraphBtn").addEventListener("click", () => {
        showPage("network");
        el.viewSelect.value = "focus_assignee";
        el.focusMEA.checked = true;
        el.focusAEM.checked = true;
        el.focusGDE.checked = true;
        el.focusNonNoble.checked = true;
        rebuildGraph();
      });
      document.getElementById("closeDrawerBtn").addEventListener("click", closePatentDrawer);
      el.drawerBackdrop.addEventListener("click", closePatentDrawer);
      document.getElementById("exportActorsBtn").addEventListener("click", () => exportRows(filteredActorRows(), actorColumns(), "assignee_intelligence.csv"));
      document.getElementById("exportTechBtn").addEventListener("click", () => exportRows(filteredTechnologyRows(), technologyColumns(), "technology_map.csv"));
      document.getElementById("exportEcoPatentsBtn").addEventListener("click", () => exportRows(ecoPatentRows(), patentColumns(), "eco_red_focus_patents.csv"));
      ["actorSearch","actorFocusFilter","actorCountryFilter"].forEach(id => el[id].addEventListener("input", renderActorTable));
      ["techSearch","techTypeFilter"].forEach(id => el[id].addEventListener("input", renderTechnologyTable));
      window.addEventListener("resize", () => {
        resizeCanvas();
        drawActorMiniGraph();
      });
      canvas.addEventListener("pointerdown", pointerDown);
      canvas.addEventListener("pointermove", pointerMove);
      canvas.addEventListener("pointerup", pointerUp);
      canvas.addEventListener("pointerleave", pointerUp);
      canvas.addEventListener("wheel", onWheel, { passive: false });
      canvas.addEventListener("click", onCanvasClick);
    }

    function showPage(page) {
      app.page = page;
      document.querySelectorAll(".page").forEach(p => p.classList.remove("active"));
      document.getElementById(`page-${page}`).classList.add("active");
      document.querySelectorAll(".nav-btn").forEach(btn => btn.classList.toggle("active", btn.dataset.page === page));
      if (page === "network") {
        resizeCanvas();
        resetGraphView(false);
      }
      if (page === "actors") drawActorMiniGraph();
    }

    function buildStats() {
      const citationsByPatent = {};
      for (const h of DATA.hyperedges) citationsByPatent[h.id] = { in: 0, out: 0, weightIn: 0, weightOut: 0 };
      for (const c of DATA.citationEdges || []) {
        const source = cleanPatentId(c.source);
        const target = cleanPatentId(c.target);
        const w = Number(c.weight || 1);
        if (citationsByPatent[source]) { citationsByPatent[source].out += 1; citationsByPatent[source].weightOut += w; }
        if (citationsByPatent[target]) { citationsByPatent[target].in += 1; citationsByPatent[target].weightIn += w; }
      }

      const actors = new Map();
      const cpc = new Map();
      const cpcCodes = new Map();
      const domains = new Map();
      const concepts = new Map();
      const countries = new Map();
      const focus = new Map();
      const years = new Map();

      for (const h of DATA.hyperedges) {
        const y = patentYear(h);
        if (y) inc(years, y);
        (h.cpc_groups || []).forEach(x => inc(cpc, x));
        (h.cpc_codes || []).forEach(x => inc(cpcCodes, x));
        (h.domains || []).forEach(x => inc(domains, x));
        (h.concepts || []).forEach(x => inc(concepts, x));
        (h.countries || []).forEach(x => inc(countries, x));
        (h.focus || []).forEach(x => inc(focus, x));
        (h.assignees || []).forEach(name => {
          if (!actors.has(name)) {
            actors.set(name, {
              name,
              patents: new Set(),
              domains: new Map(),
              cpc: new Map(),
              cpcCodes: new Map(),
              countries: new Map(),
              focus: new Map(),
              concepts: new Map(),
              citationsIn: 0,
              citationsOut: 0,
              relevantPatents: []
            });
          }
          const a = actors.get(name);
          a.patents.add(h.id);
          (h.domains || []).forEach(x => inc(a.domains, x));
          (h.cpc_groups || []).forEach(x => inc(a.cpc, x));
          (h.cpc_codes || []).forEach(x => inc(a.cpcCodes, x));
          (h.countries || []).forEach(x => inc(a.countries, x));
          (h.focus || []).forEach(x => inc(a.focus, x));
          (h.concepts || []).slice(0, 12).forEach(x => inc(a.concepts, x));
          a.citationsIn += citationsByPatent[h.id]?.weightIn || 0;
          a.citationsOut += citationsByPatent[h.id]?.weightOut || 0;
          a.relevantPatents.push(h);
        });
      }

      const actorRows = Array.from(actors.values()).map(a => ({
        name: a.name,
        patents: a.patents.size,
        domains: topKeys(a.domains, 4),
        cpc: topKeys(a.cpc, 5),
        cpcCodes: topKeys(a.cpcCodes, 5),
        countries: topKeys(a.countries, 5),
        focus: topKeys(a.focus, 5),
        concepts: topKeys(a.concepts, 6),
        citationsIn: a.citationsIn,
        citationsOut: a.citationsOut,
        relevantPatents: a.relevantPatents.sort((x, y) => (citationsByPatent[y.id]?.weightIn || 0) - (citationsByPatent[x.id]?.weightIn || 0))
      })).sort((a, b) => b.patents - a.patents || b.citationsIn - a.citationsIn);

      const techRows = [
        ...mapToRows(cpc, "CPC group"),
        ...mapToRows(cpcCodes, "CPC specifico"),
        ...mapToRows(domains, "Dominio"),
        ...mapToRows(concepts, "Concetto")
      ].map(r => ({ ...r, actors: actorsForTech(r.name).slice(0, 8) }));

      function actorsForTech(value) {
        const list = [];
        for (const a of actorRows) {
          if (a.domains.includes(value) || a.cpc.includes(value) || a.cpcCodes.includes(value) || a.concepts.includes(value)) list.push(a.name);
        }
        return list;
      }

      return {
        citationsByPatent,
        actors: actorRows,
        cpc: mapToRows(cpc, "CPC group"),
        cpcCodes: mapToRows(cpcCodes, "CPC specifico"),
        domains: mapToRows(domains, "Dominio"),
        concepts: mapToRows(concepts, "Concetto"),
        countries: mapToRows(countries, "Paese"),
        focus: mapToRows(focus, "Focus"),
        years: mapToRows(years, "Anno").sort((a, b) => Number(a.name) - Number(b.name)),
        technologies: techRows.sort((a, b) => b.count - a.count),
        ecoPatents: DATA.hyperedges.filter(h => (h.focus || []).some(f => ["MEA","AEM","GDE","Non-noble candidate"].includes(f)))
      };
    }

    function renderHeaderKpis() {
      const s = DATA.summary;
      const kpis = [
        ["Brevetti", fmt(s.patents)],
        ["Assignee", fmt(s.node_type_counts.assignee || app.stats.actors.length)],
        ["Nodi", fmt(s.nodes)],
        ["Collegamenti", fmt(s.incidence_edges)],
        ["Citazioni", fmt(s.citation_edges)],
        ["Periodo", `${s.year_min}-${s.year_max}`]
      ];
      el.headerKpis.innerHTML = kpis.map(([label, value]) => `<div class="header-kpi"><strong>${value}</strong><span>${label}</span></div>`).join("");
    }

    function renderOverview() {
      const metrics = [
        ["Totale brevetti", DATA.summary.patents, "Famiglie brevettuali nel dataset"],
        ["Assignee", DATA.summary.node_type_counts.assignee, "Aziende, università ed enti"],
        ["CPC group", DATA.summary.node_type_counts.cpc_group, "Macro-classi tecniche"],
        ["Citazioni interne", DATA.summary.citation_edges, "Link brevetto-brevetto"]
      ];
      el.overviewMetrics.innerHTML = metrics.map(([label, value, note]) => `
        <div class="card metric-card">
          <div class="metric-label">${escapeHtml(label)}</div>
          <div class="metric-value">${fmt(value)}</div>
          <div class="metric-note">${escapeHtml(note)}</div>
        </div>
      `).join("");

      const topActor = app.stats.actors[0];
      const topCpc = app.stats.cpc[0];
      const topDomain = app.stats.domains[0];
      const ecoShare = Math.round((app.stats.ecoPatents.length / DATA.hyperedges.length) * 100);
      const alive = DATA.hyperedges.filter(h => String(h.legal_state || "").toUpperCase() === "ALIVE").length;
      const insights = [
        `Il dataset copre ${DATA.summary.patents} brevetti tra ${DATA.summary.year_min} e ${DATA.summary.year_max}, con ${DATA.summary.citation_edges} citazioni interne utilizzabili.`,
        `${topActor?.name || "n.d."} è l'assignee più presente per numero di brevetti nel dataset.`,
        `La classe CPC più frequente è ${topCpc?.name || "n.d."}, segnale di forte concentrazione su elettrolisi e sistemi elettrochimici.`,
        `Circa ${ecoShare}% dei brevetti contiene almeno un focus vicino a ECO RED: MEA, AEM, GDE o catalizzatori non nobili.`,
        `${alive} brevetti risultano marcati come ALIVE, quindi potenzialmente ancora rilevanti per libertà operativa e monitoraggio competitivo.`
      ];
      el.overviewInsights.innerHTML = insights.map((text, i) => `<div class="insight"><i>${i + 1}</i><div>${escapeHtml(text)}</div></div>`).join("");
      renderFocusCards(el.overviewFocus);
      renderBars(el.topAssigneeBars, app.stats.actors.map(a => ({ name: a.name, count: a.patents })).slice(0, 8), "blue");
      renderBars(el.topCpcBars, app.stats.cpc.slice(0, 8), "orange");
      renderBars(el.topDomainBars, app.stats.domains.slice(0, 8), "green");
    }

    function renderFocusCards(container) {
      const focusMap = Object.fromEntries(app.stats.focus.map(f => [f.name, f.count]));
      const cards = [
        ["MEA", focusMap.MEA || 0, "Membrane electrode assembly"],
        ["AEM", focusMap.AEM || 0, "Anion exchange membrane"],
        ["GDE", focusMap.GDE || 0, "Gas diffusion electrode"],
        ["Non-noble", focusMap["Non-noble candidate"] || 0, "Catalizzatori non nobili"]
      ];
      container.innerHTML = cards.map(([label, value, note]) => `
        <div class="focus-card"><strong>${fmt(value)}</strong><span>${escapeHtml(label)}</span><div class="hint">${escapeHtml(note)}</div></div>
      `).join("");
    }

    function renderBars(container, rows, tone = "blue") {
      const max = Math.max(1, ...rows.map(r => r.count || 0));
      const color = tone === "orange" ? "linear-gradient(90deg,#f97316,#fbbf24)" : tone === "green" ? "linear-gradient(90deg,#16a34a,#2dd4bf)" : "linear-gradient(90deg,#2563eb,#22d3ee)";
      container.innerHTML = rows.map(r => `
        <div class="bar-row" title="${escapeHtml(r.name)}">
          <div class="bar-label">${escapeHtml(r.name)}</div>
          <div class="bar-track"><div class="bar-fill" style="width:${Math.max(3, (r.count / max) * 100)}%; background:${color};"></div></div>
          <div class="bar-value">${fmt(r.count)}</div>
        </div>
      `).join("");
    }

    function renderActorsPage() {
      const top = app.stats.actors.slice(0, 6);
      el.actorCards.innerHTML = top.map(a => actorCard(a)).join("");
      el.actorCards.querySelectorAll("[data-actor]").forEach(btn => btn.addEventListener("click", () => selectActor(btn.dataset.actor)));
      renderActorTable();
      selectActor(top[0]?.name || null);
      drawActorMiniGraph();
    }

    function actorCard(a) {
      const posture = classifyActor(a);
      return `
        <article class="actor-card">
          <h4>${escapeHtml(a.name)}</h4>
          <div class="actor-meta">
            <span>${fmt(a.patents)} brevetti</span>
            <span>${fmt(a.citationsIn)} citazioni in</span>
          </div>
          <div class="badge-row">${chips(a.focus, 5)}${badge(posture, posture === "Possibile partner" ? "green" : posture === "Competitor da monitorare" ? "red" : "blue")}</div>
          <div class="hint" style="margin-top:10px;">Domini: ${escapeHtml(a.domains.slice(0, 3).join(", ") || "n.d.")}</div>
          <button class="btn secondary small" data-actor="${escapeHtml(a.name)}" type="button" style="margin-top:12px;">Apri scheda</button>
        </article>
      `;
    }

    function populateActorFilters() {
      const focusOptions = ["", "MEA", "AEM", "GDE", "Non-noble candidate"];
      el.actorFocusFilter.innerHTML = focusOptions.map(f => `<option value="${escapeHtml(f)}">${f ? escapeHtml(f) : "Tutti i focus"}</option>`).join("");
      const countries = unique(app.stats?.actors?.flatMap(a => a.countries) || []);
      el.actorCountryFilter.innerHTML = ["", ...countries].map(c => `<option value="${escapeHtml(c)}">${c ? escapeHtml(c) : "Tutti i paesi"}</option>`).join("");
    }

    function filteredActorRows() {
      const q = (el.actorSearch?.value || "").trim().toLowerCase();
      const focus = el.actorFocusFilter?.value || "";
      const country = el.actorCountryFilter?.value || "";
      return app.stats.actors.filter(a => {
        if (q && !a.name.toLowerCase().includes(q)) return false;
        if (focus && !a.focus.includes(focus)) return false;
        if (country && !a.countries.includes(country)) return false;
        return true;
      });
    }

    function actorColumns() {
      return [
        { key: "name", label: "Assignee" },
        { key: "patents", label: "Brevetti" },
        { key: "focus", label: "Focus", render: r => chips(r.focus, 4) },
        { key: "domains", label: "Domini", render: r => chips(r.domains, 3) },
        { key: "cpc", label: "CPC group", render: r => chips(r.cpc, 4) },
        { key: "countries", label: "Paesi", render: r => chips(r.countries, 4) },
        { key: "citationsIn", label: "Citazioni in" },
        { key: "role", label: "Lettura", render: r => badge(classifyActor(r), classifyActor(r) === "Possibile partner" ? "green" : classifyActor(r) === "Competitor da monitorare" ? "red" : "blue") }
      ];
    }

    function renderActorTable() {
      renderTable("actorTable", filteredActorRows(), actorColumns(), {
        tableKey: "actors",
        onRowClick: row => selectActor(row.name)
      });
    }

    function selectActor(name) {
      if (!name) {
        el.actorDetail.innerHTML = `<div class="hint">Nessun assignee selezionato.</div>`;
        return;
      }
      const a = app.stats.actors.find(x => x.name === name);
      if (!a) return;
      app.selectedActor = a;
      const patents = a.relevantPatents.slice(0, 6).map(h => `<li><button class="btn secondary small" data-patent="${h.id}" type="button">${escapeHtml(h.id)}</button> ${escapeHtml(truncate(h.title, 70))}</li>`).join("");
      el.actorDetail.innerHTML = `
        <div class="detail-row"><b>Assignee</b>${escapeHtml(a.name)}</div>
        <div class="detail-row"><b>Numero brevetti</b>${fmt(a.patents)}</div>
        <div class="detail-row"><b>Lettura strategica</b>${badge(classifyActor(a), classifyActor(a) === "Possibile partner" ? "green" : classifyActor(a) === "Competitor da monitorare" ? "red" : "blue")}</div>
        <div class="detail-row"><b>Focus tecnologici</b><div class="badge-row">${chips(a.focus, 8)}</div></div>
        <div class="detail-row"><b>Domini principali</b><div class="badge-row">${chips(a.domains, 8)}</div></div>
        <div class="detail-row"><b>CPC principali</b><div class="badge-row">${chips(a.cpc, 8)}</div></div>
        <div class="detail-row"><b>Paesi</b><div class="badge-row">${chips(a.countries, 8)}</div></div>
        <div class="detail-row"><b>Brevetti più rilevanti</b><ul>${patents}</ul></div>
      `;
      el.actorDetail.querySelectorAll("[data-patent]").forEach(btn => btn.addEventListener("click", () => openPatentDrawer(btn.dataset.patent)));
    }

    function drawActorMiniGraph() {
      const c = el.actorMiniGraph;
      if (!c) return;
      const dpr = window.devicePixelRatio || 1;
      const rect = c.getBoundingClientRect();
      c.width = Math.max(320, rect.width * dpr);
      c.height = Math.max(280, rect.height * dpr);
      const g = c.getContext("2d");
      g.setTransform(dpr, 0, 0, dpr, 0, 0);
      const w = rect.width || 480, h = rect.height || 360;
      g.clearRect(0, 0, w, h);
      g.fillStyle = "#fbfdff"; g.fillRect(0, 0, w, h);
      const actors = app.stats.actors.slice(0, 8);
      const cpcs = app.stats.cpc.slice(0, 7);
      const leftX = 32, rightX = w - 70;
      actors.forEach((a, i) => {
        a._x = leftX;
        a._y = 36 + i * ((h - 72) / Math.max(1, actors.length - 1));
      });
      cpcs.forEach((cpc, i) => {
        cpc._x = rightX;
        cpc._y = 36 + i * ((h - 72) / Math.max(1, cpcs.length - 1));
      });
      for (const a of actors) {
        for (const cpc of cpcs) {
          if (!a.cpc.includes(cpc.name)) continue;
          const weight = a.relevantPatents.filter(p => (p.cpc_groups || []).includes(cpc.name)).length;
          g.strokeStyle = `rgba(37,99,235,${Math.min(.45, .08 + weight * .06)})`;
          g.lineWidth = Math.max(1, Math.min(5, weight));
          g.beginPath(); g.moveTo(a._x + 8, a._y); g.lineTo(cpc._x - 8, cpc._y); g.stroke();
        }
      }
      actors.forEach(a => drawMiniNode(g, a._x, a._y, TYPE_COLORS.assignee, truncate(a.name, 18)));
      cpcs.forEach(cpc => drawMiniNode(g, cpc._x, cpc._y, TYPE_COLORS.cpc_group, cpc.name));
    }

    function drawMiniNode(g, x, y, color, label) {
      g.fillStyle = color; g.beginPath(); g.arc(x, y, 7, 0, Math.PI * 2); g.fill();
      g.fillStyle = "#334155"; g.font = "12px Inter, Segoe UI, sans-serif"; g.textBaseline = "middle";
      g.fillText(label, x + 12, y);
    }

    function renderTechnologyPage() {
      renderBars(el.techCpcBars, app.stats.cpc.slice(0, 12), "orange");
      renderTimeline();
      renderHeatmap();
      renderTechClusters();
      renderTechnologyTable();
    }

    function populateTechnologyFilters() {
      if (!el.techTypeFilter) return;
      const types = ["", "CPC group", "CPC specifico", "Dominio", "Concetto"];
      el.techTypeFilter.innerHTML = types.map(t => `<option value="${escapeHtml(t)}">${t || "Tutte le tecnologie"}</option>`).join("");
    }

    function filteredTechnologyRows() {
      const q = (el.techSearch?.value || "").trim().toLowerCase();
      const type = el.techTypeFilter?.value || "";
      return app.stats.technologies.filter(r => {
        if (q && !r.name.toLowerCase().includes(q)) return false;
        if (type && r.type !== type) return false;
        return true;
      });
    }

    function technologyColumns() {
      return [
        { key: "name", label: "Tecnologia" },
        { key: "type", label: "Tipo" },
        { key: "count", label: "Frequenza" },
        { key: "actors", label: "Attori associati", render: r => chips(r.actors || [], 5) }
      ];
    }

    function renderTechnologyTable() {
      renderTable("techTable", filteredTechnologyRows(), technologyColumns(), { tableKey: "technology" });
    }

    function renderTimeline() {
      const rows = app.stats.years;
      const max = Math.max(1, ...rows.map(r => r.count));
      el.patentTimeline.innerHTML = rows.map(r => `
        <div class="timeline-bar" style="height:${Math.max(6, (r.count / max) * 160)}px;" title="${r.name}: ${r.count}">
          <span>${escapeHtml(r.name)}</span>
        </div>
      `).join("");
    }

    function renderHeatmap() {
      const actors = app.stats.actors.slice(0, 10);
      const cpcs = app.stats.cpc.slice(0, 8).map(x => x.name);
      const header = `<div class="heat-row"><div></div>${cpcs.map(c => `<div class="heat-label" title="${escapeHtml(c)}">${escapeHtml(c)}</div>`).join("")}</div>`;
      const rows = actors.map(a => {
        const cells = cpcs.map(c => {
          const v = a.relevantPatents.filter(p => (p.cpc_groups || []).includes(c)).length;
          const alpha = v ? Math.min(.95, .12 + v * .12) : .04;
          return `<div class="heat-cell" style="background:rgba(37,99,235,${alpha}); color:${v > 3 ? "#fff" : "#0f172a"}">${v || ""}</div>`;
        }).join("");
        return `<div class="heat-row"><div class="heat-label" title="${escapeHtml(a.name)}">${escapeHtml(a.name)}</div>${cells}</div>`;
      }).join("");
      el.techHeatmap.innerHTML = header + rows;
    }

    function renderTechClusters() {
      const clusters = [
        ["Electrolysis core", "C25B domina la mappa e segnala il cuore elettrochimico della tecnologia CO₂-to-CO."],
        ["Surface and materials", "Domini come surface technology e materials indicano forte attenzione a elettrodi, coating e catalizzatori."],
        ["System integration", "CPC collegati a energia, celle e apparati suggeriscono traiettorie verso stack e dispositivi industriali."],
        ["ECO RED adjacency", "MEA, AEM, GDE e non-noble sono segnali utili per isolare attori vicini al perimetro startup."]
      ];
      el.techClusters.innerHTML = clusters.map((c, i) => `<div class="insight"><i>${i + 1}</i><div><strong>${escapeHtml(c[0])}</strong><br>${escapeHtml(c[1])}</div></div>`).join("");
    }

    function renderEcoPage() {
      renderFocusCards(el.ecoFocusCards);
      const focusActors = app.stats.actors.filter(a => a.focus.some(f => ["MEA","AEM","GDE","Non-noble candidate"].includes(f)));
      const competitors = focusActors.filter(a => a.patents >= 4).slice(0, 8);
      const partners = focusActors.filter(a => a.patents <= 3 && a.focus.length >= 2).slice(0, 8);
      const nonNoble = focusActors.filter(a => a.focus.includes("Non-noble candidate")).slice(0, 8);
      const cards = [
        ["Attori da monitorare", "Soggetti con volume brevettuale e focus vicini al perimetro ECO RED.", focusActors.slice(0, 7).map(a => a.name)],
        ["Possibili competitor", "Attori con portafogli più ampi su focus rilevanti.", competitors.map(a => a.name)],
        ["Possibili partner", "Attori focalizzati e meno estesi, potenzialmente compatibili con collaborazioni.", partners.map(a => a.name)],
        ["Tecnologie presidiate", "Focus più presenti nella porzione ECO RED del dataset.", app.stats.focus.map(f => `${f.name} (${f.count})`)],
        ["Aree meno affollate", "Combinazioni con meno presidio relativo da verificare come white spaces.", whiteSpaces()],
        ["Brevetti fondazionali", "Brevetti ECO RED-like con più citazioni interne ricevute.", ecoPatentRows().slice(0, 5).map(h => `${h.id} - ${truncate(h.title, 42)}`)]
      ];
      el.ecoStrategyCards.innerHTML = cards.map(([title, text, items]) => `
        <div class="strategy-card">
          <h3>${escapeHtml(title)}</h3>
          <p>${escapeHtml(text)}</p>
          <div class="badge-row">${chips(items, 8)}</div>
        </div>
      `).join("");
      renderTable("ecoPatentTable", ecoPatentRows(), patentColumns(), {
        tableKey: "ecoPatents",
        onRowClick: row => openPatentDrawer(row.id)
      });
      renderTable("foundationalTable", ecoPatentRows().slice(0, 25), [
        { key: "id", label: "Brevetto" },
        { key: "title", label: "Titolo", render: r => escapeHtml(truncate(r.title, 80)) },
        { key: "assignees", label: "Assignee", render: r => chips(r.assignees, 3) },
        { key: "citationsIn", label: "Citazioni in" },
        { key: "focus", label: "Focus", render: r => chips(r.focus, 4) }
      ], {
        tableKey: "foundational",
        onRowClick: row => openPatentDrawer(row.id)
      });
    }

    function ecoPatentRows() {
      return app.stats.ecoPatents.map(h => ({
        ...h,
        citationsIn: app.stats.citationsByPatent[h.id]?.weightIn || 0,
        citationsOut: app.stats.citationsByPatent[h.id]?.weightOut || 0
      })).sort((a, b) => b.citationsIn - a.citationsIn || patentYear(b) - patentYear(a));
    }

    function whiteSpaces() {
      const focusCounts = Object.fromEntries(app.stats.focus.map(f => [f.name, f.count]));
      const candidates = [
        ["AEM + non-noble", DATA.hyperedges.filter(h => h.focus?.includes("AEM") && h.focus?.includes("Non-noble candidate")).length],
        ["MEA + GDE", DATA.hyperedges.filter(h => h.focus?.includes("MEA") && h.focus?.includes("GDE")).length],
        ["AEM + GDE", DATA.hyperedges.filter(h => h.focus?.includes("AEM") && h.focus?.includes("GDE")).length],
        ["MEA + AEM", DATA.hyperedges.filter(h => h.focus?.includes("MEA") && h.focus?.includes("AEM")).length]
      ].sort((a, b) => a[1] - b[1]);
      return candidates.map(([label, count]) => `${label}: ${count}`);
    }

    function selectedPatents() {
      const minYear = Number(el.yearMin.value) || -Infinity;
      const maxYear = Number(el.yearMax.value) || Infinity;
      const focus = [];
      if (el.focusMEA.checked) focus.push("MEA");
      if (el.focusAEM.checked) focus.push("AEM");
      if (el.focusGDE.checked) focus.push("GDE");
      if (el.focusNonNoble.checked) focus.push("Non-noble candidate");
      const selected = new Set();
      for (const h of DATA.hyperedges) {
        const y = patentYear(h);
        if (y && (y < minYear || y > maxYear)) continue;
        if (focus.length && !focus.some(f => (h.focus || []).includes(f))) continue;
        selected.add(h.id);
      }
      return selected;
    }

    function rebuildGraph() {
      const viewKey = el.viewSelect.value;
      const config = VIEW_CONFIG[viewKey];
      const patentSet = selectedPatents();
      const minWeight = Number(el.minWeight.value) || 1;
      const maxNodes = Number(el.maxNodes.value) || 220;
      let rawEdges = [];
      el.viewHint.textContent = config.short;
      el.graphViewTitle.textContent = config.label;
      el.graphViewSubtitle.textContent = config.short;

      if (config.mode === "incidence") {
        const relations = new Set(config.relations);
        rawEdges = DATA.incidenceEdges
          .filter(e => patentSet.has(e.patent) && relations.has(e.relation))
          .map(e => ({ source: e.source, target: e.target, weight: 1, directed: false, patents: [e.patent], relation: e.relation }));
      } else if (config.mode === "projection") {
        rawEdges = (DATA.projectionEdges[config.source] || [])
          .map(e => {
            const patents = (e.patents || []).filter(p => patentSet.has(p));
            return { source: e.source, target: e.target, weight: patents.length, directed: false, patents, relation: config.source };
          })
          .filter(e => e.weight >= minWeight);
      } else if (config.mode === "citation") {
        rawEdges = (DATA.citationEdges || [])
          .filter(e => patentSet.has(cleanPatentId(e.source)) && patentSet.has(cleanPatentId(e.target)))
          .filter(e => (e.weight || 1) >= minWeight)
          .map(e => ({ ...e, directed: true, relation: "citation", patents: e.patents || [cleanPatentId(e.source), cleanPatentId(e.target)] }));
      }

      const search = el.searchInput.value.trim().toLowerCase();
      if (search.length >= 2) {
        rawEdges = filterEdgesBySearch(rawEdges, search);
      }

      if (app.isolatedNodeId || (el.focusMode.checked && app.selectedNode)) {
        const id = app.isolatedNodeId || app.selectedNode.id;
        rawEdges = rawEdges.filter(e => e.source === id || e.target === id);
      }

      const degree = new Map();
      for (const e of rawEdges) {
        degree.set(e.source, (degree.get(e.source) || 0) + (e.weight || 1));
        degree.set(e.target, (degree.get(e.target) || 0) + (e.weight || 1));
      }

      let candidateNodes = Array.from(degree.keys()).map(id => {
        const base = nodeMap.get(id) || { id, label: id, type: "unknown", count: 1, meta: {} };
        return { ...base, degree: degree.get(id) || 0 };
      }).sort((a, b) => b.degree - a.degree || (b.count || 0) - (a.count || 0));

      const keep = new Set(candidateNodes.slice(0, maxNodes).map(n => n.id));
      rawEdges = rawEdges.filter(e => keep.has(e.source) && keep.has(e.target));

      const old = app.graph.nodeIndex;
      const finalIds = new Set();
      rawEdges.forEach(e => { finalIds.add(e.source); finalIds.add(e.target); });
      const finalNodes = Array.from(finalIds).map(id => {
        const base = nodeMap.get(id) || { id, label: id, type: "unknown", count: 1, meta: {} };
        const prev = old.get(id);
        return {
          ...base,
          degree: degree.get(id) || 0,
          x: prev?.x ?? Math.random() * Math.max(600, canvas.clientWidth),
          y: prev?.y ?? Math.random() * Math.max(420, canvas.clientHeight),
          vx: 0, vy: 0, fixed: false
        };
      });

      app.graph.nodes = finalNodes;
      app.graph.edges = rawEdges;
      app.graph.nodeIndex = new Map(finalNodes.map(n => [n.id, n]));
      app.graph.edges.forEach(e => { e.s = app.graph.nodeIndex.get(e.source); e.t = app.graph.nodeIndex.get(e.target); });
      app.graph.edges = app.graph.edges.filter(e => e.s && e.t);
      initializePositions();
      updateGraphPanels();
      el.graphEmpty.classList.toggle("show", app.graph.edges.length === 0);
    }

    function filterEdgesBySearch(edges, q) {
      const matches = new Set();
      const patentMatches = new Set();
      for (const n of DATA.nodes) {
        if ((n.label || "").toLowerCase().includes(q) || (n.id || "").toLowerCase().includes(q)) matches.add(n.id);
      }
      for (const h of DATA.hyperedges) {
        const text = [h.id, h.title, ...(h.assignees || []), ...(h.concepts || []), ...(h.cpc_groups || []), ...(h.focus || [])].join(" ").toLowerCase();
        if (text.includes(q)) {
          patentMatches.add(h.id);
          matches.add(h.patent_node);
        }
      }
      return edges.filter(e =>
        matches.has(e.source) || matches.has(e.target) ||
        (e.patents || []).some(p => patentMatches.has(p))
      );
    }

    function initializePositions() {
      const w = canvas.clientWidth || 900;
      const h = canvas.clientHeight || 620;
      const byType = new Map();
      for (const n of app.graph.nodes) {
        if (!byType.has(n.type)) byType.set(n.type, []);
        byType.get(n.type).push(n);
      }
      const types = Array.from(byType.keys());
      types.forEach((type, i) => {
        const angle = (i / Math.max(1, types.length)) * Math.PI * 2;
        const cx = w / 2 + Math.cos(angle) * w * .20;
        const cy = h / 2 + Math.sin(angle) * h * .20;
        for (const n of byType.get(type)) {
          if (!Number.isFinite(n.x) || !Number.isFinite(n.y) || n.x < -w || n.y < -h) {
            n.x = cx + (Math.random() - .5) * w * .22;
            n.y = cy + (Math.random() - .5) * h * .22;
          }
        }
      });
    }

    function updateGraphPanels() {
      const view = VIEW_CONFIG[el.viewSelect.value];
      el.graphStatus.innerHTML = [
        `${app.graph.nodes.length} nodi`,
        `${app.graph.edges.length} archi`,
        `peso ≥ ${el.minWeight.value}`,
        app.isolatedNodeId ? "nodo isolato" : null
      ].filter(Boolean).map(x => `<span class="status-pill">${escapeHtml(x)}</span>`).join("");
      renderContextGuide(view);
      renderContextInsights();
      renderLegend();
      renderSelectedNode();
    }

    function renderContextGuide(view) {
      const modeText = view.mode === "projection"
        ? "Questa è una proiezione: il collegamento è derivato da brevetti che condividono due dimensioni."
        : view.mode === "citation"
          ? "Questa è una rete diretta: la freccia va dal brevetto citante al brevetto citato."
          : "Questa è una rete di incidenza: il collegamento è presente direttamente nel brevetto.";
      el["tab-guide"].innerHTML = `
        <div class="guide-card">
          <h3>${escapeHtml(view.label)}</h3>
          <p>${escapeHtml(view.short)}</p>
          <p><b>Come leggere i link:</b> ${escapeHtml(modeText)}</p>
          <p><b>Utile per:</b></p>
          <ul>${(view.useful || []).map(x => `<li>${escapeHtml(x)}</li>`).join("")}</ul>
          <p class="hint" style="margin-top:12px;"><b>Nota:</b> ${escapeHtml(view.caution || "")}</p>
        </div>
      `;
    }

    function renderContextInsights() {
      const topNodes = app.graph.nodes.slice().sort((a,b) => b.degree - a.degree).slice(0, 8);
      const topEdges = app.graph.edges.slice().sort((a,b) => (b.weight || 1) - (a.weight || 1)).slice(0, 8);
      el["tab-insights"].innerHTML = `
        <div class="guide-card">
          <h3>Insight della vista</h3>
          <p>Questi elementi sono i più connessi nella vista corrente. Sono buoni punti di partenza per l’esplorazione.</p>
        </div>
        <h3>Top nodi</h3>
        <div class="detail-stack">${topNodes.map(n => `<div class="detail-row"><b>${escapeHtml(TYPE_LABELS[n.type] || n.type)}</b>${escapeHtml(n.label)}<br><span class="hint">grado ${Math.round(n.degree || 0)}</span></div>`).join("") || `<div class="hint">Nessun nodo.</div>`}</div>
        <h3>Top collegamenti</h3>
        <div class="detail-stack">${topEdges.map(e => `<div class="detail-row"><b>Peso ${e.weight || 1}</b>${escapeHtml(labelFor(e.source))} → ${escapeHtml(labelFor(e.target))}</div>`).join("") || `<div class="hint">Nessun arco.</div>`}</div>
      `;
    }

    function renderLegend() {
      const types = ["patent","assignee","cpc_group","cpc_code","domain","concept","country","priority_year","legal_state","focus"];
      el["tab-legend"].innerHTML = `
        <div class="guide-card">
          <h3>Legenda nodi</h3>
          <div class="legend-grid">
            ${types.map(t => `<div class="legend-item"><i class="dot" style="background:${TYPE_COLORS[t]}"></i>${escapeHtml(TYPE_LABELS[t])}</div>`).join("")}
          </div>
        </div>
      `;
    }

    function renderSelectedNode() {
      const n = app.selectedNode;
      if (!n || !app.graph.nodeIndex.has(n.id)) {
        el["tab-details"].innerHTML = `
          <div class="guide-card">
            <h3>Nessun nodo selezionato</h3>
            <p>Clicca un nodo nel grafo per vedere dettagli, brevetti collegati e ruolo nell’ipergrafo.</p>
            <p class="hint">Suggerimento: parti da una vista semplice come Assignee - domini, poi passa ad Assignee - CPC group.</p>
          </div>
        `;
        return;
      }
      if (n.type === "patent") {
        const h = patentNodeToHyperedge.get(n.id);
        el["tab-details"].innerHTML = patentSummaryHtml(h, true);
        el["tab-details"].querySelector("[data-open-patent]")?.addEventListener("click", () => openPatentDrawer(h.id));
        return;
      }
      const connectedPatentIds = connectedPatentsForNode(n.id).slice(0, 12);
      const patents = connectedPatentIds.map(id => {
        const h = hyperedgeMap.get(id);
        return h ? `<li><button class="btn secondary small" data-patent="${id}" type="button">${escapeHtml(id)}</button> ${escapeHtml(truncate(h.title, 70))}</li>` : "";
      }).join("");
      el["tab-details"].innerHTML = `
        <div class="detail-stack">
          <div class="detail-row"><b>Nome</b>${escapeHtml(n.label)}</div>
          <div class="detail-row"><b>Tipo</b>${escapeHtml(TYPE_LABELS[n.type] || n.type)}</div>
          <div class="detail-row"><b>Grado nella vista</b>${Math.round(n.degree || 0)}</div>
          <div class="detail-row"><b>Brevetti collegati</b><ul>${patents || "<li>Nessun brevetto mostrato nella vista corrente.</li>"}</ul></div>
        </div>
      `;
      el["tab-details"].querySelectorAll("[data-patent]").forEach(btn => btn.addEventListener("click", () => openPatentDrawer(btn.dataset.patent)));
    }

    function patentSummaryHtml(h, includeButton = false) {
      if (!h) return `<div class="hint">Brevetto non trovato.</div>`;
      const cits = app.stats.citationsByPatent[h.id] || { in: 0, out: 0, weightIn: 0, weightOut: 0 };
      return `
        <div class="detail-stack">
          <div class="detail-row"><b>Numero brevetto</b>${escapeHtml(h.id)}</div>
          <div class="detail-row"><b>Titolo</b>${escapeHtml(h.title || "")}</div>
          <div class="detail-row"><b>Anno</b>${patentYear(h) || "n.d."}</div>
          <div class="detail-row"><b>Assignee</b><div class="badge-row">${chips(h.assignees, 8)}</div></div>
          <div class="detail-row"><b>Stato legale</b>${badge(h.legal_state || "n.d.", String(h.legal_state).toUpperCase() === "ALIVE" ? "green" : "red")}</div>
          <div class="detail-row"><b>Paesi</b><div class="badge-row">${chips(h.countries, 8)}</div></div>
          <div class="detail-row"><b>CPC</b><div class="badge-row">${chips([...(h.cpc_groups || []), ...(h.cpc_codes || []).slice(0, 8)], 12)}</div></div>
          <div class="detail-row"><b>Domini</b><div class="badge-row">${chips(h.domains, 8)}</div></div>
          <div class="detail-row"><b>Concetti tecnici</b><div class="badge-row">${chips(h.concepts, 14)}</div></div>
          <div class="detail-row"><b>Focus tecnologico</b><div class="badge-row">${chips(h.focus, 8)}</div></div>
          <div class="detail-row"><b>Citazioni interne</b>${fmt(cits.weightIn)} ricevute · ${fmt(cits.weightOut)} in uscita</div>
          <div class="guide-card">
            <h3>Perché è una hyperedge</h3>
            <p>Questo brevetto collega simultaneamente questi attori, queste tecnologie e questi concetti. Per questo nell’ipergrafo agisce come una hyperedge: non è solo un nodo, ma un ponte tra più dimensioni informative.</p>
          </div>
          ${includeButton ? `<button class="btn primary" data-open-patent="${h.id}" type="button">Apri scheda completa</button>` : ""}
        </div>
      `;
    }

    function openPatentDrawer(id) {
      const h = hyperedgeMap.get(cleanPatentId(id));
      if (!h) return;
      el.drawerTitle.textContent = `${h.id} · ${truncate(h.title || "Brevetto", 80)}`;
      const related = relatedGraphLinks(h).slice(0, 18);
      el.drawerBody.innerHTML = `
        ${patentSummaryHtml(h, false)}
        <div class="card" style="box-shadow:none;">
          <div class="card-title"><div><h3>Collegamenti generati nell'ipergrafo</h3><p>Dimensioni informative collegate da questo brevetto.</p></div></div>
          <div class="badge-row">${chips(related, 18)}</div>
        </div>
      `;
      el.drawerBackdrop.classList.add("show");
      el.patentDrawer.classList.add("show");
    }

    function closePatentDrawer() {
      el.drawerBackdrop.classList.remove("show");
      el.patentDrawer.classList.remove("show");
    }

    function relatedGraphLinks(h) {
      return [
        ...(h.assignees || []).map(x => `Assignee: ${x}`),
        ...(h.cpc_groups || []).map(x => `CPC: ${x}`),
        ...(h.domains || []).map(x => `Dominio: ${x}`),
        ...(h.focus || []).map(x => `Focus: ${x}`),
        ...(h.countries || []).map(x => `Paese: ${x}`)
      ];
    }

    function connectedPatentsForNode(nodeId) {
      const ids = new Set();
      for (const e of app.graph.edges) {
        if (e.source === nodeId || e.target === nodeId) (e.patents || []).forEach(p => ids.add(p));
      }
      for (const h of DATA.hyperedges) if ((h.nodes || []).includes(nodeId)) ids.add(h.id);
      return Array.from(ids);
    }

    function resizeCanvas() {
      if (!canvas) return;
      const rect = canvas.getBoundingClientRect();
      const dpr = window.devicePixelRatio || 1;
      canvas.width = Math.max(360, Math.floor(rect.width * dpr));
      canvas.height = Math.max(360, Math.floor(rect.height * dpr));
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    }

    function tick() {
      if (!app.graph.paused && app.page === "network") simulateGraph();
      drawGraph();
      requestAnimationFrame(tick);
    }

    function simulateGraph() {
      const nodes = app.graph.nodes;
      const edges = app.graph.edges;
      if (!nodes.length) return;
      const w = canvas.clientWidth || 900, h = canvas.clientHeight || 620;
      const centerX = w / 2, centerY = h / 2;
      for (const e of edges) {
        const s = e.s, t = e.t;
        if (!s || !t) continue;
        const dx = t.x - s.x, dy = t.y - s.y;
        const dist = Math.max(24, Math.hypot(dx, dy));
        const desired = 72 + Math.min(120, 18 * Math.log1p(e.weight || 1));
        const force = (dist - desired) * 0.006;
        const fx = (dx / dist) * force, fy = (dy / dist) * force;
        if (!s.fixed) { s.vx += fx; s.vy += fy; }
        if (!t.fixed) { t.vx -= fx; t.vy -= fy; }
      }
      for (let i = 0; i < nodes.length; i++) {
        for (let j = i + 1; j < nodes.length; j++) {
          const a = nodes[i], b = nodes[j];
          const dx = b.x - a.x, dy = b.y - a.y;
          const dist2 = Math.max(80, dx * dx + dy * dy);
          const force = Math.min(2.8, 620 / dist2);
          const dist = Math.sqrt(dist2);
          const fx = (dx / dist) * force, fy = (dy / dist) * force;
          if (!a.fixed) { a.vx -= fx; a.vy -= fy; }
          if (!b.fixed) { b.vx += fx; b.vy += fy; }
        }
      }
      for (const n of nodes) {
        if (!n.fixed) {
          n.vx += (centerX - n.x) * 0.0009;
          n.vy += (centerY - n.y) * 0.0009;
          n.vx *= 0.86; n.vy *= 0.86;
          n.x += n.vx; n.y += n.vy;
        }
      }
    }

    function drawGraph() {
      if (!ctx || app.page !== "network") return;
      const w = canvas.clientWidth || 900, h = canvas.clientHeight || 620;
      ctx.clearRect(0, 0, w, h);
      ctx.save();
      ctx.translate(app.graph.transform.x, app.graph.transform.y);
      ctx.scale(app.graph.transform.scale, app.graph.transform.scale);
      const selected = app.selectedNode?.id;
      const neighborSet = selected ? selectedNeighborhood(selected) : null;
      for (const e of app.graph.edges) drawEdge(e, neighborSet);
      for (const n of app.graph.nodes) drawNode(n, neighborSet);
      ctx.restore();
    }

    function drawEdge(e, neighborSet) {
      const s = e.s, t = e.t;
      if (!s || !t) return;
      const selectedRelated = !neighborSet || (neighborSet.has(s.id) && neighborSet.has(t.id));
      ctx.strokeStyle = e.directed
        ? `rgba(71,85,105,${selectedRelated ? .34 : .055})`
        : `rgba(37,99,235,${selectedRelated ? .25 : .045})`;
      ctx.lineWidth = Math.max(.6, Math.min(4.2, Math.log1p(e.weight || 1))) / app.graph.transform.scale;
      ctx.beginPath();
      ctx.moveTo(s.x, s.y);
      const mx = (s.x + t.x) / 2, my = (s.y + t.y) / 2;
      ctx.quadraticCurveTo(mx, my, t.x, t.y);
      ctx.stroke();
      if (e.directed && selectedRelated) drawArrow(s, t);
    }

    function drawArrow(s, t) {
      const angle = Math.atan2(t.y - s.y, t.x - s.x);
      const r = nodeRadius(t) + 3;
      const x = t.x - Math.cos(angle) * r;
      const y = t.y - Math.sin(angle) * r;
      ctx.fillStyle = "rgba(71,85,105,.52)";
      ctx.beginPath();
      ctx.moveTo(x, y);
      ctx.lineTo(x - Math.cos(angle - .45) * 9, y - Math.sin(angle - .45) * 9);
      ctx.lineTo(x - Math.cos(angle + .45) * 9, y - Math.sin(angle + .45) * 9);
      ctx.closePath();
      ctx.fill();
    }

    function drawNode(n, neighborSet) {
      const selected = app.selectedNode?.id === n.id;
      const hovered = app.graph.hovered?.id === n.id;
      const related = !neighborSet || neighborSet.has(n.id);
      const r = nodeRadius(n);
      ctx.globalAlpha = related ? 1 : .22;
      ctx.beginPath();
      ctx.fillStyle = TYPE_COLORS[n.type] || TYPE_COLORS.unknown;
      ctx.arc(n.x, n.y, r, 0, Math.PI * 2);
      ctx.fill();
      ctx.lineWidth = selected ? 4 / app.graph.transform.scale : hovered ? 3 / app.graph.transform.scale : 1.6 / app.graph.transform.scale;
      ctx.strokeStyle = selected ? "#0f172a" : hovered ? "#38bdf8" : "rgba(255,255,255,.92)";
      ctx.stroke();
      if (el.showLabels.checked && (selected || hovered || (n.degree || 0) >= labelThreshold())) drawLabel(n, r);
      ctx.globalAlpha = 1;
    }

    function drawLabel(n, r) {
      const scale = app.graph.transform.scale;
      ctx.font = `${Math.max(10, 12 / Math.sqrt(scale))}px Inter, Segoe UI, sans-serif`;
      ctx.textBaseline = "middle";
      const text = truncate(n.label, n.type === "patent" ? 16 : 24);
      const width = ctx.measureText(text).width + 12;
      const x = n.x + r + 6, y = n.y;
      ctx.fillStyle = "rgba(255,255,255,.88)";
      roundRect(ctx, x - 4, y - 10, width, 20, 7);
      ctx.fill();
      ctx.fillStyle = "#263241";
      ctx.fillText(text, x + 2, y);
    }

    function nodeRadius(n) {
      const base = n.type === "patent" ? 6 : n.type === "assignee" ? 8 : n.type === "focus" ? 9 : 6;
      return base + Math.min(12, Math.log1p(n.degree || 1) * 2.2);
    }

    function labelThreshold() {
      return Math.max(4, app.graph.nodes.length / 42);
    }

    function selectedNeighborhood(id) {
      const set = new Set([id]);
      for (const e of app.graph.edges) {
        if (e.source === id) set.add(e.target);
        if (e.target === id) set.add(e.source);
      }
      return set;
    }

    function pointerDown(ev) {
      const p = screenToWorldEvent(ev);
      const n = nodeAtWorld(p.x, p.y);
      app.graph.didDrag = false;
      if (n) {
        app.graph.draggingNode = n;
        n.fixed = true;
      } else {
        app.graph.panning = true;
      }
      app.graph.lastPointer = { x: ev.clientX, y: ev.clientY };
      canvas.classList.add("dragging");
    }

    function pointerMove(ev) {
      if (app.graph.draggingNode) {
        const p = screenToWorldEvent(ev);
        app.graph.draggingNode.x = p.x;
        app.graph.draggingNode.y = p.y;
        app.graph.didDrag = true;
      } else if (app.graph.panning && app.graph.lastPointer) {
        app.graph.transform.x += ev.clientX - app.graph.lastPointer.x;
        app.graph.transform.y += ev.clientY - app.graph.lastPointer.y;
        app.graph.lastPointer = { x: ev.clientX, y: ev.clientY };
        app.graph.didDrag = true;
      } else {
        const p = screenToWorldEvent(ev);
        app.graph.hovered = nodeAtWorld(p.x, p.y);
        renderTooltip(ev, app.graph.hovered);
      }
    }

    function pointerUp() {
      if (app.graph.draggingNode) app.graph.draggingNode.fixed = false;
      app.graph.draggingNode = null;
      app.graph.panning = false;
      app.graph.lastPointer = null;
      canvas.classList.remove("dragging");
    }

    function onCanvasClick(ev) {
      if (app.graph.didDrag) return;
      const p = screenToWorldEvent(ev);
      const n = nodeAtWorld(p.x, p.y);
      if (!n) return;
      app.selectedNode = n;
      app.isolatedNodeId = el.focusMode.checked ? n.id : app.isolatedNodeId;
      renderSelectedNode();
      renderContextInsights();
      activateContextTab("details");
      if (n.type === "patent") {
        const h = patentNodeToHyperedge.get(n.id);
        if (h) openPatentDrawer(h.id);
      }
    }

    function onWheel(ev) {
      ev.preventDefault();
      const rect = canvas.getBoundingClientRect();
      const mx = ev.clientX - rect.left;
      const my = ev.clientY - rect.top;
      const before = screenToWorld(mx, my);
      const factor = ev.deltaY < 0 ? 1.08 : 0.92;
      app.graph.transform.scale = Math.max(.22, Math.min(4, app.graph.transform.scale * factor));
      const after = worldToScreen(before.x, before.y);
      app.graph.transform.x += mx - after.x;
      app.graph.transform.y += my - after.y;
    }

    function renderTooltip(ev, n) {
      const tip = el.graphTooltip;
      if (!n) {
        tip.style.display = "none";
        return;
      }
      tip.innerHTML = `<strong>${escapeHtml(n.label)}</strong>${escapeHtml(TYPE_LABELS[n.type] || n.type)} · grado ${Math.round(n.degree || 0)}`;
      tip.style.display = "block";
      tip.style.left = `${ev.clientX + 14}px`;
      tip.style.top = `${ev.clientY + 14}px`;
    }

    function nodeAtWorld(x, y) {
      for (let i = app.graph.nodes.length - 1; i >= 0; i--) {
        const n = app.graph.nodes[i];
        if (Math.hypot(n.x - x, n.y - y) <= nodeRadius(n) + 3) return n;
      }
      return null;
    }

    function screenToWorldEvent(ev) {
      const rect = canvas.getBoundingClientRect();
      return screenToWorld(ev.clientX - rect.left, ev.clientY - rect.top);
    }

    function screenToWorld(x, y) {
      return {
        x: (x - app.graph.transform.x) / app.graph.transform.scale,
        y: (y - app.graph.transform.y) / app.graph.transform.scale
      };
    }

    function worldToScreen(x, y) {
      return {
        x: x * app.graph.transform.scale + app.graph.transform.x,
        y: y * app.graph.transform.scale + app.graph.transform.y
      };
    }

    function resetGraphView(rebuild = true) {
      app.graph.transform = { x: 0, y: 0, scale: 1 };
      app.graph.nodes.forEach(n => { n.x = NaN; n.y = NaN; });
      if (rebuild) rebuildGraph();
      else initializePositions();
    }

    function isolateSelectedNode() {
      if (!app.selectedNode) return;
      app.isolatedNodeId = app.selectedNode.id;
      rebuildGraph();
    }

    function updateRangeLabels() {
      el.maxNodesLabel.textContent = el.maxNodes.value;
      el.minWeightLabel.textContent = el.minWeight.value;
    }

    function activateContextTab(tab) {
      document.querySelectorAll(".tab-btn").forEach(btn => btn.classList.toggle("active", btn.dataset.tab === tab));
      document.querySelectorAll(".tab-pane").forEach(p => p.classList.remove("active"));
      document.getElementById(`tab-${tab}`).classList.add("active");
    }

    function renderTable(tableId, rows, columns, options = {}) {
      const key = options.tableKey || tableId;
      if (!app.tables[key]) app.tables[key] = { sort: columns[0].key, dir: "asc" };
      const state = app.tables[key];
      const sorted = rows.slice().sort((a, b) => compareValues(valueForSort(a, state.sort), valueForSort(b, state.sort)) * (state.dir === "asc" ? 1 : -1));
      const table = document.getElementById(tableId);
      table.innerHTML = `
        <thead><tr>${columns.map(c => `<th data-key="${c.key}">${escapeHtml(c.label)}${state.sort === c.key ? (state.dir === "asc" ? " ▲" : " ▼") : ""}</th>`).join("")}</tr></thead>
        <tbody>${sorted.map(row => `
          <tr data-row="${escapeHtml(row.id || row.name || "")}">
            ${columns.map(c => `<td>${c.render ? c.render(row) : escapeHtml(formatCell(row[c.key]))}</td>`).join("")}
          </tr>
        `).join("")}</tbody>
      `;
      table.querySelectorAll("th").forEach(th => th.addEventListener("click", () => {
        const k = th.dataset.key;
        if (state.sort === k) state.dir = state.dir === "asc" ? "desc" : "asc";
        else { state.sort = k; state.dir = "desc"; }
        renderTable(tableId, rows, columns, options);
      }));
      if (options.onRowClick) {
        table.querySelectorAll("tbody tr").forEach((tr, i) => tr.addEventListener("click", () => options.onRowClick(sorted[i])));
      }
    }

    function patentColumns() {
      return [
        { key: "id", label: "Brevetto" },
        { key: "title", label: "Titolo", render: r => escapeHtml(truncate(r.title, 90)) },
        { key: "year", label: "Anno", render: r => patentYear(r) || "", export: r => patentYear(r) || "" },
        { key: "assignees", label: "Assignee", render: r => chips(r.assignees, 3) },
        { key: "focus", label: "Focus", render: r => chips(r.focus, 4) },
        { key: "cpc_groups", label: "CPC", render: r => chips(r.cpc_groups, 4) },
        { key: "legal_state", label: "Stato", render: r => badge(r.legal_state || "", String(r.legal_state).toUpperCase() === "ALIVE" ? "green" : "red") }
      ];
    }

    function exportRows(rows, columns, filename) {
      try {
        const cleanRows = Array.isArray(rows) ? rows : [];
        const cleanColumns = Array.isArray(columns) ? columns : [];
        if (!cleanRows.length || !cleanColumns.length) {
          showToast("Nessun dato da esportare.");
          return;
        }
        const delimiter = ";";
        const csv = "\ufeff" + [
          cleanColumns.map(c => csvCell(c.label)).join(delimiter),
          ...cleanRows.map(row => cleanColumns.map(c => csvCell(exportCell(row, c))).join(delimiter))
        ].join("\r\n");
        const blob = new Blob([csv], { type: "text/csv;charset=utf-8" });
        const safeFilename = filename || `export_${new Date().toISOString().slice(0, 10)}.csv`;

        if (window.navigator && typeof window.navigator.msSaveOrOpenBlob === "function") {
          window.navigator.msSaveOrOpenBlob(blob, safeFilename);
          showToast(`Export creato: ${safeFilename}`);
          return;
        }

        const isIOS = /iPad|iPhone|iPod/.test(navigator.userAgent) || (navigator.platform === "MacIntel" && navigator.maxTouchPoints > 1);
        if (isIOS) {
          const reader = new FileReader();
          reader.onload = () => {
            const opened = window.open(reader.result, "_blank");
            if (!opened) {
              fallbackCsvDownload(csv, safeFilename);
            }
            showToast(`CSV pronto: ${safeFilename}`);
          };
          reader.onerror = () => fallbackCsvDownload(csv, safeFilename);
          reader.readAsDataURL(blob);
          return;
        }

        const url = URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = safeFilename;
        a.rel = "noopener";
        a.style.display = "none";
        document.body.appendChild(a);
        a.click();
        setTimeout(() => {
          URL.revokeObjectURL(url);
          a.remove();
        }, 5000);
        showToast(`Export creato: ${safeFilename}`);
      } catch (err) {
        console.error("CSV export failed", err);
        showToast("Export non riuscito. Prova da un browser desktop o riduci i filtri.");
      }
    }

    function exportCell(row, column) {
      if (column && typeof column.export === "function") return column.export(row);
      return row ? row[column.key] : "";
    }

    function fallbackCsvDownload(csv, filename) {
      const encoded = encodeURIComponent(csv);
      const a = document.createElement("a");
      a.href = `data:text/csv;charset=utf-8,${encoded}`;
      a.download = filename;
      a.rel = "noopener";
      a.style.display = "none";
      document.body.appendChild(a);
      a.click();
      setTimeout(() => a.remove(), 1000);
    }

    function showToast(message) {
      if (!el.toast) return;
      el.toast.textContent = message;
      el.toast.classList.add("show");
      clearTimeout(showToast._timer);
      showToast._timer = setTimeout(() => el.toast.classList.remove("show"), 2600);
    }

    function populateSearchSuggestions() {
      const suggestions = [
        ...DATA.nodes.slice(0, 900).map(n => n.label),
        ...DATA.hyperedges.slice(0, 345).map(h => h.title)
      ].filter(Boolean);
      el.searchSuggestions.innerHTML = unique(suggestions).slice(0, 1000).map(x => `<option value="${escapeHtml(x)}"></option>`).join("");
    }

    function inc(map, key, by = 1) {
      if (key === undefined || key === null || key === "") return;
      map.set(key, (map.get(key) || 0) + by);
    }

    function mapToRows(map, type) {
      return Array.from(map.entries()).map(([name, count]) => ({ name, count, type })).sort((a, b) => b.count - a.count || String(a.name).localeCompare(String(b.name)));
    }

    function topKeys(map, n) {
      return mapToRows(map, "").slice(0, n).map(x => x.name);
    }

    function unique(arr) {
      return Array.from(new Set(arr.filter(Boolean))).sort((a, b) => String(a).localeCompare(String(b)));
    }

    function classifyActor(a) {
      const eco = a.focus.some(f => ["MEA","AEM","GDE","Non-noble candidate"].includes(f));
      if (eco && a.patents >= 4) return "Competitor da monitorare";
      if (eco && a.focus.length >= 2 && a.patents <= 3) return "Possibile partner";
      if (eco) return "Attore vicino a ECO RED";
      return "Attore periferico";
    }

    function cleanPatentId(id) {
      return String(id || "").replace(/^patent::/, "");
    }

    function patentYear(h) {
      return Number(h?.priority_year || h?.year || h?.publication_year || 0) || null;
    }

    function labelFor(id) {
      return nodeMap.get(id)?.label || patentNodeToHyperedge.get(id)?.title || String(id).replace(/^[^:]+::/, "");
    }

    function valueForSort(row, key) {
      const v = row[key];
      if (Array.isArray(v)) return v.join(" ");
      return v;
    }

    function compareValues(a, b) {
      const na = Number(a), nb = Number(b);
      if (Number.isFinite(na) && Number.isFinite(nb)) return na - nb;
      return String(a ?? "").localeCompare(String(b ?? ""));
    }

    function formatCell(v) {
      if (Array.isArray(v)) return v.join("; ");
      if (v instanceof Set) return Array.from(v).join("; ");
      return v ?? "";
    }

    function chips(items, max = 6) {
      const arr = Array.isArray(items) ? items.filter(Boolean) : [];
      if (!arr.length) return `<span class="hint">n.d.</span>`;
      const shown = arr.slice(0, max);
      const extra = arr.length - shown.length;
      return shown.map(x => badge(String(x), badgeTone(String(x)))).join("") + (extra > 0 ? badge(`+${extra}`, "blue") : "");
    }

    function badge(text, tone = "blue") {
      return `<span class="badge ${tone}">${escapeHtml(text)}</span>`;
    }

    function badgeTone(text) {
      const t = text.toLowerCase();
      if (t.includes("alive") || t.includes("partner")) return "green";
      if (t.includes("dead") || t.includes("competitor")) return "red";
      if (t.includes("aem") || t.includes("mea") || t.includes("gde")) return "cyan";
      if (t.includes("non-noble") || t.includes("c25")) return "orange";
      return "blue";
    }

    function fmt(value) {
      return Number(value || 0).toLocaleString("en-US");
    }

    function truncate(text, max = 80) {
      text = String(text || "");
      return text.length > max ? text.slice(0, max - 1) + "…" : text;
    }

    function escapeHtml(value) {
      return String(value ?? "")
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
    }

    function csvCell(value) {
      const text = String(formatCell(value)).replace(/"/g, '""');
      return `"${text}"`;
    }

    function roundRect(ctx, x, y, w, h, r) {
      ctx.beginPath();
      ctx.moveTo(x + r, y);
      ctx.arcTo(x + w, y, x + w, y + h, r);
      ctx.arcTo(x + w, y + h, x, y + h, r);
      ctx.arcTo(x, y + h, x, y, r);
      ctx.arcTo(x, y, x + w, y, r);
      ctx.closePath();
    }

    init();
  </script>
</body>
</html>
'''


OUT_PATH.write_text(html.replace("__DATA_JSON__", data_json), encoding="utf-8")
print(f"Wrote {OUT_PATH}")
