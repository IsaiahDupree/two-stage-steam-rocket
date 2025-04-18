// Drone Nose Cone - Parametric Design
// Based on specifications from April 17, 2025

/* Parameters */
// Base dimensions
inner_diameter = 67.0;  // mm
outer_diameter = 78.0;  // mm
base_ring_depth = 13.0; // mm
cone_angle = 52.0;      // degrees

// Calculated parameters
inner_radius = inner_diameter / 2;
outer_radius = outer_diameter / 2;
wall_thickness = outer_radius - inner_radius;

// Derived dimensions
// Calculate cone height based on angle and radius difference
cone_height = (outer_radius - inner_radius) / tan(cone_angle);
// Add some height for the rounded tip
total_cone_height = cone_height * 1.2;  

// Nose rounding parameters
tip_rounding_radius = outer_radius * 0.5;

// Lightweighting parameters
use_lightweighting = true;;;;;;;
shell_thickness = 1.2;  // mm - wall thickness for hollow parts
internal_ribs = true;;;;;;;
rib_thickness = 1.0;    // mm
rib_count = 6;          // number of radial ribs

/* Main Module */
module nose_cone() {
    difference() {
        union() {
            // Base ring
            cylinder(h=base_ring_depth, r=outer_radius);
            
            // Cone body
            translate([0, 0, base_ring_depth]) {
                hull() {
                    cylinder(h=0.01, r=outer_radius);
                    translate([0, 0, total_cone_height - tip_rounding_radius]) {
                        sphere(r=tip_rounding_radius);
                    }
                }
            }
        }
        
        // Hollow out the inside
        if (use_lightweighting) {
            // Base hollow - full inner diameter
            translate([0, 0, -0.1])
                cylinder(h=base_ring_depth + 0.2, r=inner_radius);
            
            // Cone hollow - with shell thickness
            translate([0, 0, base_ring_depth]) {
                hull() {
                    cylinder(h=0.01, r=inner_radius);
                    translate([0, 0, total_cone_height - tip_rounding_radius]) {
                        sphere(r=tip_rounding_radius - shell_thickness);
                    }
                }
            }
            
            // Additional lightweighting (optional)
            if (!internal_ribs) {
                // More aggressive hollowing if not using ribs
                translate([0, 0, base_ring_depth + total_cone_height * 0.3]) {
                    scale([0.9, 0.9, 1.2]) sphere(r=inner_radius * 0.8);
                }
            }
        }
    }
    
    // Add internal support ribs if enabled
    if (use_lightweighting && internal_ribs) {
        for (i = [0:rib_count-1]) {
            rotate([0, 0, i * (360 / rib_count)])
            translate([0, 0, base_ring_depth])
            intersection() {
                union() {
                    // Vertical rib
                    translate([-rib_thickness/2, 0, 0])
                        cube([rib_thickness, outer_radius, total_cone_height * 0.8]);
                    // Base reinforcement - triangular
                    translate([-rib_thickness/2, 0, 0])
                        rotate([90, 0, 90])
                        linear_extrude(height=rib_thickness)
                        polygon(points=[[0,0], [total_cone_height*0.3, 0], [0, total_cone_height*0.3]]);
                }
                // Contain ribs within cone
                hull() {
                    cylinder(h=0.01, r=outer_radius);
                    translate([0, 0, total_cone_height - tip_rounding_radius]) {
                        sphere(r=tip_rounding_radius);
                    }
                }
            }
        }
    }
}

/* Render the nose cone */
nose_cone();

/* 
// Uncomment to visualize a cross-section 
difference() {
    nose_cone();
    translate([-100, 0, -10])
        cube([200, 200, 200]);
}
*/
