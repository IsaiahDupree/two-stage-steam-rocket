#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Rocket Optimization Module

An extension to the rocket_physics module that adds:
1. Trajectory simulation to determine maximum altitude
2. Iterative optimization to meet a target altitude
3. Mass optimization to minimize overall rocket weight
4. Structural integrity calculations based on loads

This module helps determine the minimum rocket configuration needed
to reach a specific altitude while maintaining structural integrity.
"""

import math
import numpy as np
import csv
import os
import time
from rocket_physics import Stage, MultiStageRocket, GRAVITY, EARTH_RADIUS, generate_rocket_csv_specs

class RocketOptimizer:
    """Class for optimizing a rocket design to reach a target altitude."""
    
    def __init__(self, target_altitude, payload_mass, propellant_type="LOX/LH2", 
                 stages=2, initial_diameter=3.0, safety_factor=1.2):
        """Initialize the rocket optimizer.
        
        Args:
            target_altitude: Target altitude in meters
            payload_mass: Payload mass in kg
            propellant_type: Type of propellant from available options
            stages: Number of stages (1, 2, or 3)
            initial_diameter: Initial rocket diameter in meters
            safety_factor: Safety factor for structural calculations (>1)
        """
        self.target_altitude = target_altitude
        self.payload_mass = payload_mass
        self.propellant_type = propellant_type
        self.num_stages = stages
        self.initial_diameter = initial_diameter
        self.safety_factor = safety_factor
        
        # Set default stage length-to-diameter ratios
        # Based on typical rocket designs
        self.stage_l_to_d = {
            1: [8.0],                # Single stage
            2: [10.0, 3.5],          # Two stages
            3: [8.0, 5.0, 3.0]       # Three stages
        }
        
        # Set default stage propellant mass fractions
        # (propellant mass / total stage mass)
        self.stage_pmf = {
            1: [0.85],               # Single stage
            2: [0.88, 0.84],         # Two stages
            3: [0.90, 0.86, 0.82]    # Three stages
        }
        
        # Set minimum wall thickness based on diameter (simplified)
        self.min_wall_thickness = lambda d: max(0.002, 0.004 * d)  # in meters
        
        # Initialize stage configurations
        self.stages = []
        self.rocket = None
        self.max_altitude = 0
        self.optimization_history = []
        
        # Initialize with a basic configuration
        self._initialize_rocket()
    
    def _initialize_rocket(self):
        """Create an initial rocket configuration based on heuristics."""
        # Simple sizing heuristics based on target altitude
        self.stages = []
        
        # Total rocket mass estimation based on payload and target altitude
        # Using industry rule-of-thumb scaling factors
        altitude_factor = self.target_altitude / 400000  # Normalized to LEO
        
        # Initial estimate for rocket mass based on real-world rockets
        # (typical mass fractions for different altitudes)
        if self.target_altitude < 100000:  # Suborbital - like sounding rockets
            initial_mass_ratio = 20  # Payload is typically 5% of total mass
        elif self.target_altitude < 400000:  # LEO - like Falcon 9
            initial_mass_ratio = 30 
        else:  # Beyond LEO - like Saturn V for lunar missions
            initial_mass_ratio = 50
            
        total_mass_estimate = self.payload_mass * initial_mass_ratio
        
        # Distribute mass across stages based on typical rockets
        stage_mass_fractions = {
            1: [1.0],
            2: [0.80, 0.20],  # 80% first stage, 20% second stage
            3: [0.75, 0.20, 0.05]  # Based on Saturn V proportions
        }
        
        # Realistic propellant types by stage
        stage_propellants = {
            1: {
                0: "LOX/RP1"  # First stage: Kerosene is denser, better for lower stages
            },
            2: {
                0: "LOX/RP1",  # First stage: Kerosene
                1: "LOX/LH2"   # Upper stage: Hydrogen has higher Isp
            },
            3: {
                0: "LOX/RP1",  # First stage: Kerosene
                1: "LOX/LH2",  # Second stage: Hydrogen
                2: "LOX/LH2"   # Third stage: Hydrogen
            }
        }
        
        # For each stage, create an initial configuration
        for i in range(self.num_stages):
            # Realistic diameters based on actual rockets
            if self.target_altitude < 100000:  # Suborbital
                base_diameter = 1.5  # Like Black Brant sounding rocket
            elif self.target_altitude < 400000:  # LEO
                base_diameter = 3.7  # Like Falcon 9
            else:  # Beyond LEO
                base_diameter = 8.4  # Like Saturn V
                
            # Each higher stage has progressively smaller diameter
            diameter_factor = 1.0 if i == 0 else 0.9 if i == 1 else 0.8
            diameter = base_diameter * diameter_factor
            
            # Stage mass allocation
            stage_mass = total_mass_estimate * stage_mass_fractions[self.num_stages][i]
            
            # Propellant mass based on typical propellant mass fraction
            # First stages: 0.92-0.94, Upper stages: 0.88-0.91
            propellant_fraction = 0.93 if i == 0 else 0.90 if i == 1 else 0.88
            propellant_mass = stage_mass * propellant_fraction
            
            # Dry mass is the remainder
            dry_mass = stage_mass - propellant_mass
            
            # Length based on L/D ratio and volume considerations
            # Real rockets typically have L/D of 8-12 for first stage
            # and 3-7 for upper stages
            base_l_to_d = 10.0 if i == 0 else 5.0 if i == 1 else 3.0
            length = diameter * base_l_to_d
            
            # Choose propellant type for this stage
            propellant = stage_propellants[self.num_stages][i]
            
            # Realistic thrust calculation
            # First stage TWR: 1.3-1.5, Upper stages: 0.8-1.0
            if i == 0:  # First stage
                thrust_sl = 1.4 * stage_mass * GRAVITY  # TWR of 1.4
                thrust_vac = 1.6 * stage_mass * GRAVITY  # Higher in vacuum
            else:  # Upper stages
                thrust_sl = 0  # Upper stages don't operate at sea level
                thrust_vac = 0.9 * stage_mass * GRAVITY  # TWR of 0.9 in vacuum
            
            # Burn time calculation from real rockets
            # Calculate based on propellant mass, thrust, and Isp
            if propellant == "LOX/RP1":
                isp_vac = 340  # s
            else:  # LOX/LH2
                isp_vac = 450  # s
                
            if propellant_mass > 0 and thrust_vac > 0:
                # ṁ = F / (g0 * Isp)
                mdot = thrust_vac / (isp_vac * GRAVITY)
                burn_time = propellant_mass / mdot
            else:
                burn_time = 200  # default
            
            # Create stage
            stage_name = f"Stage {i+1}"
            stage = Stage(
                name=stage_name,
                dry_mass=dry_mass,
                propellant_mass=propellant_mass,
                thrust_sl=thrust_sl,
                thrust_vac=thrust_vac,
                burn_time=burn_time,
                diameter=diameter,
                length=length,
                propellant_type=propellant
            )
            self.stages.append(stage)
        
        # Create the multi-stage rocket
        self.rocket = MultiStageRocket(
            name=f"{self.num_stages}-Stage to {self.target_altitude/1000:.0f} km",
            payload_mass=self.payload_mass,
            stages=self.stages
        )
        
        # Estimate initial maximum altitude
        self.max_altitude = self._estimate_altitude()
        print(f"Initial configuration: {self.num_stages} stages, estimated altitude: {self.max_altitude/1000:.1f} km")
    
    def _estimate_altitude(self):
        """Estimate maximum altitude based on simplified physics.
        
        Uses the rocket equation and a simplified trajectory model.
        """
        # Get total delta-V capability
        delta_v = self.rocket.get_total_delta_v()
        
        # Get total initial mass and thrust
        initial_mass = self.rocket.get_total_mass()
        first_stage_thrust_sl = self.stages[0].thrust_sl if self.stages else 0
        
        # Check if thrust-to-weight ratio is sufficient for liftoff
        twr = first_stage_thrust_sl / (initial_mass * GRAVITY)
        if twr < 1.2:  # Minimum TWR for practical liftoff
            print(f"Warning: Thrust-to-weight ratio ({twr:.2f}) is too low for liftoff!")
            return 0
        
        # Simplified gravity losses based on TWR
        # Lower TWR means higher gravity losses
        gravity_loss = 1500 * (1.5 / twr)
        
        # Simplified drag losses based on rocket shape
        # Narrower rockets have less drag
        diameter = self.stages[0].diameter
        length = self.rocket.get_height()
        fineness_ratio = length / diameter
        
        # Drag loss - decreases with higher fineness ratio but increases with diameter
        drag_loss = 300 * (3.0 / fineness_ratio) * (diameter / 3.0)
        
        # Effective delta-V
        effective_delta_v = delta_v - gravity_loss - drag_loss
        
        # Log details for debugging
        print(f"  Delta-V: {delta_v:.0f} m/s")
        print(f"  TWR: {twr:.2f}")
        print(f"  Gravity losses: {gravity_loss:.0f} m/s")
        print(f"  Drag losses: {drag_loss:.0f} m/s")
        print(f"  Effective delta-V: {effective_delta_v:.0f} m/s")
        
        # Simplified altitude calculation based on energy
        if effective_delta_v <= 0:
            return 0
            
        # For suborbital flights:
        if effective_delta_v < 7800:  # Less than orbital velocity
            # Convert delta-V to max altitude using energy equation
            # Simplified model: final KE = 0 (apex), initial KE converts to PE
            # PE = m*g*h, KE = 0.5*m*v^2, so h = v^2/(2*g)
            max_altitude = (effective_delta_v**2) / (2 * GRAVITY)
            
            # Apply a correction factor for atmospheric effects
            correction_factor = 0.85  # Typically 80-90% of theoretical
            return max_altitude * correction_factor
        
        # For orbital altitudes:
        else:
            # Circular orbit altitude from velocity
            mu = GRAVITY * EARTH_RADIUS**2  # Gravitational parameter
            orbital_velocity = effective_delta_v  # Simplified
            
            # Calculate orbit radius from orbital velocity
            # v_orbit = sqrt(GM/r)
            orbital_radius = mu / (orbital_velocity**2)
            altitude = orbital_radius - EARTH_RADIUS
            return max(0, altitude)  # Ensure non-negative
    
    def _calculate_wall_thickness(self, stage_index):
        """Calculate minimum wall thickness needed for a stage."""
        stage = self.stages[stage_index]
        
        # Pressure differential (internal tank pressure - external)
        # Typical tank pressure for rocket propellants
        if "LOX" in stage.propellant["name"]:
            tank_pressure = 3.0e5  # Pa, cryo tanks are typically 3-5 bar
        else:
            tank_pressure = 2.0e5  # Pa, non-cryo tanks are lower pressure
        
        # External pressure at max altitude for this stage
        # (simplified, just using sea level for first stage, vacuum for others)
        external_pressure = 101325 if stage_index == 0 else 0
        
        # Pressure differential
        delta_p = tank_pressure - external_pressure
        
        # Longitudinal stress from acceleration
        max_accel = 5.0 * GRAVITY  # Typical max acceleration
        stage_mass_above = self.payload_mass
        for s in self.stages[:stage_index]:
            stage_mass_above += s.total_mass
        
        # Force from acceleration
        accel_force = stage_mass_above * max_accel
        
        # Cross-sectional area
        cross_area = math.pi * (stage.diameter**2) / 4
        
        # Stress from acceleration
        accel_stress = accel_force / cross_area
        
        # Hoop stress from pressure
        # σ = p * r / t
        hoop_stress = delta_p * (stage.diameter / 2)
        
        # Material yield strength (aluminum alloy, MPa)
        yield_strength = 270e6  # Pa, typical for aerospace aluminum
        
        # Calculate thickness from hoop stress with safety factor
        min_thickness_pressure = (delta_p * stage.diameter/2) / (yield_strength / self.safety_factor)
        
        # Calculate thickness from acceleration stress
        min_thickness_accel = accel_stress * (stage.diameter/2) / (yield_strength / self.safety_factor)
        
        # Use larger of the two
        min_thickness = max(min_thickness_pressure, min_thickness_accel)
        
        # Minimum practical thickness
        practical_min = self.min_wall_thickness(stage.diameter)
        
        return max(min_thickness, practical_min)
    
    def _update_stage_mass(self, stage_index, new_propellant_mass=None, new_dry_mass=None):
        """Update a stage's mass properties."""
        stage = self.stages[stage_index]
        
        if new_propellant_mass is not None:
            stage.propellant_mass = max(100, new_propellant_mass)  # Ensure positive mass
        
        if new_dry_mass is not None:
            stage.dry_mass = max(100, new_dry_mass)  # Ensure positive mass
        
        # Recalculate stage properties
        stage.total_mass = stage.dry_mass + stage.propellant_mass
        stage.mass_ratio = stage.total_mass / stage.dry_mass if stage.dry_mass > 0 else 1
        
        # Update engine parameters
        if stage.propellant_mass > 0:
            stage.propellant_flow_rate = stage.propellant_mass / stage.burn_time if stage.burn_time > 0 else 0
            
            # Adjust thrust for new mass
            stage.thrust_vac = stage.propellant_flow_rate * stage.propellant["isp_vac"] * GRAVITY
            stage.thrust_sl = stage.propellant_flow_rate * stage.propellant["isp_sl"] * GRAVITY if stage_index == 0 else 0
        
        # Recalculate engine parameters
        stage._calculate_engine_parameters()
    
    def _adjust_stage_geometry(self, stage_index, new_diameter=None, new_length=None):
        """Adjust a stage's geometry."""
        stage = self.stages[stage_index]
        
        if new_diameter is not None:
            stage.diameter = max(0.5, new_diameter)  # Ensure positive diameter
            
            # Recalculate nozzle parameters which depend on diameter
            stage._calculate_engine_parameters()
        
        if new_length is not None:
            stage.length = max(1.0, new_length)  # Ensure positive length
    
    def optimize_to_altitude(self, iterations=10, adjustment_factor=0.2):
        """Iteratively optimize the rocket to reach the target altitude."""
        print(f"\nOptimizing rocket to reach {self.target_altitude/1000:.1f} km altitude...")
        
        # Record initial state
        self.optimization_history.append({
            "iteration": 0,
            "altitude": self.max_altitude,
            "total_mass": self.rocket.get_total_mass(),
            "delta_v": self.rocket.get_total_delta_v(),
            "stages": [{"dry_mass": s.dry_mass, "propellant_mass": s.propellant_mass} 
                      for s in self.stages]
        })
        
        for i in range(1, iterations+1):
            print(f"\nIteration {i}/{iterations}")
            
            # Calculate current error
            altitude_error = self.target_altitude - self.max_altitude
            error_ratio = altitude_error / self.target_altitude
            
            print(f"Current altitude: {self.max_altitude/1000:.1f} km")
            print(f"Target altitude: {self.target_altitude/1000:.1f} km")
            print(f"Error: {error_ratio*100:.1f}%")
            
            if abs(error_ratio) < 0.05:  # Within 5% of target
                print("Target achieved within tolerance. Optimizing mass...")
                self._optimize_mass()
                break
            
            # Adjust propellant masses based on error
            for j, stage in enumerate(self.stages):
                # Scale propellant based on altitude error and stage position
                # First stage gets more adjustment than upper stages
                stage_factor = 1.0 if j == 0 else 0.5 if j == 1 else 0.2
                
                # Calculate adjustment
                propellant_adjustment = stage.propellant_mass * error_ratio * adjustment_factor * stage_factor
                
                # Apply adjustment (different strategies for overshoot vs undershoot)
                if altitude_error > 0:  # Need more altitude
                    new_propellant = stage.propellant_mass + propellant_adjustment
                    self._update_stage_mass(j, new_propellant_mass=new_propellant)
                    
                    # For significant undershoot, increase engine thrust
                    if error_ratio > 0.2:
                        stage.thrust_vac *= 1.1
                        if j == 0:
                            stage.thrust_sl *= 1.1
                else:  # Need less altitude
                    new_propellant = stage.propellant_mass + propellant_adjustment
                    self._update_stage_mass(j, new_propellant_mass=new_propellant)
            
            # Adjust structural mass based on loads
            self._adjust_structural_mass()
            
            # Adjust geometry for better performance
            if i % 3 == 0:  # Every few iterations
                self._adjust_geometry(error_ratio)
            
            # Recalculate altitude
            self.max_altitude = self._estimate_altitude()
            
            # Record state
            self.optimization_history.append({
                "iteration": i,
                "altitude": self.max_altitude,
                "total_mass": self.rocket.get_total_mass(),
                "delta_v": self.rocket.get_total_delta_v(),
                "stages": [{"dry_mass": s.dry_mass, "propellant_mass": s.propellant_mass} 
                          for s in self.stages]
            })
        
        # Finalize with structural mass calculation
        self._adjust_structural_mass()
        
        # Print final design
        self._print_final_design()
        
        return self.rocket
    
    def _adjust_structural_mass(self):
        """Adjust the structural mass of each stage based on physical requirements."""
        for i, stage in enumerate(self.stages):
            # Calculate minimum wall thickness
            wall_thickness = self._calculate_wall_thickness(i)
            
            # Calculate tank surface area (simplified as cylinder)
            tank_height = stage.length * 0.8  # Tanks typically 80% of stage length
            tank_surface_area = 2 * math.pi * (stage.diameter/2) * tank_height
            
            # Calculate tank volume
            tank_volume = math.pi * (stage.diameter/2)**2 * tank_height
            
            # Calculate tank mass based on wall thickness and material density
            # Aluminum density ~2700 kg/m^3
            material_density = 2700
            tank_mass = tank_surface_area * wall_thickness * material_density
            
            # Engine mass (typically 1-4% of propellant mass)
            engine_mass_fraction = 0.03 if i == 0 else 0.02
            engine_mass = stage.propellant_mass * engine_mass_fraction
            
            # Avionics, wiring, misc (typically 1-2% of stage mass)
            avionics_mass_fraction = 0.01
            avionics_mass = stage.total_mass * avionics_mass_fraction
            
            # Structural supports, interstage adapters
            # (typically 2-5% of dry mass)
            structural_mass_fraction = 0.04 if i == 0 else 0.03
            structural_mass = stage.dry_mass * structural_mass_fraction
            
            # Total dry mass
            new_dry_mass = tank_mass + engine_mass + avionics_mass + structural_mass
            
            # Add a margin for unknown components (5-10%)
            margin = 1.08
            new_dry_mass *= margin
            
            # Update stage
            self._update_stage_mass(i, new_dry_mass=new_dry_mass)
    
    def _adjust_geometry(self, error_ratio):
        """Adjust geometry to improve performance."""
        # Adjust diameters for better aerodynamics
        for i, stage in enumerate(self.stages):
            # Adjust length-to-diameter ratio for better performance
            # Lower L/D for more altitude, higher L/D for less
            if error_ratio > 0:  # Need more altitude
                # Shorter, wider rocket has less drag per mass
                new_l_to_d = self.stage_l_to_d[self.num_stages][i] * 0.95
            else:  # Need less altitude
                # Longer, thinner rocket has more drag, less performance
                new_l_to_d = self.stage_l_to_d[self.num_stages][i] * 1.05
            
            # Constrain to reasonable values
            new_l_to_d = max(3.0, min(12.0, new_l_to_d))
            
            # Update length while keeping volume constant
            # V = π * (d/2)² * l
            volume = math.pi * (stage.diameter/2)**2 * stage.length
            
            # If we change L/D ratio but keep volume constant:
            # new_l = volume / (π * (new_d/2)²)
            # where new_d = new_l / new_l_to_d
            # Solving: new_l² = volume * new_l_to_d * 4 / π
            
            new_length = math.pow((volume * new_l_to_d * 4 / math.pi), 1/3)
            new_diameter = new_length / new_l_to_d
            
            # Update stage geometry
            self._adjust_stage_geometry(i, new_diameter=new_diameter, new_length=new_length)
            
            # Update the stored L/D ratio
            self.stage_l_to_d[self.num_stages][i] = new_l_to_d
    
    def _optimize_mass(self):
        """Optimize mass once altitude target is achieved."""
        print("Performing mass optimization...")
        
        # Try reducing propellant mass incrementally until altitude drops below target
        for i, stage in enumerate(self.stages):
            # Start with small reductions
            reduction_step = 0.02  # 2% reduction per step
            max_iterations = 10
            
            for j in range(max_iterations):
                # Save current state
                current_propellant = stage.propellant_mass
                
                # Try a reduced propellant mass
                new_propellant = current_propellant * (1 - reduction_step)
                self._update_stage_mass(i, new_propellant_mass=new_propellant)
                
                # Recalculate altitude
                new_altitude = self._estimate_altitude()
                
                # If altitude drops below target or mass ratio becomes unrealistic, revert
                if new_altitude < self.target_altitude * 0.95 or stage.mass_ratio > 10:
                    # Revert to previous state
                    self._update_stage_mass(i, new_propellant_mass=current_propellant)
                    break
                
                print(f"  Reduced Stage {i+1} propellant by {reduction_step*100:.1f}%, "
                      f"altitude: {new_altitude/1000:.1f} km")
                
                # Store the new altitude
                self.max_altitude = new_altitude
        
        # Recalculate structural mass to match the new propellant loading
        self._adjust_structural_mass()
        
        # Final altitude calculation
        self.max_altitude = self._estimate_altitude()
    
    def _print_final_design(self):
        """Print the final rocket design details."""
        print("\n" + "="*50)
        print(f"FINAL ROCKET DESIGN FOR {self.target_altitude/1000:.1f} km ALTITUDE")
        print("="*50)
        
        # Overall rocket information
        print(f"\nRocket: {self.rocket.name}")
        print(f"Total Mass: {self.rocket.get_total_mass():,.0f} kg")
        print(f"Height: {self.rocket.get_height():.1f} m")
        print(f"Delta-V: {self.rocket.get_total_delta_v():,.0f} m/s")
        print(f"Max Altitude: {self.max_altitude/1000:.1f} km")
        
        # Mass fractions
        mass_fractions = self.rocket.get_mass_fractions()
        print("\nMass Fractions:")
        print(f"Payload: {mass_fractions['payload']*100:.1f}%")
        
        # Individual stage information
        print("\nStage Information:")
        for i, stage in enumerate(self.stages):
            print(f"\nStage {i+1} ({stage.name}):")
            print(f"  Diameter: {stage.diameter:.2f} m")
            print(f"  Length: {stage.length:.2f} m")
            print(f"  Dry Mass: {stage.dry_mass:,.0f} kg")
            print(f"  Propellant Mass: {stage.propellant_mass:,.0f} kg")
            print(f"  Total Mass: {stage.total_mass:,.0f} kg")
            print(f"  Mass Ratio: {stage.mass_ratio:.2f}")
            print(f"  Propellant: {stage.propellant['name']}")
            print(f"  Vacuum Thrust: {stage.thrust_vac/1000:,.0f} kN")
            if i == 0:
                print(f"  Sea Level Thrust: {stage.thrust_sl/1000:,.0f} kN")
            print(f"  Burn Time: {stage.burn_time:.0f} s")
            print(f"  Nozzle Throat Diameter: {stage.throat_diameter*1000:.1f} mm")
            print(f"  Nozzle Exit Diameter: {stage.exit_diameter*1000:.1f} mm")
            print(f"  Nozzle Length: {stage.nozzle_length:.2f} m")
            print(f"  Expansion Ratio: {stage.expansion_ratio:.1f}")
        
        print("\n" + "="*50)
    
    def generate_csv(self, filename):
        """Generate a CSV file with the rocket specifications for FreeCAD."""
        return generate_rocket_csv_specs(self.rocket, filename)
    
    def save_optimization_history(self, filename):
        """Save the optimization history to a CSV file."""
        with open(filename, 'w', newline='') as file:
            writer = csv.writer(file)
            
            # Write header
            writer.writerow(['Iteration', 'Altitude (km)', 'Total Mass (kg)', 'Delta-V (m/s)'] + 
                           [f'Stage {i+1} Dry Mass (kg)' for i in range(self.num_stages)] +
                           [f'Stage {i+1} Propellant Mass (kg)' for i in range(self.num_stages)])
            
            # Write data
            for entry in self.optimization_history:
                row = [
                    entry['iteration'],
                    entry['altitude'] / 1000,
                    entry['total_mass'],
                    entry['delta_v']
                ]
                
                # Add stage masses
                for stage in entry['stages']:
                    row.append(stage['dry_mass'])
                for stage in entry['stages']:
                    row.append(stage['propellant_mass'])
                
                writer.writerow(row)
        
        print(f"Optimization history saved to {filename}")
        return filename


def main():
    """Main function to demonstrate rocket optimization capabilities."""
    print("="*60)
    print("ROCKET OPTIMIZER - DESIGN TO TARGET ALTITUDE")
    print("="*60)
    
    # Get user input for target altitude
    altitude_options = {
        1: ("Suborbital", 100000),           # 100 km
        2: ("Low Earth Orbit", 400000),      # 400 km
        3: ("Geosynchronous Orbit", 35786000) # 35,786 km
    }
    
    print("\nSelect a target altitude:")
    for key, (name, altitude) in altitude_options.items():
        print(f"{key}. {name} ({altitude/1000:,.0f} km)")
    
    # Let's use option 2 for this demonstration - LEO
    altitude_choice = 2
    target_altitude = altitude_options[altitude_choice][1]
    print(f"\nSelected: {altitude_options[altitude_choice][0]} ({target_altitude/1000:,.0f} km)")
    
    # Get payload mass
    payload_options = {
        1: ("Small Satellite", 200),
        2: ("Medium Satellite", 2000),
        3: ("Large Satellite", 10000)
    }
    
    print("\nSelect a payload mass:")
    for key, (name, mass) in payload_options.items():
        print(f"{key}. {name} ({mass:,} kg)")
    
    # Let's use option 2 for this demonstration - Medium satellite
    payload_choice = 2
    payload_mass = payload_options[payload_choice][1]
    print(f"\nSelected: {payload_options[payload_choice][0]} ({payload_mass:,} kg)")
    
    # Determine appropriate number of stages based on target altitude
    if target_altitude < 150000:  # 150 km
        num_stages = 1
    elif target_altitude < 2000000:  # 2,000 km
        num_stages = 2
    else:
        num_stages = 3
    
    print(f"\nBased on your target altitude, a {num_stages}-stage rocket is recommended.")
    
    # Create the optimizer
    optimizer = RocketOptimizer(
        target_altitude=target_altitude,
        payload_mass=payload_mass,
        stages=num_stages,
        initial_diameter=3.7  # Similar to Falcon 9
    )
    
    # Run the optimization
    rocket = optimizer.optimize_to_altitude(iterations=15)
    
    # Generate output files
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    csv_file = f"optimized_rocket_{timestamp}.csv"
    history_file = f"optimization_history_{timestamp}.csv"
    
    # Save results
    optimizer.generate_csv(csv_file)
    optimizer.save_optimization_history(history_file)
    
    print(f"\nOptimized rocket design saved to {csv_file}")
    print(f"Use the following command to generate the 3D model:")
    print(f"launch_rocket_design.bat {csv_file}")


if __name__ == "__main__":
    main()
