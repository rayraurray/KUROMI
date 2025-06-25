@echo off

@REM Upgrade python tools
pip install --upgrade pip setuptools wheel

@REM Pip install requirements
python -m pip install -r requirements.txt

@REM Run the App
python app.py

@REM Pause to keep the command prompt open
pause