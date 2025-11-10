import unittest
import os
import shutil
import tempfile
import csv
import io
import sys
from typing import List, Dict, Any

# Add project 'src' directory to Python path
# This finds the 'tests' directory path
current_script_dir = os.path.dirname(os.path.abspath(__file__))
# This goes one level up to the project root (DSA-CaseStudy)
project_root = os.path.dirname(current_script_dir)
# This builds the path to the 'src' directory
src_dir = os.path.join(project_root, 'src')

# This tells Python to look for modules in the 'src' directory first
sys.path.insert(0, src_dir)
# End of path modification


# Import the modules we are testing
# Assumes that these files (ingest.py, transform.py, etc.)
# are in the same directory or on the Python path.
try:
    import ingest
    import transform
    import analyze
    import reports
    import compare_section
except ImportError as e:
    print(f"Error: Could not import project modules. Make sure .py files are accessible.")
    print(f"Details: {e}")

# Mock Data for Testing

# A mock config, similar to config.json
MOCK_CONFIG = {
  "paths": {
    "input_csv": "fake_data/input.csv",
    "output_dir": "fake_reports"
  },
  "grade_weights": {
    "quiz": 0.25,
    "midterm": 0.30,
    "final": 0.30,
    "attendance": 0.15
  },
  "thresholds": {
    "at_risk_grade": 65.0
  },
  "grading_scale": {
    "A": 93.0,
    "A-": 90.0,
    "B+": 87.0,
    "B": 83.0,
    "B-": 80.0,
    "C+": 77.0,
    "C": 73.0,
    "C-": 70.0,
    "D+": 67.0,
    "D": 60.0,
    "F": 0.0
  }
}

# A small, controlled set of student records *after* transformation.
# Used to test analyze.py, compare_section.py, and reports.py
MOCK_TRANSFORMED_RECORDS = [
    {
        'student_id': '101', 'last_name': 'Reyes', 'first_name': 'Mika', 'section': 'BSIT-1A',
        'final_score': 95.5, 'letter_grade': 'A', 'is_at_risk': False
    },
    {
        'student_id': '102', 'last_name': 'Santos', 'first_name': 'Lara', 'section': 'BSIT-1B',
        'final_score': 88.0, 'letter_grade': 'B+', 'is_at_risk': False
    },
    {
        'student_id': '103', 'last_name': 'Lim', 'first_name': 'Ken', 'section': 'BSIT-1C',
        'final_score': 62.0, 'letter_grade': 'D', 'is_at_risk': True
    },
    {
        'student_id': '104', 'last_name': 'Tan', 'first_name': 'Ana', 'section': 'BSIT-1A',
        'final_score': 85.0, 'letter_grade': 'B', 'is_at_risk': False
    },
    {
        'student_id': '105', 'last_name': 'Lee', 'first_name': 'Jin', 'section': 'BSIT-1C',
        'final_score': 91.0, 'letter_grade': 'A-', 'is_at_risk': False
    }
]


class TestIngest(unittest.TestCase):
    """Tests functions from ingest.py"""

    def setUp(self):
        """Create a temporary CSV file for testing."""
        # Used tempfile to create files that are automatically handled.
        self.temp_dir = tempfile.mkdtemp()
        self.csv_path = os.path.join(self.temp_dir, "test_input.csv")

    def tearDown(self):
        """Remove the temporary directory and all its files."""
        shutil.rmtree(self.temp_dir)

    def write_mock_csv(self, content: str):
        """Helper to write string content to our temp CSV file."""
        with open(self.csv_path, 'w', newline='') as f:
            f.write(content)

    def test_load_csv_normal(self):
        """Test loading a perfect CSV row."""
        csv_content = (
            "student_id,last_name,first_name,section,quiz1,midterm,final,attendance_percent\n"
            "101,Reyes,Mika,BSIT-1A,85,87,90,95\n"
        )
        self.write_mock_csv(csv_content)
        records = ingest.load_csv(self.csv_path)
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0]['student_id'], '101')
        self.assertEqual(records[0]['last_name'], 'Reyes')
        self.assertEqual(records[0]['midterm'], 87.0)
        self.assertEqual(records[0]['attendance_percent'], 95.0)

    def test_load_csv_cleaning(self):
        """Test if spaces are stripped and empty/bad values become None."""
        csv_content = (
            "student_id, last_name , first_name, section, quiz1, quiz2, quiz3\n"
            "102, Tan , Ana, BSIT-1B , 80, , 101\n"
        )
        self.write_mock_csv(csv_content)
        records = ingest.load_csv(self.csv_path)
        self.assertEqual(len(records), 1)
        record = records[0]
        # Test keys are stripped
        self.assertIn('last_name', record)
        # Test values are stripped
        self.assertEqual(record['last_name'], 'Tan')
        self.assertEqual(record['section'], 'BSIT-1B')
        # Test empty string becomes None
        self.assertIsNone(record['quiz2'])
        # Test invalid number (out of 0-100 range) becomes None
        self.assertIsNone(record['quiz3'])
        self.assertEqual(record['quiz1'], 80.0)

    def test_validate_data_duplicates(self):
        """Test that validate_data removes duplicate student IDs."""
        mock_records = [
            {'student_id': '101', 'last_name': 'Reyes'},
            {'student_id': '102', 'last_name': 'Santos'},
            {'student_id': '101', 'last_name': 'Reyes_Duplicate'},
            {'student_id': None, 'last_name': 'NoID'},
        ]
        valid_records = ingest.validate_data(mock_records)
        self.assertEqual(len(valid_records), 2)
        # Check that the first '101' record was kept
        self.assertEqual(valid_records[0]['last_name'], 'Reyes')
        self.assertEqual(valid_records[1]['last_name'], 'Santos')


class TestTransform(unittest.TestCase):
    """Tests functions from transform.py"""

    def setUp(self):
        self.weights = MOCK_CONFIG['grade_weights']
        self.scale = MOCK_CONFIG['grading_scale']

    def test_compute_final_score_perfect(self):
        """Test score calculation with all values present."""
        record = {
            'quiz1': 80, 'quiz2': 90, 'quiz3': 100, 'quiz4': 70, 'quiz5': 80, # Avg: 84
            'midterm': 85,
            'final': 90,
            'attendance_percent': 100
        }
        # Score = (84 * 0.25) + (85 * 0.30) + (90 * 0.30) + (100 * 0.15)
        # Score = 21 + 25.5 + 27 + 15 = 88.5
        score = transform.compute_final_score(record, self.weights)
        self.assertAlmostEqual(score, 88.5)

    def test_compute_final_score_missing_data(self):
        """Test score calculation with missing (None) values."""
        record = {
            'quiz1': 80, 'quiz2': None, 'quiz3': 100, 'quiz4': None, 'quiz5': 90, # Avg: 90
            'midterm': None, # This should cause the whole score to be None
            'final': 90,
            'attendance_percent': 100
        }
        score = transform.compute_final_score(record, self.weights)
        self.assertIsNone(score)

    def test_compute_final_score_missing_quizzes(self):
        """Test score calculation with only some quizzes present."""
        record = {
            'quiz1': 80, 'quiz2': 100, # Avg: 90
            'midterm': 80,
            'final': 80,
            'attendance_percent': 100
        }
        # Score = (90 * 0.25) + (80 * 0.30) + (80 * 0.30) + (100 * 0.15)
        # Score = 22.5 + 24 + 24 + 15 = 85.5
        score = transform.compute_final_score(record, self.weights)
        self.assertAlmostEqual(score, 85.5)

    def test_get_letter_grade_boundaries(self):
        """Test letter grade logic at the boundaries."""
        self.assertEqual(transform.get_letter_grade(100, self.scale), 'A')
        self.assertEqual(transform.get_letter_grade(93.0, self.scale), 'A')
        self.assertEqual(transform.get_letter_grade(92.9, self.scale), 'A-')
        self.assertEqual(transform.get_letter_grade(80.0, self.scale), 'B-')
        self.assertEqual(transform.get_letter_grade(79.9, self.scale), 'C+')
        self.assertEqual(transform.get_letter_grade(59.9, self.scale), 'F')
        self.assertEqual(transform.get_letter_grade(0, self.scale), 'F')
        self.assertEqual(transform.get_letter_grade(None, self.scale), 'N/A')

    def test_set_risk_status(self):
        """Test the at-risk flag logic."""
        threshold = MOCK_CONFIG['thresholds']['at_risk_grade'] # 65.0
        
        rec_safe = {'final_score': 70.0}
        transform.set_risk_status(rec_safe, threshold)
        self.assertFalse(rec_safe['is_at_risk'])

        rec_at_threshold = {'final_score': 65.0}
        transform.set_risk_status(rec_at_threshold, threshold)
        self.assertFalse(rec_at_threshold['is_at_risk']) # At 65.0, not *below*

        rec_at_risk = {'final_score': 64.9}
        transform.set_risk_status(rec_at_risk, threshold)
        self.assertTrue(rec_at_risk['is_at_risk'])
        
        rec_none = {'final_score': None}
        transform.set_risk_status(rec_none, threshold)
        self.assertFalse(rec_none['is_at_risk'])


class TestAnalyze(unittest.TestCase):
    """Tests functions from analyze.py"""

    def setUp(self):
        self.rows = MOCK_TRANSFORMED_RECORDS
        self.threshold = MOCK_CONFIG['thresholds']['at_risk_grade'] # 65.0

    def test_basic_stats(self):
        """Test mean, min, max calculation."""
        # Scores: [95.5, 88.0, 62.0, 85.0, 91.0]
        stats = analyze.basic_stats(self.rows, 'final_score')
        self.assertEqual(stats['min'], 62.0)
        self.assertEqual(stats['max'], 95.5)
        # Mean = (95.5 + 88.0 + 62.0 + 85.0 + 91.0) / 5 = 421.5 / 5 = 84.3
        self.assertAlmostEqual(stats['mean'], 84.3)

    def test_compute_percentiles(self):
        """Test 25th, 50th, 75th percentiles."""
        # Sorted scores: [62.0, 85.0, 88.0, 91.0, 95.5]
        # index-based method:
        # 25th: k = (5-1) * 0.25 = 1 -> index 1 -> 85.0
        # 50th: k = (5-1) * 0.50 = 2 -> index 2 -> 88.0
        # 75th: k = (5-1) * 0.75 = 3 -> index 3 -> 91.0
        percentiles = analyze.compute_percentiles(self.rows, 'final_score')
        self.assertAlmostEqual(percentiles['50th'], 88.0) 
        self.assertAlmostEqual(percentiles['25th'], 85.0)
        self.assertAlmostEqual(percentiles['75th'], 91.0)

    def test_at_risk_students(self):
        """Test filtering for at-risk students."""
        at_risk = analyze.at_risk_students(self.rows, self.threshold)
        self.assertEqual(len(at_risk), 1)
        self.assertEqual(at_risk[0]['student_id'], '103')

    def test_section_summary(self):
        """Test calculation of per-section averages."""
        # BSIT-1A: [95.5, 85.0] -> Avg: 90.25
        # BSIT-1B: [88.0] -> Avg: 88.0
        # BSIT-1C: [62.0, 91.0] -> Avg: 76.5
        summary = analyze.section_summary(self.rows)
        self.assertIn('BSIT-1A', summary)
        self.assertAlmostEqual(summary['BSIT-1A']['mean'], 90.25)
        self.assertIn('BSIT-1B', summary)
        self.assertAlmostEqual(summary['BSIT-1B']['mean'], 88.0)
        self.assertIn('BSIT-1C', summary)
        self.assertAlmostEqual(summary['BSIT-1C']['mean'], 76.5)


class TestCompareSection(unittest.TestCase):
    """Tests functions from compare_section.py"""

    def setUp(self):
        self.rows = MOCK_TRANSFORMED_RECORDS

    def test_compare_section_performance(self):
        """Test the detailed section comparison logic."""
        stats = compare_section.compare_section_performance(self.rows)
        
        # BSIT-1A: [95.5, 85.0]
        self.assertIn('BSIT-1A', stats)
        sec_1a = stats['BSIT-1A']
        
        self.assertEqual(sec_1a['count'], 2)
        # Cast string results back to float for comparison
        self.assertAlmostEqual(float(sec_1a['average']), 90.25)
        self.assertAlmostEqual(float(sec_1a['median']), 90.25)

        self.assertEqual(float(sec_1a['lowest']), 85.0)     
        self.assertEqual(float(sec_1a['highest']), 95.5)    

        self.assertEqual(sec_1a['mode'], '95.50')

        # BSIT-1C: [62.0, 91.0]
        self.assertIn('BSIT-1C', stats)
        sec_1c = stats['BSIT-1C']
        self.assertEqual(sec_1c['count'], 2)
        self.assertAlmostEqual(float(sec_1c['average']), 76.5)
        self.assertAlmostEqual(float(sec_1c['median']), 76.5)

        self.assertEqual(float(sec_1c['lowest']), 62.0)     
        self.assertEqual(float(sec_1c['highest']), 91.0)    

        # BSIT-1B: [88.0]
        self.assertIn('BSIT-1B', stats)
        sec_1b = stats['BSIT-1B']
        self.assertEqual(sec_1b['count'], 1)
        self.assertAlmostEqual(float(sec_1b['average']), 88.0)
        self.assertEqual(sec_1b['mode'], '88.00') # Mode exists with 1 item


class TestReports(unittest.TestCase):
    """Tests functions from reports.py"""

    def setUp(self):
        """Set up the output directory in project_root/reports."""
        # project_root is defined globally at the top
        self.output_dir = os.path.join(project_root, 'reports')
        os.makedirs(self.output_dir, exist_ok=True)
        
        self.at_risk_list = analyze.at_risk_students(
            MOCK_TRANSFORMED_RECORDS, 
            MOCK_CONFIG['thresholds']['at_risk_grade']
        )
        
        # Define paths for test files to be created
        self.at_risk_path = os.path.join(self.output_dir, "at_risk_report.csv")
        self.section_path_1a = os.path.join(self.output_dir, "section_BSIT_1A_report.csv")
        self.section_path_1b = os.path.join(self.output_dir, "section_BSIT_1B_report.csv")
        self.section_path_1c = os.path.join(self.output_dir, "section_BSIT_1C_report.csv")
        self.section_comparison_barchart = os.path.join(self.output_dir, "section_comparison_barchart.png")
        
        # A list of all files this test might create
        self.generated_files = [
            self.at_risk_path, 
            self.section_path_1a, 
            self.section_path_1b, 
            self.section_path_1c,
            self.section_comparison_barchart
        ]
        
        # Clean up any old files before running tests
        self.cleanup_files()

    def tearDown(self):
        """Remove the temporary files created by the tests."""
        self.cleanup_files()
        
    def cleanup_files(self):
        """Helper to delete generated files."""
        for f in self.generated_files:
            if os.path.exists(f):
                os.remove(f)

    def test_print_summary_report(self):
        """Test if the summary report prints to stdout."""
        # We capture stdout by replacing it with a string buffer
        captured_output = io.StringIO()
        
        # A mock summary to print
        summary_data = {
            'class_average': 84.3,
            'total_students': 5,
            'at_risk_count': 1
        }
        
        try:
            import sys
            old_stdout = sys.stdout
            sys.stdout = captured_output
            
            reports.print_summary_report(summary_data)
            
            sys.stdout = old_stdout # Restore stdout
        finally:
             if 'sys' in locals():
                sys.stdout = old_stdout # Ensure stdout is restored even on error

        output = captured_output.getvalue()
        self.assertIn("--- COURSE PERFORMANCE SUMMARY", output)
        self.assertIn("Class average: 84.3", output)
        self.assertIn("Total students: 5", output)
        self.assertIn("At risk count: 1", output)

    def test_export_at_risk_list(self):
        """Test that the at-risk CSV is created with correct content."""
        # Use the path defined in setUp
        reports.export_at_risk_list(self.at_risk_list, self.at_risk_path)
        
        # Check file was created
        self.assertTrue(os.path.exists(self.at_risk_path))
        
        # Check content
        with open(self.at_risk_path, 'r') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            self.assertEqual(len(rows), 1)
            self.assertEqual(rows[0]['student_id'], '103')
            self.assertEqual(rows[0]['last_name'], 'Lim')
            self.assertEqual(rows[0]['final_score'], '62.0')

    def test_export_section_reports(self):
        """Test that per-section CSVs are created."""
        reports.export_section_reports(MOCK_TRANSFORMED_RECORDS, self.output_dir)
        
        # Check for expected files (paths defined in setUp)
        self.assertTrue(os.path.exists(self.section_path_1a))
        self.assertTrue(os.path.exists(self.section_path_1b))
        self.assertTrue(os.path.exists(self.section_path_1c))
        
        # Spot check content of BSIT-1A
        with open(self.section_path_1a, 'r') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            self.assertEqual(len(rows), 2)
            student_ids = {rows[0]['student_id'], rows[1]['student_id']}
            self.assertEqual(student_ids, {'101', '104'})


if __name__ == '__main__':
    """
    To run the test. Use the command:
    python -m unittest tests.unit_tests
    """
    unittest.main()