@ECHO OFF

ECHO * Running unit-tests...

ECHO   * Test version check...
CALL "%~dp0rs.cmd" --version
IF ERRORLEVEL 1 GOTO :ERROR

ECHO   * Test search with command execution and redirected output... 
CALL "%~dp0rs.cmd"  -r -p /\\Tests\.cmd$/ -c /@@@MARKER@@@/ -- ECHO SUCCESS >nul
IF ERRORLEVEL 2 GOTO :ERROR
IF NOT ERRORLEVEL 1 (
  ECHO     - Expected a match, but got none ^(exit code = 0^).
  EXIT /B 1
)

ECHO   * Test usage help...
CALL "%~dp0rs.cmd" --help %* >nul
IF ERRORLEVEL 1 GOTO :ERROR

ECHO + Passed unit-tests.
EXIT /B 0

:ERROR
  ECHO   - Error %ERRORLEVEL%.
  EXIT /B %ERRORLEVEL%
