@ECHO OFF
SETLOCAL
SET REDIRECT_STDOUT_FILE_PATH=%TEMP%\BugId Test stdout %RANDOM%.txt
ECHO   * Test usage help...
CALL "%~dp0\..\rs.cmd" --help >"%REDIRECT_STDOUT_FILE_PATH%"
IF ERRORLEVEL 1 GOTO :ERROR
ECHO   * Test version info...
CALL "%~dp0\..\rs.cmd" --version >"%REDIRECT_STDOUT_FILE_PATH%"
IF ERRORLEVEL 1 GOTO :ERROR
ECHO   * Test version check...
CALL "%~dp0\..\rs.cmd" --version-check >"%REDIRECT_STDOUT_FILE_PATH%"
IF ERRORLEVEL 1 GOTO :ERROR
ECHO   * Test license info...
CALL "%~dp0\..\rs.cmd" --license >"%REDIRECT_STDOUT_FILE_PATH%"
IF ERRORLEVEL 1 GOTO :ERROR
ECHO   * Test license update...
CALL "%~dp0\..\rs.cmd" --license-update >"%REDIRECT_STDOUT_FILE_PATH%"
IF ERRORLEVEL 1 GOTO :ERROR
DEL "%REDIRECT_STDOUT_FILE_PATH%" /Q

PUSHD "%~dp0"
ECHO   * Test search with command execution and redirected output... 
REM Looking for this -> @@@MARKER@@@
REM Here's another on a different line: @@@MARKER@@@
CALL "%~dp0\..\rs.cmd" "n/\ATests\.cmd\Z/" "c/@@@(M)(A)(R)(K)(E)(R)@@@/" --verbose -- "%ComSpec%" /C ECHO SUCCESS \\{f}=[\{f}] f=[{f}] l=[{l},{l},{l}] 0=[{0}] 1=[{1}] 2=[{2}] 3=[{3}] 4=[{4}] 5=[{5}] 6=[{6}] 7=[{7}] 8=[{8}] 9=[{9}] 10=[{10}] d=[{d}] p=[{p}] n=[{n}] x=[{x}] dpnx=[{dpnx}]
IF %ERRORLEVEL% == 10 (
  POPD
  ECHO =^> Expected a match ^(exit code = 0^) but got no matches ^(exit code 10^).
  ENDLOCAL
  EXIT /B 1
)
IF ERRORLEVEL 1 (
  ECHO =^> Expected a match ^(exit code = 0^) but got exit code %ERRORLEVEL%!?
  POPD
  CALL :CLEANUP
  ENDLOCAL
  EXIT /B 3
)

POPD
CALL :CLEANUP
ENDLOCAL
ECHO + Test.cmd completed.
EXIT /B 0

:ERROR
  ECHO     - Failed with error level %ERRORLEVEL%
  CALL :CLEANUP
  ENDLOCAL
  EXIT /B 3

:CLEANUP
  IF EXIST "%REDIRECT_STDOUT_FILE_PATH%" (
    POWERSHELL $OutputEncoding = New-Object -Typename System.Text.UTF8Encoding; Get-Content -Encoding utf8 '"%REDIRECT_STDOUT_FILE_PATH%"'
    DEL "%REDIRECT_STDOUT_FILE_PATH%" /Q
  )
