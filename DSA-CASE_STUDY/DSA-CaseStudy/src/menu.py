import os
from typing import Dict, Any, List

import transform
import analyze
import reports
import visualize 
import compare_section
import matplotlib
MATPLOTLIB_AVAILABLE = True
    
Student = Dict[str, Any]

def run_full_report(students_list: List[Student], config: Dict[str, Any], output_dir: str):
    # analysis, reporting, and plotting.
    print("\n--- Running Full Report ---")
    if not students_list:
        print("No student data to report on. Load data first.")
        return

    thresholds_config = config.get('thresholds', {})
    at_risk_threshold = thresholds_config.get('at_risk_grade', 60.0)

    os.makedirs(output_dir, exist_ok=True)

    # Transform data
    all_student_data = transform.transform_records(students_list, config)
    
    # Get main stats
    class_stats = analyze.get_class_statistics(all_student_data)
    
    # Get at-risk students
    at_risk_list = analyze.at_risk_students(all_student_data, at_risk_threshold)
    class_stats['total_students'] = len(all_student_data)
    class_stats['at_risk_students_count'] = len(at_risk_list)

    # Get section comparison stats
    section_comparison = compare_section.compare_section_performance(all_student_data)

    # Print text reports
    reports.print_summary_report(class_stats)
    compare_section.print_section_comparison(section_comparison)
    
    # Export CSV reports
    at_risk_path = os.path.join(output_dir, "at_risk_report.csv")
    reports.export_at_risk_list(at_risk_list, at_risk_path)
    reports.export_section_reports(all_student_data, output_dir)

    # Generate plots
    if MATPLOTLIB_AVAILABLE:
        visualize.plot_grade_distribution(all_student_data, output_dir)
        visualize.plot_section_comparison(section_comparison, output_dir) 
    else:
        print("\nPlot generation skipped: matplotlib, numpy, or scipy not installed.")
        
    print(f"--- Report Generation Complete ---")

def view_all_students(students_list: List[Student]):
    # Displays the current in-memory student roster.
    print("\n--- Current Student Roster ---")
    if not students_list:
        print("No students loaded.")
        return
    
    print(f"Displaying {len(students_list)} students (in current sort order):")
    for s in students_list:
        grade = s.get('letter_grade', 'N/A')
        final_score = s.get('final_score', 'N/A')
        last = s.get('last_name', 'N/A')
        first = s.get('first_name', 'N/A')
        section = s.get('section', 'N/A')
        sid = s.get('student_id', 'N/A')
        print(f"  ID: {sid:<6} | Name: {last}, {first:<20} | Section: {section:<7} | Grade: {grade} ({final_score})")


def add_student(students_list: List[Student]):
    # Prompts user to add a new student record to the in-memory list.
    print("\n--- Add New Student ---")
    
    while True:
        student_id = input("Enter Student ID: ").strip()
        if not student_id:
            print("Student ID cannot be empty.")
            continue
            
        if any(s.get('student_id') == student_id for s in students_list):
            print(f"Error: Student ID {student_id} already exists. Please use a unique ID.")
        else:
            break
            
    last_name = input("Enter Last Name: ").strip()
    first_name = input("Enter First Name: ").strip()
    section = input("Enter Section: ").strip()
    
    new_student: Student = {
        'student_id': student_id,
        'last_name': last_name,
        'first_name': first_name,
        'section': section,
        'quiz1': None, 'quiz2': None, 'quiz3': None, 'quiz4': None, 'quiz5': None,
        'midterm': None,
        'final': None,
        'attendance_percent': None
    }
    
    students_list.append(new_student)
    
    print(f"Success: Added {first_name} {last_name} (ID: {student_id}) to the roster.")
    print("Note: New student has no grades. Run report to see 'N/A'.")

def delete_student(students_list: List[Student]):
    # Prompts user to delete a student by ID from the in-memory list.
    
    print("\n--- Delete Student ---")
    student_id = input("Enter Student ID to delete: ").strip()
    
    student_to_delete = None
    
    for student in students_list:
        if student.get('student_id') == student_id:
            student_to_delete = student
            break
            
    if student_to_delete:
        students_list.remove(student_to_delete)
        print(f"Success: Removed {student_to_delete.get('first_name')} {student_to_delete.get('last_name')} (ID: {student_id}).")
    else:
        print(f"Error: Student ID {student_id} not found.")

def sort_students_menu(students_list: List[Student], config: Dict[str, Any]):
    # Shows sorting options and sorts the in-memory list.
    print("\n--- Sort Students (In-Memory) ---")
    print(" (1) Sort by Last Name (A-Z)")
    print(" (2) Sort by Student ID (Ascending)")
    print(" (3) Sort by Final Grade (High-to-Low)")
    print(" (4) Back to Main Menu")
    
    choice = input("Enter your choice (1-4): ").strip()
    
    if choice == '1':
        students_list.sort(key=lambda s: (s.get('last_name', '').lower(), s.get('first_name', '').lower()))
        print("Successfully sorted students by Last Name.")
        
    elif choice == '2':
        students_list.sort(key=lambda s: s.get('student_id', '0'))
        print("Successfully sorted students by Student ID.")
        
    elif choice == '3':
        if not students_list or 'final_score' not in students_list[0]:
            print("Calculating grades first...")
            transform.transform_records(students_list, config)
            
        students_list.sort(key=lambda s: s.get('final_score', -1) or -1, reverse=True)
        print("Successfully sorted students by Final Grade (High-to-Low).")
        
    elif choice == '4':
        return
        
    else:
        print("Invalid choice. Returning to Main Menu.")

def main_menu(students: List[Student], config: Dict[str, Any], output_dir: str):
    """Displays the main command-line menu and handles user input."""

    print(f"\nSuccessfully loaded {len(students)} students into memory.")
    
    while True:
        print("\n" + "---" * 15)
        print("Main Menu")
        print(" (1) Run Full Report (Process & Export all data)")
        print(" (2) View All Students (In-Memory Roster)")
        print(" (3) Add Student")
        print(" (4) Delete Student")
        print(" (5) Sort Students")
        print(" (6) Generate Grade Distribution Plot")
        print(" (7) Compare Section Performance")
        print(" (8) Exit")
        print("---" * 15)
        
        choice = input("Enter your choice (1-8): ").strip()
        
        if choice == '1':
            run_full_report(students, config, output_dir)
        
        elif choice == '2':
            view_all_students(students)
            
        elif choice == '3':
            add_student(students)
            
        elif choice == '4':
            delete_student(students)
        
        elif choice == '5':
            sort_students_menu(students, config)
            
        elif choice == '6':
            if not MATPLOTLIB_AVAILABLE:
                print("\nCannot generate plot: matplotlib, numpy, or scipy not installed.")
                print("Please run: pip install matplotlib numpy scipy")
            else:
                if not students or 'final_score' not in students[0]:
                    print("Calculating grades first...")
                    transform.transform_records(students, config)
                visualize.plot_grade_distribution(students, output_dir)
        
        elif choice == '7':
            if not students or 'final_score' not in students[0]:
                print("Calculating grades first...")
                transform.transform_records(students, config)
            
            comparison_data = compare_section.compare_section_performance(students)
            compare_section.print_section_comparison(comparison_data)
            
            if MATPLOTLIB_AVAILABLE:
                visualize.plot_section_comparison(comparison_data, output_dir)
            else:
                print("\nPlot generation skipped: matplotlib not installed.")
            
        elif choice == '8':
            print("\nExiting Academic Analytics Lite.")
            break
            
        else:
            print("\nInvalid choice. Please enter a number from 1 to 8.")