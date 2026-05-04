@echo off
echo Starting AlterEgo...
cd /d E:\AlterEgo
call venv\Scripts\activate
cd core
python agent.py
pause
