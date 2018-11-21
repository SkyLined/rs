@ECHO OFF

ECHO * Running unit-tests...

ECHO   * Test version check...
CALL "%~dp0rs.cmd" --version
IF ERRORLEVEL 1 GOTO :ERROR

ECHO   * Test search with command execution and redirected output... 
REM Looking for this -> @@@MARKER@@@
REM Here's another on a different line: @@@MARKER@@@
CALL "%~dp0rs.cmd" -p /\\Tests\.cmd$/ -c "/@@@(M)(A)(R)(K)(E)(R)@@@/" -- ECHO SUCCESS \\{f}=[\{f}] f=[{f}] l=[{l},{l},{l}] 0=[{0}] 1=[{1}] 2=[{2}] 3=[{3}] 4=[{4}] 5=[{5}] 6=[{6}] 7=[{7}] 8=[{8}] 9=[{9}] 10=[{10}] d=[{d}] p=[{p}] n=[{n}] x=[{x}] dpnx=[{dpnx}]
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
