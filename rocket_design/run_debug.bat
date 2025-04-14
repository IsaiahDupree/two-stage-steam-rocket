@echo off
echo Running FreeCAD Debug Script...
echo.

REM Set FreeCAD path
set FREECAD_PATH="C:\Program Files\FreeCAD 1.0\bin"

REM Check if FreeCAD exists
if not exist %FREECAD_PATH%\FreeCAD.exe (
    echo ERROR: FreeCAD not found at %FREECAD_PATH%
    echo Please install FreeCAD or update the path in this batch file.
    pause
    exit /b 1
)

REM Set Python script path
set SCRIPT_PATH="%~dp0debug_freecad.py"

REM Check if script exists
if not exist %SCRIPT_PATH% (
    echo ERROR: Script not found at %SCRIPT_PATH%
    pause
    exit /b 1
)

echo Running FreeCAD with the debug script...
echo.

REM Run FreeCAD with the script
%FREECAD_PATH%\FreeCAD.exe --console --run %SCRIPT_PATH%

echo.
echo Script execution completed.
echo Check debug_log.txt for details.
pause
