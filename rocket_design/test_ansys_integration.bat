@echo off
echo Running Ansys Geometry Integration Test...
echo.

REM Set Python environment
set PYTHONPATH=%~dp0src;%PYTHONPATH%

REM Ensure output directories exist
if not exist "%~dp0output" mkdir "%~dp0output"
if not exist "%~dp0output\ansys_test" mkdir "%~dp0output\ansys_test"
if not exist "%~dp0output\reports" mkdir "%~dp0output\reports"

REM Run the test script
python "%~dp0test_ansys_integration.py"

echo.
echo Test completed.
pause
