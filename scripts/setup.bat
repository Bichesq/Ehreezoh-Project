@echo off
REM Cameroon Traffic App - Quick Setup Script (Windows)
REM This script helps set up the development environment

echo.
echo ========================================
echo Cameroon Traffic App - Development Setup
echo ========================================
echo.

REM Check Node.js
echo Checking prerequisites...
echo.

where node >nul 2>nul
if %errorlevel% equ 0 (
    echo [OK] Node.js installed
    node --version
) else (
    echo [ERROR] Node.js not found
    echo Please install Node.js 18+ from https://nodejs.org/
    pause
    exit /b 1
)

REM Check Python
where python >nul 2>nul
if %errorlevel% equ 0 (
    echo [OK] Python installed
    python --version
) else (
    echo [ERROR] Python not found
    echo Please install Python 3.11+ from https://python.org/
    pause
    exit /b 1
)

REM Check Docker
where docker >nul 2>nul
if %errorlevel% equ 0 (
    echo [OK] Docker installed
    docker --version
) else (
    echo [WARNING] Docker not found
    echo Install Docker Desktop from https://docker.com/
)

REM Check Git
where git >nul 2>nul
if %errorlevel% equ 0 (
    echo [OK] Git installed
    git --version
) else (
    echo [ERROR] Git not found
    echo Please install Git from https://git-scm.com/
    pause
    exit /b 1
)

echo.
echo Setting up project...
echo.

REM Backend setup
echo Setting up backend...
cd backend

REM Create virtual environment
if not exist "venv" (
    echo Creating Python virtual environment...
    python -m venv venv
    echo [OK] Virtual environment created
) else (
    echo [OK] Virtual environment already exists
)

REM Activate virtual environment and install dependencies
echo Installing Python dependencies...
call venv\Scripts\activate.bat
pip install -r requirements.txt
echo [OK] Python dependencies installed

REM Create .env file
if not exist ".env" (
    echo Creating .env file from template...
    copy .env.example .env
    echo [OK] .env file created - Please edit it with your configuration
) else (
    echo [OK] .env file already exists
)

cd ..

REM Mobile setup
echo.
echo Setting up mobile app...
cd mobile

REM Install Node dependencies
if not exist "node_modules" (
    echo Installing Node.js dependencies (this may take a few minutes)...
    call npm install
    echo [OK] Node.js dependencies installed
) else (
    echo [OK] Node.js dependencies already installed
)

REM Create .env file
if not exist ".env" (
    echo Creating .env file from template...
    copy .env.example .env
    echo [OK] .env file created - Please edit it with your configuration
) else (
    echo [OK] .env file already exists
)

cd ..

REM Docker setup
echo.
echo Setting up Docker services...

where docker-compose >nul 2>nul
if %errorlevel% equ 0 (
    echo Starting PostgreSQL and Redis...
    docker-compose up -d postgres redis
    echo [OK] Docker services started
) else (
    echo [WARNING] Docker Compose not available. Skipping Docker setup.
    echo You can start services later with: docker-compose up -d
)

REM Git setup
echo.
echo Git repository setup...

if not exist ".git" (
    echo Initializing Git repository...
    git init
    echo [OK] Git repository initialized
    
    set /p response="Do you want to create an initial commit? (y/n): "
    if /i "%response%"=="y" (
        git add .
        git commit -m "feat: initial project setup with documentation and structure"
        echo [OK] Initial commit created
    )
) else (
    echo [OK] Git repository already initialized
)

REM Summary
echo.
echo ==========================================
echo Setup Complete!
echo ==========================================
echo.
echo Next steps:
echo.
echo 1. Configure environment variables:
echo    - Edit backend\.env with your settings
echo    - Edit mobile\.env with your API keys
echo.
echo 2. Set up third-party services:
echo    - Create Firebase project
echo    - Get Mapbox access token
echo    - (Optional) Set up Sentry
echo.
echo 3. Start the backend:
echo    cd backend
echo    venv\Scripts\activate
echo    uvicorn app.main:app --reload
echo.
echo 4. Test the API:
echo    curl http://localhost:8000/api/v1/health
echo    Open http://localhost:8000/api/docs in browser
echo.
echo 5. Read the documentation:
echo    - PROJECT_DOCUMENTATION.md - Complete technical docs
echo    - PROGRESS.md - Development progress tracker
echo    - docs\guides\SETUP.md - Detailed setup guide
echo.
echo For help, see: docs\guides\SETUP.md
echo.
echo Happy coding!
echo.
pause

