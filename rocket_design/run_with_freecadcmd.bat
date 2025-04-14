@echo off
echo Running Two-Stage Space Vehicle Design Project with freecadcmd...
echo.

REM Search for freecadcmd.exe in common installation locations
set FOUND=0
set SEARCH_PATHS=^
"C:\Program Files\FreeCAD 1.0\bin\freecadcmd.exe" ^
"C:\Program Files\FreeCAD 0.20\bin\freecadcmd.exe" ^
"C:\Program Files\FreeCAD 0.19\bin\freecadcmd.exe" ^
"C:\Program Files\FreeCAD\bin\freecadcmd.exe"

for %%p in (%SEARCH_PATHS%) do (
    if exist %%p (
        echo Found FreeCAD command-line tool: %%p
        set FREECAD_CMD=%%p
        set FOUND=1
        goto FOUND_FREECAD
    )
)

:FOUND_FREECAD
if %FOUND%==0 (
    echo ERROR: Could not find freecadcmd.exe in any of the standard locations.
    echo Please install FreeCAD or manually edit this batch file with the correct path.
    pause
    exit /b 1
)

REM Set script paths
set PROJECT_ROOT=%~dp0
set MAIN_SCRIPT="%PROJECT_ROOT%src\main.py"
set TEST_SCRIPT="%PROJECT_ROOT%test_freecad_api.py"

REM Check for required files
if not exist %MAIN_SCRIPT% (
    echo ERROR: Main script not found at %MAIN_SCRIPT%
    pause
    exit /b 1
)

REM Create output directories if they don't exist
if not exist "%PROJECT_ROOT%output" mkdir "%PROJECT_ROOT%output"
if not exist "%PROJECT_ROOT%output\models" mkdir "%PROJECT_ROOT%output\models"
if not exist "%PROJECT_ROOT%output\reports" mkdir "%PROJECT_ROOT%output\reports"

echo.
echo STEP 1: Testing FreeCAD API configuration...
echo ---------------------------------------
%FREECAD_CMD% %TEST_SCRIPT%

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ERROR: FreeCAD API test failed. Please check your FreeCAD installation.
    pause
    exit /b 1
)

echo.
echo STEP 2: Running main rocket design script...
echo ---------------------------------------
echo This may take a few minutes to complete.
echo.

%FREECAD_CMD% %MAIN_SCRIPT%

echo.
echo Script execution completed.
echo Results should be available in the output directory.
pause
