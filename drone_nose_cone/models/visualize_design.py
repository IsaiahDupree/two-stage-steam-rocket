#!/usr/bin/env python
"""
Drone Nose Cone Visualization
Creates a 2D diagram showing the key dimensions and parameters of the nose cone design.
"""

import matplotlib.pyplot as plt
import numpy as np
import math
import os

# Parameters from specifications
INNER_DIAMETER = 67.0  # mm
OUTER_DIAMETER = 78.0  # mm
BASE_RING_DEPTH = 13.0  # mm
CONE_ANGLE = 52.0  # degrees

# Calculated parameters
INNER_RADIUS = INNER_DIAMETER / 2
OUTER_RADIUS = OUTER_DIAMETER / 2

# Calculate cone height based on angle and radius difference
CONE_HEIGHT = (OUTER_RADIUS - INNER_RADIUS) / math.tan(math.radians(CONE_ANGLE))
# Add some height for the rounded tip
TOTAL_CONE_HEIGHT = CONE_HEIGHT * 1.2

# Nose rounding parameters
TIP_ROUNDING_RADIUS = OUTER_RADIUS * 0.5

def create_visualization(show_plot=True):
    """Create a 2D cross-section visualization of the nose cone
    
    Args:
        show_plot: Whether to show the interactive plot window (default: True)
    """
    # Create figure and axis
    fig, ax = plt.subplots(figsize=(10, 8))
    
    # Set equal aspect ratio
    ax.set_aspect('equal')
    
    # Draw outer profile
    # Base ring - right side
    x_base_outer = [OUTER_RADIUS, OUTER_RADIUS]
    y_base_outer = [0, BASE_RING_DEPTH]
    ax.plot(x_base_outer, y_base_outer, 'b-', linewidth=2)
    
    # Cone outer profile - right side
    cone_tip_y = BASE_RING_DEPTH + CONE_HEIGHT
    x_cone_outer = [OUTER_RADIUS, 0]
    y_cone_outer = [BASE_RING_DEPTH, cone_tip_y]
    ax.plot(x_cone_outer, y_cone_outer, 'b-', linewidth=2)
    
    # Draw inner profile
    # Base ring - right side
    x_base_inner = [INNER_RADIUS, INNER_RADIUS]
    y_base_inner = [0, BASE_RING_DEPTH]
    ax.plot(x_base_inner, y_base_inner, 'r-', linewidth=2)
    
    # Cone inner profile - right side
    x_cone_inner = [INNER_RADIUS, 0]
    y_cone_inner = [BASE_RING_DEPTH, cone_tip_y - TIP_ROUNDING_RADIUS/2]
    ax.plot(x_cone_inner, y_cone_inner, 'r-', linewidth=2)
    
    # Mirror to left side
    ax.plot([-x for x in x_base_outer], y_base_outer, 'b-', linewidth=2)
    ax.plot([-x for x in x_cone_outer], y_cone_outer, 'b-', linewidth=2)
    ax.plot([-x for x in x_base_inner], y_base_inner, 'r-', linewidth=2)
    ax.plot([-x for x in x_cone_inner], y_cone_inner, 'r-', linewidth=2)
    
    # Add rounded tip approximation
    tip_circle = plt.Circle((0, cone_tip_y - TIP_ROUNDING_RADIUS/2), TIP_ROUNDING_RADIUS/2, 
                          fill=False, color='b', linewidth=2)
    ax.add_patch(tip_circle)
    
    # Add annotations
    # Outer diameter
    ax.annotate('', xy=(-OUTER_RADIUS, -5), xytext=(OUTER_RADIUS, -5),
                arrowprops=dict(arrowstyle='<->', color='green'))
    ax.text(0, -10, f'Outer Diameter: {OUTER_DIAMETER} mm', ha='center', color='green')
    
    # Inner diameter
    ax.annotate('', xy=(-INNER_RADIUS, -20), xytext=(INNER_RADIUS, -20),
                arrowprops=dict(arrowstyle='<->', color='green'))
    ax.text(0, -25, f'Inner Diameter: {INNER_DIAMETER} mm', ha='center', color='green')
    
    # Base ring depth
    ax.annotate('', xy=(OUTER_RADIUS + 10, 0), xytext=(OUTER_RADIUS + 10, BASE_RING_DEPTH),
                arrowprops=dict(arrowstyle='<->', color='green'))
    ax.text(OUTER_RADIUS + 20, BASE_RING_DEPTH/2, f'Base Ring: {BASE_RING_DEPTH} mm', va='center', color='green')
    
    # Cone angle
    angle_arc_radius = 30
    angle_start = 0
    angle_end = CONE_ANGLE
    theta = np.linspace(angle_start, angle_end, 50) * np.pi / 180
    x_arc = angle_arc_radius * np.cos(theta)
    y_arc = angle_arc_radius * np.sin(theta) + BASE_RING_DEPTH
    ax.plot(x_arc, y_arc, 'g-', linewidth=1.5)
    ax.text(angle_arc_radius/2, BASE_RING_DEPTH + 10, f'{CONE_ANGLE}°', color='green')
    
    # Total height
    total_height = BASE_RING_DEPTH + TOTAL_CONE_HEIGHT
    ax.annotate('', xy=(-OUTER_RADIUS - 20, 0), xytext=(-OUTER_RADIUS - 20, total_height),
                arrowprops=dict(arrowstyle='<->', color='green'))
    ax.text(-OUTER_RADIUS - 30, total_height/2, f'Total Height: {total_height:.1f} mm', va='center', color='green', rotation=90)
    
    # Set axis limits
    margin = 40
    ax.set_xlim(-OUTER_RADIUS - margin, OUTER_RADIUS + margin)
    ax.set_ylim(-margin, total_height + margin)
    
    # Add title and labels
    ax.set_title('Drone Nose Cone - Cross-Section Diagram', fontsize=16)
    ax.set_xlabel('Radial Distance (mm)')
    ax.set_ylabel('Height (mm)')
    
    # Add grid
    ax.grid(True, linestyle='--', alpha=0.7)
    
    # Add legend
    ax.plot([], [], 'b-', linewidth=2, label='Outer Profile')
    ax.plot([], [], 'r-', linewidth=2, label='Inner Profile')
    ax.legend(loc='lower right')
    
    # Save the figure
    output_dir = os.path.join(os.path.dirname(__file__), "output")
    os.makedirs(output_dir, exist_ok=True)
    plt.savefig(os.path.join(output_dir, 'nose_cone_diagram.png'), dpi=300, bbox_inches='tight')
    plt.savefig(os.path.join(output_dir, 'nose_cone_diagram.pdf'), bbox_inches='tight')
    
    print(f"Diagram saved to {output_dir}")
    
    # Show the plot if requested
    plt.tight_layout()
    if show_plot:
        plt.show()
    else:
        plt.close(fig)  # Close the figure to avoid memory leaks

if __name__ == "__main__":
    # Check if running from command line with --no-display flag
    import sys
    show_plot = "--no-display" not in sys.argv
    create_visualization(show_plot=show_plot)
