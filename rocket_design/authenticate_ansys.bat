@echo off
echo Ansys Container Registry Authentication
echo ======================================
echo.
echo This script will help you authenticate with the Ansys container registry (ghcr.io)
echo to enable pulling the Ansys Geometry Docker image.
echo.
echo NOTE: You need valid Ansys credentials to access the registry.
echo If you don't have credentials, contact your Ansys administrator or license manager.
echo.

set /p username=Enter your Ansys Container Registry username: 

echo.
echo Now you will be prompted to enter your password.
echo The password will not be displayed as you type.
echo.
echo When ready, press any key to continue...
pause >nul

echo.
echo Running: docker login ghcr.io -u %username%
docker login ghcr.io -u %username%

echo.
if %ERRORLEVEL% EQU 0 (
    echo SUCCESS: Authentication completed.
    echo You should now be able to pull Ansys Docker images.
    echo.
    echo To start the Ansys Geometry container, run:
    echo python setup_ansys_docker.py --action start
    echo or use the run_ansys_docker.bat menu.
) else (
    echo FAILED: Authentication was not successful.
    echo Please check your credentials and try again.
    echo.
    echo Troubleshooting:
    echo 1. Verify your Ansys license is active
    echo 2. Ensure you have permission to access the container registry
    echo 3. Check your network connection
)

echo.
pause
