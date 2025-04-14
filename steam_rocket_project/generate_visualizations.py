#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Generate Visualizations for Steam Rocket Proposal

This script creates professional visualizations for the steam rocket proposal document,
including thrust profiles, pressure vessel diagrams, and performance charts.
"""

import os
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Rectangle, Polygon
from steam_rocket_calculator import SteamRocketCalculator

# Set up a professional style for plots
plt.style.use('seaborn-v0_8-whitegrid')
plt.rcParams['font.family'] = 'serif'
plt.rcParams['font.serif'] = ['Times New Roman', 'DejaVu Serif', 'Times', 'Palatino', 'serif']

def generate_thrust_profile(calculator, output_dir='.'):
    """Generate a thrust profile plot showing thrust over burn time."""
    # Run analysis to ensure we have results
    if not hasattr(calculator, 'results') or not calculator.results:
        calculator.run_complete_analysis()
    
    # Get initial thrust and burn time
    initial_thrust = calculator.results['thrust']
    burn_time = calculator.results['burn_time']
    
    # Create time points for plotting
    time_points = np.linspace(0, burn_time * 1.1, 100)
    
    # Calculate thrust at each time point (assumes linear pressure decrease)
    thrust_values = []
    for t in time_points:
        if t <= burn_time:
            # Simple model: thrust decreases linearly as pressure decreases
            thrust_ratio = 1 - (t / burn_time)
            thrust_values.append(initial_thrust * thrust_ratio)
        else:
            thrust_values.append(0)
    
    # Create the plot
    plt.figure(figsize=(10, 6))
    plt.plot(time_points, [t/1000 for t in thrust_values], 'b-', linewidth=2.5)
    
    # Fill beneath the curve
    plt.fill_between(time_points, [t/1000 for t in thrust_values], 0, 
                     alpha=0.2, color='blue')
    
    # Add annotations
    max_thrust = initial_thrust/1000
    plt.annotate(f'Maximum Thrust: {max_thrust:.2f} kN', 
                 xy=(0, max_thrust), 
                 xytext=(burn_time/4, max_thrust*0.9),
                 arrowprops=dict(arrowstyle='->', lw=1.5),
                 fontsize=12)
    
    # Add total impulse annotation
    total_impulse = calculator.results['total_impulse']/1000  # kN·s
    plt.annotate(f'Total Impulse: {total_impulse:.2f} kN·s', 
                 xy=(burn_time/2, max_thrust/2), 
                 xytext=(burn_time*0.6, max_thrust*0.6),
                 arrowprops=dict(arrowstyle='->', lw=1.5),
                 fontsize=12)
    
    # Customize the plot
    plt.title('Thrust Profile Over Burn Duration', fontsize=16)
    plt.xlabel('Time (seconds)', fontsize=14)
    plt.ylabel('Thrust (kN)', fontsize=14)
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.tight_layout()
    
    # Save the figure
    output_file = os.path.join(output_dir, 'thrust_profile.png')
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    plt.close()
    
    return output_file

def generate_pressure_vessel_diagram(calculator, output_dir='.'):
    """Generate a technical diagram of the pressure vessel with dimensions."""
    # Run analysis to ensure we have results
    if not hasattr(calculator, 'results') or not calculator.results:
        calculator.run_complete_analysis()
    
    # Get key dimensions
    vessel_diameter = calculator.results['vessel_diameter']
    vessel_length = calculator.results['vessel_length']
    wall_thickness = calculator.results['wall_thickness']
    
    # Create the figure
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Define the vessel dimensions for drawing
    # The vessel is drawn horizontally
    vessel_radius = vessel_diameter / 2
    inner_radius = vessel_radius - wall_thickness
    
    # Draw the outer vessel outline
    rectangle = Rectangle(
        (0, -vessel_radius), 
        vessel_length, 
        vessel_diameter, 
        fill=False, 
        linewidth=2,
        edgecolor='blue'
    )
    ax.add_patch(rectangle)
    
    # Draw the inner vessel outline (hollow part)
    rectangle_inner = Rectangle(
        (0, -inner_radius),
        vessel_length,
        inner_radius * 2,
        fill=False,
        linewidth=2,
        linestyle='--',
        edgecolor='red'
    )
    ax.add_patch(rectangle_inner)
    
    # Add hemispherical end caps
    left_cap = Circle(
        (0, 0), 
        vessel_radius, 
        fill=False, 
        linewidth=2,
        edgecolor='blue'
    )
    ax.add_patch(left_cap)
    
    right_cap = Circle(
        (vessel_length, 0), 
        vessel_radius, 
        fill=False, 
        linewidth=2,
        edgecolor='blue'
    )
    ax.add_patch(right_cap)
    
    # Add inner caps
    left_cap_inner = Circle(
        (0, 0), 
        inner_radius, 
        fill=False, 
        linewidth=2,
        linestyle='--',
        edgecolor='red'
    )
    ax.add_patch(left_cap_inner)
    
    right_cap_inner = Circle(
        (vessel_length, 0), 
        inner_radius, 
        fill=False, 
        linewidth=2,
        linestyle='--',
        edgecolor='red'
    )
    ax.add_patch(right_cap_inner)
    
    # Add dimensions and labels
    # Diameter dimension line
    ax.annotate('', xy=(-0.1, -vessel_radius), xytext=(-0.1, vessel_radius),
               arrowprops=dict(arrowstyle='<->', lw=1.5))
    ax.text(-0.3, 0, f'Diameter\n{vessel_diameter*100:.1f} cm', 
            ha='center', va='center', fontsize=10, rotation=90)
    
    # Length dimension line
    ax.annotate('', xy=(0, vessel_radius*1.2), xytext=(vessel_length, vessel_radius*1.2),
               arrowprops=dict(arrowstyle='<->', lw=1.5))
    ax.text(vessel_length/2, vessel_radius*1.4, f'Length: {vessel_length*100:.1f} cm', 
            ha='center', va='center', fontsize=10)
    
    # Wall thickness label
    ax.annotate('Wall Thickness', xy=(vessel_length/2, inner_radius),
               xytext=(vessel_length/2, inner_radius/2),
               arrowprops=dict(arrowstyle='->', lw=1.5),
               fontsize=10)
    ax.text(vessel_length/2, inner_radius/3, f'{wall_thickness*1000:.2f} mm', 
            ha='center', va='center', fontsize=10)
    
    # Add title and adjust view
    plt.title('Steam Rocket Pressure Vessel Cross-Section', fontsize=16)
    ax.set_xlim(-0.5, vessel_length + 0.5)
    ax.set_ylim(-vessel_radius*1.5, vessel_radius*1.5)
    
    ax.set_aspect('equal')
    ax.axis('off')
    plt.tight_layout()
    
    # Save the figure
    output_file = os.path.join(output_dir, 'pressure_vessel_diagram.png')
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    plt.close()
    
    return output_file

def generate_two_stage_rocket_diagram(first_stage, second_stage, output_dir='.'):
    """Generate a technical diagram of the complete two-stage rocket."""
    # Run analysis to ensure we have results
    if not hasattr(first_stage, 'results') or not first_stage.results:
        first_stage.run_complete_analysis()
    if not hasattr(second_stage, 'results') or not second_stage.results:
        second_stage.run_complete_analysis()
    
    # Get key dimensions
    fs_diameter = first_stage.results['vessel_diameter']
    fs_length = first_stage.results['vessel_length']
    fs_nozzle_exit = first_stage.results['exit_diameter']
    
    ss_diameter = second_stage.results['vessel_diameter']
    ss_length = second_stage.results['vessel_length']
    ss_nozzle_exit = second_stage.results['exit_diameter']
    
    # Create figure
    fig, ax = plt.subplots(figsize=(12, 8))
    
    # Define colors
    first_stage_color = '#1f77b4'  # Blue
    second_stage_color = '#ff7f0e'  # Orange
    nozzle_color = '#2ca02c'  # Green
    
    # Draw first stage (at the bottom)
    # Main body
    fs_y_offset = 0
    fs_body = Rectangle(
        (0, fs_y_offset), 
        fs_length, 
        fs_diameter, 
        fill=True, 
        alpha=0.3,
        linewidth=2,
        edgecolor=first_stage_color,
        facecolor=first_stage_color
    )
    ax.add_patch(fs_body)
    
    # First stage nozzle (simplified as a triangle)
    nozzle_height = fs_diameter * 0.5  # Approximate nozzle height
    nozzle_x = [fs_length, fs_length + nozzle_height, fs_length]
    nozzle_y = [fs_y_offset, fs_y_offset + fs_diameter/2, fs_y_offset + fs_diameter]
    
    nozzle = Polygon(
        np.array([nozzle_x, nozzle_y]).T,
        fill=True,
        alpha=0.5,
        linewidth=2,
        edgecolor=nozzle_color,
        facecolor=nozzle_color
    )
    ax.add_patch(nozzle)
    
    # Draw second stage (on top of first stage)
    # Calculate offset to center the second stage on top of the first stage
    ss_y_offset = fs_y_offset + fs_diameter
    ss_x_offset = (fs_length - ss_length) / 2  # Center second stage on first stage
    
    # Main body
    ss_body = Rectangle(
        (ss_x_offset, ss_y_offset), 
        ss_length, 
        ss_diameter, 
        fill=True, 
        alpha=0.3,
        linewidth=2,
        edgecolor=second_stage_color,
        facecolor=second_stage_color
    )
    ax.add_patch(ss_body)
    
    # Second stage nozzle (simplified)
    ss_nozzle_height = ss_diameter * 0.4  # Approximate nozzle height
    ss_nozzle_x = [ss_x_offset + ss_length/2 - ss_nozzle_exit/3, ss_x_offset + ss_length/2, ss_x_offset + ss_length/2 + ss_nozzle_exit/3]
    ss_nozzle_y = [ss_y_offset, ss_y_offset - ss_nozzle_height, ss_y_offset]
    
    ss_nozzle = Polygon(
        np.array([ss_nozzle_x, ss_nozzle_y]).T,
        fill=True,
        alpha=0.5,
        linewidth=2,
        edgecolor=nozzle_color,
        facecolor=nozzle_color
    )
    ax.add_patch(ss_nozzle)
    
    # Add a nose cone to the second stage
    nosecone_height = ss_diameter * 1.5
    nosecone_x = [ss_x_offset, ss_x_offset + ss_length/2, ss_x_offset + ss_length]
    nosecone_y = [ss_y_offset + ss_diameter, ss_y_offset + ss_diameter + nosecone_height, ss_y_offset + ss_diameter]
    
    nosecone = Polygon(
        np.array([nosecone_x, nosecone_y]).T,
        fill=True,
        alpha=0.3,
        linewidth=2,
        edgecolor=second_stage_color,
        facecolor=second_stage_color
    )
    ax.add_patch(nosecone)
    
    # Add separation plane indicator
    ax.plot([0, fs_length], [ss_y_offset, ss_y_offset], 'r--', linewidth=2)
    ax.text(fs_length/2, ss_y_offset * 1.01, 'Separation Plane', 
            ha='center', va='bottom', fontsize=12, color='red')
    
    # Add labels
    ax.text(fs_length/2, fs_y_offset + fs_diameter/2, 'First Stage',
            ha='center', va='center', fontsize=14, color='white')
    
    ax.text(ss_x_offset + ss_length/2, ss_y_offset + ss_diameter/2, 'Second Stage',
            ha='center', va='center', fontsize=14, color='white')
    
    ax.text(ss_x_offset + ss_length/2, ss_y_offset + ss_diameter + nosecone_height/2, 'Payload Fairing',
            ha='center', va='center', fontsize=12, color='white')
    
    # Add title and adjust view
    plt.title('Two-Stage Steam Rocket Configuration', fontsize=16)
    
    # Add dimensions
    total_height = ss_y_offset + ss_diameter + nosecone_height
    ax.text(fs_length + nozzle_height + 0.5, total_height/2, 
            f'Total Height: {(total_height + nozzle_height)*100:.1f} cm',
            ha='left', va='center', fontsize=12, rotation=90)
    
    ax.annotate('', xy=(fs_length + nozzle_height + 0.3, 0), 
                xytext=(fs_length + nozzle_height + 0.3, total_height),
                arrowprops=dict(arrowstyle='<->', lw=1.5))
    
    # Set equal aspect ratio and remove axis
    ax.set_aspect('equal')
    ax.set_xlim(-0.5, fs_length + nozzle_height + 2)
    ax.set_ylim(-0.5, total_height + 0.5)
    ax.axis('off')
    
    plt.tight_layout()
    
    # Save the figure
    output_file = os.path.join(output_dir, 'two_stage_rocket_diagram.png')
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    plt.close()
    
    return output_file

def generate_performance_comparison(output_dir='.'):
    """Generate a comparison chart of different steam rocket configurations."""
    # Define different configurations to compare
    configurations = [
        {
            'name': 'Low Pressure',
            'pressure': 1.0e6,  # 1 MPa
            'temperature': (200 + 273.15),  # 200°C
            'isp': 60,  # estimated
            'thrust': 200  # N
        },
        {
            'name': 'Medium Pressure',
            'pressure': 2.0e6,  # 2 MPa
            'temperature': (350 + 273.15),  # 350°C
            'isp': 80,  # estimated
            'thrust': 500  # N
        },
        {
            'name': 'High Pressure',
            'pressure': 5.0e6,  # 5 MPa
            'temperature': (500 + 273.15),  # 500°C
            'isp': 100,  # estimated
            'thrust': 1200  # N
        },
        {
            'name': 'Two-Stage System',
            'pressure': 3.0e6,  # 3 MPa
            'temperature': (400 + 273.15),  # 400°C
            'isp': 90,  # estimated
            'thrust': 2000  # N (combined)
        }
    ]
    
    # Create figure with subplots
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 6))
    
    # Data for plotting
    names = [config['name'] for config in configurations]
    pressures = [config['pressure']/1e6 for config in configurations]  # MPa
    isps = [config['isp'] for config in configurations]
    thrusts = [config['thrust'] for config in configurations]
    
    # Bar colors
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728']
    
    # Pressure comparison
    bars1 = ax1.bar(names, pressures, color=colors, alpha=0.7)
    ax1.set_ylabel('Chamber Pressure (MPa)', fontsize=12)
    ax1.set_title('Pressure Comparison', fontsize=14)
    ax1.grid(axis='y', linestyle='--', alpha=0.7)
    
    # Add values on top of bars
    for bar in bars1:
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                f'{height:.1f}',
                ha='center', va='bottom')
    
    # Performance comparison (ISP and Thrust together)
    ax2twin = ax2.twinx()
    
    # Plot ISP as bars
    bars2 = ax2.bar(names, isps, color=colors, alpha=0.7)
    ax2.set_ylabel('Specific Impulse (s)', fontsize=12)
    ax2.set_title('Performance Metrics', fontsize=14)
    ax2.grid(axis='y', linestyle='--', alpha=0.7)
    
    # Add values on top of bars
    for bar in bars2:
        height = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2., height + 2,
                f'{height:.0f}',
                ha='center', va='bottom')
    
    # Plot Thrust as points
    ax2twin.plot(names, thrusts, 'ro-', linewidth=2, markersize=8)
    ax2twin.set_ylabel('Thrust (N)', fontsize=12)
    
    # Add thrust values
    for i, thrust in enumerate(thrusts):
        ax2twin.annotate(f'{thrust:.0f}N', 
                         xy=(i, thrust),
                         xytext=(i, thrust + 100),
                         ha='center',
                         fontsize=9)
    
    # Set y-limit for thrust to avoid overlap
    ax2twin.set_ylim(0, max(thrusts) * 1.3)
    
    # Legend
    ax2.legend(['Specific Impulse'], loc='upper left')
    ax2twin.legend(['Thrust'], loc='upper right')
    
    plt.tight_layout()
    
    # Save the figure
    output_file = os.path.join(output_dir, 'performance_comparison.png')
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    plt.close()
    
    return output_file

def main():
    """Generate all visualizations for the proposal document."""
    print("Generating visualizations for the proposal document...")
    
    # Create output directory if it doesn't exist
    output_dir = 'visualizations'
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Create calculators for both stages
    # First stage - higher pressure for initial thrust
    first_stage = SteamRocketCalculator()
    first_stage.set_pressure_parameters(
        chamber_pressure=3.0e6,  # 3 MPa
        chamber_temperature=450 + 273.15,  # 450°C
    )
    first_stage.set_geometry_parameters(
        throat_diameter=0.025,  # 25 mm
        exit_diameter=0.075,  # 75 mm (3:1 expansion)
        vessel_diameter=0.3,    # 30 cm
        vessel_length=0.6       # 60 cm
    )
    first_stage.run_complete_analysis()
    
    # Second stage - optimized for vacuum performance
    second_stage = SteamRocketCalculator()
    second_stage.set_pressure_parameters(
        chamber_pressure=2.0e6,  # 2 MPa
        chamber_temperature=400 + 273.15,  # 400°C
    )
    second_stage.set_geometry_parameters(
        throat_diameter=0.015,  # 15 mm
        exit_diameter=0.06,  # 60 mm (4:1 expansion for vacuum)
        vessel_diameter=0.2,    # 20 cm
        vessel_length=0.4       # 40 cm
    )
    second_stage.run_complete_analysis()
    
    # Generate visualizations
    thrust_profile_file = generate_thrust_profile(first_stage, output_dir)
    print(f"Created thrust profile: {thrust_profile_file}")
    
    pressure_vessel_file = generate_pressure_vessel_diagram(first_stage, output_dir)
    print(f"Created pressure vessel diagram: {pressure_vessel_file}")
    
    two_stage_file = generate_two_stage_rocket_diagram(first_stage, second_stage, output_dir)
    print(f"Created two-stage rocket diagram: {two_stage_file}")
    
    performance_file = generate_performance_comparison(output_dir)
    print(f"Created performance comparison chart: {performance_file}")
    
    print("All visualizations generated successfully!")

if __name__ == "__main__":
    main()
