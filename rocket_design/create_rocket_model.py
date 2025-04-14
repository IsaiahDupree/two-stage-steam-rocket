#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Simplified script to create a two-stage rocket model with FreeCAD.
This version avoids GUI dependencies for headless operation.
"""

import os
import sys
import math

# Add FreeCAD to Python path if not already there
try:
    import FreeCAD
except ImportError:
    # Check common installation locations
    freecad_paths = [
        r"C:\Program Files\FreeCAD 1.0\bin",
        r"C:\Program Files\FreeCAD 0.20\bin",
        r"C:\Program Files\FreeCAD 0.19\bin",
        r"C:\Program Files\FreeCAD\bin"
    ]
    
    for path in freecad_paths:
        if os.path.exists(path):
            sys.path.append(path)
            print(f"Added FreeCAD path: {path}")
            break
    else:
        print("Error: FreeCAD path not found.")
        sys.exit(1)

# Import FreeCAD modules (no GUI)
import FreeCAD as App
import Part

print(f"Using FreeCAD version: {App.Version()}")

# Output directory setup
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(SCRIPT_DIR) if os.path.basename(SCRIPT_DIR) == "src" else SCRIPT_DIR
OUTPUT_DIR = os.path.join(PROJECT_DIR, "output")
MODELS_DIR = os.path.join(OUTPUT_DIR, "models")

# Create output directories
os.makedirs(MODELS_DIR, exist_ok=True)

# Rocket configuration
rocket_config = {
    "total_length": 5000,      # mm
    "max_diameter": 500,       # mm
    "first_stage_length_ratio": 0.6,
    "nose_cone_length_ratio": 0.15,
    "fin_count": 4
}

# Engine configuration
engine_config = {
    "throat_diameter": 30,     # mm
    "exit_diameter": 150,      # mm
    "length": 300,             # mm
}

def create_rocket_model():
    """Create the rocket 3D model and save it to output files."""
    print("Creating two-stage rocket model...")
    
    # Create a new document
    doc = App.newDocument("TwoStageRocket")
    
    # Calculate dimensions
    total_length = rocket_config["total_length"]
    max_diameter = rocket_config["max_diameter"]
    first_stage_length = total_length * rocket_config["first_stage_length_ratio"]
    second_stage_length = total_length * (1 - rocket_config["first_stage_length_ratio"] - rocket_config["nose_cone_length_ratio"])
    nose_cone_length = total_length * rocket_config["nose_cone_length_ratio"]
    fin_count = rocket_config["fin_count"]
    
    # Create first stage
    print("Creating first stage...")
    first_stage = Part.makeCylinder(max_diameter/2, first_stage_length, 
                                    App.Vector(0, 0, 0), App.Vector(0, 0, 1))
    first_stage_obj = doc.addObject("Part::Feature", "FirstStage")
    first_stage_obj.Shape = first_stage
    
    # Create second stage (slightly smaller diameter)
    print("Creating second stage...")
    second_stage_diameter = max_diameter * 0.9
    second_stage = Part.makeCylinder(second_stage_diameter/2, second_stage_length,
                                     App.Vector(0, 0, first_stage_length),
                                     App.Vector(0, 0, 1))
    second_stage_obj = doc.addObject("Part::Feature", "SecondStage")
    second_stage_obj.Shape = second_stage
    
    # Create nose cone
    print("Creating nose cone...")
    nose_cone = Part.makeCone(second_stage_diameter/2, 0, nose_cone_length,
                              App.Vector(0, 0, first_stage_length + second_stage_length),
                              App.Vector(0, 0, 1))
    nose_cone_obj = doc.addObject("Part::Feature", "NoseCone")
    nose_cone_obj.Shape = nose_cone
    
    # Create fins
    print(f"Creating {fin_count} fins...")
    fin_height = max_diameter * 0.8
    fin_length = first_stage_length * 0.3
    fin_thickness = 10  # mm
    
    for i in range(fin_count):
        angle = 360 / fin_count * i
        angle_rad = math.radians(angle)
        
        # Create fin shape
        fin = Part.makeBox(fin_thickness, fin_height, fin_length)
        
        # Rotate and position fin
        fin.rotate(App.Vector(0, 0, 0), App.Vector(0, 0, 1), angle)
        
        # Position at correct radius and height
        radius_offset = (max_diameter / 2) - (fin_thickness / 2)
        fin.translate(App.Vector(
            math.cos(angle_rad) * radius_offset,
            math.sin(angle_rad) * radius_offset,
            first_stage_length * 0.1
        ))
        
        # Add to document
        fin_obj = doc.addObject("Part::Feature", f"Fin_{i+1}")
        fin_obj.Shape = fin
    
    # Create engine nozzle
    print("Creating engine nozzle...")
    throat_d = engine_config["throat_diameter"]
    exit_d = engine_config["exit_diameter"]
    nozzle_length = engine_config["length"]
    
    # Create nozzle as a truncated cone
    nozzle = Part.makeCone(throat_d/2, exit_d/2, nozzle_length,
                          App.Vector(0, 0, -nozzle_length),
                          App.Vector(0, 0, 1))
    nozzle_obj = doc.addObject("Part::Feature", "Nozzle")
    nozzle_obj.Shape = nozzle
    
    # Refresh the document
    doc.recompute()
    
    # Save the document
    fcstd_file = os.path.join(MODELS_DIR, "two_stage_rocket.FCStd")
    doc.saveAs(fcstd_file)
    print(f"Saved FreeCAD document to: {fcstd_file}")
    
    # Export to STEP format
    try:
        step_file = os.path.join(MODELS_DIR, "two_stage_rocket.step")
        
        # Method 1: Using Import module
        try:
            import Import
            Import.export([obj for obj in doc.Objects if hasattr(obj, "Shape")], step_file)
            print(f"Exported STEP file to: {step_file}")
        except:
            # Method 2: Using Part module directly
            compound = Part.Compound([obj.Shape for obj in doc.Objects if hasattr(obj, "Shape")])
            compound.exportStep(step_file)
            print(f"Exported STEP file to: {step_file} (using Part module)")
    except Exception as e:
        print(f"Error exporting STEP file: {e}")
    
    # Export to STL format
    try:
        stl_file = os.path.join(MODELS_DIR, "two_stage_rocket.stl")
        
        # Method 1: Using Mesh module
        try:
            import Mesh
            combined_mesh = Mesh.Mesh()
            for obj in doc.Objects:
                if hasattr(obj, "Shape"):
                    mesh = Mesh.Mesh(obj.Shape.tessellate(0.1))
                    combined_mesh.addMesh(mesh)
            combined_mesh.write(stl_file)
            print(f"Exported STL file to: {stl_file}")
        except:
            # Method 2: Export individual meshes
            for i, obj in enumerate(doc.Objects):
                if hasattr(obj, "Shape"):
                    obj_stl = os.path.join(MODELS_DIR, f"{obj.Name}.stl")
                    obj.Shape.exportStl(obj_stl)
            print(f"Exported individual STL files to: {MODELS_DIR}")
    except Exception as e:
        print(f"Error exporting STL file: {e}")
    
    return doc

if __name__ == "__main__":
    try:
        doc = create_rocket_model()
        print("Rocket model created successfully!")
    except Exception as e:
        print(f"Error creating rocket model: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
