@echo off
REM Activation script for Windows Command Prompt
REM Usage: activate.bat

echo Activating Python virtual environment...
call venv\Scripts\activate.bat

echo.
echo ✅ Virtual environment activated!
echo.
echo Next steps:
echo   1. Install dependencies: pip install -r requirements.txt
echo   2. Test connection: python test_remote_setup.py
echo   3. Run migrations: alembic upgrade head
echo   4. Start server: uvicorn app.main:app --reload
echo.
