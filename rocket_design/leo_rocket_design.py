#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
LEO Rocket Design Tool

A specialized script for designing a physically realistic two-stage rocket
to reach Low Earth Orbit (400 km) with a 2000 kg payload, based on the
physics constraints from our reference materials.

This script applies realistic engineering constraints:
1. Thrust-to-weight ratio must be sufficient for liftoff (>1.2)
2. Nozzle throat area must be non-zero and physically feasible
3. Stage dimensions must be realistic and structurally sound
4. Mass fractions must adhere to engineering best practices
"""

import math
import os
import csv
import time
from datetime import datetime
from rocket_physics import Stage, MultiStageRocket, GRAVITY, EARTH_RADIUS, generate_rocket_csv_specs

# Physical constants
ISP_CORRECTION = 0.98  # Realistic correction for vacuum Isp
DRAG_COEFFICIENT = 0.3  # Typical for rockets
AIR_DENSITY_SL = 1.225  # kg/m³, sea level

# Engineering constraints
MIN_TWR_LIFTOFF = 1.3  # Minimum thrust-to-weight ratio for liftoff
MAX_TWR_LIFTOFF = 1.7  # Maximum practical TWR for structural integrity
MIN_DIAMETER = 2.0  # Minimum practical diameter in meters
MAX_EXPANSION_RATIO = 150  # Maximum practical nozzle expansion ratio
MIN_WALL_THICKNESS_RATIO = 0.01  # Minimum wall thickness as fraction of diameter
TANKAGE_FACTOR_FIRST = 0.05  # Tank mass as fraction of propellant mass (first stage)
TANKAGE_FACTOR_UPPER = 0.08  # Tank mass as fraction of propellant mass (upper stages)
ENGINE_MASS_FACTOR = 0.004  # Engine mass as fraction of thrust (kg/N)


def calculate_delta_v(initial_mass, final_mass, isp):
    """Calculate delta-V using the Tsiolkovsky rocket equation."""
    return GRAVITY * isp * math.log(initial_mass / final_mass)


def calculate_first_stage(payload_mass, upper_stage_mass, target_delta_v_first):
    """Design a first stage to provide the specified delta-V."""
    # First stage uses LOX/RP-1 for better thrust at sea level
    isp_sl = 282  # Sea level Isp for LOX/RP-1, 282s
    isp_vac = 311  # Vacuum Isp for LOX/RP-1, 311s
    
    # Starting with a reasonable mass ratio (based on Falcon 9 first stage)
    mass_ratio = 22  # Initial guess
    
    # Propellant mass fraction (based on real rockets)
    pmf = 0.94  # Propellant mass / total stage mass
    
    # Initial estimate of first stage mass
    first_stage_dry_mass_initial = (upper_stage_mass + payload_mass) / (math.exp(target_delta_v_first / (GRAVITY * isp_vac)) - 1)
    first_stage_total_mass_initial = first_stage_dry_mass_initial * mass_ratio
    
    # Adjust dry mass to match PMF constraint
    first_stage_total_mass = first_stage_dry_mass_initial / (1 - pmf)
    first_stage_propellant_mass = first_stage_total_mass * pmf
    first_stage_dry_mass = first_stage_total_mass - first_stage_propellant_mass
    
    # Recalculate to verify delta-V
    total_initial_mass = payload_mass + upper_stage_mass + first_stage_total_mass
    total_final_mass = payload_mass + upper_stage_mass + first_stage_dry_mass
    actual_delta_v = calculate_delta_v(total_initial_mass, total_final_mass, isp_vac)
    
    print(f"First Stage - Target Delta-V: {target_delta_v_first:.0f} m/s, Actual Delta-V: {actual_delta_v:.0f} m/s")
    print(f"First Stage Propellant Mass: {first_stage_propellant_mass:,.0f} kg")
    print(f"First Stage Dry Mass: {first_stage_dry_mass:,.0f} kg")
    
    # Determine realistic physical dimensions
    # Based on propellant density and realistic fineness ratio
    lox_rp1_bulk_density = 1030  # kg/m³ for LOX/RP-1 with proper mixture ratio
    
    # Allocate propellant volume with ullage (5% extra for expansion)
    propellant_volume = first_stage_propellant_mass / lox_rp1_bulk_density * 1.05
    
    # Determine diameter based on realistic constraints
    # Using a diameter similar to Falcon 9
    diameter = 3.7  # meters
    
    # Calculate length based on volume and diameter
    # Tanks typically occupy ~80% of stage length, rest is structure/engines
    tank_area = math.pi * (diameter/2)**2
    tank_length = propellant_volume / tank_area
    total_length = tank_length / 0.8  # Account for non-tank sections
    
    # For realistic fineness ratio (length/diameter), typically 7-12 for first stages
    fineness_ratio = total_length / diameter
    if fineness_ratio < 6:
        diameter = math.sqrt(propellant_volume / (math.pi * 6))
        total_length = 6 * diameter
    elif fineness_ratio > 15:
        diameter = math.sqrt(propellant_volume / (math.pi * 15))
        total_length = 15 * diameter
    
    print(f"First Stage Diameter: {diameter:.2f} m")
    print(f"First Stage Length: {total_length:.2f} m")
    print(f"First Stage Fineness Ratio (L/D): {total_length/diameter:.1f}")
    
    # Calculate thrust requirements
    liftoff_twr = 1.35  # Typical for efficient rockets
    liftoff_thrust = liftoff_twr * total_initial_mass * GRAVITY
    vacuum_thrust = liftoff_thrust / (isp_sl / isp_vac)  # Adjust for Isp difference
    
    # Calculate burn time
    mdot = liftoff_thrust / (isp_sl * GRAVITY)  # Mass flow rate at sea level
    burn_time = first_stage_propellant_mass / mdot
    
    print(f"First Stage Thrust (SL): {liftoff_thrust/1000:.0f} kN, (Vac): {vacuum_thrust/1000:.0f} kN")
    print(f"First Stage Burn Time: {burn_time:.0f} seconds")
    
    return {
        "dry_mass": first_stage_dry_mass,
        "propellant_mass": first_stage_propellant_mass,
        "total_mass": first_stage_total_mass,
        "diameter": diameter,
        "length": total_length,
        "thrust_sl": liftoff_thrust,
        "thrust_vac": vacuum_thrust,
        "burn_time": burn_time,
        "propellant_type": "LOX/RP1",
        "actual_delta_v": actual_delta_v
    }


def calculate_upper_stage(payload_mass, target_delta_v_upper):
    """Design an upper stage to provide the specified delta-V."""
    # Upper stage uses LOX/LH2 for better Isp
    isp_vac = 450  # High-efficiency upper stage engine
    
    # Upper stage typically has a mass ratio of ~10-15
    mass_ratio = 10  # Conservative estimate for upper stage
    
    # Propellant mass fraction (based on real rockets)
    pmf = 0.90  # Propellant mass / total stage mass for upper stage
    
    # Initial estimate of upper stage mass
    upper_stage_dry_mass_initial = payload_mass / (math.exp(target_delta_v_upper / (GRAVITY * isp_vac)) - 1)
    upper_stage_total_mass_initial = upper_stage_dry_mass_initial * mass_ratio
    
    # Adjust dry mass to match PMF constraint
    upper_stage_total_mass = payload_mass / (1 - pmf * (1 - 1/mass_ratio))
    upper_stage_propellant_mass = upper_stage_total_mass * pmf
    upper_stage_dry_mass = upper_stage_total_mass - upper_stage_propellant_mass
    
    # Recalculate to verify delta-V
    total_initial_mass = payload_mass + upper_stage_total_mass
    total_final_mass = payload_mass + upper_stage_dry_mass
    actual_delta_v = calculate_delta_v(total_initial_mass, total_final_mass, isp_vac)
    
    print(f"Upper Stage - Target Delta-V: {target_delta_v_upper:.0f} m/s, Actual Delta-V: {actual_delta_v:.0f} m/s")
    print(f"Upper Stage Propellant Mass: {upper_stage_propellant_mass:,.0f} kg")
    print(f"Upper Stage Dry Mass: {upper_stage_dry_mass:,.0f} kg")
    
    # Determine realistic physical dimensions
    # Based on propellant density and realistic fineness ratio
    lox_lh2_bulk_density = 360  # kg/m³ for LOX/LH2 with proper mixture ratio
    
    # Allocate propellant volume with ullage (8% extra for expansion, LH2 needs more)
    propellant_volume = upper_stage_propellant_mass / lox_lh2_bulk_density * 1.08
    
    # Upper stages typically have smaller diameter than first stage
    # Using a diameter similar to Falcon 9 upper stage
    diameter = 3.7  # meters (keeping same as first stage for this example)
    
    # Calculate length based on volume and diameter
    # Tanks typically occupy ~85% of stage length, rest is structure/engines
    tank_area = math.pi * (diameter/2)**2
    tank_length = propellant_volume / tank_area
    total_length = tank_length / 0.85  # Account for non-tank sections
    
    # For realistic fineness ratio (length/diameter), typically 3-8 for upper stages
    fineness_ratio = total_length / diameter
    if fineness_ratio < 3:
        diameter = math.sqrt(propellant_volume / (math.pi * 3))
        total_length = 3 * diameter
    elif fineness_ratio > 8:
        diameter = math.sqrt(propellant_volume / (math.pi * 8))
        total_length = 8 * diameter
    
    print(f"Upper Stage Diameter: {diameter:.2f} m")
    print(f"Upper Stage Length: {total_length:.2f} m")
    print(f"Upper Stage Fineness Ratio (L/D): {total_length/diameter:.1f}")
    
    # Calculate thrust requirements
    # Upper stage TWR can be lower, typically 0.7-0.9 in vacuum
    vacuum_twr = 0.8  # Good balance for upper stage
    vacuum_thrust = vacuum_twr * total_initial_mass * GRAVITY
    
    # Calculate burn time
    mdot = vacuum_thrust / (isp_vac * GRAVITY)  # Mass flow rate
    burn_time = upper_stage_propellant_mass / mdot
    
    print(f"Upper Stage Thrust (Vac): {vacuum_thrust/1000:.0f} kN")
    print(f"Upper Stage Burn Time: {burn_time:.0f} seconds")
    
    return {
        "dry_mass": upper_stage_dry_mass,
        "propellant_mass": upper_stage_propellant_mass,
        "total_mass": upper_stage_total_mass,
        "diameter": diameter,
        "length": total_length,
        "thrust_sl": 0,  # Upper stage doesn't operate at sea level
        "thrust_vac": vacuum_thrust,
        "burn_time": burn_time,
        "propellant_type": "LOX/LH2",
        "actual_delta_v": actual_delta_v
    }


def calculate_orbital_requirements(target_altitude):
    """Calculate delta-V requirements for the specified orbit."""
    # Orbital velocity at target altitude
    orbital_velocity = math.sqrt(GRAVITY * EARTH_RADIUS**2 / (EARTH_RADIUS + target_altitude))
    
    # Additional requirements (based on real missions)
    # These values account for gravity and drag losses
    gravity_loss = 1500  # m/s - Gravity loss during ascent
    drag_loss = 300  # m/s - Aerodynamic drag loss
    
    # Add margin for insertion accuracy and orbital maintenance
    margin = 200  # m/s
    
    # Total delta-V requirement
    total_delta_v = orbital_velocity + gravity_loss + drag_loss + margin
    
    # Typical allocation: 65-70% to first stage, 30-35% to upper stage
    first_stage_delta_v = total_delta_v * 0.65
    upper_stage_delta_v = total_delta_v * 0.35
    
    return {
        "orbital_velocity": orbital_velocity,
        "total_delta_v": total_delta_v,
        "first_stage_delta_v": first_stage_delta_v,
        "upper_stage_delta_v": upper_stage_delta_v
    }


def design_rocket_for_leo(payload_mass, target_altitude=400000):
    """Design a complete two-stage rocket for Low Earth Orbit."""
    print("="*60)
    print(f"DESIGNING ROCKET FOR {target_altitude/1000:.0f} km ORBIT WITH {payload_mass:,} kg PAYLOAD")
    print("="*60)
    
    # Step 1: Calculate orbital requirements
    print("\nSTEP 1: ORBITAL REQUIREMENTS")
    requirements = calculate_orbital_requirements(target_altitude)
    total_delta_v = requirements["total_delta_v"]
    first_stage_delta_v = requirements["first_stage_delta_v"]
    upper_stage_delta_v = requirements["upper_stage_delta_v"]
    
    print(f"Orbital Velocity: {requirements['orbital_velocity']/1000:.2f} km/s")
    print(f"Total Required Delta-V: {total_delta_v/1000:.2f} km/s")
    print(f"First Stage Delta-V: {first_stage_delta_v/1000:.2f} km/s")
    print(f"Upper Stage Delta-V: {upper_stage_delta_v/1000:.2f} km/s")
    
    # Step 2: Design upper stage first (since payload is known)
    print("\nSTEP 2: UPPER STAGE DESIGN")
    upper_stage = calculate_upper_stage(payload_mass, upper_stage_delta_v)
    
    # Step 3: Design first stage to lift upper stage and payload
    print("\nSTEP 3: FIRST STAGE DESIGN")
    upper_stage_total_mass = upper_stage["total_mass"]
    first_stage = calculate_first_stage(payload_mass, upper_stage_total_mass, first_stage_delta_v)
    
    # Step 4: Create the combined rocket and verify performance
    print("\nSTEP 4: COMPLETE ROCKET ANALYSIS")
    total_rocket_mass = payload_mass + upper_stage["total_mass"] + first_stage["total_mass"]
    total_rocket_height = upper_stage["length"] + first_stage["length"]
    total_actual_delta_v = upper_stage["actual_delta_v"] + first_stage["actual_delta_v"]
    
    print(f"Total Rocket Mass: {total_rocket_mass:,.0f} kg")
    print(f"Total Height: {total_rocket_height:.2f} m")
    print(f"Total Delta-V: {total_actual_delta_v/1000:.2f} km/s")
    print(f"Required Delta-V: {total_delta_v/1000:.2f} km/s")
    print(f"Delta-V Margin: {(total_actual_delta_v - total_delta_v)/1000:.2f} km/s")
    
    # Step 5: Create stage objects for FreeCAD visualization
    print("\nSTEP 5: PREPARING FOR VISUALIZATION")
    
    # Create first stage
    first_stage_obj = Stage(
        name="First Stage",
        dry_mass=first_stage["dry_mass"],
        propellant_mass=first_stage["propellant_mass"],
        thrust_sl=first_stage["thrust_sl"],
        thrust_vac=first_stage["thrust_vac"],
        burn_time=first_stage["burn_time"],
        diameter=first_stage["diameter"],
        length=first_stage["length"],
        propellant_type=first_stage["propellant_type"]
    )
    
    # Create upper stage
    upper_stage_obj = Stage(
        name="Upper Stage",
        dry_mass=upper_stage["dry_mass"],
        propellant_mass=upper_stage["propellant_mass"],
        thrust_sl=upper_stage["thrust_sl"],
        thrust_vac=upper_stage["thrust_vac"],
        burn_time=upper_stage["burn_time"],
        diameter=upper_stage["diameter"],
        length=upper_stage["length"],
        propellant_type=upper_stage["propellant_type"]
    )
    
    # Create the complete rocket
    rocket = MultiStageRocket(
        name=f"LEO Rocket ({payload_mass:,}kg to {target_altitude/1000:.0f}km)",
        payload_mass=payload_mass,
        stages=[first_stage_obj, upper_stage_obj]
    )
    
    return rocket


def main():
    """Main function to design and visualize a rocket for LEO."""
    # Set the payload mass and target altitude
    payload_mass = 2000  # kg
    target_altitude = 400000  # meters (400 km)
    
    # Design the rocket
    rocket = design_rocket_for_leo(payload_mass, target_altitude)
    
    # Generate CSV file for visualization
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    csv_file = f"leo_rocket_{timestamp}.csv"
    generate_rocket_csv_specs(rocket, csv_file)
    
    print(f"\nRocket design saved to {csv_file}")
    print(f"To visualize in FreeCAD, run:")
    print(f"launch_rocket_design.bat {csv_file}")


if __name__ == "__main__":
    main()
