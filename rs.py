import json, math, multiprocessing, os, re, sys;

# Augment the search path: look in main folder, parent folder or "modules" child folder, in that order.
sMainFolderPath = os.path.abspath(os.path.dirname(__file__));
sParentFolderPath = os.path.normpath(os.path.join(sMainFolderPath, ".."));
sModulesFolderPath = os.path.join(sMainFolderPath, "modules");
asOriginalSysPath = sys.path[:];
sys.path = [sParentFolderPath, sModulesFolderPath] + asOriginalSysPath;

for (sModuleName, sURL) in {
  "mProductDetails": "https://github.com/SkyLined/mProductDetails/",
  "oConsole": "https://github.com/SkyLined/oConsole/",
}.items():
  try:
    __import__(sModuleName, globals(), locals(), [], -1);
  except ImportError, oError:
    if oError.message == "No module named %s" % sModuleName:
      print "*" * 80;
      print "rs depends on %s which you can download at:" % sModuleName;
      print "    %s" % sDownloadURL;
      print "After downloading, please save the code in this folder:";
      print "    %s" % os.path.join(sModuleFolderPath, sModuleName);
      print " - or -";
      print "    %s" % os.path.join(sParentFolderPath, sModuleName);
      print "Once you have completed these steps, please try again.";
      print "*" * 80;
    raise;

# Restore the search path
sys.path = asOriginalSysPath;

# Read product details for rs and all modules it uses.
import mProductDetails, mWindowsAPI, oConsole;
oMainProductDetails = mProductDetails.cProductDetails.foReadForMainModule();
mProductDetails.cProductDetails.foReadForModule(oConsole);
mProductDetails.cProductDetails.foReadForModule(mProductDetails);
mProductDetails.cProductDetails.foReadForModule(mWindowsAPI);

from fasMultithreadedFileFinder import fasMultithreadedFileFinder;
from foMultithreadedFileContentMatcher import foMultithreadedFileContentMatcher;
from mColors import *;
from oConsole import oConsole;
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

def fRunCommand(asCommandTemplate, sFilePath, auLineNumbers):
  asCommandTemplate = [unicode(s) for s in asCommandTemplate];
  auLineNumbers = auLineNumbers[:];
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
    sChars = oMatch.group(1);
    if sChars == u"l": return len(auLineNumbers) > 0 and u"%d" % auLineNumbers.pop(0) or u"-1";
    if u"f" in sChars: return sFilePath;
    sDrivePath = (u"d" in sChars and sDrive or u"") + (u"p" in sChars and sPath or u"");
    sNameExtension = (u"n" in sChars and sName or u"") + (u"x" in sChars and sExtension or u"");
    return u"\\".join([s for s in [sDrivePath, sNameExtension] if s]);
  
  asCommandLine = [
    re.sub(u"%(f|l|[dpnx]+)", fsSubstitudePathTemplates, sTemplate)
    for sTemplate in asCommandTemplate
  ];
  oProcess = mWindowsAPI.cConsoleProcess.foCreateForBinaryPathAndArguments(
    sBinaryPath = sComSpec,
    asArguments = [u"/C"] + asCommandLine,
  );
  oProcess.fbWait();

def fShowHelp():
  print """
grep - Filter files by name or content using Regular Expressions.
  
Usage:
  grep [[-c] /content/*] [-p /path/+] [-v] path* [options] [-- command]

Where:
  [-c] /content/    Files whose content does not match any of the regular
                    expressions in this list are filtered out of the results.
  -p /path/+        Files whose path does not match any of the regular
                    expressions in this list are filtered out of the results.
  path*             Optional names of files/folders to search in.
  -- command        Execute specified command for all files that have not been
                    filtered out. The command can contain the following
                    variables:
                      %d - the drive on which the file was found.
                      %p - the folder path in which the file was found.
                      %n - the name of the file (excluding the extension).
                      %x - the extension of the file (including the dot).
                        The above arguments can be combined, as in %dp will
                        give the folder's drive and path. and %nx will give
                        the file's full name.
                      %f - the full path of the file (== %dpnx).
                      %l - the line number on which a match was found.
                      Repeating %l gives you the next line number on which
                      a match was found, or -1 if there are no more matches.

Options:
    -r, --recursive Include all files in subfolders of any selected folders in
                    the search.
    -w, --wait      Wait for user to press ENTER before terminating.
    -u, --unicode   Remove all '\0' chars from the file before scanning to
                    convert utf-16 Unicode encoded characters back to ASCII.
    -v, --verbose   Output the file names of all files that could not be
                    scanned, including an error message that indicates why.
    -q, --quiet     Does not output the names of the files that matched. Useful
                    in combination with "--", if you only want to execute the
                    command and are not interested in the file names.
    -l N, --lines N Show N lines of the file's content around each match.
    --version       Show version and license information.
Notes:
  - Regular expressions start and end with a slash "/" and can optionally have
    an "i" (case Insensitive) and/or "m" (Multi-line) suffix.
  - By specifying "?" instead of any regular expression on the command line, the
    user will be asked to enter a regular expression manually.
  - By specifying "-" instead of any regular expression on the command line, no
    regular expression will be added to the specific list.

Examples:
  grep /T+/ -p /P+/ C:\\ -r
    Scan for files in the root of the C: drive and all its sub-folders. Select 
    all files which' path contains a sequence of 1 or more "P"-s. Search the
    content of the selected files for a sequence of 1 or more "A"-s. Output
    the paths of the files that match and the line number(s) on which the match
    was found.
  grep -p /P+/i C:\\ -r
    Scan for files in the root of the C: drive and all its sub-folders. Select 
    all files which' path contains a sequence of 1 or more "p"-s (both upper-
    and lowercase). Output the paths of the files that match.

  grep /class\\s+\\w+/m -p /\\.c(pp|xx)$/i -- notepad "%f"
    Select all files in the current folder. Filter out all files which do not
    have a ".cpp" or ".cxx" extension. Filter out all files which do not have a
    C++ class definitions. Output the paths of the files that were not filtered
    out and open them using Notepad.

  grep ? -p ? "C:\\dev\\my project"
    Ask the user to enter a content regular expressions and a name regular
    expression. Select all files in the "C:\\dev\\my project" folder. Filter out
    all files that do not match the content regular expression, if one was
    entered. Then filter out all files that do not match the name regular
    expression, if one was entered. Output the paths of the files that were not
    filtered out.

""".strip("\n").replace("\n", "\r\n");

def frRegExp(sRegExp, sFlags):
  return re.compile(unicode(sRegExp), sum([
    {"i": re.I, "l":re.L, "m":re.M, "s": re.S, "u": re.U, "x": re.X}[sFlag]
    for sFlag in sFlags
  ]));

def fShowVersionAndLicenseInformation():
  def fPrintProductDetails(oProductDetails, uIndent = 0):
    oConsole.fPrint( \
        NORMAL, " " * uIndent,
        INFO, oProductDetails.sProductName, \
        NORMAL, " version ", INFO, str(oProductDetails.oProductVersion), NORMAL, ".");
    if oProductDetails.oLicense:
      oConsole.fPrint( \
          NORMAL, " " * (uIndent + 2), "+ Licensed to ", INFO, oProductDetails.oLicense.sLicenseeName, \
          NORMAL, " for ", INFO, oProductDetails.oLicense.sUsageTypeDescription, \
          NORMAL, " on up to ", INFO, str(oProductDetails.oLicense.uLicensedInstances), \
          NORMAL, " systems until ", INFO, str(oProductDetails.oLicense.oEndDate), NORMAL, ".");
    else:
      assert oProductDetails.bInTrialPeriod, \
          "This code should not be reached";
      oConsole.fPrint( \
          NORMAL, " " * (uIndent + 2), WARNING, "* In trial period.");
  fPrintProductDetails(oMainProductDetails);
  oConsole.fPrint("This product depends on the following modules:");
  for oProductDetails in oMainProductDetails.faoGetAllLoadedProductDetails():
    if oProductDetails != oMainProductDetails:
      fPrintProductDetails(oProductDetails, uIndent = 2);

def fMain(asArgs):
  asLicenseErrors = oMainProductDetails.fasGetLicenseErrors();
  if asLicenseErrors:
    oConsole.fPrint(ERROR, "- You do not have a valid license to use this software:");
    for sLicenseError in asLicenseErrors:
      oConsole.fPrint(NORMAL, "  ", ERROR_INFO, sLicenseError);
    return -1;
  asLicenseWarnings = oMainProductDetails.fasGetLicenseWarnings();
  if asLicenseWarnings:
    oConsole.fPrint(WARNING, "Warning:");
    for sLicenseWarning in asLicenseWarnings:
      oConsole.fPrint(WARNING, "  * ", sLicenseWarning);
  asFilePaths = set();
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
  for sArg in asArgs:
    if bArgIsConvertTabsToSpaces:
      try:
        uConvertTabsToSpaces = long(sArg);
      except Exception as oException:
        oConsole.fPrint(ERROR, "Invalid tabs length ", ERROR_INFO, sArg, ERROR, ": ", ERROR_INFO, oException.message, ERROR, ".");
        return -1;
      continue;
    if bArgIsNumberOfRelevantLinesAroundMatch:
      # valid formats : "C" "-B", "-B+A" "+A"
      oBeforeAfterMatch = re.match(r"^(?:(\d+)|(?:\-(\d+))?(?:(?:,|,?\+)(\d+))?)$", sArg);
      if not oBeforeAfterMatch:
        oConsole.fPrint(ERROR, "Invalid lines range ", ERROR_INFO, sArg, ERROR, ".");
        oConsole.fPrint("Try ", INFO, "N", NORMAL, ", ", INFO, "-N", NORMAL, ", ", INFO, "-N+N", NORMAL, ", or ", INFO, "+N", NORMAL, ".");
        oConsole.fPrint("Where each N is an integer. '-' prefix indicates before, '+' prefix indices after the match.");
        return -1;
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
        return -1;
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
        fShowHelp();
        return 0;
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
        fShowVersionAndLicenseInformation();
        return 0;
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
        asFilePaths.add(sArg);
      elif os.path.isdir(sArg):
        asFolderPaths.add(sArg);
      else:
        oConsole.fPrint(ERROR, "Unknown argument: ", ERROR_INFO, sArg, ERROR, ".");
        return -1;
  
  # Check arguments and set some defaults
  if bArgsAreCommandTemplate and not asCommandTemplate:
    asCommandTemplate = [u"uedit64.exe", u"%f/%l"];
  if not arContentRegExps and not arNegativeContentRegExps and not arPathRegExps and not arNegativePathRegExps:
    oConsole.fPrint(ERROR, "Missing regular expression");
    return -1;
  if not asFilePaths and not asFolderPaths:
    asFolderPaths.add(os.getcwdu());
  if bRecursive:
    if not asFolderPaths:
      oConsole.fPrint(ERROR, "No folders to scan recursively");
      return -1;
  if bArgIsNumberOfRelevantLinesAroundMatch:
    oConsole.fPrint(ERROR, "missing number of matched lines to show");
    return -1;
  
  # Show argument values in verbose mode
  if bVerbose:
    if asFolderPaths:
      oConsole.fPrint("+ Selected folders:");
      for sFolderPath in asFolderPaths:
        oConsole.fPrint("  + ", sFolderPath);
    if bRecursive:
      oConsole.fPrint("+ Folders will be traversed recursively");
    
    if asFilePaths:
      oConsole.fPrint("+ Selected files:");
      for sFilePath in asFilePaths:
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
    asFilePaths |= fasMultithreadedFileFinder(uMaxThreads, asFolderPaths, bRecursive, arPathRegExps, arNegativePathRegExps, bVerbose);
  if not asFilePaths:
    if arPathRegExps or arNegativePathRegExps:
      oConsole.fPrint(ERROR, "No files found that matched any of the regular expressions");
    else:
      oConsole.fPrint(ERROR, "No files found");
    uResult = 1;
  elif not arContentRegExps and not arNegativeContentRegExps:
    for sFilePath in sorted(asFilePaths):
      oConsole.fPrint(sFilePath); # Strip "\\?\"
      if bArgsAreCommandTemplate:
        fRunCommand(asCommandTemplate, sFilePath, [0]);
    uResult = len(asFilePaths) == 0 and 1 or 0;
  else:
    oContentMatchingResults = foMultithreadedFileContentMatcher(uMaxThreads, asFilePaths, arContentRegExps, arNegativeContentRegExps, bUnicode, uNumberOfRelevantLinesBeforeMatch, uNumberOfRelevantLinesAfterMatch);
    if bVerbose:
      for sFilePath in oContentMatchingResults.asNotScannedFilePaths:
        oConsole.fPrint(DIM, "- ", sFilePath);
    if not oContentMatchingResults.dMatched_auLineNumbers_by_sFilePath:
      oConsole.fPrint(ERROR, "No match found.");
      uResult = 1;
    else:
      uResult = 0;
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
          fRunCommand(asCommandTemplate, sFilePath, auMatchedLineNumbers);
      if not bFirst:
        oConsole.fPrint();
    if bVerbose:
      if oContentMatchingResults.asNotScannedFilePaths > 0:
        oConsole.fPrint("Scanned %d/%d files, %s bytes." % (
            len(asFilePaths) - len(oContentMatchingResults.asNotScannedFilePaths), len(asFilePaths), fsBytes(oContentMatchingResults.uScannedBytes)));
      else:
        oConsole.fPrint("Scanned %d files, %s bytes." % (len(asFilePaths), fsBytes(oContentMatchingResults.uScannedBytes)));
  if bWait:
    raw_input();
  return uResult;

if __name__ == "__main__":
  sys.exit(fMain(sys.argv[1:]));