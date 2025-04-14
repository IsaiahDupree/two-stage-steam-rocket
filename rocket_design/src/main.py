#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Main script for the Two-Stage Space Vehicle Design Project.
This script coordinates the creation of all rocket components and runs the analysis.
"""

import os
import sys
import math
import datetime

# Add FreeCAD to Python path if not already there
try:
    import FreeCAD
except ImportError:
    # Properly configure FreeCAD Python path - check common installation locations
    possible_paths = [
        r"C:\Program Files\FreeCAD 1.0\bin",
        r"C:\Program Files\FreeCAD 0.20\bin",
        r"C:\Program Files\FreeCAD 0.19\bin",
        r"C:\Program Files\FreeCAD\bin"
    ]
    
    freecad_path = None
    for path in possible_paths:
        if os.path.exists(path):
            freecad_path = path
            break
    
    if freecad_path:
        sys.path.append(freecad_path)
        print(f"Added FreeCAD path: {freecad_path}")
    else:
        print("Error: FreeCAD path not found. Please install FreeCAD or update the path.")
        sys.exit(1)

# Import FreeCAD modules
try:
    import FreeCAD as App
    import Part
    import Draft
    import Mesh
    
    print(f"Successfully imported FreeCAD {App.Version}")
except ImportError as e:
    print(f"Error importing FreeCAD modules: {e}")
    print("Make sure FreeCAD is properly installed and configured.")
    sys.exit(1)

# Import our custom modules
from rocket_geometry import RocketBuilder
from engine_design import PressureVessel, Nozzle
from propulsion_calc import SteamPropulsionAnalysis
from export_tools import ModelExporter
from performance_analysis import RocketPerformanceAnalyzer
from ansys_integration import create_rocket_in_ansys, integrate_with_freecad_model

# Project paths
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(SCRIPT_DIR)
DATA_DIR = os.path.join(PROJECT_DIR, "data")
OUTPUT_DIR = os.path.join(PROJECT_DIR, "output")

def setup_environment():
    """Set up the FreeCAD environment and project folders."""
    print("Setting up FreeCAD environment...")
    
    # Create a new document
    doc = App.newDocument("TwoStageRocket")
    
    # Ensure output directories exist
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    os.makedirs(os.path.join(OUTPUT_DIR, "models"), exist_ok=True)
    os.makedirs(os.path.join(OUTPUT_DIR, "reports"), exist_ok=True)
    os.makedirs(os.path.join(OUTPUT_DIR, "calculations"), exist_ok=True)
    os.makedirs(os.path.join(OUTPUT_DIR, "graphs"), exist_ok=True)
    
    return doc

def load_config():
    """Load rocket configuration from data files."""
    # In a real application, this would load from JSON/YAML/CSV
    # For this example, we'll use hardcoded values
    config = {
        # Overall rocket parameters
        "rocket": {
            "total_length": 5000,  # mm
            "max_diameter": 500,   # mm
            "first_stage_length_ratio": 0.6,
            "nose_cone_length_ratio": 0.15,
            "fin_count": 4
        },
        
        # Pressure vessel parameters
        "pressure_vessel": {
            "design_pressure": 5.0,  # MPa
            "safety_factor": 2.0,
            "material": "stainless_steel",
            "thickness": 5.0,  # mm
            "volume": 0.1  # m³
        },
        
        # Nozzle parameters
        "nozzle": {
            "throat_diameter": 30,  # mm
            "exit_diameter": 150,   # mm
            "length": 300,          # mm
            "convergent_half_angle": 30,  # degrees
            "divergent_half_angle": 15    # degrees
        },
        
        # Propulsion parameters
        "propulsion": {
            "propellant": "water",
            "initial_temperature": 573.15,  # K (300°C)
            "initial_pressure": 5.0,        # MPa
            "propellant_mass": 100,         # kg
            "burn_duration": 60             # seconds
        }
    }
    return config

def main():
    """Main function to execute the rocket design and analysis workflow."""
    print("Starting Two-Stage Space Vehicle Design...")
    
    # Setup FreeCAD environment
    doc = setup_environment()
    
    # Load configuration
    config = load_config()
    
    # Create rocket geometry
    print("Creating rocket geometry...")
    rocket_builder = RocketBuilder(doc, config["rocket"])
    first_stage = rocket_builder.create_first_stage()
    second_stage = rocket_builder.create_second_stage()
    nose_cone = rocket_builder.create_nose_cone()
    fins = rocket_builder.create_fins()
    stage_connector = rocket_builder.create_stage_separation_mechanism()
    
    # Design engine components
    print("Designing propulsion system...")
    pressure_vessel = PressureVessel(doc, config["pressure_vessel"])
    pressure_vessel_obj = pressure_vessel.create_model()
    
    nozzle = Nozzle(doc, config["nozzle"])
    nozzle_obj = nozzle.create_model()
    
    # Run propulsion calculations
    print("Analyzing steam propulsion system...")
    propulsion = SteamPropulsionAnalysis(config["propulsion"])
    thrust = propulsion.calculate_thrust()
    isp = propulsion.calculate_specific_impulse()
    mass_flow = propulsion.calculate_mass_flow_rate()
    
    # Generate reports
    print("Generating analysis reports...")
    propulsion.generate_report(os.path.join(OUTPUT_DIR, "reports", "propulsion_analysis.pdf"))
    pressure_vessel.generate_stress_report(os.path.join(OUTPUT_DIR, "reports", "pressure_analysis.pdf"))
    
    # Export models
    print("Exporting 3D models...")
    exporter = ModelExporter(doc)
    exporter.export_step(os.path.join(OUTPUT_DIR, "models", "two_stage_rocket.step"))
    exporter.export_stl(os.path.join(OUTPUT_DIR, "models", "two_stage_rocket.stl"))
    
    # Run advanced performance analysis
    print("\nPerforming advanced rocket performance analysis...")
    performance_analyzer = RocketPerformanceAnalyzer(config["rocket"], config["pressure_vessel"], config["propulsion"])
    
    # Analyze flow properties and generate performance metrics
    print("Analyzing flow properties throughout propulsion system...")
    flow_properties = performance_analyzer.analyze_flow_properties()
    
    # Simulate trajectory to find maximum altitude
    print("Simulating rocket trajectory...")
    trajectory = performance_analyzer.analyze_trajectory()
    
    # Calculate maximum payload capacity
    print("Calculating maximum payload capacity...")
    payload_info = performance_analyzer.calculate_maximum_payload()
    
    # Generate comprehensive performance graphs
    print("Generating performance visualizations...")
    graph_files = performance_analyzer.generate_performance_graphs(os.path.join(OUTPUT_DIR, "graphs"))
    
    # Print advanced performance summary
    print("\nAdvanced Performance Analysis Results:")
    print(f"Flow Rate: {flow_properties['mass_flow_rate']:.3f} kg/s")
    print(f"Chamber Pressure: {flow_properties['chamber']['pressure']/1e6:.2f} MPa")
    print(f"Throat Velocity: {flow_properties['throat']['velocity']:.2f} m/s (Mach 1.0)")
    print(f"Exit Velocity: {flow_properties['exit']['velocity']:.2f} m/s (Mach {flow_properties['exit']['mach']:.2f})")
    print(f"Exit Pressure: {flow_properties['exit']['pressure']/1e3:.2f} kPa")
    
    print(f"\nMaximum Altitude: {trajectory['apogee']/1000:.2f} km")
    print(f"Maximum Velocity: {trajectory['max_velocity']:.2f} m/s")
    print(f"Maximum Acceleration: {trajectory['max_acceleration']:.2f} m/s²")
    print(f"Maximum Dynamic Pressure: {trajectory['max_q']/1000:.2f} kPa at t={trajectory['max_q_time']:.1f}s")
    
    print(f"\nMaximum Payload Capacity: {payload_info['max_payload']:.2f} kg")
    print(f"Altitude with Max Payload: {payload_info['altitude_with_max_payload']/1000:.2f} km")
    
    print(f"\nGenerated {len(graph_files)} performance visualizations in: {os.path.join(OUTPUT_DIR, 'graphs')}")
    
    # Summary
    print("\nRocket Design Summary:")
    print(f"Total Length: {config['rocket']['total_length']/1000:.2f} m")
    print(f"Diameter: {config['rocket']['max_diameter']/1000:.2f} m")
    print(f"Estimated Thrust: {performance_analyzer.performance_metrics['thrust']:.2f} N")
    print(f"Specific Impulse: {performance_analyzer.performance_metrics['specific_impulse']:.2f} s")
    print(f"Propellant Mass: {config['propulsion']['propellant_mass']:.2f} kg")
    print(f"Burn Duration: {config['propulsion']['burn_duration']:.2f} s")
    
    print("\nDesign and analysis completed successfully.")
    print(f"Results saved to: {OUTPUT_DIR}")
    
    # Save the FreeCAD document
    fcstd_file = os.path.join(OUTPUT_DIR, "models", "two_stage_rocket.FCStd")
    doc.saveAs(fcstd_file)
    
    # Integrate with Ansys for advanced simulation
    print("\nIntegrating with Ansys Geometry for advanced simulation capabilities...")
    try:
        # Method 1: Create directly in Ansys using our configuration
        create_rocket_in_ansys(config["rocket"], config["nozzle"], 
                              output_dir=os.path.join(OUTPUT_DIR, "ansys"))
        
        # Method 2: Import our FreeCAD model into Ansys
        step_file = os.path.join(OUTPUT_DIR, "models", "two_stage_rocket.step")
        if os.path.exists(step_file):
            integrate_with_freecad_model(step_file, 
                                       output_dir=os.path.join(OUTPUT_DIR, "ansys"))
        
        print("Ansys integration completed. Check the reports directory for analysis setup details.")
    except Exception as e:
        print(f"Warning: Ansys integration failed: {e}")
        print("Continuing without Ansys integration.")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
