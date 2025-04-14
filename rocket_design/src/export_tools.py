#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Export tools module for saving FreeCAD models to various file formats.
This module handles exporting to formats like STEP, STL, DXF, and others required for the project.
"""

import os
import FreeCAD as App
import Import
import ImportGui
import Mesh

class ModelExporter:
    """Class for exporting FreeCAD models to various file formats."""
    
    def __init__(self, doc):
        """
        Initialize the model exporter with a FreeCAD document.
        
        Args:
            doc: FreeCAD document containing models to export
        """
        self.doc = doc
    
    def export_step(self, filename):
        """
        Export the entire document to STEP format.
        
        Args:
            filename: Path to save the STEP file
        """
        # Ensure the directory exists
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        
        # Export to STEP format
        Import.export(self.doc.Objects, filename)
        
        print(f"Exported STEP file to: {filename}")
    
    def export_stl(self, filename):
        """
        Export the entire document to STL format.
        
        Args:
            filename: Path to save the STL file
        """
        # Ensure the directory exists
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        
        # Get a compound of all shapes
        all_shapes = []
        for obj in self.doc.Objects:
            if hasattr(obj, "Shape"):
                all_shapes.append(obj.Shape)
        
        if not all_shapes:
            print("Warning: No shapes found to export to STL")
            return
        
        # Create a mesh from all shapes
        mesh = Mesh.Mesh()
        for shape in all_shapes:
            mesh_from_shape = Mesh.Mesh(shape.tessellate(0.1))
            mesh.addMesh(mesh_from_shape)
        
        # Export to STL
        mesh.write(filename)
        
        print(f"Exported STL file to: {filename}")
    
    def export_dxf(self, filename, view_direction=(0, 0, 1)):
        """
        Export a 2D projection of the model to DXF format.
        
        Args:
            filename: Path to save the DXF file
            view_direction: Vector defining projection direction
        """
        # Ensure the directory exists
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        
        # Create a new document for the projection
        projection_doc = App.newDocument("TempProjection")
        
        # Create projection of each object
        for obj in self.doc.Objects:
            if hasattr(obj, "Shape"):
                # Create a projection view
                projected_shape = self._project_shape(obj.Shape, view_direction)
                if projected_shape:
                    projected_obj = projection_doc.addObject("Part::Feature", f"Projection_{obj.Name}")
                    projected_obj.Shape = projected_shape
        
        projection_doc.recompute()
        
        # Export to DXF
        ImportGui.export(projection_doc.Objects, filename)
        
        # Close temporary document
        App.closeDocument(projection_doc.Name)
        
        print(f"Exported DXF file to: {filename}")
    
    def _project_shape(self, shape, direction):
        """
        Project a 3D shape onto a 2D plane.
        
        Args:
            shape: FreeCAD shape to project
            direction: Direction vector for projection
        
        Returns:
            Projected shape or None if projection failed
        """
        try:
            # Convert the direction vector to a FreeCAD.Vector
            if not isinstance(direction, App.Vector):
                direction = App.Vector(*direction)
            
            # Create a projection
            projection = shape.project(direction)
            return projection
        except Exception as e:
            print(f"Error projecting shape: {e}")
            return None
    
    def export_all_formats(self, base_filename):
        """
        Export the model to multiple formats at once.
        
        Args:
            base_filename: Base path/name for the exported files (without extension)
        """
        # Export to various formats
        self.export_step(f"{base_filename}.step")
        self.export_stl(f"{base_filename}.stl")
        
        # Export multiple DXF views
        views = {
            "top": (0, 0, 1),
            "front": (0, -1, 0),
            "side": (1, 0, 0)
        }
        
        for view_name, direction in views.items():
            self.export_dxf(f"{base_filename}_{view_name}.dxf", direction)
        
        # Save the FreeCAD document
        self.doc.saveAs(f"{base_filename}.FCStd")
        
        print(f"Exported model to multiple formats with base name: {base_filename}")
    
    def generate_drawings(self, output_dir):
        """
        Generate technical drawings of the rocket design.
        
        Args:
            output_dir: Directory to save drawing files
        """
        # Ensure the directory exists
        os.makedirs(output_dir, exist_ok=True)
        
        # In a real implementation, this would use FreeCAD's drawing workbench
        # or TechDraw workbench to create detailed engineering drawings
        
        # For this example, we'll just export DXF views
        base_filename = os.path.join(output_dir, "rocket_drawing")
        
        views = {
            "top": (0, 0, 1),
            "front": (0, -1, 0),
            "side": (1, 0, 0),
            "isometric": (1, 1, 1)
        }
        
        for view_name, direction in views.items():
            self.export_dxf(f"{base_filename}_{view_name}.dxf", direction)
        
        print(f"Generated technical drawings in: {output_dir}")

    def export_bom(self, filename):
        """
        Export a Bill of Materials (BOM) for the rocket design.
        
        Args:
            filename: Path to save the BOM file
        """
        # Ensure the directory exists
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        
        # Prepare BOM data
        bom_data = []
        
        for obj in self.doc.Objects:
            # Skip objects without proper properties
            if not hasattr(obj, "Label"):
                continue
                
            # Get basic properties
            item = {
                "name": obj.Label,
                "type": obj.TypeId
            }
            
            # Get volume and mass if available
            if hasattr(obj, "Shape"):
                try:
                    item["volume"] = obj.Shape.Volume  # mm³
                    
                    # Estimate mass based on density (if available)
                    if hasattr(obj, "Material"):
                        # Density lookup (kg/m³)
                        densities = {
                            "stainless_steel": 7900,
                            "aluminum": 2700,
                            "titanium": 4500,
                            "plastic": 1200,
                            "carbon_fiber": 1600
                        }
                        
                        # Get material (default to aluminum)
                        material = getattr(obj, "Material", "aluminum")
                        density = densities.get(material, 2700)  # kg/m³
                        
                        # Calculate mass (kg) - convert volume from mm³ to m³
                        item["mass"] = density * (item["volume"] / 1e9)
                    else:
                        # Default to aluminum if no material specified
                        item["mass"] = 2700 * (item["volume"] / 1e9)
                except:
                    pass
            
            bom_data.append(item)
        
        # Write BOM to CSV
        with open(filename, 'w') as f:
            # Write header
            f.write("Component,Type,Volume (mm³),Mass (kg)\n")
            
            # Write each item
            for item in bom_data:
                volume = item.get("volume", "N/A")
                mass = item.get("mass", "N/A")
                
                if volume != "N/A":
                    volume = f"{volume:.2f}"
                
                if mass != "N/A":
                    mass = f"{mass:.3f}"
                
                f.write(f"{item['name']},{item['type']},{volume},{mass}\n")
        
        print(f"Exported Bill of Materials to: {filename}")
