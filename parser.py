import pandas as pd
from dataclasses import dataclass
from typing import Optional

# Legal limits per pathogen (CFU/g or CFU/mL)
# Based on FDA Food Safety Modernization Act (FSMA) and FDA/USDA criteria
LIMITS = {
    "E. coli O157:H7":        {"limit": 0,      "unit": "CFU/g",   "action": "IMMEDIATE REJECTION — adulterant pathogen"},
    "Salmonella spp.":        {"limit": 0,      "unit": "CFU/25g", "action": "IMMEDIATE REJECTION — adulterant pathogen"},
    "Listeria monocytogenes": {"limit": 0,      "unit": "CFU/g",   "action": "IMMEDIATE REJECTION — adulterant pathogen"},
    "Total coliforms":        {"limit": 100,    "unit": "CFU/g",   "action": "Review process — possible cross-contamination"},
    "Aerobic mesophiles":     {"limit": 100000, "unit": "CFU/g",   "action": "Review storage temperatures"},
    "Molds and yeasts":       {"limit": 1000,   "unit": "CFU/g",   "action": "Review humidity, packaging and sanitation"},
}

@dataclass
class MicroResult:
    sample_id: str
    pathogen: str
    count: float
    unit: str
    compliant: bool
    risk_level: str        # "OK", "WARNING", "CRITICAL"
    action_required: Optional[str]


def parse_lab_csv(filepath: str) -> list[MicroResult]:
    """
    Reads a CSV with columns: sample_id, pathogen, count, unit
    Also accepts LIMS output (Biobank, LabWare, etc.)
    """
    df = pd.read_csv(filepath)

    # Normalize column names (different labs use different headers)
    col_map = {
        "sample": "sample_id", "id": "sample_id",
        "microorganism": "pathogen", "analyte": "pathogen", "organism": "pathogen",
        "result": "count", "count_cfu": "count",
        "units": "unit"
    }
    df.rename(columns={k: v for k, v in col_map.items() if k in df.columns}, inplace=True)

    results = []
    for _, row in df.iterrows():
        pathogen = str(row["pathogen"]).strip()
        count = float(row["count"])
        limit_info = LIMITS.get(pathogen, {
            "limit": None,
            "unit": row.get("unit", "CFU/g"),
            "action": None
        })

        if limit_info["limit"] is None:
            compliant, risk, action = True, "OK", None
        elif limit_info["limit"] == 0:
            compliant = (count == 0)
            risk = "CRITICAL" if count > 0 else "OK"
            action = limit_info["action"] if count > 0 else None
        else:
            compliant = (count <= limit_info["limit"])
            if not compliant:
                risk = "CRITICAL" if count > limit_info["limit"] * 10 else "WARNING"
                action = limit_info["action"]
            else:
                risk = "OK"
                action = None

        results.append(MicroResult(
            sample_id=str(row["sample_id"]),
            pathogen=pathogen,
            count=count,
            unit=limit_info["unit"],
            compliant=compliant,
            risk_level=risk,
            action_required=action
        ))

    return results