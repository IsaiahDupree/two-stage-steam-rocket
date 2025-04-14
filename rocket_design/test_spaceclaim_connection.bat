@echo off
echo Ansys Geometry Service - SpaceClaim Connection Test
echo ================================================
echo.
echo This script will attempt to connect to the Ansys Geometry service
echo through SpaceClaim using the Ansys license server on Orion.
echo.

REM Set license server environment variable
set ANSRV_GEO_LICENSE_SERVER=Orion:49768

echo License server: %ANSRV_GEO_LICENSE_SERVER%
echo.
echo Running connection test...
echo.

python simple_ansys_connection_test.py --no-docker --spaceclaim

echo.
if %ERRORLEVEL% EQU 0 (
    echo SUCCESS: Connection test completed successfully.
) else (
    echo WARNING: Connection test encountered issues.
    echo Check the output above for details.
)

echo.
pause
