import math, os, Queue, re, threading, time;
from cCounter import cCounter;
from cList import cList;
from mColors import *;
from oConsole import oConsole;
bDebug = False;

def foMultithreadedFileContentMatcher(uMaxThreads, asFilePaths, arContentRegExps, arNegativeContentRegExps, bUnicode, uNumberOfRelevantLinesBeforeMatch, uNumberOfRelevantLinesAfterMatch):
  oScanner = cMultithreadedFileContentMatcher(uMaxThreads, asFilePaths, arContentRegExps, arNegativeContentRegExps, bUnicode, uNumberOfRelevantLinesBeforeMatch, uNumberOfRelevantLinesAfterMatch);
  return oScanner;

class cMultithreadedFileContentMatcher(object):
  def __init__(oSelf, uMaxThreads, asFilePaths, arContentRegExps, arNegativeContentRegExps, bUnicode, uNumberOfRelevantLinesBeforeMatch, uNumberOfRelevantLinesAfterMatch):
    oSelf.asFilePaths = asFilePaths;
    oSelf.arContentRegExps = arContentRegExps;
    oSelf.arNegativeContentRegExps = arNegativeContentRegExps;
    oSelf.bUnicode = bUnicode;
    oSelf.uNumberOfRelevantLinesBeforeMatch = uNumberOfRelevantLinesBeforeMatch;
    oSelf.uNumberOfRelevantLinesAfterMatch = uNumberOfRelevantLinesAfterMatch;
    oSelf.uNumberOfFiles = len(asFilePaths);
    oSelf.uScannedBytes = 0;
    oSelf.oException = None;
    oSelf.oasNotScannedFilePaths = cList();
    oSelf.dMatched_auLineNumbers_by_sFilePath = {};
    oSelf.dRelevant_asLines_by_uLineNumber_by_sFilePath = {};
    oSelf.oScanThreadsStarted = cCounter(uMaxThreads);
    oSelf.oScanThreadsFinished = cCounter(0);
    oSelf.oFilePathsQueue = Queue.Queue();
    oSelf.oFileScansStarted = cCounter(0);
    oSelf.oFileScansFinished = cCounter(0);
    for sFilePath in oSelf.asFilePaths:
      oSelf.oFilePathsQueue.put(sFilePath);
    oSelf.fDebug("initialized");
    
    aoThreads = [
      threading.Thread(target = oSelf.fScanThread)
      for x in xrange(uMaxThreads)
    ] + [
      threading.Thread(target = oSelf.fStatusThread)
    ];
    for oThread in aoThreads:
      oThread.start();
    for oThread in aoThreads:
      oThread.join();
    oSelf.fDebug("Finished scanning");
    oSelf.asNotScannedFilePaths = oSelf.oasNotScannedFilePaths.axValue;
  
  def fDebug(oSelf, sStatus):
    if bDebug:
      oConsole.fPrint("%d/%d/%d %s" % (oSelf.oFileScansStarted.uValue, oSelf.oFileScansFinished.uValue, oSelf.uNumberOfFiles, sStatus));
  
  def fScanThread(oSelf):
    try:
      while oSelf.oFileScansFinished.uValue < oSelf.uNumberOfFiles and not oSelf.oException:
        sFilePath = oSelf.oFilePathsQueue.get();
        if sFilePath is None:
          break;
        oSelf.oFileScansStarted.fuIncrease();
        oSelf.fDebug("start scan (%s)" % sFilePath);
        nStartTime = time.clock();
        fnScanTime = lambda: time.clock() - nStartTime;
        try:
          oFile = open(sFilePath, "rb");
        except Exception, oException:
          oSelf.oasNotScannedFilePaths.fAdd(sFilePath);
          oSelf.oFileScansFinished.fuIncrease();
          oSelf.fDebug("stop scan: can't open %s (%fs)" % (sFilePath, fnScanTime()));
          continue;
        if oSelf.oException: return;
        try:
          sContent = oFile.read();
        except Exception, oException:
          oSelf.oasNotScannedFilePaths.fAdd(sFilePath);
          oSelf.oFileScansFinished.fuIncrease();
          oSelf.fDebug("stop scan: can't read %s (%fs)" % (sFilePath, fnScanTime()));
          continue;
        finally:
          oFile.close();
        oSelf.uScannedBytes += len(sContent);
        if oSelf.bUnicode:
          sContent = sContent.replace("\0", "");
        if oSelf.oException: return;
        bNegativeMatch = False;
        for rNegativeContentRegExp in oSelf.arNegativeContentRegExps:
          if oSelf.oException: return;
          oMatch = rNegativeContentRegExp.search(sContent)
          if oMatch:
            bNegativeMatch = True;
            oSelf.fDebug("stop scan: !/%s/ => %s in %s (%fs)" % (rNegativeContentRegExp.pattern, repr(oMatch.group(0)), sFilePath, fnScanTime()));
            break; # If it matches a negative reg.exp., stop.
          oSelf.fDebug("scan: no match for !/%s/ in %s" % (rNegativeContentRegExp.pattern, sFilePath));
        if bNegativeMatch:
          oSelf.oFileScansFinished.fuIncrease();
          continue;
        # If it does not match any negative reg.exp. look for normal reg.exps. if provided, or match immediately
        if not oSelf.arContentRegExps:
          oSelf.dMatched_auLineNumbers_by_sFilePath[sFilePath] = set([0]);
          oSelf.oFileScansFinished.fuIncrease();
          oSelf.fDebug("stop scan: no negative matched means matched in %s (%fs)" % (sFilePath, fnScanTime()));
          continue;
        bSaveRelevantLines = oSelf.uNumberOfRelevantLinesBeforeMatch is not None or oSelf.uNumberOfRelevantLinesAfterMatch is not None;
        if bSaveRelevantLines:
          oSelf.dRelevant_asLines_by_uLineNumber_by_sFilePath[sFilePath] = {};
        auLineNumbers = set();
        for rContentRegExp in oSelf.arContentRegExps:
          bFound = False;
          for oMatch in rContentRegExp.finditer(sContent):
            bFound = True;
            if oSelf.oException: return;
            uCurrentLineStartIndex = sContent.rfind("\n", 0, oMatch.start()) + 1;
            uCurrentLineNumber = sContent.count("\n", 0, uCurrentLineStartIndex) + 1;
            # Mark the line on which the match starts
            auLineNumbers.add(uCurrentLineNumber);
            # Mark all additional lines in the match as well.
            uMatchedLinesCount = sContent.count("\n", oMatch.start(), oMatch.end()) + 1;
            for uMatchedLineCount in xrange(uMatchedLinesCount):
              auLineNumbers.add(uCurrentLineNumber + uMatchedLineCount);
            oSelf.fDebug("scan: matched /%s/ on line #%d in %s (%fs)" % (rContentRegExp.pattern, uCurrentLineNumber, sFilePath, fnScanTime()));
            if bSaveRelevantLines:
              # Find the start of the first relevant line, by finding the start of the line on which the match starts
              # and going back the requested number of lines, if possible.
              if oSelf.uNumberOfRelevantLinesBeforeMatch:
                for x in xrange(oSelf.uNumberOfRelevantLinesBeforeMatch):
                  if uCurrentLineStartIndex == 0:
                    break;
                  uCurrentLineStartIndex = sContent.rfind("\n", 0, uCurrentLineStartIndex - 1) + 1;
                  uCurrentLineNumber -= 1;
              oSelf.fDebug("scan:   start relevant lines at #%d in %s (%fs)" % (uCurrentLineNumber, sFilePath, fnScanTime()));
              # Find the end of the last relevant line, by adding lines until we reach the end of the match and then
              # continue for the requested number of lines, if possible.
              uAdditionalLinesToAddAfterMatch = oSelf.uNumberOfRelevantLinesAfterMatch or 0;
              while uCurrentLineStartIndex < oMatch.end() or uAdditionalLinesToAddAfterMatch > 0:
                uCurrentLineEndIndex = sContent.find("\n", uCurrentLineStartIndex);
                if uCurrentLineEndIndex == - 1:
                  uAdditionalLinesToAddAfterMatch = 0;
                  uCurrentLineEndIndex = len(sContent);
                sCurrentLine = sContent[uCurrentLineStartIndex:uCurrentLineEndIndex].rstrip("\r");
                oSelf.dRelevant_asLines_by_uLineNumber_by_sFilePath[sFilePath][uCurrentLineNumber] = sCurrentLine;
                oSelf.fDebug("scan:   relevant line at #%d in %s" % (uCurrentLineNumber, sFilePath));
                uCurrentLineNumber += 1;
                if uCurrentLineStartIndex >= oMatch.end():
                  uAdditionalLinesToAddAfterMatch -= 1;
                uCurrentLineStartIndex = uCurrentLineEndIndex + 1;
          if not bFound:
            oSelf.fDebug("scan: no match for /%s/ in %s (%fs)" % (rContentRegExp.pattern, sFilePath, fnScanTime()));
            auLineNumbers = [];
            break;
        if auLineNumbers:
          oSelf.dMatched_auLineNumbers_by_sFilePath[sFilePath] = sorted(list(auLineNumbers));
        oSelf.oFileScansFinished.fuIncrease();
        oSelf.fDebug("scan done (%fs)" % fnScanTime());
    except Exception as oException:
      oSelf.oException = oException;
      raise;
    finally:
      uFinished = oSelf.oScanThreadsFinished.fuIncrease();
#      oConsole.fPrint("Scan thread %d/%d done" % (uFinished, oSelf.oScanThreadsStarted.uValue));
      oSelf.oFilePathsQueue.put(None);
  
  def fStatusThread(oSelf):
    try:
      while oSelf.oScanThreadsStarted.uValue != oSelf.oScanThreadsFinished.uValue and not oSelf.oException:
        nProgress = 1.0 * oSelf.oFileScansFinished.uValue / oSelf.uNumberOfFiles;
        sStatus = "Matched content in %d files (%d/%d remaining)" % (
          len(oSelf.dMatched_auLineNumbers_by_sFilePath),
          oSelf.uNumberOfFiles - oSelf.oFileScansFinished.uValue,
          oSelf.uNumberOfFiles,
        );
        oConsole.fProgressBar(nProgress,  sStatus);
        time.sleep(0.25);
    except Exception as oException:
      oSelf.oException = oException;
      raise;
#    finally:
#      oConsole.fPrint("status thread done");
