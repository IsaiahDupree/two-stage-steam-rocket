#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Simple test script to verify FreeCAD API functionality.
"""

import sys
import os

print("Python version:", sys.version)
print("Script location:", os.path.abspath(__file__))

try:
    import FreeCAD
    print("FreeCAD imported successfully!")
    print("FreeCAD version:", FreeCAD.Version())
    
    # Try to create a document
    doc = FreeCAD.newDocument("TestDoc")
    print("Document created:", doc.Name)
    
    # Try to create a simple shape
    import Part
    box = Part.makeBox(10, 10, 10)
    print("Created box with volume:", box.Volume)
    
    print("FreeCAD API test SUCCESSFUL!")
except Exception as e:
    print("Error:", str(e))
    print("FreeCAD API test FAILED!")
