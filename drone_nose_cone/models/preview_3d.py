#!/usr/bin/env python
"""
Drone Nose Cone 3D Preview
Generates a 3D preview of the nose cone using PyVista for visualization.
This provides a quick way to visualize the shape without needing OpenSCAD.
"""

import numpy as np
import pyvista as pv
import math
import os

# Parameters from specifications
INNER_DIAMETER = 67.0  # mm
OUTER_DIAMETER = 78.0  # mm
BASE_RING_DEPTH = 13.0  # mm
CONE_ANGLE = 52.0  # degrees

# Calculated parameters
INNER_RADIUS = INNER_DIAMETER / 2
OUTER_RADIUS = OUTER_DIAMETER / 2

# Calculate cone height based on angle and radius difference
CONE_HEIGHT = (OUTER_RADIUS - INNER_RADIUS) / math.tan(math.radians(CONE_ANGLE))
# Add some height for the rounded tip
TOTAL_CONE_HEIGHT = CONE_HEIGHT * 1.2

# Nose rounding parameters
TIP_ROUNDING_RADIUS = OUTER_RADIUS * 0.5

# Lightweighting parameters
USE_LIGHTWEIGHTING = True  #   #   #   #   #   # 
SHELL_THICKNESS = 1.2  # mm - wall thickness for hollow parts
INTERNAL_RIBS = True  #   #   #   #   #   # 
RIB_THICKNESS = 1.0  # mm
RIB_COUNT = 6  # number of radial ribs

def create_nose_cone_mesh():
    """Create a PyVista mesh for the nose cone"""
    # Create base cylinder (outer)
    outer_base = pv.Cylinder(
        center=(0, 0, BASE_RING_DEPTH/2),
        direction=(0, 0, 1),
        radius=OUTER_RADIUS,
        height=BASE_RING_DEPTH
    )
    
    # Create the cone part
    cone_height = TOTAL_CONE_HEIGHT - TIP_ROUNDING_RADIUS
    outer_cone = pv.Cone(
        center=(0, 0, BASE_RING_DEPTH + cone_height/2),
        direction=(0, 0, 1),
        height=cone_height,
        radius=OUTER_RADIUS,
        resolution=64
    )
    
    # Create sphere for the rounded tip
    tip_sphere = pv.Sphere(
        center=(0, 0, BASE_RING_DEPTH + cone_height),
        radius=TIP_ROUNDING_RADIUS,
        resolution=32
    )
    
    # Combine to create outer shell
    outer_shell = outer_base.boolean_union(outer_cone)
    outer_shell = outer_shell.boolean_union(tip_sphere)
    
    # Create hollow parts if using lightweighting
    if USE_LIGHTWEIGHTING:
        # Inner base cylinder
        inner_base = pv.Cylinder(
            center=(0, 0, BASE_RING_DEPTH/2),
            direction=(0, 0, 1),
            radius=INNER_RADIUS,
            height=BASE_RING_DEPTH + 0.2  # slightly larger to ensure clean boolean
        )
        
        # Inner cone
        inner_cone = pv.Cone(
            center=(0, 0, BASE_RING_DEPTH + cone_height/2),
            direction=(0, 0, 1),
            height=cone_height,
            radius=INNER_RADIUS,
            resolution=64
        )
        
        # Inner sphere for the tip hollow
        inner_sphere = pv.Sphere(
            center=(0, 0, BASE_RING_DEPTH + cone_height),
            radius=TIP_ROUNDING_RADIUS - SHELL_THICKNESS,
            resolution=32
        )
        
        # Combine inner parts
        inner_shell = inner_base.boolean_union(inner_cone)
        inner_shell = inner_shell.boolean_union(inner_sphere)
        
        # Subtract inner from outer to create hollow shell
        nose_cone = outer_shell.boolean_difference(inner_shell)
        
        # Add internal ribs if enabled
        if INTERNAL_RIBS:
            all_ribs = pv.PolyData()
            for i in range(RIB_COUNT):
                angle = i * (360 / RIB_COUNT)
                # Create rib as a box with proper rotation
                rib_height = TOTAL_CONE_HEIGHT * 0.8
                rib = pv.Box(
                    bounds=(-RIB_THICKNESS/2, RIB_THICKNESS/2, 
                            0, OUTER_RADIUS, 
                            BASE_RING_DEPTH, BASE_RING_DEPTH + rib_height)
                )
                # Rotate rib around z-axis
                rib.rotate_z(angle)
                all_ribs += rib
            
            # Intersect ribs with the cone shape
            all_ribs = all_ribs.boolean_intersect(outer_shell)
            
            # Add ribs to the hollow cone
            nose_cone = nose_cone.boolean_union(all_ribs)
            
        return nose_cone
    
    # If not using lightweighting, return solid shape
    return outer_shell

def visualize_nose_cone():
    """Create a visualization of the nose cone"""
    # Create the plotter
    plotter = pv.Plotter()
    
    # Add a title
    plotter.add_title("Drone Nose Cone 3D Preview", font_size=20)
    
    # Get the mesh
    nose_cone = create_nose_cone_mesh()
    
    # Add the nose cone mesh to the plot
    plotter.add_mesh(nose_cone, color='lightblue', show_edges=True)
    
    # Optional: Add a cross-section view
    create_cross_section = True
    if create_cross_section:
        # Create a clipping plane
        clipping_plane = pv.Plane(origin=(0, 0, 0), normal=(0, 1, 0))
        
        # Clip the mesh with the plane
        clipped = nose_cone.clip(normal=(0, 1, 0), origin=(0, 0, 0))
        
        # Add clipped mesh
        plotter.add_mesh(clipped, color='lightblue', show_edges=True)
    
    # Add axes
    plotter.add_axes()
    
    # Add text with dimensions
    plotter.add_text(f"Inner Diameter: {INNER_DIAMETER} mm\nOuter Diameter: {OUTER_DIAMETER} mm\n"
                    f"Base Ring: {BASE_RING_DEPTH} mm\nCone Angle: {CONE_ANGLE}°", 
                    position='upper_left', font_size=12)
    
    # Show the plot
    plotter.show()
    
    # Save screenshot to output directory
    output_dir = os.path.join(os.path.dirname(__file__), "output")
    os.makedirs(output_dir, exist_ok=True)
    plotter.screenshot(os.path.join(output_dir, 'nose_cone_3d_preview.png'), transparent_background=True)

if __name__ == "__main__":
    print("Generating 3D preview of the nose cone...")
    print("This may take a few moments to render.")
    visualize_nose_cone()
    print("Preview complete. Screenshot saved to models/output directory.")
