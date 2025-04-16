# Two-Stage Steam Rocket Design - AI-Enhanced

## Project Overview
This repository contains a comprehensive AI-powered rocket design system along with engineering documentation and 3D models for a two-stage steam-powered rocket. The design includes detailed specifications, calculations, and 3D models created with FreeCAD, plus an advanced AI assistant that can analyze, optimize, and modify rocket designs based on natural language prompts.


## Contents

### AI-Powered Design System
- **Web Application Interface**
  - Interactive 3D model viewer
  - AI chat interface for design modifications
  - STEP file interpretation and analysis
  - Performance optimization tools


### Documentation

- **Engineering Reports**
  - Detailed vehicle configuration and structural design
  - Comprehensive pressure vessel design specifications
  - Thrust and performance calculations
  - AI-generated design analysis and recommendations


### 3D Models

- Complete two-stage rocket design
- FreeCAD native format (.FCStd)
- STEP format for CAD interoperability
- STL format for 3D printing and visualization

### Technical Specifications

#### First Stage

- Length: 7.2 meters
- Diameter: 1.2 meters
- Pressure Vessel: 3.0m length, 900mm diameter, 16mm wall thickness
- Nozzle: 200mm throat, 600mm exit diameter, 800mm length
- Thrust: 108,619 N (24,419 lbf)
- Specific Impulse: 153 seconds


#### Second Stage

- Length: 5.2 meters
- Diameter: 0.8 meters
- Pressure Vessel: 1.8m length, 600mm diameter, 3mm wall thickness
- Nozzle: 120mm throat, 480mm exit diameter, 600mm length
- Thrust: 39,621 N (8,909 lbf)
- Specific Impulse: 132 seconds


## System Components

### AI Services
- **AI Controller** - Central integration of all AI capabilities
- **STEP Interpreter** - AI-powered analysis of 3D model geometry
- **Design Optimizer** - Multi-parameter optimization using AI
- **Visual Analyzer** - Generates engineering visualizations and comparisons


### Web Application

- **Flask Backend** - API endpoints for AI design services
- **Interactive Frontend** - 3D visualization and AI chat interface
- **Design Parameter Controls** - Real-time modification of design parameters


### Testing Framework

- **Human Interaction Tests** - Verification of AI understanding of design requests
- **Design Verification** - Validation of correctly implemented design changes
- **Performance Analysis** - Verification of engineering calculations


### Scripts

- `compile_report.py` - Converts markdown documentation to Word/PDF formats
- `SteamRocketMacro.FCMacro` - FreeCAD macro for generating the 3D rocket model


## Usage

### AI Design System
1. Run the Flask web application: `python rocket_design/nx_rocket_portfolio/app/app.py`
2. Open a web browser and navigate to: `http://localhost:5000/ai-designer`
3. Upload a STEP file or start with the sample model
4. Use natural language to request design changes such as:
   - "Increase the first stage diameter to 1.5 meters"
   - "Optimize for maximum altitude with a 50kg payload"
   - "Switch to carbon fiber for the first stage to reduce weight"


### Traditional Tools

1. Open the documentation in the `/rocket_design/` directory for technical specifications
2. Run `python compile_report.py` to generate the full technical report in Word/PDF format
3. Open `SteamRocketMacro.FCMacro` in FreeCAD to view or modify the 3D model


### Testing Framework

1. Run basic design tests: `python nx_rocket_portfolio/tests/run_simple_design_test.py`
2. Run comprehensive test suite: `python nx_rocket_portfolio/tests/run_design_tests.py`


## Key Technologies

- OpenAI API integration for intelligent design assistance
- Flask web framework for the application backend
- Three.js for interactive 3D visualization
- Python for engineering calculations and AI service integration
- Matplotlib for engineering visualization generation


## License

MIT License - See LICENSE file for details
