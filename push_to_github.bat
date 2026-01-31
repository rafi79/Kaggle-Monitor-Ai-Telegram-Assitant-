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
echo This script will:
echo 1. Initialize git repository (if needed)
echo 2. Add all files (except those in .gitignore)
echo 3. Commit changes
echo 4. Push to GitHub
echo.
echo Press Ctrl+C to cancel, or
pause

echo.
echo Step 1: Initializing git repository...
git init

echo.
echo Step 2: Adding remote repository...
git remote add origin https://github.com/rafi79/Kaggle-Monitor-Ai-Telegram-Assitant.git
git remote -v

echo.
echo Step 3: Adding files...
git add .

echo.
echo Step 4: Checking what will be committed...
git status

echo.
echo Step 5: Committing changes...
set /p commit_message="Enter commit message (or press Enter for default): "
if "%commit_message%"=="" set commit_message=Update Kaggle Monitor with AI improvements

git commit -m "%commit_message%"

echo.
echo Step 6: Pushing to GitHub...
git branch -M main
git push -u origin main --force

echo.
echo ============================================================
echo Done! Check your GitHub repository:
echo https://github.com/rafi79/Kaggle-Monitor-Ai-Telegram-Assitant
echo ============================================================
echo.
pause
