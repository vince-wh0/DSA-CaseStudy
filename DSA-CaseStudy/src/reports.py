import csv
import os
from typing import List, Dict, Any


def print_summary_report(summary_stats: Dict[str, Any]) -> None:
    print("\nCOURSE PERFORMANCE SUMMARY")
    if not summary_stats:
        print("No summary statistics available.")
        return
    for key, value in summary_stats.items():
        label = key.replace("_", " ").capitalize()
        print(f"{label}: {value}")

def export_section_reports(student_records: List[Dict[str, Any]], output_dir: str) -> None:
    if not student_records:
        print("No student data available to export.")
        return
    os.makedirs(output_dir, exist_ok=True)
    sections = {}
    for record in student_records:
        section = record.get("section", "Unknown") or "Unknown"
        sections.setdefault(section, []).append(record)
    for section, records in sections.items():
        filename = f"section_{section}.csv".replace(" ", "_")
        filepath = os.path.join(output_dir, filename)
        headers = list(records[0].keys())
        with open(filepath, mode="w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=headers)
            writer.writeheader()
            writer.writerows(records)
        print(f"Section report saved: {filepath}")

def export_at_risk_list(student_records: List[Dict[str, Any]], threshold: float, output_path: str) -> None:
    if not student_records:
        print("No student data available for at-risk report.")
        return
    at_risk = [
        r for r in student_records
        if isinstance(r.get("final_score"), (int, float)) and r["final_score"] < threshold
    ]
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, mode="w", newline="", encoding="utf-8") as f:
        if at_risk:
            writer = csv.DictWriter(f, fieldnames=at_risk[0].keys())
            writer.writeheader()
            writer.writerows(at_risk)
        else:
            f.write("No at-risk students found.\n")
    print(f"At-risk report generated: {output_path}")

def generate_full_report(
    student_records: List[Dict[str, Any]],
    summary_stats: Dict[str, Any],
    config: Dict[str, Any]
) -> None:
    print("\nGenerating Full Analytics Report")
    print_summary_report(summary_stats)
    output_dir = config["paths"]["output_dir"]
    export_section_reports(student_records, output_dir)
    threshold = config["thresholds"]["at_risk_grade"]
    at_risk_file = os.path.join(output_dir, "at_risk.csv")
    export_at_risk_list(student_records, threshold, at_risk_file)

    print("All reports generated successfully.\n")
