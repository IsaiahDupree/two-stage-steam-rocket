@echo off
:: Rocket Design Automation Launcher
:: Uses Python 3.11 virtual environment specifically for FreeCAD compatibility
:: Created: %date% 

echo ---------------------------------------------
echo Rocket Design Automation with FreeCAD
echo ---------------------------------------------

:: Set environment variables
set SCRIPT_DIR=%~dp0
set VENV_PATH=%SCRIPT_DIR%freecad_venv
set FREECAD_PATH=C:\Program Files\FreeCAD 1.0
set PYTHON_EXE=%VENV_PATH%\Scripts\python.exe
set AUTOMATION_SCRIPT=%SCRIPT_DIR%rocket_csv_automation.py

:: Verify environment exists
if not exist "%VENV_PATH%" (
  echo Error: Virtual environment not found at %VENV_PATH%
  echo Creating virtual environment with Python 3.11...
  "C:\Users\Isaia\AppData\Local\Programs\Python\Python311\python.exe" -m venv "%VENV_PATH%"
  if ERRORLEVEL 1 (
    echo Failed to create virtual environment. Please check Python 3.11 installation.
    exit /b 1
  )
)

:: Add FreeCAD to Python path if not already done
if not exist "%VENV_PATH%\freecad_path_added.txt" (
  echo Setting up FreeCAD paths in virtual environment...
  
  :: Create the site-packages directory if it doesn't exist
  if not exist "%VENV_PATH%\Lib\site-packages" (
    mkdir "%VENV_PATH%\Lib\site-packages"
  )
  
  :: Create a .pth file to add FreeCAD to the Python path
  echo %FREECAD_PATH%\bin > "%VENV_PATH%\Lib\site-packages\freecad.pth"
  echo %FREECAD_PATH%\Mod > "%VENV_PATH%\Lib\site-packages\freecad_mod.pth"
  echo %FREECAD_PATH%\Ext > "%VENV_PATH%\Lib\site-packages\freecad_ext.pth"
  
  :: Create a flag file to indicate FreeCAD paths have been added
  echo FreeCAD paths added on %date% > "%VENV_PATH%\freecad_path_added.txt"
)

:: Install required packages if not already done
if not exist "%VENV_PATH%\packages_installed.txt" (
  echo Installing required packages...
  "%PYTHON_EXE%" -m pip install pandas
  if ERRORLEVEL 1 (
    echo Failed to install required packages.
    exit /b 1
  )
  
  :: Create a flag file to indicate packages have been installed
  echo Packages installed on %date% > "%VENV_PATH%\packages_installed.txt"
)

:: Get the input CSV file
set CSV_FILE=%1
if "%CSV_FILE%"=="" (
  set CSV_FILE=%SCRIPT_DIR%rocket_specs.csv
  echo No CSV file specified, using default: %CSV_FILE%
)

:: Run the automation script
echo Running Rocket Design Automation...
echo Using Python: %PYTHON_EXE%
echo Using script: %AUTOMATION_SCRIPT%
echo Input CSV: %CSV_FILE%
echo.

"%PYTHON_EXE%" "%AUTOMATION_SCRIPT%" "%CSV_FILE%"
if ERRORLEVEL 1 (
  echo.
  echo Rocket Design Automation failed. See log for details.
  exit /b 1
) else (
  echo.
  echo Rocket Design Automation completed successfully!
)

exit /b 0
