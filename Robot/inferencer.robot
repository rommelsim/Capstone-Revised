*** Settings ***
Library      SeleniumLibrary
Library      OperatingSystem
Library      Process
Library      inferencer_lib.py
Library      BlackWidow.py

*** Variables ***
${BATCH_SCRIPT}      video.bat
${MODEL_PATH}        vgg16_model.h5
${IMAGE_PATH}        pictures

*** Keywords ***
Set BlackWidow V4 Keyboard Chroma 
    Perform Chroma Test BlackWidow V4

Check If Chroma Status Is Complete
    ${status}=    Run Keyword And Return Status    Check Status
    Should Be True    ${status}    msg=Chroma Setup Incomplete.

Take Pictures Using Webcam
    Run Process		${CURDIR}/${BATCH_SCRIPT}
    Sleep    5s

Predict From Directory
    ${result}=    Predict Directory    ${CURDIR}/${MODEL_PATH}    ${CURDIR}/${IMAGE_PATH}   
    Should Be Equal    ${result}    PASS

*** Test Cases ***
Test Image Classification
    [Documentation]    Use Deep Neural Network to check for keyboard defects   
    Set BlackWidow V4 Keyboard Chroma
    Check If Chroma Status Is Complete
    Take Pictures Using Webcam
    Predict From Directory