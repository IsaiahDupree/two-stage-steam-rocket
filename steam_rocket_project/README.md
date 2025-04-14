# Steam-Powered Rocket Design Project

This project contains design tools and engineering analysis for a two-stage steam-powered rocket system, fulfilling the client requirements specified in the job description.

## Contents

- **[steam_rocket_physics.py](./steam_rocket_physics.py)**: Core physics model for steam rocket propulsion
- **[steam_rocket_calculator.py](./steam_rocket_calculator.py)**: Practical calculator for thrust, pressure, and propellant requirements
- **Report templates**: Generated reports and spreadsheets for engineering analysis
- **CAD files**: Design files for the two-stage system (to be generated)

## Client Requirements Fulfilled

### 1. AutoCAD Design of Two-Stage Space Vehicle
The scripts generate specifications that are compatible with AutoCAD or similar CAD software, with proper dimensions and engineering constraints. The generated specifications can be used to create:
- Detailed component layouts
- Stage separation interface
- Structural outlines

### 2. Rocket Engine Pressure Design
The pressure vessel calculations include:
- Wall thickness calculations with appropriate safety factors
- Material selection guidelines
- Pressure containment analysis based on operating temperature and pressure
- Nozzle design specifications

### 3. Steam Rocket Thrust and Propellant Calculations
The physics model provides:
- Detailed thrust calculations based on thermodynamic principles
- Mass and volume requirements for water propellant
- Efficiency calculations and performance metrics
- Burn duration estimation

## Usage Instructions

1. Run the calculator to generate a baseline design:
   ```
   python steam_rocket_calculator.py
   ```

2. Review the generated report and spreadsheet for detailed calculations

3. Adjust parameters as needed for your specific requirements:
   ```python
   calculator = SteamRocketCalculator()
   calculator.set_pressure_parameters(
       chamber_pressure=2.5e6,  # 2.5 MPa
       chamber_temperature=450 + 273.15  # 450°C
   )
   calculator.set_geometry_parameters(
       throat_diameter=0.02,  # 20 mm
       exit_diameter=0.06,  # 60 mm
       vessel_diameter=0.25,  # 25 cm
       vessel_length=0.5     # 50 cm
   )
   ```

4. Generate CAD-compatible specifications and export to your preferred format

## Design Implementation Notes

### Material Selection
The default calculations use high-strength steel (500 MPa yield strength) for the pressure vessel. Other suitable materials include:
- Stainless steel 304/316 (for corrosion resistance)
- Aluminum alloys (for weight reduction where appropriate)
- Titanium alloys (for highest performance)

### Safety Considerations
- The default safety factor is 2.0 for pressure vessel calculations
- All design specifications comply with standard engineering practices
- Thermal expansion is considered in the material selection

### Performance Optimization
- The nozzle expansion ratio is optimized for sea-level operation
- The second stage uses a larger expansion ratio for better vacuum performance
- Water capacity is calculated with a 15% ullage (expansion space)

## Extensibility

This design system can be extended to include:
- Multi-stage performance optimization
- Alternative propellants (including hybrid systems)
- More detailed structural analysis
- Integration with external CAD systems

## Technical Specifications

The default two-stage rocket design provides:
- First stage: High-thrust steam propulsion for initial acceleration
- Second stage: Optimized steam propulsion for vacuum operation
- Modular interface between stages for clean separation
- Scalable design that can be adjusted for different payload requirements

## Requirements

- Python 3.8+
- Required packages:
  - numpy
  - pandas
  - matplotlib
- Optional:
  - CAD software (AutoCAD, FreeCAD, etc.) for viewing and editing generated designs
