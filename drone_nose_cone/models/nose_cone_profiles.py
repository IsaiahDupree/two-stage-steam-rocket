#!/usr/bin/env python
"""
Drone Nose Cone Profiles
A collection of different nose cone profile generators for optimized aerodynamics.

This module provides functions to generate different nose cone profile curves:
- Standard conical (with rounded tip)
- Ogive (parabolic)
- Elliptical
- Von Kármán (Haack series)
- Tangent ogive
"""

import numpy as np
import math


def generate_profile_points(profile_type, length, radius, resolution=100):
    """
    Generate a set of points representing the profile curve of a nose cone.
    
    Args:
        profile_type: Type of profile ('conical', 'ogive', 'elliptical', 'karman', 'tangent')
        length: Length of the nose cone (height)
        radius: Base radius of the nose cone
        resolution: Number of points to generate
    
    Returns:
        points: Numpy array of (x, y) coordinates representing the profile
    """
    if profile_type == 'conical':
        return conical_profile(length, radius, resolution)
    elif profile_type == 'ogive':
        return ogive_profile(length, radius, resolution)
    elif profile_type == 'elliptical':
        return elliptical_profile(length, radius, resolution)
    elif profile_type == 'karman':
        return karman_profile(length, radius, resolution)
    elif profile_type == 'tangent':
        return tangent_ogive_profile(length, radius, resolution)
    else:
        # Default to conical if unknown profile type
        return conical_profile(length, radius, resolution)


def conical_profile(length, radius, resolution=100, tip_radius_factor=0.5):
    """
    Generate a conical profile with a rounded tip.
    
    Args:
        length: Length of the nose cone
        radius: Base radius of the nose cone
        resolution: Number of points to generate
        tip_radius_factor: Size of the rounded tip as a fraction of the base radius
    
    Returns:
        points: Numpy array of (x, y) coordinates
    """
    # Calculate the tip radius
    tip_radius = radius * tip_radius_factor
    
    # Adjust length to account for the rounded tip
    cone_length = length - tip_radius
    
    # Generate points for the conical section
    z = np.linspace(0, cone_length, resolution)
    r = radius * (1 - z / cone_length)
    
    # Generate points for the rounded tip
    theta = np.linspace(0, np.pi/2, resolution)
    tip_z = cone_length + tip_radius * np.sin(theta)
    tip_r = tip_radius * np.cos(theta)
    
    # Combine the sections
    z_points = np.concatenate([z, tip_z])
    r_points = np.concatenate([r, tip_r])
    
    # Return as (z, r) coordinates
    return np.column_stack((z_points, r_points))


def ogive_profile(length, radius, resolution=100):
    """
    Generate a parabolic ogive profile.
    
    A parabolic ogive has a rounded shape that provides good aerodynamic
    performance with reasonable ease of manufacturing. It's a common choice
    for many rockets and high-speed projectiles.
    
    Args:
        length: Length of the nose cone
        radius: Base radius of the nose cone
        resolution: Number of points to generate
    
    Returns:
        points: Numpy array of (x, y) coordinates
    """
    # Generate z-coordinates
    z = np.linspace(0, length, resolution)
    
    # Calculate the radius at each point using a parabolic equation
    # r = radius * (1 - (z/length)^2)
    r = radius * (1 - (z/length)**2)
    
    # Return as (z, r) coordinates
    return np.column_stack((z, r))


def elliptical_profile(length, radius, resolution=100):
    """
    Generate an elliptical profile.
    
    An elliptical nose cone follows the curve of an ellipse. It provides
    good aerodynamic characteristics and often has a slightly blunter tip
    than an ogive profile.
    
    Args:
        length: Length of the nose cone
        radius: Base radius of the nose cone
        resolution: Number of points to generate
    
    Returns:
        points: Numpy array of (x, y) coordinates
    """
    # Generate z-coordinates
    z = np.linspace(0, length, resolution)
    
    # Calculate the radius at each point using an elliptical equation
    # For an ellipse with semi-major axis a=length and semi-minor axis b=radius:
    # r = radius * sqrt(1 - (z/length)^2)
    r = radius * np.sqrt(1 - (z/length)**2)
    
    # Return as (z, r) coordinates
    return np.column_stack((z, r))


def karman_profile(length, radius, resolution=100, C=0):
    """
    Generate a Von Kármán (Haack series) profile.
    
    The Von Kármán nose cone shape is derived from the Haack series and
    is optimized to minimize drag at supersonic speeds.
    C=0 gives the Von Kármán shape, which minimizes drag for a given length and diameter.
    C=1/3 gives the LV-Haack (Sears-Haack) shape, which minimizes drag for a given length and volume.
    C=2/3 gives the LD-Haack shape, which minimizes drag for a given length and diameter.
    
    Args:
        length: Length of the nose cone
        radius: Base radius of the nose cone
        resolution: Number of points to generate
        C: Haack series parameter (0 for Von Kármán, 1/3 for LV-Haack, 2/3 for LD-Haack)
    
    Returns:
        points: Numpy array of (x, y) coordinates
    """
    # Generate theta values
    theta = np.linspace(0, np.pi, resolution)
    
    # Calculate the radius at each theta using the Haack series formula
    r = radius * np.sqrt((theta - np.sin(2*theta)/2) / np.pi + C * np.sin(theta)**3)
    
    # Calculate the z-coordinate for each theta
    z = length * (1 - np.cos(theta)) / 2
    
    # Return as (z, r) coordinates
    return np.column_stack((z, r))


def tangent_ogive_profile(length, radius, resolution=100):
    """
    Generate a tangent ogive profile.
    
    A tangent ogive is formed by a circular arc that is tangent to the 
    cylindrical body at the base and comes to a point at the tip.
    It's widely used in rocketry due to its ease of construction and good performance.
    
    Args:
        length: Length of the nose cone
        radius: Base radius of the nose cone
        resolution: Number of points to generate
    
    Returns:
        points: Numpy array of (x, y) coordinates
    """
    # Calculate the radius of the circular arc
    rho = (length**2 + radius**2) / (2 * radius)
    
    # Calculate the offset from the base
    x_offset = length - np.sqrt(rho**2 - (rho - radius)**2)
    
    # Generate z-coordinates
    z = np.linspace(0, length, resolution)
    
    # Calculate the radius at each point using the tangent ogive formula
    r = np.zeros_like(z)
    for i, zi in enumerate(z):
        if zi <= length:
            r[i] = np.sqrt(rho**2 - (zi - x_offset)**2) - (rho - radius)
    
    # Return as (z, r) coordinates
    return np.column_stack((z, r))


def calculate_profile_metrics(profile, length, radius):
    """
    Calculate key metrics for a nose cone profile.
    
    Args:
        profile: Numpy array of (z, r) coordinates
        length: Length of the nose cone
        radius: Base radius of the nose cone
    
    Returns:
        metrics: Dictionary of calculated metrics
    """
    # Extract z and r values
    z = profile[:, 1]  # Z-axis is the second column in our coordinate system
    r = profile[:, 0]  # Radius is the first column
    
    # Ensure no division by zero or other numerical issues
    if len(z) <= 1 or len(r) <= 1:
        return {
            "volume": 0,
            "surface_area": 0,
            "center_of_mass": length / 2,  # Default to middle
            "fineness_ratio": length / (2 * radius),
            "tip_bluntness": 0
        }
    
    # Make sure points are ordered by z
    if not np.all(np.diff(z) >= 0):
        # Sort points by z value
        sort_idx = np.argsort(z)
        z = z[sort_idx]
        r = r[sort_idx]
    
    # Calculate volume using numerical integration (trapezoidal rule)
    # Volume of revolution = pi * integral(r^2 dz)
    r_squared = np.square(r)
    volume = np.pi * np.trapz(r_squared, z)
    
    # Calculate surface area using numerical integration
    # Surface area of revolution = 2pi * integral(r * sqrt(1 + (dr/dz)^2) dz)
    # Handle numerical differentiation with care
    epsilon = 1e-10  # Small value to avoid division by zero
    dz = np.diff(z)
    dz = np.append(dz, dz[-1])  # Repeat last element for array size matching
    dz = np.maximum(dz, epsilon)  # Ensure no division by zero
    
    # Use np.gradient with explicit spacing to avoid issues
    dr = np.gradient(r, z)
    
    # Calculate the integrand safely
    integrand = r * np.sqrt(1 + np.square(dr))
    # Replace any NaN or inf values with reasonable defaults
    integrand = np.nan_to_num(integrand, nan=0.0, posinf=r, neginf=0.0)
    
    surface_area = 2 * np.pi * np.trapz(integrand, z)
    
    # Calculate center of mass (assuming uniform density)
    # CoM_z = integral(z * r^2 dz) / integral(r^2 dz)
    integral_num = np.trapz(z * r_squared, z)
    integral_denom = np.trapz(r_squared, z)
    
    if abs(integral_denom) < epsilon:
        com_z = length / 2  # Default to middle if denominator is too small
    else:
        com_z = integral_num / integral_denom
    
    # Calculate fineness ratio (length to diameter ratio)
    fineness_ratio = length / (2 * radius)
    
    # Calculate tip bluntness (ratio of tip radius to base radius)
    tip_bluntness = r[0] / radius if r[0] > 0 and radius > 0 else 0
    
    # Return metrics
    return {
        "volume": volume,
        "surface_area": surface_area,
        "center_of_mass": com_z,
        "fineness_ratio": fineness_ratio,
        "tip_bluntness": tip_bluntness
    }


def visualize_profile(profile, title="Nose Cone Profile", show=True, save_path=None):
    """
    Visualize a nose cone profile.
    
    Args:
        profile: Numpy array of (z, r) coordinates
        title: Title for the plot
        show: Whether to display the plot
        save_path: Path to save the plot image (if None, don't save)
    """
    try:
        import matplotlib.pyplot as plt
        
        # Create a figure
        fig, ax = plt.subplots(figsize=(10, 6))
        
        # Extract z and r values
        z = profile[:, 0]
        r = profile[:, 1]
        
        # Plot the top profile
        ax.plot(z, r, 'b-', linewidth=2, label='Profile')
        
        # Plot the bottom profile (mirror)
        ax.plot(z, -r, 'b-', linewidth=2)
        
        # Fill the shape
        ax.fill_between(z, r, -r, alpha=0.2, color='blue')
        
        # Set axis labels and title
        ax.set_xlabel('Length (mm)')
        ax.set_ylabel('Radius (mm)')
        ax.set_title(title)
        
        # Set equal aspect ratio
        ax.set_aspect('equal')
        
        # Add grid
        ax.grid(True, linestyle='--', alpha=0.7)
        
        # Save if requested
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        
        # Show if requested
        if show:
            plt.show()
        else:
            plt.close()
        
    except ImportError:
        print("Matplotlib is required for visualization.")


if __name__ == "__main__":
    # Example usage
    length = 100  # mm
    radius = 50   # mm
    
    # Generate profiles
    conical = conical_profile(length, radius)
    ogive = ogive_profile(length, radius)
    elliptical = elliptical_profile(length, radius)
    karman = karman_profile(length, radius)
    tangent = tangent_ogive_profile(length, radius)
    
    # Visualize profiles
    visualize_profile(conical, "Conical Profile", show=False, 
                     save_path="output/conical_profile.png")
    visualize_profile(ogive, "Ogive Profile", show=False, 
                     save_path="output/ogive_profile.png")
    visualize_profile(elliptical, "Elliptical Profile", show=False, 
                     save_path="output/elliptical_profile.png")
    visualize_profile(karman, "Von Kármán Profile", show=False, 
                     save_path="output/karman_profile.png")
    visualize_profile(tangent, "Tangent Ogive Profile", show=False, 
                     save_path="output/tangent_profile.png")
    
    # Calculate and print metrics for each profile
    profiles = {
        "Conical": conical,
        "Ogive": ogive,
        "Elliptical": elliptical,
        "Von Kármán": karman,
        "Tangent Ogive": tangent
    }
    
    print("Nose Cone Profile Metrics Comparison:")
    print("=====================================")
    for name, profile in profiles.items():
        metrics = calculate_profile_metrics(profile, length, radius)
        print(f"\n{name} Profile:")
        print(f"  Volume: {metrics['volume']:.2f} mm³")
        print(f"  Surface Area: {metrics['surface_area']:.2f} mm²")
        print(f"  Center of Mass: {metrics['center_of_mass']:.2f} mm from tip")
        print(f"  Fineness Ratio: {metrics['fineness_ratio']:.2f}")
        print(f"  Tip Bluntness: {metrics['tip_bluntness']:.4f}")
    
    # Compare all profiles in one plot
    try:
        import matplotlib.pyplot as plt
        
        fig, ax = plt.subplots(figsize=(12, 8))
        
        for name, profile in profiles.items():
            ax.plot(profile[:, 0], profile[:, 1], linewidth=2, label=name)
        
        ax.set_xlabel('Length (mm)')
        ax.set_ylabel('Radius (mm)')
        ax.set_title('Nose Cone Profile Comparison')
        ax.grid(True, linestyle='--', alpha=0.7)
        ax.legend()
        
        plt.savefig("output/profile_comparison.png", dpi=300, bbox_inches='tight')
        plt.show()
    except ImportError:
        print("Matplotlib is required for visualization.")
