@echo off
setlocal
pushd "%~dp0.."
call run.bat --vfs vfs/several --script scripts/error_unknown.txt <nul
if not errorlevel 1 exit /b 1
call run.bat --vfs vfs/several --script scripts/error_arguments.txt <nul
if not errorlevel 1 exit /b 1
call run.bat --vfs vfs/several --script scripts/error_exit.txt <nul
if not errorlevel 1 exit /b 1
popd
exit /b 0
