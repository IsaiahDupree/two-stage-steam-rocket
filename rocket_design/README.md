# Two-Stage Space Vehicle Design Project

This project uses FreeCAD's Python API to design and analyze a two-stage rocket with steam-based propulsion system.

## 🚀 NEW: CSV-Driven Rocket Design Automation

A cross-platform tool for rocket design automation using FreeCAD's Python API has been added to the project. This application allows for rapid creation of rocket components and assemblies from CSV specifications.

### Key Features

- **CSV-Driven Design**: Define rocket components in a simple CSV format
- **Component Library**: Support for nosecones, body tubes, fins, and more
- **Automatic Assembly**: Positions components correctly in the assembly
- **Multi-Format Export**: Export to FCStd, STEP, and STL formats
- **Cross-Platform**: Works on Windows, Mac, and Linux
- **Isolated Environment**: Uses dedicated Python virtual environment with version 3.11

## Project Structure


- `src/` - Python source code for the FreeCAD models and engineering calculations
- `data/` - Input data, parameters, and configuration files
- `output/` - Generated CAD models, reports, and calculation results


## Requirements

- FreeCAD (0.19, 0.20, or 1.0)
- Python 3.7+
- NumPy and SciPy for engineering calculations
- Matplotlib for visualization

## Getting Started

1. Install FreeCAD from [https://www.freecadweb.org/](https://www.freecadweb.org/)
2. Clone this repository
3. Run the project using one of the following methods:

### Method 1: Using the batch files (Windows)

The simplest method is to use the provided batch files:

```batch
run_with_freecadcmd.bat
```

This script will:
- Locate your FreeCAD installation
- Test the FreeCAD API configuration
- Run the main rocket design script
- Generate all output files in the output directory

### Method 2: Manual execution with FreeCAD

You can also run the script from the FreeCAD Python console:

1. Open FreeCAD
2. Go to View → Panels → Python Console
3. In the console, run:

```python
import sys
sys.path.append(r"path/to/rocket_design/src")
exec(open(r"path/to/rocket_design/src/main.py").read())
```

### Method 3: Command-line execution

Run directly with freecadcmd (FreeCAD's command-line tool):

```bash
# Windows
"C:\Program Files\FreeCAD VERSION\bin\freecadcmd.exe" path/to/src/main.py

# macOS
/Applications/FreeCAD.app/Contents/MacOS/FreeCAD path/to/src/main.py

# Linux
freecadcmd path/to/src/main.py
```

## Features


1. **Two-Stage Space Vehicle Design**
   - 3D model generation of the complete rocket
   - Stage separation mechanism
   - Structural components


2. **Rocket Engine Pressure Design**
   - Pressure vessel calculations
   - Nozzle geometry optimization
   - Material stress analysis

3. **Steam Rocket Thrust Analysis**
   - Propellant mass calculations
   - Thrust estimation
   - Burn duration simulation

## Outputs

- 3D models in STEP and STL formats
- Engineering analysis reports in PDF
- Calculation spreadsheets with formulas and assumptions

## Troubleshooting

If you encounter issues with the FreeCAD Python API, try running the test script:

```bash
freecadcmd test_freecad_api.py
```

Common issues include:

- Incorrect path to FreeCAD binaries
- Missing dependencies
- Version mismatches between Python and FreeCAD

Refer to the FreeCAD documentation for more details on Python scripting with FreeCAD.

## CSV Rocket Automation

### Quick Start

Windows:
```bash
launch_rocket_design.bat [path/to/specs.csv]
```

Mac/Linux:
```bash
./launch_rocket_design.sh [path/to/specs.csv]
```

If no CSV file is specified, the default `rocket_specs.csv` will be used.

### CSV Format

Create a CSV file with the following columns:

| Column | Description |
|--------|-------------|
| name | Component name |
| type | Component type (cone, tube, cylinder, fins) |
| length | Length in mm |
| diameter | Diameter in mm |
| thickness | Wall thickness in mm (for tubes) |
| material | Optional material specification |
| comments | Optional notes |

For fins, additional parameters are available:

- height: Fin height from rocket body
- width: Fin thickness
- count: Number of fins (default: 3)


### Example CSV


```csv
name,type,length,diameter,thickness,material,comments
Nosecone,cone,150,50,2,aluminum,Aerodynamic nosecone
Main Body,tube,300,50,2,composite,Primary structure
Fins,fins,80,60,3,carbon fiber,Stabilizing fins (count=4)
```


### Output Files

Generated files are saved in the `output` directory:

- `.FCStd`: Native FreeCAD file
- `.step`: STEP format for CAD interchange
- `.stl`: STL format for 3D printing

### Environment Management

The launcher scripts automatically:

1. Create a dedicated Python 3.11 virtual environment
2. Configure FreeCAD paths
3. Install required dependencies
4. Run the automation with proper Python version

### Report Generation

To generate a comprehensive report from the markdown files:

1. Install the required Python packages:
   ```bash
   pip install python-docx markdown2 pywin32
   ```

2. Run the compilation script:
   ```bash
   python compile_report.py
   ```

This will generate:
- `Rocket_Design_Report.docx` - Complete Word document with all sections
- `Rocket_Design_Report.pdf` - PDF version (if Word is installed)

### Troubleshooting CSV Automation

#### FreeCAD Not Found

Ensure FreeCAD is installed in the standard location:

- Windows: `C:\Program Files\FreeCAD 1.0`
- Mac: `/Applications/FreeCAD.app`
- Linux: `/usr/lib/freecad`

Or update the path in the launcher script.

#### Python Version Conflict

The launcher automatically uses Python 3.11. If you encounter issues:

1. Ensure Python 3.11 is installed
2. Check the compatibility between your FreeCAD version and Python

#### Detailed Logs

Check the `rocket_automation.log` file for detailed output and debugging information.
