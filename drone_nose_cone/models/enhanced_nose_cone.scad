// Enhanced Drone Nose Cone - Parametric Design with Multiple Profiles
// Based on specifications from April 17, 2025

/* Base Parameters */
// Basic dimensions
inner_diameter = 67;  // mm
outer_diameter = 78;  // mm
base_ring_depth = 13; // mm
cone_angle = 52;      // degrees

// Calculated parameters
inner_radius = inner_diameter / 2;
outer_radius = outer_diameter / 2;
wall_thickness = outer_radius - inner_radius;

// Derived dimensions
// Calculate cone height based on angle and radius difference
cone_height = (outer_radius - inner_radius) / tan(cone_angle);
// Add some height for the rounded tip
total_cone_height = cone_height * 1.2;  

/* Design Parameters */
// Profile type: "conical", "ogive", "elliptical", "karman", "tangent"
profile_type = "conical";  // Default to conical

// Nose rounding parameters
tip_rounding_radius = outer_radius * 0.5;
tip_rounding_factor = 0.5;  // As a proportion of outer radius

// Lightweighting parameters
use_lightweighting = true;
shell_thickness = 1.2;  // mm - wall thickness for hollow parts
wall_thinning_factor = 1.0;  // 1.0 = uniform thickness, <1.0 = thinner at tip
internal_ribs = true;
rib_thickness = 1.0;    // mm
rib_count = 6;          // number of radial ribs

// Resolution parameters for smooth curves
$fn = 120;  // Facet number for cylinders and spheres

/* Profile Functions */
// Generate points for a profile curve
function generate_profile_points(type, length, radius, steps=100) =
    type == "conical" ? conical_profile(length, radius, steps) :
    type == "ogive" ? ogive_profile(length, radius, steps) :
    type == "elliptical" ? elliptical_profile(length, radius, steps) :
    type == "karman" ? karman_profile(length, radius, steps) :
    type == "tangent" ? tangent_ogive_profile(length, radius, steps) :
    conical_profile(length, radius, steps);  // Default

// Conical profile with rounded tip
function conical_profile(length, radius, steps=100) =
    let(
        tip_radius = radius * tip_rounding_factor,
        cone_length = length - tip_radius,
        cone_points = [for(i = [0:steps]) 
            let(z = i * cone_length / steps)
            [radius * (1 - z / cone_length), z]],
        tip_points = [for(i = [0:steps]) 
            let(angle = i * 90 / steps, 
                z = cone_length + tip_radius * sin(angle),
                r = tip_radius * cos(angle))
            [r, z]]
    )
    concat(cone_points, tip_points);

// Ogive (parabolic) profile
function ogive_profile(length, radius, steps=100) =
    [for(i = [0:steps]) 
        let(z = i * length / steps)
        [radius * (1 - pow(z/length, 2)), z]];

// Elliptical profile
function elliptical_profile(length, radius, steps=100) =
    [for(i = [0:steps]) 
        let(z = i * length / steps)
        [radius * sqrt(1 - pow(z/length, 2)), z]];

// Von Kármán profile (Haack series with C=0)
function karman_profile(length, radius, steps=100) =
    [for(i = [0:steps]) 
        let(theta = i * 180 / steps,
            z = length * (1 - cos(theta)) / 2,
            r = radius * sqrt((theta - sin(2*theta)/2) / 180))
        [r, z]];

// Tangent ogive profile
function tangent_ogive_profile(length, radius, steps=100) =
    let(
        rho = (pow(length, 2) + pow(radius, 2)) / (2 * radius),
        x_offset = length - sqrt(pow(rho, 2) - pow(rho - radius, 2))
    )
    [for(i = [0:steps]) 
        let(z = i * length / steps,
            r = z <= length ? 
                sqrt(pow(rho, 2) - pow(z - x_offset, 2)) - (rho - radius) : 0)
        [r, z]];

/* 3D Geometry Modules */
// Generate a 3D nose cone from a 2D profile
module nose_cone_from_profile(profile, steps=100) {
    // Rotate points around Z axis to create the 3D shape
    rotate_extrude() {
        polygon(profile);
    }
}

// Create the hollow interior for lightweighting
module nose_cone_hollow(profile, steps=100, shell_thickness=1.2, wall_thinning=1.0) {
    // Adjust the profile to create the interior hollow
    adjusted_profile = [for(i = [0:len(profile)-1])
        let(
            original_radius = profile[i][0],
            z_position = profile[i][1],
            z_ratio = z_position / total_cone_height,
            // Apply wall thinning toward the tip
            adjusted_thickness = shell_thickness * (1 - (1 - wall_thinning) * z_ratio),
            new_radius = max(0, original_radius - adjusted_thickness)
        )
        [new_radius, z_position]
    ];
    
    // Create the hollow by extruding the adjusted profile
    rotate_extrude() {
        polygon(adjusted_profile);
    }
}

// Create internal support ribs
module internal_ribs(profile, rib_count=6, rib_thickness=1.0) {
    // Calculate the maximum height for ribs
    max_height = total_cone_height * 0.8;
    
    // Create each rib
    for (i = [0:rib_count-1]) {
        rotate([0, 0, i * (360 / rib_count)]) {
            // Vertical rib
            intersection() {
                // Create the basic rib shape
                linear_extrude(height=max_height) {
                    polygon([
                        [0, 0],
                        [outer_radius, 0],
                        [0, max_height * 0.8]
                    ]);
                }
                
                // Intersect with the nose cone to shape the rib
                nose_cone_from_profile(profile);
            }
            
            // Add a triangular reinforcement at the base
            translate([0, 0, base_ring_depth]) {
                linear_extrude(height=rib_thickness, center=true) {
                    polygon([
                        [0, 0],
                        [0, max_height * 0.3],
                        [max_height * 0.3, 0]
                    ]);
                }
            }
        }
    }
}

/* Main Module */
module nose_cone() {
    // Generate the appropriate profile based on the selected type
    profile = generate_profile_points(profile_type, total_cone_height, outer_radius);
    
    // Translate the profile to the base ring
    full_profile = [for(p = profile) [p[0], p[1] + base_ring_depth]];
    
    // Create the combined profile including the base ring
    base_profile = [
        [inner_radius, 0],
        [outer_radius, 0],
        [outer_radius, base_ring_depth],
        [inner_radius, base_ring_depth]
    ];
    
    complete_profile = concat([[0, 0]], base_profile, [[0, base_ring_depth]]);
    
    difference() {
        union() {
            // Base ring
            difference() {
                cylinder(h=base_ring_depth, r=outer_radius);
                translate([0, 0, -0.1])
                    cylinder(h=base_ring_depth + 0.2, r=inner_radius);
            }
            
            // Nose cone from profile
            nose_cone_from_profile(full_profile);
        }
        
        // Hollow out the inside if using lightweighting
        if (use_lightweighting) {
            translate([0, 0, base_ring_depth]) {
                nose_cone_hollow(profile, shell_thickness=shell_thickness, 
                                wall_thinning=wall_thinning_factor);
            }
        }
    }
    
    // Add internal support ribs if enabled
    if (use_lightweighting && internal_ribs) {
        internal_ribs(full_profile, rib_count=rib_count, rib_thickness=rib_thickness);
    }
}

/* Render the nose cone */
nose_cone();

/* 
// Cross section view for debugging
difference() {
    nose_cone();
    translate([-100, 0, -10])
        cube([200, 200, 200]);
}
*/
