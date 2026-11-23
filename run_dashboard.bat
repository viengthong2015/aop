@echo off
rem Starts the live AOP 2027 dashboard and opens it in the browser.
cd /d "%~dp0"
python -m streamlit run streamlit_app.py --server.headless false
if errorlevel 1 pause
