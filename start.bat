@echo off
setlocal
chcp 65001 >nul
cd /d "%~dp0"
title LoopNote

set "PY_CMD="
where py >nul 2>nul
if not errorlevel 1 (
  py -3 -c "import sys; raise SystemExit(0 if sys.version_info >= (3, 11) else 1)" >nul 2>nul
  if not errorlevel 1 set "PY_CMD=py -3"
)

if not defined PY_CMD (
  where python >nul 2>nul
  if not errorlevel 1 (
    python -c "import sys; raise SystemExit(0 if sys.version_info >= (3, 11) else 1)" >nul 2>nul
    if not errorlevel 1 set "PY_CMD=python"
  )
)

if not defined PY_CMD (
  where python3 >nul 2>nul
  if not errorlevel 1 (
    python3 -c "import sys; raise SystemExit(0 if sys.version_info >= (3, 11) else 1)" >nul 2>nul
    if not errorlevel 1 set "PY_CMD=python3"
  )
)

if not exist ".venv\Scripts\python.exe" (
  if not defined PY_CMD goto :python_missing
  echo [First setup] Creating the Python environment...
  %PY_CMD% -m venv .venv
  if errorlevel 1 goto :setup_error
)

".venv\Scripts\python.exe" -c "import sys; raise SystemExit(0 if sys.version_info >= (3, 11) else 1)" >nul 2>nul
if errorlevel 1 goto :old_venv

echo Checking required libraries...
".venv\Scripts\python.exe" -m pip install -r requirements.txt
if errorlevel 1 goto :install_error

echo Starting LoopNote...
echo Startup details are saved in startup.log if the app exits unexpectedly.
> startup.log echo LoopNote startup log
".venv\Scripts\python.exe" app.py %* >> startup.log 2>&1
set "APP_EXIT=%errorlevel%"
if "%APP_EXIT%"=="0" goto :eof
echo.
echo The app exited with error code %APP_EXIT%.
echo ----- startup.log -----
type startup.log
echo -----------------------
pause
goto :eof

:python_missing
echo.
echo Python 3.11 or newer was not found.
echo Install 64-bit Python from:
echo https://www.python.org/downloads/windows/
echo During installation, enable "Add python.exe to PATH".
pause
goto :eof

:old_venv
echo.
echo The existing .venv uses Python older than 3.11 or is broken.
echo Rename or remove the .venv folder, then run start.bat again.
pause
goto :eof

:setup_error
echo.
echo Failed to create .venv. Check the Python installation above.
pause
goto :eof

:install_error
echo.
echo Failed to install required libraries.
echo Check the internet connection, then run start.bat again.
pause
goto :eof
