#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Test script for Ansys Geometry integration with the Rocket Design project.
This standalone script verifies the Ansys integration functionality.
"""

import os
import sys
import time

# Add project src directory to path
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.join(SCRIPT_DIR, "src")
if SRC_DIR not in sys.path:
    sys.path.append(SRC_DIR)

# Import our Ansys integration module
try:
    from ansys_integration import create_rocket_in_ansys, integrate_with_freecad_model, ANSYS_AVAILABLE
except ImportError as e:
    print(f"Error importing ansys_integration module: {e}")
    print("Make sure the module exists in the src directory.")
    sys.exit(1)

def print_separator():
    """Print a separator line for better console readability."""
    print("\n" + "="*80 + "\n")

def main():
    """Main function to test Ansys integration."""
    print_separator()
    print("ANSYS GEOMETRY INTEGRATION TEST")
    print_separator()
    
    # Check if Ansys Geometry is available
    if not ANSYS_AVAILABLE:
        print("WARNING: Ansys Geometry is not available on this system.")
        print("This test will show the functionality but won't connect to Ansys services.")
        print("To enable full functionality, install the ansys-geometry-core package.")
        print_separator()
    else:
        print("SUCCESS: Ansys Geometry is available on this system.")
        print_separator()
    
    # Create output directory
    output_dir = os.path.join(SCRIPT_DIR, "output", "ansys_test")
    os.makedirs(output_dir, exist_ok=True)
    print(f"Created output directory: {output_dir}")
    
    # Define rocket configuration
    rocket_config = {
        "total_length": 5000,      # mm
        "max_diameter": 500,       # mm
        "first_stage_length_ratio": 0.6,
        "nose_cone_length_ratio": 0.15,
        "fin_count": 4
    }
    
    # Define engine configuration
    engine_config = {
        "throat_diameter": 30,     # mm
        "exit_diameter": 150,      # mm
        "length": 300,             # mm
    }
    
    # Test Method 1: Create rocket directly in Ansys
    print("\nTEST 1: Creating rocket model directly in Ansys Geometry...")
    start_time = time.time()
    try:
        success = create_rocket_in_ansys(rocket_config, engine_config, output_dir=output_dir)
        if success:
            print("SUCCESS: Successfully created rocket model in Ansys Geometry!")
            print(f"Check the report at: {os.path.join(output_dir, '..', 'reports', 'ansys_analysis_report.md')}")
        else:
            print("FAILED: Failed to create rocket model in Ansys Geometry.")
    except Exception as e:
        print(f"ERROR: Error creating rocket model in Ansys: {e}")
    
    duration = time.time() - start_time
    print(f"Test 1 completed in {duration:.2f} seconds.")
    print_separator()
    
    # Test Method 2: Import from STEP file
    # First, check if a STEP file exists
    step_file = os.path.join(SCRIPT_DIR, "output", "models", "two_stage_rocket.step")
    
    print("\nTEST 2: Importing rocket model from STEP file...")
    
    if not os.path.exists(step_file):
        print(f"WARNING: STEP file not found at: {step_file}")
        print("Skipping STEP file import test.")
    else:
        start_time = time.time()
        try:
            success = integrate_with_freecad_model(step_file, output_dir=output_dir)
            if success:
                print("SUCCESS: Successfully imported STEP model into Ansys Geometry!")
                print(f"Check the report at: {os.path.join(output_dir, '..', 'reports', 'ansys_analysis_report.md')}")
            else:
                print("FAILED: Failed to import STEP model into Ansys Geometry.")
        except Exception as e:
            print(f"ERROR: Error importing STEP model into Ansys: {e}")
        
        duration = time.time() - start_time
        print(f"Test 2 completed in {duration:.2f} seconds.")
    
    print_separator()
    print("ANSYS INTEGRATION TEST COMPLETED")
    print_separator()
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
