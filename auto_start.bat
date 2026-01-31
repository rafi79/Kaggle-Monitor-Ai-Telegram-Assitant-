@echo off
REM This script starts the remote bot automatically when Windows starts

REM Change to the kaggle-monitor directory
cd /d "C:\Users\Rafi7\Downloads\Ai Training Agent\kaggle-monitor"

REM Start the bot in a minimized window
start /min "Kaggle Monitor Bot" cmd /c "python remote_starter.py"

REM Optional: Show a notification
msg * "Kaggle Monitor Bot started!"
