import json
import os
from typing import Dict, Any, List

# Import our custom modules
import ingest
import transform
import analyze
import reports

# Type alias from ingest
Student = Dict[str, Any]

# --- Build absolute paths based on this script's location ---
# Get the directory where this script (main.py) is located
# e.g., /path/to/project/src
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
# Get the project's root directory (one level up from 'src')
# e.g., /path/to/project
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
# Build the full, absolute path to config.json
# e.g., /path/to/project/config.json
CONFIG_PATH = os.path.join(PROJECT_ROOT, 'config.json')

def load_configuration(config_path: str) -> Dict[str, Any]:
    
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
        print(f"Configuration loaded from {config_path}")
        return config
    except FileNotFoundError:
        print(f"Error: Configuration file not found at {config_path}")
        print("Please ensure 'config.json' is in the main project directory.")
        exit(1) # Exit script if config is missing
    except json.JSONDecodeError:
        print(f"Error: Configuration file {config_path} is not valid JSON.")
        exit(1)

def run_full_report(students_list: List[Student], config: Dict[str, Any], output_dir: str):
    """
    Runs the full analysis and reporting pipeline on the current student data.
    Args:
        students_list: The current list of student records (could be modified).
        config: The loaded configuration dictionary.
        output_dir: The full, absolute path to the reports directory.
    """
    print("\n--- Running Full Report ---")
    if not students_list:
        print("No student data to report on. Load data first.")
        return

    # Get settings from config
    weights = config.get('grade_weights', {})
    grading_scale = config.get('grading_scale', {})
    
    # Get the at-risk threshold from the config
    # Use .get() for nested dictionary safety
    thresholds_config = config.get('thresholds', {})
    at_risk_threshold = thresholds_config.get('at_risk_grade', 60.0)

    # Create reports directory if it doesn't exist
    # This now uses the absolute path, which is more reliable
    os.makedirs(output_dir, exist_ok=True)

    # 1. Transform Data (Re-calculates grades for all students)
    students_with_grades = transform.compute_weighted_grades(students_list, weights)
    all_student_data = transform.assign_letter_grades(students_with_grades, grading_scale)
    
    # 2. Analyze Data
    class_stats = analyze.get_class_statistics(all_student_data)
    at_risk_students = analyze.find_at_risk_students(all_student_data, at_risk_threshold)
    
    # 3. Generate Reports
    reports.print_summary_report(class_stats, len(at_risk_students), len(all_student_data))
    reports.export_at_risk_list(at_risk_students, output_dir)
    reports.export_section_reports(all_student_data, output_dir)
    print(f"--- Report Generation Complete (Check '{output_dir}') ---")

def view_all_students(students_list: List[Student]):
    """
    Prints a simple roster of all students currently in memory
    in their CURRENT order.
    """
    print("\n--- Current Student Roster ---")
    if not students_list:
        print("No students loaded.")
        return
    
    print(f"Displaying {len(students_list)} students (in current sort order):")
    for s in students_list:
        grade = s.get('final_grade', 'N/A')
        # Use .get() for names/section in case they are missing (robustness)
        last = s.get('last_name', 'N/A')
        first = s.get('first_name', 'N/A')
        section = s.get('section', 'N/A')
        sid = s.get('student_id', 'N/A')
        print(f"  ID: {sid:<6} | Name: {last}, {first:<15} | Section: {section:<3} | Grade: {grade}")

def add_student(students_list: List[Student]):
    """
    (INSERT operation)
    Prompts the user for student details and adds them to the in-memory list.
    """
    print("\n--- Add New Student (Insert) ---")
    
    # --- Validation: Check for duplicate ID ---
    while True:
        student_id = input("Enter Student ID: ").strip()
        if not student_id:
            print("Student ID cannot be empty.")
            continue
            
        # Check if ID already exists
        if any(s.get('student_id') == student_id for s in students_list):
            print(f"Error: Student ID {student_id} already exists. Please use a unique ID.")
        else:
            break
            
    last_name = input("Enter Last Name: ").strip()
    first_name = input("Enter First Name: ").strip()
    section = input("Enter Section: ").strip()
    
    # Create the new student dictionary
    # New students will have no grades by default (None)
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
    
    # --- The "Insert" Operation ---
    students_list.append(new_student)
    
    print(f"Success: Added {first_name} {last_name} (ID: {student_id}) to the roster.")
    print("Note: New student has no grades. Run report to see 'N/A' or 0.")

def delete_student(students_list: List[Student]):
    """
    (DELETE operation)
    Prompts for a student ID and removes the student from the in-memory list.
    """
    print("\n--- Delete Student ---")
    student_id = input("Enter Student ID to delete: ").strip()
    
    student_to_delete = None
    
    # --- The "Search" Operation ---
    for student in students_list:
        if student.get('student_id') == student_id:
            student_to_delete = student
            break
            
    if student_to_delete:
        # --- The "Delete" Operation ---
        students_list.remove(student_to_delete)
        print(f"Success: Removed {student_to_delete.get('first_name')} {student_to_delete.get('last_name')} (ID: {student_id}).")
    else:
        print(f"Error: Student ID {student_id} not found.")

# --- NEW FUNCTION ---
def sort_students_menu(students_list: List[Student], config: Dict[str, Any]):
    """
    (SORT operation)
    Displays a sub-menu to sort the in-memory student list.
    This modifies the list in-place.
    """
    print("\n--- Sort Students (In-Memory) ---")
    print(" (1) Sort by Last Name (A-Z)")
    print(" (2) Sort by Student ID (Ascending)")
    print(" (3) Sort by Final Grade (High-to-Low)")
    print(" (4) Back to Main Menu")
    
    choice = input("Enter your choice (1-4): ").strip()
    
    if choice == '1':
        # Sort by last name, then first name as a tie-breaker
        students_list.sort(key=lambda s: (s.get('last_name', '').lower(), s.get('first_name', '').lower()))
        print("Successfully sorted students by Last Name.")
        
    elif choice == '2':
        # Sort by student ID. Handle Nones/empty strings
        students_list.sort(key=lambda s: s.get('student_id', '0'))
        print("Successfully sorted students by Student ID.")
        
    elif choice == '3':
        # This requires grades to be calculated.
        # Check if 'final_grade' exists on the first student.
        if 'final_grade' not in students_list[0]:
            print("Calculating grades first...")
            weights = config.get('grade_weights', {})
            # This function modifies the list in-place, adding 'final_grade'
            transform.compute_weighted_grades(students_list, weights)
            
        # Sort by final grade. Use -1 for "None" grades to put them at the bottom.
        students_list.sort(key=lambda s: s.get('final_grade', -1) or -1, reverse=True)
        print("Successfully sorted students by Final Grade (High-to-Low).")
        
    elif choice == '4':
        return
        
    else:
        print("Invalid choice. Returning to Main Menu.")

def main_menu():
    """
    Runs the interactive command-line menu.
    """
    print("=== Welcome to Academic Analytics Lite ===")
    
    # 1. Load Configuration (using the new absolute path)
    config = load_configuration(CONFIG_PATH)
    
    # 2. Resolve all paths from config *once* using PROJECT_ROOT
    paths_config = config.get('paths', {})
    
    # Use config value, or 'data/input.csv' as default
    input_csv_name = paths_config.get('input_csv', 'data/input.csv')
    input_csv_path = os.path.join(PROJECT_ROOT, input_csv_name)
    
    # Use config value, or 'reports' as default
    output_dir_name = paths_config.get('output_dir', 'reports')
    output_dir = os.path.join(PROJECT_ROOT, output_dir_name)
    
    # 3. Ingest Data (using the new absolute path)
    students = ingest.read_csv_data(input_csv_path)
    
    if not students:
        print(f"No valid student data loaded from {input_csv_path}. Exiting.")
        return
        
    print(f"\nSuccessfully loaded {len(students)} students into memory.")
    
    # 4. Start the main menu loop
    while True:
        print("\n" + "---" * 10)
        print("Main Menu")
        print(" (1) Run Full Report (Process & Export all data)")
        print(" (2) View All Students (In-Memory Roster)")
        print(" (3) Add Student")
        print(" (4) Delete Student")
        print(" (5) Sort Students")
        print(" (6) Exit")
        print("---" * 10)
        
        choice = input("Enter your choice (1-6): ").strip()
        
        if choice == '1':
            # Pass the resolved output_dir to the report function
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
            print("\nExiting Academic Analytics Lite.")
            print("Note: Changes made (add/delete/sort) were in-memory and are not saved to the original CSV file.")
            break
            
        else:
            print("\nInvalid choice. Please enter a number from 1 to 6.")

if __name__ == "__main__":
    main_menu()