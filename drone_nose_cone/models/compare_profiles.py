#!/usr/bin/env python
"""
Drone Nose Cone Profile Comparison
Compare different nose cone profiles for aerodynamic properties and weight optimization.
"""

import os
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
from nose_cone_profiles import (
    generate_profile_points,
    calculate_profile_metrics,
    conical_profile,
    ogive_profile,
    elliptical_profile,
    karman_profile,
    tangent_ogive_profile
)

# Parameters from specifications
INNER_DIAMETER = 67.0  # mm
OUTER_DIAMETER = 78.0  # mm
BASE_RING_DEPTH = 13.0  # mm
CONE_ANGLE = 52.0  # degrees

# Calculated parameters
INNER_RADIUS = INNER_DIAMETER / 2
OUTER_RADIUS = OUTER_DIAMETER / 2

# Calculate cone height based on angle and radius difference
CONE_HEIGHT = (OUTER_RADIUS - INNER_RADIUS) / np.tan(np.radians(CONE_ANGLE))
# Add some height for the rounded tip
TOTAL_CONE_HEIGHT = CONE_HEIGHT * 1.2


def run_profile_comparison(show_plots=True):
    """
    Generate, compare, and visualize different nose cone profiles.
    
    Args:
        show_plots: Whether to display interactive plots (default: True)
    """
    # Define profile types to compare
    profile_types = {
        "Conical": "conical",
        "Ogive": "ogive",
        "Elliptical": "elliptical",
        "Von Kármán": "karman",
        "Tangent Ogive": "tangent"
    }
    
    # Colors for each profile
    colors = {
        "Conical": "blue",
        "Ogive": "red",
        "Elliptical": "green",
        "Von Kármán": "purple",
        "Tangent Ogive": "orange"
    }
    
    # Generate profiles
    profiles = {}
    metrics = {}
    
    for name, profile_type in profile_types.items():
        if profile_type == "conical":
            profile = conical_profile(TOTAL_CONE_HEIGHT, OUTER_RADIUS)
        elif profile_type == "ogive":
            profile = ogive_profile(TOTAL_CONE_HEIGHT, OUTER_RADIUS)
        elif profile_type == "elliptical":
            profile = elliptical_profile(TOTAL_CONE_HEIGHT, OUTER_RADIUS)
        elif profile_type == "karman":
            profile = karman_profile(TOTAL_CONE_HEIGHT, OUTER_RADIUS)
        elif profile_type == "tangent":
            profile = tangent_ogive_profile(TOTAL_CONE_HEIGHT, OUTER_RADIUS)
        
        profiles[name] = profile
        
        # Make sure we have valid data
        if np.any(np.isnan(profile)) or np.any(np.isinf(profile)):
            print(f"Warning: {name} profile contains invalid values. Fixing...")
            profile = np.nan_to_num(profile, nan=0.0, posinf=OUTER_RADIUS, neginf=0.0)
        
        metrics[name] = calculate_profile_metrics(profile, TOTAL_CONE_HEIGHT, OUTER_RADIUS)
    
    # Create output directory
    output_dir = os.path.join(os.path.dirname(__file__), "output")
    os.makedirs(output_dir, exist_ok=True)
    
    # Create a comparison visualization
    plt.figure(figsize=(16, 12))
    gs = GridSpec(2, 2, height_ratios=[2, 1])
    
    # Plot 1: Profile shapes comparison
    ax1 = plt.subplot(gs[0, :])
    
    for name, profile in profiles.items():
        # Correctly extract the z and r coordinates
        r = profile[:, 0]  # First column is radius
        z = profile[:, 1] + BASE_RING_DEPTH  # Second column is z, add base ring height
        
        # Plot the profile
        ax1.plot(z, r, color=colors[name], linewidth=2, label=name)
        # Mirror the profile for visual representation
        ax1.plot(z, -r, color=colors[name], linewidth=2)
        # Fill the shape
        ax1.fill_between(z, r, -r, color=colors[name], alpha=0.1)
    
    # Add base ring rectangle
    rect_x = [0, 0, BASE_RING_DEPTH, BASE_RING_DEPTH]
    rect_y = [INNER_RADIUS, OUTER_RADIUS, OUTER_RADIUS, INNER_RADIUS]
    ax1.fill(rect_x, rect_y, color='gray', alpha=0.3)
    ax1.fill(rect_x, [-y for y in rect_y], color='gray', alpha=0.3)
    
    ax1.set_xlabel('Length (mm)')
    ax1.set_ylabel('Radius (mm)')
    ax1.set_title('Nose Cone Profile Comparison')
    ax1.grid(True, linestyle='--', alpha=0.7)
    ax1.legend(loc='upper right')
    ax1.set_aspect('equal')
    
    # Set reasonable limits
    ax1.set_xlim(0, BASE_RING_DEPTH + TOTAL_CONE_HEIGHT * 1.1)
    ax1.set_ylim(-OUTER_RADIUS * 1.1, OUTER_RADIUS * 1.1)
    
    # Plot 2: Volume comparison
    ax2 = plt.subplot(gs[1, 0])
    
    volumes = [metrics[name]["volume"] for name in profile_types.keys()]
    bars = ax2.bar(profile_types.keys(), volumes, color=[colors[name] for name in profile_types.keys()])
    
    ax2.set_ylabel('Volume (mm³)')
    ax2.set_title('Volume Comparison')
    ax2.grid(True, axis='y', linestyle='--', alpha=0.7)
    
    # Add labels on bars
    for bar in bars:
        height = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                f'{height:.1f}',
                ha='center', va='bottom', rotation=0)
    
    # Plot 3: Surface area and center of mass
    ax3 = plt.subplot(gs[1, 1])
    
    # Set up plots with two y-axes
    ax3_twin = ax3.twinx()
    
    # Plot surface area
    surface_areas = [metrics[name]["surface_area"] for name in profile_types.keys()]
    bars1 = ax3.bar([p + "-SA" for p in profile_types.keys()], surface_areas, 
                   width=0.4, color=[colors[name] for name in profile_types.keys()], alpha=0.7)
    ax3.set_ylabel('Surface Area (mm²)')
    
    # Plot center of mass
    coms = [metrics[name]["center_of_mass"] for name in profile_types.keys()]
    bars2 = ax3_twin.bar([p + "-CM" for p in profile_types.keys()], coms, 
                        width=0.4, color=[colors[name] for name in profile_types.keys()], alpha=0.4)
    ax3_twin.set_ylabel('Center of Mass (mm from tip)')
    
    # Set titles and labels
    ax3.set_title('Surface Area & Center of Mass Comparison')
    ax3.set_xticklabels(profile_types.keys(), rotation=45, ha='right')
    ax3.grid(True, axis='y', linestyle='--', alpha=0.7)
    
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "profile_comparison_full.png"), dpi=300, bbox_inches='tight')
    
    # Close the figure if not showing plots
    if not show_plots:
        plt.close()
    
    # Save metrics to file
    with open(os.path.join(output_dir, "profile_metrics.txt"), "w") as f:
        f.write("Nose Cone Profile Metrics Comparison\n")
        f.write("====================================\n\n")
        
        for name in profile_types.keys():
            f.write(f"{name} Profile:\n")
            f.write(f"  Volume: {metrics[name]['volume']:.2f} mm³\n")
            f.write(f"  Surface Area: {metrics[name]['surface_area']:.2f} mm²\n")
            f.write(f"  Center of Mass: {metrics[name]['center_of_mass']:.2f} mm from tip\n")
            f.write(f"  Fineness Ratio: {metrics[name]['fineness_ratio']:.2f}\n")
            f.write(f"  Tip Bluntness: {metrics[name]['tip_bluntness']:.4f}\n\n")
        
        # Add profile recommendations
        f.write("Profile Recommendations:\n")
        f.write("=======================\n")
        f.write("1. For minimum drag at supersonic speeds: Von Kármán\n")
        f.write("2. For minimum drag at subsonic/transonic speeds: Tangent Ogive\n")
        f.write("3. For ease of manufacturing: Conical\n")
        f.write("4. For balanced performance: Elliptical\n")
        f.write("5. For optimized volume-to-drag ratio: Ogive\n\n")
        
        f.write("Note: The optimal profile depends on the specific application and flight regime.\n")
        f.write("For lightweight drone applications, the elliptical or ogive profiles often provide\n")
        f.write("a good balance between aerodynamic performance and ease of manufacturing.\n")
    
    print(f"Profile comparison completed. Results saved to {output_dir}")
    
    # Create separate plots for each profile
    for name, profile in profiles.items():
        plt.figure(figsize=(8, 6))
        
        # Correctly extract the z and r coordinates
        r = profile[:, 0]  # First column is radius
        z = profile[:, 1] + BASE_RING_DEPTH  # Second column is z, add base ring height
        
        # Plot the profile
        plt.plot(z, r, color=colors[name], linewidth=2, label=name)
        # Mirror the profile for visual representation
        plt.plot(z, -r, color=colors[name], linewidth=2)
        # Fill the shape
        plt.fill_between(z, r, -r, color=colors[name], alpha=0.2)
        
        # Add base ring rectangle
        rect_x = [0, 0, BASE_RING_DEPTH, BASE_RING_DEPTH]
        rect_y = [INNER_RADIUS, OUTER_RADIUS, OUTER_RADIUS, INNER_RADIUS]
        plt.fill(rect_x, rect_y, color='gray', alpha=0.3)
        plt.fill(rect_x, [-y for y in rect_y], color='gray', alpha=0.3)
        
        plt.xlabel('Length (mm)')
        plt.ylabel('Radius (mm)')
        plt.title(f'{name} Nose Cone Profile')
        plt.grid(True, linestyle='--', alpha=0.7)
        plt.axis('equal')
        
        # Set reasonable limits
        plt.xlim(0, BASE_RING_DEPTH + TOTAL_CONE_HEIGHT * 1.1)
        plt.ylim(-OUTER_RADIUS * 1.1, OUTER_RADIUS * 1.1)
        
        # Add metrics in a text box
        textstr = f"Volume: {metrics[name]['volume']:.2f} mm³\n" \
                 f"Surface Area: {metrics[name]['surface_area']:.2f} mm²\n" \
                 f"Center of Mass: {metrics[name]['center_of_mass']:.2f} mm from tip\n" \
                 f"Fineness Ratio: {metrics[name]['fineness_ratio']:.2f}"
        
        props = dict(boxstyle='round', facecolor='white', alpha=0.5)
        plt.text(0.05, 0.95, textstr, transform=plt.gca().transAxes, fontsize=9,
                verticalalignment='top', bbox=props)
        
        plt.tight_layout()
        plt.savefig(os.path.join(output_dir, f"{name.lower().replace(' ', '_')}_profile.png"), 
                   dpi=300, bbox_inches='tight')
        plt.close()  # Always close individual profile plots
    
    return profiles, metrics


def calculate_aerodynamic_coefficients(profiles, show_plots=True):
    """
    Estimate aerodynamic coefficients for different profiles.
    Note: This is a simplified model for comparison purposes only.
    """
    # Mach numbers to evaluate
    mach_numbers = np.linspace(0.1, 2.0, 20)
    
    # Dictionary to store coefficient data
    cd_data = {}
    
    # Simple empirical model for different shapes - THIS IS APPROXIMATE
    # Based on general trends from aerodynamic studies
    for name, profile in profiles.items():
        cd_values = []
        
        for mach in mach_numbers:
            # Extract profile fineness ratio (length to diameter)
            fineness = TOTAL_CONE_HEIGHT / (2 * OUTER_RADIUS)
            
            # Base drag coefficient (very simplified model)
            if name == "Conical":
                cd_base = 0.12 + 0.05 * np.exp(-fineness)
            elif name == "Ogive":
                cd_base = 0.08 + 0.06 * np.exp(-1.2 * fineness)
            elif name == "Elliptical":
                cd_base = 0.09 + 0.05 * np.exp(-1.1 * fineness)
            elif name == "Von Kármán":
                cd_base = 0.05 + 0.07 * np.exp(-1.3 * fineness)
            elif name == "Tangent Ogive":
                cd_base = 0.07 + 0.06 * np.exp(-1.2 * fineness)
            else:
                cd_base = 0.1
            
            # Mach number effects (transonic bump)
            if 0.8 <= mach <= 1.2:
                mach_factor = 0.1 * np.exp(-10 * (mach - 1.0)**2)
            else:
                mach_factor = 0
            
            # Different shapes have different transonic behavior
            if name == "Von Kármán":
                mach_factor *= 0.6  # Reduced transonic drag
            elif name == "Conical":
                mach_factor *= 1.2  # Increased transonic drag
            
            # Calculate final coefficient
            cd = cd_base + mach_factor
            
            cd_values.append(cd)
        
        cd_data[name] = cd_values
    
    # Create a plot of drag coefficients vs Mach number
    plt.figure(figsize=(10, 6))
    
    colors = {
        "Conical": "blue",
        "Ogive": "red",
        "Elliptical": "green",
        "Von Kármán": "purple",
        "Tangent Ogive": "orange"
    }
    
    for name, cd_values in cd_data.items():
        plt.plot(mach_numbers, cd_values, linewidth=2, label=name, color=colors[name])
    
    plt.axvline(x=1.0, color='gray', linestyle='--', alpha=0.5, label='Mach 1')
    
    plt.xlabel('Mach Number')
    plt.ylabel('Drag Coefficient (Cd)')
    plt.title('Estimated Drag Coefficients vs. Mach Number')
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.legend()
    
    # Save the plot
    output_dir = os.path.join(os.path.dirname(__file__), "output")
    plt.savefig(os.path.join(output_dir, "drag_coefficient_comparison.png"), dpi=300, bbox_inches='tight')
    
    # Close the figure if not showing plots
    if not show_plots:
        plt.close()
    
    return cd_data


if __name__ == "__main__":
    # Check for command line arguments
    import sys
    show_plots = "--no-display" not in sys.argv
    
    # Run profile comparison
    profiles, metrics = run_profile_comparison(show_plots=show_plots)
    
    # Calculate and plot aerodynamic coefficients
    cd_data = calculate_aerodynamic_coefficients(profiles, show_plots=show_plots)
    
    # Print summary
    print("\nProfile Comparison Summary:")
    print("===========================")
    
    # Find optimal profiles for different criteria - handle potential negative or invalid values
    volume_data = [(name, metrics[name]["volume"]) for name in metrics.keys() 
                  if metrics[name]["volume"] > 0 and not np.isnan(metrics[name]["volume"])]
    min_volume = min(volume_data, key=lambda x: x[1]) if volume_data else ("None", 0)
    
    surface_area_data = [(name, metrics[name]["surface_area"]) for name in metrics.keys() 
                        if metrics[name]["surface_area"] > 0 and not np.isnan(metrics[name]["surface_area"])]
    min_surface = min(surface_area_data, key=lambda x: x[1]) if surface_area_data else ("None", 0)
    
    com_data = [(name, metrics[name]["center_of_mass"]) for name in metrics.keys() 
                if metrics[name]["center_of_mass"] > 0 and not np.isnan(metrics[name]["center_of_mass"]) 
                and metrics[name]["center_of_mass"] < TOTAL_CONE_HEIGHT]
    best_com = min(com_data, key=lambda x: x[1]) if com_data else ("None", 0)
    
    # Print recommendations
    print(f"Lightest design (minimum volume): {min_volume[0]} ({min_volume[1]:.2f} mm³)")
    print(f"Minimum surface area: {min_surface[0]} ({min_surface[1]:.2f} mm²)")
    print(f"Best center of mass (closest to tip): {best_com[0]} ({best_com[1]:.2f} mm from tip)")
    print("\nBased on aerodynamic performance:")
    print("- Best for subsonic flight: Elliptical or Tangent Ogive")
    print("- Best for transonic flight: Von Kármán")
    print("- Best for supersonic flight: Von Kármán")
    print("- Easiest to manufacture: Conical")
    print("\nFor the drone nose cone application (likely subsonic):")
    print("Recommended profile: Elliptical")
    print("  - Good balance of aerodynamic performance and weight")
    print("  - Relatively easy to 3D print")
