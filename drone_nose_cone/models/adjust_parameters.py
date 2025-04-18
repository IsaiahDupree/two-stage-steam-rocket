#!/usr/bin/env python
"""
Drone Nose Cone Parameter Adjuster
Allows users to modify nose cone parameters and generate updated models.
"""

import os
import argparse
import re
import subprocess
import json
from pathlib import Path

# Define the default parameters
DEFAULT_PARAMS = {
    "inner_diameter": 67.0,  # mm
    "outer_diameter": 78.0,  # mm
    "base_ring_depth": 13.0,  # mm
    "cone_angle": 52.0,      # degrees
    "profile_type": "conical",  # Shape profile
    "use_lightweighting": True,
    "shell_thickness": 1.2,  # mm
    "wall_thinning_factor": 1.0,  # Gradual wall thinning (1.0 = none)
    "internal_ribs": True,
    "rib_count": 6           # number of ribs
}

CONFIG_FILE = os.path.join(os.path.dirname(__file__), "parameters.json")

def read_parameters():
    """Read parameters from the config file if it exists, otherwise use defaults"""
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    return DEFAULT_PARAMS

def save_parameters(params):
    """Save parameters to the config file"""
    with open(CONFIG_FILE, 'w') as f:
        json.dump(params, f, indent=2)
    print(f"Parameters saved to {CONFIG_FILE}")

def update_openscad_file(params):
    """Update the OpenSCAD file with new parameters"""
    scad_file = os.path.join(os.path.dirname(__file__), "nose_cone.scad")
    
    if not os.path.exists(scad_file):
        print(f"Error: OpenSCAD file not found at {scad_file}")
        return False
    
    with open(scad_file, 'r') as f:
        content = f.read()
    
    # Update each parameter in the file
    for param_name, param_value in params.items():
        # Handle boolean values specially for OpenSCAD
        if isinstance(param_value, bool):
            param_value_str = "true" if param_value else "false"
            pattern = rf"{param_name}\s*=\s*(true|false)"
        else:
            param_value_str = str(param_value)
            pattern = rf"{param_name}\s*=\s*[0-9.]+\s*;"
            
        replacement = f"{param_name} = {param_value_str};"
        
        # Use regex to replace the parameter
        content = re.sub(pattern, replacement, content)
    
    # Write the updated content back to the file
    with open(scad_file, 'w') as f:
        f.write(content)
    
    print(f"Updated OpenSCAD file with new parameters at {scad_file}")
    return True

def update_python_files(params):
    """Update parameter values in Python files"""
    files_to_update = [
        os.path.join(os.path.dirname(__file__), "nose_cone_generator.py"),
        os.path.join(os.path.dirname(__file__), "visualize_design.py"),
        os.path.join(os.path.dirname(__file__), "preview_3d.py"),
        os.path.join(os.path.dirname(__file__), "validate_design.py")
    ]
    
    for file_path in files_to_update:
        if not os.path.exists(file_path):
            print(f"Warning: File not found: {file_path}")
            continue
        
        with open(file_path, 'r') as f:
            content = f.read()
        
        # Update each parameter in the file
        for param_name, param_value in params.items():
            # Convert parameter name to uppercase for Python constants
            upper_param_name = param_name.upper()
            
            # Handle boolean values specially
            if isinstance(param_value, bool):
                param_value_str = str(param_value)
                pattern = rf"{upper_param_name}\s*=\s*(True|False)"
            else:
                param_value_str = str(param_value)
                pattern = rf"{upper_param_name}\s*=\s*[0-9.]+\s*#?\s*"
                
            replacement = f"{upper_param_name} = {param_value_str}  # "
            
            # Use regex to replace the parameter
            content = re.sub(pattern, replacement, content)
        
        # Write the updated content back to the file
        with open(file_path, 'w') as f:
            f.write(content)
        
        print(f"Updated {file_path}")
    
    return True

def generate_all():
    """Generate all output files after parameter updates"""
    params = read_parameters()
    
    # Run validation
    validate_script = os.path.join(os.path.dirname(__file__), "validate_design.py")
    if os.path.exists(validate_script):
        print("\nRunning design validation...")
        result = subprocess.run(['python', validate_script], 
                                capture_output=True, text=True)
        print(result.stdout)
        if result.returncode != 0:
            print(f"Validation error: {result.stderr}")
            return False
    
    # Generate visualization in non-interactive mode
    print("\nGenerating 2D visualization...")
    vis_script = os.path.join(os.path.dirname(__file__), "visualize_design.py")
    if os.path.exists(vis_script):
        try:
            # Use --no-display flag to prevent interactive plotting
            result = subprocess.run(['python', vis_script, '--no-display'], 
                                  capture_output=True, text=True)
            print(result.stdout)
        except Exception as e:
            print(f"Visualization error: {e}")
            
    # Run profile comparison in non-interactive mode
    print("\nGenerating profile comparison...")
    comp_script = os.path.join(os.path.dirname(__file__), "compare_profiles.py")
    if os.path.exists(comp_script):
        try:
            # Use --no-display flag to prevent interactive plotting
            result = subprocess.run(['python', comp_script, '--no-display'], 
                                  capture_output=True, text=True)
            print(result.stdout)
        except Exception as e:
            print(f"Comparison error: {e}")
    
    # Generate 3D models
    print("\nGenerating 3D models...")
    gen_script = os.path.join(os.path.dirname(__file__), "nose_cone_generator.py")
    if os.path.exists(gen_script):
        try:
            result = subprocess.run(['python', gen_script], 
                                  capture_output=True, text=True)
            print(result.stdout)
        except Exception as e:
            print(f"Generation error: {e}")
    
    print("\nAll files generated successfully!")
    return True

def main():
    """Main entry point for the parameter adjustment script"""
    parser = argparse.ArgumentParser(description="Adjust drone nose cone parameters")
    
    # Add arguments for each parameter
    parser.add_argument("--inner-diameter", type=float, help="Inner diameter in mm")
    parser.add_argument("--outer-diameter", type=float, help="Outer diameter in mm")
    parser.add_argument("--base-ring-depth", type=float, help="Base ring depth in mm")
    parser.add_argument("--cone-angle", type=float, help="Cone angle in degrees")
    parser.add_argument("--profile-type", type=str, 
                     choices=["conical", "ogive", "elliptical", "karman", "tangent", "rounded_elliptical"],
                       help="Profile type for the nose cone shape")
    parser.add_argument("--use-lightweighting", type=str, choices=["true", "false"], 
                        help="Use lightweighting features (true/false)")
    parser.add_argument("--shell-thickness", type=float, help="Shell thickness in mm")
    parser.add_argument("--wall-thinning-factor", type=float, 
                       help="Wall thinning factor (0.5-1.0)")
    parser.add_argument("--internal-ribs", type=str, choices=["true", "false"],
                        help="Use internal ribs (true/false)")
    parser.add_argument("--rib-count", type=int, help="Number of internal ribs")
    parser.add_argument("--reset", action="store_true", help="Reset to default parameters")
    parser.add_argument("--generate", action="store_true", 
                        help="Generate all output files after parameter updates")
    
    args = parser.parse_args()
    
    # If reset is specified, reset to default parameters
    if args.reset:
        save_parameters(DEFAULT_PARAMS)
        params = DEFAULT_PARAMS
    else:
        # Read current parameters
        params = read_parameters()
        
        # Update parameters with command-line arguments
        if args.inner_diameter is not None:
            params["inner_diameter"] = args.inner_diameter
        if args.outer_diameter is not None:
            params["outer_diameter"] = args.outer_diameter
        if args.base_ring_depth is not None:
            params["base_ring_depth"] = args.base_ring_depth
        if args.cone_angle is not None:
            params["cone_angle"] = args.cone_angle
        if args.profile_type is not None:
            params["profile_type"] = args.profile_type
        if args.use_lightweighting is not None:
            params["use_lightweighting"] = args.use_lightweighting.lower() == "true"
        if args.shell_thickness is not None:
            params["shell_thickness"] = args.shell_thickness
        if args.wall_thinning_factor is not None:
            params["wall_thinning_factor"] = args.wall_thinning_factor
        if args.internal_ribs is not None:
            params["internal_ribs"] = args.internal_ribs.lower() == "true"
        if args.rib_count is not None:
            params["rib_count"] = args.rib_count
        
        # Save updated parameters
        save_parameters(params)
    
    # Update files with new parameters
    if update_openscad_file(params) and update_python_files(params):
        print("All files updated with new parameters")
    
    # Generate output files if requested
    if args.generate:
        generate_all()
    else:
        print("\nTo generate updated output files, run:")
        print("  python models/adjust_parameters.py --generate")
    
    print("\nCurrent parameters:")
    for param_name, param_value in params.items():
        print(f"  {param_name}: {param_value}")

if __name__ == "__main__":
    main()
