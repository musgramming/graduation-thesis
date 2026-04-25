@echo off
setlocal enabledelayedexpansion

REM ================================
REM Config
REM ================================
set VENV_NAME=.venv_notebook
set REQUIRED_PYTHON_VERSION=3.12

echo =====================================
echo Kiem tra Python %REQUIRED_PYTHON_VERSION%
echo =====================================

REM Kiem tra python co ton tai khong
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo Python chua duoc cai dat.
    echo Vui long cai Python %REQUIRED_PYTHON_VERSION%^+ tu:
    echo https://www.python.org/downloads/
    pause
    exit /b 1
)

REM Lay version python
for /f "tokens=2 delims= " %%v in ('python --version 2^>^&1') do (
    set PY_VERSION=%%v
)

echo Python hien tai: !PY_VERSION!

REM Kiem tra version co phai 3.12.x khong
echo !PY_VERSION! | findstr /b "3.12." >nul
if %errorlevel% neq 0 (
    echo Python khong phai version 3.12.x
    echo Vui long cai dat dung Python %REQUIRED_PYTHON_VERSION%
    pause
    exit /b 1
)

echo Python hop le.

echo.
echo =====================================
echo Kiem tra virtual environment
echo =====================================

if not exist "%VENV_NAME%\Scripts\activate.bat" (
    echo Chua ton tai %VENV_NAME%, dang tao...

    python -m venv %VENV_NAME%
    if %errorlevel% neq 0 (
        echo Tao virtual environment that bai.
        pause
        exit /b 1
    )

    echo Dang kich hoat venv va cai dependencies...

    call %VENV_NAME%\Scripts\activate.bat

    python -m pip install --upgrade pip

    if exist requirements.txt (
        pip install -r requirements.txt
        if %errorlevel% neq 0 (
            echo Cai dat requirements that bai.
            pause
            exit /b 1
        )
    ) else (
        echo Khong tim thay requirements.txt
    )
) else (
    echo Virtual environment da ton tai.
)

echo.
echo =====================================
echo Kich hoat virtual environment
echo =====================================

call %VENV_NAME%\Scripts\activate.bat

echo.
echo =====================================
echo Mo Jupyter Notebook
echo =====================================

jupyter notebook

pause
endlocal