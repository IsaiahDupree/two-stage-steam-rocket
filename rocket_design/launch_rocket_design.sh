#!/bin/bash
# Rocket Design Automation Launcher (Cross-platform)
# Uses Python 3.11 virtual environment specifically for FreeCAD compatibility

echo "---------------------------------------------"
echo "Rocket Design Automation with FreeCAD"
echo "---------------------------------------------"

# Set environment variables based on platform
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
VENV_PATH="${SCRIPT_DIR}/freecad_venv"
AUTOMATION_SCRIPT="${SCRIPT_DIR}/rocket_csv_automation.py"

# Detect operating system
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    FREECAD_PATH="/Applications/FreeCAD.app/Contents"
    if [[ -d "$FREECAD_PATH" ]]; then
        echo "Found FreeCAD at: $FREECAD_PATH"
    else
        echo "Warning: FreeCAD not found at standard location"
        echo "Searching for FreeCAD..."
        FREECAD_PATH=$(find /Applications -name "FreeCAD*.app" -type d -maxdepth 1 | head -n 1)
        if [[ -d "$FREECAD_PATH" ]]; then
            FREECAD_PATH="${FREECAD_PATH}/Contents"
            echo "Found FreeCAD at: $FREECAD_PATH"
        else
            echo "FreeCAD not found. Please install FreeCAD first."
            exit 1
        fi
    fi
    
    # Find Python 3.11 on Mac
    if [[ -x "/usr/local/bin/python3.11" ]]; then
        PYTHON311_PATH="/usr/local/bin/python3.11"
    elif [[ -x "/usr/bin/python3.11" ]]; then
        PYTHON311_PATH="/usr/bin/python3.11"
    elif [[ -x "/opt/homebrew/bin/python3.11" ]]; then
        PYTHON311_PATH="/opt/homebrew/bin/python3.11"
    else
        echo "Python 3.11 not found. Please install Python 3.11 first."
        exit 1
    fi
elif [[ "$OSTYPE" == "msys" || "$OSTYPE" == "cygwin" || "$OSTYPE" == "win32" ]]; then
    # Windows (Git Bash/Cygwin/MSYS)
    FREECAD_PATH="C:/Program Files/FreeCAD 1.0"
    PYTHON311_PATH="C:/Users/Isaia/AppData/Local/Programs/Python/Python311/python.exe"
    
    # Convert paths to Windows format for the Python executable
    VENV_PATH=$(cygpath -w "$VENV_PATH" 2>/dev/null || echo "$VENV_PATH")
    SCRIPT_DIR=$(cygpath -w "$SCRIPT_DIR" 2>/dev/null || echo "$SCRIPT_DIR")
    AUTOMATION_SCRIPT=$(cygpath -w "$AUTOMATION_SCRIPT" 2>/dev/null || echo "$AUTOMATION_SCRIPT")
else
    # Linux
    FREECAD_PATH="/usr/lib/freecad"
    if [[ ! -d "$FREECAD_PATH" ]]; then
        FREECAD_PATH="/usr/local/lib/freecad"
    fi
    
    # Find Python 3.11 on Linux
    if [[ -x "/usr/bin/python3.11" ]]; then
        PYTHON311_PATH="/usr/bin/python3.11"
    else
        echo "Python 3.11 not found. Please install Python 3.11 first."
        exit 1
    fi
fi

# Set Python executable path based on virtual environment
if [[ "$OSTYPE" == "darwin"* || "$OSTYPE" == "linux"* ]]; then
    PYTHON_EXE="${VENV_PATH}/bin/python"
else
    # Windows
    PYTHON_EXE="${VENV_PATH}/Scripts/python.exe"
fi

# Verify environment exists
if [[ ! -d "$VENV_PATH" ]]; then
    echo "Error: Virtual environment not found at $VENV_PATH"
    echo "Creating virtual environment with Python 3.11..."
    "$PYTHON311_PATH" -m venv "$VENV_PATH"
    if [[ $? -ne 0 ]]; then
        echo "Failed to create virtual environment. Please check Python 3.11 installation."
        exit 1
    fi
fi

# Add FreeCAD to Python path if not already done
if [[ ! -f "${VENV_PATH}/freecad_path_added.txt" ]]; then
    echo "Setting up FreeCAD paths in virtual environment..."
    
    # Create the site-packages directory if it doesn't exist
    if [[ ! -d "${VENV_PATH}/lib/site-packages" && "$OSTYPE" == "darwin"* ]]; then
        mkdir -p "${VENV_PATH}/lib/python3.11/site-packages"
    elif [[ ! -d "${VENV_PATH}/lib/site-packages" && "$OSTYPE" == "linux"* ]]; then
        mkdir -p "${VENV_PATH}/lib/python3.11/site-packages"
    elif [[ ! -d "${VENV_PATH}/Lib/site-packages" ]]; then
        mkdir -p "${VENV_PATH}/Lib/site-packages"
    fi
    
    # Create .pth files to add FreeCAD to the Python path
    if [[ "$OSTYPE" == "darwin"* || "$OSTYPE" == "linux"* ]]; then
        SITE_PACKAGES="${VENV_PATH}/lib/python3.11/site-packages"
        echo "$FREECAD_PATH/Resources/lib" > "${SITE_PACKAGES}/freecad.pth"
        echo "$FREECAD_PATH/MacOS" >> "${SITE_PACKAGES}/freecad.pth"
        echo "$FREECAD_PATH/Mod" > "${SITE_PACKAGES}/freecad_mod.pth"
        echo "$FREECAD_PATH/Ext" > "${SITE_PACKAGES}/freecad_ext.pth"
    else
        # Windows
        SITE_PACKAGES="${VENV_PATH}/Lib/site-packages"
        echo "$FREECAD_PATH/bin" > "${SITE_PACKAGES}/freecad.pth"
        echo "$FREECAD_PATH/Mod" > "${SITE_PACKAGES}/freecad_mod.pth"
        echo "$FREECAD_PATH/Ext" > "${SITE_PACKAGES}/freecad_ext.pth"
    fi
    
    # Create a flag file to indicate FreeCAD paths have been added
    echo "FreeCAD paths added on $(date)" > "${VENV_PATH}/freecad_path_added.txt"
fi

# Install required packages if not already done
if [[ ! -f "${VENV_PATH}/packages_installed.txt" ]]; then
    echo "Installing required packages..."
    "$PYTHON_EXE" -m pip install pandas
    if [[ $? -ne 0 ]]; then
        echo "Failed to install required packages."
        exit 1
    fi
    
    # Create a flag file to indicate packages have been installed
    echo "Packages installed on $(date)" > "${VENV_PATH}/packages_installed.txt"
fi

# Get the input CSV file
CSV_FILE="$1"
if [[ -z "$CSV_FILE" ]]; then
    CSV_FILE="${SCRIPT_DIR}/rocket_specs.csv"
    echo "No CSV file specified, using default: $CSV_FILE"
fi

# Run the automation script
echo "Running Rocket Design Automation..."
echo "Using Python: $PYTHON_EXE"
echo "Using script: $AUTOMATION_SCRIPT"
echo "Input CSV: $CSV_FILE"
echo ""

"$PYTHON_EXE" "$AUTOMATION_SCRIPT" "$CSV_FILE"
if [[ $? -ne 0 ]]; then
    echo ""
    echo "Rocket Design Automation failed. See log for details."
    exit 1
else
    echo ""
    echo "Rocket Design Automation completed successfully!"
fi

exit 0
