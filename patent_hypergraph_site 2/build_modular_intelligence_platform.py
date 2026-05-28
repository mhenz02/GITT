import json
import math
import re
from collections import Counter, defaultdict
from itertools import combinations
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parent
PROJECT_ROOT = ROOT.parents[1]
PUB_FILE = PROJECT_ROOT / "PUBBLICAZIONI DEFINITIVO.xlsx"
PATENT_FILE = ROOT / "patent_hypergraph_data.json"
DATA_DIR = ROOT / "public" / "data"
OUT_HTML = ROOT / "index.html"


ECO_BENCHMARKS = {
    "FE_CO": {"label": "FE_CO (%)", "value": 97, "threshold": 90, "unit": "%"},
    "Current Density": {"label": "Current Density (mA/cm²)", "value": 200, "threshold": 200, "unit": "mA/cm²"},
    "Stability": {"label": "Stability (h)", "value": 300, "threshold": 300, "threshold_high": 500, "unit": "h"},
}

EUROPE = {
    "Austria", "Belgium", "Bulgaria", "Croatia", "Cyprus", "Czech Republic", "Denmark",
    "Estonia", "Finland", "France", "Germany", "Greece", "Hungary", "Ireland", "Italy",
    "Latvia", "Lithuania", "Luxembourg", "Malta", "Netherlands", "Poland", "Portugal",
    "Romania", "Slovakia", "Slovenia", "Spain", "Sweden", "Norway", "Switzerland",
    "United Kingdom", "UK"
}


def clean_text(value):
    if pd.isna(value):
        return ""
    text = str(value).replace("\xa0", " ").strip()
    if text.lower() in {"", "n/d", "nd", "nan", "none", "n.a.", "na", "-"}:
        return ""
    return re.sub(r"\s+", " ", text)


def normalize_country(value):
    text = clean_text(value)
    if not text or text.upper() in {"NOT_FOUND", "NOT FOUND"}:
        return "Non disponibile"
    if text.lower() in {"multiple", "multi-country", "multicountry"}:
        return "Più paesi"
    return text


def is_known_country(country):
    return country not in {"", "Non disponibile", "Più paesi"}


def parse_number(value):
    text = clean_text(value)
    if not text:
        return None
    text = text.replace(",", ".")
    match = re.search(r"-?\d+(?:\.\d+)?", text)
    return float(match.group(0)) if match else None


def parse_year(value):
    if pd.isna(value):
        return None
    match = re.search(r"(19|20)\d{2}", str(value))
    return int(match.group(0)) if match else None


def split_values(value):
    text = clean_text(value)
    if not text:
        return []
    parts = re.split(r"\s*[;|]\s*", text)
    return [p.strip() for p in parts if p.strip()]


def split_authors(value):
    text = clean_text(value)
    if not text:
        return []
    parts = re.split(r"\s*;\s*", text)
    return [p.strip() for p in parts if len(p.strip()) > 2]


def top_rows(counter, n=10):
    return [{"name": k, "count": int(v)} for k, v in counter.most_common(n)]


def percentile(values, p):
    values = sorted([v for v in values if v is not None])
    if not values:
        return 0
    idx = (len(values) - 1) * p
    lo = math.floor(idx)
    hi = math.ceil(idx)
    if lo == hi:
        return values[lo]
    return values[lo] * (hi - idx) + values[hi] * (idx - lo)


TECH_RULES = [
    ("MEA", [r"\bMEA\b", r"membrane electrode assembly", r"zero[- ]gap"]),
    ("AEM", [r"\bAEM\b", r"anion[- ]exchange", r"anion exchange", r"scambio anionico"]),
    ("GDE", [r"\bGDE\b", r"gas diffusion", r"diffusione gas"]),
    ("Non-noble catalysts", [r"non[- ]noble", r"non nobili", r"\bfe\b", r"iron", r"\bni\b", r"nickel", r"\bzn\b", r"zinc", r"\bco\b", r"cobalt", r"\bsn\b", r"tin"]),
    ("CO2-to-CO", [r"co2[- ]to[- ]co", r"co₂[- ]to[- ]co", r"carbon monoxide", r"prodotto\s*[–-]\s*co", r"to co\b"]),
    ("Membranes", [r"membrane", r"membrana"]),
    ("Ionomers", [r"ionomer", r"ionomeri"]),
    ("Electrodes", [r"electrode", r"elettrodi", r"cathode", r"anode"]),
    ("Catalyst layer", [r"catalyst layer", r"strato catalitico"]),
    ("Electrolyzer", [r"electrolyzer", r"elettrolizzatore", r"electrolysis cell"]),
    ("Flow cell", [r"flow cell", r"flow-cell", r"cella a flusso"]),
    ("Zero-gap", [r"zero[- ]gap"]),
    ("Silver catalysts", [r"silver", r"\bag\b", r"argento"]),
    ("Copper-based", [r"copper", r"\bcu\b", r"rame"]),
    ("Single atom catalysts", [r"single[- ]atom", r"atomically dispersed", r"sac\b"]),
    ("Water management", [r"water management", r"gestione acqua", r"humidity", r"umid"]),
]


def detect_technologies(*values):
    text = " | ".join(clean_text(v) for v in values if clean_text(v)).lower()
    found = []
    for name, patterns in TECH_RULES:
        if any(re.search(p, text, flags=re.I) for p in patterns):
            found.append(name)
    return sorted(set(found))


def performance_class(row):
    classes = []
    if row.get("FE_CO") is not None:
        classes.append("FE_CO ≥ 90%" if row["FE_CO"] >= 90 else "FE_CO < 90%")
    if row.get("Current Density") is not None:
        classes.append("Current Density ≥ 200" if row["Current Density"] >= 200 else "Current Density < 200")
    if row.get("Stability") is not None:
        if row["Stability"] >= 500:
            classes.append("Stability ≥ 500 h")
        elif row["Stability"] >= 300:
            classes.append("Stability 300-500 h")
        else:
            classes.append("Stability < 300 h")
    return classes


def metric_series(rows, metric_key, limit=None):
    valid = [r for r in rows if r.get("year") and r.get(metric_key) is not None]
    by_year = defaultdict(list)
    for r in valid:
        by_year[int(r["year"])].append(float(r[metric_key]))
    years = sorted(by_year)
    annual = []
    frontier = []
    running = None
    for y in years:
        vals = by_year[y]
        annual_max = max(vals)
        running = annual_max if running is None else max(running, annual_max)
        annual.append({"year": y, "count": len(vals), "max": annual_max, "mean": sum(vals) / len(vals)})
        frontier.append({"year": y, "value": running})
    values = [r[metric_key] for r in valid]
    return {
        "valid_count": len(valid),
        "mean": round(sum(values) / len(values), 3) if values else None,
        "max": max(values) if values else None,
        "annual": annual,
        "frontier": frontier,
        "limit": limit,
    }


def make_nodes_edges_from_pairs(pairs, source_type, target_type, weight_default=1, min_weight=1, max_edges=2200):
    counter = Counter()
    examples = defaultdict(list)
    for s, t, pid in pairs:
        if not s or not t:
            continue
        counter[(s, t)] += weight_default
        if pid and len(examples[(s, t)]) < 20:
            examples[(s, t)].append(pid)
    edges = []
    node_counts = Counter()
    for (s, t), w in counter.most_common(max_edges):
        if w < min_weight:
            continue
        sid = f"{source_type}::{s}"
        tid = f"{target_type}::{t}"
        edges.append({"source": sid, "target": tid, "weight": int(w), "items": examples[(s, t)]})
        node_counts[(sid, source_type, s)] += w
        node_counts[(tid, target_type, t)] += w
    nodes = {}
    for (nid, ntype, label), count in node_counts.items():
        nodes[nid] = {"id": nid, "label": label, "type": ntype, "count": int(count)}
    return list(nodes.values()), edges


def build_publications():
    df = pd.read_excel(PUB_FILE, sheet_name="Dataset_unico")
    rows = []
    for idx, rec in df.iterrows():
        title = clean_text(rec.get("Title"))
        year = parse_year(rec.get("Year"))
        country = normalize_country(rec.get("Country"))
        authors = split_authors(rec.get("Authors"))
        fe = parse_number(rec.get("FE_CO (%)"))
        stability = parse_number(rec.get("Stability (h)"))
        current_raw = parse_number(rec.get("Current Density (mA/cm²)"))
        current = current_raw
        outlier = False
        if year == 2017 and current_raw and current_raw >= 3000 and "water electrolysis" in title.lower():
            current = None
            outlier = True
        text_fields = [
            title,
            rec.get("Abstract (2 sentences: Catalyst | Cell | Performance)"),
            rec.get("Catalizzatori e materiali"),
            rec.get("Celle e tecnologie elettrolitiche"),
            rec.get("Conversione CO₂ e prodotti target"),
            rec.get("Membrane, MEA e ionomeri"),
            rec.get("Elettrodi, GDE e componenti"),
            rec.get("Performance e condizioni operative"),
        ]
        techs = detect_technologies(*text_fields)
        row = {
            "id": f"PUB-{idx+1:04d}",
            "title": title,
            "city": clean_text(rec.get("City")),
            "country": country,
            "authors": authors,
            "year": year,
            "doi": clean_text(rec.get("DOI")),
            "abstract": clean_text(rec.get("Abstract (2 sentences: Catalyst | Cell | Performance)")),
            "FE_CO": fe,
            "Stability": stability,
            "Current Density": current,
            "Current Density Raw": current_raw,
            "current_density_outlier_excluded": outlier,
            "catalysts_materials": clean_text(rec.get("Catalizzatori e materiali")),
            "cell_technology": clean_text(rec.get("Celle e tecnologie elettrolitiche")),
            "conversion_target": clean_text(rec.get("Conversione CO₂ e prodotti target")),
            "membranes_mea_ionomers": clean_text(rec.get("Membrane, MEA e ionomeri")),
            "electrodes_gde": clean_text(rec.get("Elettrodi, GDE e componenti")),
            "operating_conditions": clean_text(rec.get("Performance e condizioni operative")),
            "process_integration": clean_text(rec.get("Integrazione di processo e applicazioni")),
            "alternative_processes": clean_text(rec.get("Processi alternativi o ibridi")),
            "methods": clean_text(rec.get("Metodi, fabbricazione e caratterizzazione")),
            "source_url": clean_text(rec.get("Source URL")),
            "technologies": techs,
        }
        row["performance_classes"] = performance_class(row)
        rows.append(row)

    country_counts = Counter(r["country"] for r in rows if is_known_country(r["country"]))
    tech_counts = Counter(t for r in rows for t in r["technologies"])
    author_counts = Counter(a for r in rows for a in r["authors"])
    years = [r["year"] for r in rows if r["year"]]
    eco_techs = {"MEA", "AEM", "GDE", "Non-noble catalysts", "CO2-to-CO"}
    eco_rows = [r for r in rows if eco_techs.intersection(r["technologies"])]
    metrics = {
        "FE_CO": metric_series(rows, "FE_CO", limit=100),
        "Current Density": metric_series(rows, "Current Density", limit=3000),
        "Stability": metric_series(rows, "Stability", limit=30000),
    }
    summary = {
        "total_publications": len(rows),
        "year_min": min(years) if years else None,
        "year_max": max(years) if years else None,
        "countries": len(country_counts),
        "authors": len(author_counts),
        "top_countries": top_rows(country_counts, 12),
        "top_technologies": top_rows(tech_counts, 16),
        "top_keywords": top_rows(tech_counts, 16),
        "eco_red_like_publications": len(eco_rows),
        "metrics": {k: {"mean": v["mean"], "max": v["max"], "valid_count": v["valid_count"]} for k, v in metrics.items()},
        "with_china": {"publications": len(rows), "countries": len(country_counts)},
        "without_china": {"publications": len([r for r in rows if r["country"] != "China"]), "countries": len(set(r["country"] for r in rows if is_known_country(r["country"]) and r["country"] != "China"))},
        "europe": {"publications": len([r for r in rows if r["country"] in EUROPE]), "countries": len(set(r["country"] for r in rows if r["country"] in EUROPE))},
        "outliers_excluded": [r for r in rows if r["current_density_outlier_excluded"]],
    }

    return rows, summary, metrics


def build_publication_network(rows):
    views = {}
    pairs = [(r["title"], t, r["id"]) for r in rows for t in r["technologies"]]
    nodes, edges = make_nodes_edges_from_pairs(pairs, "publication", "technology", max_edges=2600)
    views["publication_technology"] = {"label": "Publication → Technology", "nodes": nodes, "edges": edges, "description": "Una pubblicazione è collegata alle tecnologie che tratta."}

    pairs = [(r["title"], r["country"], r["id"]) for r in rows if is_known_country(r["country"])]
    nodes, edges = make_nodes_edges_from_pairs(pairs, "publication", "country", max_edges=1200)
    views["publication_country"] = {"label": "Publication → Country", "nodes": nodes, "edges": edges, "description": "Una pubblicazione è collegata al paese associato nel dataset."}

    top_authors = {a for a, c in Counter(a for r in rows for a in r["authors"]).items() if c >= 2}
    pairs = [(r["title"], a, r["id"]) for r in rows for a in r["authors"] if a in top_authors]
    nodes, edges = make_nodes_edges_from_pairs(pairs, "publication", "author", max_edges=1800)
    views["publication_author"] = {"label": "Publication → Authors", "nodes": nodes, "edges": edges, "description": "Una pubblicazione è collegata agli autori ricorrenti nel dataset."}

    co_pairs = []
    for r in rows:
        for a, b in combinations(sorted(set(r["technologies"])), 2):
            co_pairs.append((a, b, r["id"]))
    nodes, edges = make_nodes_edges_from_pairs(co_pairs, "technology", "technology", max_edges=1200)
    views["technology_technology"] = {"label": "Technology → Technology", "nodes": nodes, "edges": edges, "description": "Due tecnologie sono collegate se co-occorrono nella stessa pubblicazione. Non implica causalità né collaborazione."}

    pairs = [(r["country"], t, r["id"]) for r in rows for t in r["technologies"] if is_known_country(r["country"])]
    nodes, edges = make_nodes_edges_from_pairs(pairs, "country", "technology", max_edges=1400)
    views["country_technology"] = {"label": "Country → Technology", "nodes": nodes, "edges": edges, "description": "Un paese è collegato alle tecnologie trattate dalle sue pubblicazioni."}

    pairs = [(a, t, r["id"]) for r in rows for a in r["authors"] if a in top_authors for t in r["technologies"]]
    nodes, edges = make_nodes_edges_from_pairs(pairs, "author", "technology", max_edges=1800)
    views["author_technology"] = {"label": "Authors → Technology", "nodes": nodes, "edges": edges, "description": "Un autore è collegato alle tecnologie sulle quali pubblica. Non implica collaborazione tra autori."}

    pairs = [(pc, t, r["id"]) for r in rows for pc in r["performance_classes"] for t in r["technologies"]]
    nodes, edges = make_nodes_edges_from_pairs(pairs, "performance_class", "technology", max_edges=1200)
    views["performance_technology"] = {"label": "Performance class → Technology", "nodes": nodes, "edges": edges, "description": "Una classe di performance è collegata alle tecnologie osservate nelle pubblicazioni."}
    return {"views": views}


def patent_stats(patents):
    actor_counter = Counter(a for h in patents["hyperedges"] for a in h.get("assignees", []))
    cpc_counter = Counter(c for h in patents["hyperedges"] for c in h.get("cpc_groups", []))
    domain_counter = Counter(d for h in patents["hyperedges"] for d in h.get("domains", []))
    focus_counter = Counter(f for h in patents["hyperedges"] for f in h.get("focus", []))
    years = [h.get("priority_year") or h.get("year") for h in patents["hyperedges"] if h.get("priority_year") or h.get("year")]
    citations = Counter()
    for e in patents.get("citationEdges", []):
        citations[str(e.get("target", "")).replace("patent::", "")] += int(e.get("weight") or 1)
    return {
        "total_patents": patents["summary"]["patents"],
        "nodes": patents["summary"]["nodes"],
        "links": patents["summary"]["incidence_edges"],
        "citations": patents["summary"]["citation_edges"],
        "year_min": min(years) if years else patents["summary"].get("year_min"),
        "year_max": max(years) if years else patents["summary"].get("year_max"),
        "assignees": len(actor_counter),
        "top_assignees": top_rows(actor_counter, 14),
        "top_cpc_groups": top_rows(cpc_counter, 14),
        "top_domains": top_rows(domain_counter, 12),
        "focus": top_rows(focus_counter, 8),
        "foundational_patents": [{"id": pid, "citations": c} for pid, c in citations.most_common(20)],
    }


def build_patent_network_light(patents):
    base_nodes = {n["id"]: {"id": n["id"], "label": n.get("label", n["id"]), "type": n.get("type", "unknown"), "count": n.get("count", 1)} for n in patents["nodes"]}
    views = {}
    incidence_defs = {
        "patent_assignee": ("Brevetti → Assignee", {"patent_assignee"}),
        "patent_cpc": ("Brevetti → CPC group", {"patent_cpc_group"}),
        "patent_concept": ("Brevetti → Concetti tecnici", {"patent_concept"}),
    }
    for key, (label, rels) in incidence_defs.items():
        edges = [
            {"source": e["source"], "target": e["target"], "weight": e.get("weight", 1), "items": [e.get("patent")]}
            for e in patents["incidenceEdges"] if e.get("relation") in rels
        ][:2500]
        node_ids = {x for e in edges for x in (e["source"], e["target"])}
        views[key] = {"label": label, "nodes": [base_nodes[i] for i in node_ids if i in base_nodes], "edges": edges, "description": "Relazione diretta brevetto-metadato."}
    for key, label in {
        "assignee_cpc_group": "Assignee → CPC group",
        "assignee_cpc_code": "Assignee → CPC specifici",
        "assignee_domain": "Assignee → Domini",
        "assignee_country": "Assignee → Paesi",
        "domain_cpc_group": "Domini → CPC group",
        "concept_cpc_group": "Concetti → CPC group",
        "focus_assignee": "Focus ECO RED → Assignee",
    }.items():
        raw = sorted(patents["projectionEdges"].get(key, []), key=lambda e: e.get("weight", 1), reverse=True)[:2500]
        edges = [{"source": e["source"], "target": e["target"], "weight": e.get("weight", 1), "items": e.get("patents", [])[:20]} for e in raw]
        node_ids = {x for e in edges for x in (e["source"], e["target"])}
        views[key] = {"label": label, "nodes": [base_nodes[i] for i in node_ids if i in base_nodes], "edges": edges, "description": "Proiezione derivata da co-occorrenza nello stesso brevetto."}
    raw = sorted(patents.get("citationEdges", []), key=lambda e: e.get("weight", 1), reverse=True)[:1200]
    edges = [{"source": e["source"], "target": e["target"], "weight": e.get("weight", 1), "items": e.get("patents", [])} for e in raw]
    node_ids = {x for e in edges for x in (e["source"], e["target"])}
    views["citation"] = {"label": "Citazioni brevetto → brevetto", "nodes": [base_nodes[i] for i in node_ids if i in base_nodes], "edges": edges, "description": "Arco diretto dal brevetto citante al brevetto citato."}
    return {"views": views}


def build_patent_tables(patents):
    citations_in = Counter()
    citations_out = Counter()
    for e in patents.get("citationEdges", []):
        s = str(e.get("source", "")).replace("patent::", "")
        t = str(e.get("target", "")).replace("patent::", "")
        w = int(e.get("weight") or 1)
        citations_out[s] += w
        citations_in[t] += w
    patent_rows = []
    for h in patents["hyperedges"]:
        patent_rows.append({
            "id": h["id"],
            "title": h.get("title", ""),
            "year": h.get("priority_year") or h.get("year"),
            "publication_year": h.get("publication_year"),
            "assignees": h.get("assignees", []),
            "domains": h.get("domains", []),
            "cpc_groups": h.get("cpc_groups", []),
            "cpc_codes": h.get("cpc_codes", [])[:20],
            "ipc_groups": h.get("ipc_groups", []),
            "concepts": h.get("concepts", [])[:30],
            "countries": h.get("countries", []),
            "legal_state": h.get("legal_state"),
            "focus": h.get("focus", []),
            "citations_in": citations_in[h["id"]],
            "citations_out": citations_out[h["id"]],
        })
    actors = defaultdict(lambda: {"patents": [], "domains": Counter(), "cpc_groups": Counter(), "countries": Counter(), "focus": Counter(), "citations": 0})
    for h in patent_rows:
        for a in h["assignees"]:
            actors[a]["patents"].append(h["id"])
            actors[a]["domains"].update(h["domains"])
            actors[a]["cpc_groups"].update(h["cpc_groups"])
            actors[a]["countries"].update(h["countries"])
            actors[a]["focus"].update(h["focus"])
            actors[a]["citations"] += h["citations_in"]
    actor_rows = []
    for name, a in actors.items():
        actor_rows.append({
            "name": name,
            "patents": len(a["patents"]),
            "domains": [x for x, _ in a["domains"].most_common(5)],
            "cpc_groups": [x for x, _ in a["cpc_groups"].most_common(5)],
            "countries": [x for x, _ in a["countries"].most_common(5)],
            "focus": [x for x, _ in a["focus"].most_common(5)],
            "citations": a["citations"],
            "patent_ids": a["patents"][:30],
        })
    actor_rows.sort(key=lambda x: (x["patents"], x["citations"]), reverse=True)
    return {"patents": patent_rows, "actors": actor_rows}


def patent_technologies(h):
    text = " | ".join([
        h.get("title", ""),
        " ".join(h.get("concepts", [])),
        " ".join(h.get("domains", [])),
        " ".join(h.get("focus", [])),
        " ".join(h.get("cpc_groups", [])),
    ])
    return detect_technologies(text, " ".join(h.get("focus", [])))


def build_integrated(pub_rows, pub_metrics, patents, patent_tables):
    pub_counter = Counter(t for r in pub_rows for t in r["technologies"])
    pub_years_by_tech = defaultdict(Counter)
    pub_countries_by_tech = defaultdict(Counter)
    for r in pub_rows:
        for t in r["technologies"]:
            if r["year"]:
                pub_years_by_tech[t][r["year"]] += 1
            if is_known_country(r["country"]):
                pub_countries_by_tech[t][r["country"]] += 1

    patent_counter = Counter()
    patent_years_by_tech = defaultdict(Counter)
    patent_actors_by_tech = defaultdict(Counter)
    for h in patents["hyperedges"]:
        techs = patent_technologies(h)
        for t in techs:
            patent_counter[t] += 1
            y = h.get("priority_year") or h.get("year")
            if y:
                patent_years_by_tech[t][y] += 1
            patent_actors_by_tech[t].update(h.get("assignees", []))

    techs = sorted(set(pub_counter) | set(patent_counter))
    pub_vals = [pub_counter[t] for t in techs]
    pat_vals = [patent_counter[t] for t in techs]
    pub_thr = max(1, percentile([v for v in pub_vals if v], 0.5))
    pat_thr = max(1, percentile([v for v in pat_vals if v], 0.5))
    matrix = []
    shared = []
    for t in techs:
        pc = pub_counter[t]
        bc = patent_counter[t]
        if pc >= pub_thr and bc >= pat_thr:
            quadrant = "Molte pubblicazioni / molti brevetti"
            meaning = "Area calda e competitiva"
        elif pc >= pub_thr and bc < pat_thr:
            quadrant = "Molte pubblicazioni / pochi brevetti"
            meaning = "Area scientificamente viva ma meno appropriata"
        elif pc < pub_thr and bc >= pat_thr:
            quadrant = "Poche pubblicazioni / molti brevetti"
            meaning = "Area più industriale o protetta"
        else:
            quadrant = "Poche pubblicazioni / pochi brevetti"
            meaning = "Area marginale o immatura"
        row = {
            "technology": t,
            "publications": int(pc),
            "patents": int(bc),
            "ratio_publications_patents": round(pc / bc, 2) if bc else None,
            "quadrant": quadrant,
            "meaning": meaning,
            "pub_trend": [{"year": y, "count": c} for y, c in sorted(pub_years_by_tech[t].items())],
            "patent_trend": [{"year": y, "count": c} for y, c in sorted(patent_years_by_tech[t].items())],
            "top_patent_actors": top_rows(patent_actors_by_tech[t], 6),
            "top_scientific_countries": top_rows(pub_countries_by_tech[t], 6),
            "eco_red_relevance": t in {"MEA", "AEM", "GDE", "Non-noble catalysts", "CO2-to-CO", "Membranes", "Ionomers", "Electrodes"},
        }
        matrix.append(row)
        if pc or bc:
            shared.append(row)

    nodes = []
    edges = []
    for row in shared:
        tech = row["technology"]
        sid = f"shared::{tech}"
        nodes.append({"id": sid, "label": tech, "type": "shared_technology", "count": row["publications"] + row["patents"]})
        if row["publications"]:
            pid = f"science::{tech}"
            nodes.append({"id": pid, "label": f"Science: {tech}", "type": "science_cluster", "count": row["publications"]})
            edges.append({"source": pid, "target": sid, "weight": row["publications"]})
        if row["patents"]:
            bid = f"patent::{tech}"
            nodes.append({"id": bid, "label": f"Patents: {tech}", "type": "patent_cluster", "count": row["patents"]})
            edges.append({"source": bid, "target": sid, "weight": row["patents"]})
    network = {"views": {"integrated_bridge": {"label": "Science → Technology ← Patents", "nodes": nodes, "edges": edges, "description": "Rete leggera che usa tecnologie comuni come ponte tra pubblicazioni e brevetti."}}}

    white_spaces = {
        "many_publications_few_patents": [r for r in matrix if r["quadrant"] == "Molte pubblicazioni / pochi brevetti"][:12],
        "many_patents_few_publications": [r for r in matrix if r["quadrant"] == "Poche pubblicazioni / molti brevetti"][:12],
        "hot_competitive": [r for r in matrix if r["quadrant"] == "Molte pubblicazioni / molti brevetti"][:12],
        "eco_red_less_crowded": sorted([r for r in matrix if r["eco_red_relevance"]], key=lambda r: (r["patents"], -r["publications"]))[:12],
    }
    positioning = {
        "benchmarks": ECO_BENCHMARKS,
        "performance_frontier": {k: v["frontier"] for k, v in pub_metrics.items()},
        "science_ip_by_focus": [r for r in matrix if r["eco_red_relevance"]],
        "closest_patent_actors": patent_tables["actors"][:12],
        "managerial_reading": [
            "ECO RED va confrontata con la frontiera scientifica delle performance e con l'intensità IP sulle stesse tecnologie.",
            "MEA, AEM, GDE e catalizzatori non nobili sono il ponte principale tra letteratura e brevetti.",
            "Aree con molte pubblicazioni ma pochi brevetti possono indicare spazi scientificamente maturi ma meno appropriati.",
            "Aree con molti brevetti e poche pubblicazioni possono indicare presidio industriale o barriere IP più forti.",
        ],
    }
    summary = {
        "total_publications": len(pub_rows),
        "total_patents": len(patents["hyperedges"]),
        "shared_technologies": len(shared),
        "publication_dominant": len(white_spaces["many_publications_few_patents"]),
        "patent_dominant": len(white_spaces["many_patents_few_publications"]),
        "hot_competitive": len(white_spaces["hot_competitive"]),
        "top_shared": sorted(shared, key=lambda r: r["publications"] + r["patents"], reverse=True)[:12],
        "white_spaces": white_spaces,
    }
    return summary, {"matrix": matrix, "thresholds": {"publications": pub_thr, "patents": pat_thr}}, network, positioning


def write_json(name, obj):
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    path = DATA_DIR / name
    path.write_text(json.dumps(obj, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    return path


def build_html():
    html = r'''<!doctype html>
<html lang="it">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>ECO RED Technology Intelligence Platform</title>
  <style>
    :root{--navy:#07111f;--navy2:#10233b;--bg:#f4f7fb;--surface:#fff;--soft:#f8fafc;--line:#dbe3ee;--text:#162033;--muted:#667085;--blue:#2563eb;--cyan:#0284c7;--teal:#0f766e;--violet:#7c3aed;--orange:#f97316;--green:#16a34a;--red:#dc2626;--yellow:#ca8a04;--shadow:0 14px 35px rgba(15,23,42,.08);--radius:16px}
    *{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--text);font-family:Inter,"IBM Plex Sans","Source Sans 3","Segoe UI",system-ui,sans-serif;line-height:1.5}button,input,select{font:inherit}button{cursor:pointer}
    .topbar{background:linear-gradient(135deg,var(--navy),var(--navy2));color:#fff;padding:22px 28px 16px}.topbar-row{display:flex;justify-content:space-between;gap:18px;align-items:flex-start;flex-wrap:wrap}.eyebrow{font-size:12px;letter-spacing:.08em;text-transform:uppercase;color:#9bd7ff;font-weight:850}.topbar h1{margin:4px 0 6px;font-size:30px;line-height:1.12}.subtitle{color:#c8d5e6;max-width:920px;font-size:15px}.actions{display:flex;gap:10px;flex-wrap:wrap}.btn{border:1px solid var(--line);border-radius:11px;background:#fff;color:var(--text);min-height:38px;padding:0 13px;font-weight:800;font-size:13px;display:inline-flex;align-items:center;justify-content:center;gap:8px}.btn.primary{background:#0ea5e9;color:#fff;border-color:#0ea5e9}.btn.ghost{background:rgba(255,255,255,.08);color:#e5eef9;border-color:rgba(255,255,255,.18)}.btn.small{min-height:32px;padding:0 10px;border-radius:9px;font-size:12px}
    .kpis{display:grid;grid-template-columns:repeat(6,minmax(90px,1fr));gap:10px;margin-top:18px}.kpi{border:1px solid rgba(255,255,255,.12);border-radius:14px;background:rgba(255,255,255,.07);padding:12px}.kpi strong{display:block;font-size:21px}.kpi span{font-size:12px;color:#b8c7da;font-weight:750}
    .nav{display:flex;gap:6px;overflow:auto;background:#fff;border-bottom:1px solid var(--line);padding:0 28px}.nav button{border:0;border-bottom:3px solid transparent;background:transparent;color:#536174;padding:16px 10px 13px;font-weight:850;white-space:nowrap}.nav button.active{color:var(--blue);border-bottom-color:var(--blue)}
    .page{display:none;padding:26px 28px 34px}.page.active{display:block}.section-head{display:flex;justify-content:space-between;gap:18px;align-items:flex-end;margin-bottom:18px}.section-head h2{margin:0;font-size:25px}.section-head p{margin:6px 0 0;color:var(--muted);max-width:920px}
    .grid{display:grid;gap:16px}.cols-4{grid-template-columns:repeat(4,minmax(0,1fr))}.cols-3{grid-template-columns:repeat(3,minmax(0,1fr))}.cols-2{grid-template-columns:repeat(2,minmax(0,1fr))}.wide{grid-template-columns:1.25fr .75fr}.card{background:#fff;border:1px solid var(--line);border-radius:var(--radius);box-shadow:var(--shadow);padding:18px;min-width:0}.card.flush{padding:0;overflow:hidden}.card h3{margin:0 0 6px;font-size:17px}.hint{color:var(--muted);font-size:13px}.metric .label{font-size:12px;color:var(--muted);font-weight:850;text-transform:uppercase;letter-spacing:.05em}.metric .value{font-size:31px;font-weight:850;margin-top:8px;color:#07111f}
    .tabs{display:flex;gap:6px;flex-wrap:wrap;margin-bottom:14px}.tab{border:1px solid var(--line);background:#fff;color:#536174;border-radius:999px;padding:8px 12px;font-size:13px;font-weight:850}.tab.active{background:#eaf2ff;color:var(--blue);border-color:#bfdbfe}
    .bar-row{display:grid;grid-template-columns:minmax(120px,1fr) minmax(120px,1.3fr) 46px;gap:10px;align-items:center;font-size:13px}.bar-label{font-weight:800;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}.bar-track{height:10px;border-radius:999px;background:#eef2f7;overflow:hidden}.bar-fill{height:100%;border-radius:999px;background:linear-gradient(90deg,var(--blue),#22d3ee)}.bar-value{text-align:right;color:var(--muted);font-weight:850}.badge{display:inline-flex;align-items:center;border:1px solid var(--line);border-radius:999px;padding:2px 8px;margin:2px;background:#f8fafc;font-size:12px;font-weight:800;color:#344054}.badge.cyan{background:#ecfeff;color:#0e7490;border-color:#a5f3fc}.badge.green{background:#ecfdf3;color:#15803d;border-color:#bbf7d0}.badge.orange{background:#fff7ed;color:#c2410c;border-color:#fed7aa}.badge.red{background:#fef2f2;color:#b91c1c;border-color:#fecaca}.badge.blue{background:#eff6ff;color:#1d4ed8;border-color:#bfdbfe}
    .network-layout{display:grid;grid-template-columns:320px minmax(480px,1fr) 360px;gap:16px;min-height:68vh}.panel{background:#fff;border:1px solid var(--line);border-radius:var(--radius);box-shadow:var(--shadow);overflow:hidden}.panel-body{padding:16px;overflow:auto}.filters{display:grid;gap:12px}.field{display:grid;gap:7px}.field label{font-size:12px;font-weight:850;color:#344054}select,input{width:100%;min-height:40px;border:1px solid #cdd6e3;border-radius:10px;padding:0 11px;background:#fff;color:var(--text);outline:none}.check{display:flex;align-items:center;gap:8px;border:1px solid #e8eef5;background:#f8fafc;border-radius:10px;padding:8px 10px;font-weight:750;font-size:13px}.check input{width:16px;height:16px;accent-color:var(--blue)}.canvas-card{display:grid;grid-template-rows:auto 1fr}.canvas-head{display:flex;justify-content:space-between;gap:10px;padding:14px;border-bottom:1px solid var(--line);align-items:center}.canvas-wrap{position:relative;min-height:560px;background:linear-gradient(180deg,#fbfdff,#f6f9fc)}canvas.network{display:block;width:100%;height:100%;min-height:560px}.status{position:absolute;left:14px;top:14px;display:flex;gap:6px;flex-wrap:wrap}.status span{background:rgba(255,255,255,.9);border:1px solid var(--line);border-radius:999px;padding:4px 9px;font-size:12px;font-weight:850}.empty{display:none;position:absolute;inset:20px;place-items:center;text-align:center;background:rgba(255,255,255,.8);border:1px dashed #cbd5e1;border-radius:16px;color:var(--muted)}.empty.show{display:grid}
    .table-toolbar{display:flex;justify-content:space-between;gap:12px;align-items:center;padding:14px;border-bottom:1px solid var(--line);background:#fff;flex-wrap:wrap}.table-toolbar input,.table-toolbar select{max-width:280px}.table-wrap{overflow:auto;max-height:580px}table{width:100%;border-collapse:collapse;font-size:13px}th,td{padding:11px 12px;border-bottom:1px solid #e8eef5;text-align:left;vertical-align:top}th{position:sticky;top:0;background:#f8fafc;color:#475467;text-transform:uppercase;font-size:12px;letter-spacing:.04em;cursor:pointer}tbody tr:hover{background:#f8fbff}
    .drawer-backdrop{position:fixed;inset:0;background:rgba(7,17,31,.38);display:none;z-index:70}.drawer-backdrop.show{display:block}.drawer{position:fixed;right:0;top:0;bottom:0;width:min(650px,94vw);background:#fff;z-index:80;transform:translateX(105%);transition:.22s;box-shadow:-20px 0 45px rgba(15,23,42,.2);display:flex;flex-direction:column}.drawer.show{transform:translateX(0)}.drawer-head{padding:20px;background:var(--navy);color:#fff;display:flex;justify-content:space-between;gap:12px}.drawer-head h2{margin:0;font-size:20px}.drawer-body{padding:18px;overflow:auto;display:grid;gap:12px}.detail-row{border-bottom:1px solid #e8eef5;padding-bottom:9px;font-size:14px}.detail-row b{display:block;font-size:12px;text-transform:uppercase;letter-spacing:.04em;color:#344054;margin-bottom:3px}.close{width:36px;height:36px;border-radius:10px;border:1px solid rgba(255,255,255,.2);background:rgba(255,255,255,.1);color:#fff;font-size:20px}
    .matrix{display:grid;grid-template-columns:1fr 1fr;gap:12px}.quadrant{min-height:170px;border:1px solid var(--line);border-radius:14px;padding:14px;background:#fff}.quadrant h3{font-size:16px}.point{display:inline-flex;margin:3px;padding:4px 8px;border-radius:999px;background:#eff6ff;color:#1d4ed8;font-size:12px;font-weight:850}.timeline{height:190px;display:flex;align-items:flex-end;gap:5px;border-bottom:1px solid var(--line);padding:10px 4px 0}.tl-bar{flex:1;min-width:10px;border-radius:8px 8px 0 0;background:linear-gradient(180deg,#38bdf8,#2563eb);position:relative}.tl-bar span{position:absolute;bottom:-24px;left:50%;transform:translateX(-50%) rotate(-42deg);font-size:10px;color:var(--muted);white-space:nowrap}
    .toast{position:fixed;left:50%;bottom:22px;transform:translate(-50%,24px);opacity:0;z-index:100;background:rgba(7,17,31,.94);color:#fff;border-radius:14px;padding:12px 14px;box-shadow:var(--shadow);font-weight:800;transition:.18s;max-width:calc(100vw - 32px)}.toast.show{opacity:1;transform:translate(-50%,0)}
    @media(max-width:1180px){.network-layout{display:flex;flex-direction:column}.canvas-card{order:1}.network-layout>.panel:first-child{order:2}.network-layout>.panel:last-child{order:3}.canvas-wrap,canvas.network{min-height:62vh}.cols-4{grid-template-columns:repeat(2,1fr)}.wide,.cols-2,.cols-3{grid-template-columns:1fr}.kpis{grid-template-columns:repeat(3,1fr)}}
    @media(max-width:640px){.topbar{padding:18px 14px}.topbar h1{font-size:24px}.actions{display:grid;grid-template-columns:1fr 1fr;width:100%}.actions .btn{width:100%;min-height:42px}.kpis{grid-template-columns:repeat(2,1fr)}.nav{padding:0 10px}.nav button{font-size:13px;padding:13px 9px 10px}.page{padding:16px 10px 24px}.section-head{align-items:flex-start;flex-direction:column}.section-head h2{font-size:21px}.canvas-wrap,canvas.network{min-height:58vh}.canvas-head{align-items:flex-start;flex-direction:column}.table-toolbar{align-items:stretch;flex-direction:column}.table-toolbar input,.table-toolbar select{max-width:none}.matrix{grid-template-columns:1fr}.drawer{width:100vw}.bar-row{grid-template-columns:minmax(90px,1fr) minmax(80px,1fr) 36px}select,input{min-height:44px;font-size:16px}}
  </style>
</head>
<body>
  <header class="topbar">
    <div class="topbar-row">
      <div><div class="eyebrow">ECO RED Technology Intelligence</div><h1>Science & Patent Intelligence Platform</h1><div class="subtitle">Piattaforma statica e modulare per confrontare pubblicazioni scientifiche, brevetti e tecnologie comuni nella conversione elettrochimica CO₂-to-CO.</div></div>
      <div class="actions"><button class="btn ghost" id="resetBtn">Reset view</button><button class="btn ghost" id="exportBtn">Export corrente</button><button class="btn primary" id="helpBtn">Help</button></div>
    </div>
    <div class="kpis" id="globalKpis"></div>
  </header>
  <nav class="nav" id="mainNav">
    <button class="active" data-page="overview">Overview</button>
    <button data-page="patents">Patents</button>
    <button data-page="publications">Publications</button>
    <button data-page="integrated">Integrated Intelligence</button>
    <button data-page="ecored">ECO RED Focus</button>
    <button data-page="data">Data Explorer</button>
  </nav>
  <main>
    <section class="page active" id="page-overview"></section>
    <section class="page" id="page-patents"></section>
    <section class="page" id="page-publications"></section>
    <section class="page" id="page-integrated"></section>
    <section class="page" id="page-ecored"></section>
    <section class="page" id="page-data"></section>
  </main>
  <div class="drawer-backdrop" id="drawerBackdrop"></div>
  <aside class="drawer" id="drawer"><div class="drawer-head"><div><div class="eyebrow" id="drawerEyebrow">Detail</div><h2 id="drawerTitle"></h2></div><button class="close" id="drawerClose">×</button></div><div class="drawer-body" id="drawerBody"></div></aside>
  <div class="toast" id="toast"></div>
  <script>
    const DATA_BASE = "public/data/";
    const cache = {};
    const state = { page:"overview", currentRows:[], currentColumns:[], currentExport:"export.csv", networks:{}, network:null };
    const typeColors = {publication:"#2563eb",patent:"#2563eb",technology:"#0f766e",country:"#64748b",author:"#7c3aed",performance_class:"#ca8a04",assignee:"#7c3aed",domain:"#16a34a",concept:"#0f766e",science_cluster:"#0284c7",patent_cluster:"#f97316",shared_technology:"#0f766e",cpc_group:"#f97316",cpc_code:"#fb923c",focus:"#0284c7"};
    const $ = id => document.getElementById(id);
    async function loadJson(name){ if(cache[name]) return cache[name]; try{ const r=await fetch(DATA_BASE+name); if(!r.ok) throw new Error(r.status); return cache[name]=await r.json(); }catch(e){ showLoadError(e); throw e; } }
    function showLoadError(){ toast("Dati non caricati. Apri il sito tramite server locale o Vercel, non direttamente come file."); }
    function toast(msg){ const t=$("toast"); t.textContent=msg; t.classList.add("show"); clearTimeout(toast.timer); toast.timer=setTimeout(()=>t.classList.remove("show"),2800); }
    function fmt(n){ return Number(n||0).toLocaleString("en-US"); }
    function esc(v){ return String(v??"").replace(/[&<>"']/g,m=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#039;"}[m])); }
    function trunc(v,n=80){ v=String(v||""); return v.length>n?v.slice(0,n-1)+"…":v; }
    function badge(x,t="blue"){ return `<span class="badge ${t}">${esc(x)}</span>`; }
    function chips(arr,n=8){ arr=Array.isArray(arr)?arr.filter(Boolean):[]; if(!arr.length)return `<span class="hint">n.d.</span>`; return arr.slice(0,n).map(x=>badge(x,tone(x))).join("")+(arr.length>n?badge("+"+(arr.length-n)):""); }
    function tone(x){ x=String(x).toLowerCase(); if(x.includes("aem")||x.includes("mea")||x.includes("gde"))return"cyan"; if(x.includes("non")||x.includes("c25"))return"orange"; if(x.includes("alive"))return"green"; if(x.includes("dead"))return"red"; return"blue"; }
    function barRows(rows){ const max=Math.max(1,...rows.map(r=>r.count||0)); return `<div class="grid">${rows.map(r=>`<div class="bar-row" title="${esc(r.name)}"><div class="bar-label">${esc(r.name)}</div><div class="bar-track"><div class="bar-fill" style="width:${Math.max(3,(r.count/max)*100)}%"></div></div><div class="bar-value">${fmt(r.count)}</div></div>`).join("")}</div>`; }
    function metricCard(label,value,note){ return `<div class="card metric"><div class="label">${esc(label)}</div><div class="value">${esc(value)}</div><div class="hint">${esc(note||"")}</div></div>`; }
    function sectionHead(title,text,extra=""){ return `<div class="section-head"><div><h2>${esc(title)}</h2><p>${esc(text)}</p></div>${extra}</div>`; }
    function setExport(rows,cols,name){ state.currentRows=rows||[]; state.currentColumns=cols||[]; state.currentExport=name||"export.csv"; }
    function csvExport(){ const rows=state.currentRows, cols=state.currentColumns; if(!rows.length||!cols.length){toast("Nessun dato da esportare.");return} const csv="\ufeff"+[cols.map(c=>csvCell(c.label)).join(";"),...rows.map(r=>cols.map(c=>csvCell(c.export?c.export(r):r[c.key])).join(";"))].join("\r\n"); const blob=new Blob([csv],{type:"text/csv;charset=utf-8"}); const isIOS=/iPad|iPhone|iPod/.test(navigator.userAgent)||(navigator.platform==="MacIntel"&&navigator.maxTouchPoints>1); if(isIOS){const rd=new FileReader();rd.onload=()=>{window.open(rd.result,"_blank");toast("CSV pronto.")};rd.readAsDataURL(blob);return} const a=document.createElement("a"); const url=URL.createObjectURL(blob); a.href=url;a.download=state.currentExport;a.style.display="none";document.body.appendChild(a);a.click();setTimeout(()=>{URL.revokeObjectURL(url);a.remove()},4000);toast("Export creato: "+state.currentExport); }
    function csvCell(v){ if(Array.isArray(v))v=v.join("; "); return `"${String(v??"").replace(/"/g,'""')}"`; }
    function renderTable(containerId,rows,cols,opt={}){ const el=$(containerId); const key=containerId; state[key]=state[key]||{sort:cols[0].key,dir:"asc"}; const st=state[key]; const sorted=[...rows].sort((a,b)=>String(val(a,st.sort)).localeCompare(String(val(b,st.sort)),undefined,{numeric:true})*(st.dir==="asc"?1:-1)); el.innerHTML=`<table><thead><tr>${cols.map(c=>`<th data-k="${c.key}">${esc(c.label)}${st.sort===c.key?(st.dir==="asc"?" ▲":" ▼"):""}</th>`).join("")}</tr></thead><tbody>${sorted.map((r,i)=>`<tr data-i="${i}">${cols.map(c=>`<td>${c.render?c.render(r):esc(cell(r[c.key]))}</td>`).join("")}</tr>`).join("")}</tbody></table>`; el.querySelectorAll("th").forEach(th=>th.onclick=()=>{const k=th.dataset.k;if(st.sort===k)st.dir=st.dir==="asc"?"desc":"asc";else{st.sort=k;st.dir="desc"};renderTable(containerId,rows,cols,opt)}); if(opt.onClick)el.querySelectorAll("tbody tr").forEach(tr=>tr.onclick=()=>opt.onClick(sorted[Number(tr.dataset.i)])); }
    function val(r,k){ const v=r[k]; return Array.isArray(v)?v.join(" "):v??"" } function cell(v){ return Array.isArray(v)?v.join("; "):v??"" }
    async function init(){ $("mainNav").onclick=e=>{if(e.target.dataset.page)showPage(e.target.dataset.page)}; $("exportBtn").onclick=csvExport; $("drawerClose").onclick=closeDrawer; $("drawerBackdrop").onclick=closeDrawer; $("resetBtn").onclick=()=>{ if(state.network) state.network.reset(); }; await renderOverview(); }
    async function showPage(page){ state.page=page; document.querySelectorAll(".nav button").forEach(b=>b.classList.toggle("active",b.dataset.page===page)); document.querySelectorAll(".page").forEach(p=>p.classList.remove("active")); $("page-"+page).classList.add("active"); if(page==="overview")await renderOverview(); if(page==="patents")await renderPatents(); if(page==="publications")await renderPublications(); if(page==="integrated")await renderIntegrated(); if(page==="ecored")await renderEcoRed(); if(page==="data")await renderDataExplorer(); }
    async function renderOverview(){ const [ps,bs,is]=await Promise.all([loadJson("publications_summary.json"),loadJson("patents_summary.json"),loadJson("integrated_summary.json")]); $("globalKpis").innerHTML=[["Pubblicazioni",ps.total_publications],["Brevetti",bs.total_patents],["Tecnologie comuni",is.shared_technologies],["Citazioni",bs.citations],["Paesi science",ps.countries],["Periodo",`${Math.min(ps.year_min,bs.year_min)}-${Math.max(ps.year_max,bs.year_max)}`]].map(x=>`<div class="kpi"><strong>${fmt(x[1])}</strong><span>${esc(x[0])}</span></div>`).join(""); $("page-overview").innerHTML=sectionHead("Overview","Vista manageriale integrata su pubblicazioni scientifiche, brevetti e tecnologie comuni.")+`<div class="grid cols-4">${metricCard("Pubblicazioni",fmt(ps.total_publications),"Dataset scientifico finale")}${metricCard("Brevetti",fmt(bs.total_patents),"Dataset brevettuale arricchito")}${metricCard("ECO RED-like paper",fmt(ps.eco_red_like_publications),"MEA/AEM/GDE/non-noble/CO2-to-CO")}${metricCard("Tecnologie comuni",fmt(is.shared_technologies),"Ponte science ↔ IP")}</div><div class="grid cols-3" style="margin-top:16px"><div class="card"><h3>Top paesi pubblicazioni</h3>${barRows(ps.top_countries||[])}</div><div class="card"><h3>Top tecnologie science</h3>${barRows(ps.top_technologies||[])}</div><div class="card"><h3>Top assignee brevetti</h3>${barRows(bs.top_assignees||[])}</div></div><div class="card" style="margin-top:16px"><h3>Insight automatici</h3><div class="grid cols-3"><div>${badge("Molte pubblicazioni / pochi brevetti","cyan")} aree scientificamente vive ma meno appropriate.</div><div>${badge("Molte pubblicazioni / molti brevetti","orange")} aree calde e competitive.</div><div>${badge("Pochi paper / molti brevetti","red")} aree più industriali o protette.</div></div></div>`; }
    async function renderPatents(){ const [sum,net,tbl]=await Promise.all([loadJson("patents_summary.json"),loadJson("patents_network_light.json"),loadJson("patents_tables.json")]); $("page-patents").innerHTML=sectionHead("Patents","Patent Intelligence: overview, rete, attori, mappa tecnologica e tabella brevetti.")+`<div class="tabs"><button class="tab active" data-pat-tab="overview">Overview</button><button class="tab" data-pat-tab="network">Network</button><button class="tab" data-pat-tab="actors">Actors</button><button class="tab" data-pat-tab="technology">Technology Map</button><button class="tab" data-pat-tab="table">Patent table</button></div><div id="patContent"></div>`; const show=t=>{document.querySelectorAll("[data-pat-tab]").forEach(x=>x.classList.toggle("active",x.dataset.patTab===t)); if(t==="overview")renderPatentOverview(sum); if(t==="network")renderNetworkSection("patContent",net,"patent"); if(t==="actors")renderActorTable(tbl.actors); if(t==="technology")renderPatentTechnologyMap(sum); if(t==="table")renderPatentTable(tbl.patents);}; document.querySelectorAll("[data-pat-tab]").forEach(b=>b.onclick=()=>show(b.dataset.patTab)); show("overview"); }
    async function renderPublications(){ const [sum,net,perf,tbl]=await Promise.all([loadJson("publications_summary.json"),loadJson("publications_network_light.json"),loadJson("publications_performance.json"),loadJson("publications_tables.json")]); $("page-publications").innerHTML=sectionHead("Publication Intelligence","Analisi delle pubblicazioni scientifiche: overview, network, performance frontier, geografia e tabella dettagliata.")+`<div class="tabs"><button class="tab active" data-pub-tab="overview">Overview</button><button class="tab" data-pub-tab="network">Network</button><button class="tab" data-pub-tab="performance">Performance Frontier</button><button class="tab" data-pub-tab="geo">Scientific Geography</button><button class="tab" data-pub-tab="table">Publication Table</button></div><div id="pubContent"></div>`; const show=t=>{document.querySelectorAll("[data-pub-tab]").forEach(x=>x.classList.toggle("active",x.dataset.pubTab===t)); if(t==="overview")renderPubOverview(sum); if(t==="network")renderNetworkSection("pubContent",net,"publication"); if(t==="performance")renderPerformance(perf); if(t==="geo")renderGeo(sum,tbl.publications); if(t==="table")renderPublicationTable(tbl.publications)}; document.querySelectorAll("[data-pub-tab]").forEach(b=>b.onclick=()=>show(b.dataset.pubTab)); show("overview"); }
    function renderPubOverview(s){ $("pubContent").innerHTML=`<div class="grid cols-4">${metricCard("Pubblicazioni",fmt(s.total_publications),`${s.year_min}-${s.year_max}`)}${metricCard("Paesi",fmt(s.countries),"provenienza scientifica")}${metricCard("Autori",fmt(s.authors),"autori unici stimati")}${metricCard("ECO RED-like",fmt(s.eco_red_like_publications),"paper vicini al focus")}</div><div class="grid cols-3" style="margin-top:16px"><div class="card"><h3>Top paesi</h3>${barRows(s.top_countries||[])}</div><div class="card"><h3>Top tecnologie</h3>${barRows(s.top_technologies||[])}</div><div class="card"><h3>Performance</h3>${Object.entries(s.metrics||{}).map(([k,v])=>`<div class="detail-row"><b>${esc(k)}</b>media ${v.mean??"n.d."} · max ${v.max??"n.d."} · n=${v.valid_count}</div>`).join("")}</div></div>`; }
    function renderPerformance(perf){ const metrics=Object.entries(perf.metrics||{}); $("pubContent").innerHTML=`<div class="grid cols-3">${metrics.map(([k,m])=>`<div class="card"><h3>${esc(k)}</h3><div class="hint">Frontiera cumulata, massimo annuo e benchmark ECO RED.</div>${lineChart(m)}<div class="detail-row"><b>Benchmark ECO RED</b>${perf.benchmarks[k]?.value??"n.d."} ${perf.benchmarks[k]?.unit??""}</div><div class="detail-row"><b>Soglia pre-industriale</b>${thresholdText(perf.benchmarks[k])}</div></div>`).join("")}</div>`; }
    function lineChart(m){ const vals=(m.frontier||[]).map(x=>x.value); const max=Math.max(1,...vals, m.limit||0); return `<svg viewBox="0 0 360 180" width="100%" height="190" role="img">${(m.annual||[]).map((x,i,a)=>`<rect x="${20+i*(320/Math.max(1,a.length))}" y="${160-(x.max/max)*140}" width="${Math.max(2,260/Math.max(1,a.length))}" height="${(x.max/max)*140}" fill="rgba(37,99,235,.18)"/>`).join("")}<polyline points="${(m.frontier||[]).map((x,i,a)=>`${20+i*(320/Math.max(1,a.length-1))},${160-(x.value/max)*140}`).join(" ")}" fill="none" stroke="#0f766e" stroke-width="3"/><line x1="20" x2="340" y1="${160-((m.limit||max)/max)*140}" y2="${160-((m.limit||max)/max)*140}" stroke="#64748b" stroke-dasharray="4 4"/></svg>`; }
    function thresholdText(b){ if(!b)return"n.d."; return b.threshold_high?`${b.threshold}-${b.threshold_high} ${b.unit}`:`≥ ${b.threshold} ${b.unit}`; }
    function renderGeo(sum,rows){ const noChina=rows.filter(r=>r.country!=="China"); const eu=rows.filter(r=>["Italy","Germany","France","Netherlands","Belgium","Spain","Denmark","Switzerland","United Kingdom","Norway","Sweden","Austria"].includes(r.country)); $("pubContent").innerHTML=`<div class="grid cols-3">${metricCard("Mondo",fmt(rows.length),"pubblicazioni totali")}${metricCard("Senza Cina",fmt(noChina.length),"toggle metodologico")}${metricCard("Europa",fmt(eu.length),"vista regionale")}</div><div class="grid cols-2" style="margin-top:16px"><div class="card"><h3>Pubblicazioni per paese</h3>${barRows(sum.top_countries||[])}</div><div class="card"><h3>Perché toggle Cina?</h3><p class="hint">La Cina può avere intensità e velocità di pubblicazione diverse. Il confronto mondo vs mondo senza Cina aiuta a capire se i trend sono globali o trainati da un singolo sistema scientifico.</p></div></div>`; }
    async function renderIntegrated(){ const [sum,matrix,net,pos]=await Promise.all([loadJson("integrated_summary.json"),loadJson("integrated_matrix.json"),loadJson("integrated_network_light.json"),loadJson("eco_red_positioning.json")]); $("page-integrated").innerHTML=sectionHead("Integrated Intelligence","Confronto strategico tra pubblicazioni e brevetti usando tecnologie comuni come ponte, senza inferire collegamenti diretti non dimostrati.")+`<div class="tabs"><button class="tab active" data-int-tab="matrix">Science vs Patent Matrix</button><button class="tab" data-int-tab="shared">Shared Technology Map</button><button class="tab" data-int-tab="network">Integrated Network</button><button class="tab" data-int-tab="white">White Space</button><button class="tab" data-int-tab="position">ECO RED Positioning</button></div><div id="intContent"></div>`; const show=t=>{document.querySelectorAll("[data-int-tab]").forEach(x=>x.classList.toggle("active",x.dataset.intTab===t)); if(t==="matrix")renderMatrix(matrix.matrix); if(t==="shared")renderShared(matrix.matrix); if(t==="network")renderNetworkSection("intContent",net,"integrated"); if(t==="white")renderWhite(sum.white_spaces); if(t==="position")renderPosition(pos)}; document.querySelectorAll("[data-int-tab]").forEach(b=>b.onclick=()=>show(b.dataset.intTab)); show("matrix"); }
    function renderMatrix(rows){ const qs=["Molte pubblicazioni / pochi brevetti","Molte pubblicazioni / molti brevetti","Poche pubblicazioni / molti brevetti","Poche pubblicazioni / pochi brevetti"]; $("intContent").innerHTML=`<div class="matrix">${qs.map(q=>`<div class="quadrant"><h3>${esc(q)}</h3><div class="hint">${esc((rows.find(r=>r.quadrant===q)||{}).meaning||"")}</div>${rows.filter(r=>r.quadrant===q).slice(0,16).map(r=>`<span class="point" title="Pub ${r.publications} · Brev ${r.patents}">${esc(r.technology)}</span>`).join("")}</div>`).join("")}</div>`; setExport(rows,sharedCols(),"science_vs_patent_matrix.csv"); }
    function renderShared(rows){ $("intContent").innerHTML=`<div class="card flush"><div class="table-toolbar"><div><b>Shared Technology Map</b><div class="hint">Tecnologie comuni tra pubblicazioni e brevetti.</div></div></div><div class="table-wrap" id="sharedTable"></div></div>`; renderTable("sharedTable",rows,sharedCols()); setExport(rows,sharedCols(),"shared_technology_map.csv"); }
    function renderWhite(ws){ const blocks=[["Molte pubblicazioni / pochi brevetti",ws.many_publications_few_patents],["Molti brevetti / poche pubblicazioni",ws.many_patents_few_publications],["Calde e competitive",ws.hot_competitive],["ECO RED meno affollate",ws.eco_red_less_crowded]]; $("intContent").innerHTML=`<div class="grid cols-2">${blocks.map(([t,arr])=>`<div class="card"><h3>${esc(t)}</h3>${(arr||[]).slice(0,12).map(r=>`<div class="detail-row"><b>${esc(r.technology)}</b>Pub ${r.publications} · Brev ${r.patents}<br><span class="hint">${esc(r.meaning||"")}</span></div>`).join("")}</div>`).join("")}</div>`; }
    function renderPosition(pos){ $("intContent").innerHTML=`<div class="grid cols-2"><div class="card"><h3>Benchmark ECO RED</h3>${Object.entries(pos.benchmarks||{}).map(([k,b])=>`<div class="detail-row"><b>${esc(k)}</b>${b.value} ${b.unit} · soglia ${thresholdText(b)}</div>`).join("")}</div><div class="card"><h3>Lettura manageriale</h3>${(pos.managerial_reading||[]).map(x=>`<div class="detail-row">${esc(x)}</div>`).join("")}</div></div><div class="card flush" style="margin-top:16px"><div class="table-toolbar"><b>Science/IP by ECO RED focus</b></div><div class="table-wrap" id="posTable"></div></div>`; renderTable("posTable",pos.science_ip_by_focus||[],sharedCols()); setExport(pos.science_ip_by_focus||[],sharedCols(),"eco_red_positioning.csv"); }
    async function renderEcoRed(){ const [pub,pat,intg,pos]=await Promise.all([loadJson("publications_summary.json"),loadJson("patents_summary.json"),loadJson("integrated_matrix.json"),loadJson("eco_red_positioning.json")]); const focus=(intg.matrix||[]).filter(r=>r.eco_red_relevance); $("page-ecored").innerHTML=sectionHead("ECO RED Focus","Lettura strategica combinata su MEA, AEM, GDE, catalizzatori non nobili e CO₂-to-CO.")+`<div class="grid cols-4">${metricCard("Paper ECO RED-like",fmt(pub.eco_red_like_publications),"pubblicazioni vicine")}${metricCard("Focus brevetti",fmt((pat.focus||[]).reduce((a,b)=>a+b.count,0)),"tag brevettuali")}${metricCard("Tecnologie focus",fmt(focus.length),"ponte science/IP")}${metricCard("Benchmark", "97% · 200 · 300h","FE · corrente · stabilità")}</div><div class="grid cols-2" style="margin-top:16px"><div class="card"><h3>Attori brevettuali da monitorare</h3>${barRows((pos.closest_patent_actors||[]).map(a=>({name:a.name,count:a.patents})).slice(0,10))}</div><div class="card"><h3>Tecnologie ECO RED science/IP</h3>${focus.map(r=>`<div class="detail-row"><b>${esc(r.technology)}</b>Pub ${r.publications} · Brev ${r.patents}<br>${badge(r.quadrant,tone(r.quadrant))}</div>`).join("")}</div></div>`; setExport(focus,sharedCols(),"eco_red_focus_integrated.csv"); }
    async function renderDataExplorer(){ const [pub,pat]=await Promise.all([loadJson("publications_tables.json"),loadJson("patents_tables.json")]); $("page-data").innerHTML=sectionHead("Data Explorer","Tabelle filtrabili ed esportabili per pubblicazioni e brevetti.")+`<div class="tabs"><button class="tab active" data-data-tab="pub">Publications</button><button class="tab" data-data-tab="pat">Patents</button></div><div id="dataContent"></div>`; const show=t=>{document.querySelectorAll("[data-data-tab]").forEach(x=>x.classList.toggle("active",x.dataset.dataTab===t)); if(t==="pub")renderPublicationTable(pub.publications,"dataContent"); else renderPatentTable(pat.patents,"dataContent")}; document.querySelectorAll("[data-data-tab]").forEach(b=>b.onclick=()=>show(b.dataset.dataTab)); show("pub"); }
    function renderNetworkSection(containerId,net,kind){ const views=Object.keys(net.views); $(containerId).innerHTML=`<div class="network-layout"><aside class="panel"><div class="panel-body filters"><div class="field"><label>Vista network</label><select id="${kind}View">${views.map(v=>`<option value="${v}">${esc(net.views[v].label)}</option>`).join("")}</select></div><div class="field"><label>Ricerca</label><input id="${kind}Search" placeholder="cerca nodo o keyword"></div><div class="field"><label>Max nodi</label><input id="${kind}Max" type="range" min="40" max="420" value="220"></div><div class="hint" id="${kind}Desc"></div></div></aside><section class="panel canvas-card"><div class="canvas-head"><div><h3 id="${kind}Title"></h3><div class="hint">Zoom con rotellina, trascina per muovere la rete.</div></div><button class="btn small" id="${kind}Fit">Centra</button></div><div class="canvas-wrap"><canvas class="network" id="${kind}Canvas"></canvas><div class="status" id="${kind}Status"></div><div class="empty" id="${kind}Empty"><div>Nessun nodo visualizzabile.<br><span class="hint">Riduci filtri o cambia vista.</span></div></div></div></section><aside class="panel"><div class="panel-body" id="${kind}Detail"></div></aside></div>`; const render=()=>{const v=$(kind+"View").value; $(kind+"Desc").textContent=net.views[v].description||""; $(kind+"Title").textContent=net.views[v].label; state.network=new MiniNetwork(kind,net.views[v]); state.network.render();}; $(kind+"View").oninput=render; $(kind+"Search").oninput=()=>state.network.render(); $(kind+"Max").oninput=()=>state.network.render(); $(kind+"Fit").onclick=()=>state.network.reset(); render(); }
    class MiniNetwork{constructor(prefix,view){this.p=prefix;this.view=view;this.canvas=$(prefix+"Canvas");this.ctx=this.canvas.getContext("2d");this.t={x:0,y:0,s:1};this.nodes=[];this.edges=[];this.drag=null;this.pan=false;this.last=null;this.selected=null;this.bind();this.resize()}bind(){if(this.bound)return;this.bound=true;this.canvas.onpointerdown=e=>this.down(e);this.canvas.onpointermove=e=>this.move(e);this.canvas.onpointerup=e=>this.up(e);this.canvas.onpointerleave=e=>this.up(e);this.canvas.onwheel=e=>this.wheel(e);window.addEventListener("resize",()=>this.resize())}resize(){const r=this.canvas.getBoundingClientRect(),d=window.devicePixelRatio||1;this.canvas.width=Math.max(320,r.width*d);this.canvas.height=Math.max(320,r.height*d);this.ctx.setTransform(d,0,0,d,0,0)}render(){const q=($(this.p+"Search")?.value||"").toLowerCase();const max=Number($(this.p+"Max")?.value||220);let ids=new Set();let edges=this.view.edges||[]; if(q){edges=edges.filter(e=>label(e.source,this.view).toLowerCase().includes(q)||label(e.target,this.view).toLowerCase().includes(q)||(e.items||[]).join(" ").toLowerCase().includes(q))} const deg={};edges.forEach(e=>{deg[e.source]=(deg[e.source]||0)+(e.weight||1);deg[e.target]=(deg[e.target]||0)+(e.weight||1)});Object.keys(deg).sort((a,b)=>deg[b]-deg[a]).slice(0,max).forEach(x=>ids.add(x));edges=edges.filter(e=>ids.has(e.source)&&ids.has(e.target));const nodeMap=new Map((this.view.nodes||[]).map(n=>[n.id,n]));this.nodes=[...ids].map(id=>({...nodeMap.get(id),id,label:label(id,this.view),degree:deg[id]||1,x:Math.random()*900,y:Math.random()*560,vx:0,vy:0}));const idx=new Map(this.nodes.map(n=>[n.id,n]));this.edges=edges.map(e=>({...e,s:idx.get(e.source),t:idx.get(e.target)})).filter(e=>e.s&&e.t);$(this.p+"Status").innerHTML=[`${this.nodes.length} nodi`,`${this.edges.length} archi`].map(x=>`<span>${x}</span>`).join("");$(this.p+"Empty").classList.toggle("show",!this.edges.length);this.tick=0;this.loop()}loop(){if(state.network!==this)return;this.sim();this.draw();requestAnimationFrame(()=>this.loop())}sim(){const w=this.canvas.clientWidth||800,h=this.canvas.clientHeight||520;for(const e of this.edges){const s=e.s,t=e.t,dx=t.x-s.x,dy=t.y-s.y,dist=Math.max(25,Math.hypot(dx,dy)),f=(dist-100)*.005,fx=dx/dist*f,fy=dy/dist*f;s.vx+=fx;t.vx-=fx;s.vy+=fy;t.vy-=fy}for(let i=0;i<this.nodes.length;i++)for(let j=i+1;j<this.nodes.length;j++){const a=this.nodes[i],b=this.nodes[j],dx=b.x-a.x,dy=b.y-a.y,d2=Math.max(120,dx*dx+dy*dy),f=Math.min(2,520/d2),d=Math.sqrt(d2),fx=dx/d*f,fy=dy/d*f;a.vx-=fx;b.vx+=fx;a.vy-=fy;b.vy+=fy}for(const n of this.nodes){if(n!==this.drag){n.vx+=(w/2-n.x)*.0008;n.vy+=(h/2-n.y)*.0008;n.vx*=.86;n.vy*=.86;n.x+=n.vx;n.y+=n.vy}}}draw(){const c=this.ctx,w=this.canvas.clientWidth||800,h=this.canvas.clientHeight||520;c.clearRect(0,0,w,h);c.save();c.translate(this.t.x,this.t.y);c.scale(this.t.s,this.t.s);const neigh=this.selected?new Set([this.selected.id]):null;if(neigh)this.edges.forEach(e=>{if(e.source===this.selected.id)neigh.add(e.target);if(e.target===this.selected.id)neigh.add(e.source)});for(const e of this.edges){const rel=!neigh||neigh.has(e.source)&&neigh.has(e.target);c.strokeStyle=`rgba(37,99,235,${rel ? .25 : .045})`;c.lineWidth=Math.max(.8,Math.log1p(e.weight||1));c.beginPath();c.moveTo(e.s.x,e.s.y);c.lineTo(e.t.x,e.t.y);c.stroke()}for(const n of this.nodes){const rel=!neigh||neigh.has(n.id),r=6+Math.min(12,Math.log1p(n.degree||1)*2);c.globalAlpha=rel?1:.22;c.fillStyle=typeColors[n.type]||"#94a3b8";c.beginPath();c.arc(n.x,n.y,r,0,Math.PI*2);c.fill();c.strokeStyle=n===this.selected?"#07111f":"#fff";c.lineWidth=n===this.selected?4:1.5;c.stroke();if(n===this.selected||n.degree>Math.max(4,this.nodes.length/45)){c.globalAlpha=1;c.font="12px Inter,Segoe UI,sans-serif";c.fillStyle="rgba(255,255,255,.9)";const tx=trunc(n.label,24),tw=c.measureText(tx).width+10;c.fillRect(n.x+r+5,n.y-10,tw,20);c.fillStyle="#263241";c.fillText(tx,n.x+r+10,n.y+4)}}c.globalAlpha=1;c.restore()}world(e){const r=this.canvas.getBoundingClientRect();return{x:(e.clientX-r.left-this.t.x)/this.t.s,y:(e.clientY-r.top-this.t.y)/this.t.s}}nodeAt(p){for(let i=this.nodes.length-1;i>=0;i--){const n=this.nodes[i],r=8+Math.min(12,Math.log1p(n.degree||1)*2);if(Math.hypot(n.x-p.x,n.y-p.y)<=r+4)return n}return null}down(e){const p=this.world(e),n=this.nodeAt(p);this.last={x:e.clientX,y:e.clientY};if(n)this.drag=n;else this.pan=true}move(e){if(this.drag){const p=this.world(e);this.drag.x=p.x;this.drag.y=p.y}else if(this.pan&&this.last){this.t.x+=e.clientX-this.last.x;this.t.y+=e.clientY-this.last.y;this.last={x:e.clientX,y:e.clientY}}}up(e){if(this.drag){this.selected=this.drag;$(this.p+"Detail").innerHTML=`<h3>${esc(this.selected.label)}</h3><div class="detail-row"><b>Tipo</b>${esc(this.selected.type)}</div><div class="detail-row"><b>Grado</b>${fmt(this.selected.degree)}</div>`}this.drag=null;this.pan=false}wheel(e){e.preventDefault();const f=e.deltaY<0?1.08:.92;this.t.s=Math.max(.25,Math.min(4,this.t.s*f))}reset(){this.t={x:0,y:0,s:1};this.render()}}
    function label(id,view){return (view.nodes||[]).find(n=>n.id===id)?.label||String(id).replace(/^[^:]+::/,"")}
    function publicationCols(){return[{key:"title",label:"Title",render:r=>esc(trunc(r.title,90))},{key:"authors",label:"Authors",render:r=>esc((r.authors||[]).slice(0,3).join("; "))},{key:"year",label:"Year"},{key:"country",label:"Country"},{key:"doi",label:"DOI"},{key:"FE_CO",label:"FE_CO"},{key:"Stability",label:"Stability"},{key:"Current Density",label:"Current Density"},{key:"technologies",label:"Technologies",render:r=>chips(r.technologies,5)}]}
    function patentCols(){return[{key:"id",label:"Patent"},{key:"title",label:"Title",render:r=>esc(trunc(r.title,90))},{key:"year",label:"Year"},{key:"assignees",label:"Assignee",render:r=>chips(r.assignees,3)},{key:"focus",label:"Focus",render:r=>chips(r.focus,4)},{key:"cpc_groups",label:"CPC",render:r=>chips(r.cpc_groups,4)},{key:"legal_state",label:"Legal",render:r=>badge(r.legal_state,tone(r.legal_state))}]}
    function sharedCols(){return[{key:"technology",label:"Technology"},{key:"publications",label:"Publications"},{key:"patents",label:"Patents"},{key:"ratio_publications_patents",label:"Pub/Patent ratio"},{key:"quadrant",label:"Matrix quadrant"},{key:"eco_red_relevance",label:"ECO RED relevant"}]}
    function actorCols(){return[{key:"name",label:"Assignee"},{key:"patents",label:"Patents"},{key:"focus",label:"Focus",render:r=>chips(r.focus,4)},{key:"domains",label:"Domains",render:r=>chips(r.domains,3)},{key:"cpc_groups",label:"CPC",render:r=>chips(r.cpc_groups,3)},{key:"citations",label:"Citations"}]}
    function renderPublicationTable(rows,container="pubContent"){ $(container).innerHTML=`<div class="card flush"><div class="table-toolbar"><div><b>Publication Table</b><div class="hint">Ricerca, ordinamento, export e dettaglio pubblicazione.</div></div><input id="${container}Search" placeholder="Cerca pubblicazione"></div><div class="table-wrap" id="${container}Table"></div></div>`; const draw=()=>{const q=($(container+"Search").value||"").toLowerCase();const f=rows.filter(r=>!q||JSON.stringify(r).toLowerCase().includes(q));renderTable(container+"Table",f,publicationCols(),{onClick:openPublication});setExport(f,publicationCols(),"publications.csv")}; $(container+"Search").oninput=draw; draw(); }
    function renderPatentTable(rows,container="patContent"){ $(container).innerHTML=`<div class="card flush"><div class="table-toolbar"><div><b>Patent Table</b><div class="hint">Brevetti, assignee, CPC e focus.</div></div><input id="${container}Search" placeholder="Cerca brevetto"></div><div class="table-wrap" id="${container}Table"></div></div>`; const draw=()=>{const q=($(container+"Search").value||"").toLowerCase();const f=rows.filter(r=>!q||JSON.stringify(r).toLowerCase().includes(q));renderTable(container+"Table",f,patentCols(),{onClick:openPatent});setExport(f,patentCols(),"patents.csv")}; $(container+"Search").oninput=draw; draw(); }
    function renderPatentOverview(s){ $("patContent").innerHTML=`<div class="grid cols-4">${metricCard("Brevetti",fmt(s.total_patents),`${s.year_min}-${s.year_max}`)}${metricCard("Assignee",fmt(s.assignees),"attori brevettuali")}${metricCard("Nodi",fmt(s.nodes),"ipergrafo")}${metricCard("Citazioni",fmt(s.citations),"link patent-patent")}</div><div class="grid cols-3" style="margin-top:16px"><div class="card"><h3>Top assignee</h3>${barRows(s.top_assignees||[])}</div><div class="card"><h3>Top CPC group</h3>${barRows(s.top_cpc_groups||[])}</div><div class="card"><h3>Focus tecnologici</h3>${barRows(s.focus||[])}</div></div>`; setExport([s],["total_patents","assignees","nodes","citations"].map(k=>({key:k,label:k})),"patents_summary.csv"); }
    function renderPatentTechnologyMap(s){ const rows=[...(s.top_cpc_groups||[]).map(x=>({...x,type:"CPC group"})),...(s.top_domains||[]).map(x=>({...x,type:"Domain"})),...(s.focus||[]).map(x=>({...x,type:"Focus"}))]; $("patContent").innerHTML=`<div class="grid cols-3"><div class="card"><h3>CPC group</h3>${barRows(s.top_cpc_groups||[])}</div><div class="card"><h3>Domini tecnologici</h3>${barRows(s.top_domains||[])}</div><div class="card"><h3>Focus ECO RED-like</h3>${barRows(s.focus||[])}</div></div><div class="card" style="margin-top:16px"><h3>Come leggere</h3><p class="hint">Questa vista sintetizza le aree tecnologiche brevettuali: CPC per classificazione ufficiale, domini per macro-area tecnica, focus per vicinanza a MEA/AEM/GDE/catalizzatori non nobili.</p></div>`; setExport(rows,[{key:"type",label:"Tipo"},{key:"name",label:"Voce"},{key:"count",label:"Conteggio"}],"patent_technology_map.csv"); }
    function renderActorTable(rows){ $("patContent").innerHTML=`<div class="card flush"><div class="table-toolbar"><b>Actor Intelligence</b></div><div class="table-wrap" id="actorTable"></div></div>`; renderTable("actorTable",rows,actorCols()); setExport(rows,actorCols(),"assignees.csv"); }
    function openPublication(r){ $("drawerEyebrow").textContent="Publication detail"; $("drawerTitle").textContent=trunc(r.title,90); $("drawerBody").innerHTML=`<div class="detail-row"><b>Titolo</b>${esc(r.title)}</div><div class="detail-row"><b>Autori</b>${esc((r.authors||[]).join("; "))}</div><div class="detail-row"><b>Anno / Paese</b>${r.year||"n.d."} · ${esc(r.country)}</div><div class="detail-row"><b>DOI</b>${esc(r.doi||"n.d.")}</div><div class="detail-row"><b>Abstract</b>${esc(r.abstract||"n.d.")}</div><div class="detail-row"><b>Performance</b>FE_CO ${r.FE_CO??"n.d."} · Stabilità ${r.Stability??"n.d."} h · Corrente ${r["Current Density"]??"n.d."} mA/cm²</div><div class="detail-row"><b>Catalizzatori/materiali</b>${esc(r.catalysts_materials)}</div><div class="detail-row"><b>Cella</b>${esc(r.cell_technology)}</div><div class="detail-row"><b>Membrane/MEA/ionomeri</b>${esc(r.membranes_mea_ionomers)}</div><div class="detail-row"><b>Elettrodi/GDE</b>${esc(r.electrodes_gde)}</div><div class="detail-row"><b>Condizioni operative</b>${esc(r.operating_conditions)}</div><div class="detail-row"><b>Tecnologie ECO RED-like</b>${chips(r.technologies,12)}</div><div class="detail-row"><b>Source URL</b>${r.source_url?`<a href="${esc(r.source_url)}" target="_blank" rel="noopener">${esc(r.source_url)}</a>`:"n.d."}</div>`; openDrawer(); }
    function openPatent(r){ $("drawerEyebrow").textContent="Patent detail"; $("drawerTitle").textContent=trunc(`${r.id} · ${r.title}`,90); $("drawerBody").innerHTML=`<div class="detail-row"><b>Numero brevetto</b>${esc(r.id)}</div><div class="detail-row"><b>Titolo</b>${esc(r.title)}</div><div class="detail-row"><b>Anno</b>${r.year||"n.d."}</div><div class="detail-row"><b>Assignee</b>${chips(r.assignees,8)}</div><div class="detail-row"><b>Stato legale</b>${badge(r.legal_state,tone(r.legal_state))}</div><div class="detail-row"><b>Paesi</b>${chips(r.countries,8)}</div><div class="detail-row"><b>CPC</b>${chips([...(r.cpc_groups||[]),...(r.cpc_codes||[]).slice(0,8)],14)}</div><div class="detail-row"><b>Domini</b>${chips(r.domains,8)}</div><div class="detail-row"><b>Concetti tecnici</b>${chips(r.concepts,16)}</div><div class="detail-row"><b>Focus tecnologico</b>${chips(r.focus,8)}</div><div class="detail-row"><b>Citazioni interne</b>${r.citations_in||0} ricevute · ${r.citations_out||0} in uscita</div><div class="detail-row"><b>Hyperedge</b>Questo brevetto collega simultaneamente attori, tecnologie, concetti, paesi e classificazioni. Per questo agisce come ponte informativo nell'ipergrafo.</div>`; openDrawer(); }
    function openDrawer(){ $("drawerBackdrop").classList.add("show"); $("drawer").classList.add("show"); } function closeDrawer(){ $("drawerBackdrop").classList.remove("show"); $("drawer").classList.remove("show"); }
    init();
  </script>
</body>
</html>'''
    OUT_HTML.write_text(html, encoding="utf-8")


def main():
    pub_rows, pub_summary, pub_metrics = build_publications()
    pub_network = build_publication_network(pub_rows)
    patents = json.loads(PATENT_FILE.read_text(encoding="utf-8"))
    pat_summary = patent_stats(patents)
    pat_network = build_patent_network_light(patents)
    pat_tables = build_patent_tables(patents)
    int_summary, int_matrix, int_network, eco_position = build_integrated(pub_rows, pub_metrics, patents, pat_tables)

    write_json("publications_summary.json", pub_summary)
    write_json("publications_network_light.json", pub_network)
    write_json("publications_performance.json", {"metrics": pub_metrics, "benchmarks": ECO_BENCHMARKS})
    write_json("publications_tables.json", {"publications": pub_rows})
    write_json("patents_summary.json", pat_summary)
    write_json("patents_network_light.json", pat_network)
    write_json("patents_tables.json", pat_tables)
    write_json("integrated_summary.json", int_summary)
    write_json("integrated_matrix.json", int_matrix)
    write_json("integrated_network_light.json", int_network)
    write_json("eco_red_positioning.json", eco_position)
    build_html()
    print(f"Built modular dashboard at {OUT_HTML}")
    print(f"Data files written to {DATA_DIR}")


if __name__ == "__main__":
    main()
