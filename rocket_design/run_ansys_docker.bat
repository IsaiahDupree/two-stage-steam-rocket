@echo off
echo Ansys Geometry Docker Container Management
echo =========================================
echo.

REM Check Python installation
python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Error: Python is not installed or not in PATH
    pause
    exit /b 1
)

:menu
cls
echo Ansys Geometry Docker Container Management
echo =========================================
echo.
echo Select an operation:
echo 1. Start Ansys Geometry container
echo 2. Stop container
echo 3. View container logs
echo 4. Test connection
echo 5. Restart container
echo 6. Exit
echo.

set /p choice=Enter your choice (1-6): 

if "%choice%"=="1" (
    echo.
    echo Starting Ansys Geometry container...
    python setup_ansys_docker.py --action start --license-server localhost:1084
    pause
    goto menu
)

if "%choice%"=="2" (
    echo.
    echo Stopping Ansys Geometry container...
    python setup_ansys_docker.py --action stop
    pause
    goto menu
)

if "%choice%"=="3" (
    echo.
    echo Viewing container logs...
    python setup_ansys_docker.py --action logs
    pause
    goto menu
)

if "%choice%"=="4" (
    echo.
    echo Testing connection to Ansys Geometry service...
    python setup_ansys_docker.py --action test
    pause
    goto menu
)

if "%choice%"=="5" (
    echo.
    echo Restarting Ansys Geometry container...
    python setup_ansys_docker.py --action restart --license-server localhost:1084
    pause
    goto menu
)

if "%choice%"=="6" (
    exit /b 0
)

echo Invalid choice. Please try again.
pause
goto menu
