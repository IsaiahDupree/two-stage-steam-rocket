#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Ansys Geometry Integration Module for Rocket Design Project.

This module provides a bridge between the FreeCAD rocket model and Ansys
simulation tools, enabling advanced engineering analysis capabilities.
"""

import os
import sys
import numpy as np
import logging
import subprocess
import time
import psutil
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# SpaceClaim paths - check common installation locations
SPACECLAIM_PATHS = [
    r"C:\Program Files\ANSYS Inc\v222\SCDM\SpaceClaim.exe",
    r"C:\Program Files\ANSYS Inc\v232\SCDM\SpaceClaim.exe",
    r"C:\Program Files\ANSYS Inc\v212\SCDM\SpaceClaim.exe",
    r"C:\Program Files\ANSYS Inc\v202\SCDM\SpaceClaim.exe",
]

# Docker container configuration
DOCKER_CONFIG = {
    "container_name": "ans_geo",
    "port": 50051,
    "license_server": "localhost:1084",
}

def find_spaceclaim_executable():
    """Find the SpaceClaim executable path."""
    for path in SPACECLAIM_PATHS:
        if os.path.exists(path):
            return path
    return None

def is_spaceclaim_running():
    """Check if SpaceClaim is already running."""
    for proc in psutil.process_iter(['name']):
        if proc.info['name'] and 'SpaceClaim' in proc.info['name']:
            logger.info(f"SpaceClaim is already running (PID: {proc.pid})")
            return True
    return False

def start_spaceclaim(spaceclaim_path=None, wait_timeout=60):
    """
    Start SpaceClaim if it's not already running.
    
    Parameters
    ----------
    spaceclaim_path : str, optional
        Path to SpaceClaim executable.
    wait_timeout : int, optional
        Maximum time to wait for SpaceClaim to start (seconds).
        
    Returns
    -------
    bool
        True if SpaceClaim is running, False otherwise.
    """
    if is_spaceclaim_running():
        return True
        
    # Find SpaceClaim if path not provided
    if not spaceclaim_path:
        spaceclaim_path = find_spaceclaim_executable()
        
    if not spaceclaim_path or not os.path.exists(spaceclaim_path):
        logger.error(f"SpaceClaim executable not found at: {spaceclaim_path}")
        return False
    
    logger.info(f"Starting SpaceClaim: {spaceclaim_path}")
    
    try:
        # Start SpaceClaim in a non-blocking way
        process = subprocess.Popen([spaceclaim_path], 
                                   shell=True, 
                                   stdout=subprocess.PIPE, 
                                   stderr=subprocess.PIPE)
        
        # Wait for SpaceClaim to start
        logger.info(f"Waiting up to {wait_timeout} seconds for SpaceClaim to start...")
        start_time = time.time()
        
        while not is_spaceclaim_running() and time.time() - start_time < wait_timeout:
            time.sleep(1)
            
        if is_spaceclaim_running():
            logger.info("SpaceClaim started successfully")
            # Give SpaceClaim extra time to initialize its services
            time.sleep(5)
            return True
        else:
            logger.error(f"SpaceClaim failed to start within {wait_timeout} seconds")
            return False
            
    except Exception as e:
        logger.error(f"Error starting SpaceClaim: {e}")
        return False

def is_docker_installed():
    """Check if Docker is installed and running."""
    try:
        result = subprocess.run(["docker", "--version"], 
                               capture_output=True, 
                               text=True, 
                               check=True)
        logger.info(f"Docker is installed: {result.stdout.strip()}")
        
        # Check if Docker is running
        result = subprocess.run(["docker", "info"], 
                               capture_output=True, 
                               text=True)
        if result.returncode != 0:
            logger.warning("Docker is installed but not running")
            return False
        
        logger.info("Docker is running")
        return True
    except FileNotFoundError:
        logger.warning("Docker is not installed or not in PATH")
        return False
    except subprocess.CalledProcessError as e:
        logger.warning(f"Error checking Docker: {e}")
        return False

def is_docker_container_running(container_name=DOCKER_CONFIG["container_name"]):
    """Check if the Ansys Geometry Docker container is running."""
    if not is_docker_installed():
        return False
        
    try:
        result = subprocess.run(
            ["docker", "ps", "--filter", f"name={container_name}", "--format", "{{.Names}}"],
            capture_output=True,
            text=True,
            check=True
        )
        
        if container_name in result.stdout:
            logger.info(f"Docker container '{container_name}' is running")
            return True
        else:
            logger.info(f"Docker container '{container_name}' is not running")
            return False
    except subprocess.CalledProcessError as e:
        logger.warning(f"Error checking Docker container: {e}")
        return False

def start_docker_container(license_server=DOCKER_CONFIG["license_server"], 
                          port=DOCKER_CONFIG["port"],
                          container_name=DOCKER_CONFIG["container_name"]):
    """Start the Ansys Geometry Docker container."""
    if not is_docker_installed():
        logger.error("Docker is not installed or not running")
        return False
    
    # Check if container is already running
    if is_docker_container_running(container_name):
        logger.info(f"Container '{container_name}' is already running")
        return True
    
    # Check if container exists but is stopped
    try:
        result = subprocess.run(
            ["docker", "ps", "-a", "--filter", f"name={container_name}", "--format", "{{.Names}}"],
            capture_output=True,
            text=True,
            check=True
        )
        
        if container_name in result.stdout:
            logger.info(f"Starting existing container '{container_name}'")
            subprocess.run(["docker", "start", container_name], check=True)
            logger.info(f"Container '{container_name}' started successfully")
            
            # Wait a moment for the container to initialize
            time.sleep(5)
            return True
        
        # Container doesn't exist, create it
        logger.info(f"Creating new Ansys Geometry container '{container_name}'")
        image = "ghcr.io/ansys/geometry:latest"
        
        cmd = [
            "docker", "run",
            "-d",  # Detached mode
            "--name", container_name,
            "-e", f"LICENSE_SERVER={license_server}",
            "-p", f"{port}:{port}",
            image
        ]
        
        subprocess.run(cmd, check=True)
        logger.info(f"Container '{container_name}' created and started successfully")
        
        # Wait a moment for the container to initialize
        logger.info("Waiting for the container to initialize...")
        time.sleep(10)
        return True
        
    except subprocess.CalledProcessError as e:
        logger.error(f"Error starting Docker container: {e}")
        return False

def check_docker_logs(container_name=DOCKER_CONFIG["container_name"], lines=10):
    """Check the Docker container logs."""
    if not is_docker_installed() or not is_docker_container_running(container_name):
        return None
    
    try:
        result = subprocess.run(
            ["docker", "logs", "--tail", str(lines), container_name],
            capture_output=True,
            text=True,
            check=True
        )
        
        logs = result.stdout
        logger.info(f"Container logs: {logs}")
        
        # Check for common errors
        if "license error" in logs.lower():
            logger.error("License error detected in container logs")
        
        return logs
    except subprocess.CalledProcessError as e:
        logger.error(f"Error checking container logs: {e}")
        return None

# Try to import Ansys Geometry Core
ANSYS_AVAILABLE = False
try:
    import ansys.geometry.core as agc
    from ansys.geometry.core import Modeler
    ANSYS_AVAILABLE = True
    logger.info("Ansys Geometry Core imported successfully")
except ImportError as e:
    logger.warning(f"Could not import Ansys Geometry Core: {e}")
    logger.warning("Ansys integration will be disabled - using simulation mode")

class AnsysRocketInterface:
    """Interface between Rocket Design and Ansys Geometry for analysis."""
    
    def __init__(self, working_dir=None, use_docker=True, use_spaceclaim=True):
        """
        Initialize the Ansys interface.
        
        Parameters
        ----------
        working_dir : str, optional
            Working directory for Ansys files.
        use_docker : bool, optional
            Whether to try using Docker for Ansys Geometry.
        use_spaceclaim : bool, optional
            Whether to try using SpaceClaim for Ansys Geometry.
        """
        self.working_dir = working_dir or os.path.join(os.getcwd(), "output", "ansys")
        os.makedirs(self.working_dir, exist_ok=True)
        
        self.modeler = None
        self.design = None
        self.rocket_bodies = {}
        self.simulation_mode = not ANSYS_AVAILABLE
        self.use_docker = use_docker
        self.use_spaceclaim = use_spaceclaim
        
        # Connection method used
        self.connection_method = None
        
        if not self.simulation_mode:
            self._connect_to_ansys()
    
    def _connect_to_ansys(self):
        """Connect to the Ansys Geometry service."""
        if self.simulation_mode:
            logger.info("Running in simulation mode (Ansys not available)")
            return False
        
        try:
            # Enhanced logging for the connection process
            logger.info("====== ANSYS GEOMETRY SERVICE CONNECTION PROCESS ======")
            logger.info("Checking for Ansys Geometry service...")
            
            # Check system environment
            logger.info(f"Operating System: {os.name} - {sys.platform}")
            python_version = sys.version.replace('\n', ' ')
            logger.info(f"Python Version: {python_version}")
            
            try:
                import ansys
                logger.info(f"PyAnsys Version: {ansys.__version__}")
            except (ImportError, AttributeError):
                logger.info("PyAnsys Version: Unknown")
            
            # Connection succeeded flag
            connection_succeeded = False
            
            # Try Docker container connection first if enabled
            if self.use_docker:
                logger.info("Attempting to use Docker container for Ansys Geometry...")
                
                if is_docker_installed():
                    # Check if container is running or start it
                    if not is_docker_container_running() and not start_docker_container():
                        logger.warning("Failed to start Docker container, trying SpaceClaim instead")
                    else:
                        # Docker container is running, try to connect
                        logger.info("Docker container is running, attempting to connect...")
                        
                        # Set environment variables for custom connection (if needed)
                        os.environ["ANSRV_GEO_HOST"] = "localhost"
                        os.environ["ANSRV_GEO_PORT"] = str(DOCKER_CONFIG["port"])
                        
                        try:
                            # Try to create the modeler
                            logger.info("Creating Ansys Geometry Modeler instance via Docker...")
                            self.modeler = Modeler(host="localhost", port=DOCKER_CONFIG["port"])
                            logger.info("SUCCESS: Connected to Ansys Geometry service via Docker!")
                            
                            # Create a new design
                            logger.info("Creating new design in Ansys Geometry...")
                            self.design = self.modeler.create_design("RocketDesign")
                            logger.info("SUCCESS: Created new Ansys design: RocketDesign")
                            
                            logger.info("====== ANSYS GEOMETRY CONNECTION SUCCESSFUL (Docker) ======")
                            self.connection_method = "docker"
                            connection_succeeded = True
                        except Exception as e:
                            logger.warning(f"Failed to connect to Docker container: {e}")
                            logger.warning("Checking Docker container logs...")
                            check_docker_logs()
                else:
                    logger.warning("Docker is not available, trying SpaceClaim instead")
            
            # Try SpaceClaim if Docker failed and SpaceClaim is enabled
            if not connection_succeeded and self.use_spaceclaim:
                logger.info("Attempting to use SpaceClaim for Ansys Geometry...")
                
                # Check and start SpaceClaim if needed
                if not is_spaceclaim_running():
                    spaceclaim_path = find_spaceclaim_executable()
                    if spaceclaim_path:
                        logger.info(f"SpaceClaim found at: {spaceclaim_path}")
                        logger.info("SpaceClaim not running, attempting to start it...")
                        if not start_spaceclaim(spaceclaim_path):
                            logger.warning("Could not start SpaceClaim. Falling back to simulation mode.")
                            logger.info("DIAGNOSIS: Check if SpaceClaim installation is correct and that you have permissions to run it.")
                            self.simulation_mode = True
                            return False
                    else:
                        logger.warning("SpaceClaim not found in standard installation paths.")
                        logger.info("Searched in the following locations:")
                        for path in SPACECLAIM_PATHS:
                            logger.info(f"  - {path} : {'EXISTS' if os.path.exists(path) else 'NOT FOUND'}")
                        logger.warning("Falling back to simulation mode.")
                        self.simulation_mode = True
                        return False
                else:
                    logger.info("SpaceClaim is already running - will attempt to connect to its Geometry service")
                
                # Enhanced logging for connections
                logger.info("Connecting to Ansys Geometry service via SpaceClaim...")
                logger.info("This connection uses gRPC to communicate with the Ansys Geometry service running in SpaceClaim")
                logger.info("Default connection parameters: localhost:50051")
                
                # Try to get service details
                try:
                    import grpc
                    from ansys.geometry.core.connection import DEFAULT_CONFIGURATION
                    
                    # Get default connection config if available
                    default_host = getattr(DEFAULT_CONFIGURATION, 'host', 'localhost')
                    default_port = getattr(DEFAULT_CONFIGURATION, 'port', '50051')
                    logger.info(f"Attempting connection to: {default_host}:{default_port}")
                    
                    # Try a quick connection check
                    channel = grpc.insecure_channel(f"{default_host}:{default_port}")
                    try:
                        # This will throw if the connection cannot be established
                        state = channel.get_state(try_to_connect=True)
                        logger.info(f"gRPC channel state: {state}")
                        channel.close()
                    except Exception as e:
                        logger.warning(f"gRPC connection test failed: {e}")
                except Exception as e:
                    logger.info(f"Could not check gRPC connection details: {e}")
                
                # Attempt to create the modeler - this is the real connection test
                try:
                    logger.info("Creating Ansys Geometry Modeler instance via SpaceClaim...")
                    self.modeler = Modeler()
                    logger.info("SUCCESS: Connected to Ansys Geometry service via SpaceClaim!")
                    
                    # Create a new design
                    logger.info("Creating new design in Ansys Geometry...")
                    self.design = self.modeler.create_design("RocketDesign")
                    logger.info("SUCCESS: Created new Ansys design: RocketDesign")
                    
                    logger.info("====== ANSYS GEOMETRY CONNECTION SUCCESSFUL (SpaceClaim) ======")
                    self.connection_method = "spaceclaim"
                    connection_succeeded = True
                except Exception as e:
                    logger.warning(f"Failed to connect to SpaceClaim: {e}")
            
            # If all connection methods failed, fall back to simulation mode
            if not connection_succeeded:
                logger.error("All connection methods failed, falling back to simulation mode")
                self.simulation_mode = True
                return False
                
            return True
        except Exception as e:
            logger.error("====== ANSYS GEOMETRY CONNECTION FAILED ======")
            logger.error(f"Failed to connect to Ansys Geometry service: {e}")
            
            # More detailed error diagnostics
            logger.error("DIAGNOSIS:")
            logger.error("1. Ensure SpaceClaim or Docker with Ansys Geometry is properly installed and running")
            logger.error("2. Check that the Ansys Geometry service is enabled")
            logger.error("3. Verify you have the correct version of PyAnsys installed")
            logger.error("4. Check for firewall or network issues blocking localhost:50051")
            
            import traceback
            logger.error("Detailed error traceback:")
            logger.error(traceback.format_exc())
            
            self.simulation_mode = True
            return False
    
    def create_rocket_from_parameters(self, rocket_config, engine_config):
        """
        Create a rocket model directly in Ansys using configuration parameters.
        
        Parameters
        ----------
        rocket_config : dict
            Dictionary containing rocket configuration parameters.
        engine_config : dict
            Dictionary containing engine configuration parameters.
            
        Returns
        -------
        bool
            True if successful, False otherwise.
        """
        # Extract parameters from config for use in simulation mode
        total_length = rocket_config["total_length"]
        max_diameter = rocket_config["max_diameter"]
        first_stage_length = total_length * rocket_config["first_stage_length_ratio"]
        second_stage_length = total_length * (1 - rocket_config["first_stage_length_ratio"] - 
                                            rocket_config["nose_cone_length_ratio"])
        nose_cone_length = total_length * rocket_config["nose_cone_length_ratio"]
        
        if self.simulation_mode:
            logger.info("Creating simulated rocket model (Ansys not available)...")
            # In simulation mode, just record that we would have created these parts
            self.rocket_bodies = {
                "first_stage": {"name": "FirstStage", "type": "cylinder", 
                               "diameter": max_diameter, "length": first_stage_length},
                "second_stage": {"name": "SecondStage", "type": "cylinder", 
                                "diameter": max_diameter * 0.9, "length": second_stage_length},
                "nose_cone": {"name": "NoseCone", "type": "cone", 
                             "base_diameter": max_diameter * 0.9, "length": nose_cone_length},
                "nozzle": {"name": "Nozzle", "type": "cone", 
                          "throat_diameter": engine_config["throat_diameter"],
                          "exit_diameter": engine_config["exit_diameter"],
                          "length": engine_config["length"]}
            }
            logger.info("Simulated rocket model created successfully")
            return True
        
        try:
            logger.info("Creating rocket model in Ansys Geometry...")
            
            # Create first stage
            first_stage = self.design.add_cylinder(
                origin=agc.math.Point3D(0, 0, 0),
                axis=agc.math.UnitVector3D(0, 0, 1),
                radius=max_diameter/2,
                height=first_stage_length,
                name="FirstStage"
            )
            self.rocket_bodies["first_stage"] = first_stage
            
            # Create second stage (slightly smaller diameter)
            second_stage_diameter = max_diameter * 0.9
            second_stage = self.design.add_cylinder(
                origin=agc.math.Point3D(0, 0, first_stage_length),
                axis=agc.math.UnitVector3D(0, 0, 1),
                radius=second_stage_diameter/2,
                height=second_stage_length,
                name="SecondStage"
            )
            self.rocket_bodies["second_stage"] = second_stage
            
            # Create nose cone
            nose_cone = self.design.add_cone(
                origin=agc.math.Point3D(0, 0, first_stage_length + second_stage_length),
                axis=agc.math.UnitVector3D(0, 0, 1),
                radius=second_stage_diameter/2,
                height=nose_cone_length,
                name="NoseCone"
            )
            self.rocket_bodies["nose_cone"] = nose_cone
            
            # Create engine nozzle
            throat_d = engine_config["throat_diameter"]
            exit_d = engine_config["exit_diameter"]
            nozzle_length = engine_config["length"]
            
            nozzle = self.design.add_cone(
                origin=agc.math.Point3D(0, 0, -nozzle_length),
                axis=agc.math.UnitVector3D(0, 0, 1),
                radius1=exit_d/2,
                radius2=throat_d/2,
                height=nozzle_length,
                name="Nozzle"
            )
            self.rocket_bodies["nozzle"] = nozzle
            
            logger.info("Rocket model created successfully in Ansys Geometry")
            return True
        except Exception as e:
            logger.error(f"Failed to create rocket model in Ansys: {e}")
            # Switch to simulation mode on error
            self.simulation_mode = True
            
            # Retry with simulation mode
            return self.create_rocket_from_parameters(rocket_config, engine_config)
    
    def import_step_model(self, step_file_path):
        """
        Import a STEP file into Ansys Geometry.
        
        Parameters
        ----------
        step_file_path : str
            Path to the STEP file.
            
        Returns
        -------
        bool
            True if successful, False otherwise.
        """
        if not os.path.exists(step_file_path):
            logger.error(f"STEP file not found: {step_file_path}")
            return False
            
        if self.simulation_mode:
            logger.info(f"Simulating import of STEP file: {step_file_path}")
            # In simulation mode, just record that we would have imported this file
            self.rocket_bodies = {
                "imported_body_0": {"name": "ImportedRocket", "source": step_file_path}
            }
            logger.info("Simulated STEP import successful")
            return True
        
        try:
            logger.info(f"Importing STEP file: {step_file_path}")
            
            imported_bodies = self.design.import_cad(step_file_path)
            logger.info(f"Successfully imported {len(imported_bodies)} bodies from STEP file")
            
            # Store imported bodies
            for i, body in enumerate(imported_bodies):
                self.rocket_bodies[f"imported_body_{i}"] = body
            
            return True
        except Exception as e:
            logger.error(f"Failed to import STEP file: {e}")
            # Switch to simulation mode on error
            self.simulation_mode = True
            
            # Retry with simulation mode
            return self.import_step_model(step_file_path)
    
    def setup_fluid_analysis(self):
        """
        Set up fluid analysis for the rocket model.
        
        This prepares the model for CFD analysis in Ansys Fluent.
        
        Returns
        -------
        bool
            True if successful, False otherwise.
        """
        if not self.rocket_bodies:
            logger.warning("No rocket bodies available. Cannot set up fluid analysis.")
            return False
            
        if self.simulation_mode:
            logger.info("Simulating fluid analysis setup (Ansys not available)...")
            # Just simulate the process in this mode
            logger.info("Simulated fluid domain created around rocket")
            logger.info("Simulated flow volume prepared for CFD analysis")
            return True
        
        try:
            logger.info("Setting up fluid analysis for rocket model...")
            
            # Find the extent of our rocket model
            z_min = float('inf')
            z_max = float('-inf')
            radius_max = 0
            
            for body in self.rocket_bodies.values():
                bbox = body.bounding_box
                z_min = min(z_min, bbox.min_z)
                z_max = max(z_max, bbox.max_z)
                radius_max = max(radius_max, max(bbox.max_x, bbox.max_y))
            
            # Add some padding
            domain_radius = radius_max * 5
            domain_z_min = z_min - (z_max - z_min)
            domain_z_max = z_max + (z_max - z_min) * 2
            domain_length = domain_z_max - domain_z_min
            
            # Create fluid domain cylinder
            fluid_domain = self.design.add_cylinder(
                origin=agc.math.Point3D(0, 0, domain_z_min),
                axis=agc.math.UnitVector3D(0, 0, 1),
                radius=domain_radius,
                height=domain_length,
                name="FluidDomain"
            )
            
            # Subtract rocket from fluid domain to create the flow volume
            flow_volume = fluid_domain.subtract([body for body in self.rocket_bodies.values()])
            flow_volume.name = "FlowVolume"
            
            logger.info("Fluid analysis setup completed")
            
            # Export for Ansys Fluent
            self._export_for_fluent(flow_volume)
            
            return True
        except Exception as e:
            logger.error(f"Failed to setup fluid analysis: {e}")
            # Switch to simulation mode on error
            self.simulation_mode = True
            
            # Retry with simulation mode
            return self.setup_fluid_analysis()
    
    def setup_structural_analysis(self):
        """
        Set up structural analysis for the rocket model.
        
        This prepares the model for structural analysis in Ansys Mechanical.
        
        Returns
        -------
        bool
            True if successful, False otherwise.
        """
        if not self.rocket_bodies:
            logger.warning("No rocket bodies available. Cannot set up structural analysis.")
            return False
            
        if self.simulation_mode:
            logger.info("Simulating structural analysis setup (Ansys not available)...")
            # Just simulate the process in this mode
            logger.info("Simulated material properties assigned to rocket components")
            logger.info("Simulated model exported for structural analysis")
            return True
        
        try:
            logger.info("Setting up structural analysis for rocket model...")
            
            # Export model for Ansys Mechanical
            self._export_for_mechanical()
            
            logger.info("Structural analysis setup completed")
            return True
        except Exception as e:
            logger.error(f"Failed to setup structural analysis: {e}")
            # Switch to simulation mode on error
            self.simulation_mode = True
            
            # Retry with simulation mode
            return self.setup_structural_analysis()
    
    def _export_for_fluent(self, flow_volume=None):
        """
        Export the model for Ansys Fluent CFD analysis.
        
        Parameters
        ----------
        flow_volume : ansys.geometry.core.bodies.Body, optional
            The flow volume to export.
        """
        if self.simulation_mode:
            # In simulation mode, create placeholder files
            fluent_file = os.path.join(self.working_dir, "rocket_flow_volume.step")
            logger.info(f"Creating placeholder for Fluent export: {fluent_file}")
            
            # Create an empty file as a placeholder
            with open(fluent_file, 'w') as f:
                f.write("# This is a placeholder file for Ansys Fluent export\n")
                f.write("# In simulation mode, no actual geometry data is available\n")
            
            logger.info("Placeholder for Fluent export created")
            return
        
        try:
            # Export to Fluent-compatible format
            fluent_file = os.path.join(self.working_dir, "rocket_flow_volume.step")
            logger.info(f"Exporting model for Fluent: {fluent_file}")
            
            # In a real implementation, we would use specific Fluent export methods
            # For now, we'll export as STEP which can be imported into Fluent
            self.design.export_cad([flow_volume], fluent_file)
            
            logger.info("Model exported for Fluent analysis")
        except Exception as e:
            logger.error(f"Failed to export for Fluent: {e}")
    
    def _export_for_mechanical(self):
        """Export the model for Ansys Mechanical structural analysis."""
        if self.simulation_mode:
            # In simulation mode, create placeholder files
            mech_file = os.path.join(self.working_dir, "rocket_mechanical.step")
            logger.info(f"Creating placeholder for Mechanical export: {mech_file}")
            
            # Create an empty file as a placeholder
            with open(mech_file, 'w') as f:
                f.write("# This is a placeholder file for Ansys Mechanical export\n")
                f.write("# In simulation mode, no actual geometry data is available\n")
            
            logger.info("Placeholder for Mechanical export created")
            return
            
        try:
            # Export to Mechanical-compatible format
            mech_file = os.path.join(self.working_dir, "rocket_mechanical.step")
            logger.info(f"Exporting model for Mechanical: {mech_file}")
            
            # Export all rocket bodies for structural analysis
            self.design.export_cad(list(self.rocket_bodies.values()), mech_file)
            
            logger.info("Model exported for Mechanical analysis")
        except Exception as e:
            logger.error(f"Failed to export for Mechanical: {e}")
    
    def generate_analysis_report(self, output_dir=None):
        """
        Generate a report with details of the Ansys analysis setup.
        
        Parameters
        ----------
        output_dir : str, optional
            Directory where the report will be saved.
            
        Returns
        -------
        str
            Path to the generated report file.
        """
        output_dir = output_dir or os.path.join(os.getcwd(), "output", "reports")
        os.makedirs(output_dir, exist_ok=True)
        
        report_file = os.path.join(output_dir, "ansys_analysis_report.md")
        
        try:
            with open(report_file, 'w') as f:
                f.write("# Rocket Design - Ansys Analysis Setup Report\n\n")
                
                if self.simulation_mode:
                    f.write("> **Note:** This report was generated in simulation mode because Ansys Geometry Core is not available. It represents what would be done in Ansys but no actual Ansys operations were performed.\n\n")
                
                f.write("## Model Components\n\n")
                if self.rocket_bodies:
                    f.write("The following components were created for Ansys Geometry:\n\n")
                    for name, body in self.rocket_bodies.items():
                        if self.simulation_mode:
                            # In simulation mode, body is a dict with descriptive info
                            if isinstance(body, dict):
                                f.write(f"- **{name}**: {body.get('name', 'Unnamed')}")
                                if 'type' in body:
                                    f.write(f" ({body['type']})")
                                f.write("\n")
                        else:
                            # In real mode, body is an Ansys object
                            f.write(f"- **{name}**: {body.name}\n")
                else:
                    f.write("No components were created in Ansys Geometry.\n")
                
                f.write("\n## Analysis Types\n\n")
                f.write("### Fluid Dynamics Analysis\n\n")
                f.write("- **Analysis Type**: Computational Fluid Dynamics (CFD)\n")
                f.write("- **Target Software**: Ansys Fluent\n")
                f.write("- **Physics Models**: External Aerodynamics, Compressible Flow\n")
                f.write("- **Expected Outputs**: Pressure distribution, drag coefficient, velocity field\n\n")
                
                f.write("### Structural Analysis\n\n")
                f.write("- **Analysis Type**: Static Structural\n")
                f.write("- **Target Software**: Ansys Mechanical\n")
                f.write("- **Physics Models**: Linear Elasticity\n")
                f.write("- **Expected Outputs**: Stress distribution, deformation, factor of safety\n\n")
                
                f.write("## Export Locations\n\n")
                f.write(f"- Fluent Analysis Files: `{os.path.join(self.working_dir, 'rocket_flow_volume.step')}`\n")
                f.write(f"- Mechanical Analysis Files: `{os.path.join(self.working_dir, 'rocket_mechanical.step')}`\n\n")
                
                f.write("## Next Steps\n\n")
                f.write("1. Open the exported files in the respective Ansys applications\n")
                f.write("2. Define boundary conditions and simulation parameters\n")
                f.write("3. Run the simulations\n")
                f.write("4. Analyze results and iterate on the design as needed\n")
                
                if self.simulation_mode:
                    f.write("\n## Using This Report With Ansys\n\n")
                    f.write("Since this report was generated in simulation mode, you'll need to:\n\n")
                    f.write("1. Create the rocket geometry directly in Ansys SpaceClaim or import from FreeCAD\n")
                    f.write("2. Follow the analysis setup guidelines outlined above\n")
                    f.write("3. Manually set up the fluid and structural analyses\n\n")
                    f.write("To use the full Ansys integration functionality, install the required PyAnsys packages:\n\n")
                    f.write("```\npip install ansys-geometry-core\n```\n")
            
            logger.info(f"Analysis report generated: {report_file}")
            return report_file
        except Exception as e:
            logger.error(f"Failed to generate analysis report: {e}")
            return None

def integrate_with_freecad_model(freecad_model_path, output_dir=None):
    """
    Integrate a FreeCAD model with Ansys for analysis.
    
    Parameters
    ----------
    freecad_model_path : str
        Path to the FreeCAD model file (FCStd or STEP).
    output_dir : str, optional
        Directory for output files.
        
    Returns
    -------
    bool
        True if successful, False otherwise.
    """
    output_dir = output_dir or os.path.join(os.getcwd(), "output", "ansys")
    os.makedirs(output_dir, exist_ok=True)
    
    # Check if the model file exists
    if not os.path.exists(freecad_model_path):
        logger.error(f"Model file not found: {freecad_model_path}")
        return False
    
    # Extract file extension
    _, ext = os.path.splitext(freecad_model_path)
    
    # If it's a FreeCAD file, attempt to convert it to STEP first
    step_file_path = freecad_model_path
    if ext.lower() == '.fcstd':
        step_file_path = os.path.join(output_dir, "freecad_model.step")
        logger.info(f"Converting FreeCAD model to STEP: {step_file_path}")
        
        try:
            # Try to use FreeCAD to convert the file
            import FreeCAD
            import Import
            
            doc = FreeCAD.open(freecad_model_path)
            Import.export(doc.Objects, step_file_path)
            logger.info(f"FreeCAD model converted to STEP: {step_file_path}")
        except ImportError:
            logger.error("FreeCAD module could not be imported for conversion.")
            logger.warning("Creating a copy of the original file as a fallback...")
            
            # Just copy the file as a fallback if it's already a STEP file
            if ext.lower() == '.step':
                import shutil
                shutil.copy(freecad_model_path, step_file_path)
                logger.info(f"Copied original STEP file to: {step_file_path}")
            else:
                logger.error("Please manually export the FreeCAD model to STEP format.")
                return False
        except Exception as e:
            logger.error(f"Failed to convert FreeCAD model to STEP: {e}")
            return False
    
    # Now we have a STEP file, let's import it into Ansys
    ansys_interface = AnsysRocketInterface(working_dir=output_dir)
    success = ansys_interface.import_step_model(step_file_path)
    
    if not success:
        return False
    
    # Set up analyses
    ansys_interface.setup_fluid_analysis()
    ansys_interface.setup_structural_analysis()
    
    # Generate report
    report_file = ansys_interface.generate_analysis_report()
    
    if report_file:
        logger.info(f"Integration complete. See report at: {report_file}")
        return True
    else:
        logger.error("Integration failed while generating the report.")
        return False

def create_rocket_in_ansys(rocket_config, engine_config, output_dir=None):
    """
    Create a rocket model directly in Ansys using configuration parameters.
    
    Parameters
    ----------
    rocket_config : dict
        Dictionary containing rocket configuration parameters.
    engine_config : dict
        Dictionary containing engine configuration parameters.
    output_dir : str, optional
        Directory for output files.
        
    Returns
    -------
    bool
        True if successful, False otherwise.
    """
    output_dir = output_dir or os.path.join(os.getcwd(), "output", "ansys")
    os.makedirs(output_dir, exist_ok=True)
    
    # Create the Ansys interface
    ansys_interface = AnsysRocketInterface(working_dir=output_dir)
    
    # Create the rocket model directly in Ansys
    success = ansys_interface.create_rocket_from_parameters(rocket_config, engine_config)
    
    if not success:
        return False
    
    # Set up analyses
    ansys_interface.setup_fluid_analysis()
    ansys_interface.setup_structural_analysis()
    
    # Generate report
    report_file = ansys_interface.generate_analysis_report()
    
    if report_file:
        logger.info(f"Rocket creation in Ansys complete. See report at: {report_file}")
        return True
    else:
        logger.error("Rocket creation in Ansys failed while generating the report.")
        return False

if __name__ == "__main__":
    # Example usage
    rocket_config = {
        "total_length": 5000,      # mm
        "max_diameter": 500,       # mm
        "first_stage_length_ratio": 0.6,
        "nose_cone_length_ratio": 0.15,
        "fin_count": 4
    }
    
    engine_config = {
        "throat_diameter": 30,     # mm
        "exit_diameter": 150,      # mm
        "length": 300,             # mm
    }
    
    # Create the rocket directly in Ansys
    create_rocket_in_ansys(rocket_config, engine_config)
