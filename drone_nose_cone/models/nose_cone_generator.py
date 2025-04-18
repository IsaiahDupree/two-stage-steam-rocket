#!/usr/bin/env python
"""
Drone Nose Cone Generator
Creates a parametric 3D model for a drone nose cone using SolidPython.
This script generates both OpenSCAD code and STL files.
"""

import math
import os
from solid import *
from solid.utils import *

# Parameters
INNER_DIAMETER = 67.0  # mm
OUTER_DIAMETER = 78.0  # mm
BASE_RING_DEPTH = 13.0  # mm
CONE_ANGLE = 52.0  # degrees

# Calculated parameters
INNER_RADIUS = INNER_DIAMETER / 2
OUTER_RADIUS = OUTER_DIAMETER / 2
WALL_THICKNESS = OUTER_RADIUS - INNER_RADIUS

# Derived dimensions
# Calculate cone height based on angle and radius difference
CONE_HEIGHT = (OUTER_RADIUS - INNER_RADIUS) / math.tan(math.radians(CONE_ANGLE))

# Read profile type from parameters.json if it exists
import json
profile_type = "conical"  # Default
config_file = os.path.join(os.path.dirname(__file__), "parameters.json")
if os.path.exists(config_file):
    try:
        with open(config_file, 'r') as f:
            params = json.load(f)
            profile_type = params.get("profile_type", "conical")
    except:
        pass

# Adjust the height based on profile type
if profile_type == "elliptical":
    # For elliptical profile, we want a taller, more pointed cone
    # Make it 2.5-3x the height calculated from the angle
    TOTAL_CONE_HEIGHT = CONE_HEIGHT * 3.0
else:
    # For other profiles, use the original calculation
    TOTAL_CONE_HEIGHT = CONE_HEIGHT * 1.2

# Nose rounding parameters
TIP_ROUNDING_RADIUS = OUTER_RADIUS * 0.5

# Lightweighting parameters
USE_LIGHTWEIGHTING = True  #   #   #   #   #   # 
SHELL_THICKNESS = 1.2  # mm - wall thickness for hollow parts
INTERNAL_RIBS = True  #   #   #   #   #   # 
RIB_THICKNESS = 1.0  # mm
RIB_COUNT = 6  # number of radial ribs

def create_rounded_elliptical_profile():
    """Create a custom rounded elliptical profile for optimized viscous drag"""
    # Create a shape that blends an elliptical body with a rounded tip
    # This shape works better in viscous drag regimes by minimizing boundary layer separation
    
    # Calculate positions
    tip_sphere_radius = OUTER_RADIUS * 0.25  # 25% of the base radius for good rounding
    elliptical_height = TOTAL_CONE_HEIGHT * 0.85  # Slightly shorter to blend with rounded tip
    sphere_center_z = BASE_RING_DEPTH + elliptical_height
    
    # Base elliptical body
    elliptical_body = up(BASE_RING_DEPTH)(
        hull()(
            cylinder(h=0.01, r=OUTER_RADIUS),
            up(elliptical_height)(
                cylinder(h=0.01, r=tip_sphere_radius * 1.2)  # Slightly wider than the tip sphere
            )
        )
    )
    
    # Rounded tip - slightly larger sphere than the pure elliptical profile
    rounded_tip = up(sphere_center_z)(
        sphere(r=tip_sphere_radius)
    )
    
    # Combine them with a smooth blend
    return hull()([elliptical_body, rounded_tip])

def create_nose_cone():
    """Generate the nose cone model"""
    # Base ring
    base_ring = cylinder(h=BASE_RING_DEPTH, r=OUTER_RADIUS)
    
    # Read profile type from parameters.json if it exists
    import json
    import os
    config_file = os.path.join(os.path.dirname(__file__), "parameters.json")
    profile_type = "conical"  # Default
    if os.path.exists(config_file):
        try:
            with open(config_file, 'r') as f:
                params = json.load(f)
                profile_type = params.get("profile_type", "conical")
        except:
            pass
    
    # For the special rounded_elliptical profile, use the custom function
    if profile_type == "rounded_elliptical":
        cone_body = create_rounded_elliptical_profile()
    elif profile_type == "elliptical":
        # For standard elliptical profile, position a small sphere at the tip
        cone_body = up(BASE_RING_DEPTH)(
            hull()(
                cylinder(h=0.01, r=OUTER_RADIUS),
                up(TOTAL_CONE_HEIGHT)(
                    sphere(r=0.01)  # Very small sphere at the tip
                )
            )
        )
    else:
        # For other profiles, use the rounded tip approach
        cone_body = up(BASE_RING_DEPTH)(
            hull()(
                cylinder(h=0.01, r=OUTER_RADIUS),
                up(TOTAL_CONE_HEIGHT - TIP_ROUNDING_RADIUS)(
                    sphere(r=TIP_ROUNDING_RADIUS)
                )
            )
        )
    
    # Combined solid body
    solid_body = base_ring + cone_body
    
    if not USE_LIGHTWEIGHTING:
        # If not using lightweighting, just hollow out the inside with constant thickness
        hollowed_body = solid_body - (
            down(0.1)(cylinder(h=BASE_RING_DEPTH + 0.2, r=INNER_RADIUS)) +
            up(BASE_RING_DEPTH)(
                hull()(
                    cylinder(h=0.01, r=INNER_RADIUS),
                    up(TOTAL_CONE_HEIGHT - TIP_ROUNDING_RADIUS)(
                        sphere(r=TIP_ROUNDING_RADIUS - SHELL_THICKNESS)
                    )
                )
            )
        )
        return hollowed_body
    
    # Base hollow
    base_hollow = down(0.1)(
        cylinder(h=BASE_RING_DEPTH + 0.2, r=INNER_RADIUS)
    )
    
    # Cone hollow
    cone_hollow = up(BASE_RING_DEPTH)(
        hull()(
            cylinder(h=0.01, r=INNER_RADIUS),
            up(TOTAL_CONE_HEIGHT - TIP_ROUNDING_RADIUS)(
                sphere(r=TIP_ROUNDING_RADIUS - SHELL_THICKNESS)
            )
        )
    )
    
    # Hollow out the body
    hollowed_body = solid_body - (base_hollow + cone_hollow)
    
    # Add internal support ribs if enabled
    if INTERNAL_RIBS:
        ribs = union()
        for i in range(RIB_COUNT):
            angle = i * (360 / RIB_COUNT)
            
            # Vertical rib
            rib = rotate([0, 0, angle])(
                up(BASE_RING_DEPTH)(
                    translate([-RIB_THICKNESS/2, 0, 0])(
                        cube([RIB_THICKNESS, OUTER_RADIUS, TOTAL_CONE_HEIGHT * 0.8])
                    )
                )
            )
            
            # Base reinforcement - triangular
            base_support = rotate([0, 0, angle])(
                up(BASE_RING_DEPTH)(
                    translate([-RIB_THICKNESS/2, 0, 0])(
                        rotate([90, 0, 90])(
                            linear_extrude(height=RIB_THICKNESS)(
                                polygon(points=[[0,0], 
                                                [TOTAL_CONE_HEIGHT*0.3, 0], 
                                                [0, TOTAL_CONE_HEIGHT*0.3]])
                            )
                        )
                    )
                )
            )
            
            # Combine rib with base support
            complete_rib = rib + base_support
            
            # Intersect with cone shape to contain ribs
            contained_rib = intersection()(
                complete_rib,
                cone_body
            )
            
            ribs += contained_rib
        
        return hollowed_body + ribs
    
    return hollowed_body

def create_cross_section():
    """Generate a cross-section view of the nose cone"""
    nose_cone = create_nose_cone()
    cross_section = difference()(
        nose_cone,
        translate([-100, 0, -10])(
            cube([200, 200, 200])
        )
    )
    return cross_section

def main():
    """Main function to generate files"""
    # Create the output directory if it doesn't exist
    output_dir = os.path.join(os.path.dirname(__file__), "output")
    os.makedirs(output_dir, exist_ok=True)
    
    # Create the nose cone model
    nose_cone = create_nose_cone()
    
    # Write OpenSCAD code
    scad_file = os.path.join(output_dir, "nose_cone_generated.scad")
    with open(scad_file, "w") as f:
        f.write(scad_render(nose_cone))
    
    # Create a cross-section view for visualization
    cross_section = create_cross_section()
    cross_section_file = os.path.join(output_dir, "nose_cone_cross_section.scad")
    with open(cross_section_file, "w") as f:
        f.write(scad_render(cross_section))
    
    print(f"Generated OpenSCAD files in {output_dir}")
    print("To create STL files, open these files in OpenSCAD and export to STL")
    print("\nParameters used:")
    print(f"Inner Diameter: {INNER_DIAMETER} mm")
    print(f"Outer Diameter: {OUTER_DIAMETER} mm")
    print(f"Base Ring Depth: {BASE_RING_DEPTH} mm")
    print(f"Cone Angle: {CONE_ANGLE} degrees")
    print(f"Calculated Cone Height: {CONE_HEIGHT:.2f} mm")
    print(f"Total Height: {BASE_RING_DEPTH + TOTAL_CONE_HEIGHT:.2f} mm")

if __name__ == "__main__":
    main()
