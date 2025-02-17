@echo off

REM Path to the executable
set MODE=2
set numVideos=5
set EXECUTABLE_PATH=VideoAPI.exe

REM Run the executable with the user-provided values
"%EXECUTABLE_PATH%" %numVideos% %MODE%
