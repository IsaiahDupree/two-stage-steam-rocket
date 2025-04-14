#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Two-Stage Steam Rocket FreeCAD Model Generator

This script creates a detailed 3D model of the two-stage steam-powered rocket
described in the engineering report. It implements the exact specifications
including dimensions, materials, and structural features.
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
from FreeCAD import Base

print(f"Using FreeCAD version: {App.Version()}")

# Output directory setup
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(SCRIPT_DIR) if os.path.basename(SCRIPT_DIR) == "src" else SCRIPT_DIR
OUTPUT_DIR = os.path.join(PROJECT_DIR, "output")
MODELS_DIR = os.path.join(OUTPUT_DIR, "models")

# Create output directories
os.makedirs(MODELS_DIR, exist_ok=True)

# Rocket configuration from the design report
rocket_config = {
    # Overall dimensions
    "first_stage_length": 7200,        # mm (7.2 meters)
    "first_stage_diameter": 1200,      # mm (1.2 meters)
    "second_stage_length": 5200,       # mm (5.2 meters)
    "second_stage_diameter": 800,      # mm (0.8 meters)
    
    # Nosecone
    "nosecone_length": 1000,           # mm (1.0 meter) - part of second stage length
    "nosecone_shape": "ogive",         # ogive shape for better aerodynamics
    
    # Fins
    "fin_count": 4,
    "fin_height": 400,                 # mm
    "fin_root_chord": 800,             # mm
    "fin_tip_chord": 400,              # mm
    "fin_sweep": 300,                  # mm
    "fin_thickness": 10,               # mm
}

# Engine configuration from the design report
engine_config = {
    # First Stage Nozzle
    "first_stage_throat_diameter": 25,    # mm
    "first_stage_exit_diameter": 75,      # mm
    "first_stage_nozzle_length": 200,     # mm
    
    # Second Stage Nozzle
    "second_stage_throat_diameter": 15,    # mm
    "second_stage_exit_diameter": 60,      # mm
    "second_stage_nozzle_length": 150,     # mm
    
    # Pressure vessels
    "first_stage_vessel_length": 600,      # mm (0.6 m)
    "first_stage_vessel_diameter": 300,    # mm (0.3 m)
    "first_stage_wall_thickness": 6,       # mm
    
    "second_stage_vessel_length": 400,     # mm (0.4 m)
    "second_stage_vessel_diameter": 200,   # mm (0.2 m)
    "second_stage_wall_thickness": 2.5,    # mm
}

def create_ogive_nosecone(length, diameter, doc, name="NoseCone"):
    """
    Create an ogive-shaped nosecone
    """
    # Ogive nosecone equation: y = radius * sqrt(1 - (x/length)²)
    radius = diameter / 2
    points = []
    num_points = 30
    
    for i in range(num_points+1):
        x = length * (i / num_points)
        # Ogive shape using square root function
        y = radius * math.sqrt(1 - ((x - length) / length)**2)
        points.append(Base.Vector(0, y, x))
    
    # Add center point at base
    points.append(Base.Vector(0, 0, 0))
    
    # Create a wire
    wire = Part.makePolygon(points)
    
    # Create face by rotating around Z axis
    face = wire.makeRevolution(Base.Vector(0, 0, 0), Base.Vector(0, 0, 1), 360)
    
    # Create solid
    solid = Part.makeSolid(face)
    
    # Add to document
    obj = doc.addObject("Part::Feature", name)
    obj.Shape = solid
    
    return obj

def create_fin(root_chord, tip_chord, height, sweep, thickness, doc, name="Fin"):
    """
    Create a swept fin with the given dimensions
    """
    # Create points for the fin profile
    p1 = Base.Vector(0, 0, 0)                     # Root leading edge
    p2 = Base.Vector(root_chord, 0, 0)            # Root trailing edge
    p3 = Base.Vector(root_chord-sweep, height, 0) # Tip trailing edge
    p4 = Base.Vector(root_chord-sweep-tip_chord, height, 0) # Tip leading edge
    
    # Create a face from the points
    wire = Part.makePolygon([p1, p2, p3, p4, p1])
    face = Part.Face(wire)
    
    # Extrude the face to create a solid
    fin_solid = face.extrude(Base.Vector(0, 0, thickness))
    
    # Add to document
    obj = doc.addObject("Part::Feature", name)
    obj.Shape = fin_solid
    
    return obj

def create_nozzle(throat_diameter, exit_diameter, length, doc, name="Nozzle"):
    """
    Create a rocket engine nozzle
    """
    # Create the nozzle as a truncated cone
    nozzle = Part.makeCone(throat_diameter/2, exit_diameter/2, length)
    
    # Add to document
    obj = doc.addObject("Part::Feature", name)
    obj.Shape = nozzle
    
    return obj

def create_pressure_vessel(diameter, length, wall_thickness, doc, name="PressureVessel"):
    """
    Create a pressure vessel with the specified wall thickness
    """
    # Create outer cylinder
    outer = Part.makeCylinder(diameter/2, length)
    
    # Create inner cylinder for hollowing
    inner_diameter = diameter - 2*wall_thickness
    inner = Part.makeCylinder(inner_diameter/2, length - wall_thickness)
    inner.translate(Base.Vector(0, 0, wall_thickness))
    
    # Cut inner from outer
    vessel = outer.cut(inner)
    
    # Add to document
    obj = doc.addObject("Part::Feature", name)
    obj.Shape = vessel
    
    return obj

def create_stage_separation_system(diameter, height, doc, name="StageSeparation"):
    """
    Create a simplified stage separation system
    """
    # Create main cylinder for the separation ring
    ring_thickness = 20  # mm
    outer = Part.makeCylinder(diameter/2, height)
    inner = Part.makeCylinder(diameter/2 - ring_thickness, height)
    ring = outer.cut(inner)
    
    # Add bolt details along the circumference
    bolt_count = 12
    bolt_diameter = 10
    bolt_height = 15
    bolt_radius = diameter/2 - ring_thickness/2
    
    bolts = []
    for i in range(bolt_count):
        angle = 360 / bolt_count * i
        angle_rad = math.radians(angle)
        x = bolt_radius * math.cos(angle_rad)
        y = bolt_radius * math.sin(angle_rad)
        
        bolt = Part.makeCylinder(bolt_diameter/2, bolt_height, 
                                Base.Vector(x, y, -bolt_height/2), 
                                Base.Vector(0, 0, 1))
        bolts.append(bolt)
    
    # Combine all bolts with the ring
    for bolt in bolts:
        ring = ring.fuse(bolt)
    
    # Add to document
    obj = doc.addObject("Part::Feature", name)
    obj.Shape = ring
    
    return obj

def create_steam_rocket_model():
    """Create the detailed two-stage steam rocket 3D model"""
    print("Creating two-stage steam rocket model...")
    
    # Create a new document
    doc = App.newDocument("TwoStageRocket")
    
    # --- Create First Stage ---
    print("Creating first stage...")
    first_stage = Part.makeCylinder(
        rocket_config["first_stage_diameter"]/2, 
        rocket_config["first_stage_length"]
    )
    first_stage_obj = doc.addObject("Part::Feature", "FirstStageBody")
    first_stage_obj.Shape = first_stage
    
    # --- Create Second Stage ---
    print("Creating second stage...")
    second_stage = Part.makeCylinder(
        rocket_config["second_stage_diameter"]/2, 
        rocket_config["second_stage_length"] - rocket_config["nosecone_length"],
        Base.Vector(0, 0, rocket_config["first_stage_length"]),
        Base.Vector(0, 0, 1)
    )
    second_stage_obj = doc.addObject("Part::Feature", "SecondStageBody")
    second_stage_obj.Shape = second_stage
    
    # --- Create Nose Cone ---
    print("Creating nose cone...")
    nose_cone = create_ogive_nosecone(
        rocket_config["nosecone_length"],
        rocket_config["second_stage_diameter"],
        doc,
        "NoseCone"
    )
    # Position at the top of the second stage
    nose_cone.Placement.Base = Base.Vector(
        0, 0, 
        rocket_config["first_stage_length"] + 
        rocket_config["second_stage_length"] - 
        rocket_config["nosecone_length"]
    )
    
    # --- Create Fins ---
    print(f"Creating {rocket_config['fin_count']} fins...")
    fin_base_z = rocket_config["first_stage_length"] * 0.1
    for i in range(rocket_config["fin_count"]):
        angle = 360 / rocket_config["fin_count"] * i
        fin = create_fin(
            rocket_config["fin_root_chord"],
            rocket_config["fin_tip_chord"],
            rocket_config["fin_height"],
            rocket_config["fin_sweep"],
            rocket_config["fin_thickness"],
            doc,
            f"Fin_{i+1}"
        )
        
        # Rotate around Z axis
        fin.Placement.Rotation = App.Rotation(App.Vector(0, 0, 1), angle)
        
        # Position at the correct height and radius
        radial_pos = rocket_config["first_stage_diameter"] / 2
        fin.Placement.Base.z = fin_base_z
        fin.Placement.Base.x = -rocket_config["fin_thickness"] / 2
    
    # --- Create First Stage Engine Nozzle ---
    print("Creating first stage engine nozzle...")
    first_nozzle = create_nozzle(
        engine_config["first_stage_throat_diameter"],
        engine_config["first_stage_exit_diameter"],
        engine_config["first_stage_nozzle_length"],
        doc,
        "FirstStageNozzle"
    )
    # Position at the bottom of the first stage
    first_nozzle.Placement.Base = Base.Vector(0, 0, 0)
    first_nozzle.Placement.Rotation = App.Rotation(Base.Vector(1, 0, 0), 180)
    
    # --- Create Second Stage Engine Nozzle ---
    print("Creating second stage engine nozzle...")
    second_nozzle = create_nozzle(
        engine_config["second_stage_throat_diameter"],
        engine_config["second_stage_exit_diameter"],
        engine_config["second_stage_nozzle_length"],
        doc,
        "SecondStageNozzle"
    )
    # Position at the bottom of the second stage
    second_nozzle.Placement.Base = Base.Vector(0, 0, rocket_config["first_stage_length"])
    second_nozzle.Placement.Rotation = App.Rotation(Base.Vector(1, 0, 0), 180)
    
    # --- Create First Stage Pressure Vessel ---
    print("Creating first stage pressure vessel...")
    first_vessel = create_pressure_vessel(
        engine_config["first_stage_vessel_diameter"],
        engine_config["first_stage_vessel_length"],
        engine_config["first_stage_wall_thickness"],
        doc,
        "FirstStagePressureVessel"
    )
    # Position inside the first stage, centered
    first_vessel_z = rocket_config["first_stage_length"] / 2 - engine_config["first_stage_vessel_length"] / 2
    first_vessel.Placement.Base = Base.Vector(0, 0, first_vessel_z)
    
    # --- Create Second Stage Pressure Vessel ---
    print("Creating second stage pressure vessel...")
    second_vessel = create_pressure_vessel(
        engine_config["second_stage_vessel_diameter"],
        engine_config["second_stage_vessel_length"],
        engine_config["second_stage_wall_thickness"],
        doc,
        "SecondStagePressureVessel"
    )
    # Position inside the second stage, centered
    second_vessel_z = rocket_config["first_stage_length"] + (rocket_config["second_stage_length"] - rocket_config["nosecone_length"]) / 2 - engine_config["second_stage_vessel_length"] / 2
    second_vessel.Placement.Base = Base.Vector(0, 0, second_vessel_z)
    
    # --- Create Stage Separation System ---
    print("Creating stage separation system...")
    separation = create_stage_separation_system(
        rocket_config["second_stage_diameter"],
        50,  # height in mm
        doc,
        "StageSeparationSystem"
    )
    # Position at the interface between stages
    separation.Placement.Base = Base.Vector(0, 0, rocket_config["first_stage_length"] - 25)
    
    # Refresh the document
    doc.recompute()
    
    # Save the document
    fcstd_file = os.path.join(MODELS_DIR, "two_stage_steam_rocket.FCStd")
    doc.saveAs(fcstd_file)
    print(f"Saved FreeCAD document to: {fcstd_file}")
    
    # Export to STEP format
    try:
        step_file = os.path.join(MODELS_DIR, "two_stage_steam_rocket.step")
        
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
        stl_file = os.path.join(MODELS_DIR, "two_stage_steam_rocket.stl")
        
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
        except Exception as e:
            # Method 2: Export individual meshes
            print(f"Could not export combined STL, using individual exports: {e}")
            for i, obj in enumerate(doc.Objects):
                if hasattr(obj, "Shape"):
                    obj_stl = os.path.join(MODELS_DIR, f"{obj.Name}.stl")
                    obj.Shape.exportStl(obj_stl)
            print(f"Exported individual STL files to: {MODELS_DIR}")
    except Exception as e:
        print(f"Error exporting STL file: {e}")
    
    return doc

def main():
    """Main function"""
    try:
        print("Starting Steam Rocket 3D model generation...")
        doc = create_steam_rocket_model()
        print("Steam Rocket model created successfully!")
        return 0
    except Exception as e:
        print(f"Error creating rocket model: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
