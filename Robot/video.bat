@echo off

REM Get the current script directory
set SCRIPT_DIR=%~dp0

REM Path to the executable
set MODE=2
set numVideos=1
set EXECUTABLE_PATH="%SCRIPT_DIR%VideoAPI.exe"

REM Run the executable with the user-provided values
"%EXECUTABLE_PATH%" %numVideos% %MODE%
