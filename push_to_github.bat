@echo off
echo ============================================================
echo Kaggle Monitor - Push to GitHub
echo ============================================================
echo.

REM Check if config.yaml exists
if exist config.yaml (
    echo WARNING: config.yaml found!
    echo This file contains your bot token and should NOT be pushed to GitHub.
    echo.
    echo The .gitignore file will prevent it from being pushed.
    echo.
)

echo Current directory: %CD%
echo.
echo This script will push to:
echo https://github.com/rafi79/Kaggle-Monitor-Ai-Telegram-Assitant
echo.
echo Press Ctrl+C to cancel, or
pause

echo.
echo Checking git status...
git status

echo.
echo Adding any new files...
git add .

echo.
echo Committing changes...
set /p commit_message="Enter commit message (or press Enter for default): "
if "%commit_message%"=="" set commit_message=Update Kaggle Monitor

git commit -m "%commit_message%"

echo.
echo Pushing to GitHub...
git push -u origin main

echo.
echo ============================================================
echo Done! Check your GitHub repository:
echo https://github.com/rafi79/Kaggle-Monitor-Ai-Telegram-Assitant
echo ============================================================
echo.
pause
