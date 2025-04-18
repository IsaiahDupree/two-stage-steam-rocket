#!/usr/bin/env python
"""
Drone Nose Cone STL Export Tool
Directly exports OpenSCAD files to STL format.
"""

import os
import sys
import subprocess
import platform
import json
import time
from pathlib import Path

# Check if OpenSCAD command-line is available
def check_openscad_cli():
    """Check if OpenSCAD command line is available"""
    try:
        # Try Windows path first
        if platform.system() == "Windows":
            # Common installation paths for OpenSCAD on Windows
            possible_paths = [
                r"C:\Program Files\OpenSCAD\openscad.exe",
                r"C:\Program Files (x86)\OpenSCAD\openscad.exe",
                # Add user's AppData location
                os.path.join(os.environ.get('APPDATA', ''), "OpenSCAD", "openscad.exe")
            ]
            
            # Try each possible path
            for path in possible_paths:
                if os.path.exists(path):
                    return path
                    
            # Try to find it in the system path
            result = subprocess.run(["where", "openscad"], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                return result.stdout.strip().split("\n")[0]
        else:
            # For macOS and Linux
            result = subprocess.run(["which", "openscad"], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                return result.stdout.strip()
        
        return None
    except Exception as e:
        print(f"Error finding OpenSCAD: {e}")
        return None

def export_stl(scad_file, stl_file=None, openscad_path=None):
    """Export OpenSCAD file to STL format"""
    if not os.path.exists(scad_file):
        print(f"Error: SCAD file not found: {scad_file}")
        return False
    
    # If STL file not specified, use same basename with .stl extension
    if stl_file is None:
        stl_file = os.path.splitext(scad_file)[0] + ".stl"
    
    # Make sure output directory exists
    os.makedirs(os.path.dirname(os.path.abspath(stl_file)), exist_ok=True)
    
    # Find OpenSCAD executable
    if openscad_path is None:
        openscad_path = check_openscad_cli()
    
    if openscad_path is None:
        print("Error: OpenSCAD executable not found.")
        print("Please install OpenSCAD or provide the path to the executable.")
        return False
    
    try:
        # Command line to export STL
        cmd = [openscad_path, "-o", stl_file, scad_file]
        
        # Run the command
        print(f"Exporting STL from {scad_file}...")
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"Successfully exported STL to {stl_file}")
            return True
        else:
            print(f"Error exporting STL: {result.stderr}")
            return False
    except Exception as e:
        print(f"Error running OpenSCAD: {e}")
        return False

def check_for_scad_files():
    """Check for SCAD files in the output directory"""
    output_dir = os.path.join(os.path.dirname(__file__), "output")
    if not os.path.exists(output_dir):
        print(f"Error: Output directory not found: {output_dir}")
        return []
    
    # Find all SCAD files
    scad_files = list(Path(output_dir).glob("*.scad"))
    return scad_files

def export_all_stl_files():
    """Export all SCAD files in the output directory to STL format"""
    scad_files = check_for_scad_files()
    
    if not scad_files:
        print("No SCAD files found in the output directory.")
        return False
    
    # Find OpenSCAD executable
    openscad_path = check_openscad_cli()
    
    if openscad_path is None:
        print("""
OpenSCAD executable not found. Cannot automatically export STL files.
Please install OpenSCAD from https://openscad.org/downloads.html

After installation, you can:
1. Open the SCAD files in OpenSCAD
2. Press F6 to render the model
3. Use File > Export > Export as STL to save the STL file
""")
        # List the files that need to be opened in OpenSCAD
        print("\nSCAD files ready for manual export:")
        for scad_file in scad_files:
            print(f"  - {scad_file}")
        return False
    
    # Export each SCAD file to STL
    success = True
    for scad_file in scad_files:
        if not export_stl(str(scad_file), openscad_path=openscad_path):
            success = False
    
    return success

def generate_and_export():
    """Generate the model and export to STL format"""
    # Get the current parameters
    config_file = os.path.join(os.path.dirname(__file__), "parameters.json")
    if os.path.exists(config_file):
        try:
            with open(config_file, 'r') as f:
                params = json.load(f)
            
            print(f"Current profile type: {params.get('profile_type', 'conical')}")
        except Exception as e:
            print(f"Error reading parameters: {e}")
    
    # Ensure the model is generated
    nose_cone_generator = os.path.join(os.path.dirname(__file__), "nose_cone_generator.py")
    if os.path.exists(nose_cone_generator):
        print("Generating OpenSCAD files...")
        try:
            result = subprocess.run([sys.executable, nose_cone_generator], 
                                  capture_output=True, text=True)
            if result.returncode != 0:
                print(f"Error generating model: {result.stderr}")
        except Exception as e:
            print(f"Error running generator: {e}")
    
    # Export to STL
    return export_all_stl_files()

if __name__ == "__main__":
    print("Drone Nose Cone STL Export Tool")
    print("===============================")
    
    if len(sys.argv) > 1 and sys.argv[1] == "--generate":
        generate_and_export()
    else:
        export_all_stl_files()
