from statistics import mean
from typing import List, Dict, Any

def get_letter_grade(score, grading_scale):
    """Assigns a letter grade using the configuration's grading scale."""
    if score is None:
        return 'N/A'

    # Sort scale from highest to lowest score
    sorted_scale = sorted(grading_scale.items(), key=lambda item: item[1], reverse=True)

    for grade, threshold in sorted_scale:
        if score >= threshold:
            return grade

    return 'F'  

def compute_final_score(record: Dict[str, Any], grade_weights: Dict[str, float]) -> float | None:
    #Calculates the weighted final score based on config weights.
    final_score = 0.0
    
    # 1. Calculate average quiz score
    quiz_scores = []
    for i in range(1, 6): # quiz1 to quiz5
        q_score = record.get(f'quiz{i}')
        if isinstance(q_score, (int, float)):
            quiz_scores.append(q_score)
    
    # Use mean if quizzes exist, otherwise 0
    quiz_avg = mean(quiz_scores) if quiz_scores else 0.0

    # 2. Get scores from record, mapping config keys to CSV columns
    component_scores = {
        'quiz': quiz_avg,
        'midterm': record.get('midterm'),
        'final': record.get('final'),
        'attendance': record.get('attendance_percent')
    }

    # 3. Calculate weighted score
    try:
        for config_key, weight in grade_weights.items():
            score = component_scores.get(config_key)
            
            # If any grade component is missing, the final score is None (N/A)
            if score is None:
                return None
            
            final_score += score * weight
            
    except TypeError:
        # This catches if a score was None and tried to multiply with weight
        return None

    return round(final_score, 2)


def set_risk_status(record, at_risk_threshold):
    """Adds a boolean flag ('is_at_risk') based on the final_score and threshold."""
    final_score = record.get('final_score')
    
    if final_score is not None and final_score < at_risk_threshold:
        record['is_at_risk'] = True
    else:
        record['is_at_risk'] = False
    

def transform_records(records: List[Dict[str, Any]], config: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Main transformation function: computes final score, letter grade, and risk status."""
    print("--- Starting Data Transformation (Calculating Scores and Grades) ---")
   
    grade_weights = config.get('grade_weights', {})
    grading_scale = config.get('grading_scale', {})
    at_risk_threshold = config.get('thresholds', {}).get('at_risk_grade', 65.0)
    
    transformed_count = 0
    for record in records:
 
        final_score = compute_final_score(record, grade_weights)
        record['final_score'] = final_score

        letter_grade = get_letter_grade(final_score, grading_scale)
        record['letter_grade'] = letter_grade
        
        set_risk_status(record, at_risk_threshold)
        transformed_count += 1
    
    print(f"Successfully transformed {transformed_count} records. Added 'final_score', 'letter_grade', and 'is_at_risk'.")
    return records