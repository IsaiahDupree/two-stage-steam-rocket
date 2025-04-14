# Steam Rocket Thrust and Propellant Calculations

## Overview
This section presents detailed thrust calculations for our steam-based propulsion system, including propellant mass requirements, burn duration analysis, and system efficiency metrics.

## Fundamental Steam Rocket Equations

### Thrust Equation
The basic thrust equation for a rocket engine is:

```
F = ṁ × ve + (pe - pa) × Ae
```

Where:
- F = Thrust force (N)
- ṁ = Mass flow rate of propellant (kg/s)
- ve = Exhaust velocity (m/s)
- pe = Exit pressure at nozzle (Pa)
- pa = Ambient pressure (Pa)
- Ae = Exit area of nozzle (m²)

### Mass Flow Rate
For a choked flow through the nozzle throat:

```
ṁ = (p0 × At) / √(R × T0) × √γ × (2/(γ+1))^((γ+1)/(2(γ-1)))
```

Where:
- ṁ = Mass flow rate (kg/s)
- p0 = Chamber pressure (Pa)
- At = Throat area (m²)
- R = Specific gas constant for steam (461.5 J/kg·K)
- T0 = Chamber temperature (K)
- γ = Specific heat ratio for steam (1.33)

### Exhaust Velocity
Ideal exhaust velocity for a convergent-divergent nozzle:

```
ve = √[2γR×T0/(γ-1) × (1-(pe/p0)^((γ-1)/γ))]
```

### Specific Impulse
Measure of propulsion efficiency:

```
Isp = F / (ṁ × g0)
```

Where g0 = 9.81 m/s² (standard gravity)

## First Stage Calculations

### Input Parameters
- Chamber Pressure (p0): 3.0 MPa
- Chamber Temperature (T0): 723.15 K (450°C)
- Throat Diameter: 200 mm (Area = 3.14×10⁻² m²)
- Exit Diameter: 600 mm (Area = 2.83×10⁻¹ m²)
- Nozzle Length: 800 mm
- Expansion Ratio (ε): 9.0
- Ambient Pressure (pa): 101.3 kPa (sea level)

### Mass Flow Rate Calculation
```
ṁ = (3.0×10⁶ × 3.14×10⁻²) / √(461.5 × 723.15) × √1.33 × (2/2.33)^(2.33/(2×0.33))
ṁ = 73.12 kg/s
```

### Exit Pressure Calculation
For a non-optimally expanded nozzle with expansion ratio 9.0:
```
pe/p0 = (1 + (γ-1)/2 × M²)^(-γ/(γ-1))
```
With exit Mach number of approximately 3.1:
```
pe = 0.0175 × p0 = 52.5 kPa
```

### Exhaust Velocity Calculation
```
ve = √[2×1.33×461.5×723.15/0.33 × (1-(52.5×10³/3.0×10⁶)^(0.33/1.33))]
ve = 873 m/s
```

### Thrust Calculation
```
F = 73.12 × 1232 + (167000 - 101300) × 2.83×10⁻¹
F = 90026 + 18593 = 108619 N (approximately 24,419 lbf)
```

### Specific Impulse
```
Isp = 108619 / (73.12 × 9.81) = 153 seconds
```

## Second Stage Calculations

### Input Parameters
- Chamber Pressure (p0): 2.0 MPa
- Chamber Temperature (T0): 673.15 K (400°C)
- Throat Diameter: 120 mm (Area = 1.13×10⁻² m²)
- Exit Diameter: 480 mm (Area = 1.81×10⁻¹ m²)
- Nozzle Length: 600 mm
- Expansion Ratio (ε): 16.0
- Ambient Pressure (pa): 10 kPa (approximate pressure at altitude)

### Mass Flow Rate Calculation
```
ṁ = (2.0×10⁶ × 1.13×10⁻²) / √(461.5 × 673.15) × √1.33 × (2/2.33)^(2.33/(2×0.33))
ṁ = 0.61 kg/s
```

### Exhaust Velocity Calculation (in vacuum)
```
ve = √[2×1.33×461.5×673.15/0.33 × (1-0)]
ve = 1283 m/s
```

### Thrust Calculation (in altitude)
```math
F = ṁ × v_e + (p_e - p_a) × A_e
F = 30.6 × 1283 + (12000 - 10000) × 1.81×10⁻¹
F = 39259 + 362 = 39621 N (approximately 8,909 lbf)
```

### Specific Impulse
```math
Isp = 39621 / (30.6 × 9.81) = 132 seconds
```

## Propellant Requirements

### First Stage
- Burn time: 30 seconds
- Mass flow rate: 73.12 kg/s
- Total propellant mass: 73.12 × 30 = 2193.6 kg
- Tank volume (liquid water at 20°C): 2193.6 / 1000 = 2.1936 m³ = 2193.6 liters
- Tank volume with 30% ullage: 2851.7 liters (2.85 m³)

### Second Stage
- Burn time: 60 seconds
- Mass flow rate: 30.6 kg/s
- Total propellant mass: 30.6 × 60 = 1836 kg
- Tank volume (liquid water at 20°C): 1836 / 1000 = 1.836 m³ = 1836 liters
- Tank volume with 30% ullage: 2386.8 liters (2.39 m³)

### Total Propellant Requirements

- Total Propellant Mass: 2193.6 + 1836 = 4029.6 kg
- Total Water Volume: 2193.6 + 1836 = 4029.6 liters (4.03 m³)
- Total Vessel Volume with Ullage: 2851.7 + 2386.8 = 5238.5 liters (5.24 m³)

## System Efficiency Analysis

### Thermal Efficiency
- Energy Content of Heated Water: 2.76 MJ/kg
- Energy Converted to Kinetic Energy: 0.38 MJ/kg
- Thermal Efficiency: 13.8%

### Propulsive Efficiency
- First Stage: 86% (slightly under-expanded at sea level)
- Second Stage: 95% (optimal expansion in vacuum)

### Performance Comparison with Other Propellants

| Propellant System    | Specific Impulse (s) | Density (kg/m³) | Toxicity | Complexity | Cost |
|----------------------|---------------------|-----------------|----------|------------|------|
| Water Steam (This Design) | 74-102        | 997             | None     | Low        | Low  |
| Hydrazine Monopropellant | 220-230       | 1010            | High     | Medium     | High |
| Liquid O₂/Kerosene   | 300-340           | 1030            | Low      | High       | Medium |
| Solid Motor          | 250-270           | 1800            | Medium   | Low        | Medium |

### Optimization Opportunities

1. **Increased Chamber Temperature**
   - Current: 450°C (first stage)
   - Potential: Up to 550°C
   - Required: Higher-grade materials
   - Benefit: ~12% increase in specific impulse

2. **Increased Chamber Pressure**
   - Current: 3.0 MPa (first stage)
   - Potential: Up to 5.0 MPa
   - Required: Thicker pressure vessel walls
   - Benefit: ~8% increase in thrust

3. **Improved Nozzle Design**
   - Current: Conical nozzle
   - Potential: Bell-shaped nozzle
   - Required: More complex manufacturing
   - Benefit: ~5% increase in efficiency

## Mission Performance

### First Stage
- Initial Mass: 840 kg (full vehicle)
- Burnout Mass: 719.5 kg (after first stage propellant depletion)
- Thrust: 1068 N
- Thrust-to-Weight Ratio at Liftoff: 1.30
- Maximum Acceleration: 1.48g (end of first stage burn)
- Burn Time: 82 seconds
- Altitude at Stage Separation: 5.8 km
- Velocity at Stage Separation: 187 m/s

### Second Stage
- Initial Mass: 160 kg (second stage + payload)
- Final Mass: 95.2 kg (after propellant depletion)
- Thrust: 481 N
- Initial Thrust-to-Weight Ratio: 3.07
- Maximum Acceleration: 5.16g (end of second stage burn)
- Burn Time: 135 seconds
- Maximum Altitude: 83.2 km
- Maximum Velocity: 1015 m/s

### Overall Mission Analysis
- Total Propellant: 185.3 kg water
- Total Impulse: 153 kN·s
- Maximum Payload to 80 km: 15 kg
- Energy Efficiency: 13.8%
- Cost per Launch: Extremely low compared to chemical propellants
