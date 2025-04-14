#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Performance analysis module for the two-stage rocket with steam propulsion.
This module provides advanced metrics, calculations, and visualizations for rocket performance.
"""

import os
import math
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
import matplotlib.gridspec as gridspec
from scipy.integrate import solve_ivp


class RocketPerformanceAnalyzer:
    """
    Comprehensive analyzer for rocket performance metrics, handling flow rates,
    pressures, velocities, trajectories, and optimization studies.
    """
    
    def __init__(self, rocket_config, engine_config, propulsion_config):
        """
        Initialize the performance analyzer with rocket, engine, and propulsion configurations.
        
        Args:
            rocket_config: Dictionary containing rocket geometry parameters
            engine_config: Dictionary containing engine design parameters
            propulsion_config: Dictionary containing propulsion system parameters
        """
        self.rocket_config = rocket_config
        self.engine_config = engine_config
        self.propulsion_config = propulsion_config
        
        # Physical constants
        self.g0 = 9.81  # m/s² - Earth's gravitational acceleration at sea level
        self.R_air = 287.05  # J/(kg·K) - Gas constant for air
        self.R_steam = 461.5  # J/(kg·K) - Gas constant for steam
        self.gamma_steam = 1.3  # Specific heat ratio for steam
        
        # Standard atmospheric conditions
        self.p0 = 101325  # Pa - Sea level pressure
        self.T0 = 288.15  # K - Sea level temperature
        self.rho0 = 1.225  # kg/m³ - Sea level air density
        
        # Derived parameters
        self.dry_mass = self._calculate_dry_mass()
        self.propellant_mass = propulsion_config["propellant_mass"]
        self.burn_time = propulsion_config["burn_duration"]
        self.total_mass = self.dry_mass + self.propellant_mass
        
        # Engine parameters
        self.chamber_pressure = propulsion_config["initial_pressure"] * 1e6  # Pa
        self.chamber_temperature = propulsion_config["initial_temperature"]  # K
        self.throat_diameter = engine_config["nozzle"]["throat_diameter"] / 1000  # m
        self.exit_diameter = engine_config["nozzle"]["exit_diameter"] / 1000  # m
        self.throat_area = math.pi * (self.throat_diameter/2)**2
        self.exit_area = math.pi * (self.exit_diameter/2)**2
        self.expansion_ratio = self.exit_area / self.throat_area
        
        # Initialize results containers
        self.flow_properties = {}
        self.trajectory_data = {}
        self.performance_metrics = {}
        
    def _calculate_dry_mass(self):
        """
        Calculate the dry mass of the rocket based on geometry and materials.
        
        Returns:
            Dry mass in kg
        """
        # In a more detailed model, this would calculate mass from all components
        # For this example, we'll use a simple approximation
        stage_1_mass = 200  # kg
        stage_2_mass = 100  # kg
        payload_mass = 50   # kg
        structure_mass = 150  # kg
        
        return stage_1_mass + stage_2_mass + payload_mass + structure_mass
        
    def analyze_flow_properties(self):
        """
        Analyze flow properties throughout the propulsion system.
        Calculates pressure, temperature, velocity, Mach number, etc. at key locations.
        
        Returns:
            Dictionary of flow properties at different locations
        """
        # Initialize flow properties dictionary
        flow = {}
        
        # Chamber properties
        flow["chamber"] = {
            "pressure": self.chamber_pressure,  # Pa
            "temperature": self.chamber_temperature,  # K
            "velocity": 0  # m/s (approximately zero in chamber)
        }
        
        # Calculate critical (throat) properties
        # For isentropic flow: p_t/p_0 = (2/(gamma+1))^(gamma/(gamma-1))
        gamma = self.gamma_steam
        p_ratio_throat = (2/(gamma+1))**(gamma/(gamma-1))
        t_ratio_throat = 2/(gamma+1)
        
        flow["throat"] = {
            "pressure": self.chamber_pressure * p_ratio_throat,
            "temperature": self.chamber_temperature * t_ratio_throat,
            "mach": 1.0  # By definition, M=1 at throat
        }
        
        # Calculate sonic velocity at throat
        a_throat = math.sqrt(gamma * self.R_steam * flow["throat"]["temperature"])
        flow["throat"]["velocity"] = a_throat
        
        # Calculate mass flow rate (constant throughout nozzle)
        # ṁ = (p_0 * A_t) / sqrt(T_0) * sqrt(gamma/R) * (gamma+1)/2)^(-(gamma+1)/(2*(gamma-1)))
        constant_term = math.sqrt(gamma/self.R_steam) * ((gamma+1)/2)**(-((gamma+1)/(2*(gamma-1))))
        mass_flow_rate = (self.chamber_pressure * self.throat_area) / math.sqrt(self.chamber_temperature) * constant_term
        flow["mass_flow_rate"] = mass_flow_rate  # kg/s
        
        # Calculate exit conditions (assuming optimal expansion)
        # p_e/p_0 = (1 + (gamma-1)/2 * M_e^2)^(-gamma/(gamma-1))
        # Need to iterate to find M_e based on expansion ratio
        
        # Estimate exit Mach number using approximation formula
        # (Only valid for moderate expansion ratios)
        M_exit_approx = math.sqrt(2/(gamma-1) * ((self.expansion_ratio)**((gamma-1)/gamma) - 1))
        
        # More accurate calculation would use numerical methods to solve
        # A_e/A_t = (1/M_e) * ((1+(gamma-1)/2 * M_e^2)/((gamma+1)/2))^((gamma+1)/(2*(gamma-1)))
        
        # Calculate exit properties
        p_ratio_exit = (1 + (gamma-1)/2 * M_exit_approx**2)**(-gamma/(gamma-1))
        t_ratio_exit = (1 + (gamma-1)/2 * M_exit_approx**2)**(-1)
        
        flow["exit"] = {
            "pressure": self.chamber_pressure * p_ratio_exit,
            "temperature": self.chamber_temperature * t_ratio_exit,
            "mach": M_exit_approx
        }
        
        # Calculate exit velocity
        a_exit = math.sqrt(gamma * self.R_steam * flow["exit"]["temperature"])
        flow["exit"]["velocity"] = a_exit * M_exit_approx
        
        # Store results
        self.flow_properties = flow
        
        # Calculate thrust and specific impulse
        p_ambient = self.p0  # Pa, ambient pressure at sea level
        
        # F = ṁ * v_e + (p_e - p_a) * A_e
        thrust = mass_flow_rate * flow["exit"]["velocity"] + (flow["exit"]["pressure"] - p_ambient) * self.exit_area
        
        # Specific impulse = thrust / (mass flow rate * g0)
        isp = thrust / (mass_flow_rate * self.g0)
        
        # Store performance metrics
        self.performance_metrics["thrust"] = thrust  # N
        self.performance_metrics["specific_impulse"] = isp  # s
        self.performance_metrics["exhaust_velocity"] = flow["exit"]["velocity"]  # m/s
        
        return flow

    def analyze_trajectory(self, initial_altitude=0, initial_velocity=0, max_time=500):
        """
        Simulate the rocket trajectory to calculate maximum altitude and performance.
        
        Args:
            initial_altitude: Initial altitude in meters
            initial_velocity: Initial velocity in m/s
            max_time: Maximum simulation time in seconds
            
        Returns:
            Dictionary containing trajectory data
        """
        # Rocket parameters
        wet_mass = self.total_mass  # kg
        dry_mass = self.dry_mass  # kg
        propellant_mass = self.propellant_mass  # kg
        burn_time = self.burn_time  # s
        
        # Thrust as a function of time (could be variable, using constant for simplicity)
        def thrust_function(t):
            if t <= burn_time:
                return self.performance_metrics["thrust"]
            else:
                return 0.0
        
        # Mass as a function of time (linear mass decrease during burn)
        def mass_function(t):
            if t <= burn_time:
                return wet_mass - (propellant_mass / burn_time) * t
            else:
                return dry_mass
        
        # Atmospheric properties as a function of altitude
        def atmospheric_properties(altitude):
            # Using simplified exponential atmosphere model
            # For more accuracy, would use a standard atmosphere model
            if altitude < 0:
                return self.p0, self.rho0, self.T0
            
            # Scale heights
            h_p = 7500  # m, pressure scale height
            h_rho = 7000  # m, density scale height
            
            pressure = self.p0 * math.exp(-altitude / h_p)
            density = self.rho0 * math.exp(-altitude / h_rho)
            temperature = pressure / (density * self.R_air)
            
            return pressure, density, temperature
        
        # Calculate drag coefficient as a function of Mach number (simplified)
        def drag_coefficient(mach):
            # Simplified model, would be more complex in real analysis
            if mach < 0.8:
                return 0.2  # Subsonic
            elif mach < 1.2:
                return 0.2 + 0.4 * (mach - 0.8) / 0.4  # Transonic
            else:
                return 0.6 - 0.1 * min(mach - 1.2, 3) / 3  # Supersonic
        
        # Calculate drag force
        def drag_force(altitude, velocity):
            # Get atmospheric properties
            _, density, temperature = atmospheric_properties(altitude)
            
            # Calculate Mach number
            speed_of_sound = math.sqrt(1.4 * self.R_air * temperature)
            mach = abs(velocity) / speed_of_sound if speed_of_sound > 0 else 0
            
            # Reference area (cross-sectional area of the rocket)
            diameter = self.rocket_config["max_diameter"] / 1000  # m
            reference_area = math.pi * (diameter / 2) ** 2
            
            # Calculate drag coefficient
            cd = drag_coefficient(mach)
            
            # Calculate drag force: F_d = 0.5 * rho * v^2 * Cd * A
            drag = 0.5 * density * velocity ** 2 * cd * reference_area
            
            # Return drag force in the opposite direction of velocity
            return -math.copysign(drag, velocity)
        
        # Differential equations for the rocket's motion
        def dynamics(t, y):
            # y = [altitude, velocity]
            altitude, velocity = y
            
            # Current mass and thrust
            mass = mass_function(t)
            thrust = thrust_function(t)
            
            # Gravitational acceleration (decreases with altitude)
            r_earth = 6371000  # m, Earth radius
            gravity = self.g0 * (r_earth / (r_earth + altitude)) ** 2
            
            # Calculate drag
            drag = drag_force(altitude, velocity)
            
            # Acceleration
            acceleration = (thrust + drag) / mass - gravity
            
            return [velocity, acceleration]
        
        # Initial conditions
        y0 = [initial_altitude, initial_velocity]
        
        # Time span for the simulation
        t_span = (0, max_time)
        
        # Event function to detect apogee (maximum altitude)
        def apogee_event(t, y):
            return y[1]  # velocity = 0 at apogee
        
        apogee_event.terminal = False  # Don't terminate the simulation at apogee
        apogee_event.direction = -1  # Only detect when velocity changes from positive to negative
        
        # Solve the differential equations
        solution = solve_ivp(
            dynamics, 
            t_span, 
            y0, 
            method='RK45', 
            events=apogee_event,
            max_step=1.0
        )
        
        # Extract results
        time = solution.t
        altitude = solution.y[0]
        velocity = solution.y[1]
        
        # Calculate acceleration, mach number, dynamic pressure, etc.
        acceleration = np.zeros_like(time)
        mach = np.zeros_like(time)
        dynamic_pressure = np.zeros_like(time)
        thrust = np.zeros_like(time)
        mass = np.zeros_like(time)
        drag = np.zeros_like(time)
        
        for i, t in enumerate(time):
            # Current mass and thrust
            mass[i] = mass_function(t)
            thrust[i] = thrust_function(t)
            
            # Calculate drag
            drag[i] = drag_force(altitude[i], velocity[i])
            
            # Gravitational acceleration
            r_earth = 6371000  # m
            gravity = self.g0 * (r_earth / (r_earth + altitude[i])) ** 2
            
            # Calculate acceleration
            acceleration[i] = (thrust[i] + drag[i]) / mass[i] - gravity
            
            # Get atmospheric properties
            _, density, temperature = atmospheric_properties(altitude[i])
            
            # Calculate Mach number
            speed_of_sound = math.sqrt(1.4 * self.R_air * temperature)
            mach[i] = abs(velocity[i]) / speed_of_sound if speed_of_sound > 0 else 0
            
            # Calculate dynamic pressure: q = 0.5 * rho * v^2
            dynamic_pressure[i] = 0.5 * density * velocity[i] ** 2
        
        # Find apogee (maximum altitude)
        max_altitude_idx = np.argmax(altitude)
        apogee = altitude[max_altitude_idx]
        apogee_time = time[max_altitude_idx]
        
        # Find maximum velocity
        max_velocity_idx = np.argmax(np.abs(velocity))
        max_velocity = velocity[max_velocity_idx]
        max_velocity_time = time[max_velocity_idx]
        
        # Find maximum acceleration
        max_accel_idx = np.argmax(np.abs(acceleration))
        max_acceleration = acceleration[max_accel_idx]
        max_accel_time = time[max_accel_idx]
        
        # Find maximum dynamic pressure (Max Q)
        max_q_idx = np.argmax(dynamic_pressure)
        max_q = dynamic_pressure[max_q_idx]
        max_q_time = time[max_q_idx]
        
        # Store trajectory data
        trajectory = {
            "time": time,
            "altitude": altitude,
            "velocity": velocity,
            "acceleration": acceleration,
            "mach": mach,
            "dynamic_pressure": dynamic_pressure,
            "thrust": thrust,
            "mass": mass,
            "drag": drag,
            "apogee": apogee,
            "apogee_time": apogee_time,
            "max_velocity": max_velocity,
            "max_velocity_time": max_velocity_time,
            "max_acceleration": max_acceleration,
            "max_acceleration_time": max_accel_time,
            "max_q": max_q,
            "max_q_time": max_q_time
        }
        
        self.trajectory_data = trajectory
        
        return trajectory

    def calculate_maximum_payload(self, target_altitude=None, altitude_range=None):
        """
        Calculate the maximum payload the rocket can carry to a given altitude.
        
        Args:
            target_altitude: Target altitude in meters, or None for apogee
            altitude_range: Acceptable range around target altitude (e.g., ±5%)
            
        Returns:
            Dictionary with maximum payload and related data
        """
        # Start with current payload estimate
        current_payload = 50  # kg
        original_dry_mass = self.dry_mass
        
        # Define step sizes for binary search
        step = 25  # kg
        min_step = 0.1  # kg
        
        # Initial altitude with current payload
        self.dry_mass = original_dry_mass  # Reset to original mass
        trajectory = self.analyze_trajectory()
        current_altitude = trajectory["apogee"]
        
        # If no target altitude is specified, we'll just maximize payload
        # while ensuring the rocket can still reach some minimum altitude
        if target_altitude is None:
            min_acceptable_altitude = 1000  # m, arbitrary minimum altitude
            target_altitude = min_acceptable_altitude
            maximize_payload = True
        else:
            maximize_payload = False
        
        # Set tolerance if altitude_range is not specified
        if altitude_range is None:
            altitude_range = target_altitude * 0.05  # 5% of target altitude
        
        # Binary search for maximum payload
        while step >= min_step:
            # Increase payload
            test_payload = current_payload + step
            self.dry_mass = original_dry_mass - current_payload + test_payload
            
            # Analyze trajectory with new payload
            trajectory = self.analyze_trajectory()
            test_altitude = trajectory["apogee"]
            
            # Check if payload change is acceptable
            if maximize_payload:
                if test_altitude >= target_altitude:
                    # Can increase payload
                    current_payload = test_payload
                    current_altitude = test_altitude
                else:
                    # Too heavy, reduce step size
                    step /= 2
            else:
                # Trying to hit a specific target altitude
                if abs(test_altitude - target_altitude) <= altitude_range:
                    # Within acceptable range
                    current_payload = test_payload
                    current_altitude = test_altitude
                    break
                elif test_altitude > target_altitude:
                    # Too light, add more payload
                    current_payload = test_payload
                    current_altitude = test_altitude
                else:
                    # Too heavy, reduce step size
                    step /= 2
        
        # Reset dry mass to original value
        self.dry_mass = original_dry_mass
        
        # Return maximum payload information
        payload_info = {
            "max_payload": current_payload,
            "altitude_with_max_payload": current_altitude,
            "target_altitude": target_altitude,
            "altitude_difference": current_altitude - target_altitude
        }
        
        return payload_info
    
    def generate_performance_graphs(self, output_dir):
        """
        Generate comprehensive performance graphs for flow rates, pressures, velocities, 
        and trajectory analysis.
        
        Args:
            output_dir: Directory to save generated graphs
            
        Returns:
            List of generated graph filenames
        """
        os.makedirs(output_dir, exist_ok=True)
        generated_files = []
        
        # 1. Flow Property Analysis
        if self.flow_properties:
            f1 = self._generate_flow_property_graphs(output_dir)
            generated_files.extend(f1)
        
        # 2. Trajectory Analysis
        if self.trajectory_data:
            f2 = self._generate_trajectory_graphs(output_dir)
            generated_files.extend(f2)
        
        # 3. Pressure Ratio Analysis
        f3 = self._generate_pressure_ratio_graphs(output_dir)
        generated_files.extend(f3)
        
        # 4. Engine Performance Analysis
        f4 = self._generate_engine_performance_graphs(output_dir)
        generated_files.extend(f4)
        
        # 5. Combined Performance Dashboard
        dashboard_file = self._generate_performance_dashboard(output_dir)
        generated_files.append(dashboard_file)
        
        return generated_files
        
    def _generate_flow_property_graphs(self, output_dir):
        """Generate detailed graphs of flow properties."""
        generated_files = []
        
        # Create a pressure profile along the engine
        # First, create more data points along the nozzle for smoother curve
        locations = np.linspace(0, 1, 100)  # Normalized distance along nozzle
        
        # Nozzle geometry (simplified)
        chamber_diameter = 2 * self.throat_diameter  # m
        diameters = []
        pressures = []
        velocities = []
        mach_numbers = []
        densities = []
        temperatures = []
        
        gamma = self.gamma_steam
        p0 = self.chamber_pressure
        T0 = self.chamber_temperature
        
        for x in locations:
            # Geometry: simple parabolic nozzle profile
            if x < 0.2:  # Chamber
                diameter = chamber_diameter
            elif x < 0.3:  # Convergent section
                # Linear transition to throat
                diameter = chamber_diameter - (chamber_diameter - self.throat_diameter) * (x - 0.2) / 0.1
            elif x < 0.35:  # Throat region
                diameter = self.throat_diameter
            else:  # Divergent section
                # Linear transition to exit
                diameter = self.throat_diameter + (self.exit_diameter - self.throat_diameter) * (x - 0.35) / 0.65
            
            diameters.append(diameter)
            
            # Calculate area ratio
            area = math.pi * (diameter/2)**2
            area_ratio = area / (math.pi * (self.throat_diameter/2)**2)
            
            # Approximate Mach number based on area ratio
            # This is an implicit relation, using approximate solution
            if area_ratio < 1.0:  # Subsonic
                # For convergent section, use subsonic relations
                # M = sqrt((2/(gamma-1))*((A_t/A)^((gamma-1)/gamma)*(1+(gamma-1)/2)^((gamma+1)/(gamma-1)) - 1))
                mach = 0
                try:
                    term = (1/area_ratio)**((gamma-1)/gamma) * ((gamma+1)/2)**((gamma+1)/(gamma-1))
                    if term > 1:
                        mach = math.sqrt((2/(gamma-1)) * (term - 1))
                except:
                    mach = 0.1  # Fallback for numerical issues
            else:  # Supersonic
                # For divergent section, use supersonic relations
                # Using Newton-Raphson to solve for Mach number
                # This is a simplified implementation
                mach = 2.0  # Initial guess
                for _ in range(10):  # Max iterations
                    f = lambda M: area_ratio - (1/M) * ((2+(gamma-1)*M*M)/(gamma+1))**((gamma+1)/(2*(gamma-1)))
                    df = lambda M: -((2+(gamma-1)*M*M)/(gamma+1))**((gamma+1)/(2*(gamma-1))) * (1/M**2) + \
                          (1/M) * ((gamma+1)/(2*(gamma-1))) * ((2+(gamma-1)*M*M)/(gamma+1))**(((gamma+1)/(2*(gamma-1)))-1) * \
                          (2*(gamma-1))/(gamma+1)
                    
                    if df(mach) != 0:
                        mach = mach - f(mach) / df(mach)
            
            # Calculate pressure, temperature
            if mach >= 0:
                pressure = p0 / ((1 + (gamma-1)/2 * mach**2)**(gamma/(gamma-1)))
                temperature = T0 / (1 + (gamma-1)/2 * mach**2)
                
                # Calculate velocity
                a = math.sqrt(gamma * self.R_steam * temperature)  # Speed of sound
                velocity = mach * a
                
                # Calculate density
                density = pressure / (self.R_steam * temperature)
            else:
                # Fallback values
                pressure = p0
                temperature = T0
                velocity = 0
                density = p0 / (self.R_steam * T0)
            
            pressures.append(pressure)
            velocities.append(velocity)
            mach_numbers.append(mach)
            densities.append(density)
            temperatures.append(temperature)
        
        # Create a nozzle profile figure
        fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(10, 15))
        
        # 1. Nozzle geometry and pressure
        ax1b = ax1.twinx()
        
        # Nozzle outline (top half)
        upper_wall = [(x, d/2) for x, d in zip(locations, diameters)]
        # Nozzle outline (bottom half)
        lower_wall = [(x, -d/2) for x, d in zip(locations, diameters)]
        
        x_top, y_top = zip(*upper_wall)
        x_bottom, y_bottom = zip(*lower_wall)
        
        ax1.fill_between(x_top, y_top, y_bottom, color='lightgray', alpha=0.5)
        ax1.plot(x_top, y_top, 'k-', linewidth=2)
        ax1.plot(x_bottom, y_bottom, 'k-', linewidth=2)
        ax1.set_ylabel('Nozzle Radius (m)')
        ax1.set_title('Nozzle Geometry and Pressure Profile')
        
        # Pressure
        ax1b.plot(locations, np.array(pressures)/1e6, 'r-', linewidth=2)
        ax1b.set_ylabel('Pressure (MPa)')
        
        # 2. Velocity and Mach number
        ax2.plot(locations, velocities, 'b-', linewidth=2)
        ax2.set_ylabel('Velocity (m/s)')
        
        ax2b = ax2.twinx()
        ax2b.plot(locations, mach_numbers, 'g--', linewidth=2)
        ax2b.set_ylabel('Mach Number')
        ax2.set_title('Velocity and Mach Number Profile')
        
        # 3. Temperature and density
        ax3.plot(locations, temperatures, 'r-', linewidth=2)
        ax3.set_ylabel('Temperature (K)')
        ax3.set_xlabel('Normalized Distance Along Nozzle')
        
        ax3b = ax3.twinx()
        ax3b.plot(locations, np.array(densities), 'b--', linewidth=2)
        ax3b.set_ylabel('Density (kg/m³)')
        ax3.set_title('Temperature and Density Profile')
        
        plt.tight_layout()
        
        # Save figure
        nozzle_file = os.path.join(output_dir, 'nozzle_flow_analysis.png')
        plt.savefig(nozzle_file, dpi=300, bbox_inches='tight')
        plt.close(fig)
        
        generated_files.append(nozzle_file)
        
        return generated_files

    def _generate_trajectory_graphs(self, output_dir):
        """Generate trajectory analysis graphs."""
        generated_files = []
        
        if not self.trajectory_data:
            return generated_files
        
        # Extract trajectory data
        time = self.trajectory_data["time"]
        altitude = self.trajectory_data["altitude"]
        velocity = self.trajectory_data["velocity"]
        acceleration = self.trajectory_data["acceleration"]
        mach = self.trajectory_data["mach"]
        q = self.trajectory_data["dynamic_pressure"]
        mass = self.trajectory_data["mass"]
        
        # Figure 1: Altitude, velocity, acceleration
        fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(10, 15))
        
        # Altitude
        ax1.plot(time, altitude/1000, 'b-', linewidth=2)
        ax1.set_ylabel('Altitude (km)')
        ax1.set_title('Rocket Trajectory - Altitude')
        ax1.grid(True)
        
        # Mark important points
        apogee = self.trajectory_data["apogee"]
        apogee_time = self.trajectory_data["apogee_time"]
        ax1.plot(apogee_time, apogee/1000, 'ro', markersize=8)
        ax1.annotate(f'Apogee: {apogee/1000:.2f} km', 
                     xy=(apogee_time, apogee/1000),
                     xytext=(apogee_time + 5, apogee/1000 * 0.9),
                     arrowprops=dict(facecolor='black', shrink=0.05, width=1.5))
        
        # Velocity
        ax2.plot(time, velocity, 'g-', linewidth=2)
        ax2.set_ylabel('Velocity (m/s)')
        ax2.set_title('Rocket Trajectory - Velocity')
        ax2.grid(True)
        
        # Mark maximum velocity
        max_vel = self.trajectory_data["max_velocity"]
        max_vel_time = self.trajectory_data["max_velocity_time"]
        ax2.plot(max_vel_time, max_vel, 'ro', markersize=8)
        ax2.annotate(f'Max Velocity: {max_vel:.2f} m/s', 
                     xy=(max_vel_time, max_vel),
                     xytext=(max_vel_time + 5, max_vel * 0.9),
                     arrowprops=dict(facecolor='black', shrink=0.05, width=1.5))
        
        # Acceleration
        ax3.plot(time, acceleration, 'r-', linewidth=2)
        ax3.set_ylabel('Acceleration (m/s²)')
        ax3.set_xlabel('Time (s)')
        ax3.set_title('Rocket Trajectory - Acceleration')
        ax3.grid(True)
        
        # Mark maximum acceleration
        max_acc = self.trajectory_data["max_acceleration"]
        max_acc_time = self.trajectory_data["max_acceleration_time"]
        ax3.plot(max_acc_time, max_acc, 'ro', markersize=8)
        ax3.annotate(f'Max Accel: {max_acc:.2f} m/s²', 
                     xy=(max_acc_time, max_acc),
                     xytext=(max_acc_time + 5, max_acc * 0.9),
                     arrowprops=dict(facecolor='black', shrink=0.05, width=1.5))
        
        plt.tight_layout()
        
        # Save figure
        trajectory_file = os.path.join(output_dir, 'trajectory_analysis.png')
        plt.savefig(trajectory_file, dpi=300, bbox_inches='tight')
        plt.close(fig)
        
        generated_files.append(trajectory_file)
        
        # Figure 2: Mach number, dynamic pressure, mass
        fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(10, 15))
        
        # Mach number
        ax1.plot(time, mach, 'b-', linewidth=2)
        ax1.set_ylabel('Mach Number')
        ax1.set_title('Rocket Trajectory - Mach Number')
        ax1.grid(True)
        
        # Draw Mach 1 line
        ax1.axhline(y=1, color='r', linestyle='--', alpha=0.7)
        ax1.annotate('Mach 1', xy=(time[-1]*0.95, 1.05), color='r')
        
        # Dynamic pressure
        ax2.plot(time, q/1000, 'g-', linewidth=2)  # kPa
        ax2.set_ylabel('Dynamic Pressure (kPa)')
        ax2.set_title('Rocket Trajectory - Dynamic Pressure')
        ax2.grid(True)
        
        # Mark max Q
        max_q = self.trajectory_data["max_q"]
        max_q_time = self.trajectory_data["max_q_time"]
        ax2.plot(max_q_time, max_q/1000, 'ro', markersize=8)
        ax2.annotate(f'Max Q: {max_q/1000:.2f} kPa', 
                     xy=(max_q_time, max_q/1000),
                     xytext=(max_q_time + 5, max_q/1000 * 0.9),
                     arrowprops=dict(facecolor='black', shrink=0.05, width=1.5))
        
        # Mass
        ax3.plot(time, mass, 'r-', linewidth=2)
        ax3.set_ylabel('Mass (kg)')
        ax3.set_xlabel('Time (s)')
        ax3.set_title('Rocket Trajectory - Mass')
        ax3.grid(True)
        
        # Mark the burn time
        if self.burn_time <= max(time):
            ax3.axvline(x=self.burn_time, color='g', linestyle='--', alpha=0.7)
            ax3.annotate('Burnout', 
                         xy=(self.burn_time, min(mass) + (max(mass) - min(mass))*0.5),
                         xytext=(self.burn_time + 5, min(mass) + (max(mass) - min(mass))*0.5),
                         arrowprops=dict(facecolor='black', shrink=0.05, width=1.5))
        
        plt.tight_layout()
        
        # Save figure
        trajectory_file2 = os.path.join(output_dir, 'trajectory_analysis_2.png')
        plt.savefig(trajectory_file2, dpi=300, bbox_inches='tight')
        plt.close(fig)
        
        generated_files.append(trajectory_file2)
        
        return generated_files
    
    def _generate_pressure_ratio_graphs(self, output_dir):
        """Generate pressure ratio analysis graphs."""
        generated_files = []
        
        # Create expansion ratio vs pressure ratio graph
        # This shows how the nozzle expansion ratio affects the pressure ratio
        # and how this relates to different altitudes
        
        fig, ax = plt.subplots(figsize=(10, 8))
        
        # Range of expansion ratios to explore
        expansion_ratios = np.linspace(1, 30, 100)
        
        # Optimal expansion ratio for different altitudes
        altitudes = [0, 5000, 10000, 15000, 20000, 30000]  # meters
        altitude_labels = ['Sea Level', '5 km', '10 km', '15 km', '20 km', '30 km']
        
        # Calculate pressure ratio for each expansion ratio
        gamma = self.gamma_steam
        
        # Function to calculate exit pressure ratio from expansion ratio
        def pressure_ratio(expansion_ratio, gamma=1.3):
            # p_e/p_0 = (1/ER)^gamma
            # This is a simplified approximation
            return (1 / expansion_ratio) ** gamma
        
        # Ideal pressure ratio curve (perfect expansion)
        pr_ideal = np.array([pressure_ratio(er) for er in expansion_ratios])
        
        # Plot the ideal curve
        ax.plot(expansion_ratios, pr_ideal, 'k-', linewidth=2, label='Ideal Pressure Ratio')
        
        # Calculate atmospheric pressure at different altitudes
        def pressure_at_altitude(altitude):
            # Using simplified exponential model
            h_p = 7500  # m, pressure scale height
            return self.p0 * math.exp(-altitude / h_p)
        
        # For each altitude, plot the ambient pressure ratio
        colors = ['r', 'g', 'b', 'c', 'm', 'y']
        for i, altitude in enumerate(altitudes):
            p_ambient = pressure_at_altitude(altitude)
            p_ratio = p_ambient / self.chamber_pressure
            
            # Plot horizontal line for this altitude
            ax.axhline(y=p_ratio, color=colors[i], linestyle='--', alpha=0.7,
                       label=f'{altitude_labels[i]} (P_ratio = {p_ratio:.6f})')
            
            # Find optimal expansion ratio for this altitude
            optimal_er = 1/p_ratio**(1/gamma)  # Simplified approximation
            
            # Mark the intersection of altitude line with ideal curve
            ax.plot(optimal_er, p_ratio, 'o', color=colors[i], markersize=8)
            ax.annotate(f'ER = {optimal_er:.1f}',
                        xy=(optimal_er, p_ratio),
                        xytext=(optimal_er + 1, p_ratio * 1.5),
                        arrowprops=dict(facecolor=colors[i], shrink=0.05, width=1))
            
        # Add current rocket expansion ratio
        current_er = self.expansion_ratio
        current_pr = pressure_ratio(current_er)
        ax.plot(current_er, current_pr, 'ko', markersize=10, label=f'Current Design (ER = {current_er:.2f})')
        
        # Set logarithmic scale for y-axis (pressure ratios can be very small)
        ax.set_yscale('log')
        
        # Labels and title
        ax.set_xlabel('Expansion Ratio (Exit Area / Throat Area)')
        ax.set_ylabel('Pressure Ratio (P_exit / P_chamber)')
        ax.set_title('Nozzle Expansion Ratio Analysis')
        
        # Add grid and legend
        ax.grid(True, which='both', linestyle='--', alpha=0.7)
        ax.legend(loc='best')
        
        # Save figure
        pressure_ratio_file = os.path.join(output_dir, 'pressure_ratio_analysis.png')
        plt.savefig(pressure_ratio_file, dpi=300, bbox_inches='tight')
        plt.close(fig)
        
        generated_files.append(pressure_ratio_file)
        
        return generated_files

    def _generate_engine_performance_graphs(self, output_dir):
        """Generate engine performance analysis graphs."""
        generated_files = []
        
        # Create a performance map showing how thrust and ISP vary with key parameters
        
        # 1. Thrust vs Chamber Pressure
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 12))
        
        # Range of chamber pressures to explore (MPa)
        pressures = np.linspace(1, 10, 20)  # 1-10 MPa
        thrusts = []
        isps = []
        
        # Calculate thrust and ISP for each pressure
        orig_pressure = self.chamber_pressure
        for p in pressures:
            # Temporarily set new pressure
            self.chamber_pressure = p * 1e6  # Convert to Pa
            
            # Recalculate flow properties
            self.analyze_flow_properties()
            
            # Store results
            thrusts.append(self.performance_metrics["thrust"])
            isps.append(self.performance_metrics["specific_impulse"])
        
        # Restore original pressure
        self.chamber_pressure = orig_pressure
        self.analyze_flow_properties()
        
        # Plot thrust vs pressure
        ax1.plot(pressures, thrusts, 'b-', linewidth=2)
        ax1.set_xlabel('Chamber Pressure (MPa)')
        ax1.set_ylabel('Thrust (N)')
        ax1.set_title('Thrust vs Chamber Pressure')
        ax1.grid(True)
        
        # Mark the current design point
        current_pressure = self.chamber_pressure / 1e6  # Convert to MPa
        current_thrust = self.performance_metrics["thrust"]
        ax1.plot(current_pressure, current_thrust, 'ro', markersize=8)
        ax1.annotate(f'Current Design: {current_thrust:.1f} N @ {current_pressure:.1f} MPa',
                    xy=(current_pressure, current_thrust),
                    xytext=(current_pressure * 0.8, current_thrust * 0.9),
                    arrowprops=dict(facecolor='black', shrink=0.05, width=1.5))
        
        # Plot ISP vs pressure
        ax2.plot(pressures, isps, 'g-', linewidth=2)
        ax2.set_xlabel('Chamber Pressure (MPa)')
        ax2.set_ylabel('Specific Impulse (s)')
        ax2.set_title('Specific Impulse vs Chamber Pressure')
        ax2.grid(True)
        
        # Mark the current design point
        current_isp = self.performance_metrics["specific_impulse"]
        ax2.plot(current_pressure, current_isp, 'ro', markersize=8)
        ax2.annotate(f'Current Design: {current_isp:.1f} s @ {current_pressure:.1f} MPa',
                    xy=(current_pressure, current_isp),
                    xytext=(current_pressure * 0.8, current_isp * 0.9),
                    arrowprops=dict(facecolor='black', shrink=0.05, width=1.5))
        
        plt.tight_layout()
        
        # Save figure
        engine_perf_file = os.path.join(output_dir, 'engine_performance_pressure.png')
        plt.savefig(engine_perf_file, dpi=300, bbox_inches='tight')
        plt.close(fig)
        
        generated_files.append(engine_perf_file)
        
        # 2. Performance vs Expansion Ratio
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 12))
        
        # Range of expansion ratios to explore
        exp_ratios = np.linspace(2, 20, 20)
        er_thrusts = []
        er_isps = []
        
        # Calculate thrust and ISP for each expansion ratio
        orig_exit_area = self.exit_area
        orig_expansion_ratio = self.expansion_ratio
        
        for er in exp_ratios:
            # Calculate new exit area
            new_exit_area = self.throat_area * er
            
            # Temporarily set new exit area and expansion ratio
            self.exit_area = new_exit_area
            self.expansion_ratio = er
            
            # Recalculate flow properties
            self.analyze_flow_properties()
            
            # Store results
            er_thrusts.append(self.performance_metrics["thrust"])
            er_isps.append(self.performance_metrics["specific_impulse"])
        
        # Restore original values
        self.exit_area = orig_exit_area
        self.expansion_ratio = orig_expansion_ratio
        self.analyze_flow_properties()
        
        # Plot thrust vs expansion ratio
        ax1.plot(exp_ratios, er_thrusts, 'b-', linewidth=2)
        ax1.set_xlabel('Expansion Ratio')
        ax1.set_ylabel('Thrust (N)')
        ax1.set_title('Thrust vs Expansion Ratio')
        ax1.grid(True)
        
        # Mark the current design point
        ax1.plot(orig_expansion_ratio, current_thrust, 'ro', markersize=8)
        ax1.annotate(f'Current Design: {current_thrust:.1f} N @ ER={orig_expansion_ratio:.1f}',
                    xy=(orig_expansion_ratio, current_thrust),
                    xytext=(orig_expansion_ratio * 0.8, current_thrust * 0.9),
                    arrowprops=dict(facecolor='black', shrink=0.05, width=1.5))
        
        # Plot ISP vs expansion ratio
        ax2.plot(exp_ratios, er_isps, 'g-', linewidth=2)
        ax2.set_xlabel('Expansion Ratio')
        ax2.set_ylabel('Specific Impulse (s)')
        ax2.set_title('Specific Impulse vs Expansion Ratio')
        ax2.grid(True)
        
        # Mark the current design point
        ax2.plot(orig_expansion_ratio, current_isp, 'ro', markersize=8)
        ax2.annotate(f'Current Design: {current_isp:.1f} s @ ER={orig_expansion_ratio:.1f}',
                    xy=(orig_expansion_ratio, current_isp),
                    xytext=(orig_expansion_ratio * 0.8, current_isp * 0.9),
                    arrowprops=dict(facecolor='black', shrink=0.05, width=1.5))
        
        plt.tight_layout()
        
        # Save figure
        engine_perf_file2 = os.path.join(output_dir, 'engine_performance_expansion.png')
        plt.savefig(engine_perf_file2, dpi=300, bbox_inches='tight')
        plt.close(fig)
        
        generated_files.append(engine_perf_file2)
        
        return generated_files
    
    def _generate_performance_dashboard(self, output_dir):
        """Generate a comprehensive performance dashboard with key metrics."""
        # Create a dashboard summary figure
        fig = plt.figure(figsize=(12, 15))
        
        # Use GridSpec for complex layout
        gs = gridspec.GridSpec(4, 2, figure=fig)
        
        # 1. Title and Key Metrics
        ax_title = fig.add_subplot(gs[0, :])
        ax_title.axis('off')  # No axes for title
        
        # Create title and key metrics text
        title_text = "TWO-STAGE STEAM ROCKET PERFORMANCE DASHBOARD"
        
        # Collect key metrics
        if hasattr(self, 'performance_metrics') and self.performance_metrics:
            thrust = self.performance_metrics.get("thrust", 0)
            isp = self.performance_metrics.get("specific_impulse", 0)
        else:
            thrust = 0
            isp = 0
            
        if hasattr(self, 'trajectory_data') and self.trajectory_data:
            apogee = self.trajectory_data.get("apogee", 0)
            max_velocity = self.trajectory_data.get("max_velocity", 0)
            max_acceleration = self.trajectory_data.get("max_acceleration", 0)
        else:
            apogee = 0
            max_velocity = 0
            max_acceleration = 0
        
        metrics_text = (
            f"Engine: {thrust:.1f} N Thrust | {isp:.1f} s Isp | "
            f"Performance: {apogee/1000:.1f} km Altitude | {max_velocity:.1f} m/s Max Velocity | "
            f"{max_acceleration:.1f} m/s² Max Acceleration"
        )
        
        # Add title and metrics to plot
        ax_title.text(0.5, 0.7, title_text, fontsize=16, weight='bold', ha='center')
        ax_title.text(0.5, 0.3, metrics_text, fontsize=12, ha='center')
        
        # 2. Rocket Diagram (simplified)
        ax_diagram = fig.add_subplot(gs[1:3, 0])
        self._draw_rocket_diagram(ax_diagram)
        
        # 3. Altitude Profile
        ax_altitude = fig.add_subplot(gs[1, 1])
        if hasattr(self, 'trajectory_data') and self.trajectory_data:
            time = self.trajectory_data["time"]
            altitude = self.trajectory_data["altitude"]
            ax_altitude.plot(time, altitude/1000, 'b-', linewidth=2)
            ax_altitude.set_xlabel('Time (s)')
            ax_altitude.set_ylabel('Altitude (km)')
            ax_altitude.set_title('Altitude Profile')
            ax_altitude.grid(True)
        else:
            ax_altitude.text(0.5, 0.5, "No trajectory data available", ha='center', va='center')
            ax_altitude.set_title('Altitude Profile')
        
        # 4. Pressure Profile
        ax_pressure = fig.add_subplot(gs[2, 1])
        # If we have flow property data, plot it
        if hasattr(self, 'flow_properties') and self.flow_properties:
            # Simplified representation of pressure along nozzle
            locations = np.linspace(0, 1, 100)  # Normalized distance
            pressures = []
            
            # Generate a simplified pressure profile
            chamber_p = self.chamber_pressure / 1e6  # MPa
            throat_p = chamber_p * 0.5  # Approximate
            exit_p = self.flow_properties.get("exit", {}).get("pressure", 0) / 1e6  # MPa
            
            for x in locations:
                if x < 0.3:  # Chamber
                    p = chamber_p
                elif x < 0.35:  # Throat
                    p = throat_p
                else:  # Divergent section - linear decay
                    p = throat_p - (throat_p - exit_p) * (x - 0.35) / 0.65
                pressures.append(p)
            
            ax_pressure.plot(locations, pressures, 'r-', linewidth=2)
            ax_pressure.set_xlabel('Normalized Distance Along Engine')
            ax_pressure.set_ylabel('Pressure (MPa)')
            ax_pressure.set_title('Pressure Profile')
            ax_pressure.grid(True)
        else:
            ax_pressure.text(0.5, 0.5, "No flow property data available", ha='center', va='center')
            ax_pressure.set_title('Pressure Profile')
        
        # 5. Performance Parameters Table
        ax_table = fig.add_subplot(gs[3, :])
        ax_table.axis('off')  # No axes for table
        
        # Create table data
        table_data = [
            ['Parameter', 'Value', 'Units', 'Notes'],
            ['Chamber Pressure', f"{self.chamber_pressure/1e6:.2f}", 'MPa', 'Design pressure'],
            ['Chamber Temperature', f"{self.chamber_temperature:.1f}", 'K', f"{self.chamber_temperature-273.15:.1f}°C"],
            ['Mass Flow Rate', f"{self.flow_properties.get('mass_flow_rate', 0):.3f}", 'kg/s', 'Propellant consumption'],
            ['Throat Diameter', f"{self.throat_diameter*1000:.1f}", 'mm', 'Critical dimension'],
            ['Exit Diameter', f"{self.exit_diameter*1000:.1f}", 'mm', 'Nozzle exit'],
            ['Expansion Ratio', f"{self.expansion_ratio:.2f}", '', 'Area ratio (exit/throat)'],
            ['Thrust', f"{thrust:.1f}", 'N', 'At sea level'],
            ['Specific Impulse', f"{isp:.1f}", 's', 'Efficiency metric'],
            ['Burn Time', f"{self.burn_time:.1f}", 's', 'Engine firing duration'],
            ['Propellant Mass', f"{self.propellant_mass:.1f}", 'kg', 'Water/steam mass'],
            ['Maximum Altitude', f"{apogee/1000:.2f}", 'km', 'Apogee'],
            ['Maximum Velocity', f"{max_velocity:.1f}", 'm/s', f"Mach {max_velocity/340:.1f}"]
        ]
        
        # Create the table
        table = ax_table.table(
            cellText=[row[1:3] for row in table_data[1:]],  # Just value and units
            rowLabels=[row[0] for row in table_data[1:]],   # Parameters as row labels
            colLabels=table_data[0][1:3],                   # Value and Units as column labels
            loc='center',
            cellLoc='center'
        )
        
        # Style the table
        table.auto_set_font_size(False)
        table.set_fontsize(10)
        table.scale(1, 1.5)  # Scale table for better readability
        
        # Add footer
        footer_text = "Generated by Two-Stage Space Vehicle Design Project"
        fig.text(0.5, 0.01, footer_text, ha='center', fontsize=10)
        
        plt.tight_layout(rect=[0, 0.02, 1, 0.98])  # Adjust layout to make room for footer
        
        # Save dashboard
        dashboard_file = os.path.join(output_dir, 'performance_dashboard.png')
        plt.savefig(dashboard_file, dpi=300, bbox_inches='tight')
        plt.close(fig)
        
        return dashboard_file
    
    def _draw_rocket_diagram(self, ax):
        """Draw a simplified diagram of the rocket on the given axes."""
        # Get rocket dimensions
        total_length = self.rocket_config["total_length"] / 1000  # m
        max_diameter = self.rocket_config["max_diameter"] / 1000  # m
        first_stage_ratio = self.rocket_config["first_stage_length_ratio"]
        nose_cone_ratio = self.rocket_config["nose_cone_length_ratio"]
        
        # Simplified rocket shape
        first_stage_length = total_length * first_stage_ratio
        second_stage_length = total_length * (1 - first_stage_ratio - nose_cone_ratio)
        nose_length = total_length * nose_cone_ratio
        
        # Center the rocket in the axes
        x_start = 0
        y_center = 0
        radius = max_diameter / 2
        
        # Draw first stage
        first_stage = plt.Rectangle((x_start, y_center - radius), 
                                   first_stage_length, 2*radius,
                                   fc='lightgray', ec='black')
        ax.add_patch(first_stage)
        
        # Draw second stage
        second_stage_radius = radius * 0.9
        second_stage = plt.Rectangle((x_start + first_stage_length, y_center - second_stage_radius),
                                    second_stage_length, 2*second_stage_radius,
                                    fc='white', ec='black')
        ax.add_patch(second_stage)
        
        # Draw nose cone
        nose_tip_x = x_start + first_stage_length + second_stage_length + nose_length
        nose_base_x = x_start + first_stage_length + second_stage_length
        nose_y_points = [y_center - second_stage_radius, y_center + second_stage_radius, y_center]
        nose_x_points = [nose_base_x, nose_base_x, nose_tip_x]
        ax.fill(nose_x_points, nose_y_points, fc='white', ec='black')
        
        # Draw fins
        fin_length = first_stage_length * 0.3
        fin_height = radius * 0.8
        fin_start_x = x_start + first_stage_length * 0.1
        
        # Bottom fin
        fin_bottom = plt.Polygon([[fin_start_x, y_center - radius],
                                 [fin_start_x + fin_length, y_center - radius],
                                 [fin_start_x, y_center - radius - fin_height]],
                                fc='darkgray', ec='black')
        ax.add_patch(fin_bottom)
        
        # Top fin
        fin_top = plt.Polygon([[fin_start_x, y_center + radius],
                              [fin_start_x + fin_length, y_center + radius],
                              [fin_start_x, y_center + radius + fin_height]],
                             fc='darkgray', ec='black')
        ax.add_patch(fin_top)
        
        # Draw engines
        engine_width = radius * 0.6
        engine_length = first_stage_length * 0.1
        engine_x = x_start - engine_length
        ax.add_patch(plt.Rectangle((engine_x, y_center - engine_width/2),
                                  engine_length, engine_width,
                                  fc='darkgray', ec='black'))
        
        # Add flame/exhaust
        flame_length = engine_length * 2
        flame_x_points = [engine_x, engine_x - flame_length, engine_x]
        flame_y_points = [y_center - engine_width/2, y_center, y_center + engine_width/2]
        ax.fill(flame_x_points, flame_y_points, fc='orangered', ec='none', alpha=0.7)
        
        # Add stage separation line
        ax.plot([x_start + first_stage_length, x_start + first_stage_length],
               [y_center - radius*1.2, y_center + radius*1.2],
               'r--', linewidth=2)
        
        # Add labels
        ax.text(x_start + first_stage_length/2, y_center, "STAGE 1", ha='center', va='center')
        ax.text(x_start + first_stage_length + second_stage_length/2, y_center, "STAGE 2", ha='center', va='center')
        ax.text(nose_base_x + nose_length/2, y_center, "PAYLOAD", ha='center', va='center')
        
        # Add steam engine label
        ax.text(engine_x, y_center - radius*1.5, "STEAM PROPULSION", ha='center', va='center', weight='bold')
        
        # Set equal aspect ratio and limits
        full_length = nose_tip_x - engine_x + flame_length
        ax.set_xlim([engine_x - flame_length*0.5, nose_tip_x + total_length*0.05])
        max_height = (radius + fin_height) * 1.5
        ax.set_ylim([y_center - max_height, y_center + max_height])
        ax.set_aspect('equal')
        
        # Set title and remove axes
        ax.set_title('Two-Stage Steam Rocket Design')
        ax.axis('off')
