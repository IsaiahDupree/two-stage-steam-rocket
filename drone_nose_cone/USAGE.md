# Drone Nose Cone - Usage Guide

This project contains several tools to design and visualize a 3D model for a drone nose cone.

## Setup

1. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

2. Install OpenSCAD (if you want to convert the models to STL):
   - Download from [OpenSCAD.org](https://www.openscad.org/downloads.html)
   - Install following the instructions for your operating system

## Available Tools

### 1. Design Validation

Analyze the design parameters and get weight estimates:


```bash
python models/validate_design.py
```
### 2. Visualization

Generate a 2D cross-section diagram of the nose cone:


```bash
python models/visualize_design.py
```

### 3. 3D Model Generation

#### Option A: Use OpenSCAD directly
Open `models/nose_cone.scad` in OpenSCAD to view and modify the 3D model.


#### Option B: Use Python to generate OpenSCAD files

Run the Python generator script:

```bash
python models/nose_cone_generator.py
```

This will create OpenSCAD files in the `models/output` directory.

## Modifying Parameters

To adjust the design parameters:

1. Edit the constants at the top of any of these files:
   - `models/nose_cone.scad`
   - `models/nose_cone_generator.py`
   - `models/visualize_design.py`
   - `models/validate_design.py`

2. Re-run the appropriate script to update the model.

## Creating STL Files for 3D Printing

1. Open the generated `.scad` file in OpenSCAD
2. Choose Design > Render (F6)
3. Export as STL (File > Export > Export as STL)

## Recommended 3D Print Settings

Based on the validation results:

- **Material**: LW-PLA for minimum weight (or PETG for more strength)
- **Infill**: 15-20% for lightweight design
- **Infill Pattern**: Gyroid or Honeycomb
- **Layer Height**: 0.16-0.2mm
- **Shells**: At least 2-3
- **Orientation**: Print base-down to minimize supports

## Troubleshooting

- If you encounter issues with the Python scripts, ensure you have installed all dependencies from requirements.txt
- If OpenSCAD shows rendering errors, check for non-manifold geometry or try reducing the complexity of the model
- For printing issues, adjust shell thickness or infill percentage for better structural integrity
