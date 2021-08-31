import os, queue, threading, time;
from mConsole import oConsole;

from cCounter import cCounter;
from cDict import cDict;
from mColors import *;

giBarLength = 80;

def fdoMultithreadedFilePathMatcher(
  uMaxThreads,
  asFolderPaths,
  bRecursive,
  arPathRegExps, arNegativePathRegExps,
  arNameRegExps, arNegativeNameRegExps,
  bVerbose,
):
  oMultithreadedFilePathMatcher = cMultithreadedFilePathMatcher(
    uMaxThreads,
    asFolderPaths,
    bRecursive,
    arPathRegExps, arNegativePathRegExps,
    arNameRegExps, arNegativeNameRegExps,
    bVerbose,
  );
  return oMultithreadedFilePathMatcher.odosMatchedFilePaths.dxValue;  

def fVerboseMatchOuput(sChar, sItemPath, sReason, oMatch):
  oConsole.fLock();
  try:
    oConsole.fOutput("  ", sChar, " ", sItemPath, DIM, " (matches ", sReason, " reg.exp. ", oMatch.re.pattern, ")");
    if len(oMatch.groups()):
      asSubMatchesOutput = [];
      for sSubMatch in oMatch.groups():
        asSubMatchesOutput += [", " if len(asSubMatchesOutput) else "", NORMAL, sSubMatch, DIM];
      oConsole.fOutput(DIM, "    Sub-matches: ", asSubMatchesOutput, ".");
  finally:
    oConsole.fUnlock();

class cMultithreadedFilePathMatcher(object):
  def __init__(oSelf,
    uMaxThreads,
    asFolderPaths,
    bRecursive,
    arPathRegExps, arNegativePathRegExps,
    arNameRegExps, arNegativeNameRegExps,
    bVerbose,
  ):
    oSelf.oUnhandledItemPathsQueue = queue.Queue();
    oSelf.bRecursive = bRecursive;
    oSelf.arPathRegExps = arPathRegExps;
    oSelf.arNegativePathRegExps = arNegativePathRegExps;
    oSelf.arNameRegExps = arNameRegExps;
    oSelf.arNegativeNameRegExps = arNegativeNameRegExps;
    oSelf.bVerbose = bVerbose;
    
    oSelf.odosMatchedFilePaths = cDict();
    oSelf.oException = None;
    oSelf.oNumberOfFilesFound = cCounter();
    oSelf.oNumberOfFoldersFound = cCounter();
    oSelf.oNumberOfItemsFound = cCounter(0);
    oSelf.oNumberOfItemsCompleted = cCounter();
    oSelf.oScanThreadsStarted = cCounter(uMaxThreads);
    oSelf.oScanThreadsFinished = cCounter(0);
    
    if oSelf.bVerbose:
      oConsole.fOutput("* Scanning ", str(len(asFolderPaths)), " folder paths", " (and descendants)" if bRecursive else "", "...");
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
#    assert oSelf.oNumberOfFilesFound.uValue + oSelf.oNumberOfFoldersFound.uValue <= oSelf.oNumberOfItemsFound.uValue, \
#        "111!";
#    assert oSelf.oNumberOfItemsCompleted.uValue <= oSelf.oNumberOfItemsFound.uValue, \
#        "333!";
    pass;
  
  def fScanThread(oSelf):
    try:
      while oSelf.oNumberOfItemsCompleted.uValue < oSelf.oNumberOfItemsFound.uValue and not oSelf.oException:
        # Try to get the item's content is if it is a folder. If this fails, it is assumed to be a file.
        sItemPath = oSelf.oUnhandledItemPathsQueue.get();
        if sItemPath is None:
          break;
        try:
          asSubItemNames = os.listdir("\\\\?\\" + sItemPath);
        except Exception:
          # This failed: assume it is a file.
          oSelf.oNumberOfFilesFound.fuIncrease();
          bIsFile = True;
        else:
          # This is a folder
          oSelf.oNumberOfFoldersFound.fuIncrease();
          bIsFile = False;
        oSelf.fDebug();
        if bIsFile:
          oSelf.fHandleFile(sItemPath);
        else:
          oSelf.fHandleFolder(sItemPath, asSubItemNames);
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
    oLastPathMatch = None;
    # Having no reg.exps. means always add:
    if (
      oSelf.arPathRegExps or oSelf.arNegativePathRegExps
      or oSelf.arNameRegExps or oSelf.arNegativeNameRegExps
    ):
      if oSelf.arNameRegExps or oSelf.arNegativeNameRegExps:
        sItemName = os.path.basename(sItemPath);
      # Having negative reg.exps. means not add if matched:
      for rNegativePathRegExp in oSelf.arNegativePathRegExps:
        oMatch = rNegativePathRegExp.search(sItemPath)
        if oMatch:
          # Matching negative reg.exp. means don't add (and stop matching).
          if oSelf.bVerbose:
            fVerboseMatchOuput("-", sItemPath, "negative path", oMatch);
          return;
      for rNegativeNameRegExp in oSelf.arNegativeNameRegExps:
        oMatch = rNegativeNameRegExp.search(sItemName);
        if oMatch:
          # Matching negative reg.exp. means don't add (and stop matching).
          if oSelf.bVerbose:
            fVerboseMatchOuput("-", sItemPath, "negative name", oMatch);
          return;
      # Not matching negative reg.exp. means maybe add:
      # Not having positive reg.exps. means add:
      # Having positive reg.exps. means add if matches all:
      if oSelf.arPathRegExps:
        for rPathRegExp in oSelf.arPathRegExps:
          oMatch = rPathRegExp.search(sItemPath);
          if oMatch:
            if oSelf.bVerbose:
              fVerboseMatchOuput("*", sItemPath, "path", oMatch);
            oLastPathMatch = oMatch;
          else:
            if oSelf.bVerbose:
              oConsole.fOutput("  - ", sItemPath, DIM, " (does not match path reg.exp. ", rPathRegExp.pattern, ")");
            return;
      if oSelf.arNameRegExps:
        for rNameRegExp in oSelf.arNameRegExps:
          oMatch = rNameRegExp.search(sItemName);
          if oMatch:
            if oSelf.bVerbose:
              fVerboseMatchOuput("*", sItemPath, "name", oMatch);
          else:
            if oSelf.bVerbose:
              oConsole.fOutput("  - ", sItemPath, DIM, " (does not match name reg.exp. ", rNameRegExp.pattern, ")");
            return;
      if oSelf.bVerbose:
        sMatchedExpressionTypes = " and ".join([s for s in [
          "path" if oSelf.arPathRegExps else None,
          "name" if oSelf.arNameRegExps else None,
        ] if s]);
        oConsole.fOutput("  + ", sItemPath, DIM, " (matches all ", sMatchedExpressionTypes, " reg.exp.)");
    elif oSelf.bVerbose:
      oConsole.fOutput("  + ", sItemPath);
    oSelf.odosMatchedFilePaths.fSet(sItemPath, oLastPathMatch);
  
  def fHandleFolder(oSelf, sItemPath, asSubItemNames):
    oLastPathMatch = None;
    # Having no reg.exps. means always add:
    if (
      oSelf.arPathRegExps or oSelf.arNegativePathRegExps
      or oSelf.arNameRegExps or oSelf.arNegativeNameRegExps
    ):
      # Having negative path reg.exps. means not add if matched:
      for rNegativePathRegExp in oSelf.arNegativePathRegExps:
        oMatch = rNegativePathRegExp.search(sItemPath);
        if oMatch:
          # Matching negative path reg.exp. means don't add and files in this folder (and stop matching).
          if oSelf.bVerbose:
            fVerboseMatchOuput("-", sItemPath + "\\*", "negative path", oMatch);
          return;
      # Not matching negative path reg.exp. means maybe add:
      # Having positive reg.exps. means add if matches all:
      if oSelf.arPathRegExps:
        for rPathRegExp in oSelf.arPathRegExps:
          oMatch = rPathRegExp.search(sItemPath);
          if not oMatch:
            if oSelf.bVerbose:
              oConsole.fOutput("  - ", sItemPath, DIM, "\\* (does not match path reg.exp. ", rPathRegExp.pattern, ")");
            return;
    if oSelf.bVerbose:
      oConsole.fOutput("  * Scanning ", str(len(asSubItemNames)), " descendants of folder ", sItemPath, DIM, " (matches all path reg.exp.)");
    oSelf.oNumberOfItemsFound.fuAdd(len(asSubItemNames));
    for sSubItemName in asSubItemNames:
      sSubItemPath = os.path.join(sItemPath, sSubItemName);
      # Doing a recursive find means getting sub-items of sub-folders as well, so queue it:
      if oSelf.bRecursive:
        oSelf.oUnhandledItemPathsQueue.put(sSubItemPath);
      else:
        # Not doing a recursive find means only handle sub-items that are files:
        if os.path.isfile("\\\\?\\" + sSubItemPath):
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
  
  def fStatusThread(oSelf):
    try:
      bMatchingPath = oSelf.arPathRegExps or oSelf.arNegativePathRegExps;
      bMatchingName = oSelf.arNameRegExps or oSelf.arNegativeNameRegExps;
      bMatchingPathOrName = bMatchingPath or bMatchingName;
      while oSelf.oScanThreadsStarted.uValue != oSelf.oScanThreadsFinished.uValue and not oSelf.oException:
        uNumberOfItemsFound = oSelf.oNumberOfItemsFound.uValue;
        uNumberOfFilesFound = oSelf.oNumberOfFilesFound.uValue;
        uNumberOfFoldersFound = oSelf.oNumberOfFoldersFound.uValue;
        uNumberOfItemsCompleted = oSelf.oNumberOfItemsCompleted.uValue;
        uNumberOfItemsRemaining = uNumberOfItemsFound - uNumberOfFoldersFound - uNumberOfFilesFound;
        nProgress = 1.0 * uNumberOfItemsCompleted / uNumberOfItemsFound if uNumberOfItemsFound else 0;
        nSubProgress = 1.0 * oSelf.odosMatchedFilePaths.uSize / uNumberOfFilesFound if uNumberOfFilesFound else 0;
        oConsole.fProgressBar(
          nProgress,
          sMessage = "%s%d files (%d/%d items remaining)" % (
            "Matched %s for %d/" % (
              " and ".join([s for s in [
                "path" if bMatchingPath else None,
                "name" if bMatchingName else None,
              ] if s]),
              oSelf.odosMatchedFilePaths.uSize,
            ) if bMatchingPathOrName else "Found ",
            uNumberOfFilesFound,
            uNumberOfItemsRemaining,
            uNumberOfItemsFound,
          ),
          nSubProgress = nSubProgress,
        );
        time.sleep(0.25);
    except Exception as oException:
      oSelf.oException = oException;
      raise;
#    finally:
#      oConsole.fOutput("status thread done");
