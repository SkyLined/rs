import os, queue, time;

from mConsole import oConsole;
from mMultiThreading import cThread;

from cCounter import cCounter;
from cDict import cDict;
from mColorsAndChars import *;

giBarLength = 80;

def fdtoMultithreadedFileNameAndPathMatcher(
  uMaxThreads,
  asFolderPaths,
  bRecursive,
  arPathRegExps, arNegativePathRegExps,
  arNameRegExps, arNegativeNameRegExps,
  bVerbose,
):
  oMatcher = cMultithreadedFileNameAndPathMatcher(
    uMaxThreads,
    asFolderPaths,
    bRecursive,
    arPathRegExps, arNegativePathRegExps,
    arNameRegExps, arNegativeNameRegExps,
    bVerbose,
  );
  return oMatcher.oMatchesByFilePath.dxValue;  

def fVerboseOutputHelper(b0Selected, sItemPath, sRegExpType, rRegExp, o0Match):
  oConsole.fLock();
  try:
    oConsole.fOutput(
      "  ", 
      [COLOR_SELECT_MAYBE, CHAR_SELECT_MAYBE] if b0Selected is None else
      [COLOR_SELECT_YES, CHAR_SELECT_YES] if b0Selected else
      [COLOR_SELECT_NO, CHAR_SELECT_NO],
      COLOR_NORMAL, " ", sItemPath,
      COLOR_DIM, " (",
      "matches" if o0Match else "does not match",
      " ", sRegExpType, " reg.exp. ", str(rRegExp.pattern),
      ")",
    );
    if o0Match and len(o0Match.groups()):
      asSubMatchesOutput = [];
      for sSubMatch in oMatch.groups():
        asSubMatchesOutput += [", " if len(asSubMatchesOutput) else "", COLOR_NORMAL, sSubMatch, COLOR_DIM];
      oConsole.fOutput(COLOR_DIM, "    Sub-matches: ", asSubMatchesOutput, ".");
  finally:
    oConsole.fUnlock();

class cMultithreadedFileNameAndPathMatcher(object):
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
    
    oSelf.oMatchesByFilePath = cDict();
    oSelf.oException = None;
    oSelf.oNumberOfFilesFound = cCounter();
    oSelf.oNumberOfFoldersFound = cCounter();
    oSelf.oNumberOfItemsFound = cCounter(0);
    oSelf.oNumberOfItemsCompleted = cCounter();
    oSelf.oScanThreadsStarted = cCounter(uMaxThreads);
    oSelf.oScanThreadsFinished = cCounter(0);
    
    if oSelf.bVerbose:
      oConsole.fOutput(
        COLOR_BUSY, CHAR_BUSY,
        COLOR_NORMAL, " Scanning ",
        COLOR_INFO, str(len(asFolderPaths)),
        COLOR_NORMAL, " folder paths", " (and descendants)" if bRecursive else "", "...",
      );
    for sFolderPath in set(asFolderPaths):
      oSelf.oNumberOfItemsFound.fuIncrease();
      if os.path.isdir(sFolderPath):
        oSelf.oUnhandledItemPathsQueue.put(sFolderPath);
        oSelf.fDebug();
      else:
        oSelf.oNumberOfItemsCompleted.fuIncrease();
        oSelf.fDebug();
    
    aoThreads = [
      cThread(oSelf.fScanThread)
      for x in range(uMaxThreads)
    ] + [
      cThread(oSelf.fStatusThread)
    ];
    
    for oThread in aoThreads:
      oThread.fStart(bVital = False);
    for oThread in aoThreads:
      oThread.fWait();
  
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
  
  def fHandleFile(oSelf, sFilePath):
    o0LastNameMatch = None;
    o0LastPathMatch = None;
    # Having no reg.exps. means always add:
    if (
      oSelf.arPathRegExps or oSelf.arNegativePathRegExps
      or oSelf.arNameRegExps or oSelf.arNegativeNameRegExps
    ):
      if oSelf.arNameRegExps or oSelf.arNegativeNameRegExps:
        sItemName = os.path.basename(sFilePath);
      # Having negative reg.exps. means not add if matched:
      for rNegativePathRegExp in oSelf.arNegativePathRegExps:
        o0Match = rNegativePathRegExp.search(sFilePath)
        if o0Match:
          # Matching negative reg.exp. means don't add (and stop matching).
          if oSelf.bVerbose:
            fVerboseOutputHelper(False, sFilePath, "negative path", rNegativePathRegExp, o0Match);
          return;
      for rNegativeNameRegExp in oSelf.arNegativeNameRegExps:
        o0Match = rNegativeNameRegExp.search(sItemName);
        if o0Match:
          # Matching negative reg.exp. means don't add (and stop matching).
          if oSelf.bVerbose:
            fVerboseOutputHelper(False, sFilePath, "negative name", rNegativeNameRegExp, o0Match);
          return;
      # Not matching negative reg.exp. means maybe add:
      # Not having positive reg.exps. means add:
      # Having positive reg.exps. means add if matches all:
      if oSelf.arPathRegExps:
        for rPathRegExp in oSelf.arPathRegExps:
          o0Match = rPathRegExp.search(sFilePath);
          if oSelf.bVerbose:
            fVerboseOutputHelper(None if o0Match else False, sFilePath, "path", rPathRegExp, o0Match);
          if o0Match:
            o0LastPathMatch = o0Match;
          else:
            return;
      if oSelf.arNameRegExps:
        for rNameRegExp in oSelf.arNameRegExps:
          o0Match = rNameRegExp.search(sItemName);
          if oSelf.bVerbose:
            fVerboseOutputHelper(None if o0Match else False, sFilePath, "name", rNameRegExp, o0Match);
          if o0Match:
            o0LastNameMatch = o0Match;
          else:
            return;
      if oSelf.bVerbose:
        sMatchedExpressionTypes = " and ".join([s for s in [
          "path" if oSelf.arPathRegExps else None,
          "name" if oSelf.arNameRegExps else None,
        ] if s]);
        oConsole.fOutput(
          "  ",
          COLOR_SELECT_YES, CHAR_SELECT_YES,
          COLOR_NORMAL, " ", sFilePath,
          COLOR_DIM, " (matches all ", sMatchedExpressionTypes, " reg.exp.)",
        );
    elif oSelf.bVerbose:
      oConsole.fOutput(
        "  ",
        COLOR_SELECT_YES, CHAR_SELECT_YES,
        COLOR_NORMAL, " ", sFilePath,
      );
    oSelf.oMatchesByFilePath.fSet(sFilePath, (o0LastNameMatch, o0LastPathMatch));
  
  def fHandleFolder(oSelf, sFolderPath, asSubItemNames):
    # Having no reg.exps. means always add:
    if (
      oSelf.arPathRegExps or oSelf.arNegativePathRegExps
      or oSelf.arNameRegExps or oSelf.arNegativeNameRegExps
    ):
      # Having negative path reg.exps. means not add if matched:
      for rNegativePathRegExp in oSelf.arNegativePathRegExps:
        oMatch = rNegativePathRegExp.search(sFolderPath);
        if oMatch:
          # Matching negative path reg.exp. means don't add and files in this folder (and stop matching).
          if oSelf.bVerbose:
            fVerboseOutputHelper(False, sFolderPath + "\\*", "negative path", rNegativePathRegExp, oMatch);
          return;
      # Not matching negative path reg.exp. means maybe add:
      # Having positive reg.exps. means add if matches all:
      if oSelf.arPathRegExps:
        for rPathRegExp in oSelf.arPathRegExps:
          oMatch = rPathRegExp.search(sFolderPath);
          if not oMatch:
            if oSelf.bVerbose:
              fVerboseOutputHelper(False, sFolderPath + "\\*", "path", rPathRegExp, None);
            return;
    if oSelf.bVerbose:
      oConsole.fOutput(
        "  ",
        COLOR_BUSY, CHAR_BUSY,
        COLOR_NORMAL, " Scanning ",
        COLOR_INFO, str(len(asSubItemNames)),
        COLOR_NORMAL, " descendants of folder ",
        COLOR_INFO, sFolderPath,
        COLOR_DIM, " (matches all path reg.exp.)",
      );
    oSelf.oNumberOfItemsFound.fuAdd(len(asSubItemNames));
    for sSubItemName in asSubItemNames:
      sSubItemPath = os.path.join(sFolderPath, sSubItemName);
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
        nSubProgress = 1.0 * oSelf.oMatchesByFilePath.uSize / uNumberOfFilesFound if uNumberOfFilesFound else 0;
        oConsole.fProgressBar(
          nProgress,
          [
            "Matched ",
            " and ".join([s for s in [
              "path" if bMatchingPath else None,
              "name" if bMatchingName else None,
            ] if s]),
            " for ", str(oSelf.oMatchesByFilePath.uSize), "/", str(uNumberOfFilesFound), " files",
          ] if bMatchingPathOrName else [
            "Found ", str(uNumberOfFilesFound), " files",
          ],
          " (", str(uNumberOfItemsRemaining), "/", str(uNumberOfItemsFound), " items remaining)",
          nSubProgress = nSubProgress,
        );
        time.sleep(0.25);
    except Exception as oException:
      oSelf.oException = oException;
      raise;
