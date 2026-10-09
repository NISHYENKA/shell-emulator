@echo off
setlocal
pushd "%~dp0.."
call run.bat --vfs .\vfs\minimal --script scripts/startup_basic.txt <nul
if errorlevel 1 exit /b 1
call run.bat --vfs .\vfs\several --script scripts/startup_basic.txt <nul
if errorlevel 1 exit /b 1
call run.bat --vfs .\vfs\nested --script scripts/startup_basic.txt <nul
if errorlevel 1 exit /b 1
call run.bat --vfs .\vfs\nested --script scripts/startup_nested.txt <nul
if errorlevel 1 exit /b 1
popd
exit /b 0
