@echo off
echo Running Steam Rocket Model in FreeCAD...

:: Path to your FreeCAD installation - adjust if needed
set FREECAD_PATH=C:\Program Files\FreeCAD 1.0
set FREECAD_BIN=%FREECAD_PATH%\bin

if not exist "%FREECAD_BIN%\FreeCAD.exe" (
  echo FreeCAD not found at %FREECAD_PATH%
  echo Please install FreeCAD or adjust the FREECAD_PATH in this script.
  exit /b 1
)

set MACRO_PATH=%~dp0SteamRocketMacro.FCMacro

echo Executing macro: %MACRO_PATH%
echo Using FreeCAD from: %FREECAD_PATH%

:: Launch FreeCAD with the macro
"%FREECAD_BIN%\FreeCAD.exe" "%MACRO_PATH%"

echo.
echo When FreeCAD opens:
echo 1. The macro should run automatically
echo 2. Output files will be saved to: %~dp0output\models
echo 3. You can explore the 3D model in the FreeCAD interface

exit /b 0
