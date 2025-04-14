#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Engine design module for creating and analyzing rocket engine components.
This includes pressure vessels and nozzles for a steam-based propulsion system.
"""

import math
import os
import numpy as np
import FreeCAD as App
import Part
from FreeCAD import Vector

class PressureVessel:
    """Class for creating pressure vessel models and performing stress analysis."""
    
    def __init__(self, doc, config):
        """
        Initialize the pressure vessel with document and configuration.
        
        Args:
            doc: FreeCAD document to add objects to
            config: Dictionary containing pressure vessel parameters
        """
        self.doc = doc
        self.config = config
        
        # Extract parameters
        self.design_pressure = config["design_pressure"]  # MPa
        self.safety_factor = config["safety_factor"]
        self.material = config["material"]
        self.thickness = config["thickness"]  # mm
        self.volume = config["volume"]  # m³
        
        # Material properties (MPa)
        self.material_properties = {
            "stainless_steel": {
                "yield_strength": 205,
                "tensile_strength": 515,
                "density": 7900,  # kg/m³
                "elastic_modulus": 193000,  # MPa
                "poisson_ratio": 0.3
            },
            "aluminum": {
                "yield_strength": 95,
                "tensile_strength": 110,
                "density": 2700,  # kg/m³
                "elastic_modulus": 68000,  # MPa
                "poisson_ratio": 0.33
            },
            "titanium": {
                "yield_strength": 825,
                "tensile_strength": 900,
                "density": 4500,  # kg/m³
                "elastic_modulus": 114000,  # MPa
                "poisson_ratio": 0.34
            }
        }
    
    def create_model(self):
        """Create a 3D model of the pressure vessel."""
        # Calculate dimensions for a cylindrical pressure vessel with the given volume
        # Volume of a cylinder: V = π * r² * h
        # We'll set height = 3 * diameter for a reasonable aspect ratio
        
        # Calculate inner radius (mm) for a cylinder with 3:1 height-to-diameter ratio
        ratio = 3
        inner_diameter = math.pow(self.volume * 4 / (math.pi * ratio), 1/3) * 1000  # Convert m to mm
        inner_radius = inner_diameter / 2
        height = inner_diameter * ratio
        
        # Create outer and inner cylinders
        outer_radius = inner_radius + self.thickness
        
        # Create vessel body (cylinder with hemispherical ends)
        # Main cylinder
        cylinder = Part.makeCylinder(
            outer_radius,
            height,
            Vector(0, 0, 0),
            Vector(0, 0, 1)
        )
        
        # Hemispherical ends
        bottom_hemisphere = Part.makeSphere(
            outer_radius,
            Vector(0, 0, 0),
            Vector(0, 0, 1),
            0, 180, 0, 360
        )
        
        top_hemisphere = Part.makeSphere(
            outer_radius,
            Vector(0, 0, height),
            Vector(0, 0, 1),
            0, 180, 0, 360
        )
        
        # Combine parts
        pressure_vessel_outer = cylinder.fuse(bottom_hemisphere)
        pressure_vessel_outer = pressure_vessel_outer.fuse(top_hemisphere)
        
        # Create inner hollow (subtract from outer shape)
        inner_cylinder = Part.makeCylinder(
            inner_radius,
            height,
            Vector(0, 0, 0),
            Vector(0, 0, 1)
        )
        
        inner_bottom_hemisphere = Part.makeSphere(
            inner_radius,
            Vector(0, 0, 0),
            Vector(0, 0, 1),
            0, 180, 0, 360
        )
        
        inner_top_hemisphere = Part.makeSphere(
            inner_radius,
            Vector(0, 0, height),
            Vector(0, 0, 1),
            0, 180, 0, 360
        )
        
        # Combine inner parts
        inner_vessel = inner_cylinder.fuse(inner_bottom_hemisphere)
        inner_vessel = inner_vessel.fuse(inner_top_hemisphere)
        
        # Hollow out the pressure vessel
        pressure_vessel = pressure_vessel_outer.cut(inner_vessel)
        
        # Create FreeCAD object
        obj = self.doc.addObject("Part::Feature", "PressureVessel")
        obj.Shape = pressure_vessel
        obj.Label = "Pressure Vessel"
        
        # Set appearance properties
        obj.ViewObject.ShapeColor = (0.75, 0.75, 0.85)  # Bluish metallic
        
        # Store calculated dimensions as object properties
        obj.addProperty("App::PropertyLength", "InnerRadius", "Dimensions", "Inner radius of the pressure vessel")
        obj.InnerRadius = inner_radius
        
        obj.addProperty("App::PropertyLength", "OuterRadius", "Dimensions", "Outer radius of the pressure vessel")
        obj.OuterRadius = outer_radius
        
        obj.addProperty("App::PropertyLength", "WallThickness", "Dimensions", "Wall thickness of the pressure vessel")
        obj.WallThickness = self.thickness
        
        obj.addProperty("App::PropertyLength", "CylinderHeight", "Dimensions", "Height of the cylindrical section")
        obj.CylinderHeight = height
        
        obj.addProperty("App::PropertyPressure", "DesignPressure", "Design", "Design pressure")
        obj.DesignPressure = self.design_pressure
        
        obj.addProperty("App::PropertyFloat", "SafetyFactor", "Design", "Safety factor")
        obj.SafetyFactor = self.safety_factor
        
        obj.addProperty("App::PropertyString", "Material", "Material", "Material of the pressure vessel")
        obj.Material = self.material
        
        self.doc.recompute()
        
        # Store object for later use
        self.vessel_obj = obj
        
        return obj
    
    def calculate_hoop_stress(self):
        """Calculate the hoop stress in the cylindrical section."""
        # Hoop stress = P * r / t
        # P = pressure, r = radius, t = thickness
        
        # Convert MPa to Pa for calculations
        pressure_pa = self.design_pressure * 1e6
        
        # Get inner radius in meters
        inner_radius_m = self.vessel_obj.InnerRadius.Value / 1000
        
        # Get thickness in meters
        thickness_m = self.thickness / 1000
        
        # Calculate hoop stress (Pa)
        hoop_stress = pressure_pa * inner_radius_m / thickness_m
        
        # Convert back to MPa
        return hoop_stress / 1e6
    
    def calculate_longitudinal_stress(self):
        """Calculate the longitudinal stress in the cylindrical section."""
        # Longitudinal stress = P * r / (2 * t)
        
        # Convert MPa to Pa for calculations
        pressure_pa = self.design_pressure * 1e6
        
        # Get inner radius in meters
        inner_radius_m = self.vessel_obj.InnerRadius.Value / 1000
        
        # Get thickness in meters
        thickness_m = self.thickness / 1000
        
        # Calculate longitudinal stress (Pa)
        longitudinal_stress = pressure_pa * inner_radius_m / (2 * thickness_m)
        
        # Convert back to MPa
        return longitudinal_stress / 1e6
    
    def calculate_safety_margin(self):
        """Calculate the safety margin based on material yield strength."""
        hoop_stress = self.calculate_hoop_stress()
        material_yield = self.material_properties[self.material]["yield_strength"]
        
        safety_margin = material_yield / hoop_stress
        return safety_margin
    
    def is_design_safe(self):
        """Check if the design meets safety requirements."""
        safety_margin = self.calculate_safety_margin()
        return safety_margin >= self.safety_factor
    
    def generate_stress_report(self, output_file):
        """Generate a PDF report of the pressure vessel stress analysis."""
        # In a real application, this would generate a PDF
        # For this example, we'll create a text file
        with open(output_file.replace('.pdf', '.txt'), 'w') as f:
            f.write("PRESSURE VESSEL STRESS ANALYSIS REPORT\n")
            f.write("=====================================\n\n")
            
            f.write("Pressure Vessel Parameters:\n")
            f.write(f"- Material: {self.material}\n")
            f.write(f"- Design Pressure: {self.design_pressure} MPa\n")
            f.write(f"- Safety Factor: {self.safety_factor}\n")
            f.write(f"- Wall Thickness: {self.thickness} mm\n")
            f.write(f"- Inner Radius: {self.vessel_obj.InnerRadius.Value:.2f} mm\n")
            f.write(f"- Outer Radius: {self.vessel_obj.OuterRadius.Value:.2f} mm\n")
            f.write(f"- Cylinder Height: {self.vessel_obj.CylinderHeight.Value:.2f} mm\n\n")
            
            f.write("Material Properties:\n")
            f.write(f"- Yield Strength: {self.material_properties[self.material]['yield_strength']} MPa\n")
            f.write(f"- Tensile Strength: {self.material_properties[self.material]['tensile_strength']} MPa\n")
            f.write(f"- Density: {self.material_properties[self.material]['density']} kg/m³\n")
            f.write(f"- Elastic Modulus: {self.material_properties[self.material]['elastic_modulus']} MPa\n\n")
            
            f.write("Stress Analysis Results:\n")
            hoop_stress = self.calculate_hoop_stress()
            longitudinal_stress = self.calculate_longitudinal_stress()
            safety_margin = self.calculate_safety_margin()
            
            f.write(f"- Hoop Stress: {hoop_stress:.2f} MPa\n")
            f.write(f"- Longitudinal Stress: {longitudinal_stress:.2f} MPa\n")
            f.write(f"- Safety Margin: {safety_margin:.2f}\n")
            f.write(f"- Design Status: {'SAFE' if self.is_design_safe() else 'UNSAFE - REDESIGN REQUIRED'}\n\n")
            
            if not self.is_design_safe():
                f.write("RECOMMENDATIONS:\n")
                f.write("- Increase wall thickness\n")
                f.write("- Use stronger material\n")
                f.write("- Reduce design pressure\n")
            
            f.write("\nNote: This report is for preliminary design purposes only.\n")
            f.write("A complete finite element analysis is recommended for final design validation.\n")
        
        print(f"Stress analysis report saved to: {output_file.replace('.pdf', '.txt')}")


class Nozzle:
    """Class for creating rocket engine nozzle models and analysis."""
    
    def __init__(self, doc, config):
        """
        Initialize the nozzle with document and configuration.
        
        Args:
            doc: FreeCAD document to add objects to
            config: Dictionary containing nozzle parameters
        """
        self.doc = doc
        self.config = config
        
        # Extract parameters
        self.throat_diameter = config["throat_diameter"]  # mm
        self.exit_diameter = config["exit_diameter"]  # mm
        self.length = config["length"]  # mm
        self.convergent_half_angle = config["convergent_half_angle"]  # degrees
        self.divergent_half_angle = config["divergent_half_angle"]  # degrees
        
        # Calculate derived values
        self.throat_radius = self.throat_diameter / 2
        self.exit_radius = self.exit_diameter / 2
        self.expansion_ratio = (self.exit_radius / self.throat_radius)**2
    
    def create_model(self):
        """Create a 3D model of the rocket nozzle."""
        # Calculate proportions
        # For simplicity, we'll make a bell-shaped nozzle using a series of cones
        
        # Calculate the throat position along the z-axis
        # Let's position the throat at 1/3 of the total length
        throat_position = self.length / 3
        
        # Create a series of circles at different positions
        positions = [
            0,                  # Entry
            throat_position,    # Throat
            self.length         # Exit
        ]
        
        radii = [
            self.throat_radius * 1.5,  # Entry radius
            self.throat_radius,        # Throat radius
            self.exit_radius           # Exit radius
        ]
        
        # Create a list of circles
        circles = []
        for i, z in enumerate(positions):
            circle = Part.makeCircle(radii[i], Vector(0, 0, z), Vector(0, 0, 1))
            circles.append(circle)
        
        # Create wires from circles
        wires = [Part.Wire(c) for c in circles]
        
        # Create a loft through the wires
        loft = Part.makeLoft(wires, True, False, False)
        
        # Create FreeCAD object
        obj = self.doc.addObject("Part::Feature", "Nozzle")
        obj.Shape = loft
        obj.Label = "Rocket Nozzle"
        
        # Set appearance properties
        obj.ViewObject.ShapeColor = (0.9, 0.5, 0.5)  # Reddish color
        
        # Add properties to the object
        obj.addProperty("App::PropertyLength", "ThroatDiameter", "Dimensions", "Throat diameter")
        obj.ThroatDiameter = self.throat_diameter
        
        obj.addProperty("App::PropertyLength", "ExitDiameter", "Dimensions", "Exit diameter")
        obj.ExitDiameter = self.exit_diameter
        
        obj.addProperty("App::PropertyLength", "NozzleLength", "Dimensions", "Overall nozzle length")
        obj.NozzleLength = self.length
        
        obj.addProperty("App::PropertyFloat", "ExpansionRatio", "Design", "Nozzle expansion ratio")
        obj.ExpansionRatio = self.expansion_ratio
        
        obj.addProperty("App::PropertyAngle", "ConvergentAngle", "Design", "Convergent half-angle")
        obj.ConvergentAngle = self.convergent_half_angle
        
        obj.addProperty("App::PropertyAngle", "DivergentAngle", "Design", "Divergent half-angle")
        obj.DivergentAngle = self.divergent_half_angle
        
        self.doc.recompute()
        
        # Store object for later use
        self.nozzle_obj = obj
        
        return obj
    
    def calculate_optimal_expansion_ratio(self, chamber_pressure, ambient_pressure):
        """
        Calculate the optimal expansion ratio for a given chamber and ambient pressure.
        
        Args:
            chamber_pressure: Pressure inside the chamber (MPa)
            ambient_pressure: Ambient pressure (typically atmospheric, in MPa)
            
        Returns:
            Optimal expansion ratio for the given conditions
        """
        # For steam, k (specific heat ratio) is approximately 1.3
        k = 1.3
        
        # Conversion to avoid issues with units
        p_chamber = chamber_pressure * 1e6  # Convert MPa to Pa
        p_ambient = ambient_pressure * 1e6  # Convert MPa to Pa
        
        # Calculate optimal expansion ratio
        # ε = ((k+1)/2)^(1/(k-1)) * (p_chamber/p_ambient)^(1/k)
        term1 = math.pow((k + 1) / 2, 1 / (k - 1))
        term2 = math.pow(p_chamber / p_ambient, 1 / k)
        
        expansion_ratio = term1 * term2
        
        return expansion_ratio
