import csv
import os
from typing import List, Dict, Any

def print_summary_report(summary_stats: Dict[str, Any]) -> None:
    # Prints the formatted summary report to the console.
    print("\n--- COURSE PERFORMANCE SUMMARY ---")
    if not summary_stats:
        print("No summary statistics available.")
        return
    
    # Iterate and print key-value pairs
    for key, value in summary_stats.items():
        label = key.replace("_", " ").capitalize()
        
        # Special formatting for nested dictionary (section averages)
        if key == 'section_averages':
            print(f"{label}:")
            if isinstance(value, dict):
                for section, stats in value.items():
                    print(f"  - {section}: {stats.get('mean', 'N/A')}")
        else:
            print(f"{label}: {value}")
    print("---------------------------------------------------------")

def export_section_reports(student_records: List[Dict[str, Any]], output_dir: str) -> None:
    # Exports a separate CSV for each section.
    if not student_records:
        print("No student data available to export.")
        return
    
    os.makedirs(output_dir, exist_ok=True)
    sections = {}
    
    # Use first record to get all possible headers, in order
    if not student_records:
        return
    headers = list(student_records[0].keys())
    
    for record in student_records:
        section = str(record.get("section", "Unknown")) or "Unknown"
        sections.setdefault(section, []).append(record)
        
    for section, records in sections.items():
        # Sanitize section name for filename
        safe_section_name = section.replace(" ", "_").replace("-", "_")
        filename = f"section_{safe_section_name}_report.csv"
        filepath = os.path.join(output_dir, filename)
        
        with open(filepath, mode="w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=headers)
            writer.writeheader()
            writer.writerows(records)
        print(f"Section report saved: {filepath}")

def export_at_risk_list(at_risk_students: List[Dict[str, Any]], output_path: str) -> None:
    if not at_risk_students:
        print("No at-risk students found.")
        # Create empty file to confirm report ran
        with open(output_path, mode="w", newline="", encoding="utf-8") as f:
            f.write("No at-risk students found.\n")
        print(f"At-risk report generated (empty): {output_path}")
        return
        
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # Get headers from the first at-risk student
    headers = list(at_risk_students[0].keys())
    
    with open(output_path, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        writer.writerows(at_risk_students)
    print(f"At-risk report generated: {output_path}")

