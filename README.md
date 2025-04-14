# Two-Stage Steam Rocket Design

## Project Overview
This repository contains comprehensive engineering design documentation and 3D models for a two-stage steam-powered rocket. The design includes detailed specifications, calculations, and 3D models created with FreeCAD.

## Contents

### Documentation
- **Engineering Reports**
  - Detailed vehicle configuration and structural design
  - Comprehensive pressure vessel design specifications
  - Thrust and performance calculations

### 3D Models
- Complete two-stage rocket design
- FreeCAD native format (.FCStd)
- STEP format for CAD interoperability
- STL format for 3D printing and visualization

### Technical Specifications

**First Stage**
- Length: 7.2 meters
- Diameter: 1.2 meters
- Pressure Vessel: 3.0m length, 900mm diameter, 16mm wall thickness
- Nozzle: 200mm throat, 600mm exit diameter, 800mm length
- Thrust: 108,619 N (24,419 lbf)
- Specific Impulse: 153 seconds

**Second Stage**
- Length: 5.2 meters
- Diameter: 0.8 meters
- Pressure Vessel: 1.8m length, 600mm diameter, 3mm wall thickness
- Nozzle: 120mm throat, 480mm exit diameter, 600mm length
- Thrust: 39,621 N (8,909 lbf)
- Specific Impulse: 132 seconds

## Scripts
- `compile_report.py` - Converts markdown documentation to Word/PDF formats
- `SteamRocketMacro.FCMacro` - FreeCAD macro for generating the 3D rocket model

## Usage
1. Open the documentation in the `/rocket_design/` directory for technical specifications
2. Run `python compile_report.py` to generate the full technical report in Word/PDF format
3. Open `SteamRocketMacro.FCMacro` in FreeCAD to view or modify the 3D rocket model

## License
MIT License - See LICENSE file for details
