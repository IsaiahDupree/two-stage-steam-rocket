#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Rocket Physics Module

Implements realistic physical constraints for multistage rocket design based on
aerospace engineering principles and NASA documentation. This module provides
functions to calculate proper dimensions, thrust, mass ratios, and nozzle 
geometries that satisfy physical limitations.

References:
- NASA SP-8120, "Liquid Rocket Engine Nozzles"
- Fundamentals of Solid Propellant Combustion
"""

import math
import numpy as np

# Physical constants
GRAVITY = 9.81  # m/s²
EARTH_RADIUS = 6371000  # m
SEA_LEVEL_PRESSURE = 101325  # Pa

# Default propellant combinations with realistic parameters
PROPELLANT_COMBINATIONS = {
    "LOX/LH2": {  # Liquid Oxygen/Liquid Hydrogen (Space Shuttle)
        "name": "Liquid Oxygen/Liquid Hydrogen",
        "isp_vac": 450,  # s (vacuum specific impulse)
        "isp_sl": 370,  # s (sea-level specific impulse)
        "density": 360,  # kg/m³ (average density)
        "mixture_ratio": 5.5,  # Oxidizer to fuel ratio (O/F)
        "chamber_temp": 3200,  # K
        "chamber_pressure": 6.9e6,  # Pa (1000 psi)
        "gamma": 1.26,  # Ratio of specific heats
    },
    "LOX/RP1": {  # Liquid Oxygen/Refined Petroleum (Falcon 9)
        "name": "Liquid Oxygen/RP-1",
        "isp_vac": 340,  # s 
        "isp_sl": 280,  # s
        "density": 1030,  # kg/m³
        "mixture_ratio": 2.56,  # O/F
        "chamber_temp": 3670,  # K
        "chamber_pressure": 7.6e6,  # Pa (1100 psi)
        "gamma": 1.22,
    },
    "HTPB": {  # Solid propellant (Space Shuttle boosters)
        "name": "HTPB Solid Propellant",
        "isp_vac": 280,  # s
        "isp_sl": 250,  # s
        "density": 1700,  # kg/m³
        "mixture_ratio": None,  # Not applicable for solid propellant
        "chamber_temp": 3400,  # K
        "chamber_pressure": 6.2e6,  # Pa (900 psi)
        "gamma": 1.18,
    }
}

class Stage:
    """Class representing a single rocket stage with physical properties."""
    
    def __init__(self, name, dry_mass, propellant_mass, thrust_sl, thrust_vac, 
                 burn_time, diameter, length, propellant_type="LOX/LH2"):
        """Initialize stage with physical parameters."""
        self.name = name
        self.dry_mass = dry_mass  # kg
        self.propellant_mass = propellant_mass  # kg
        self.thrust_sl = thrust_sl  # N (sea level)
        self.thrust_vac = thrust_vac  # N (vacuum)
        self.burn_time = burn_time  # s
        self.diameter = diameter  # m
        self.length = length  # m
        
        # Set propellant properties
        if propellant_type in PROPELLANT_COMBINATIONS:
            self.propellant = PROPELLANT_COMBINATIONS[propellant_type]
        else:
            # Default to LOX/LH2 if specified type not found
            self.propellant = PROPELLANT_COMBINATIONS["LOX/LH2"]
        
        # Calculate additional properties
        self.mass_ratio = (self.dry_mass + self.propellant_mass) / self.dry_mass
        self.total_mass = self.dry_mass + self.propellant_mass
        self.propellant_flow_rate = self.propellant_mass / self.burn_time if self.burn_time > 0 else 0
        
        # Calculate engine parameters
        self._calculate_engine_parameters()
    
    def _calculate_engine_parameters(self):
        """Calculate engine parameters based on thrust and propellant."""
        # Calculate throat area based on thrust and chamber pressure
        # From rocket thrust equation: F = Cf * At * Pc
        # where Cf is thrust coefficient, At is throat area, Pc is chamber pressure
        pc = self.propellant["chamber_pressure"]
        gamma = self.propellant["gamma"]
        
        # Thrust coefficient calculation (simplified)
        expansion_ratio = 20  # Initial guess for expansion ratio
        Cf = self._calculate_thrust_coefficient(expansion_ratio, gamma)
        
        # Calculate throat area (m²)
        self.throat_area = self.thrust_vac / (Cf * pc)
        
        # Calculate throat diameter (m)
        self.throat_diameter = 2 * math.sqrt(self.throat_area / math.pi)
        
        # Calculate nozzle exit area for optimal expansion in vacuum
        self.expansion_ratio = self._calculate_optimal_expansion_ratio(gamma)
        self.exit_area = self.throat_area * self.expansion_ratio
        self.exit_diameter = 2 * math.sqrt(self.exit_area / math.pi)
        
        # Nozzle length calculation using 80% rule for bell nozzle
        # A bell nozzle is typically 80% the length of an equivalent conical nozzle
        # For a 15° half-angle conical nozzle
        conical_length = (self.exit_diameter - self.throat_diameter) / (2 * math.tan(math.radians(15)))
        self.nozzle_length = 0.8 * conical_length
    
    def _calculate_thrust_coefficient(self, expansion_ratio, gamma):
        """Calculate the thrust coefficient."""
        # Simplified thrust coefficient calculation
        term1 = math.sqrt((2 * gamma**2) / (gamma - 1))
        term2 = (2 / (gamma + 1))**((gamma + 1) / (gamma - 1))
        term3 = (1 - (1 / expansion_ratio)**(gamma - 1) / gamma)
        
        Cf = term1 * term2 * math.sqrt(term3)
        
        # Add divergence correction factor (typically 0.98 for 15° half-angle)
        Cf *= 0.98
        
        return Cf
    
    def _calculate_optimal_expansion_ratio(self, gamma):
        """Calculate optimal expansion ratio for vacuum conditions."""
        # For vacuum conditions, higher expansion ratios are better
        # But practical considerations limit this
        
        # Typical values by stage:
        if "first" in self.name.lower() or "booster" in self.name.lower():
            # First stages typically have lower expansion ratios (8-15)
            return 10
        elif "second" in self.name.lower():
            # Second stages have higher expansion ratios (30-60)
            return 40
        elif "third" in self.name.lower() or "upper" in self.name.lower():
            # Upper stages have very high expansion ratios (60-200)
            return 80
        else:
            # Default to mid-range
            return 25

    def get_delta_v(self):
        """Calculate the delta-V of this stage using the Tsiolkovsky rocket equation."""
        isp = self.propellant["isp_vac"]  # Use vacuum Isp for simplicity
        g0 = GRAVITY
        mass_ratio = self.mass_ratio
        
        # Tsiolkovsky rocket equation: ΔV = Isp * g0 * ln(mass_ratio)
        delta_v = isp * g0 * math.log(mass_ratio)
        return delta_v
    
    def get_nozzle_parameters(self):
        """Return nozzle parameters for FreeCAD modeling."""
        return {
            "throat_diameter": self.throat_diameter,
            "exit_diameter": self.exit_diameter,
            "length": self.nozzle_length,
            "shape": "bell"  # Bell nozzle is typical for modern rockets
        }


class MultiStageRocket:
    """Class representing a complete multistage rocket."""
    
    def __init__(self, name, payload_mass, stages=None):
        """Initialize a multistage rocket with stages and payload."""
        self.name = name
        self.payload_mass = payload_mass  # kg
        self.stages = stages if stages else []
    
    def add_stage(self, stage):
        """Add a stage to the rocket (from bottom to top)."""
        self.stages.append(stage)
    
    def get_total_mass(self):
        """Get the total mass of the rocket including payload."""
        total = self.payload_mass
        for stage in self.stages:
            total += stage.total_mass
        return total
    
    def get_total_delta_v(self):
        """Calculate the total delta-V of the rocket."""
        delta_v = 0
        current_mass = self.get_total_mass()
        
        # Calculate delta-V for each stage accounting for staging
        for stage in self.stages:
            # Calculate the mass after this stage burns and separates
            stage_start_mass = current_mass
            current_mass -= stage.propellant_mass + stage.dry_mass
            
            # Modified Tsiolkovsky equation accounting for actual stage mass ratios
            isp = stage.propellant["isp_vac"]
            delta_v += GRAVITY * isp * math.log(stage_start_mass / current_mass)
        
        return delta_v
    
    def get_height(self):
        """Calculate the total height of the rocket."""
        height = 0
        for stage in self.stages:
            height += stage.length
        # Add a nominal height for the payload fairing
        height += 0.1 * height  # Typically around 10% of total rocket height
        return height
    
    def get_mass_fractions(self):
        """Calculate mass fractions for each stage and the payload."""
        total_mass = self.get_total_mass()
        fractions = {
            "payload": self.payload_mass / total_mass
        }
        
        for i, stage in enumerate(self.stages):
            fractions[f"stage_{i+1}_dry"] = stage.dry_mass / total_mass
            fractions[f"stage_{i+1}_propellant"] = stage.propellant_mass / total_mass
        
        return fractions
    
    def get_stage_dimensions(self):
        """Get dimensions for all stages for FreeCAD modeling."""
        dimensions = []
        
        for i, stage in enumerate(self.stages):
            stage_info = {
                "name": f"{stage.name} (Stage {i+1})",
                "diameter": stage.diameter,
                "length": stage.length,
                "nozzle": stage.get_nozzle_parameters()
            }
            dimensions.append(stage_info)
        
        return dimensions


def create_realistic_two_stage_rocket():
    """Create a realistic two-stage rocket based on typical parameters."""
    # First stage (similar to Falcon 9 first stage)
    first_stage = Stage(
        name="First Stage",
        dry_mass=25000,  # kg (structure, engines, avionics)
        propellant_mass=385000,  # kg
        thrust_sl=7600000,  # N
        thrust_vac=8200000,  # N
        burn_time=162,  # s
        diameter=3.7,  # m
        length=41.2,  # m
        propellant_type="LOX/RP1"
    )
    
    # Second stage (similar to Falcon 9 second stage)
    second_stage = Stage(
        name="Second Stage",
        dry_mass=4000,  # kg
        propellant_mass=90000,  # kg
        thrust_sl=0,  # N (not designed for sea level)
        thrust_vac=934000,  # N
        burn_time=397,  # s
        diameter=3.7,  # m
        length=12.6,  # m
        propellant_type="LOX/RP1"
    )
    
    # Create the complete rocket
    rocket = MultiStageRocket(
        name="Realistic Two-Stage",
        payload_mass=15000  # kg
    )
    
    # Add stages from bottom to top
    rocket.add_stage(first_stage)
    rocket.add_stage(second_stage)
    
    return rocket


def create_realistic_three_stage_rocket():
    """Create a realistic three-stage rocket similar to Saturn V."""
    # First stage (S-IC)
    first_stage = Stage(
        name="First Stage (S-IC)",
        dry_mass=131000,  # kg
        propellant_mass=2159000,  # kg
        thrust_sl=33400000,  # N
        thrust_vac=38700000,  # N
        burn_time=168,  # s
        diameter=10.1,  # m
        length=42.0,  # m
        propellant_type="LOX/RP1"
    )
    
    # Second stage (S-II)
    second_stage = Stage(
        name="Second Stage (S-II)",
        dry_mass=40100,  # kg
        propellant_mass=456100,  # kg
        thrust_sl=0,  # N
        thrust_vac=5115000,  # N
        burn_time=384,  # s
        diameter=10.1,  # m
        length=24.9,  # m
        propellant_type="LOX/LH2"
    )
    
    # Third stage (S-IVB)
    third_stage = Stage(
        name="Third Stage (S-IVB)",
        dry_mass=13300,  # kg
        propellant_mass=106900,  # kg
        thrust_sl=0,  # N
        thrust_vac=1033000,  # N
        burn_time=475,  # s (cumulative for two burns)
        diameter=6.6,  # m
        length=17.8,  # m
        propellant_type="LOX/LH2"
    )
    
    # Create the complete rocket
    rocket = MultiStageRocket(
        name="Realistic Three-Stage",
        payload_mass=45000  # kg (Apollo spacecraft + Lunar Module)
    )
    
    # Add stages from bottom to top
    rocket.add_stage(first_stage)
    rocket.add_stage(second_stage)
    rocket.add_stage(third_stage)
    
    return rocket


def generate_rocket_csv_specs(rocket, output_file):
    """Generate a CSV file with rocket specifications for FreeCAD automation."""
    import csv
    
    with open(output_file, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        
        # Write header
        writer.writerow([
            'name', 'type', 'length', 'diameter', 'thickness', 
            'material', 'comments'
        ])
        
        # Add a payload fairing
        payload_height = 0.15 * rocket.get_height()  # Estimate
        top_stage_diameter = rocket.stages[-1].diameter
        
        writer.writerow([
            'Payload Fairing', 'cone', payload_height * 1000, top_stage_diameter * 1000, 10,
            'composite', f'Houses {rocket.payload_mass} kg payload'
        ])
        
        # Add stages from top to bottom (reversed from rocket.stages)
        for i, stage in enumerate(reversed(rocket.stages)):
            stage_index = len(rocket.stages) - i
            
            # Add interstage adapter if not the first stage
            if i > 0:
                prev_diameter = rocket.stages[stage_index].diameter
                curr_diameter = stage.diameter
                adapter_height = 0.1 * stage.length  # Estimate
                
                writer.writerow([
                    f'Interstage {stage_index-1}/{stage_index}', 
                    'cone' if prev_diameter != curr_diameter else 'tube', 
                    adapter_height * 1000, 
                    max(prev_diameter, curr_diameter) * 1000, 
                    15,
                    'aluminum', 
                    f'Connects stages {stage_index-1} and {stage_index}'
                ])
            
            # Add stage tank/body
            writer.writerow([
                f'{stage.name} Body', 'tube', 
                (stage.length - stage.nozzle_length) * 1000, 
                stage.diameter * 1000, 
                20,
                'aluminum', 
                f'Contains {stage.propellant_mass} kg propellant'
            ])
            
            # Add engine section with nozzle
            nozzle = stage.get_nozzle_parameters()
            writer.writerow([
                f'{stage.name} Engine Section', 'tube', 
                50, # Small section for engine mounting
                stage.diameter * 1000, 
                30,
                'stainless steel', 
                f'Engine mount structure'
            ])
            
            # Add nozzle
            writer.writerow([
                f'{stage.name} Nozzle', 'cone', 
                nozzle['length'] * 1000, 
                nozzle['exit_diameter'] * 1000, 
                10,
                'inconel', 
                f'Expansion ratio: {stage.expansion_ratio:.1f}, Throat diameter: {nozzle["throat_diameter"]*1000:.1f} mm'
            ])
            
            # Add fins for first stage only
            if stage_index == 1:
                fin_height = 0.15 * stage.diameter * 1000  # Fin height in mm
                fin_length = 0.3 * stage.length * 1000  # Fin length in mm
                
                writer.writerow([
                    'First Stage Fins', 'fins', 
                    fin_length, 
                    fin_height, 
                    10,
                    'titanium', 
                    'Aerodynamic stabilizers (count=4)'
                ])
    
    return output_file


def main():
    """Main function to demonstrate the module's capabilities."""
    print("Realistic Rocket Physics Module")
    print("===============================")
    
    # Create a realistic two-stage rocket
    two_stage = create_realistic_two_stage_rocket()
    print(f"\n{two_stage.name} Rocket:")
    print(f"Total mass: {two_stage.get_total_mass():,.0f} kg")
    print(f"Total height: {two_stage.get_height():.1f} m")
    print(f"Total delta-V: {two_stage.get_total_delta_v():,.0f} m/s")
    
    # Create a realistic three-stage rocket
    three_stage = create_realistic_three_stage_rocket()
    print(f"\n{three_stage.name} Rocket:")
    print(f"Total mass: {three_stage.get_total_mass():,.0f} kg")
    print(f"Total height: {three_stage.get_height():.1f} m")
    print(f"Total delta-V: {three_stage.get_total_delta_v():,.0f} m/s")
    
    # Generate CSV specifications for FreeCAD
    two_stage_csv = generate_rocket_csv_specs(two_stage, "two_stage_rocket.csv")
    three_stage_csv = generate_rocket_csv_specs(three_stage, "three_stage_rocket.csv")
    
    print(f"\nGenerated CSV specifications for FreeCAD automation:")
    print(f"- {two_stage_csv}")
    print(f"- {three_stage_csv}")
    print("\nUse these CSV files with the FreeCAD automation script:")
    print("launch_rocket_design.bat two_stage_rocket.csv")


if __name__ == "__main__":
    main()
