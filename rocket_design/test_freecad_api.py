#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Test script to verify FreeCAD API configuration.
Run this script with: freecadcmd test_freecad_api.py
"""

import os
import sys
import traceback

def check_freecad_api():
    """Test if FreeCAD API is properly configured."""
    print("FreeCAD API Configuration Test")
    print("============================")
    
    # Print Python version and environment
    print(f"Python version: {sys.version}")
    print(f"Python executable: {sys.executable}")
    print(f"Working directory: {os.getcwd()}")
    
    # Check system path
    print("\nSystem path:")
    for path in sys.path:
        print(f"  {path}")
    
    # Try to import FreeCAD
    try:
        import FreeCAD
        print("\nFreeCAD successfully imported!")
        print(f"FreeCAD version: {FreeCAD.Version()}")
        
        # Try basic FreeCAD operations
        doc = FreeCAD.newDocument("TestDocument")
        print(f"Created test document: {doc.Name}")
        
        # Try to import Part module
        import Part
        print("Part module successfully imported")
        
        # Create a simple cube
        cube = Part.makeBox(10, 10, 10)
        print(f"Created test cube: Volume = {cube.Volume} mm³")
        
        # Add to document
        obj = doc.addObject("Part::Feature", "TestCube")
        obj.Shape = cube
        print("Added cube to document")
        
        # Update document
        doc.recompute()
        print("Document recomputed successfully")
        
        # Try to save the document (uncommenting would actually create a file)
        # test_file = os.path.join(os.getcwd(), "test_output", "test_document.FCStd")
        # os.makedirs(os.path.dirname(test_file), exist_ok=True)
        # doc.saveAs(test_file)
        # print(f"Document saved to: {test_file}")
        
        print("\nAll FreeCAD API tests PASSED!")
        return True
    
    except ImportError as e:
        print(f"\nERROR: Could not import FreeCAD modules: {e}")
        print("Please check your FreeCAD installation and system path configuration.")
        return False
    
    except Exception as e:
        print(f"\nERROR: {str(e)}")
        print(traceback.format_exc())
        return False

if __name__ == "__main__":
    success = check_freecad_api()
    print("\nTest completed.")
    sys.exit(0 if success else 1)
