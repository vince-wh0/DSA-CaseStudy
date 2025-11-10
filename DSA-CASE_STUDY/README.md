# Academic Analytics Lite

### Course: Data Structures and Algorithms (Python)

---

## 1. Overview

**Academic Analytics Lite** is a lightweight, Python-based analytics tool designed to ingest, analyze, and report on student academic performance. It is built to be modular, configurable, and efficient, using standard Python data structures (lists and dictionaries) to process data from a CSV file.

The system loads student records from a CSV, processes them using weights from a JSON configuration file, and generates several analytical reports, including per-section CSVs and a list of at-risk students.

## 2. Core Features

- **Clean Ingest**: Reads raw `input.csv` data, cleans text fields, validates numeric scores, and skips duplicate or invalid records.
- **Data Transformation**: Calculates a weighted `final_score` and `letter_grade` for each student based on configurable weights.
- **Statistical Analysis**: Computes class-wide statistics (mean, min, max, percentiles) and identifies at-risk students.
- **Section Comparison**: Provides a detailed statistical breakdown (mean, median, mode, min, max) comparing performance between course sections.
- **Reporting**: Generates a comprehensive summary report to the console and exports detailed CSV files for each section and for the at-risk student list.
- **Configurable**: All key logic (file paths, grade weights, thresholds) is controlled via an external `config.json` file.
- **Interactive Menu**: A command-line menu (`menu.py`) allows for interactive use of the tool's features.
- **Tested**: Includes a full unit_tests.py suite to validate all core functions.

## 3. File Structure

    ``` bash
    DSA-CaseStudy/
    │
    ├── config.json                     # Main configuration file (paths, weights, grades)
    ├── README.md                       # This file
    │
    ├── data/
    │   └── input.csv                   # Raw student data
    │
    ├── reports/
    │   ├── at_risk_report.csv          # Generated report of at-risk students
    │   ├── section_BSIT_1A_report.csv  # Generated report for one section
    │   └── ...                         # Other generated section reports
    │
    ├── src/
    │   ├── ingest.py                   # Functions for loading and validating data
    │   ├── transform.py                # Functions for calculating grades
    │   ├── analyze.py                  # Functions for class-wide statistics
    │   ├── compare_section.py          # Functions for detailed section comparison
    │   ├── reports.py                  # Functions for printing and exporting reports
    │   ├── visualize.py                # Functions for plotting
    │   ├── menu.py                     # Interactive menu
    │   └── main.py                     # Main application entry point
    │
    └── tests/
        └── unit_tests.py               # Unit test suite for all modules
    ```

## 4. How to Run

### Prerequisites
- Python 3.7+
- matplotlib for visualization features in the menu.
``` bash
    pip install matplotlib
```

### 1. Run the Full Report
This is the main function of the project. It will run the entire pipeline from start to finish and generate all reports in the `reports/` directory.
``` bash
    # From the main DSA-CaseStudy/ directory:
    python src/main.py
```

### 2. Run the Unit Tests
To verify that all modules are working correctly, you can run the test suite from the main project directory.
``` bash
    # From the main DSA-CaseStudy/ directory:
    python tests/unit_tests.py
```

## 5. Configuration (`config.json`)
All application settings are controlled by config.json.
- **paths:**
    input_csv: The location of the raw data file, relative to the project root.
    output_dir: The folder where all generated CSV reports will be saved.

- **grade_weights:**
    Defines the weight of each component in the final grade. The program will automatically average all quizzes before applying the quiz weight.
    Note: The weights should ideally sum to 1.0 (or 100%).

- **thresholds:**
    at_risk_grade: The score (inclusive) below which a student is flagged as "at-risk".

- **grading_scale:**
    A dictionary mapping the letter grade to the minimum score required to achieve it. The system automatically sorts this to apply the highest grade possible.

## 6. Complexity Discussion
This analysis focuses on the efficiency of the core functions, where `N` is the total number of student records (rows) in the `input.csv` file.

### `O(N)` - Linear Time Operations
Most operations in this pipeline are highly efficient, operating in Linear Time. This means the time taken grows directly in proportion to the number of students. If you double the students, these operations take roughly double the time.

- `ingest.py` (Ingestion):
    - `load_csv`: Reads all `N` rows once. `O(N)`.
    - `validate_data`: Passes over all `N` records once. Using a *set* for `seen_ids` makes checking for duplicates an `O(1)` (average case) operation. Total: `O(N)`.

- `transform.py` (Transformation):
    - `transform_records`: This function loops through all `N` students once.
    - Inside the loop, `compute_final_score` and `get_letter_grade` are both `O(1)` because they operate on a fixed, small number of items (5 quizzes, 4 grade components, ~10 letter grades) that do not depend on `N`.
    - Total: `N * O(1) = O(N)`.

- `analyze.py` (Basic Stats):
    - `basic_stats`: Calculates *mean*, *min*, and *max* by iterating through `N` records once. `O(N)`.
    - `at_risk_students`: Filters the list by checking all `N` records once. `O(N)`.
    - `section_summary`: Groups `N` records into a dictionary, then loops through the (much smaller) number of sections. `O(N)`.

- `reports.py` (Reporting):
    - `export_section_reports`: Groups all `N` students by section, then writes each student's data to a file. Each record is processed a constant number of times. `O(N)`.
    - `export_at_risk_list`: Writes `R` records, where `R` is the number of at-risk students `(R <= N)`. `O(R)`, which is at most `O(N)`.

### `O(N log N)` - Log-Linear Time (The Bottleneck)
The primary performance bottleneck in the entire application comes from sorting. Any operation that requires sorting all `N` student scores will run in `O(N log N)` time, which is slightly slower than linear but still very efficient.

- `analyze.py` (Percentiles):
    - `compute_percentiles`: This function must first extract all `N` scores (`O(N)`) and then *sort* them (`O(N log N)`) to find the 25th, 50th (median), and 75th percentiles.
    - The sorting step is the dominant factor. Total: `O(N log N)`.

- `compare_section.py` (Section Median/Mode):
    - This function groups `N` students (`O(N)`) and then calculates statistics for each section.
    - Calculating the *median* for a section requires sorting the students within that section. In the worst case, if all students are in one section, this becomes `O(N log N)`.
    - Calculating the *mode* also typically involves sorting or a hash map, adding to this complexity.
