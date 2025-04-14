#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Debug script to test FreeCAD integration and diagnose issues.
"""

import os
import sys
import traceback

# Create a log file
log_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "debug_log.txt")
with open(log_file, 'w') as f:
    f.write("FreeCAD Debug Log\n")
    f.write("===============\n\n")
    f.write(f"Python version: {sys.version}\n")
    f.write(f"Python executable: {sys.executable}\n")
    f.write(f"Script path: {__file__}\n\n")
    f.write("System path:\n")
    for p in sys.path:
        f.write(f"  {p}\n")
    f.write("\n")

# Try to import FreeCAD
try:
    # Try to add FreeCAD to path if not there
    freecad_path = "C:/Program Files/FreeCAD 1.0/bin"
    if os.path.exists(freecad_path) and freecad_path not in sys.path:
        sys.path.append(freecad_path)
        with open(log_file, 'a') as f:
            f.write(f"Added FreeCAD path: {freecad_path}\n")
    
    # Try to import FreeCAD
    import FreeCAD
    with open(log_file, 'a') as f:
        f.write(f"Successfully imported FreeCAD module\n")
        f.write(f"FreeCAD version: {FreeCAD.Version}\n")
    
    # Try to create a document
    doc = FreeCAD.newDocument("TestDocument")
    with open(log_file, 'a') as f:
        f.write(f"Successfully created new document: {doc.Name}\n")
    
    # Try to import Part module
    import Part
    with open(log_file, 'a') as f:
        f.write(f"Successfully imported Part module\n")
    
    # Create a simple cylinder
    cylinder = Part.makeCylinder(10, 30)
    with open(log_file, 'a') as f:
        f.write(f"Successfully created cylinder\n")
    
    # Add to document
    obj = doc.addObject("Part::Feature", "TestCylinder")
    obj.Shape = cylinder
    with open(log_file, 'a') as f:
        f.write(f"Successfully added cylinder to document\n")
    
    # Update the document
    doc.recompute()
    with open(log_file, 'a') as f:
        f.write(f"Successfully recomputed document\n")
    
    # Try to create output directory
    output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")
    os.makedirs(output_dir, exist_ok=True)
    with open(log_file, 'a') as f:
        f.write(f"Created output directory: {output_dir}\n")
    
    # Try to save the FreeCAD document
    fcstd_file = os.path.join(output_dir, "test_cylinder.FCStd")
    doc.saveAs(fcstd_file)
    with open(log_file, 'a') as f:
        f.write(f"Saved FreeCAD document to: {fcstd_file}\n")
    
    # Try to export to STEP
    step_file = os.path.join(output_dir, "test_cylinder.step")
    import Import
    Import.export([obj], step_file)
    with open(log_file, 'a') as f:
        f.write(f"Exported to STEP file: {step_file}\n")
    
    # Try to create a mesh and export to STL
    stl_file = os.path.join(output_dir, "test_cylinder.stl")
    import Mesh
    mesh = Mesh.Mesh(cylinder.tessellate(0.1))
    mesh.write(stl_file)
    with open(log_file, 'a') as f:
        f.write(f"Exported to STL file: {stl_file}\n")
    
    with open(log_file, 'a') as f:
        f.write("\nDebug test completed successfully.\n")

except Exception as e:
    with open(log_file, 'a') as f:
        f.write(f"\nERROR: {str(e)}\n")
        f.write(traceback.format_exc())

print(f"Debug completed. See log file: {log_file}")
