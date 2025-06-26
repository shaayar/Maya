"""
Compile Qt resource files.
Run this script to compile the .qrc file into a Python module.
"""

import os
import sys
import subprocess
from pathlib import Path

def find_pyrcc():
    """Find the pyrcc6 executable in the Python scripts directory."""
    python_dir = Path(sys.executable).parent
    
    # Common locations for pyrcc6
    possible_paths = [
        python_dir / 'Scripts' / 'pyrcc6.exe',  # Windows
        python_dir / 'pyrcc6',  # Unix-like
        python_dir / 'Scripts' / 'pyrcc6',  # Windows (alternative)
    ]
    
    for path in possible_paths:
        if path.exists():
            return str(path)
    
    return None

def compile_resources():
    """Compile the .qrc file into a Python module."""
    try:
        # Get the path to the resource file
        base_dir = os.path.dirname(os.path.abspath(__file__))
        qrc_file = os.path.join(base_dir, 'resources.qrc')
        output_file = os.path.join(base_dir, 'resources_rc.py')
        
        # Find pyrcc6 executable
        pyrcc_path = find_pyrcc()
        if not pyrcc_path:
            print("Error: Could not find pyrcc6 executable. Make sure PyQt6-tools is installed.")
            print("Try running: pip install pyqt6-tools")
            return False
            
        # Compile the resource file using pyrcc6
        cmd = [pyrcc_path, qrc_file, '-o', output_file]
        print(f"Running: {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        print(f"Successfully compiled resources to {output_file}")
        return True
    except Exception as e:
        print(f"Error compiling resources: {e}")
        return False

if __name__ == "__main__":
    compile_resources()
