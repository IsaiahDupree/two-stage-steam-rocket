#!/usr/bin/env python
"""
Drone Nose Cone Project Setup
This script will help set up the environment for the drone nose cone designer.
"""

import os
import sys
import subprocess
import platform
import shutil

def check_python_version():
    """Check if Python version is compatible."""
    version_info = sys.version_info
    if version_info.major < 3 or (version_info.major == 3 and version_info.minor < 6):
        print("Error: Python 3.6 or higher is required.")
        print(f"Current Python version: {platform.python_version()}")
        return False
    return True

def install_dependencies():
    """Install required Python packages."""
    required_packages = [
        "numpy>=1.20.0",
        "matplotlib>=3.5.0",
        "solidpython>=1.0.0",
        "pyvista>=0.36.0"
    ]
    
    print("Installing required packages...")
    for package in required_packages:
        try:
            print(f"Installing {package}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        except subprocess.CalledProcessError as e:
            print(f"Error installing {package}: {e}")
            return False
    
    print("All dependencies installed successfully.")
    return True

def create_openscad_files():
    """Copy OpenSCAD files to models directory."""
    # Enhanced model should already exist, check if original exists
    src_file = os.path.join("models", "enhanced_nose_cone.scad")
    dst_file = os.path.join("models", "nose_cone.scad")
    
    if os.path.exists(src_file) and not os.path.exists(dst_file):
        try:
            shutil.copy2(src_file, dst_file)
            print(f"Created {dst_file} from {src_file}")
        except Exception as e:
            print(f"Error copying OpenSCAD file: {e}")
            return False
    
    return True

def run_designer():
    """Run the drone nose cone designer."""
    try:
        subprocess.run([sys.executable, "drone_nose_cone_designer.py", "params"])
        print("\nSetup complete! You can now use the drone nose cone designer.")
        print("\nCommands you can use:")
        print("  python drone_nose_cone_designer.py validate   - Validate the current design")
        print("  python drone_nose_cone_designer.py compare    - Compare different nose cone profiles")
        print("  python drone_nose_cone_designer.py generate   - Generate 3D models")
        print("  python drone_nose_cone_designer.py params     - View or modify parameters")
        print("  python drone_nose_cone_designer.py gui        - Launch the graphical interface")
        return True
    except Exception as e:
        print(f"Error running designer: {e}")
        return False

def main():
    """Main setup function."""
    print("=" * 60)
    print("Drone Nose Cone Designer - Setup")
    print("=" * 60)
    
    # Check Python version
    if not check_python_version():
        return False
    
    # Install dependencies
    if not install_dependencies():
        print("Error: Failed to install dependencies.")
        return False
    
    # Create OpenSCAD files
    if not create_openscad_files():
        print("Warning: Failed to create OpenSCAD files.")
        # Continue anyway
    
    # Run the designer
    if not run_designer():
        print("Error: Failed to run designer.")
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    if not success:
        print("\nSetup encountered errors. Please check the output above.")
        sys.exit(1)
