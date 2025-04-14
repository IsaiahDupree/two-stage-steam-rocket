#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Steam Rocket Calculator for Client Project

This script specifically addresses the client requirements:
1. Rocket Engine Pressure Design
2. Steam Rocket Thrust Calculations
3. Propellant (Water) Requirements
"""

import math
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

# Physical constants
GRAVITY = 9.80665  # m/s^2, standard gravity
R_STEAM = 461.5  # J/(kg*K), specific gas constant for steam
ATM_PRESSURE = 101325  # Pa, standard atmospheric pressure
WATER_DENSITY = 1000  # kg/m^3 at room temperature

class SteamRocketCalculator:
    """
    Steam Rocket Calculator designed specifically for client requirements.
    Focuses on pressure vessel design, thrust calculations, and propellant requirements.
    """
    
    def __init__(self):
        """Initialize the calculator with default values."""
        # Default values - can be changed by user
        self.chamber_pressure = 2.0e6  # Pa (2 MPa)
        self.chamber_temperature = 450 + 273.15  # K (450°C)
        self.throat_diameter = 0.03  # m (3 cm)
        self.exit_diameter = 0.09  # m (9 cm)
        self.vessel_diameter = 0.3  # m (30 cm)
        self.vessel_length = 0.6  # m (60 cm)
        self.material_yield_strength = 500e6  # Pa (500 MPa, typical for high-grade steel)
        self.safety_factor = 2.0  # Standard for pressure vessels
        self.gamma = 1.33  # Specific heat ratio for superheated steam
        
        # Design constraints
        self.min_wall_thickness = 0.001  # m (1 mm minimum fabrication thickness)
        self.min_thrust_required = 1000  # N (minimum thrust for demonstration)
        
        # Results storage
        self.results = {}
    
    def set_pressure_parameters(self, chamber_pressure, chamber_temperature, 
                              material_yield_strength=None, safety_factor=None):
        """Set pressure vessel parameters."""
        self.chamber_pressure = chamber_pressure
        self.chamber_temperature = chamber_temperature
        
        if material_yield_strength:
            self.material_yield_strength = material_yield_strength
        
        if safety_factor:
            self.safety_factor = safety_factor
        
        return self
    
    def set_geometry_parameters(self, throat_diameter, exit_diameter, 
                              vessel_diameter, vessel_length):
        """Set geometric parameters."""
        self.throat_diameter = throat_diameter
        self.exit_diameter = exit_diameter
        self.vessel_diameter = vessel_diameter
        self.vessel_length = vessel_length
        
        return self
    
    def calculate_vessel_thickness(self):
        """
        Calculate required wall thickness for cylindrical pressure vessel.
        Uses the thin-walled pressure vessel formula with safety factor.
        """
        # Thin-walled cylindrical vessel formula: t = (P*r)/(σ*SF)
        radius = self.vessel_diameter / 2
        thickness = (self.chamber_pressure * radius) / (self.material_yield_strength / self.safety_factor)
        
        # Apply minimum thickness constraint
        thickness = max(thickness, self.min_wall_thickness)
        
        return thickness
    
    def calculate_vessel_mass(self, thickness=None):
        """Calculate the mass of the pressure vessel."""
        if thickness is None:
            thickness = self.calculate_vessel_thickness()
            
        # Calculate vessel volume (material only)
        radius = self.vessel_diameter / 2
        outer_radius = radius + thickness
        
        # Cylinder volume
        cylinder_volume = math.pi * (outer_radius**2 - radius**2) * self.vessel_length
        
        # End caps (approximated as hemispherical)
        end_caps_volume = (4/3) * math.pi * (outer_radius**3 - radius**3)
        
        # Total volume
        total_volume = cylinder_volume + end_caps_volume
        
        # Mass calculation (assuming steel density ~7800 kg/m³)
        steel_density = 7800  # kg/m³
        vessel_mass = total_volume * steel_density
        
        return vessel_mass
    
    def calculate_vessel_volume(self):
        """Calculate the internal volume of the pressure vessel."""
        radius = self.vessel_diameter / 2
        cylinder_volume = math.pi * radius**2 * self.vessel_length
        
        # Add end caps (approximated as hemispherical)
        end_caps_volume = (4/3) * math.pi * radius**3
        
        return cylinder_volume + end_caps_volume
    
    def calculate_water_capacity(self):
        """Calculate how much water the vessel can hold (in kg)."""
        # Leave 15% for expansion when heated
        usable_volume = self.calculate_vessel_volume() * 0.85
        water_mass = usable_volume * WATER_DENSITY
        
        return water_mass
    
    def calculate_throat_area(self):
        """Calculate nozzle throat area."""
        return math.pi * (self.throat_diameter/2)**2
    
    def calculate_exit_area(self):
        """Calculate nozzle exit area."""
        return math.pi * (self.exit_diameter/2)**2
    
    def calculate_expansion_ratio(self):
        """Calculate nozzle expansion ratio."""
        return self.calculate_exit_area() / self.calculate_throat_area()
    
    def calculate_exhaust_velocity(self):
        """
        Calculate the exhaust velocity of steam using the rocket equation.
        Based on isentropic expansion through the nozzle.
        """
        # Pressure ratio (assuming optimal expansion to ambient)
        pressure_ratio = ATM_PRESSURE / self.chamber_pressure
        
        # Exhaust velocity calculation using the rocket equation
        ve = math.sqrt((2 * self.gamma * R_STEAM * self.chamber_temperature) / 
                      (self.gamma - 1) * (1 - pressure_ratio**((self.gamma - 1) / self.gamma)))
        
        # Apply efficiency factor for heat losses (typically 80-90%)
        efficiency = 0.85
        ve *= efficiency
        
        return ve
    
    def calculate_mass_flow_rate(self):
        """
        Calculate the mass flow rate of steam through the nozzle.
        Uses the choked flow equation for the throat.
        """
        # Choked flow parameter
        choked_param = math.sqrt(self.gamma) * (2/(self.gamma+1))**((self.gamma+1)/(2*(self.gamma-1)))
        
        # Mass flow rate calculation
        mdot = (self.chamber_pressure * self.calculate_throat_area() * 
                choked_param / math.sqrt(R_STEAM * self.chamber_temperature))
        
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
    
    def calculate_burn_time(self, water_mass=None):
        """
        Calculate how long the rocket can produce thrust with the given water mass.
        """
        if water_mass is None:
            water_mass = self.calculate_water_capacity()
            
        # Mass flow rate
        mass_flow_rate = self.calculate_mass_flow_rate()
        
        # Burn time (assuming all water is converted to steam)
        if mass_flow_rate > 0:
            burn_time = water_mass / mass_flow_rate
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
    
    def calculate_total_impulse(self, water_mass=None):
        """Calculate total impulse (thrust integrated over time)."""
        thrust = self.calculate_thrust()
        burn_time = self.calculate_burn_time(water_mass)
        
        return thrust * burn_time
    
    def calculate_required_water_mass(self, target_thrust, target_burn_time):
        """
        Calculate the water mass required for a specific thrust and burn time.
        """
        # First, adjust the nozzle throat to achieve the target thrust
        self.adjust_throat_for_target_thrust(target_thrust)
        
        # Calculate required water mass for the target burn time
        mass_flow_rate = self.calculate_mass_flow_rate()
        required_water_mass = mass_flow_rate * target_burn_time
        
        return required_water_mass
    
    def adjust_throat_for_target_thrust(self, target_thrust):
        """
        Adjust the throat diameter to achieve a target thrust.
        This is an iterative process to find the right throat diameter.
        """
        # Initial values
        current_thrust = self.calculate_thrust()
        iterations = 0
        max_iterations = 20
        tolerance = 0.01  # 1% accuracy
        
        while (abs(current_thrust - target_thrust) / target_thrust > tolerance and 
               iterations < max_iterations):
            # Adjust throat diameter based on thrust ratio
            self.throat_diameter *= math.sqrt(target_thrust / current_thrust)
            
            # Recalculate thrust
            current_thrust = self.calculate_thrust()
            iterations += 1
        
        # Adjust exit diameter to maintain expansion ratio
        original_expansion_ratio = self.calculate_expansion_ratio()
        new_throat_area = self.calculate_throat_area()
        new_exit_area = new_throat_area * original_expansion_ratio
        self.exit_diameter = 2 * math.sqrt(new_exit_area / math.pi)
        
        return current_thrust
    
    def run_complete_analysis(self):
        """
        Run all calculations and return comprehensive results.
        """
        # Pressure vessel calculations
        wall_thickness = self.calculate_vessel_thickness()
        vessel_mass = self.calculate_vessel_mass(wall_thickness)
        vessel_volume = self.calculate_vessel_volume()
        water_capacity = self.calculate_water_capacity()
        
        # Nozzle and performance calculations
        throat_area = self.calculate_throat_area()
        exit_area = self.calculate_exit_area()
        expansion_ratio = self.calculate_expansion_ratio()
        exhaust_velocity = self.calculate_exhaust_velocity()
        mass_flow_rate = self.calculate_mass_flow_rate()
        thrust = self.calculate_thrust()
        burn_time = self.calculate_burn_time()
        specific_impulse = self.calculate_specific_impulse()
        total_impulse = self.calculate_total_impulse()
        
        # Store results
        self.results = {
            # Input parameters
            "chamber_pressure": self.chamber_pressure,
            "chamber_temperature": self.chamber_temperature,
            "throat_diameter": self.throat_diameter,
            "exit_diameter": self.exit_diameter,
            "vessel_diameter": self.vessel_diameter,
            "vessel_length": self.vessel_length,
            "material_yield_strength": self.material_yield_strength,
            "safety_factor": self.safety_factor,
            
            # Pressure vessel results
            "wall_thickness": wall_thickness,
            "vessel_mass": vessel_mass,
            "vessel_volume": vessel_volume,
            "water_capacity": water_capacity,
            
            # Nozzle and performance results
            "throat_area": throat_area,
            "exit_area": exit_area,
            "expansion_ratio": expansion_ratio,
            "exhaust_velocity": exhaust_velocity,
            "mass_flow_rate": mass_flow_rate,
            "thrust": thrust,
            "burn_time": burn_time,
            "specific_impulse": specific_impulse,
            "total_impulse": total_impulse
        }
        
        return self.results
    
    def generate_report(self, filename=None):
        """
        Generate a detailed report of the steam rocket design.
        """
        if not self.results:
            self.run_complete_analysis()
            
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"steam_rocket_report_{timestamp}.txt"
        
        with open(filename, 'w') as f:
            f.write("===============================================\n")
            f.write("STEAM ROCKET DESIGN AND ANALYSIS REPORT\n")
            f.write("===============================================\n\n")
            
            f.write("1. PRESSURE VESSEL SPECIFICATIONS\n")
            f.write("-----------------------------------------------\n")
            f.write(f"Chamber Pressure: {self.results['chamber_pressure']/1e6:.2f} MPa\n")
            f.write(f"Chamber Temperature: {self.results['chamber_temperature']-273.15:.2f}°C\n")
            f.write(f"Vessel Diameter: {self.results['vessel_diameter']*100:.2f} cm\n")
            f.write(f"Vessel Length: {self.results['vessel_length']*100:.2f} cm\n")
            f.write(f"Material Yield Strength: {self.results['material_yield_strength']/1e6:.2f} MPa\n")
            f.write(f"Safety Factor: {self.results['safety_factor']:.2f}\n")
            f.write(f"Required Wall Thickness: {self.results['wall_thickness']*1000:.2f} mm\n")
            f.write(f"Vessel Mass (empty): {self.results['vessel_mass']:.2f} kg\n")
            f.write(f"Vessel Volume (internal): {self.results['vessel_volume']*1000:.2f} liters\n")
            f.write(f"Water Capacity: {self.results['water_capacity']:.2f} kg\n\n")
            
            f.write("2. NOZZLE SPECIFICATIONS\n")
            f.write("-----------------------------------------------\n")
            f.write(f"Throat Diameter: {self.results['throat_diameter']*1000:.2f} mm\n")
            f.write(f"Exit Diameter: {self.results['exit_diameter']*1000:.2f} mm\n")
            f.write(f"Expansion Ratio: {self.results['expansion_ratio']:.2f}\n")
            f.write(f"Throat Area: {self.results['throat_area']*1e4:.2f} cm²\n")
            f.write(f"Exit Area: {self.results['exit_area']*1e4:.2f} cm²\n\n")
            
            f.write("3. PERFORMANCE CALCULATIONS\n")
            f.write("-----------------------------------------------\n")
            f.write(f"Exhaust Velocity: {self.results['exhaust_velocity']:.2f} m/s\n")
            f.write(f"Mass Flow Rate: {self.results['mass_flow_rate']:.4f} kg/s\n")
            f.write(f"Thrust: {self.results['thrust']:.2f} N ({self.results['thrust']/1000:.2f} kN)\n")
            f.write(f"Specific Impulse: {self.results['specific_impulse']:.2f} seconds\n")
            f.write(f"Burn Time: {self.results['burn_time']:.2f} seconds\n")
            f.write(f"Total Impulse: {self.results['total_impulse']/1000:.2f} kN·s\n\n")
            
            f.write("4. DESIGN RECOMMENDATIONS\n")
            f.write("-----------------------------------------------\n")
            if self.results['wall_thickness'] * 1000 < 3:
                f.write("- Wall thickness is below 3mm, consider increasing for manufacturing ease\n")
            if self.results['specific_impulse'] < 80:
                f.write("- Consider increasing chamber temperature to improve specific impulse\n")
            if self.results['burn_time'] < 10:
                f.write("- Consider increasing vessel size or decreasing throat diameter for longer burn time\n")
            if self.results['thrust'] < 1000:
                f.write("- Thrust may be insufficient for meaningful flight, consider increasing chamber pressure\n")
            
            f.write("\n===============================================\n")
            f.write("END OF REPORT\n")
            f.write("===============================================\n")
            
        return filename
    
    def generate_spreadsheet(self, filename=None):
        """
        Generate a detailed Excel spreadsheet with all calculations and formulas.
        """
        if not self.results:
            self.run_complete_analysis()
            
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"steam_rocket_calculations_{timestamp}.xlsx"
        
        # Create a Pandas Excel writer
        writer = pd.ExcelWriter(filename, engine='xlsxwriter')
        
        # Create dataframes for each section
        input_data = {
            'Parameter': [
                'Chamber Pressure',
                'Chamber Temperature',
                'Throat Diameter',
                'Exit Diameter',
                'Vessel Diameter',
                'Vessel Length',
                'Material Yield Strength',
                'Safety Factor'
            ],
            'Value': [
                self.chamber_pressure,
                self.chamber_temperature,
                self.throat_diameter,
                self.exit_diameter,
                self.vessel_diameter,
                self.vessel_length,
                self.material_yield_strength,
                self.safety_factor
            ],
            'Unit': [
                'Pa',
                'K',
                'm',
                'm',
                'm',
                'm',
                'Pa',
                '-'
            ],
            'Value (conventional)': [
                f"{self.chamber_pressure/1e6:.2f} MPa",
                f"{self.chamber_temperature-273.15:.2f}°C",
                f"{self.throat_diameter*1000:.2f} mm",
                f"{self.exit_diameter*1000:.2f} mm",
                f"{self.vessel_diameter*100:.2f} cm",
                f"{self.vessel_length*100:.2f} cm",
                f"{self.material_yield_strength/1e6:.2f} MPa",
                f"{self.safety_factor:.2f}"
            ]
        }
        
        vessel_data = {
            'Parameter': [
                'Wall Thickness',
                'Vessel Mass (empty)',
                'Vessel Volume (internal)',
                'Water Capacity'
            ],
            'Value': [
                self.results['wall_thickness'],
                self.results['vessel_mass'],
                self.results['vessel_volume'],
                self.results['water_capacity']
            ],
            'Unit': [
                'm',
                'kg',
                'm³',
                'kg'
            ],
            'Value (conventional)': [
                f"{self.results['wall_thickness']*1000:.2f} mm",
                f"{self.results['vessel_mass']:.2f} kg",
                f"{self.results['vessel_volume']*1000:.2f} liters",
                f"{self.results['water_capacity']:.2f} kg"
            ]
        }
        
        nozzle_data = {
            'Parameter': [
                'Throat Area',
                'Exit Area',
                'Expansion Ratio'
            ],
            'Value': [
                self.results['throat_area'],
                self.results['exit_area'],
                self.results['expansion_ratio']
            ],
            'Unit': [
                'm²',
                'm²',
                '-'
            ],
            'Value (conventional)': [
                f"{self.results['throat_area']*1e4:.2f} cm²",
                f"{self.results['exit_area']*1e4:.2f} cm²",
                f"{self.results['expansion_ratio']:.2f}"
            ]
        }
        
        performance_data = {
            'Parameter': [
                'Exhaust Velocity',
                'Mass Flow Rate',
                'Thrust',
                'Specific Impulse',
                'Burn Time',
                'Total Impulse'
            ],
            'Value': [
                self.results['exhaust_velocity'],
                self.results['mass_flow_rate'],
                self.results['thrust'],
                self.results['specific_impulse'],
                self.results['burn_time'],
                self.results['total_impulse']
            ],
            'Unit': [
                'm/s',
                'kg/s',
                'N',
                's',
                's',
                'N·s'
            ],
            'Value (conventional)': [
                f"{self.results['exhaust_velocity']:.2f} m/s",
                f"{self.results['mass_flow_rate']:.4f} kg/s",
                f"{self.results['thrust']/1000:.2f} kN",
                f"{self.results['specific_impulse']:.2f} s",
                f"{self.results['burn_time']:.2f} s",
                f"{self.results['total_impulse']/1000:.2f} kN·s"
            ]
        }
        
        # Create dataframes
        df_input = pd.DataFrame(input_data)
        df_vessel = pd.DataFrame(vessel_data)
        df_nozzle = pd.DataFrame(nozzle_data)
        df_performance = pd.DataFrame(performance_data)
        
        # Write each dataframe to a different worksheet
        df_input.to_excel(writer, sheet_name='Input Parameters', index=False)
        df_vessel.to_excel(writer, sheet_name='Pressure Vessel', index=False)
        df_nozzle.to_excel(writer, sheet_name='Nozzle Design', index=False)
        df_performance.to_excel(writer, sheet_name='Performance', index=False)
        
        # Save the Excel file
        writer.close()
        
        return filename


def main():
    """Example usage of the Steam Rocket Calculator."""
    # Create a calculator instance
    calculator = SteamRocketCalculator()
    
    # Set parameters appropriate for a small demonstration steam rocket
    calculator.set_pressure_parameters(
        chamber_pressure=2.0e6,  # 2 MPa
        chamber_temperature=400 + 273.15,  # 400°C
    )
    
    calculator.set_geometry_parameters(
        throat_diameter=0.015,  # 15 mm
        exit_diameter=0.045,  # 45 mm
        vessel_diameter=0.2,   # 20 cm
        vessel_length=0.4      # 40 cm
    )
    
    # Run analysis and generate reports
    calculator.run_complete_analysis()
    report_file = calculator.generate_report()
    spreadsheet_file = calculator.generate_spreadsheet()
    
    print(f"Steam rocket analysis completed!")
    print(f"Thrust: {calculator.results['thrust']:.2f} N")
    print(f"Burn time: {calculator.results['burn_time']:.2f} seconds")
    print(f"Report saved to: {report_file}")
    print(f"Calculations saved to: {spreadsheet_file}")
    
    # Example of sizing a rocket for specific requirements
    print("\nSizing rocket for target performance:")
    target_thrust = 2000  # N
    target_burn_time = 20  # seconds
    
    required_water = calculator.calculate_required_water_mass(target_thrust, target_burn_time)
    print(f"Required water mass for {target_thrust} N thrust and {target_burn_time} s burn time: {required_water:.2f} kg")


if __name__ == "__main__":
    main()
