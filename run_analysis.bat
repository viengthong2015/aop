@echo off
cd /d "%~dp0"
python run_aop_analysis.py %*
if errorlevel 1 pause & exit /b 1
start "" "output\AOP2027_dashboard.html"
