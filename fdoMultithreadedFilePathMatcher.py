import os, queue, threading, time;
from mConsole import oConsole;

from cCounter import cCounter;
from cDict import cDict;
from mColors import *;

giBarLength = 80;

def fdoMultithreadedFilePathMatcher(uMaxThreads, asFolderPaths, bRecursive, arPathRegExps, arNegativePathRegExps, bVerbose):
  oMultithreadedFilePathMatcher = cMultithreadedFilePathMatcher(uMaxThreads, asFolderPaths, bRecursive, arPathRegExps, arNegativePathRegExps, bVerbose);
  return oMultithreadedFilePathMatcher.odosMatchedFilePaths.dxValue;  

class cMultithreadedFilePathMatcher(object):
  def __init__(oSelf, uMaxThreads, asFolderPaths, bRecursive, arPathRegExps, arNegativePathRegExps, bVerbose):
    oSelf.oUnhandledItemPathsQueue = queue.Queue();
    oSelf.bRecursive = bRecursive;
    oSelf.arPathRegExps = arPathRegExps;
    oSelf.arNegativePathRegExps = arNegativePathRegExps;
    oSelf.bVerbose = bVerbose;
    
    oSelf.odosMatchedFilePaths = cDict();
    oSelf.oException = None;
    oSelf.oNumberOfFilesFound = cCounter();
    oSelf.oNumberOfFoldersFound = cCounter();
    oSelf.oNumberOfItemsFound = cCounter(0);
    oSelf.oNumberOfItemsCompleted = cCounter();
    oSelf.oScanThreadsStarted = cCounter(uMaxThreads);
    oSelf.oScanThreadsFinished = cCounter(0);

    for sFolderPath in set(asFolderPaths):
      oSelf.oNumberOfItemsFound.fuIncrease();
      if os.path.isdir(sFolderPath):
        oSelf.oUnhandledItemPathsQueue.put(sFolderPath);
        oSelf.fDebug();
      else:
        oSelf.oNumberOfItemsCompleted.fuIncrease();
        oSelf.fDebug();
    
    aoThreads = [
      threading.Thread(target = oSelf.fScanThread)
      for x in range(uMaxThreads)
    ] + [
      threading.Thread(target = oSelf.fStatusThread)
    ];
    
    for oThread in aoThreads:
      oThread.daemon = True;
      oThread.start();
    for oThread in aoThreads:
      oThread.join();
  
  def fDebug(oSelf):
#    oConsole.fOutput("%d/%d/%d/%d" % (oSelf.oNumberOfFilesFound.uValue, oSelf.oNumberOfFoldersFound.uValue, oSelf.oNumberOfItemsFound.uValue, oSelf.oNumberOfItemsCompleted.uValue));
    assert oSelf.oNumberOfFilesFound.uValue + oSelf.oNumberOfFoldersFound.uValue <= oSelf.oNumberOfItemsFound.uValue, \
        "111!";
    assert oSelf.oNumberOfItemsCompleted.uValue <= oSelf.oNumberOfItemsFound.uValue, \
        "333!";
  
  def fScanThread(oSelf):
    try:
      while oSelf.oNumberOfItemsCompleted.uValue < oSelf.oNumberOfItemsFound.uValue and not oSelf.oException:
        # Try to get the item's content is if it is a folder. If this fails, it is assumed to be a file.
        sItemPath = oSelf.oUnhandledItemPathsQueue.get();
        if sItemPath is None:
          break;
        sFullItemPath = "\\\\?\\" + str(sItemPath);
        try:
          asSubItemNames = os.listdir(sFullItemPath);
        except Exception:
          # This failed: assume it is a file.
          oSelf.oNumberOfFilesFound.fuIncrease();
          oSelf.fDebug();
          oSelf.fHandleFile(sItemPath);
          oSelf.oNumberOfItemsCompleted.fuIncrease();
          oSelf.fDebug();
        else:
          # This is a folder, process sub-items:
          oSelf.oNumberOfFoldersFound.fuIncrease();
          oSelf.fDebug();
          oSelf.oNumberOfItemsFound.fuAdd(len(asSubItemNames));
          oSelf.fDebug();
          for sSubItemName in asSubItemNames:
            sFullSubItemPath = os.path.join(sFullItemPath, sSubItemName);
            try:
              sSubItemName = str(sSubItemName);
            except Exception:
              pass;
            sSubItemPath = os.path.join(sItemPath, sSubItemName);
            # Doing a recursive find means getting sub-items of sub-folders as well, so queue it:
            if oSelf.bRecursive:
              oSelf.oUnhandledItemPathsQueue.put(sSubItemPath);
            else:
              # Not doing a recursive find means only handle sub-items that are files:
              if os.path.isfile(sFullSubItemPath):
                oSelf.oNumberOfFilesFound.fuIncrease();
                oSelf.fDebug();
                oSelf.fHandleFile(sSubItemPath);
                oSelf.oNumberOfItemsCompleted.fuIncrease();
                oSelf.fDebug();
              else:
                oSelf.oNumberOfFoldersFound.fuIncrease();
                oSelf.fDebug();
                oSelf.oNumberOfItemsCompleted.fuIncrease();
                oSelf.fDebug();
          oSelf.oNumberOfItemsCompleted.fuIncrease();
          oSelf.fDebug();
    except Exception as oException:
      oSelf.oException = oException;
      raise;
    finally:
      oSelf.oScanThreadsFinished.fuIncrease();
#      oConsole.fOutput("scan thread %d/%d done" % (oSelf.oScanThreadsFinished.uValue, oSelf.oScanThreadsStarted.uValue));
      oSelf.oUnhandledItemPathsQueue.put(None);
  
  def fHandleFile(oSelf, sItemPath):
    oMatch = None;
    # Having no reg.exps. means always add:
    if oSelf.arPathRegExps or oSelf.arNegativePathRegExps:
      # Having negative reg.exps. means not add if matched:
      for rNegativePathRegExp in oSelf.arNegativePathRegExps:
        if rNegativePathRegExp.search(sItemPath):
          # Matching negative reg.exp. means don't add (and stop matching).
          if oSelf.bVerbose:
            oConsole.fOutput(DIM, "  - %s (matches negative reg.exp.)" % sItemPath);
          return;
      # Not matching negative reg.exp. means maybe add:
      if not oSelf.arPathRegExps:
        # Not having positive reg.exps. means add:
        if oSelf.bVerbose:
          oConsole.fOutput("  + %s (does not match any negative reg.exp.)" % sItemPath);
      else:
        # Having positive reg.exps. means add if matched:
        for rPathRegExp in oSelf.arPathRegExps:
          oMatch = rPathRegExp.search(sItemPath);
          if oMatch:
            # Matching positive reg.exp. means add (and stop matching).
            if oSelf.bVerbose:
              asSubMatchesOutput = [];
              for sSubMatch in oMatch.groups():
                if len(asSubMatchesOutput):
                  asSubMatchesOutput.append(", ");
                asSubMatchesOutput.extend([NORMAL, sSubMatch, DIM]);
              asSubMatchesOutput.append(".");
              oConsole.fLock();
              try:
                oConsole.fOutput("  + %s (matches reg.exp.)" % sItemPath);
                oConsole.fOutput(DIM, "    Sub-matches: ", *asSubMatchesOutput);
              finally:
                oConsole.fUnlock();
            break;
          else:
            # Not matching positive reg.exps. means don't add.
            if oSelf.bVerbose:
              oConsole.fOutput(DIM, "  - %s (does not match any reg.exp.)" % sItemPath);
            return;
    oSelf.odosMatchedFilePaths.fSet(sItemPath, oMatch);
  
  def fStatusThread(oSelf):
    try:
      while oSelf.oScanThreadsStarted.uValue != oSelf.oScanThreadsFinished.uValue and not oSelf.oException:
        uNumberOfItemsFound = oSelf.oNumberOfItemsFound.uValue;
        uNumberOfFilesFound = oSelf.oNumberOfFilesFound.uValue;
        uNumberOfFoldersFound = oSelf.oNumberOfFoldersFound.uValue;
        uNumberOfItemsCompleted = oSelf.oNumberOfItemsCompleted.uValue;
        uNumberOfItemsRemaining = uNumberOfItemsFound - uNumberOfFoldersFound - uNumberOfFilesFound;
        nProgress = uNumberOfItemsFound and 1.0 * uNumberOfItemsCompleted / uNumberOfItemsFound or 0;
        sStatus = "%s%d files (%d/%d items remaining)" % (
          (oSelf.arPathRegExps or oSelf.arNegativePathRegExps)
              and ("Matched path for %d/" % oSelf.odosMatchedFilePaths.uSize)
              or "Found ",
          uNumberOfFilesFound,
          uNumberOfItemsRemaining,
          uNumberOfItemsFound,
        );
        oConsole.fProgressBar(nProgress,  sStatus);
        time.sleep(0.25);
    except Exception as oException:
      oSelf.oException = oException;
      raise;
#    finally:
#      oConsole.fOutput("status thread done");
