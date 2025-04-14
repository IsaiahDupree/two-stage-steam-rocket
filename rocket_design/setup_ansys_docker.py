#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Ansys Geometry Docker Container Setup Script.

This script helps set up and manage the Ansys Geometry Docker container
with proper license configuration for integration with the rocket design project.
"""

import os
import sys
import time
import subprocess
import argparse
import logging
import socket
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("AnsysDockerSetup")

# Default configuration
DEFAULT_CONFIG = {
    "container_name": "ans_geo",
    "image": "ghcr.io/ansys/geometry:latest",
    "port": 50051,
    "license_server": "Orion:49768",
    "enable_trace": "false",
    "log_level": "info"
}

def check_docker_installed():
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
            logger.error("Docker is installed but not running")
            logger.error(result.stderr)
            return False
        
        logger.info("Docker is running")
        return True
    except FileNotFoundError:
        logger.error("Docker is not installed or not in PATH")
        return False
    except subprocess.CalledProcessError as e:
        logger.error(f"Error checking Docker: {e}")
        return False

def check_ansys_docker_auth():
    """Check if Docker is authenticated with Ansys container registry."""
    try:
        # Check if logged in to ghcr.io
        result = subprocess.run(
            ["docker", "login", "ghcr.io", "--password-stdin"],
            input="\n",  # Empty password to check current auth status
            capture_output=True,
            text=True
        )
        
        if "Login Succeeded" in result.stdout or "Login Succeeded" in result.stderr:
            logger.info("Already authenticated with ghcr.io")
            return True
        else:
            logger.warning("Not authenticated with Ansys container registry (ghcr.io)")
            logger.warning("You need proper Ansys credentials to access the container images")
            return False
    except subprocess.CalledProcessError as e:
        logger.error(f"Error checking Docker authentication: {e}")
        return False

def authenticate_with_ansys_registry(username=None, password=None):
    """Authenticate with the Ansys container registry."""
    if username is None:
        username = input("Enter your Ansys Container Registry username: ")
    
    if password is None:
        import getpass
        password = getpass.getpass("Enter your Ansys Container Registry password: ")
    
    try:
        result = subprocess.run(
            ["docker", "login", "ghcr.io", "-u", username, "--password-stdin"],
            input=password,
            capture_output=True,
            text=True
        )
        
        if "Login Succeeded" in result.stdout or "Login Succeeded" in result.stderr:
            logger.info("Successfully authenticated with Ansys container registry")
            return True
        else:
            logger.error("Failed to authenticate with Ansys container registry")
            logger.error(result.stderr)
            return False
    except subprocess.CalledProcessError as e:
        logger.error(f"Error authenticating with Docker: {e}")
        return False

def check_port_available(port):
    """Check if the specified port is available."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.bind(("localhost", port))
            logger.info(f"Port {port} is available")
            return True
        except socket.error:
            logger.warning(f"Port {port} is already in use")
            return False

def check_container_running(container_name):
    """Check if a container with the given name is already running."""
    try:
        result = subprocess.run(
            ["docker", "ps", "-a", "--filter", f"name={container_name}", "--format", "{{.Status}}"],
            capture_output=True,
            text=True,
            check=True
        )
        if "Up" in result.stdout:
            logger.info(f"Container '{container_name}' is already running")
            return True
        elif result.stdout.strip():
            logger.info(f"Container '{container_name}' exists but is not running")
            return False
        else:
            logger.info(f"Container '{container_name}' does not exist")
            return False
    except subprocess.CalledProcessError as e:
        logger.error(f"Error checking container status: {e}")
        return False

def start_container(config):
    """Start the Ansys Geometry Docker container."""
    container_name = config["container_name"]
    image = config["image"]
    port = config["port"]
    license_server = config["license_server"]
    enable_trace = config["enable_trace"]
    log_level = config["log_level"]
    
    # Check if container is already running
    if check_container_running(container_name):
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
        if result.stdout.strip() == container_name:
            logger.info(f"Starting existing container '{container_name}'")
            subprocess.run(["docker", "start", container_name], check=True)
            logger.info(f"Container '{container_name}' started successfully")
            return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Error checking container existence: {e}")
    
    # Check authentication with Ansys registry if using Ansys image
    if "ghcr.io/ansys" in image and not check_ansys_docker_auth():
        logger.warning("You need to authenticate with the Ansys container registry")
        print("\nIMPORTANT: Ansys Docker images require authentication")
        print("This is typically available only to licensed Ansys users")
        print("Please contact your Ansys administrator for access\n")
        
        # Offer alternative approaches
        print("Alternative approaches:")
        print("1. Use a local Ansys SpaceClaim installation instead of Docker")
        print("2. Obtain proper credentials for the Ansys container registry")
        print("3. Use simulation mode for development without Ansys\n")
        
        use_alt = input("Would you like to use a local SpaceClaim installation? (y/n): ")
        if use_alt.lower() == 'y':
            print("Please run the connection test with --no-docker --spaceclaim flags")
            return False
        
        try_auth = input("Would you like to try authenticating with Ansys registry? (y/n): ")
        if try_auth.lower() == 'y':
            if not authenticate_with_ansys_registry():
                return False
        else:
            return False
    
    # Create and start new container
    try:
        logger.info(f"Creating new Ansys Geometry container '{container_name}'")
        cmd = [
            "docker", "run",
            "-d",  # Detached mode
            "--name", container_name,
            "-e", f"LICENSE_SERVER={license_server}",
            "-e", f"ENABLE_TRACE={enable_trace}",
            "-e", f"LOG_LEVEL={log_level}",
            "-p", f"{port}:{port}",
            image
        ]
        
        subprocess.run(cmd, check=True)
        logger.info(f"Container '{container_name}' created and started successfully")
        
        # Give the container a moment to initialize
        logger.info("Waiting for the container to initialize...")
        time.sleep(5)
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Error starting container: {e}")
        
        if "unable to find image" in str(e).lower() or "failed to resolve reference" in str(e).lower():
            logger.error("Could not find or access the specified Docker image")
            logger.error("This may be due to:")
            logger.error("1. Missing authentication for the Ansys container registry")
            logger.error("2. Invalid image name or tag")
            logger.error("3. Network connectivity issues")
            
            # Provide detailed troubleshooting advice
            print("\nTroubleshooting steps:")
            print("1. Ensure you have a valid Ansys license")
            print("2. Authenticate with the Ansys container registry:")
            print("   docker login ghcr.io -u YOUR_USERNAME")
            print("3. Verify your internet connection")
            print("4. If available, try using SpaceClaim directly instead of Docker")
        
        return False

def stop_container(container_name):
    """Stop the Ansys Geometry Docker container."""
    if not check_container_running(container_name):
        logger.info(f"Container '{container_name}' is not running")
        return True
    
    try:
        logger.info(f"Stopping container '{container_name}'")
        subprocess.run(["docker", "stop", container_name], check=True)
        logger.info(f"Container '{container_name}' stopped successfully")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Error stopping container: {e}")
        return False

def check_container_logs(container_name, lines=50):
    """Check the logs of the Ansys Geometry Docker container."""
    try:
        logger.info(f"Checking logs for container '{container_name}'")
        result = subprocess.run(
            ["docker", "logs", "--tail", str(lines), container_name],
            capture_output=True,
            text=True,
            check=True
        )
        
        logs = result.stdout
        
        # Check for common errors in logs
        if "license error" in logs.lower() or "failed to acquire license" in logs.lower():
            logger.error("License error detected in container logs")
            logger.error("Make sure the license server is correctly configured")
        elif "error" in logs.lower():
            logger.warning("Potential issues detected in container logs")
        else:
            logger.info("No obvious errors found in container logs")
        
        print("\nContainer Logs:")
        print("=" * 80)
        print(logs)
        print("=" * 80)
        
        return logs
    except subprocess.CalledProcessError as e:
        logger.error(f"Error checking container logs: {e}")
        return None

def test_connection():
    """Test connection to the Ansys Geometry service using PyAnsys."""
    try:
        import ansys.geometry.core
        from ansys.geometry.core import launch_modeler
        
        logger.info("Testing connection to Ansys Geometry service...")
        logger.info("This may take a few moments...")
        
        try:
            modeler = launch_modeler()
            logger.info("Successfully connected to Ansys Geometry service!")
            
            # Create a simple test design
            design = modeler.create_design("DockerTestDesign")
            logger.info("Successfully created test design")
            
            # Clean up
            design.delete()
            logger.info("Test design deleted")
            
            return True
        except Exception as e:
            logger.error(f"Failed to connect to Ansys Geometry service: {e}")
            logger.error("Check the container logs for more details")
            
            print("\nCommon issues and solutions:")
            print("1. License issues: Ensure your license server is correctly configured")
            print(f"   Current license server setting: {DEFAULT_CONFIG['license_server']}")
            print("2. Network issues: Make sure port 50051 is not blocked by firewall")
            print("3. Container not running properly: Check the container logs")
            
            return False
    except ImportError:
        logger.error("PyAnsys Geometry package is not installed")
        logger.error("Install with: pip install ansys-geometry-core")
        return False

def main():
    """Main function to run the script."""
    parser = argparse.ArgumentParser(
        description="Set up and manage Ansys Geometry Docker container"
    )
    
    parser.add_argument(
        "--action",
        choices=["start", "stop", "restart", "logs", "test", "auth", "all"],
        default="all",
        help="Action to perform (default: all)"
    )
    
    parser.add_argument(
        "--license-server",
        default=DEFAULT_CONFIG["license_server"],
        help=f"License server (default: {DEFAULT_CONFIG['license_server']})"
    )
    
    parser.add_argument(
        "--port",
        type=int,
        default=DEFAULT_CONFIG["port"],
        help=f"Port to use (default: {DEFAULT_CONFIG['port']})"
    )
    
    parser.add_argument(
        "--container-name",
        default=DEFAULT_CONFIG["container_name"],
        help=f"Container name (default: {DEFAULT_CONFIG['container_name']})"
    )
    
    parser.add_argument(
        "--image",
        default=DEFAULT_CONFIG["image"],
        help=f"Docker image (default: {DEFAULT_CONFIG['image']})"
    )
    
    parser.add_argument(
        "--username",
        help="Username for Ansys container registry"
    )
    
    parser.add_argument(
        "--password",
        help="Password for Ansys container registry (not recommended, use interactive prompt instead)"
    )
    
    args = parser.parse_args()
    
    # Check Docker installation
    if not check_docker_installed():
        logger.error("Docker is required to run this script")
        return 1
    
    # Create config dictionary
    config = {
        "container_name": args.container_name,
        "image": args.image,
        "port": args.port,
        "license_server": args.license_server,
        "enable_trace": DEFAULT_CONFIG["enable_trace"],
        "log_level": DEFAULT_CONFIG["log_level"]
    }
    
    # Handle authentication if requested
    if args.action == "auth":
        authenticate_with_ansys_registry(args.username, args.password)
        return 0
    
    # Perform the requested action
    if args.action in ["start", "all", "restart"]:
        if args.action == "restart":
            stop_container(config["container_name"])
        
        if not start_container(config):
            logger.error("Failed to start container")
            return 1
    
    if args.action in ["logs", "all"]:
        check_container_logs(config["container_name"])
    
    if args.action in ["test", "all"]:
        test_connection()
    
    if args.action == "stop":
        stop_container(config["container_name"])
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
