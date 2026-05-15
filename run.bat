@echo off
title Khoi dong StudyAI
echo Dang kiem tra moi truong...
cd app
python main.py
if %errorlevel% neq 0 (
    echo.
    echo [LOI] Co loi xay ra khi chay ung dung.
    echo Vui long kiem tra xem ban da cai dat CustomTkinter chua.
    pause
)
