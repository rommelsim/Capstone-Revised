*** Settings ***
Library      SeleniumLibrary
Library      OperatingSystem
Library      Process
Library      inferencer_lib.py
Library      BlackWidow.py

*** Variables ***
${BATCH_SCRIPT}    video.bat

*** Keywords ***
Set BlackWidow V4 Keyboard Chroma 
    Perform Chroma Test BlackWidow V4

Check If Chroma Status Is Complete
    ${status}=    Run Keyword And Return Status    Check Status
    Should Be True    ${status}    msg=Chroma Setup Incomplete.

Take Pictures Using Webcam
    Run Process    ${BATCH_SCRIPT}
    Sleep    8s

*** Test Cases ***
Test Image Classification
    [Documentation]    Test image if classified correctly    
    Set BlackWidow V4 Keyboard Chroma
    Check If Chroma Status Is Complete
    Take Pictures Using Webcam
    