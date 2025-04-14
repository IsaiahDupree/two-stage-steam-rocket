#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Rocket Design Automation Script using FreeCAD

This script automates the creation of rocket components by reading specifications from a CSV file
and generating the corresponding 3D models in FreeCAD.

Usage:
1. Ensure FreeCAD is installed and properly configured
2. Prepare a CSV file with rocket component specifications
3. Run this script with: freecadcmd rocket_csv_automation.py path/to/specs.csv

Compatible with both Windows and Mac environments.
"""

import os
import sys
import traceback
import csv
import argparse
from datetime import datetime


def setup_freecad_environment():
    """Setup the FreeCAD environment by adding appropriate paths to sys.path."""
    
    log_message("Setting up FreeCAD environment...")
    
    # Common FreeCAD installation paths by platform
    freecad_paths = {
        'windows': [
            "C:/Program Files/FreeCAD 1.0/bin",
            "C:/Program Files/FreeCAD 0.20/bin", 
            "C:/Program Files/FreeCAD 0.19/bin",
            "C:/Program Files/FreeCAD 0.18/bin",
        ],
        'darwin': [  # Mac OS
            "/Applications/FreeCAD.app/Contents/Resources/lib",
            "/Applications/FreeCAD.app/Contents/MacOS",
        ],
        'linux': [
            "/usr/lib/freecad/lib",
            "/usr/local/lib/freecad/lib",
        ]
    }
    
    # Determine platform
    if sys.platform.startswith('win'):
        platform = 'windows'
    elif sys.platform.startswith('darwin'):
        platform = 'darwin'
    else:
        platform = 'linux'
    
    log_message(f"Detected platform: {platform}")
    
    # Add platform-specific paths
    for path in freecad_paths.get(platform, []):
        if os.path.exists(path) and path not in sys.path:
            sys.path.append(path)
            log_message(f"Added FreeCAD path: {path}")
    
    # Check if python version matches FreeCAD's expected version
    python_version = sys.version.split()[0]
    log_message(f"Current Python version: {python_version}")
    
    # Return whether we successfully imported FreeCAD
    try:
        import FreeCAD
        log_message(f"Successfully imported FreeCAD module")
        log_message(f"FreeCAD version: {FreeCAD.Version()}")
        return True
    except ImportError as e:
        log_message(f"ERROR: Could not import FreeCAD: {e}")
        log_message("Please ensure FreeCAD is installed and compatible with your Python version.")
        return False


def log_message(message):
    """Log a message to both console and log file."""
    print(message)
    with open(LOG_FILE, 'a') as f:
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        f.write(f"[{timestamp}] {message}\n")


def read_csv_data(csv_file):
    """Read rocket component specifications from a CSV file."""
    if not os.path.exists(csv_file):
        log_message(f"ERROR: CSV file not found: {csv_file}")
        return None
    
    try:
        log_message(f"Reading specifications from CSV: {csv_file}")
        components = []
        with open(csv_file, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                components.append(row)
        
        log_message(f"Successfully read {len(components)} components from CSV")
        return components
    except Exception as e:
        log_message(f"ERROR reading CSV file: {str(e)}")
        return None


def create_rocket_component(doc, component):
    """Create a rocket component in FreeCAD based on specifications."""
    try:
        import FreeCAD
        import Part
        
        # Extract component parameters (with default values)
        name = component.get('name', f"Component_{len(doc.Objects)+1}")
        component_type = component.get('type', 'cylinder').lower()
        
        # Convert dimensions to float, with defaults
        length = float(component.get('length', 100))
        diameter = float(component.get('diameter', 50))
        thickness = float(component.get('thickness', 2))
        
        log_message(f"Creating component: {name}, Type: {component_type}")
        
        # Create different geometries based on type
        if component_type == 'cylinder' or component_type == 'tube':
            # Create outer cylinder
            outer_cylinder = Part.makeCylinder(diameter/2, length)
            
            # For tubes, create inner cylinder and subtract
            if thickness > 0 and thickness < diameter/2:
                inner_cylinder = Part.makeCylinder(diameter/2 - thickness, length)
                shape = outer_cylinder.cut(inner_cylinder)
            else:
                shape = outer_cylinder
        
        elif component_type == 'cone' or component_type == 'nosecone':
            shape = Part.makeCone(diameter/2, 0, length)
        
        elif component_type == 'fins':
            # Simple rectangular fin
            fin_height = float(component.get('height', 30))
            fin_width = float(component.get('width', 2))
            fin_length = float(component.get('length', 50))
            num_fins = int(component.get('count', 3))
            
            # Create a single fin
            fin_shape = Part.makeBox(fin_length, fin_width, fin_height)
            
            # Position it at the center
            fin_shape.translate(FreeCAD.Vector(0, -fin_width/2, 0))
            
            # Create compound shape with all fins
            fins = []
            for i in range(num_fins):
                angle = 360 * i / num_fins
                rotated_fin = fin_shape.copy()
                rotated_fin.rotate(FreeCAD.Vector(0, 0, 0), FreeCAD.Vector(0, 0, 1), angle)
                fins.append(rotated_fin)
            
            shape = Part.makeCompound(fins)
        
        else:
            log_message(f"WARNING: Unknown component type: {component_type}, using cylinder")
            shape = Part.makeCylinder(diameter/2, length)
        
        # Add to document
        obj = doc.addObject("Part::Feature", name)
        obj.Shape = shape
        
        # Set component properties for reference
        obj.addProperty("App::PropertyString", "ComponentType", "Rocket", "Component Type")
        obj.ComponentType = component_type
        
        for key, value in component.items():
            if key not in ['name', 'type']:
                prop_name = key.title().replace('_', '')
                obj.addProperty("App::PropertyString", prop_name, "Rocket", key)
                setattr(obj, prop_name, str(value))
        
        return obj
    
    except Exception as e:
        log_message(f"ERROR creating component {component.get('name', 'unknown')}: {str(e)}")
        log_message(traceback.format_exc())
        return None


def create_rocket_assembly(components_data):
    """Create a complete rocket assembly from component specifications."""
    try:
        import FreeCAD
        
        # Create a new document
        doc_name = "Rocket_" + datetime.now().strftime("%Y%m%d_%H%M%S")
        doc = FreeCAD.newDocument(doc_name)
        log_message(f"Created new document: {doc.Name}")
        
        # Create components
        z_position = 0
        created_objects = []
        
        for component in components_data:
            obj = create_rocket_component(doc, component)
            if obj:
                # Handle component positioning
                length = float(component.get('length', 100))
                
                # Position along Z axis
                if hasattr(obj, "Placement"):
                    obj.Placement.Base.z = z_position
                
                # Update Z position for next component
                z_position += length
                
                created_objects.append(obj)
        
        doc.recompute()
        log_message(f"Successfully created {len(created_objects)} components")
        
        return doc
    
    except Exception as e:
        log_message(f"ERROR creating rocket assembly: {str(e)}")
        log_message(traceback.format_exc())
        return None


def export_rocket_model(doc, output_dir):
    """Export the rocket model to various file formats."""
    try:
        import FreeCAD
        import Mesh
        import Part
        
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        log_message(f"Created output directory: {output_dir}")
        
        # Base filename
        base_filename = os.path.join(output_dir, doc.Name)
        
        # Save FreeCAD document
        fcstd_file = f"{base_filename}.FCStd"
        doc.saveAs(fcstd_file)
        log_message(f"Saved FreeCAD document to: {fcstd_file}")
        
        # Export to STEP format
        step_file = f"{base_filename}.step"
        objects = [obj for obj in doc.Objects if hasattr(obj, "Shape")]
        
        try:
            import Import
            Import.export(objects, step_file)
            log_message(f"Exported to STEP file: {step_file}")
        except Exception as e:
            log_message(f"WARNING: Could not export to STEP: {str(e)}")
        
        # Export to STL format
        stl_file = f"{base_filename}.stl"
        try:
            # Create a mesh and export to STL
            shapes = [obj.Shape for obj in objects]
            compound = Part.makeCompound(shapes)
            mesh = Mesh.Mesh(compound.tessellate(0.1))
            mesh.write(stl_file)
            log_message(f"Exported to STL file: {stl_file}")
        except Exception as e:
            log_message(f"WARNING: Could not export to STL: {str(e)}")
            # Alternative approach for STL export
            try:
                log_message("Trying alternative STL export method...")
                import Mesh
                from FreeCAD import Base
                mesh_obj = doc.addObject("Mesh::Feature", "RocketMesh")
                mesh = Mesh.Mesh()
                for obj in objects:
                    if hasattr(obj, 'Shape'):
                        mesh_data = obj.Shape.tessellate(0.1)
                        mesh_obj = Mesh.Mesh(mesh_data)
                        mesh.addMesh(mesh_obj)
                mesh.write(stl_file)
                log_message(f"Exported to STL file (alternative method): {stl_file}")
            except Exception as e2:
                log_message(f"WARNING: Alternative STL export also failed: {str(e2)}")
        
        return True
        
    except Exception as e:
        log_message(f"ERROR exporting rocket model: {str(e)}")
        log_message(traceback.format_exc())
        return False


def main():
    """Main function to run the rocket design automation."""
    global LOG_FILE
    
    # Setup log file
    script_dir = os.path.dirname(os.path.abspath(__file__))
    LOG_FILE = os.path.join(script_dir, "rocket_automation.log")
    
    # Initialize log file
    with open(LOG_FILE, 'w') as f:
        f.write("Rocket Design Automation Log\n")
        f.write("===========================\n\n")
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        f.write(f"[{timestamp}] Starting rocket design automation\n")
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Automate rocket design using FreeCAD')
    parser.add_argument('csv_file', nargs='?', help='Path to CSV file with rocket specifications')
    parser.add_argument('--output', '-o', default='output', help='Output directory for generated files')
    
    args = parser.parse_args()
    
    # Check if CSV file was provided
    if not args.csv_file:
        log_message("No CSV file specified. Using sample data.")
        # Create a sample CSV file if none provided
        sample_csv = os.path.join(script_dir, "sample_rocket.csv")
        if not os.path.exists(sample_csv):
            with open(sample_csv, 'w') as f:
                f.write("name,type,length,diameter,thickness\n")
                f.write("Nosecone,cone,100,50,2\n")
                f.write("Main Body,tube,200,50,2\n")
                f.write("Fins,fins,40,50,2\n")
                f.write("Motor Mount,cylinder,80,20,0\n")
            log_message(f"Created sample CSV file: {sample_csv}")
        args.csv_file = sample_csv
    
    # Setup the FreeCAD environment
    if not setup_freecad_environment():
        log_message("Failed to setup FreeCAD environment. Exiting.")
        return 1
    
    # Read rocket specifications from CSV
    components_data = read_csv_data(args.csv_file)
    if not components_data:
        log_message("Failed to read component data. Exiting.")
        return 1
    
    # Create rocket assembly
    doc = create_rocket_assembly(components_data)
    if not doc:
        log_message("Failed to create rocket assembly. Exiting.")
        return 1
    
    # Export rocket model
    output_dir = os.path.join(script_dir, args.output)
    if not export_rocket_model(doc, output_dir):
        log_message("Failed to export rocket model. Exiting.")
        return 1
    
    log_message("Rocket design automation completed successfully!")
    log_message(f"See output files in: {output_dir}")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:
        print(f"ERROR: {str(e)}")
        print(traceback.format_exc())
        sys.exit(1)
