import json, math, multiprocessing, os, re, sys;

"""
          dS'                          dS'                                      
         dS' .cid ,dSSc  ,dS"*sd      dS'   /R/egular expression /S/earch       
        dS'    SS;' '*'  YS(   Y     dS'                                        
       dS'     SS`        `*%s,     dS'                                         
      dS'      SS        b   )Sb   dS'                                          
     dS'     .dSSb.      P*ssSP'  dS'                                           
    dS'                          dS'                                            
""";
# Running this script will return an exit code, which translates as such:
# 0 = executed successfully, no matches found.
# 1 = executed successfully, matches found.
# 2 = bad arguments
# 3 = internal error
# 4 = not used

from fCheckDependencies import fCheckDependencies;
fCheckDependencies();
try:
  import mDebugOutput;
except:
  mDebugOutput = None;

try:
  from oConsole import oConsole;
  import mWindowsAPI;
  
  from fCheckPythonVersion import fCheckPythonVersion;
  from fdoMultithreadedFilePathMatcher import fdoMultithreadedFilePathMatcher;
  from foMultithreadedFileContentMatcher import foMultithreadedFileContentMatcher;
  from fPrintLogo import fPrintLogo;
  from fPrintUsageInformation import fPrintUsageInformation;
  from fPrintVersionInformation import fPrintVersionInformation;
  from mColors import *;
  
  asTestedPythonVersions = ["2.7.14", "2.7.15", "2.7.16", "2.7.17"];
  
  sComSpec = unicode(os.environ["COMSPEC"]);
  uMaxThreads = max(1, multiprocessing.cpu_count() - 1);
  
  def fsBytes(nValue):
    asUnits = ["bytes", "kB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB"];
    nValue = float(nValue);
    for uUnitIndex in range(0, len(asUnits)):
      if nValue < 9999:
        break;
      nValue /= 1000.0;
    sValue = str(math.floor(nValue * 100) / 100.0);
    return sValue + " " + asUnits[uUnitIndex];
  
  def fRunCommand(asCommandTemplate, sFilePath, oPathMatch, auLineNumbers = []):
    asCommandTemplate = [unicode(s) for s in asCommandTemplate];
    sDrivePath, sNameExtension = sFilePath.rsplit(u"\\", 1);
    if u":" in sDrivePath:
      sDrive, sPath = sDrivePath.split(u":", 1);
      if sDrive.startswith(u"\\\\?\\"):
        sDrive = sDrive[4:];
      sDrive += ":";
    else:
      sDrive, sPath = u"", sDrivePath;
    if u"." in sNameExtension:
      sName, sExtension = sNameExtension.rsplit(u".", 1);
      sExtension = "." + sExtension;
    else:
      sName, sExtension = sNameExtension, u"";
    def fsSubstitudePathTemplates(oMatch):
      sEscape, sDoNotQuote, sChars = oMatch.groups();
      if sEscape:
        return u"{" + sDoNotQuote + sChars + u"}"; # do not replace.
      if sChars == u"l":
        if fsSubstitudePathTemplates.uCurrentLineNumberIndex < len(auLineNumbers):
          fsSubstitudePathTemplates.uCurrentLineNumberIndex += 1;
          return u"%d" % auLineNumbers[fsSubstitudePathTemplates.uCurrentLineNumberIndex - 1];
        return u"-1";
      if sChars[0] in u"0123456789":
        uIndex = long(sChars);
        try:
          sSubstitute = oPathMatch.group(uIndex);
        except IndexError:
          sSubstitute = u"";
      else:
        sSubstitute = u"";
        dsReplacements = {
          u"f": sFilePath,
          u"d": sDrive or u"",
          u"p": sPath or u"",
          u"n": sName or u"",
          u"x": sExtension or u"",
        };
        sLastChar = "";
        for sChar in sChars:
          if sChar == u"n" and sLastChar == u"p":
            sSubstitute += u"\\"
          sSubstitute += dsReplacements[sChar];
          sLastChar = sChar;
      if sDoNotQuote == u"":
        sSubstitute = u'"%s"' % sSubstitute.replace(u"\\", u"\\\\").replace(u'"', u'\\"');
      return sSubstitute;
    fsSubstitudePathTemplates.uCurrentLineNumberIndex = 0;
    
    asCommandLine = [
      # match everything "{" replacement "}", and note if "{" is escaped as "\\{"
      re.sub(ur"(\\)?\{(~?)(l|[0-9]+|[fdpnx]+)\}", fsSubstitudePathTemplates, sTemplate)
      for sTemplate in asCommandTemplate
    ];
    oProcess = mWindowsAPI.cConsoleProcess.foCreateForBinaryPathAndArguments(
      sBinaryPath = sComSpec,
      asArguments = [u"/C"] + asCommandLine,
      bRedirectStdOut = False,
      bRedirectStdErr = False,
    );
    oProcess.fbWait();
  
  def frRegExp(sRegExp, sFlags):
    return re.compile(unicode(sRegExp), sum([
      {"i": re.I, "l":re.L, "m":re.M, "s": re.S, "u": re.U, "x": re.X}[sFlag]
      for sFlag in sFlags
    ]));
  
  # Make sure the Python binary is up to date; we don't want our users to unknowingly run outdated software as this is
  # likely to cause unexpected issues.
  fCheckPythonVersion("rs", asTestedPythonVersions, "https://github.com/SkyLined/rs/issues/new")
  
  doPathMatch_by_sSelectedFilePath = {};
  asFolderPaths = set();
  arContentRegExps = [];
  arNegativeContentRegExps = [];
  arPathRegExps = [];
  arNegativePathRegExps = [];
  bRecursive = False;
  bVerbose = False;
  bWait = False;
  bUnicode = False;
  bQuiet = False;
  uConvertTabsToSpaces = 4;
  uNumberOfRelevantLinesBeforeMatch = None;
  uNumberOfRelevantLinesAfterMatch = None;
  bRegExpArgsAreForPath = False;
  bArgIsConvertTabsToSpaces = False;
  bArgIsNumberOfRelevantLinesAroundMatch = False;
  bArgsAreCommandTemplate = False;
  asCommandTemplate = [];
  for sArg in sys.argv[1:]:
    if bArgIsConvertTabsToSpaces:
      try:
        uConvertTabsToSpaces = long(sArg);
      except Exception as oException:
        oConsole.fPrint(ERROR, "Invalid tabs length ", ERROR_INFO, sArg, ERROR, ": ", ERROR_INFO, oException.message, ERROR, ".");
        os._exit(2);
      continue;
    if bArgIsNumberOfRelevantLinesAroundMatch:
      # valid formats : "C" "-B", "-B+A" "+A"
      oBeforeAfterMatch = re.match(r"^(?:(\d+)|(?:\-(\d+))?(?:(?:,|,?\+)(\d+))?)$", sArg);
      if not oBeforeAfterMatch:
        oConsole.fPrint(ERROR, "Invalid lines range ", ERROR_INFO, sArg, ERROR, ".");
        oConsole.fPrint("Try ", INFO, "N", NORMAL, ", ", INFO, "-N", NORMAL, ", ", INFO, "-N+N", NORMAL, ", or ", INFO, "+N", NORMAL, ".");
        oConsole.fPrint("Where each N is an integer. '-' prefix indicates before, '+' prefix indices after the match.");
        os._exit(2);
      suBeforeAndAfer, suBefore, suAfter = oBeforeAfterMatch.groups();
      if suBeforeAndAfer:
        uNumberOfRelevantLinesBeforeMatch = uNumberOfRelevantLinesAfterMatch = long(suBeforeAndAfer);
      else:
        uNumberOfRelevantLinesBeforeMatch = long(suBefore or 0);
        uNumberOfRelevantLinesAfterMatch = long(suAfter or 0);
      bArgIsNumberOfRelevantLinesAroundMatch = False;
      continue;
    if bArgsAreCommandTemplate:
      asCommandTemplate.append(sArg);
      continue;
    oRegExpMatch = re.match(r"^(!)?\/(.*)\/([ilmsux]*)$", sArg);
    if oRegExpMatch:
      sNegative, sRegExp, sFlags = oRegExpMatch.groups();
      try:
        rRegExp = frRegExp(sRegExp, sFlags);
      except Exception, oException:
        oConsole.fPrint(ERROR, "Invalid regular expressions ", ERROR_INFO, sNegative or "", ERROR, "/", ERROR_INFO, \
            sRegExp, ERROR, "/", ERROR_INFO, sFlags);
        oConsole.fPrint("     ", ERROR_INFO, oException.message, ERROR, ".");
        os._exit(2);
      else:
        if bRegExpArgsAreForPath:
          if sNegative:
            arNegativePathRegExps.append(rRegExp);
          else:
            arPathRegExps.append(rRegExp);
        else:
          if sNegative:
            arNegativeContentRegExps.append(rRegExp);
          else:
            arContentRegExps.append(rRegExp);
    elif sArg == "?":
      bFirst = True;
      while 1:
        sRegExp = raw_input("Enter %s file %s regular expression or string: " % (
            bFirst and "a" or "another",
            bRegExpArgsAreForPath and "path" or "content"
        ));
        bFirst = False;
        if sRegExp in ["", "-"]:
          break;
        oRegExpMatch = re.match(r"^(!)?\/(.*)\/([ilmsux]*)$", sRegExp);
        if not oRegExpMatch:
          # Not a regular expression - use as string
          sRegExp = re.escape(sRegExp);
          sFlags = "";
        else:
          sNegative, sRegExp, sFlags = oRegExpMatch.groups();
        try:
          rRegExp = frRegExp(sRegExp, sFlags);
        except Exception, oException:
          oConsole.fPrint(ERROR, "Invalid regular expressions ", ERROR_INFO, sNegative, ERROR, "/", ERROR_INFO, \
              sRegExp, ERROR, "/", ERROR_INFO, sFlags, ERROR, ": ", ERROR_INFO, oException.message, ERROR, ".");
        else:
          if bRegExpArgsAreForPath:
            if sNegative:
              arNegativePathRegExps.append(rRegExp);
            else:
              arPathRegExps.append(rRegExp);
          else:
            if sNegative:
              arNegativeContentRegExps.append(rRegExp);
            else:
              arContentRegExps.append(rRegExp);
    else:
      # Only regular expressions and "?" immediately following the -p argument should be matched to the path; this
      # allow you to do -p /path_reg_exp/ -r /content_reg_exp/
      bRegExpArgsAreForPath = False;
      if sArg in ["-?", "-h", "--help", "/?", "/h", "/help"]:
        fPrintLogo();
        fPrintUsageInformation();
        os._exit(0);
      elif sArg in ["-r", "/r", "--recursive", "/recursive"]:
        bRecursive = True;
      elif sArg in ["-v", "/v", "--verbose", "/verbose"]:
        bVerbose = True;
      elif sArg in ["-w", "/w", "--wait", "/wait"]:
        bWait = True;
      elif sArg in ["-u", "/u", "--unicode", "/unicode"]:
        bUnicode = True;
      elif sArg in ["-q", "/q", "--quiet", "/quiet"]:
        bQuiet = True;
      elif sArg in ["--version", "/version"]:
        fPrintVersionInformation(
          bCheckForUpdates = True,
          bCheckAndShowLicenses = True,
          bShowInstallationFolders = True,
        );
        os._exit(0);
      elif sArg in ["-p", "--path", "/p", "/path"]:
        bRegExpArgsAreForPath = True;
      elif sArg in ["-c", "--content", "/c", "/content"]:
        bRegExpArgsAreForPath = False;
      elif sArg in ["-t", "--tabs", "/t", "/tabs"]:
        bArgIsConvertTabsToSpaces = True;
      elif sArg in ["-l", "--lines", "/l", "/lines"]:
        bArgIsNumberOfRelevantLinesAroundMatch = True;
      elif sArg in ["--"]:
        bArgsAreCommandTemplate = True;
      elif os.path.isfile(sArg):
        doPathMatch_by_sSelectedFilePath[sArg] = None; # User supplied; no regular expression match
      elif os.path.isdir(sArg):
        asFolderPaths.add(sArg);
      else:
        oConsole.fPrint(ERROR, "Unknown argument: ", ERROR_INFO, sArg, ERROR, ".");
        os._exit(2);
  
  # Check arguments and set some defaults
  if bArgsAreCommandTemplate and not asCommandTemplate:
    if not arContentRegExps:
      asCommandTemplate = [u"uedit64.exe", u"{f}"];
    else:
      asCommandTemplate = [u"uedit64.exe", u'"{~f}/{l}"']; # line number must be inside quotes
  if not arContentRegExps and not arNegativeContentRegExps and not arPathRegExps and not arNegativePathRegExps:
    oConsole.fPrint(ERROR, "Missing regular expression");
    os._exit(2);
  if not doPathMatch_by_sSelectedFilePath and not asFolderPaths:
    asFolderPaths.add(os.getcwdu());
  if bRecursive:
    if not asFolderPaths:
      oConsole.fPrint(ERROR, "No folders to scan recursively");
      os._exit(2);
  if bArgIsNumberOfRelevantLinesAroundMatch:
    oConsole.fPrint(ERROR, "missing number of matched lines to show");
    os._exit(2);
  
  # Show argument values in verbose mode
  if bVerbose:
    if asFolderPaths:
      oConsole.fPrint("+ Selected folders:");
      for sFolderPath in asFolderPaths:
        oConsole.fPrint("  + ", sFolderPath);
    if bRecursive:
      oConsole.fPrint("+ Folders will be traversed recursively");
    
    if doPathMatch_by_sSelectedFilePath:
      oConsole.fPrint("+ Selected files:");
      for sFilePath in sorted(doPathMatch_by_sSelectedFilePath.keys()):
        oConsole.fPrint("  + ", sFilePath);
    if arPathRegExps or arNegativePathRegExps:
      oConsole.fPrint("+ File path regular expressions:");
    for rNegativePathRegExp in arNegativePathRegExps:
      oConsole.fPrint("  - ", json.dumps(rNegativePathRegExp.pattern)[1:-1]);
    for rPathRegExp in arPathRegExps:
      oConsole.fPrint("  + ", json.dumps(rPathRegExp.pattern)[1:-1]);
    
    if arContentRegExps or arNegativeContentRegExps:
      oConsole.fPrint("+ File content regular expressions:");
    for rNegativeContentRegExp in arNegativeContentRegExps:
      oConsole.fPrint("  - ", json.dumps(rNegativeContentRegExp.pattern)[1:-1]);
    for rContentRegExp in arContentRegExps:
      oConsole.fPrint("  + ", json.dumps(rContentRegExp.pattern)[1:-1]);
    if bUnicode:
      oConsole.fPrint("+ All '\\0' characters will be removed from the file contents before scanning,");
      oConsole.fPrint("  to convert UTF-16 Unicode encoded ASCII characters back to ASCII.");
    if asCommandTemplate:
      oConsole.fPrint("+ Command to be executed for each matched file:");
      oConsole.fPrint(u"  ", " ".join(asCommandTemplate));
    if bWait:
      oConsole.fPrint("+ After scanning is complete, wait for the user to press ENTER.");
  
  if asFolderPaths:
    doPathMatch_by_sSelectedFilePath.update(fdoMultithreadedFilePathMatcher(uMaxThreads, asFolderPaths, bRecursive, arPathRegExps, arNegativePathRegExps, bVerbose));
  if not doPathMatch_by_sSelectedFilePath:
    if arPathRegExps or arNegativePathRegExps:
      oConsole.fPrint(ERROR, "No files found that matched any of the path regular expressions.");
    else:
      oConsole.fPrint(ERROR, "No files found.");
    uResult = 0;
  elif not arContentRegExps and not arNegativeContentRegExps:
    for sFilePath in sorted(doPathMatch_by_sSelectedFilePath.keys()):
      oConsole.fPrint(sFilePath); # Strip "\\?\"
      if bArgsAreCommandTemplate:
        oPathMatch = doPathMatch_by_sSelectedFilePath[sFilePath];
        fRunCommand(asCommandTemplate, sFilePath, oPathMatch);
    uResult = len(doPathMatch_by_sSelectedFilePath) > 0 and 1 or 0;
  else:
    oContentMatchingResults = foMultithreadedFileContentMatcher(uMaxThreads, doPathMatch_by_sSelectedFilePath.keys(), arContentRegExps, arNegativeContentRegExps, bUnicode, uNumberOfRelevantLinesBeforeMatch, uNumberOfRelevantLinesAfterMatch);
    if bVerbose:
      for sFilePath in oContentMatchingResults.asNotScannedFilePaths:
        oConsole.fPrint(DIM, "- ", sFilePath);
    if not oContentMatchingResults.dMatched_auLineNumbers_by_sFilePath:
      if arPathRegExps or arNegativePathRegExps:
        oConsole.fPrint(ERROR, "No match found in %d files that matched the path regular expressions." % len(doPathMatch_by_sSelectedFilePath));
      else:
        oConsole.fPrint(ERROR, "No match found in any files.");
      uResult = 0;
    else:
      uResult = 1;
      bFirst = True;
      bOutputRelevantLines = uNumberOfRelevantLinesBeforeMatch is not None or uNumberOfRelevantLinesAfterMatch is not None;
      for sFilePath in sorted(oContentMatchingResults.dMatched_auLineNumbers_by_sFilePath.keys()):
        auMatchedLineNumbers = sorted(oContentMatchingResults.dMatched_auLineNumbers_by_sFilePath[sFilePath]);
        if not bQuiet:
          if not bOutputRelevantLines:
            oConsole.fPrint(
              FILE_NAME, sFilePath,
              FILE_LINENO, "/", ",".join([str(u) for u in auMatchedLineNumbers]),
            );
          else:
            if bFirst:
              bFirst = False;
            else:
              # Separator between results for different files.
              oConsole.fPrint();
            uNextMatchedLineIndex = 0;
            oConsole.fPrint(
              FILE_BOX, " ",
              FILE_BOX_NAME, sFilePath,
              FILE_BOX_LINENO, "/%d" % auMatchedLineNumbers[uNextMatchedLineIndex],
              FILE_BOX, sPadding = " ",
            );
            auRelevantLineNumbers = sorted(oContentMatchingResults.dRelevant_asLines_by_uLineNumber_by_sFilePath[sFilePath].keys());
            uPreviousLineNumber = None;
            for uRelevantLineNumber in auRelevantLineNumbers:
              # Seperator between non-sequential sections of file.
              if uPreviousLineNumber is not None and uRelevantLineNumber > uPreviousLineNumber + 1:
                oConsole.fPrint(
                  FILE_BOX, " ",
                  FILE_CUT_LINENO_COLOMN, "\xFA" * 6,
                  LINENO_CONTENT_SEPARATOR, ":",
                  FILE_CUT_NAME, " ", sFilePath,
                  FILE_CUT_LINENO, "/%d" % auMatchedLineNumbers[uNextMatchedLineIndex],
                  FILE_CUT_PAD, " ", sPadding = "\xFA",
               );
              sRelevantLine = oContentMatchingResults.dRelevant_asLines_by_uLineNumber_by_sFilePath[sFilePath][uRelevantLineNumber];
              bMatchedLine = uNextMatchedLineIndex < len(auMatchedLineNumbers) and uRelevantLineNumber == auMatchedLineNumbers[uNextMatchedLineIndex];
              if bMatchedLine:
                uNextMatchedLineIndex += 1;
              oConsole.fPrint(
                FILE_BOX, " ",
                bMatchedLine and LINENO_COLOMN_MATCH or LINENO_COLOMN, "%6d" % uRelevantLineNumber,
                LINENO_CONTENT_SEPARATOR, "\xB3",
                bMatchedLine and CONTENT_MATCH or CONTENT, sRelevantLine,
                CONTENT_EOL, "\x1B\xD9",
                uConvertTabsToSpaces = uConvertTabsToSpaces,
              );
              uPreviousLineNumber = uRelevantLineNumber;
        if bArgsAreCommandTemplate:
          oPathMatch = doPathMatch_by_sSelectedFilePath[sFilePath];
          fRunCommand(asCommandTemplate, sFilePath, oPathMatch, auMatchedLineNumbers);
      if not bFirst:
        oConsole.fPrint();
    if bVerbose:
      if oContentMatchingResults.asNotScannedFilePaths > 0:
        oConsole.fPrint("Scanned %d/%d files, %s bytes." % (
            len(doPathMatch_by_sSelectedFilePath) - len(oContentMatchingResults.asNotScannedFilePaths), len(doPathMatch_by_sSelectedFilePath), fsBytes(oContentMatchingResults.uScannedBytes)));
      else:
        oConsole.fPrint("Scanned %d files, %s bytes." % (len(doPathMatch_by_sSelectedFilePath), fsBytes(oContentMatchingResults.uScannedBytes)));
  if bWait:
    raw_input();
  os._exit(uResult);

except Exception as oException:
  if mDebugOutput:
    mDebugOutput.fTerminateWithException(oException);
  raise;