from typing import List, Dict, Optional
from statistics import mean
import math

# Type alias for readability
Record = Dict[str, Optional[float]]


# BASIC STATISTICS

def basic_stats(rows: List[Record], key: str) -> Dict[str, float]:
    """
    Compute simple descriptive statistics (mean, min, max)
    for a given numeric field across all records.
    """
    values = [r[key] for r in rows if isinstance(r.get(key), (int, float))]
    if not values:
        return {"mean": 0.0, "min": 0.0, "max": 0.0}

    return {
        "mean": round(mean(values), 2),
        "min": round(min(values), 2),
        "max": round(max(values), 2)
    }

# PERCENTILE CALCULATIONS

def _percentile(sorted_values: List[float], p: float) -> float:
    
    if not sorted_values:
        return 0.0
    k = (len(sorted_values) - 1) * (p / 100.0)
    f = math.floor(k)
    c = math.ceil(k)
    if f == c:
        return round(sorted_values[int(k)], 2)
    d0 = sorted_values[f] * (c - k)
    d1 = sorted_values[c] * (k - f)
    return round(d0 + d1, 2)


def compute_percentiles(rows: List[Record], key: str) -> Dict[str, float]:
    
    vals = sorted([r[key] for r in rows if isinstance(r.get(key), (int, float))])
    if not vals:
        return {"25th": 0, "50th": 0, "75th": 0, "90th": 0}

    return {
        "25th": _percentile(vals, 25),
        "50th": _percentile(vals, 50),
        "75th": _percentile(vals, 75),
        "90th": _percentile(vals, 90)
    }

# OUTLIER DETECTION (IQR METHOD)

def detect_outliers(rows: List[Record], key: str) -> List[Record]:
    
    vals = sorted([r[key] for r in rows if isinstance(r.get(key), (int, float))])
    if len(vals) < 4:
        return []

    q1 = _percentile(vals, 25)
    q3 = _percentile(vals, 75)
    iqr = q3 - q1
    lower_bound = q1 - 1.5 * iqr
    upper_bound = q3 + 1.5 * iqr

    return [
        r for r in rows
        if isinstance(r.get(key), (int, float))
        and (r[key] < lower_bound or r[key] > upper_bound)
    ]

# AT-RISK STUDENTS

def at_risk_students(rows: List[Record], threshold: float) -> List[Record]:
    
    return [r for r in rows if (r.get("final_score") or 0) < threshold]

# SECTION-BASED SUMMARY

def section_summary(rows: List[Record]) -> Dict[str, Dict[str, float]]:
    
    sections: Dict[str, List[float]] = {}

    for r in rows:
        sec = r.get("section", "Unknown")
        score = r.get("final_score")
        if isinstance(score, (int, float)):
            sections.setdefault(sec, []).append(score)

    summary = {}
    for sec, scores in sections.items():
        summary[sec] = {"mean": round(mean(scores), 2)} if scores else {"mean": 0.0}

    return summary