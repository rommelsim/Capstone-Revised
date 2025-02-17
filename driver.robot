*** Settings ***
Library  SeleniumLibrary
Library  OperatingSystem
Library  Process
Library  BlackWidow.py
Library  Dentrite.py


*** Variables ***
${BATCH_SCRIPT}    video.bat

*** Keywords ***
Set BlackWidow V4 Keyboard Chroma 
    Perform Chroma Test BlackWidow V4
    
Check If Chroma Status Is Complete
    ${status}=    Run Keyword And Return Status    Check Status
    Should Be True    ${status}    msg=Chroma Setup Incomplete.

Run Prediction Using Model
    Predict

*** Test Cases ***
Chroma Tests
    Set BlackWidow V4 Keyboard Chroma
    Wait Until Keyword Succeeds    5s    1s    Check If Chroma Status Is Complete
    Run Process    ${BATCH_SCRIPT}
    Sleep    8s
    Run Prediction Using Model
