"""
Simple script to compile Qt resources using PyQt6's pyrcc6.
"""

import os
import sys
import subprocess

def main():
    # Get the directory of this script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Define input and output files
    qrc_file = os.path.join(script_dir, 'resources.qrc')
    output_file = os.path.join(script_dir, 'resources_rc.py')
    
    # Try to find pyrcc6 in common locations
    python_dir = os.path.dirname(sys.executable)
    pyrcc_paths = [
        os.path.join(python_dir, 'Scripts', 'pyrcc6.exe'),  # Windows
        os.path.join(python_dir, 'pyrcc6'),  # Unix
        'pyrcc6',  # Try if it's in PATH
    ]
    
    # Try each possible path
    for pyrcc_path in pyrcc_paths:
        try:
            cmd = [pyrcc_path, qrc_file, '-o', output_file]
            print(f"Trying: {' '.join(cmd)}")
            result = subprocess.run(cmd, check=True, capture_output=True, text=True)
            print(f"Successfully compiled resources to {output_file}")
            return True
        except (subprocess.CalledProcessError, FileNotFoundError) as e:
            print(f"Failed with {pyrcc_path}: {str(e)}")
    
    print("\nCould not compile resources. Please try one of these solutions:")
    print("1. Install PyQt6-tools: pip install pyqt6-tools")
    print("2. Add PyQt6's bin directory to your PATH")
    print("3. Run the command manually: pyrcc6 resources.qrc -o resources_rc.py")
    return False

if __name__ == "__main__":
    main()
