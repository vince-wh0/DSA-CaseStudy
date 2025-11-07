import os
from typing import List, Dict, Any

try:
    import matplotlib.pyplot as plt
    import numpy as np
    from scipy.stats import norm
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False

Record = Dict[str, Any]

def plot_grade_distribution(rows: List[Record], output_dir: str):
    # Generates and saves a histogram and density curve of final scores.
    # Check if the required libraries were imported successfully
    if not MATPLOTLIB_AVAILABLE:
        print("Required libraries (matplotlib, numpy, scipy) not found.")
        return

    print("\n--- Generating Grade Distribution Plot ---")
    
    # Get all valid final scores
    scores = [r['final_score'] for r in rows if isinstance(r.get('final_score'), (int, float))]
    
    if not scores:
        print("No valid scores available. Cannot generate plot.")
        return
        
    # Convert to numpy array for easier calculations
    scores_arr = np.array(scores)

    #  Calculate mean
    mean_score = np.mean(scores_arr)

    # Set up the plot
    plt.figure(figsize=(10, 6))
    
    # Plot the histogram
    plt.hist(scores, bins='auto', density=True, alpha=0.6, color='skyblue', edgecolor='red', label='Grade Histogram')
    
    # Plot the density curve
    try:
        mu, std = norm.fit(scores)
        xmin, xmax = plt.xlim()
        x = np.linspace(min(scores), max(scores), 100)
        p = norm.pdf(x, mu, std)
        plt.plot(x, p, 'k', linewidth=2, label='Normal Distribution Fit (Curve)')
    except Exception as e:
        print(f"Warning: Could not fit normal distribution curve. {e}")

    # Add vertical lines for mean
    plt.axvline(mean_score, color='r', linestyle='dashed', linewidth=2, label=f'Mean: {mean_score:.2f}')

    # Add titles and labels
    title = f"Grade Distribution (n={len(scores)}) - $\mu={mu:.2f}$, $\sigma={std:.2f}$"
    plt.title(title, fontsize=16)
    plt.xlabel('Final Score', fontsize=12)
    plt.ylabel('Density', fontsize=12)
    plt.legend()
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    
    # Save the plot
    os.makedirs(output_dir, exist_ok=True)
    plot_path = os.path.join(output_dir, "grade_distribution_curve.png")
    
    try:
        plt.savefig(plot_path)
        plt.close() 
        print(f"Successfully saved grade distribution plot to: {plot_path}")
    except Exception as e:
        print(f"Error saving plot: {e}")

def plot_section_comparison(comparison_stats: Dict[str, Dict[str, Any]], output_dir: str):
    # Generates and saves a bar chart comparing average scores by section.
    print("\n--- Generating Section Comparison Plot ---")

    if not comparison_stats:
        print("No comparison stats available. Cannot generate plot.")
        return

    # Extract data for plotting
    try:
        sections = list(comparison_stats.keys())
        # Sort sections alphabetically for consistent plot order
        sections.sort() 
        
        # Get averages, converting them back to floats for plotting
        averages = [float(comparison_stats[sec]['average']) for sec in sections]
    except Exception as e:
        print(f"Error processing stats for plotting: {e}")
        return

    # Set up the plot
    plt.figure(figsize=(10, 6))
    
    # Create the bar chart
    colors = plt.cm.get_cmap('Pastel1', len(sections))
    bars = plt.bar(sections, averages, color=colors.colors, edgecolor='red')

    # Add titles and labels
    plt.title('Average Final Score by Section', fontsize=16)
    plt.xlabel('Section', fontsize=12)
    plt.ylabel('Average Final Score', fontsize=12)
    plt.ylim(0, 100) # Grades are 0-100
    plt.grid(axis='y', linestyle='--', alpha=0.7)

    # Add data labels on top of each bar
    for bar in bars:
        yval = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2.0, yval + 1.0, f'{yval:.2f}', ha='center', va='bottom')

    #  Save the plot
    os.makedirs(output_dir, exist_ok=True)
    plot_path = os.path.join(output_dir, "section_comparison_barchart.png")
    
    try:
        plt.savefig(plot_path)
        plt.close() # Close the plot to free memory
        print(f"Successfully saved section comparison plot to: {plot_path}")
    except Exception as e:
        print(f"Error saving plot: {e}")