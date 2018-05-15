@ECHO OFF
CALL "%~dp0rs.cmd" --version
IF ERRORLEVEL 1 GOTO :ERROR
CALL "%~dp0rs.cmd"  -r -p /\\Tests\.cmd$/ -c /@@@MARKER@@@/ -- ECHO SUCCESS >nul
IF ERRORLEVEL 2 GOTO :ERROR
IF NOT ERRORLEVEL 1 (
  EXIT /B 1
)

EXIT /B 0

:ERROR
  ECHO   - Error %ERRORLEVEL%.
  EXIT /B %ERRORLEVEL%
