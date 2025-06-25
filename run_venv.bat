@echo off

@REM Create new Virtual Environment
python -m venv venv

@REM Activate the virtual environment
call .\venv\Scripts\activate.bat

@REM Upgrade python tools
python -m pip install --upgrade pip setuptools wheel

@REM Pip install requirements
python -m pip install -r requirements.txt

@REM Run the App
python app.py

@REM Pause to keep the command prompt open
pause