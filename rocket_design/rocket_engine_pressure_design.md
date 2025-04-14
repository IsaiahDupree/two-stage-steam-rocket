# Rocket Engine Pressure Design

## Overview
This section details the engineering design of our steam-based rocket propulsion system, including pressure vessel specifications, nozzle design, and material selection considerations.

## Pressure Vessel Design

### Design Requirements
The pressure vessel must safely contain high-pressure, high-temperature steam while being as lightweight as possible:

- **First Stage Operating Pressure**: 3.0 MPa (435 psi)
- **First Stage Operating Temperature**: 450°C (842°F)
- **Second Stage Operating Pressure**: 2.0 MPa (290 psi)
- **Second Stage Operating Temperature**: 400°C (752°F)
- **Safety Factor**: 2.0 (per ASME BPVC Section VIII standards)
- **Cycles to Failure**: >100 (target operational life)

### Wall Thickness Calculations

The minimum required wall thickness for a cylindrical pressure vessel is calculated using the formula:

```
t = (P × r) / (S × E)
```

Where:
- t = Wall thickness (m)
- P = Internal pressure (Pa)
- r = Vessel radius (m)
- S = Material yield strength (Pa)
- E = Joint efficiency factor (0.85 for welded construction)

#### First Stage Calculations
- Vessel radius: 0.45 m (450 mm)
- Vessel length: 3.0 m (3000 mm)
- Operating pressure: 3.0 MPa
- Safety factor: 2.0
- Material: Stainless Steel 304 (yield strength = 215 MPa)
- Joint efficiency: 0.85

**Required wall thickness:**
```math
t = (3.0 × 10^6 Pa × 0.45 m × 2.0) / (215 × 10^6 Pa × 0.85)
t = 14.73 mm
```

For manufacturing considerations and additional safety, the actual wall thickness is specified as 16 mm.

#### Second Stage Calculations
- Vessel radius: 0.30 m (300 mm)
- Vessel length: 1.8 m (1800 mm)
- Operating pressure: 2.0 MPa
- Safety factor: 2.0
- Material: Ti-6Al-4V (yield strength = 880 MPa)
- Joint efficiency: 0.9

**Required wall thickness:**
```math
t = (2.0 × 10^6 Pa × 0.30 m × 2.0) / (880 × 10^6 Pa × 0.9)
t = 1.52 mm
```

For manufacturing considerations and additional safety, the actual wall thickness is specified as 3 mm.

### Thermal Expansion Analysis

Thermal expansion must be accounted for in the pressure vessel design, particularly at the high operating temperatures of a steam rocket:

- **Stainless Steel 304 Thermal Expansion Coefficient**: 17.3 × 10^-6 /°C
- **Ti-6Al-4V Thermal Expansion Coefficient**: 8.6 × 10^-6 /°C

For the first stage vessel (L = 0.6 m), the expansion at operating temperature:
```
ΔL = L × α × ΔT
ΔL = 0.6 m × 17.3 × 10^-6 /°C × (450°C - 20°C)
ΔL = 4.45 mm
```

Design accommodations for this expansion include:
- Bellows-type expansion joints
- Sliding supports with PTFE pads
- Pre-stressed mounting points

## Nozzle Design

### Design Principles
The rocket nozzle converts the thermal energy of the pressurized steam into kinetic energy. The design follows de Laval nozzle principles with converging-diverging geometry.

### First Stage Nozzle (Sea Level)
- **Throat Diameter**: 200 mm (20 cm)
- **Exit Diameter**: 600 mm (60 cm)
- **Expansion Ratio (Ae/At)**: 9.0
- **Nozzle Length**: 800 mm (80 cm)
- **Throat Material**: Copper alloy (C17200) for thermal conductivity
- **Expansion Section**: 304 stainless steel with thermal barrier coating

### Second Stage Nozzle (Vacuum)
- **Throat Diameter**: 120 mm (12 cm)
- **Exit Diameter**: 480 mm (48 cm)
- **Expansion Ratio (Ae/At)**: 16.0
- **Nozzle Length**: 600 mm (60 cm)
- **Throat Material**: Copper alloy (C17200) for thermal conductivity
- **Expansion Section**: Titanium alloy with ceramic coating

### Nozzle Flow Analysis
Flow behavior is modeled using compressible fluid dynamics principles:

- **Mach Number at Throat**: 1.0 (by definition at the sonic point)
- **Exit Mach Number (First Stage)**: 3.1
- **Exit Mach Number (Second Stage)**: 4.2
- **Flow Regime**: Supersonic in expansion section
- **Boundary Layer**: Accounting for approximately 2% thrust loss

## Material Selection Considerations

### Material Comparison

| Material | Yield Strength (MPa) | Density (kg/m³) | Max Temp (°C) | Cost Factor | Machinability |
|----------|---------------------|-----------------|--------------|------------|---------------|
| SS 304   | 215                 | 8000           | 870          | 1.0x       | Good          |
| SS 316   | 240                 | 8000           | 870          | 1.2x       | Good          |
| Ti-6Al-4V| 880                 | 4430           | 600          | 5.0x       | Moderate      |
| Inconel 718 | 1100            | 8190           | 980          | 7.0x       | Poor          |

### Selection Rationale
- **First Stage**: Stainless Steel 304 - selected for cost-effectiveness, good machinability, and adequate strength for the pressure requirements
- **Second Stage**: Ti-6Al-4V - selected for superior strength-to-weight ratio despite higher cost, critical for upper stage performance
- **High-Heat Areas**: Inconel 718 - used selectively for components experiencing extreme thermal conditions

## Pressure Relief Systems

### Safety Mechanisms
- **Burst Discs**: Calibrated to rupture at 120% of maximum design pressure
- **Relief Valves**: Spring-loaded, set to activate at 110% of maximum design pressure
- **Redundancy**: Dual relief systems on each pressure vessel
- **Monitoring**: Pressure transducers with digital readout and data logging

### Testing Protocol
- **Hydrostatic Testing**: To 1.5× design pressure
- **Leak Testing**: Helium mass spectrometer testing to detect microleaks
- **Thermal Cycling**: 20 cycles from ambient to operating temperature
- **X-Ray Inspection**: 100% of welds to ensure integrity
