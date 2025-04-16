"""
Advanced Rocket Performance Test Demonstration
Tests the AI's ability to handle complex performance-related design requests
"""

import os
import sys
import json
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime

# Configure paths
TEST_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(TEST_DIR)
sys.path.append(PROJECT_ROOT)

# Define an extended rocket model for testing with propulsion parameters
sample_rocket_model = {
    "name": "Performance Test Rocket",
    "firstStage": {
        "diameter": 1.2,
        "length": 7.0,
        "material": "aluminum-2024",
        "propellant": "LOX/RP-1",
        "engineCount": 1,
        "dryMass": 800,  # kg
        "propellantMass": 3500,  # kg
        "thrustSL": 40000,  # N
        "thrustVac": 45000,  # N
        "isp": 290  # s
    },
    "secondStage": {
        "diameter": 0.8,
        "length": 3.0,
        "material": "aluminum-7075",
        "propellant": "LOX/RP-1",
        "engineCount": 1,
        "dryMass": 350,  # kg
        "propellantMass": 1200,  # kg
        "thrustVac": 20000,  # N
        "isp": 320  # s
    },
    "noseCone": {
        "shape": "conical",
        "length": 1.0,
        "material": "aluminum-7075"
    },
    "fins": {
        "count": 4,
        "shape": "trapezoidal",
        "span": 0.5,
        "material": "aluminum-2024"
    },
    "payload": {
        "mass": 200  # kg
    }
}

# Material properties for calculations
material_properties = {
    "aluminum-2024": {"density": 2780, "yield_strength": 324, "cost_per_kg": 15},
    "aluminum-7075": {"density": 2810, "yield_strength": 503, "cost_per_kg": 22},
    "titanium-6al4v": {"density": 4430, "yield_strength": 880, "cost_per_kg": 120},
    "carbon-fiber": {"density": 1600, "yield_strength": 600, "cost_per_kg": 100},
    "stainless-steel-304": {"density": 8000, "yield_strength": 215, "cost_per_kg": 8}
}

# Propellant properties
propellant_properties = {
    "LOX/LH2": {"isp_vac": 450, "isp_sl": 370, "density": 360, "cost_per_kg": 4.5},
    "LOX/RP-1": {"isp_vac": 350, "isp_sl": 300, "density": 1030, "cost_per_kg": 2.5},
    "N2O4/UDMH": {"isp_vac": 320, "isp_sl": 280, "density": 1200, "cost_per_kg": 8.0},
    "water/steam": {"isp_vac": 70, "isp_sl": 60, "density": 1000, "cost_per_kg": 0.1}
}

def calculate_delta_v(rocket_model):
    """Calculate delta-v for a rocket using the Tsiolkovsky rocket equation"""
    # Constants
    g0 = 9.81  # Standard gravity (m/s²)
    
    # Extract stage information
    first_stage = rocket_model["firstStage"]
    second_stage = rocket_model["secondStage"]
    payload_mass = rocket_model["payload"]["mass"]
    
    # Calculate stage masses
    first_stage_dry_mass = first_stage["dryMass"]
    first_stage_prop_mass = first_stage["propellantMass"]
    second_stage_dry_mass = second_stage["dryMass"]
    second_stage_prop_mass = second_stage["propellantMass"]
    
    # Calculate mass ratios
    initial_mass = first_stage_dry_mass + first_stage_prop_mass + second_stage_dry_mass + second_stage_prop_mass + payload_mass
    after_first_burn = initial_mass - first_stage_prop_mass
    after_stage_sep = after_first_burn - first_stage_dry_mass
    final_mass = after_stage_sep - second_stage_prop_mass
    
    first_stage_mass_ratio = initial_mass / after_first_burn
    second_stage_mass_ratio = after_stage_sep / final_mass
    
    # Get ISP values
    first_stage_isp = first_stage["isp"]
    second_stage_isp = second_stage["isp"]
    
    # Calculate delta-v
    first_stage_dv = g0 * first_stage_isp * np.log(first_stage_mass_ratio)
    second_stage_dv = g0 * second_stage_isp * np.log(second_stage_mass_ratio)
    total_dv = first_stage_dv + second_stage_dv
    
    return {
        "first_stage_dv": first_stage_dv,
        "second_stage_dv": second_stage_dv,
        "total_dv": total_dv,
        "first_stage_mass_ratio": first_stage_mass_ratio,
        "second_stage_mass_ratio": second_stage_mass_ratio,
        "initial_mass": initial_mass,
        "final_mass": final_mass,
        "payload_fraction": payload_mass / initial_mass * 100  # as percentage
    }

def estimate_altitude(rocket_model, delta_v_data):
    """Estimate maximum altitude using a simplified model"""
    # This is a very simplified model - real altitude calculations would be much more complex
    # and would involve detailed trajectory simulation
    
    # Constants
    g0 = 9.81  # Standard gravity (m/s²)
    earth_radius = 6371000  # m
    
    # Simplistic altitude estimation based on delta-v
    # Accounting for gravity losses and drag (rough approximations)
    gravity_losses = 1500  # m/s (typical value for vertical launch)
    drag_losses = 500  # m/s (simplified)
    
    # Effective delta-v after losses
    effective_dv = delta_v_data["total_dv"] - gravity_losses - drag_losses
    
    # If effective delta-v is negative, the rocket won't leave the ground
    if effective_dv <= 0:
        return 0
    
    # Simple estimation for suborbital flights
    if effective_dv < 7800:  # Orbital velocity is ~7.8 km/s
        # Simplified equation for maximum height of a ballistic trajectory
        max_height = (effective_dv**2) / (2 * g0)
        return max_height
    else:
        # For orbital-capable rockets, return low Earth orbit altitude
        return 400000  # 400 km, typical LEO
    
def generate_performance_chart(before_data, after_data, output_file=None):
    """Generate a performance comparison chart"""
    metrics = [
        ('First Stage ΔV (m/s)', before_data["first_stage_dv"], after_data["first_stage_dv"]),
        ('Second Stage ΔV (m/s)', before_data["second_stage_dv"], after_data["second_stage_dv"]),
        ('Total ΔV (m/s)', before_data["total_dv"], after_data["total_dv"]),
        ('Initial Mass (kg)', before_data["initial_mass"], after_data["initial_mass"]),
        ('Final Mass (kg)', before_data["final_mass"], after_data["final_mass"]),
        ('Payload Fraction (%)', before_data["payload_fraction"], after_data["payload_fraction"]),
        ('Est. Max Altitude (km)', before_data["estimated_altitude"]/1000, after_data["estimated_altitude"]/1000)
    ]
    
    # Extract data for plotting
    labels = [m[0] for m in metrics]
    before_values = [m[1] for m in metrics]
    after_values = [m[2] for m in metrics]
    
    # Calculate percentage changes
    percent_changes = [(after - before) / before * 100 if before != 0 else 0 
                      for before, after in zip(before_values, after_values)]
    
    # Create figure with two subplots
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 8))
    
    # Bar chart of raw values
    x = np.arange(len(labels))
    width = 0.35
    
    rects1 = ax1.bar(x - width/2, before_values, width, label='Before')
    rects2 = ax1.bar(x + width/2, after_values, width, label='After')
    
    # Add labels and formatting
    ax1.set_ylabel('Value')
    ax1.set_title('Performance Metrics Comparison')
    ax1.set_xticks(x)
    ax1.set_xticklabels(labels, rotation=45, ha='right')
    ax1.legend()
    
    # Add value labels to bars
    for i, (before, after) in enumerate(zip(before_values, after_values)):
        ax1.text(i - width/2, before * 1.01, f"{before:.1f}", ha='center', va='bottom', fontsize=9)
        ax1.text(i + width/2, after * 1.01, f"{after:.1f}", ha='center', va='bottom', fontsize=9)
    
    # Bar chart of percentage changes
    ax2.bar(x, percent_changes, 0.7, color=['g' if p >= 0 else 'r' for p in percent_changes])
    
    # Add labels and formatting
    ax2.set_ylabel('Percent Change (%)')
    ax2.set_title('Performance Improvement')
    ax2.set_xticks(x)
    ax2.set_xticklabels(labels, rotation=45, ha='right')
    
    # Add percentage change labels
    for i, p_change in enumerate(percent_changes):
        color = 'g' if p_change >= 0 else 'r'
        ax2.text(i, p_change + (1 if p_change >= 0 else -3), 
                f"{p_change:.1f}%", ha='center', va='bottom', color=color)
    
    plt.tight_layout()
    
    # Save or display the chart
    if output_file:
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        plt.close(fig)
        return output_file
    else:
        plt.show()
        return None

def generate_rocket_visualization(model, title, output_file=None):
    """Generate a visualization of a rocket model with propulsion details"""
    # Create figure
    fig, ax = plt.subplots(figsize=(12, 10))
    ax.set_xlim(-4, 4)
    
    # Calculate total height
    first_stage_length = model["firstStage"]["length"]
    second_stage_length = model["secondStage"]["length"]
    nose_cone_length = model["noseCone"]["length"]
    total_height = first_stage_length + second_stage_length + nose_cone_length
    
    # Set y limits with padding
    ax.set_ylim(-2, total_height + 1)
    
    # Draw first stage
    first_stage_radius = model["firstStage"]["diameter"] / 2
    first_stage_bottom = 0
    first_stage_top = first_stage_length
    
    # First stage cylinder
    ax.add_patch(plt.Rectangle(
        (-first_stage_radius, first_stage_bottom),
        2 * first_stage_radius,
        first_stage_length,
        fill=True,
        color='lightgrey',
        alpha=0.7
    ))
    
    # Add first stage outline
    ax.plot(
        [-first_stage_radius, -first_stage_radius],
        [first_stage_bottom, first_stage_top],
        'k-', lw=2
    )
    ax.plot(
        [first_stage_radius, first_stage_radius],
        [first_stage_bottom, first_stage_top],
        'k-', lw=2
    )
    
    # Draw engine bell
    engine_width = first_stage_radius * 0.4
    engine_height = first_stage_length * 0.1
    engine_x = 0
    engine_y = first_stage_bottom
    
    # Draw engine bell shape
    bell_x = np.array([-engine_width, 0, engine_width]) 
    bell_y = np.array([engine_y, engine_y - engine_height, engine_y])
    ax.plot(bell_x, bell_y, 'k-', lw=2, color='darkgrey')
    
    # Draw flame if first stage propellant is high-energy
    if model["firstStage"]["propellant"] == "LOX/LH2":
        flame_length = first_stage_length * 0.25
        flame_x = np.array([-engine_width*0.8, 0, engine_width*0.8, 0])
        flame_y = np.array([engine_y, engine_y - flame_length, engine_y, engine_y - flame_length*0.6])
        ax.plot(flame_x, flame_y, 'r-', lw=2, alpha=0.7)
        ax.fill(flame_x, flame_y, 'orange', alpha=0.5)
    else:
        flame_length = first_stage_length * 0.15
        flame_x = np.array([-engine_width*0.8, 0, engine_width*0.8, 0])
        flame_y = np.array([engine_y, engine_y - flame_length, engine_y, engine_y - flame_length*0.6])
        ax.plot(flame_x, flame_y, 'r-', lw=2, alpha=0.7)
        ax.fill(flame_x, flame_y, 'r', alpha=0.5)
    
    # Draw second stage
    second_stage_radius = model["secondStage"]["diameter"] / 2
    second_stage_bottom = first_stage_top
    second_stage_top = second_stage_bottom + second_stage_length
    
    # Second stage cylinder
    ax.add_patch(plt.Rectangle(
        (-second_stage_radius, second_stage_bottom),
        2 * second_stage_radius,
        second_stage_length,
        fill=True,
        color='darkgrey',
        alpha=0.7
    ))
    
    # Add second stage outline
    ax.plot(
        [-second_stage_radius, -second_stage_radius],
        [second_stage_bottom, second_stage_top],
        'k-', lw=2
    )
    ax.plot(
        [second_stage_radius, second_stage_radius],
        [second_stage_bottom, second_stage_top],
        'k-', lw=2
    )
    
    # Draw nose cone
    nose_cone_bottom = second_stage_top
    nose_cone_top = nose_cone_bottom + nose_cone_length
    
    # Simple triangular nose cone
    ax.plot(
        [0, -second_stage_radius, second_stage_radius, 0],
        [nose_cone_top, nose_cone_bottom, nose_cone_bottom, nose_cone_top],
        'k-', lw=2, color='darkgrey', alpha=0.9
    )
    
    # Draw fins
    fin_count = model["fins"]["count"]
    fin_span = model["fins"]["span"]
    fin_height = first_stage_length * 0.2  # 20% of first stage length
    fin_bottom = first_stage_bottom + first_stage_length * 0.1  # 10% up from bottom
    
    for i in range(fin_count):
        angle = i * (360 / fin_count)
        rad_angle = np.radians(angle)
        
        # Base of fin
        x_base = first_stage_radius * np.cos(rad_angle)
        y_base = fin_bottom
        
        # Tip of fin
        x_tip = (first_stage_radius + fin_span) * np.cos(rad_angle)
        y_tip = fin_bottom + fin_height / 2
        
        # Top of fin attachment
        x_top = first_stage_radius * np.cos(rad_angle)
        y_top = fin_bottom + fin_height
        
        # Draw fin
        ax.plot(
            [x_base, x_tip, x_top, x_base],
            [y_base, y_tip, y_top, y_base],
            'k-', lw=2, color='darkblue', alpha=0.7
        )
    
    # Add annotations for key dimensions and propulsion info
    ax.annotate(
        f"First Stage\nDiameter: {model['firstStage']['diameter']}m\nLength: {model['firstStage']['length']}m\nMaterial: {model['firstStage']['material']}\nPropellant: {model['firstStage']['propellant']}\nISP: {model['firstStage']['isp']}s\nThrust: {model['firstStage']['thrustSL']/1000:.1f}kN",
        xy=(2.5, first_stage_length / 2),
        xytext=(3.0, first_stage_length / 2),
        arrowprops=dict(arrowstyle='->'),
        fontsize=9
    )
    
    ax.annotate(
        f"Second Stage\nDiameter: {model['secondStage']['diameter']}m\nLength: {model['secondStage']['length']}m\nMaterial: {model['secondStage']['material']}\nPropellant: {model['secondStage']['propellant']}\nISP: {model['secondStage']['isp']}s\nThrust: {model['secondStage']['thrustVac']/1000:.1f}kN",
        xy=(2.5, first_stage_length + second_stage_length / 2),
        xytext=(3.0, first_stage_length + second_stage_length / 2),
        arrowprops=dict(arrowstyle='->'),
        fontsize=9
    )
    
    ax.annotate(
        f"Nose Cone\nShape: {model['noseCone']['shape']}\nLength: {model['noseCone']['length']}m",
        xy=(1, nose_cone_bottom + nose_cone_length / 2),
        xytext=(3.0, nose_cone_bottom + nose_cone_length / 2),
        arrowprops=dict(arrowstyle='->'),
        fontsize=9
    )
    
    ax.annotate(
        f"Fins\nCount: {model['fins']['count']}\nShape: {model['fins']['shape']}\nSpan: {model['fins']['span']}m",
        xy=(-2, fin_bottom + fin_height / 2),
        xytext=(-3.0, fin_bottom + fin_height / 2),
        arrowprops=dict(arrowstyle='->'),
        ha='right',
        fontsize=9
    )
    
    # Add payload information
    ax.annotate(
        f"Payload\nMass: {model['payload']['mass']}kg",
        xy=(0, second_stage_top + nose_cone_length/2),
        xytext=(-3.0, second_stage_top + nose_cone_length/2),
        arrowprops=dict(arrowstyle='->'),
        ha='right',
        fontsize=9
    )
    
    # Add title and axes
    ax.set_title(title)
    ax.set_xlabel('Width (m)')
    ax.set_ylabel('Height (m)')
    ax.grid(True, linestyle='--', alpha=0.5)
    ax.set_aspect('equal')
    
    plt.tight_layout()
    
    # Save to file if requested
    if output_file:
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        plt.close(fig)
        return output_file
    else:
        plt.show()
        return None

def main():
    """Run a performance-focused design test demonstration"""
    print("AI Rocket Design - Performance Test Demonstration")
    print("================================================")
    
    # Create output directory
    output_dir = os.path.join(TEST_DIR, 'perf_test_output')
    os.makedirs(output_dir, exist_ok=True)
    
    # Original model
    original_model = json.loads(json.dumps(sample_rocket_model))
    
    # Display the original design specs
    print("\nOriginal Rocket Design:")
    print(f"- First Stage: Propellant {original_model['firstStage']['propellant']}, ISP {original_model['firstStage']['isp']}s")
    print(f"- Second Stage: Length {original_model['secondStage']['length']}m, Propellant Mass {original_model['secondStage']['propellantMass']}kg")
    print(f"- Payload Mass: {original_model['payload']['mass']}kg")
    
    # Calculate original performance
    original_dv = calculate_delta_v(original_model)
    original_altitude = estimate_altitude(original_model, original_dv)
    original_dv["estimated_altitude"] = original_altitude
    
    print(f"- Original Delta-V: {original_dv['total_dv']:.0f} m/s")
    print(f"- Original Estimated Max Altitude: {original_altitude/1000:.1f} km")
    
    # Visualize original design
    original_viz = os.path.join(output_dir, 'original_rocket.png')
    generate_rocket_visualization(original_model, "Original Rocket Design", original_viz)
    print(f"Original design visualization saved to: {original_viz}")
    
    # Simulate design prompt
    design_prompt = "Increase the maximum altitude by switching the first stage to LOX/LH2 propellant, extending the second stage length to 4 meters, and increasing the second stage propellant mass by 30%"
    print(f"\nDesign Prompt: '{design_prompt}'")
    
    # Show AI response (simulated)
    ai_response = """
I'll make these changes to increase your rocket's maximum altitude:

1. Changed first stage propellant from LOX/RP-1 to LOX/LH2, which increases the specific impulse from 290s to 370s. This significantly improves efficiency.

2. Extended second stage length from 3.0m to 4.0m, allowing for more propellant capacity.

3. Increased second stage propellant mass by 30% from 1200kg to 1560kg.

These modifications will significantly increase your maximum altitude. The higher ISP of the LOX/LH2 propellant in the first stage provides much better efficiency, though note that it has lower density so the tank volume increases. The lengthened second stage with 30% more propellant extends the burn time in the upper atmosphere where efficiency is highest.

Based on my calculations, these changes should increase your total delta-V by approximately 25-30%, which translates to a substantial increase in maximum altitude.
"""
    print("\nAI Response:")
    print(ai_response)
    
    # Apply the changes to create modified design
    modified_model = json.loads(json.dumps(original_model))
    
    # 1. Change first stage propellant to LOX/LH2
    modified_model["firstStage"]["propellant"] = "LOX/LH2"
    modified_model["firstStage"]["isp"] = 370  # Higher ISP for LOX/LH2
    
    # 2. Extend second stage length
    modified_model["secondStage"]["length"] = 4.0  # Increased from 3.0m
    
    # 3. Increase second stage propellant mass by 30%
    modified_model["secondStage"]["propellantMass"] = int(modified_model["secondStage"]["propellantMass"] * 1.3)  # 30% increase
    
    # Display the modified design
    print("\nModified Rocket Design:")
    print(f"- First Stage: Propellant {modified_model['firstStage']['propellant']}, ISP {modified_model['firstStage']['isp']}s")
    print(f"- Second Stage: Length {modified_model['secondStage']['length']}m, Propellant Mass {modified_model['secondStage']['propellantMass']}kg")
    print(f"- Payload Mass: {modified_model['payload']['mass']}kg")
    
    # Calculate modified performance
    modified_dv = calculate_delta_v(modified_model)
    modified_altitude = estimate_altitude(modified_model, modified_dv)
    modified_dv["estimated_altitude"] = modified_altitude
    
    print(f"- Modified Delta-V: {modified_dv['total_dv']:.0f} m/s")
    print(f"- Modified Estimated Max Altitude: {modified_altitude/1000:.1f} km")
    print(f"- Altitude Increase: {(modified_altitude - original_altitude)/1000:.1f} km ({(modified_altitude/original_altitude - 1)*100:.1f}%)")
    
    # Visualize modified design
    modified_viz = os.path.join(output_dir, 'modified_rocket.png')
    generate_rocket_visualization(modified_model, "Modified Rocket Design", modified_viz)
    print(f"Modified design visualization saved to: {modified_viz}")
    
    # Show changes
    print("\nChanges Applied:")
    print("- First Stage Propellant: LOX/RP-1 -> LOX/LH2")
    print("- First Stage ISP: 290s -> 370s")
    print("- Second Stage Length: 3.0m -> 4.0m")
    print(f"- Second Stage Propellant Mass: {original_model['secondStage']['propellantMass']}kg -> {modified_model['secondStage']['propellantMass']}kg")
    
    # Generate performance comparison chart
    perf_chart = os.path.join(output_dir, 'performance_comparison.png')
    generate_performance_chart(original_dv, modified_dv, perf_chart)
    print(f"\nPerformance comparison chart saved to: {perf_chart}")
    
    # Performance analysis
    print("\nPerformance Analysis:")
    print(f"- Delta-V Increase: {modified_dv['total_dv'] - original_dv['total_dv']:.0f} m/s ({(modified_dv['total_dv']/original_dv['total_dv'] - 1)*100:.1f}%)")
    print(f"- First Stage Delta-V: {original_dv['first_stage_dv']:.0f} m/s -> {modified_dv['first_stage_dv']:.0f} m/s")
    print(f"- Second Stage Delta-V: {original_dv['second_stage_dv']:.0f} m/s -> {modified_dv['second_stage_dv']:.0f} m/s")
    print(f"- Payload Fraction: {original_dv['payload_fraction']:.2f}% -> {modified_dv['payload_fraction']:.2f}%")
    
    # Engineering tradeoffs
    print("\nEngineering Tradeoffs:")
    print("- LOX/LH2 provides higher performance but requires larger tanks due to lower density")
    print("- LOX/LH2 requires cryogenic storage and has more complex handling requirements")
    print("- Longer second stage increases drag slightly but the propellant capacity benefit outweighs this")
    print("- Overall, the changes significantly improve altitude performance with modest complexity increase")
    
    print("\nTest completed! Visualizations and performance data generated in the perf_test_output directory.")
    print("This demonstrates how our testing framework verifies that complex performance-oriented")
    print("design changes requested by human designers are correctly implemented and analyzed.")

if __name__ == "__main__":
    main()
