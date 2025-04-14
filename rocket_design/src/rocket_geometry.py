#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Rocket geometry module for creating the structural components of the two-stage rocket.
"""

import math
import FreeCAD as App
import Part
import Draft
from FreeCAD import Vector

class RocketBuilder:
    """Class for building the geometric components of a two-stage rocket."""
    
    def __init__(self, doc, config):
        """
        Initialize the rocket builder with document and configuration.
        
        Args:
            doc: FreeCAD document to add objects to
            config: Dictionary containing rocket geometry parameters
        """
        self.doc = doc
        self.config = config
        
        # Extract common parameters
        self.total_length = config["total_length"]
        self.max_diameter = config["max_diameter"]
        self.first_stage_length = self.total_length * config["first_stage_length_ratio"]
        self.second_stage_length = self.total_length * (1 - config["first_stage_length_ratio"] - config["nose_cone_length_ratio"])
        self.nose_cone_length = self.total_length * config["nose_cone_length_ratio"]
        self.fin_count = config["fin_count"]
        
        # Calculate positions
        self.first_stage_position = Vector(0, 0, 0)
        self.second_stage_position = Vector(0, 0, self.first_stage_length)
        self.nose_cone_position = Vector(0, 0, self.first_stage_length + self.second_stage_length)
        
    def create_first_stage(self):
        """Create the first stage of the rocket."""
        # Create a cylinder for the first stage body
        cylinder = Part.makeCylinder(
            self.max_diameter / 2,
            self.first_stage_length,
            self.first_stage_position,
            Vector(0, 0, 1)
        )
        
        # Create a FreeCAD object from the shape
        obj = self.doc.addObject("Part::Feature", "FirstStage")
        obj.Shape = cylinder
        obj.Label = "First Stage Body"
        
        # Set appearance properties
        obj.ViewObject.ShapeColor = (0.8, 0.8, 0.8)  # Light gray
        
        self.doc.recompute()
        return obj
    
    def create_second_stage(self):
        """Create the second stage of the rocket."""
        # Create a cylinder with slightly smaller diameter for the second stage
        second_stage_diameter = self.max_diameter * 0.9  # 90% of first stage diameter
        
        cylinder = Part.makeCylinder(
            second_stage_diameter / 2,
            self.second_stage_length,
            self.second_stage_position,
            Vector(0, 0, 1)
        )
        
        obj = self.doc.addObject("Part::Feature", "SecondStage")
        obj.Shape = cylinder
        obj.Label = "Second Stage Body"
        
        # Set appearance properties
        obj.ViewObject.ShapeColor = (0.9, 0.9, 0.9)  # Lighter gray
        
        self.doc.recompute()
        return obj
    
    def create_nose_cone(self):
        """Create the rocket nose cone."""
        # Create a cone for the nose
        radius = self.max_diameter * 0.9 / 2  # Match second stage diameter
        
        # Create a cone shape
        cone = Part.makeCone(
            radius, 0,  # Base radius, top radius
            self.nose_cone_length,
            self.nose_cone_position,
            Vector(0, 0, 1)
        )
        
        obj = self.doc.addObject("Part::Feature", "NoseCone")
        obj.Shape = cone
        obj.Label = "Nose Cone"
        
        # Set appearance properties
        obj.ViewObject.ShapeColor = (0.9, 0.9, 0.9)  # Lighter gray
        
        self.doc.recompute()
        return obj
    
    def create_fins(self):
        """Create rocket fins for the first stage."""
        fin_objects = []
        
        # Fin dimensions
        fin_height = self.max_diameter * 0.8  # Fin height (radial extension)
        fin_length = self.first_stage_length * 0.3  # Fin length along rocket body
        fin_thickness = 10  # mm
        
        # Position fins at the bottom of the first stage
        fin_z_position = self.first_stage_length * 0.1  # 10% up from the bottom
        
        for i in range(self.fin_count):
            # Calculate angle for this fin
            angle = 360 / self.fin_count * i
            angle_rad = math.radians(angle)
            
            # Create a box for the fin
            fin_shape = Part.makeBox(
                fin_thickness,
                fin_height,
                fin_length
            )
            
            # Rotate and position the fin
            rotation = App.Rotation(App.Vector(0, 0, 1), angle)
            fin_shape.rotate(Vector(0, 0, 0), Vector(0, 0, 1), angle)
            
            # Position fin at correct distance from center and height
            radius_vector = Vector(
                math.cos(angle_rad) * (self.max_diameter / 2 - fin_thickness / 2),
                math.sin(angle_rad) * (self.max_diameter / 2 - fin_thickness / 2),
                fin_z_position
            )
            fin_shape.translate(radius_vector)
            
            # Create FreeCAD object
            fin_name = f"Fin_{i+1}"
            fin_obj = self.doc.addObject("Part::Feature", fin_name)
            fin_obj.Shape = fin_shape
            fin_obj.Label = f"Fin {i+1}"
            
            # Set appearance properties
            fin_obj.ViewObject.ShapeColor = (0.7, 0.7, 0.7)  # Darker gray
            
            fin_objects.append(fin_obj)
        
        self.doc.recompute()
        return fin_objects
    
    def create_stage_separation_mechanism(self):
        """Create the mechanism that connects and separates the two stages."""
        # Create a cylindrical ring at the top of the first stage
        
        # Dimensions for separation ring
        outer_radius = self.max_diameter / 2
        inner_radius = self.max_diameter * 0.8 / 2
        height = 50  # mm
        
        # Create a tube (hollow cylinder)
        outer_cylinder = Part.makeCylinder(outer_radius, height, 
                                           Vector(0, 0, self.first_stage_length - height),
                                           Vector(0, 0, 1))
        inner_cylinder = Part.makeCylinder(inner_radius, height, 
                                           Vector(0, 0, self.first_stage_length - height),
                                           Vector(0, 0, 1))
        
        separation_ring = outer_cylinder.cut(inner_cylinder)
        
        # Add small separation charges (just for visualization)
        charge_count = 4
        charge_radius = 10
        charge_height = 20
        charges = []
        
        for i in range(charge_count):
            angle = 360 / charge_count * i
            angle_rad = math.radians(angle)
            position = Vector(
                math.cos(angle_rad) * (outer_radius + inner_radius) / 2,
                math.sin(angle_rad) * (outer_radius + inner_radius) / 2,
                self.first_stage_length - height/2 - charge_height/2
            )
            
            charge = Part.makeCylinder(charge_radius, charge_height, position, Vector(0, 0, 1))
            charges.append(charge)
        
        # Add charges to separation ring
        for charge in charges:
            separation_ring = separation_ring.fuse(charge)
        
        # Create FreeCAD object
        sep_obj = self.doc.addObject("Part::Feature", "StageSeparation")
        sep_obj.Shape = separation_ring
        sep_obj.Label = "Stage Separation Mechanism"
        
        # Set appearance properties
        sep_obj.ViewObject.ShapeColor = (0.6, 0.6, 0.8)  # Bluish gray
        
        self.doc.recompute()
        return sep_obj
