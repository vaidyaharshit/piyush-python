@echo off
title ContactHub - Contact Book Management System
echo Launching ContactHub...
python main.py
if errorlevel 1 (
    echo.
    echo An error occurred. Make sure dependencies are installed:
    echo pip install -r requirements.txt
    pause
)
