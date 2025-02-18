@echo off

:ask_input
REM Prompt the user for the number of videos (or photos)
set /p numVideos=Enter the number of iterations: 

REM Check if the input is a valid positive integer
for /f "delims=0123456789" %%a in ("%numVideos%") do (
    echo Invalid input. Please enter a positive integer.
    goto ask_input
)

REM Validate that the number is greater than zero
if %numVideos% LEQ 0 (
    echo Invalid input. Please enter a positive integer.
    goto ask_input
)

:ask_mode
echo.
echo Select the mode:
echo 1) VIDEO
echo 2) PICTURE
echo.
set /p inputMode=Enter mode (1 or 2): 

REM Validate mode input
if "%inputMode%"=="1" (
    set MODE=1
) else if "%inputMode%"=="2" (
    set MODE=2
) else (
    echo Invalid mode. Please enter 1 or 2.
    goto ask_mode
)

REM Path to the executable
set EXECUTABLE_PATH=VideoAPI.exe

REM Run the executable with the user-provided values
"%EXECUTABLE_PATH%" %numVideos% %MODE%

REM Pause to display completion message
pause
