import json
import os
from typing import Dict, Any, List

import ingest
import menu  

# --- Build robust, absolute paths based on this script's location ---
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
CONFIG_PATH = os.path.join(PROJECT_ROOT, 'config.json')

def load_configuration(config_path: str) -> Dict[str, Any]:
    """Loads the main JSON configuration file."""
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
        print(f"Configuration loaded from {config_path}")
        return config
    except FileNotFoundError:
        print(f"Error: Configuration file not found at {config_path}")
        print("Please ensure 'config.json' is in the main project directory.")
        exit(1) 
    except json.JSONDecodeError:
        print(f"Error: Configuration file {config_path} is not valid JSON.")
        exit(1)

def main():
    print("===== Welcome to Academic Analytics Lite =====")
    
    config = load_configuration(CONFIG_PATH)
    paths_config = config.get('paths', {})
    
    # --- Setup paths ---
    input_csv_name = paths_config.get('input_csv', 'data/input.csv')
    input_csv_path = os.path.join(PROJECT_ROOT, input_csv_name)
    output_dir_name = paths_config.get('output_dir', 'reports')
    output_dir = os.path.join(PROJECT_ROOT, output_dir_name)
    
    # --- Load initial data ---
    students = ingest.read_csv_data(input_csv_path)
    if not students:
        print(f"No valid student data loaded from {input_csv_path}. Exiting.")
        return
        
    # --- Start the command-line menu ---
    menu.main_menu(students, config, output_dir)

if __name__ == "__main__":
    main()