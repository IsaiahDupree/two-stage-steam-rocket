#!/usr/bin/env python
"""
Drone Nose Cone Design Validator
Checks the design parameters for common issues and calculates important metrics.
"""

import math

class NoseConeValidator:
    def __init__(self, inner_diameter, outer_diameter, base_ring_depth, cone_angle):
        """Initialize with the basic design parameters"""
        self.inner_diameter = inner_diameter
        self.outer_diameter = outer_diameter
        self.base_ring_depth = base_ring_depth
        self.cone_angle = cone_angle
        
        # Calculated parameters
        self.inner_radius = inner_diameter / 2
        self.outer_radius = outer_diameter / 2
        self.wall_thickness = self.outer_radius - self.inner_radius
        
        # Calculate cone height based on angle and radius
        self.cone_height = (self.outer_radius - self.inner_radius) / math.tan(math.radians(self.cone_angle))
        
        # Tip rounding radius (assuming 50% of outer radius)
        self.tip_radius = self.outer_radius * 0.5
        
        # Total height with rounded tip
        self.total_height = self.base_ring_depth + self.cone_height * 1.2  # 1.2 factor for rounded tip
        
    def validate_dimensions(self):
        """Check if all dimensions are valid and make sense"""
        issues = []
        
        # Check for negative or zero values
        if self.inner_diameter <= 0:
            issues.append("Inner diameter must be positive")
        if self.outer_diameter <= 0:
            issues.append("Outer diameter must be positive")
        if self.base_ring_depth <= 0:
            issues.append("Base ring depth must be positive")
        if self.cone_angle <= 0 or self.cone_angle >= 90:
            issues.append("Cone angle must be between 0 and 90 degrees")
            
        # Check that outer diameter is larger than inner
        if self.outer_diameter <= self.inner_diameter:
            issues.append("Outer diameter must be larger than inner diameter")
            
        # Check if wall thickness is reasonable (at least 1mm)
        if self.wall_thickness < 1:
            issues.append(f"Wall thickness ({self.wall_thickness:.2f}mm) is very thin, might be fragile")
            
        # Check if base ring depth is sufficient
        if self.base_ring_depth < 10:
            issues.append(f"Base ring depth ({self.base_ring_depth}mm) might not provide enough gluing surface")
            
        # Check if cone angle creates a reasonable shape
        if self.cone_angle < 30:
            issues.append(f"Cone angle ({self.cone_angle}°) is very sharp, might be difficult to print")
        elif self.cone_angle > 70:
            issues.append(f"Cone angle ({self.cone_angle}°) is very blunt, might not be aerodynamic")
            
        return issues
    
    def calculate_volume(self, shell_thickness=1.2, use_lightweighting=True):
        """Estimate the volume of the nose cone (simplified calculation)"""
        # Base ring volume (cylinder shell)
        base_ring_volume = math.pi * (self.outer_radius**2 - self.inner_radius**2) * self.base_ring_depth
        
        # Cone volume (simplified as solid, then subtract hollow part)
        # For a cone: V = 1/3 * π * r² * h
        solid_cone_volume = (1/3) * math.pi * self.outer_radius**2 * self.cone_height
        hollow_cone_volume = (1/3) * math.pi * self.inner_radius**2 * self.cone_height
        
        # Add volume for rounded tip (approximation)
        tip_volume = (2/3) * math.pi * self.tip_radius**3
        # Subtract inner hollowing of tip
        if use_lightweighting:
            inner_tip_radius = max(0, self.tip_radius - shell_thickness)
            inner_tip_volume = (2/3) * math.pi * inner_tip_radius**3
            tip_volume -= inner_tip_volume
        
        # Calculate total volume
        if use_lightweighting:
            total_volume = base_ring_volume + (solid_cone_volume - hollow_cone_volume) + tip_volume
        else:
            total_volume = base_ring_volume + solid_cone_volume + tip_volume
            
        return total_volume  # mm³
    
    def estimate_weight(self, material_density=1.24, shell_thickness=1.2, infill_percentage=20):
        """Estimate the weight of the printed part in grams
        
        Args:
            material_density: g/cm³ (default: 1.24 for PLA)
            shell_thickness: mm
            infill_percentage: 0-100%
        """
        # Get volume in mm³
        volume_mm3 = self.calculate_volume(shell_thickness, use_lightweighting=True)
        
        # Convert to cm³
        volume_cm3 = volume_mm3 / 1000
        
        # Apply infill factor (100% would be solid)
        effective_volume = volume_cm3 * (shell_thickness * 2 / self.wall_thickness + 
                                         (infill_percentage / 100) * (1 - 2 * shell_thickness / self.wall_thickness))
        
        # Calculate weight
        weight_g = effective_volume * material_density
        
        return weight_g
    
    def print_report(self):
        """Print a comprehensive report about the design"""
        print("="*50)
        print("DRONE NOSE CONE DESIGN VALIDATION REPORT")
        print("="*50)
        
        print("\nInput Parameters:")
        print(f"- Inner Diameter: {self.inner_diameter} mm")
        print(f"- Outer Diameter: {self.outer_diameter} mm")
        print(f"- Base Ring Depth: {self.base_ring_depth} mm")
        print(f"- Cone Angle: {self.cone_angle}°")
        
        print("\nCalculated Dimensions:")
        print(f"- Wall Thickness: {self.wall_thickness:.2f} mm")
        print(f"- Cone Height: {self.cone_height:.2f} mm")
        print(f"- Total Height: {self.total_height:.2f} mm")
        print(f"- Tip Radius: {self.tip_radius:.2f} mm")
        
        print("\nDesign Validation:")
        issues = self.validate_dimensions()
        if issues:
            print("ISSUES FOUND:")
            for issue in issues:
                print(f"- {issue}")
        else:
            print("No issues found! Design parameters appear valid.")
            
        # Calculate volumes for different configurations
        solid_volume = self.calculate_volume(use_lightweighting=False)
        lightweight_volume = self.calculate_volume(use_lightweighting=True)
        volume_reduction = (solid_volume - lightweight_volume) / solid_volume * 100
        
        print("\nVolume Estimates:")
        print(f"- Solid Design: {solid_volume/1000:.2f} cm³")
        print(f"- Lightweight Design: {lightweight_volume/1000:.2f} cm³")
        print(f"- Volume Reduction: {volume_reduction:.1f}%")
        
        # Weight estimates for different materials and infill
        print("\nWeight Estimates (Lightweight Design):")
        materials = {
            "PLA": 1.24,
            "PETG": 1.27,
            "ABS": 1.04,
            "Nylon": 1.10,
            "LW-PLA": 0.8  # Lightweight PLA
        }
        
        for material, density in materials.items():
            for infill in [15, 20, 30]:
                weight = self.estimate_weight(density, shell_thickness=1.2, infill_percentage=infill)
                print(f"- {material} ({infill}% infill): {weight:.1f}g")
        
        print("\nFinal Recommendation:")
        if issues:
            print("Please address the identified issues before proceeding.")
        else:
            print("The design parameters look good. For minimum weight with adequate strength,")
            print("consider printing with LW-PLA at 15-20% infill with a gyroid or honeycomb pattern.")
            print("For maximum strength, use PETG with 25-30% infill.")
        
        print("="*50)

if __name__ == "__main__":
    # Use the specified parameters
    validator = NoseConeValidator(
        inner_diameter=67.0,
        outer_diameter=78.0,
        base_ring_depth=13.0,
        cone_angle=52.0
    )
    
    validator.print_report()
