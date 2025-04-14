#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Simple test script to verify connection to Ansys Geometry service.

This script tests connecting to the Ansys Geometry service using either:
1. Docker container (preferred) or
2. SpaceClaim (fallback)

It will attempt to create a simple object to verify the service is working.
"""

import os
import sys
import time
import logging
from pathlib import Path

# Add the parent directory to the path so we can import our modules
current_dir = Path(__file__).resolve().parent
if str(current_dir) not in sys.path:
    sys.path.append(str(current_dir))

# Configure logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("AnsysConnectionTest")

# Import our ansys_integration module
try:
    from src.ansys_integration import (
        AnsysRocketInterface, 
        is_docker_installed,
        is_docker_container_running, 
        start_docker_container,
        is_spaceclaim_running,
        start_spaceclaim,
        check_docker_logs,
        DOCKER_CONFIG
    )
    logger.info("Successfully imported ansys_integration module")
except ImportError as e:
    logger.error(f"Failed to import ansys_integration module: {e}")
    logger.error("Make sure the module exists and is accessible")
    sys.exit(1)

def print_section(title):
    """Print a section title with decorative formatting."""
    print("\n" + "=" * 80)
    print(f" {title} ".center(80, "="))
    print("=" * 80)

def test_ansys_geometry_connection(use_docker=True, use_spaceclaim=True):
    """
    Test connection to Ansys Geometry service.
    
    Parameters
    ----------
    use_docker : bool, optional
        Whether to try using Docker for Ansys Geometry.
    use_spaceclaim : bool, optional
        Whether to try using SpaceClaim for Ansys Geometry.
    
    Returns
    -------
    bool
        True if connection was successful, False otherwise
    """
    print_section("ANSYS GEOMETRY CONNECTION TEST")
    print("This script will test the connection to the Ansys Geometry service")
    print("and attempt to create a simple object to verify functionality.\n")
    
    # Display test configuration
    print("Test configuration:")
    print(f"- Try Docker container: {'Yes' if use_docker else 'No'}")
    print(f"- Try SpaceClaim: {'Yes' if use_spaceclaim else 'No'}")
    
    # Environment information
    print("\nEnvironment information:")
    print(f"- Operating System: {sys.platform}")
    print(f"- Python Version: {sys.version.split()[0]}")
    
    # Try PyAnsys import
    try:
        import ansys.geometry.core as agc
        print(f"- PyAnsys Geometry Version: {agc.__version__}")
    except (ImportError, AttributeError):
        print("- PyAnsys Geometry: Not installed or version unknown")
        print("\nERROR: PyAnsys Geometry is required for this test")
        print("Install with: pip install ansys-geometry-core")
        return False
    
    # Connection test
    try:
        print("\nInitializing Ansys Rocket Interface...")
        rocket = AnsysRocketInterface(use_docker=use_docker, use_spaceclaim=use_spaceclaim)
        
        if rocket.simulation_mode:
            print("\nERROR: Could not connect to Ansys Geometry service")
            print("       Running in simulation mode instead")
            
            if use_docker and not is_docker_installed():
                print("\nDiagnosis: Docker is not installed or not running")
                print("1. Install Docker Desktop: https://www.docker.com/products/docker-desktop")
                print("2. Make sure Docker service is running")
            
            if use_docker and is_docker_installed() and not is_docker_container_running():
                print("\nDiagnosis: Ansys Geometry Docker container is not running")
                print("1. Run: python setup_ansys_docker.py --action start")
                print("   or use the run_ansys_docker.bat script")
                print("2. Check container logs for errors: python setup_ansys_docker.py --action logs")
            
            if use_spaceclaim and not is_spaceclaim_running():
                print("\nDiagnosis: SpaceClaim is not running")
                print("1. Start SpaceClaim manually or using the Ansys Workbench")
                print("2. Make sure SpaceClaim has the Geometry service enabled")
            
            return False
        
        # Connection successful
        print("\nSUCCESS: Connected to Ansys Geometry service!")
        print(f"Connection method: {rocket.connection_method}")
        
        # Check if we have a modeler
        if rocket.modeler is None:
            print("\nERROR: Connected to service but modeler is None")
            return False
        
        # Try to create a simple object
        print("\nCreating a simple test object...")
        
        # Get a reference to the design
        design = rocket.design
        
        # Create a box
        print("- Creating a box...")
        box = rocket.modeler.shapes.create_box(
            design=design,
            origin=[-0.5, -0.5, -0.5],
            dimensions=[1.0, 1.0, 1.0]
        )
        print(f"- Box created: {box}")
        
        # Create a sphere
        print("- Creating a sphere...")
        sphere = rocket.modeler.shapes.create_sphere(
            design=design,
            origin=[2.0, 0.0, 0.0],
            radius=0.75
        )
        print(f"- Sphere created: {sphere}")
        
        # Create a cylinder
        print("- Creating a cylinder...")
        cylinder = rocket.modeler.shapes.create_cylinder(
            design=design,
            origin=[0.0, 2.0, 0.0],
            axis=[0.0, 0.0, 1.0],
            radius=0.5,
            height=2.0
        )
        print(f"- Cylinder created: {cylinder}")
        
        print("\nSUCCESS: All test objects created successfully!")
        
        # Test completed successfully
        return True
        
    except Exception as e:
        print(f"\nERROR: Failed to create test objects: {e}")
        
        # More detailed diagnostics
        print("\nDiagnostics:")
        
        if use_docker and is_docker_container_running():
            print("- Docker container is running, but there might be issues with the service")
            print("- Checking container logs...")
            logs = check_docker_logs(lines=50)
            if logs and "license error" in logs.lower():
                print("  - License error detected in container logs")
                print(f"  - Check license server configuration: {DOCKER_CONFIG['license_server']}")
        
        return False

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Test Ansys Geometry connection")
    parser.add_argument("--docker", action="store_true", help="Try Docker container (default)")
    parser.add_argument("--no-docker", action="store_true", help="Don't try Docker container")
    parser.add_argument("--spaceclaim", action="store_true", help="Try SpaceClaim (default)")
    parser.add_argument("--no-spaceclaim", action="store_true", help="Don't try SpaceClaim")
    
    args = parser.parse_args()
    
    # Determine which methods to try
    use_docker = not args.no_docker
    use_spaceclaim = not args.no_spaceclaim
    
    # If explicitly specified, override defaults
    if args.docker:
        use_docker = True
    if args.spaceclaim:
        use_spaceclaim = True
    
    # Run the test
    success = test_ansys_geometry_connection(use_docker=use_docker, use_spaceclaim=use_spaceclaim)
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)
