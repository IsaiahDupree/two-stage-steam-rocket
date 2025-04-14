#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
FreeCAD Launcher Script

This script handles Python version compatibility issues by:
1. Detecting which Python version is needed by FreeCAD
2. Creating a custom environment 
3. Launching the appropriate version of FreeCAD/Python

Compatible with both Windows and Mac environments.
"""

import os
import sys
import subprocess
import platform
import time
import json

def log(message):
    """Print log message with timestamp"""
    print(f"[{time.strftime('%H:%M:%S')}] {message}")

def detect_freecad_paths():
    """Detect common FreeCAD installation paths by platform"""
    log("Detecting FreeCAD installation...")
    
    # Common FreeCAD installation paths by platform
    freecad_paths = {
        'windows': [
            "C:/Program Files/FreeCAD 1.0",
            "C:/Program Files/FreeCAD 0.20", 
            "C:/Program Files/FreeCAD 0.19",
            "C:/Program Files/FreeCAD 0.18",
        ],
        'darwin': [  # Mac OS
            "/Applications/FreeCAD.app",
        ],
        'linux': [
            "/usr/lib/freecad",
            "/usr/local/lib/freecad",
        ]
    }
    
    # Determine platform
    system = platform.system().lower()
    if system == 'windows':
        platform_key = 'windows'
    elif system == 'darwin':
        platform_key = 'darwin'
    else:
        platform_key = 'linux'
    
    log(f"Detected platform: {platform_key}")
    
    # Check paths
    valid_paths = []
    for path in freecad_paths.get(platform_key, []):
        if os.path.exists(path):
            log(f"Found FreeCAD at: {path}")
            valid_paths.append(path)
    
    return valid_paths

def detect_python_version_for_freecad(freecad_path):
    """Detect which Python version FreeCAD is expecting"""
    log(f"Detecting Python version for FreeCAD at {freecad_path}...")
    
    # Check for Python DLLs in bin directory
    bin_dir = os.path.join(freecad_path, "bin")
    if os.path.exists(bin_dir):
        for file in os.listdir(bin_dir):
            if file.lower().startswith("python") and file.lower().endswith(".dll"):
                version = file.lower().replace("python", "").replace(".dll", "")
                if version.isdigit() and len(version) >= 2:
                    major = version[0]
                    minor = version[1:]
                    log(f"Detected Python {major}.{minor} requirement from {file}")
                    return f"{major}.{minor}"
    
    # Default to Python 3.11 (common for newer FreeCAD versions)
    log("Could not determine exact version, defaulting to Python 3.11")
    return "3.11"

def check_conda():
    """Check if conda is available"""
    try:
        result = subprocess.run(["conda", "--version"], 
                               capture_output=True, 
                               text=True)
        if result.returncode == 0:
            log(f"Found conda: {result.stdout.strip()}")
            return True
    except:
        pass
    
    return False

def check_python_version(desired_version):
    """Check if a specific Python version is available"""
    try:
        # Try running Python with -V flag
        cmd = f"python{desired_version}" if sys.platform != "win32" else f"py -{desired_version}"
        result = subprocess.run([cmd, "-V"], 
                               capture_output=True, 
                               text=True,
                               shell=True)
        if result.returncode == 0:
            log(f"Found {result.stdout.strip()}")
            return True
    except:
        pass
    
    return False

def setup_conda_env(python_version):
    """Setup a conda environment with the correct Python version"""
    env_name = f"freecad-py{python_version.replace('.', '')}"
    
    log(f"Creating conda environment '{env_name}' with Python {python_version}...")
    
    # Check if environment already exists
    try:
        result = subprocess.run(["conda", "env", "list", "--json"], 
                               capture_output=True, 
                               text=True)
        if result.returncode == 0:
            env_list = json.loads(result.stdout)
            for env_path in env_list["envs"]:
                if env_path.endswith(env_name):
                    log(f"Environment '{env_name}' already exists")
                    return env_name
    except:
        pass
    
    # Create new environment
    try:
        subprocess.run(["conda", "create", "-n", env_name, f"python={python_version}", "-y"], 
                      check=True)
        log(f"Successfully created environment '{env_name}'")
        return env_name
    except subprocess.CalledProcessError as e:
        log(f"Error creating conda environment: {e}")
        return None

def run_automation_script(script_path, csv_path=None, env_name=None):
    """Run the automation script with the correct environment"""
    log(f"Running automation script: {script_path}")
    
    cmd = []
    
    # Decide how to run the script
    if env_name:
        # Run with conda environment
        if sys.platform == "win32":
            cmd = ["conda", "run", "-n", env_name, "python", script_path]
        else:
            cmd = ["conda", "run", "-n", env_name, "python", script_path]
    else:
        # Run with system Python
        cmd = ["python", script_path]
    
    # Add CSV path if provided
    if csv_path:
        cmd.append(csv_path)
    
    # Run the command
    try:
        log(f"Executing: {' '.join(cmd)}")
        subprocess.run(cmd, check=True)
        log("Automation script completed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        log(f"Error running automation script: {e}")
        return False

def main():
    """Main function to handle FreeCAD automation"""
    log("Starting FreeCAD Automation Launcher...")
    
    # Get current directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    automation_script = os.path.join(script_dir, "rocket_csv_automation.py")
    
    # Check if automation script exists
    if not os.path.exists(automation_script):
        log(f"ERROR: Automation script not found: {automation_script}")
        return 1
    
    # Detect FreeCAD paths
    freecad_paths = detect_freecad_paths()
    if not freecad_paths:
        log("ERROR: FreeCAD installation not found. Please install FreeCAD first.")
        install_instructions()
        return 1
    
    # For simplicity, use the first found FreeCAD path
    freecad_path = freecad_paths[0]
    
    # Detect required Python version
    python_version = detect_python_version_for_freecad(freecad_path)
    
    # Check conda availability
    has_conda = check_conda()
    
    # Check if we have direct access to the right Python version
    has_python_version = check_python_version(python_version)
    
    # Decide how to proceed
    if has_python_version:
        log(f"Using system Python {python_version}")
        env_name = None
    elif has_conda:
        log(f"Setting up conda environment for Python {python_version}")
        env_name = setup_conda_env(python_version)
    else:
        log("ERROR: Required Python version not found and conda not available.")
        log(f"Please install Python {python_version} or conda to proceed.")
        install_instructions()
        return 1
    
    # Get CSV path from command line if provided
    csv_path = None
    if len(sys.argv) > 1:
        csv_path = sys.argv[1]
        if not os.path.exists(csv_path):
            log(f"WARNING: CSV file not found: {csv_path}")
            csv_path = None
    
    # If no CSV provided, use default
    if not csv_path:
        default_csv = os.path.join(script_dir, "rocket_specs.csv")
        if os.path.exists(default_csv):
            csv_path = default_csv
            log(f"Using default CSV file: {csv_path}")
        else:
            log("WARNING: No CSV file specified and default not found.")
    
    # Run the automation script
    success = run_automation_script(automation_script, csv_path, env_name)
    
    if success:
        log("FreeCAD Automation completed successfully!")
        return 0
    else:
        log("FreeCAD Automation failed. Please check logs for details.")
        return 1

def install_instructions():
    """Print installation instructions"""
    print("\n" + "="*50)
    print("INSTALLATION INSTRUCTIONS")
    print("="*50)
    print("\nOption 1: Install FreeCAD from official website")
    print("1. Download FreeCAD from https://www.freecadweb.org/downloads.php")
    print("2. Install following the instructions for your platform")
    print("\nOption 2: Install via conda (recommended for automation)")
    print("1. Install Miniconda from https://docs.conda.io/en/latest/miniconda.html")
    print("2. Open command prompt or terminal")
    print("3. Run: conda install -c conda-forge freecad")
    print("\nAfter installation, run this script again.\n")

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\nOperation cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
