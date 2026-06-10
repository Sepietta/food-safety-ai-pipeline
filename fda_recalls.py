import requests
from datetime import datetime
from typing import Optional

BASE_URL = "https://api.fda.gov/food/enforcement.json"

PATHOGEN_SEARCH_TERMS = {
    "E. coli O157:H7":        ["E.+coli+O157", "STEC"],
    "Salmonella spp.":        ["Salmonella"],
    "Listeria monocytogenes": ["Listeria"],
    "Total coliforms":        ["coliform"],
    "Aerobic mesophiles":     [],
    "Molds and yeasts":       ["mold", "yeast", "mycotoxin"],
}

RECALL_COST_BY_CLASS = {
    "Class I":   "$8.5M",
    "Class II":  "$2.1M",
    "Class III": "$0.3M",
}


def _query_fda(search_term: str) -> dict:
    params = {
        "search": f'reason_for_recall:{search_term}',
        "limit": 100,
    }
    try:
        resp = requests.get(BASE_URL, params=params, timeout=8)
        if resp.status_code == 200:
            return resp.json()
        return {}
    except Exception:
        return {}


def get_recall_intel(pathogen: str) -> Optional[dict]:
    search_terms = PATHOGEN_SEARCH_TERMS.get(pathogen, [])
    if not search_terms:
        return None

    all_results = []
    for term in search_terms:
        data = _query_fda(term)
        all_results.extend(data.get("results", []))

    if not all_results:
        return None

    # Deduplicate by recall number
    seen = set()
    unique = []
    for r in all_results:
        key = r.get("recall_number", r.get("product_description", ""))
        if key not in seen:
            seen.add(key)
            unique.append(r)

    # Sort by date descending
    def parse_date(r):
        d = r.get("recall_initiation_date", "19000101")
        try:
            return datetime.strptime(str(d), "%Y%m%d")
        except Exception:
            return datetime(1900, 1, 1)

    unique.sort(key=parse_date, reverse=True)
    most_recent = unique[0]

    # Most common classification
    classes = [r.get("classification", "") for r in unique if r.get("classification")]
    top_class = max(set(classes), key=classes.count) if classes else "Class I"

    # Format most recent date
    raw_date = str(most_recent.get("recall_initiation_date", ""))
    try:
        fmt_date = datetime.strptime(raw_date, "%Y%m%d").strftime("%B %Y")
    except Exception:
        fmt_date = "recent"

    # Truncate product description
    product = most_recent.get("product_description", "food product")
    if len(product) > 80:
        product = product[:77] + "..."

    # Count last 24 months
    cutoff = datetime.now().replace(year=datetime.now().year - 2)
    recent_count = sum(1 for r in unique if parse_date(r) >= cutoff)

# Get recall number and build FDA search URL for the most recent recall
    recall_number = most_recent.get("recall_number", "N/A")
    fda_url = (
        f"https://www.accessdata.fda.gov/scripts/ires/index.cfm"
        f"?action=ClassificationSearch&ClassificationSearchType=recall"
        f"&recallNumber={recall_number}"
    )

    return {
        "pathogen":          pathogen,
        "recall_count":      len(unique),
        "recent_count":      recent_count,
        "most_recent":       product,
        "most_recent_date":  fmt_date,
        "top_class":         top_class,
        "avg_cost":          RECALL_COST_BY_CLASS.get(top_class, "$2.1M"),
        "months_searched":   24,
        "recall_number":     recall_number,
        "fda_url":           fda_url,
        "recalling_firm":    most_recent.get("recalling_firm", ""),
    }


def get_all_recall_intel(pathogens: list[str]) -> dict[str, Optional[dict]]:
    intel = {}
    for p in pathogens:
        intel[p] = get_recall_intel(p)
    return intel