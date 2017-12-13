import os, threading;
from ctypes import *
from ctypes.wintypes import *

INFINITE    = 0xFFFFFFFFL;
WAIT_FAILED = 0xFFFFFFFFL;

class STARTUPINFOW(Structure):
  __slots__ = '__weakref__';
  _fields_ = [
    ("cb",               DWORD),
    ("lpReserved",       LPWSTR),
    ("lpDesktop",        LPWSTR),
    ("lpTitle",          LPWSTR),
    ("dwX",              DWORD),
    ("dwY",              DWORD),
    ("dwXSize",          DWORD),
    ("dwYSize",          DWORD),
    ("dwXCountChars",    DWORD),
    ("dwYCountChars",    DWORD),
    ("dwFillAtrribute",  DWORD),
    ("dwFlags",          DWORD),
    ("wShowWindow",      WORD),
    ("cbReserved2",      WORD),
    ("lpReserved2",      POINTER(BYTE)),
    ("hStdInput",        HANDLE),
    ("hStdOutput",       HANDLE),
    ("hStdError",        HANDLE),
  ];

class PROCESS_INFORMATION(Structure):
  __slots__ = '__weakref__';
  _fields_ = [
    ("hProcess",         HANDLE),
    ("hThread",          HANDLE),
    ("dwProcessId",      DWORD),
    ("dwThreadId",       DWORD),
  ];

class cProcess(object):
  def __init__(oProcess, asCommandLine, fTerminationCallback = None):
    oProcess.oStartupInfo = STARTUPINFOW();
    oProcess.oStartupInfo.cb = sizeof(oProcess.oStartupInfo);
    oProcess.oProcessInformation = PROCESS_INFORMATION();
    asCommandLine = [unicode(s) for s in asCommandLine];
    oProcess.sApplication = asCommandLine[0];
    oProcess.sCommandLine = u" ".join([" " in s and '"%s"' % s or s for s in asCommandLine]);
    oProcess.uExitCode = None;
    if not windll.kernel32.CreateProcessW(
      oProcess.sApplication, # lpApplicationName
      oProcess.sCommandLine, # lpCommandLine
      None, # lpProcessAttributes
      None, # lpThreadAttributes
      False, # bInheritHandles
      0, # dwCreationFlags
      None, # lpEnvironment
      None, # lpCurrentDirectory
      byref(oProcess.oStartupInfo),
      byref(oProcess.oProcessInformation),
    ):
      raise WindowsError("Cannot start process");
    oProcess.uPId = windll.kernel32.GetProcessId(oProcess.oProcessInformation.hProcess);
    oProcess.oTerminationLock = threading.Lock();
    oProcess.oTerminationLock.acquire();
    threading.Thread(target = oProcess._fWaitForProcessTerminationThread, args = (fTerminationCallback,)).start();
  
  def _fWaitForProcessTerminationThread(oProcess, fTerminationCallback):
    if windll.kernel32.WaitForSingleObject(oProcess.oProcessInformation.hProcess, INFINITE) == WAIT_FAILED:
      raise WindowsError("Cannot wait for process termination");
    dwExitCode = DWORD();
    if not windll.kernel32.GetExitCodeProcess(oProcess.oProcessInformation.hProcess, byref(dwExitCode)):
      raise WindowsError("Cannot get process exit code");
    oProcess.uExitCode = dwExitCode.value;
    oProcess.oTerminationLock.release();
    fTerminationCallback and fTerminationCallback(oProcess);
  
  def fuWaitForTermination(oProcess):
    oProcess.oTerminationLock.acquire();
    oProcess.oTerminationLock.release();
