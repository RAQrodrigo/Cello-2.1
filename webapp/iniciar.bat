@echo off
cd /d "%~dp0"
start "" http://localhost:5000
"C:\Users\Rodri\AppData\Local\Python\bin\python.exe" app.py
