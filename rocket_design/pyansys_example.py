#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
PyAnsys Geometry Example for Rocket Design Project.

This script creates a basic rocket model using PyAnsys Geometry API.
"""

import os
import sys
import math
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Try to import PyAnsys Geometry packages
try:
    from ansys.geometry.core import launch_modeler
    from ansys.geometry.core.math import Plane, Point3D, Point2D, UnitVector3D, Vector3D
    from ansys.geometry.core.misc import UNITS, Distance
    from ansys.geometry.core.sketch import Sketch
    ANSYS_AVAILABLE = True
    logger.info("PyAnsys Geometry imported successfully")
except ImportError as e:
    logger.error(f"Error importing PyAnsys Geometry: {e}")
    logger.error("Please install with: pip install ansys-geometry-core")
    ANSYS_AVAILABLE = False
    sys.exit(1)

# Create output directory
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output", "ansys")
os.makedirs(OUTPUT_DIR, exist_ok=True)

def create_rocket_design():
    """Create a 2-stage rocket using PyAnsys Geometry API."""
    logger.info("Starting PyAnsys Geometry rocket modeling...")
    
    # Define rocket parameters
    total_length = 5000 * UNITS.mm
    max_diameter = 500 * UNITS.mm
    first_stage_ratio = 0.6
    nose_cone_ratio = 0.15
    
    # Calculate component dimensions
    first_stage_length = total_length * first_stage_ratio
    second_stage_length = total_length * (1 - first_stage_ratio - nose_cone_ratio)
    nose_cone_length = total_length * nose_cone_ratio
    second_stage_diameter = max_diameter * 0.9
    
    # Start Modeler session
    logger.info("Launching PyAnsys Geometry Modeler...")
    modeler = launch_modeler()
    
    # Create a design
    design = modeler.create_design("TwoStageRocket")
    logger.info("Created new design: TwoStageRocket")
    
    # Create first stage (cylinder)
    logger.info("Creating first stage...")
    first_stage_origin = Point3D([0, 0, 0])
    first_stage_axis = UnitVector3D([0, 0, 1])
    
    # Create first stage using revolve
    first_stage_sketch = Sketch(Plane(first_stage_origin, first_stage_axis, UnitVector3D([1, 0, 0])))
    
    # Draw rectangle for revolution
    first_stage_sketch.line_segment(
        Point2D([0, 0]), 
        Point2D([max_diameter / 2, 0])
    )
    first_stage_sketch.line_segment(
        Point2D([max_diameter / 2, 0]), 
        Point2D([max_diameter / 2, first_stage_length])
    )
    first_stage_sketch.line_segment(
        Point2D([max_diameter / 2, first_stage_length]), 
        Point2D([0, first_stage_length])
    )
    first_stage_sketch.line_segment(
        Point2D([0, first_stage_length]), 
        Point2D([0, 0])
    )
    
    # Revolve to create first stage
    first_stage = design.revolve_sketch(
        name="FirstStage",
        sketch=first_stage_sketch,
        axis_origin=Point3D([0, 0, 0]),
        axis_direction=Vector3D([0, 0, 1]),
        angle=360 * UNITS.deg
    )
    
    # Create second stage (cylinder)
    logger.info("Creating second stage...")
    second_stage_origin = Point3D([0, 0, first_stage_length])
    second_stage_axis = UnitVector3D([0, 0, 1])
    
    # Create second stage using revolve
    second_stage_sketch = Sketch(Plane(second_stage_origin, second_stage_axis, UnitVector3D([1, 0, 0])))
    
    # Draw rectangle for revolution
    second_stage_sketch.line_segment(
        Point2D([0, 0]), 
        Point2D([second_stage_diameter / 2, 0])
    )
    second_stage_sketch.line_segment(
        Point2D([second_stage_diameter / 2, 0]), 
        Point2D([second_stage_diameter / 2, second_stage_length])
    )
    second_stage_sketch.line_segment(
        Point2D([second_stage_diameter / 2, second_stage_length]), 
        Point2D([0, second_stage_length])
    )
    second_stage_sketch.line_segment(
        Point2D([0, second_stage_length]), 
        Point2D([0, 0])
    )
    
    # Revolve to create second stage
    second_stage = design.revolve_sketch(
        name="SecondStage",
        sketch=second_stage_sketch,
        axis_origin=second_stage_origin,
        axis_direction=Vector3D([0, 0, 1]),
        angle=360 * UNITS.deg
    )
    
    # Create nose cone
    logger.info("Creating nose cone...")
    nose_cone_origin = Point3D([0, 0, first_stage_length + second_stage_length])
    nose_cone_axis = UnitVector3D([0, 0, 1])
    
    # Create nose cone sketch
    nose_cone_sketch = Sketch(Plane(nose_cone_origin, nose_cone_axis, UnitVector3D([1, 0, 0])))
    
    # Draw triangle for revolution to create cone
    nose_cone_sketch.line_segment(
        Point2D([0, 0]), 
        Point2D([second_stage_diameter / 2, 0])
    )
    nose_cone_sketch.line_segment(
        Point2D([second_stage_diameter / 2, 0]), 
        Point2D([0, nose_cone_length])
    )
    nose_cone_sketch.line_segment(
        Point2D([0, nose_cone_length]), 
        Point2D([0, 0])
    )
    
    # Revolve to create nose cone
    nose_cone = design.revolve_sketch(
        name="NoseCone",
        sketch=nose_cone_sketch,
        axis_origin=nose_cone_origin,
        axis_direction=Vector3D([0, 0, 1]),
        angle=360 * UNITS.deg
    )
    
    # Create fins (4 fins attached to first stage)
    logger.info("Creating stabilizing fins...")
    
    fin_count = 4
    fin_height = max_diameter * 0.8
    fin_length = first_stage_length * 0.3
    fin_thickness = 10 * UNITS.mm
    fin_position = first_stage_length * 0.1  # Distance from bottom of first stage
    
    for i in range(fin_count):
        angle = (360 / fin_count * i) * UNITS.deg
        
        # Create fin sketch on radial plane
        fin_origin = Point3D([0, 0, fin_position])
        fin_x_dir = UnitVector3D([math.cos(angle/UNITS.deg), math.sin(angle/UNITS.deg), 0])
        fin_y_dir = UnitVector3D([0, 0, 1])
        
        fin_sketch = Sketch(Plane(fin_origin, fin_x_dir, fin_y_dir))
        
        # Draw fin profile
        fin_sketch.line_segment(
            Point2D([max_diameter/2, 0]), 
            Point2D([max_diameter/2 + fin_height, 0])
        )
        fin_sketch.line_segment(
            Point2D([max_diameter/2 + fin_height, 0]), 
            Point2D([max_diameter/2, fin_length])
        )
        fin_sketch.line_segment(
            Point2D([max_diameter/2, fin_length]), 
            Point2D([max_diameter/2, 0])
        )
        
        # Extrude fin
        fin = design.extrude_sketch(
            name=f"Fin_{i+1}",
            sketch=fin_sketch,
            distance=Distance(fin_thickness),
            direction=fin_x_dir.perpendicular
        )
    
    # Plot the complete rocket
    logger.info("Plotting the complete rocket design...")
    design.plot()
    
    # Export the model to various formats
    logger.info("Exporting rocket model...")
    
    # Export to STEP format
    step_file = os.path.join(OUTPUT_DIR, "rocket_pyansys.step")
    design.export_cad(design.get_bodies(), step_file)
    logger.info(f"Exported STEP file to: {step_file}")
    
    # Export to SCDOCX format (native Ansys SpaceClaim format)
    scdocx_file = design.export_to_scdocx(os.path.join(OUTPUT_DIR, "rocket_pyansys.scdocx"))
    logger.info(f"Exported SCDOCX file to: {scdocx_file}")
    
    return design

if __name__ == "__main__":
    try:
        rocket_design = create_rocket_design()
        logger.info("PyAnsys Geometry rocket design completed successfully!")
    except Exception as e:
        logger.error(f"Error creating rocket design: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
