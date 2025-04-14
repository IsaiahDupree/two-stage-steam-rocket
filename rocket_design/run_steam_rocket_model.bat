@echo off
echo Running Steam Rocket Model Generator with FreeCAD...

:: Path to your FreeCAD installation - adjust if needed
set FREECAD_PATH=C:\Program Files\FreeCAD 1.0
set FREECAD_BIN=%FREECAD_PATH%\bin

if not exist "%FREECAD_BIN%\FreeCAD.exe" (
  echo FreeCAD not found at %FREECAD_PATH%
  echo Please adjust the FREECAD_PATH in this script.
  exit /b 1
)

:: Create a temporary Python script to run
set TEMP_SCRIPT=%TEMP%\steam_rocket_temp.py

echo import sys > "%TEMP_SCRIPT%"
echo sys.path.append(r"%~dp0") >> "%TEMP_SCRIPT%"
echo import steam_rocket_model >> "%TEMP_SCRIPT%"
echo steam_rocket_model.main() >> "%TEMP_SCRIPT%"

:: Run the script with FreeCAD's Python interpreter
echo Using FreeCAD from: %FREECAD_PATH%
echo Running through temporary script: %TEMP_SCRIPT%

"%FREECAD_BIN%\FreeCADCmd.exe" "%TEMP_SCRIPT%"

if %ERRORLEVEL% NEQ 0 (
  echo Failed to run the model generator.
  exit /b %ERRORLEVEL%
)

del "%TEMP_SCRIPT%"

echo Model generation complete!
echo Files are located in: %~dp0\output\models
