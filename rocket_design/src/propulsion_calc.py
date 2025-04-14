#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Propulsion calculation module for steam-based rocket propulsion system.
This module focuses on thrust calculation, specific impulse, and propellant requirements.
"""

import math
import numpy as np
import matplotlib.pyplot as plt
import os

class SteamPropulsionAnalysis:
    """Class for analyzing steam-based rocket propulsion systems."""
    
    def __init__(self, config):
        """
        Initialize the propulsion analysis with configuration.
        
        Args:
            config: Dictionary containing propulsion parameters
        """
        self.config = config
        
        # Extract parameters
        self.propellant = config["propellant"]
        self.initial_temperature = config["initial_temperature"]  # K
        self.initial_pressure = config["initial_pressure"]  # MPa
        self.propellant_mass = config["propellant_mass"]  # kg
        self.burn_duration = config["burn_duration"]  # seconds
        
        # Physical constants
        self.g0 = 9.81  # m/s², Earth's gravitational acceleration
        
        # Properties for water/steam (will vary with temperature and pressure)
        self.steam_properties = {
            # Specific heat ratio (k) is approximately 1.3 for steam
            "k": 1.3,
            
            # Gas constant for water vapor (J/kg·K)
            "R": 461.5,
            
            # Specific heat capacity (J/kg·K) at constant pressure
            "cp": 2080,
            
            # Latent heat of vaporization at 100°C (J/kg)
            "Lv": 2257000
        }
        
        # Calculate derived values
        self.mass_flow_rate = self.propellant_mass / self.burn_duration  # kg/s
    
    def calculate_thrust(self):
        """
        Calculate the thrust produced by the steam propulsion system.
        
        Returns:
            Thrust in Newtons
        """
        # For a simple steam rocket, thrust is calculated using the rocket equation:
        # F = m_dot * ve
        # Where:
        # - m_dot is the mass flow rate (kg/s)
        # - ve is the exhaust velocity (m/s)
        
        # Calculate exhaust velocity
        exhaust_velocity = self.calculate_exhaust_velocity()
        
        # Calculate thrust
        thrust = self.mass_flow_rate * exhaust_velocity
        
        return thrust
    
    def calculate_exhaust_velocity(self):
        """
        Calculate the exhaust velocity of the steam.
        
        Returns:
            Exhaust velocity in m/s
        """
        # For an ideal rocket nozzle, the exhaust velocity is:
        # ve = sqrt(2 * k * R * T * (1 - (p_ambient/p_chamber)^((k-1)/k)) / (k-1))
        # Where:
        # - k is the specific heat ratio
        # - R is the gas constant for the propellant
        # - T is the chamber temperature
        # - p_ambient is the ambient pressure (assumed to be near vacuum in space)
        # - p_chamber is the chamber pressure
        
        k = self.steam_properties["k"]
        R = self.steam_properties["R"]
        T = self.initial_temperature
        
        # Convert chamber pressure from MPa to Pa for calculation
        p_chamber = self.initial_pressure * 1e6
        
        # Assume ambient pressure at sea level (101325 Pa)
        p_ambient = 101325
        
        # Calculate pressure ratio term
        pressure_ratio = p_ambient / p_chamber
        pressure_term = 1 - math.pow(pressure_ratio, (k-1)/k)
        
        # Calculate exhaust velocity
        exhaust_velocity = math.sqrt(2 * k * R * T * pressure_term / (k-1))
        
        return exhaust_velocity
    
    def calculate_specific_impulse(self):
        """
        Calculate the specific impulse of the propulsion system.
        
        Returns:
            Specific impulse in seconds
        """
        # Specific impulse is exhaust velocity divided by Earth's gravitational acceleration
        exhaust_velocity = self.calculate_exhaust_velocity()
        Isp = exhaust_velocity / self.g0
        
        return Isp
    
    def calculate_mass_flow_rate(self):
        """
        Calculate the mass flow rate of the propellant.
        
        Returns:
            Mass flow rate in kg/s
        """
        return self.mass_flow_rate
    
    def calculate_delta_v(self):
        """
        Calculate the delta-v (change in velocity) the rocket can achieve.
        
        Returns:
            Delta-v in m/s
        """
        # The Tsiolkovsky rocket equation:
        # Δv = ve * ln(m0/mf)
        # Where:
        # - ve is the exhaust velocity
        # - m0 is the initial mass (vehicle + propellant)
        # - mf is the final mass (vehicle without propellant)
        
        # Assume vehicle dry mass is 3 times the propellant mass
        # This is a rough approximation for initial calculations
        vehicle_dry_mass = 3 * self.propellant_mass
        initial_mass = vehicle_dry_mass + self.propellant_mass
        final_mass = vehicle_dry_mass
        
        exhaust_velocity = self.calculate_exhaust_velocity()
        delta_v = exhaust_velocity * math.log(initial_mass / final_mass)
        
        return delta_v
    
    def calculate_energy_requirements(self):
        """
        Calculate the energy required to heat the water to steam.
        
        Returns:
            Energy required in Joules
        """
        # Energy to heat water to boiling + energy to convert to steam + energy to superheat
        # Assuming water starts at room temperature (20°C)
        
        # Specific heat of water (J/kg·K)
        c_water = 4186
        
        # Room temperature (K)
        room_temp = 293.15
        
        # Boiling temperature at the given pressure
        # For simplicity, assume standard boiling point of water (100°C = 373.15K)
        # A more accurate calculation would use steam tables
        boiling_temp = 373.15
        
        # Energy to heat water to boiling
        e_heating = self.propellant_mass * c_water * (boiling_temp - room_temp)
        
        # Energy to convert to steam (latent heat)
        e_vaporization = self.propellant_mass * self.steam_properties["Lv"]
        
        # Energy to superheat the steam (if initial_temperature > boiling_temp)
        e_superheat = 0
        if self.initial_temperature > boiling_temp:
            e_superheat = self.propellant_mass * self.steam_properties["cp"] * (self.initial_temperature - boiling_temp)
        
        # Total energy
        total_energy = e_heating + e_vaporization + e_superheat
        
        return total_energy
    
    def calculate_thrust_profile(self):
        """
        Calculate the thrust profile over the burn duration.
        
        Returns:
            Dictionary with time and thrust arrays
        """
        # For a steam rocket, thrust typically decreases over time as pressure drops
        # A simple model is exponential decay
        time_points = np.linspace(0, self.burn_duration, 100)
        
        # Initial thrust
        initial_thrust = self.calculate_thrust()
        
        # Decay constant (adjust for realistic behavior)
        decay_rate = 0.5 / self.burn_duration
        
        # Calculate thrust at each time point
        thrust_profile = initial_thrust * np.exp(-decay_rate * time_points)
        
        return {
            "time": time_points,
            "thrust": thrust_profile
        }
    
    def generate_report(self, output_file):
        """
        Generate a report of the propulsion system analysis.
        
        Args:
            output_file: Path to save the report
        """
        # Calculate performance metrics
        thrust = self.calculate_thrust()
        isp = self.calculate_specific_impulse()
        delta_v = self.calculate_delta_v()
        energy = self.calculate_energy_requirements()
        exhaust_velocity = self.calculate_exhaust_velocity()
        
        # Get thrust profile
        thrust_profile = self.calculate_thrust_profile()
        
        # In a real application, this would generate a PDF
        # For this example, we'll create a text file
        with open(output_file.replace('.pdf', '.txt'), 'w') as f:
            f.write("STEAM PROPULSION SYSTEM ANALYSIS REPORT\n")
            f.write("======================================\n\n")
            
            f.write("Propulsion System Parameters:\n")
            f.write(f"- Propellant: {self.propellant}\n")
            f.write(f"- Initial Temperature: {self.initial_temperature} K ({self.initial_temperature - 273.15:.1f}°C)\n")
            f.write(f"- Initial Pressure: {self.initial_pressure} MPa\n")
            f.write(f"- Propellant Mass: {self.propellant_mass} kg\n")
            f.write(f"- Burn Duration: {self.burn_duration} seconds\n")
            f.write(f"- Mass Flow Rate: {self.mass_flow_rate:.3f} kg/s\n\n")
            
            f.write("Performance Metrics:\n")
            f.write(f"- Thrust: {thrust:.2f} N\n")
            f.write(f"- Specific Impulse: {isp:.2f} s\n")
            f.write(f"- Exhaust Velocity: {exhaust_velocity:.2f} m/s\n")
            f.write(f"- Delta-v Capability: {delta_v:.2f} m/s\n")
            f.write(f"- Energy Required: {energy/1e6:.2f} MJ\n\n")
            
            f.write("Thrust Profile:\n")
            f.write("- The thrust starts at maximum and decreases exponentially as pressure drops\n")
            f.write(f"- Initial Thrust: {thrust:.2f} N\n")
            f.write(f"- Final Thrust: {thrust_profile['thrust'][-1]:.2f} N\n\n")
            
            f.write("Efficiency Analysis:\n")
            f.write(f"- Propellant Efficiency: {isp/self.steam_properties['cp']:.3f}\n")
            f.write(f"- Energy to Thrust Conversion: {thrust/(energy/self.burn_duration):.3e} N/W\n\n")
            
            f.write("Recommendations:\n")
            if isp < 100:
                f.write("- Consider increasing operating temperature and pressure for better performance\n")
            else:
                f.write("- Current design provides reasonable performance for a steam system\n")
            f.write("- For increased delta-v, consider reducing vehicle mass or increasing propellant fraction\n\n")
            
            f.write("Notes:\n")
            f.write("- This analysis uses simplified models and assumptions\n")
            f.write("- Real-world performance may vary due to losses and non-ideal behavior\n")
            f.write("- Detailed CFD analysis is recommended for final design verification\n")
        
        # Generate a simple thrust profile plot and save it
        plt_file = os.path.splitext(output_file)[0] + '_thrust_profile.png'
        try:
            plt.figure(figsize=(10, 6))
            plt.plot(thrust_profile['time'], thrust_profile['thrust'])
            plt.title('Thrust Profile Over Burn Duration')
            plt.xlabel('Time (s)')
            plt.ylabel('Thrust (N)')
            plt.grid(True)
            plt.savefig(plt_file)
            plt.close()
            print(f"Thrust profile plot saved to: {plt_file}")
        except Exception as e:
            print(f"Could not generate thrust profile plot: {e}")
        
        print(f"Propulsion analysis report saved to: {output_file.replace('.pdf', '.txt')}")
        
        # Return a summary dictionary
        return {
            "thrust": thrust,
            "specific_impulse": isp,
            "delta_v": delta_v,
            "energy_required": energy,
            "exhaust_velocity": exhaust_velocity
        }
