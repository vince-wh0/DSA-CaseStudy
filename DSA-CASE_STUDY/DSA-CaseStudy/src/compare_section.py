from typing import List, Dict, Any
from statistics import mean, median, mode, StatisticsError
import os

# --- Optional Imports ---
# Make matplotlib and numpy optional dependencies.
try:
    import matplotlib.pyplot as plt
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False

# Type alias for readability
Record = Dict[str, Any]

def compare_section_performance(rows: List[Record]) -> Dict[str, Dict[str, Any]]:
    """
    Generates a detailed statistical comparison between sections.
    Uses the 'final_score' already calculated by transform.py.
    """
    sections: Dict[str, List[float]] = {}
    
    # 1. Group final scores by section
    for r in rows:
        sec = str(r.get("section", "Unknown"))
        score = r.get("final_score")
        if isinstance(score, (int, float)):
            sections.setdefault(sec, []).append(score)

    comparison_results = {}
    
    # 2. Calculate detailed stats for each section
    for sec, scores in sections.items():
        if not scores:
            continue
            
        try:
            # Calculate mode, handle error if no unique mode
            mode_val = f"{mode(scores):.2f}"
        except StatisticsError:
            mode_val = "N/A (no unique mode)"
            
        comparison_results[sec] = {
            "count": len(scores),
            "average": f"{mean(scores):.2f}",
            "median": f"{median(scores):.2f}",
            "mode": mode_val,
            "highest": f"{max(scores):.2f}",
            "lowest": f"{min(scores):.2f}",
        }
        
    return comparison_results

def print_section_comparison(comparison_stats: Dict[str, Dict[str, Any]]) -> None:
    """Prints the detailed section-by-section comparison."""
    print("\n--- SECTION PERFORMANCE COMPARISON ---")
    if not comparison_stats:
        print("No section comparison data available.")
        return
        
    for section, stats in comparison_stats.items():
        print(f"\nSection: {section}")
        print(f"  Students: {stats['count']}")
        print(f"  Average:  {stats['average']}")
        print(f"  Median:   {stats['median']}")
        print(f"  Mode:     {stats['mode']}")
        print(f"  Highest:  {stats['highest']}")
        print(f"  Lowest:   {stats['lowest']}")
        
    print("\n----------------------------------------")

# --- NEW FUNCTION ---
def plot_section_comparison(comparison_stats: Dict[str, Dict[str, Any]], output_dir: str):
    """
    Generates and saves a bar chart comparing average scores by section.
    """
    
    # Check if the required libraries were imported successfully
    if not MATPLOTLIB_AVAILABLE:
        print("\n--- Plot Generation Skipped ---")
        print("Required library (matplotlib) not found.")
        print("Please install it to enable plotting: pip install matplotlib")
        return

    print("\n--- Generating Section Comparison Plot ---")

    if not comparison_stats:
        print("No comparison stats available. Cannot generate plot.")
        return

    # 1. Extract data for plotting
    try:
        sections = list(comparison_stats.keys())
        # Sort sections alphabetically for consistent plot order
        sections.sort() 
        
        # Get averages, converting them back to floats for plotting
        averages = [float(comparison_stats[sec]['average']) for sec in sections]
    except Exception as e:
        print(f"Error processing stats for plotting: {e}")
        return

    # 2. Set up the plot
    plt.figure(figsize=(10, 6))
    
    # 3. Create the bar chart
    colors = plt.cm.get_cmap('Pastel1', len(sections))
    bars = plt.bar(sections, averages, color=colors.colors)

    # 4. Add titles and labels
    plt.title('Average Final Score by Section', fontsize=16)
    plt.xlabel('Section', fontsize=12)
    plt.ylabel('Average Final Score', fontsize=12)
    plt.ylim(0, 100) # Grades are 0-100
    plt.grid(axis='y', linestyle='--', alpha=0.7)

    # Add data labels on top of each bar
    for bar in bars:
        yval = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2.0, yval + 1.0, f'{yval:.2f}', ha='center', va='bottom')

    # 5. Save the plot
    os.makedirs(output_dir, exist_ok=True)
    plot_path = os.path.join(output_dir, "section_comparison_barchart.png")
    
    try:
        plt.savefig(plot_path)
        plt.close() # Close the plot to free memory
        print(f"Successfully saved section comparison plot to: {plot_path}")
    except Exception as e:
        print(f"Error saving plot: {e}")