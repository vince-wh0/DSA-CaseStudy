import csv

def load_csv(filename):
    """Reads a CSV file and returns a cleaned list of student records."""
    records = []
    try:
        with open(filename, 'r', newline='', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row_num, row in enumerate(reader, start=2):  # start=2 (row 1 is header)
                clean_row = {}
                for key, value in row.items():
                    # Trim spaces if value is text
                    if isinstance(value, str):
                        key = key.strip() # Also strip keys
                        value = value.strip()

                    # Convert numeric fields (scores) to floats if valid
                    if key not in ['student_id', 'last_name', 'first_name', 'section']:
                        if value == '':
                            value = None
                        else:
                            try:
                                num = float(value)
                                value = num if 0 <= num <= 100 else None
                            except ValueError:
                                value = None
                    clean_row[key] = value

                # Warn if any important fields are missing
                if None in [clean_row.get('student_id'), clean_row.get('last_name')]:
                    print(f"Warning: Missing required data (ID/Name) in row {row_num}: {clean_row}")

                records.append(clean_row)
    except FileNotFoundError:
        print(f"Error: Input CSV file not found at {filename}")
        return []
        
    return records


def validate_data(records):
    """Removes duplicate or invalid student records."""
    valid = []
    seen_ids = set()
    for rec in records:
        sid = rec.get('student_id')
        if sid and sid not in seen_ids:
            valid.append(rec)
            seen_ids.add(sid)
        elif sid in seen_ids:
            print(f"Duplicate student ID skipped: {sid}")
        elif not sid:
            print(f"Record skipped, missing student ID: {rec.get('last_name')}")
    return valid


def read_csv_data(filename):
    """Main ingest function: load → clean → validate """
    data = load_csv(filename)
    if not data:
        return []
    clean_data = validate_data(data)
    print(f"\nSuccessfully loaded {len(clean_data)} valid records from {filename}\n")
    return clean_data


if __name__ == "__main__":
    # Test run
    records = read_csv_data('data/input.csv')
    for rec in records:
        print(rec)