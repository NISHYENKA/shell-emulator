@echo off
setlocal
pushd "%~dp0.."
call run.bat --vfs vfs/several --script scripts/error_unknown.txt <nul
if not errorlevel 1 exit /b 1
call run.bat --vfs vfs/several --script scripts/error_arguments.txt <nul
if not errorlevel 1 exit /b 1
call run.bat --vfs vfs/several --script scripts/error_exit.txt <nul
if not errorlevel 1 exit /b 1
call run.bat --vfs vfs/several --script scripts/error_vfs_info.txt <nul
if not errorlevel 1 exit /b 1
call run.bat --vfs vfs/several --script scripts/error_missing.txt <nul
if not errorlevel 1 exit /b 1
call run.bat --vfs vfs/several --script scripts/error_file_directory.txt <nul
if not errorlevel 1 exit /b 1
call run.bat --vfs vfs/several --script scripts/error_ls.txt <nul
if not errorlevel 1 exit /b 1
call run.bat --vfs vfs/several --script scripts/error_date.txt <nul
if not errorlevel 1 exit /b 1
call run.bat --vfs vfs/several --script scripts/error_pwd.txt <nul
if not errorlevel 1 exit /b 1
call run.bat --vfs vfs/several --script scripts/error_cal.txt <nul
if not errorlevel 1 exit /b 1
call run.bat --vfs vfs/several --script scripts/error_cal_year.txt <nul
if not errorlevel 1 exit /b 1
call run.bat --vfs vfs/several --script scripts/error_mkdir.txt <nul
if not errorlevel 1 exit /b 1
call run.bat --vfs vfs/several --script scripts/error_mkdir_parent.txt <nul
if not errorlevel 1 exit /b 1
call run.bat --vfs vfs/several --script scripts/error_cp.txt <nul
if not errorlevel 1 exit /b 1
call run.bat --vfs vfs/several --script scripts/error_cp_missing.txt <nul
if not errorlevel 1 exit /b 1
call run.bat --vfs vfs/several --script scripts/error_cp_self.txt <nul
if not errorlevel 1 exit /b 1
call run.bat --vfs vfs/several --script scripts/error_cp_descendant.txt <nul
if not errorlevel 1 exit /b 1
call run.bat --vfs vfs/missing <nul
if not errorlevel 1 exit /b 1
call run.bat --vfs README.md <nul
if not errorlevel 1 exit /b 1
popd
exit /b 0
