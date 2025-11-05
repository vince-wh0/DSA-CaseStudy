# src/transform.py

SCORE_KEY_MAP = {
    "quiz": "quiz_score",
    "midterm": "midterm_score",
    "final": "final_exam",
    "attendance": "attendance_score"
}


def get_letter_grade(score, grading_scale):
    """Assigns a letter grade using the configuration's grading scale."""
    if score is None:
     return 'N/A'


sorted_scale = sorted(grading_scale.items(), key=lambda item: item[1], reverse=True)

    for grade, threshold in sorted_scale:
    if score >= threshold:
    return grade

return 'F'


def compute_final_score(record, grade_weights):
    """Calculates the weighted final score based on config weights and key mapping."""
    final_score = 0

    for config_key, weight in grade_weights.items():
     # Get the actual column name from the record
        record_key = SCORE_KEY_MAP.get(config_key)
        
        if record_key is None:
         continue

    score = record.get(record_key)

    if score is None:
    return None

    final_score += score * weight

    return round(final_score, 2)


def set_risk_status(record, at_risk_threshold):
    """Adds a boolean flag ('is_at_risk') based on the final_score and threshold."""
     final_score = record.get('final_score')
    
    if final_score is not None and final_score < at_risk_threshold:
        record['is_at_risk'] = True
    else:
        record['is_at_risk'] = False
    

def transform_records(records, config):
    """Main transformation function: computes final score, letter grade, and risk status."""
    print("--- Starting Data Transformation (Calculating Scores and Grades) ---")

   
    grade_weights = config.get('grade_weights', {})
    grading_scale = config.get('grading_scale', {})
    at_risk_threshold = config.get('thresholds', {}).get('at_risk_grade', 60.0)

    
    for record in records:
 
    final_score = compute_final_score(record, grade_weights)
    record['final_score'] = final_score

    letter_grade = get_letter_grade(final_score, grading_scale)
    record['letter_grade'] = letter_grade
    
    set_risk_status(record, at_risk_threshold)
    
     print(f"Successfully transformed {len(records)} records. Added 'final_score', 'letter_grade', and 'is_at_risk'.")
     return records