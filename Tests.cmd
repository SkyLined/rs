@ECHO OFF
SETLOCAL
SET _NT_SYMBOL_PATH=

IF "%~1" == "--all" (
  REM If you can add the x86 and x64 binaries of python to the path, or add links to the local folder, tests will be run
  REM in both
  WHERE PYTHON_X86 >nul 2>&1
  IF NOT ERRORLEVEL 0 (
    ECHO - PYTHON_X86 was not found; not testing both x86 and x64 ISAs.
  ) ELSE (
    WHERE PYTHON_X64 >nul 2>&1
    IF NOT ERRORLEVEL 0 (
      ECHO - PYTHON_X64 was not found; not testing both x86 and x64 ISAs.
    ) ELSE (
      GOTO :TEST_BOTH_ISAS
    )
  )
)

WHERE PYTHON 2>&1 >nul
IF ERRORLEVEL 1 (
  ECHO - PYTHON was not found!
  ENDLOCAL
  EXIT /B 1
)

CALL PYTHON "%~dpn0\%~n0.py" %*
IF ERRORLEVEL 1 GOTO :ERROR
ENDLOCAL
GOTO :ADDITIONAL_TESTS

:TEST_BOTH_ISAS
  ECHO * Running tests in x86 build of Python...
  CALL PYTHON_X86 "%~dpn0\%~n0.py" %*
  IF ERRORLEVEL 1 GOTO :ERROR
  ECHO * Running tests in x64 build of Python...
  CALL PYTHON_X64 "%~dpn0\%~n0.py" %*
  IF ERRORLEVEL 1 GOTO :ERROR
  ENDLOCAL
  EXIT /B 0

:ADDITIONAL_TESTS
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
  ENDLOCAL
  EXIT /B 1
)

ECHO   * Test usage help...
CALL "%~dp0rs.cmd" --help %* >nul
IF ERRORLEVEL 1 GOTO :ERROR

ECHO + Passed unit-tests.
ENDLOCAL
EXIT /B 0

:ERROR
  ECHO   - Error %ERRORLEVEL%.
  ENDLOCAL
  EXIT /B %ERRORLEVEL%
