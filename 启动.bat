@echo off
chcp 65001 >nul
title QQ音乐取流下载工具
cd /d "%~dp0"

echo ============================================================
echo   QQ音乐取流下载工具
echo ============================================================
echo.

where python >nul 2>nul
if %errorlevel%==0 (
    set PY=python
) else (
    set PY=C:\Users\wesker\.workbuddy\binaries\python\versions\3.13.12\python.exe
)

echo 正在启动服务并打开浏览器...
start "" http://127.0.0.1:8770/
%PY% server.py --port 8770 --open

pause
