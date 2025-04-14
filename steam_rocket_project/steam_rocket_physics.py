#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Steam Rocket Physics Calculator

This module provides calculations for steam-powered rocket propulsion systems,
including thrust, pressure, propellant requirements, and efficiency.
Based on thermodynamic principles and rocket engineering fundamentals.
"""

import math
import numpy as np
import matplotlib.pyplot as plt
from dataclasses import dataclass

# Physical constants
GRAVITY = 9.80665  # m/s^2, standard gravity
R_STEAM = 461.5  # J/(kg*K), specific gas constant for steam
R_UNIVERSAL = 8.3145  # J/(mol*K), universal gas constant
WATER_MOLAR_MASS = 18.01528  # g/mol
ATM_PRESSURE = 101325  # Pa, standard atmospheric pressure
WATER_DENSITY = 1000  # kg/m^3 at room temperature

@dataclass
class SteamRocketParameters:
    """Container for steam rocket design parameters."""
    chamber_pressure: float  # Pa
    chamber_temperature: float  # K
    nozzle_throat_diameter: float  # m
    nozzle_exit_diameter: float  # m
    water_mass: float  # kg
    vessel_volume: float  # m^3
    vessel_material_yield_strength: float  # Pa
    safety_factor: float = 1.5
    heat_loss_factor: float = 0.85  # Efficiency factor for heat losses
    
    @property
    def throat_area(self):
        """Calculate throat area in m^2."""
        return math.pi * (self.nozzle_throat_diameter/2)**2
    
    @property
    def exit_area(self):
        """Calculate exit area in m^2."""
        return math.pi * (self.nozzle_exit_diameter/2)**2
    
    @property
    def expansion_ratio(self):
        """Calculate nozzle expansion ratio."""
        return self.exit_area / self.throat_area
    
    @property
    def vessel_wall_thickness(self):
        """
        Calculate minimum vessel wall thickness using pressure vessel formula.
        For cylindrical pressure vessels under internal pressure.
        """
        vessel_radius = (self.vessel_volume / (4/3 * math.pi))**(1/3)  # Approximating as spherical
        required_thickness = (self.chamber_pressure * vessel_radius) / \
                           (2 * self.vessel_material_yield_strength / self.safety_factor)
        return required_thickness


class SteamRocketCalculator:
    """Calculates performance parameters for a steam rocket."""
    
    def __init__(self, rocket_params):
        """Initialize with steam rocket parameters."""
        self.params = rocket_params
        
    def calculate_exhaust_velocity(self):
        """
        Calculate the exhaust velocity of steam using the rocket equation.
        Based on isentropic expansion through the nozzle.
        """
        # Specific heat ratio for superheated steam (approximation)
        gamma = 1.33
        
        # Pressure ratio (assuming optimal expansion to ambient)
        pressure_ratio = ATM_PRESSURE / self.params.chamber_pressure
        
        # Exhaust velocity calculation using the rocket equation
        ve = math.sqrt((2 * gamma * R_STEAM * self.params.chamber_temperature) / 
                      (gamma - 1) * (1 - pressure_ratio**((gamma - 1) / gamma)))
        
        # Apply heat loss / efficiency factor
        ve *= self.params.heat_loss_factor
        
        return ve
    
    def calculate_mass_flow_rate(self):
        """
        Calculate the mass flow rate of steam through the nozzle.
        Uses the choked flow equation for the throat.
        """
        # Specific heat ratio for superheated steam
        gamma = 1.33
        
        # Choked flow parameter
        choked_param = math.sqrt(gamma) * (2/(gamma+1))**((gamma+1)/(2*(gamma-1)))
        
        # Mass flow rate calculation
        mdot = (self.params.chamber_pressure * self.params.throat_area * 
                choked_param / math.sqrt(R_STEAM * self.params.chamber_temperature))
        
        return mdot
    
    def calculate_thrust(self):
        """
        Calculate thrust produced by the steam rocket.
        F = mdot * ve + (pe - pa) * Ae
        """
        # Calculate exhaust velocity and mass flow rate
        exhaust_velocity = self.calculate_exhaust_velocity()
        mass_flow_rate = self.calculate_mass_flow_rate()
        
        # For simplicity, assuming optimal expansion (pe = pa)
        pressure_thrust = 0
        
        # Total thrust
        thrust = mass_flow_rate * exhaust_velocity + pressure_thrust
        
        return thrust
    
    def calculate_burn_time(self):
        """
        Calculate how long the rocket can produce thrust with the given water mass.
        """
        # Mass flow rate
        mass_flow_rate = self.calculate_mass_flow_rate()
        
        # Burn time (assuming all water is converted to steam)
        if mass_flow_rate > 0:
            burn_time = self.params.water_mass / mass_flow_rate
        else:
            burn_time = 0
            
        return burn_time
    
    def calculate_specific_impulse(self):
        """
        Calculate specific impulse (Isp) in seconds.
        Isp = F / (mdot * g0)
        """
        thrust = self.calculate_thrust()
        mass_flow_rate = self.calculate_mass_flow_rate()
        
        if mass_flow_rate > 0:
            isp = thrust / (mass_flow_rate * GRAVITY)
        else:
            isp = 0
            
        return isp
    
    def calculate_delta_v(self, rocket_dry_mass):
        """
        Calculate the theoretical delta-v using the rocket equation.
        delta_v = ve * ln(m0/mf)
        """
        initial_mass = rocket_dry_mass + self.params.water_mass
        final_mass = rocket_dry_mass
        
        exhaust_velocity = self.calculate_exhaust_velocity()
        delta_v = exhaust_velocity * math.log(initial_mass / final_mass)
        
        return delta_v
    
    def calculate_pressure_over_time(self, time_points):
        """
        Calculate pressure decay over time as steam is expended.
        Simplified model assuming isothermal expansion.
        """
        mass_flow_rate = self.calculate_mass_flow_rate()
        burn_time = self.calculate_burn_time()
        
        pressures = []
        for t in time_points:
            if t > burn_time:
                pressures.append(0)  # Out of propellant
            else:
                # Remaining mass fraction
                mass_fraction = 1 - (t / burn_time)
                # Simplified pressure model (proportional to mass)
                pressure = self.params.chamber_pressure * mass_fraction
                pressures.append(pressure)
                
        return pressures
    
    def plot_performance(self):
        """Generate plots of key performance metrics over time."""
        burn_time = self.calculate_burn_time()
        time_points = np.linspace(0, burn_time * 1.1, 100)
        
        # Calculate metrics over time
        pressures = self.calculate_pressure_over_time(time_points)
        
        # Plot pressure vs time
        plt.figure(figsize=(10, 6))
        plt.plot(time_points, [p/1e6 for p in pressures])
        plt.title('Chamber Pressure vs Time')
        plt.xlabel('Time (s)')
        plt.ylabel('Pressure (MPa)')
        plt.grid(True)
        
        # Save the figure
        plt.savefig('steam_rocket_pressure.png')
        plt.close()
        
        # Calculate thrust over time (simplified - proportional to pressure)
        thrust = self.calculate_thrust()
        thrusts = [thrust * (p/self.params.chamber_pressure) for p in pressures]
        
        # Plot thrust vs time
        plt.figure(figsize=(10, 6))
        plt.plot(time_points, [t/1e3 for t in thrusts])
        plt.title('Thrust vs Time')
        plt.xlabel('Time (s)')
        plt.ylabel('Thrust (kN)')
        plt.grid(True)
        
        # Save the figure
        plt.savefig('steam_rocket_thrust.png')
        plt.close()
    
    def generate_performance_report(self, rocket_dry_mass, report_file='steam_rocket_report.txt'):
        """Generate a comprehensive performance report."""
        thrust = self.calculate_thrust()
        isp = self.calculate_specific_impulse()
        exhaust_velocity = self.calculate_exhaust_velocity()
        mass_flow_rate = self.calculate_mass_flow_rate()
        burn_time = self.calculate_burn_time()
        delta_v = self.calculate_delta_v(rocket_dry_mass)
        
        with open(report_file, 'w') as f:
            f.write("============================================\n")
            f.write("STEAM ROCKET PERFORMANCE REPORT\n")
            f.write("============================================\n\n")
            
            f.write("INPUT PARAMETERS:\n")
            f.write(f"Chamber Pressure: {self.params.chamber_pressure/1e6:.2f} MPa\n")
            f.write(f"Chamber Temperature: {self.params.chamber_temperature:.2f} K ({self.params.chamber_temperature-273.15:.2f}°C)\n")
            f.write(f"Throat Diameter: {self.params.nozzle_throat_diameter*1000:.2f} mm\n")
            f.write(f"Exit Diameter: {self.params.nozzle_exit_diameter*1000:.2f} mm\n")
            f.write(f"Expansion Ratio: {self.params.expansion_ratio:.2f}\n")
            f.write(f"Water Mass: {self.params.water_mass:.2f} kg\n")
            f.write(f"Vessel Volume: {self.params.vessel_volume*1000:.2f} liters\n")
            f.write(f"Vessel Material Yield Strength: {self.params.vessel_material_yield_strength/1e6:.2f} MPa\n")
            f.write(f"Safety Factor: {self.params.safety_factor:.2f}\n\n")
            
            f.write("CALCULATED PERFORMANCE:\n")
            f.write(f"Thrust: {thrust/1e3:.2f} kN\n")
            f.write(f"Specific Impulse (Isp): {isp:.2f} seconds\n")
            f.write(f"Exhaust Velocity: {exhaust_velocity:.2f} m/s\n")
            f.write(f"Mass Flow Rate: {mass_flow_rate:.4f} kg/s\n")
            f.write(f"Burn Time: {burn_time:.2f} seconds\n")
            f.write(f"Total Impulse: {thrust * burn_time/1e3:.2f} kN·s\n")
            f.write(f"Theoretical Delta-V: {delta_v:.2f} m/s\n\n")
            
            f.write("PRESSURE VESSEL SPECIFICATIONS:\n")
            f.write(f"Required Wall Thickness: {self.params.vessel_wall_thickness*1000:.2f} mm\n")
            
            # Recommendations
            f.write("\nRECOMMENDATIONS:\n")
            if isp < 70:
                f.write("- Consider increasing chamber temperature to improve specific impulse\n")
            if burn_time < a:
                f.write("- Consider increasing water mass or decreasing throat diameter for longer burn time\n")
            if self.params.vessel_wall_thickness > 0.01:
                f.write("- Consider using higher strength materials or reducing chamber pressure to decrease wall thickness\n")
            
            f.write("\n============================================\n")
            f.write("END OF REPORT\n")
            f.write("============================================\n")


def design_example_steam_rocket():
    """
    Design example for a two-stage steam rocket for educational purposes.
    """
    # First stage parameters (larger, higher pressure)
    first_stage_params = SteamRocketParameters(
        chamber_pressure=5.0e6,  # 5 MPa
        chamber_temperature=500 + 273.15,  # 500°C in Kelvin
        nozzle_throat_diameter=0.05,  # 5 cm
        nozzle_exit_diameter=0.15,  # 15 cm
        water_mass=100.0,  # 100 kg of water
        vessel_volume=0.15,  # 150 liters
        vessel_material_yield_strength=500e6,  # 500 MPa (high-strength steel)
        safety_factor=2.0
    )
    
    # Second stage parameters (smaller, optimized for vacuum)
    second_stage_params = SteamRocketParameters(
        chamber_pressure=3.0e6,  # 3 MPa
        chamber_temperature=450 + 273.15,  # 450°C in Kelvin
        nozzle_throat_diameter=0.025,  # 2.5 cm
        nozzle_exit_diameter=0.125,  # 12.5 cm (higher expansion ratio for vacuum)
        water_mass=20.0,  # 20 kg of water
        vessel_volume=0.03,  # 30 liters
        vessel_material_yield_strength=650e6,  # 650 MPa (higher strength alloy)
        safety_factor=1.8
    )
    
    # Create calculators
    first_stage_calc = SteamRocketCalculator(first_stage_params)
    second_stage_calc = SteamRocketCalculator(second_stage_params)
    
    # Rocket masses (excluding propellant)
    first_stage_dry_mass = 50.0  # kg
    second_stage_dry_mass = 15.0  # kg
    payload_mass = 5.0  # kg
    
    # Generate reports
    first_stage_calc.generate_performance_report(
        first_stage_dry_mass + second_stage_dry_mass + second_stage_params.water_mass + payload_mass,
        'first_stage_report.txt'
    )
    
    second_stage_calc.generate_performance_report(
        second_stage_dry_mass + payload_mass,
        'second_stage_report.txt'
    )
    
    # Generate plots
    first_stage_calc.plot_performance()
    second_stage_calc.plot_performance()
    
    print("Steam rocket design and analysis completed!")
    print("Check the report files and performance plots for details.")


if __name__ == "__main__":
    design_example_steam_rocket()
