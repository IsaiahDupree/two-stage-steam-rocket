#!/usr/bin/env python
"""
Drone Nose Cone Designer
An all-in-one tool for designing, analyzing, and generating 3D models of drone nose cones.

This script provides a command-line interface to access all the drone nose cone tools:
- Parameter adjustment
- Profile comparison
- Design validation
- 3D model generation
- Visualization

Usage:
    python drone_nose_cone_designer.py --help
    python drone_nose_cone_designer.py validate
    python drone_nose_cone_designer.py compare
    python drone_nose_cone_designer.py generate --profile elliptical
"""

import os
import sys
import argparse
import subprocess
import json
import time

# Default parameters
DEFAULT_PARAMS = {
    "inner_diameter": 67.0,  # mm
    "outer_diameter": 78.0,  # mm
    "base_ring_depth": 13.0,  # mm
    "cone_angle": 52.0,      # degrees
    "profile_type": "conical",  # Profile type
    "use_lightweighting": True,
    "shell_thickness": 1.2,  # mm
    "wall_thinning_factor": 1.0,  # 1.0 = no thinning
    "internal_ribs": True,
    "rib_count": 6           # number of ribs
}

CONFIG_FILE = os.path.join(os.path.dirname(__file__), "models", "parameters.json")


def read_parameters():
    """Read parameters from the config file if it exists, otherwise use defaults"""
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error reading config: {e}")
            return DEFAULT_PARAMS.copy()
    return DEFAULT_PARAMS.copy()


def save_parameters(params):
    """Save parameters to the config file"""
    os.makedirs(os.path.dirname(CONFIG_FILE), exist_ok=True)
    with open(CONFIG_FILE, 'w') as f:
        json.dump(params, f, indent=2)
    print(f"Parameters saved to {CONFIG_FILE}")


def update_parameters(args):
    """Update parameters based on command-line arguments"""
    params = read_parameters()
    
    # Update parameters if specified
    if args.inner_diameter is not None:
        params["inner_diameter"] = args.inner_diameter
    if args.outer_diameter is not None:
        params["outer_diameter"] = args.outer_diameter
    if args.base_ring_depth is not None:
        params["base_ring_depth"] = args.base_ring_depth
    if args.cone_angle is not None:
        params["cone_angle"] = args.cone_angle
    if args.profile is not None:
        params["profile_type"] = args.profile
    if args.use_lightweighting is not None:
        params["use_lightweighting"] = args.use_lightweighting
    if args.shell_thickness is not None:
        params["shell_thickness"] = args.shell_thickness
    if args.wall_thinning is not None:
        params["wall_thinning_factor"] = args.wall_thinning
    if args.internal_ribs is not None:
        params["internal_ribs"] = args.internal_ribs
    if args.rib_count is not None:
        params["rib_count"] = args.rib_count
    
    # Save the updated parameters
    save_parameters(params)
    return params


def validate_parameters(params):
    """Validate parameter values"""
    inner_diameter = params["inner_diameter"]
    outer_diameter = params["outer_diameter"]
    base_ring_depth = params["base_ring_depth"]
    cone_angle = params["cone_angle"]
    
    issues = []
    
    # Basic validation
    if inner_diameter <= 0:
        issues.append("Inner diameter must be positive")
    if outer_diameter <= 0:
        issues.append("Outer diameter must be positive")
    if base_ring_depth <= 0:
        issues.append("Base ring depth must be positive")
    if cone_angle <= 0 or cone_angle >= 90:
        issues.append("Cone angle must be between 0 and 90 degrees")
    
    # Relationship validation
    if outer_diameter <= inner_diameter:
        issues.append("Outer diameter must be larger than inner diameter")
    
    return issues


def run_script(script_name, args=None, capture_output=False):
    """Run a Python script"""
    if args is None:
        args = []
    
    script_path = os.path.join(os.path.dirname(__file__), "models", script_name)
    
    if not os.path.exists(script_path):
        print(f"Script not found: {script_path}")
        return None
    
    try:
        if capture_output:
            result = subprocess.run([sys.executable, script_path] + args, 
                                  capture_output=True, text=True)
            return result
        else:
            subprocess.run([sys.executable, script_path] + args)
            return True
    except Exception as e:
        print(f"Error running script: {e}")
        return None


def run_validation():
    """Run the validation script and display the results"""
    print("Running validation...")
    result = run_script("validate_design.py", capture_output=True)
    
    if result and result.returncode == 0:
        print(result.stdout)
        print("Validation complete.")
        return True
    else:
        print("Validation failed.")
        if result:
            print(result.stderr)
        return False


def run_profile_comparison(interactive=False):
    """Run the profile comparison script
    
    Args:
        interactive: Whether to show interactive plots
    """
    print("Running profile comparison...")
    args = ["--no-display"] if not interactive else []
    result = run_script("compare_profiles.py", args, capture_output=True)
    
    if result and result.returncode == 0:
        print("Profile comparison complete. Results saved to models/output directory.")
        return True
    else:
        print("Profile comparison failed.")
        if result:
            print(result.stderr)
        return False


def generate_models(profile_type=None, interactive=False):
    """Generate 3D models with current parameters
    
    Args:
        profile_type: The profile type to use (e.g., "conical", "elliptical")
        interactive: Whether to show interactive plots during generation
    """
    params = read_parameters()
    
    # Update profile type if specified
    if profile_type:
        params["profile_type"] = profile_type
        save_parameters(params)
    
    print(f"Generating models with profile type: {params['profile_type']}...")
    
    # Update the script arguments - ensure parameter names match what adjust_parameters.py expects
    update_script = []
    
    # Map our parameters to the adjust_parameters.py script's expected parameters
    param_mapping = {
        "profile_type": "profile-type",
        "wall_thinning_factor": "wall-thinning-factor"
    }
    
    for key, value in params.items():
        # Get the correct parameter name
        param_name = param_mapping.get(key, key.replace('_', '-'))
        
        # Build the command arguments
        if isinstance(value, bool):
            update_script.extend([f"--{param_name}", "true" if value else "false"])
        else:
            update_script.extend([f"--{param_name}", str(value)])
    
    # Run the parameter update script
    result = run_script("adjust_parameters.py", update_script)
    
    if not result:
        print("Failed to update parameters.")
        return False
    
    # Run the generation sequence
    print("Running validation...")
    run_script("validate_design.py")
    
    print("Generating visualization...")
    run_script("visualize_design.py", ["--no-display"])
    
    print("Generating 3D models...")
    run_script("nose_cone_generator.py")
    
    print("Models generated successfully!")
    
    # Attempt to open the output directory
    try:
        output_dir = os.path.join(os.path.dirname(__file__), "models", "output")
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        # Open folder in explorer
        if sys.platform == 'win32':
            os.startfile(output_dir)
        elif sys.platform == 'darwin':  # macOS
            subprocess.run(['open', output_dir])
        else:  # Linux
            subprocess.run(['xdg-open', output_dir])
    except Exception as e:
        print(f"Note: Could not open output directory: {e}")
    
    return True


def launch_gui():
    """Launch the GUI interface"""
    print("Launching GUI interface...")
    run_script("nose_cone_gui.py")


def print_parameters():
    """Print the current parameters"""
    params = read_parameters()
    
    print("\nCurrent Parameters:")
    print("==================")
    
    # Organize parameters by groups
    basic_params = ["inner_diameter", "outer_diameter", "base_ring_depth", "cone_angle", "profile_type"]
    advanced_params = ["use_lightweighting", "shell_thickness", "wall_thinning_factor", "internal_ribs", "rib_count"]
    
    print("\nBasic Parameters:")
    for param in basic_params:
        if param in params:
            if param == "profile_type":
                print(f"  Profile Type: {params[param]}")
            else:
                unit = "mm" if "diameter" in param or "depth" in param else "°" if param == "cone_angle" else ""
                print(f"  {param.replace('_', ' ').title()}: {params[param]} {unit}")
    
    print("\nAdvanced Parameters:")
    for param in advanced_params:
        if param in params:
            if isinstance(params[param], bool):
                print(f"  {param.replace('_', ' ').title()}: {'Yes' if params[param] else 'No'}")
            else:
                unit = "mm" if "thickness" in param else ""
                print(f"  {param.replace('_', ' ').title()}: {params[param]} {unit}")


def main():
    """Main entry point for the drone nose cone designer"""
    parser = argparse.ArgumentParser(
        description="Drone Nose Cone Designer - An all-in-one tool for designing drone nose cones",
        formatter_class=argparse.RawTextHelpFormatter
    )
    
    # Add subparsers for different commands
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    
    # Validate command
    validate_parser = subparsers.add_parser("validate", help="Validate the current design parameters")
    
    # Compare command
    compare_parser = subparsers.add_parser("compare", help="Compare different nose cone profiles")
    compare_parser.add_argument("--interactive", action="store_true",
                             help="Show interactive plots during comparison")
    
    # Generate command
    generate_parser = subparsers.add_parser("generate", help="Generate 3D models with current parameters")
    generate_parser.add_argument("--profile", choices=["conical", "ogive", "elliptical", "karman", "tangent"],
                               help="Profile type to use for generation")
    generate_parser.add_argument("--interactive", action="store_true",
                              help="Show interactive plots during generation")
    
    # Parameters command
    params_parser = subparsers.add_parser("params", help="View or modify parameters")
    params_parser.add_argument("--inner-diameter", type=float, help="Inner diameter in mm")
    params_parser.add_argument("--outer-diameter", type=float, help="Outer diameter in mm")
    params_parser.add_argument("--base-ring-depth", type=float, help="Base ring depth in mm")
    params_parser.add_argument("--cone-angle", type=float, help="Cone angle in degrees")
    params_parser.add_argument("--profile", choices=["conical", "ogive", "elliptical", "karman", "tangent"],
                              help="Profile type to use")
    params_parser.add_argument("--use-lightweighting", type=lambda x: x.lower() == "true",
                              help="Use lightweighting features (true/false)")
    params_parser.add_argument("--shell-thickness", type=float, help="Shell thickness in mm")
    params_parser.add_argument("--wall-thinning", type=float, help="Wall thinning factor (0.5-1.0)")
    params_parser.add_argument("--internal-ribs", type=lambda x: x.lower() == "true",
                              help="Use internal ribs (true/false)")
    params_parser.add_argument("--rib-count", type=int, help="Number of internal ribs")
    params_parser.add_argument("--reset", action="store_true", help="Reset to default parameters")
    
    # GUI command
    gui_parser = subparsers.add_parser("gui", help="Launch the graphical user interface")
    
    # Parse arguments
    args = parser.parse_args()
    
    # If no command is specified, print help
    if not args.command:
        parser.print_help()
        return
    
    # Execute the specified command
    if args.command == "validate":
        run_validation()
    
    elif args.command == "compare":
        # Check if interactive flag is available (for backward compatibility)
        interactive = getattr(args, "interactive", False)
        run_profile_comparison(interactive=interactive)
    
    elif args.command == "generate":
        # Get interactive flag if available
        interactive = getattr(args, "interactive", False)
        generate_models(args.profile, interactive=interactive)
    
    elif args.command == "params":
        # If reset is specified, reset to default parameters
        if args.reset:
            save_parameters(DEFAULT_PARAMS)
            print("Parameters reset to defaults.")
        else:
            # Update parameters
            update_parameters(args)
        
        # Print current parameters
        print_parameters()
    
    elif args.command == "gui":
        launch_gui()


if __name__ == "__main__":
    main()
