@echo off
echo Running Two-Stage Space Vehicle Design Project...
echo.

REM Set FreeCAD path
set FREECAD_PATH="C:\Program Files\FreeCAD 1.0\bin"
set FREECAD_CMD="C:\Program Files\FreeCAD 1.0\bin\freecadcmd.exe"

REM Check if FreeCAD exists
if not exist %FREECAD_CMD% (
    echo ERROR: FreeCAD command-line tool not found at %FREECAD_CMD%
    echo Please install FreeCAD or update the path in this batch file.
    pause
    exit /b 1
)

REM Set Python script path
set SCRIPT_PATH="%~dp0src\main.py"

REM Check if script exists
if not exist %SCRIPT_PATH% (
    echo ERROR: Script not found at %SCRIPT_PATH%
    pause
    exit /b 1
)

REM Create output directories if they don't exist
if not exist "%~dp0output" mkdir "%~dp0output"
if not exist "%~dp0output\models" mkdir "%~dp0output\models"
if not exist "%~dp0output\reports" mkdir "%~dp0output\reports"
if not exist "%~dp0output\calculations" mkdir "%~dp0output\calculations"
if not exist "%~dp0output\graphs" mkdir "%~dp0output\graphs"

echo Running FreeCAD with the rocket design script...
echo This may take a few minutes to complete.
echo.

%FREECAD_CMD% %SCRIPT_PATH%

echo.
echo Script execution completed.
echo Results saved to the output directory.
pause
