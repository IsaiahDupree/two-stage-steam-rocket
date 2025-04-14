@echo off
echo Creating Two-Stage Rocket 3D Model...
echo.

REM Set FreeCAD path
set FREECAD_CMD="C:\Program Files\FreeCAD 1.0\bin\freecadcmd.exe"

REM Check if FreeCAD exists
if not exist %FREECAD_CMD% (
    echo ERROR: FreeCAD command-line tool not found at %FREECAD_CMD%
    echo Please install FreeCAD or update the path in this batch file.
    pause
    exit /b 1
)

REM Set Python script path
set SCRIPT_PATH="%~dp0create_rocket_model.py"

REM Check if script exists
if not exist %SCRIPT_PATH% (
    echo ERROR: Script not found at %SCRIPT_PATH%
    pause
    exit /b 1
)

REM Create output directories if they don't exist
if not exist "%~dp0output" mkdir "%~dp0output"
if not exist "%~dp0output\models" mkdir "%~dp0output\models"

echo Running FreeCAD to create the rocket 3D model...
echo This may take a few moments to complete.
echo.

%FREECAD_CMD% %SCRIPT_PATH%

echo.
echo Script execution completed.
echo Check the output\models directory for the generated 3D files.
pause
