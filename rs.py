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

from fInitializeProduct import fInitializeProduct;
fInitializeProduct();

try: # mDebugOutput use is Optional
  import mDebugOutput as m0DebugOutput;
except ModuleNotFoundError as oException:
  if oException.args[0] != "No module named 'mDebugOutput'":
    raise;
  m0DebugOutput = None;

try:
  from mConsole import oConsole;
  import mWindowsAPI;
  from mHumanReadable import fsBytesToHumanReadableString;
  
  from fasSortedAlphabetically import fasSortedAlphabetically;
  from fCheckPythonVersion import fCheckPythonVersion;
  from fdoMultithreadedFilePathMatcher import fdoMultithreadedFilePathMatcher;
  from foMultithreadedFileContentMatcher import foMultithreadedFileContentMatcher;
  from fatsArgumentLowerNameAndValue import fatsArgumentLowerNameAndValue;
  from mColors import *;
  
  if __name__ == "__main__":
    oConsole.uDefaultColor = NORMAL;
    oConsole.uDefaultBarColor = BAR;
    oConsole.uDefaultProgressColor = PROGRESS;
    
    asTestedPythonVersions = ["3.9.1"];
    
    sComSpec = os.environ["COMSPEC"];
    uMaxThreads = max(1, multiprocessing.cpu_count() - 1);
    
    def fRunCommand(asCommandTemplate, sFilePath, oPathMatch, auLineNumbers = []):
      asCommandTemplate = [s for s in asCommandTemplate];
      sDrivePath, sNameExtension = sFilePath.rsplit("\\", 1);
      if ":" in sDrivePath:
        sDrive, sPath = sDrivePath.split(":", 1);
        if sDrive.startswith("\\\\?\\"):
          sDrive = sDrive[4:];
        sDrive += ":";
      else:
        sDrive, sPath = "", sDrivePath;
      if "." in sNameExtension:
        sName, sExtension = sNameExtension.rsplit(".", 1);
        sExtension = "." + sExtension;
      else:
        sName, sExtension = sNameExtension, "";
      def fsSubstitudePathTemplates(oMatch):
        sEscape, sDoNotQuote, sChars = oMatch.groups();
        if sEscape:
          return "{" + sDoNotQuote + sChars + "}"; # do not replace.
        if sChars == "l":
          if fsSubstitudePathTemplates.uCurrentLineNumberIndex < len(auLineNumbers):
            fsSubstitudePathTemplates.uCurrentLineNumberIndex += 1;
            return "%d" % auLineNumbers[fsSubstitudePathTemplates.uCurrentLineNumberIndex - 1];
          return "-1";
        if sChars[0] in "0123456789":
          uIndex = int(sChars);
          try:
            sSubstitute = oPathMatch.group(uIndex);
          except IndexError:
            sSubstitute = "";
        else:
          sSubstitute = "";
          dsReplacements = {
            "f": sFilePath,
            "d": sDrive or "",
            "p": sPath or "",
            "n": sName or "",
            "x": sExtension or "",
          };
          sLastChar = "";
          for sChar in sChars:
            if sChar == "n" and sLastChar == "p":
              sSubstitute += "\\"
            sSubstitute += dsReplacements[sChar];
            sLastChar = sChar;
        if sDoNotQuote == "":
          sSubstitute = '"%s"' % sSubstitute.replace('"', '"""');
        return sSubstitute;
      fsSubstitudePathTemplates.uCurrentLineNumberIndex = 0;
      
      asCommandLine = [
        # match everything "{" replacement "}", and note if "{" is escaped as "\\{"
        re.sub(r"(\\)?\{(~?)(l|[0-9]+|[fdpnx]+)\}", fsSubstitudePathTemplates, sTemplate)
        for sTemplate in asCommandTemplate
      ];
      oProcess = mWindowsAPI.cConsoleProcess.foCreateForBinaryPathAndArguments(
        sBinaryPath = sComSpec,
        asArguments = ["/C"] + asCommandLine,
        bRedirectStdOut = False,
        bRedirectStdErr = False,
      );
      oProcess.fbWait();
    
    def frRegExp(sRegExp, sFlags):
      return re.compile(sRegExp, sum([
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
    bPause = False;
    bUnicode = False;
    bQuiet = False;
    uConvertTabsToSpaces = 4;
    uNumberOfRelevantLinesBeforeMatch = None;
    uNumberOfRelevantLinesAfterMatch = None;
    bUseUEditCommandTemplate = False;
    asCommandTemplate = [];
    for (sArgument, s0LowerName, s0Value) in fatsArgumentLowerNameAndValue():
      if s0LowerName in ["r", "recursive"]:
        if s0Value is None or s0Value.lower() == "true":
          bRecursive = True;
        elif s0Value.lower() == "false":
          bRecursive = False;
        else:
          oConsole.fOutput(ERROR, "- The value for ", ERROR_INFO, sArgument, ERROR, \
              " must be \"", ERROR_INFO, "true", ERROR, "\" (default) or \"", ERROR_INFO, "false", ERROR, "\".");
          sys.exit(2);
      elif s0LowerName in ["q", "quiet"]:
        if s0Value is None or s0Value.lower() == "true":
          bQuiet = True;
        elif s0Value.lower() == "false":
          bQuiet = False;
        else:
          oConsole.fOutput(ERROR, "- The value for ", ERROR_INFO, sArgument, ERROR, \
              " must be \"", ERROR_INFO, "true", ERROR, "\" (default) or \"", ERROR_INFO, "false", ERROR, "\".");
          sys.exit(2);
      elif s0LowerName in ["v", "verbose"]:
        if s0Value is None or s0Value.lower() == "true":
          bVerbose = True;
        elif s0Value.lower() == "false":
          bVerbose = False;
        else:
          oConsole.fOutput(ERROR, "- The value for ", ERROR_INFO, sArgument, ERROR, \
              " must be \"", ERROR_INFO, "true", ERROR, "\" (default) or \"", ERROR_INFO, "false", ERROR, "\".");
          sys.exit(2);
      elif s0LowerName in ["p", "pause"]:
        if s0Value is None or s0Value.lower() == "true":
          bPause = True;
        elif s0Value.lower() == "false":
          bPause = False;
        else:
          oConsole.fOutput(ERROR, "- The value for ", ERROR_INFO, sArgument, ERROR, \
              " must be \"", ERROR_INFO, "true", ERROR, "\" (default) or \"", ERROR_INFO, "false", ERROR, "\".");
          sys.exit(2);
      elif s0LowerName in ["u", "unicode"]:
        if s0Value is None or s0Value.lower() == "true":
          bUnicode = True;
        elif s0Value.lower() == "false":
          bUnicode = False;
        else:
          oConsole.fOutput(ERROR, "- The value for ", ERROR_INFO, sArgument, ERROR, \
              " must be \"", ERROR_INFO, "true", ERROR, "\" (default) or \"", ERROR_INFO, "false", ERROR, "\".");
          sys.exit(2);
      elif s0LowerName in ["e", "uedit"]:
        if s0Value is None or s0Value.lower() == "true":
          bUseUEditCommandTemplate = True;
        elif s0Value.lower() == "false":
          bUseUEditCommandTemplate = False;
        else:
          oConsole.fOutput(ERROR, "- The value for ", ERROR_INFO, sArgument, ERROR, \
              " must be \"", ERROR_INFO, "true", ERROR, "\" (default) or \"", ERROR_INFO, "false", ERROR, "\".");
          sys.exit(2);
      elif s0LowerName in ["t", "tabs"]:
        try:
          uConvertTabsToSpaces = int(s0Value);
          assert uConvertTabsToSpaces < 1, "";
        except Exception as oException:
          oConsole.fOutput(ERROR, "- The value for ", ERROR_INFO, sArgument, ERROR, \
              " must be ", ERROR_INFO, "an integer larger than 0", ERROR, ".");
          os._exit(2);
      elif s0LowerName in ["l", "lines"]:
        # valid formats : "C" "-B", "-B+A" "+A"
        oBeforeAfterMatch = re.match(r"^(?:(\d+)|(?:\-(\d+))?(?:(?:,|,?\+)(\d+))?)$", s0Value);
        if not oBeforeAfterMatch:
          oConsole.fOutput(ERROR, "- The value for ", ERROR_INFO, s0Value, ERROR, " must be a valid range.");
          oConsole.fOutput("  Try ", INFO, "N", NORMAL, ", ", INFO, "-N", NORMAL, ", ", INFO, "-N+N", NORMAL, ", or ", INFO, "+N", NORMAL, ".");
          oConsole.fOutput("  Where each N is an integer. '-' prefix indicates before, '+' prefix indices after the match.");
          os._exit(2);
        suBeforeAndAfer, suBefore, suAfter = oBeforeAfterMatch.groups();
        if suBeforeAndAfer:
          uNumberOfRelevantLinesBeforeMatch = uNumberOfRelevantLinesAfterMatch = int(suBeforeAndAfer);
        else:
          uNumberOfRelevantLinesBeforeMatch = int(suBefore or 0);
          uNumberOfRelevantLinesAfterMatch = int(suAfter or 0);
      elif s0LowerName or s0Value: # arguments before "--"
        oRegExpMatch = re.match(r"^([cp]?)(!?)\/(.+)\/([ilmsux]*)$", sArgument);
        if oRegExpMatch:
          sContentOrPath, sNegative, sRegExp, sFlags = oRegExpMatch.groups();
          # Paths are type string, file contents are type bytes; reg.exp. must conform:
          sxRegExp = sRegExp if sContentOrPath == "p" else bytes(sRegExp, 'latin1');
          try:
            rRegExp = frRegExp(sxRegExp, sFlags);
          except Exception as oException:
            oConsole.fOutput(
              ERROR, "- Invalid regular expressions ",
              ERROR_INFO, sContentOrPath, sNegative,
              ERROR, "/",
              ERROR_INFO, sRegExp,
              ERROR, "/",
              ERROR_INFO, sFlags
            );
            oConsole.fOutput("  ", ERROR_INFO, oException.message, ERROR, ".");
            os._exit(2);
          else:
            if sContentOrPath == "p":
              if sNegative == "!":
                arNegativePathRegExps.append(rRegExp);
              else:
                arPathRegExps.append(rRegExp);
            else:
              if sNegative == "!":
                arNegativeContentRegExps.append(rRegExp);
              else:
                arContentRegExps.append(rRegExp);
        elif os.path.isfile(sArgument):
          doPathMatch_by_sSelectedFilePath[sArgument] = None; # User supplied; no regular expression match
        elif os.path.isdir(sArgument):
          asFolderPaths.add(sArgument);
        else:
          oConsole.fOutput(ERROR, "- Unknown argument: ", ERROR_INFO, sArgument, ERROR, ".");
          os._exit(2);
      else:
        asCommandTemplate.append(sArgument);
    
    # Check arguments and set some defaults
    if bUseUEditCommandTemplate:
      if asCommandTemplate:
        oConsole.fOutput(ERROR, "You cannot provide a commend tempalte when using the -e option.");
        os._exit(2);
      if not arContentRegExps:
        asCommandTemplate = ["uedit64.exe", "{f}"];
      else:
        asCommandTemplate = ["uedit64.exe", '"{~f}/{l}"']; # line number must be inside quotes
    if not arContentRegExps and not arNegativeContentRegExps and not arPathRegExps and not arNegativePathRegExps:
      oConsole.fOutput(ERROR, "- Missing regular expression");
      os._exit(2);
    if not doPathMatch_by_sSelectedFilePath and not asFolderPaths:
      asFolderPaths.add(os.getcwd());
    if bRecursive:
      if not asFolderPaths:
        oConsole.fOutput(ERROR, "No folders to scan recursively");
        os._exit(2);
    
    # Show argument values in verbose mode
    if bVerbose:
      if asFolderPaths:
        oConsole.fOutput("+ Selected folders:");
        for sFolderPath in asFolderPaths:
          oConsole.fOutput("  + ", sFolderPath);
      if bRecursive:
        oConsole.fOutput("+ Folders will be traversed recursively");
      
      if doPathMatch_by_sSelectedFilePath:
        oConsole.fOutput("+ Selected files:");
        for sFilePath in fasSortedAlphabetically(doPathMatch_by_sSelectedFilePath.keys()):
          oConsole.fOutput("  + ", sFilePath);
      if arPathRegExps or arNegativePathRegExps:
        oConsole.fOutput("+ File path regular expressions:");
      for rNegativePathRegExp in arNegativePathRegExps:
        oConsole.fOutput("  - ", json.dumps(rNegativePathRegExp.pattern)[1:-1]);
      for rPathRegExp in arPathRegExps:
        oConsole.fOutput("  + ", json.dumps(rPathRegExp.pattern)[1:-1]);
      
      if arContentRegExps or arNegativeContentRegExps:
        oConsole.fOutput("+ File content regular expressions:");
      for rNegativeContentRegExp in arNegativeContentRegExps:
        oConsole.fOutput("  - ", json.dumps(rNegativeContentRegExp.pattern)[1:-1]);
      for rContentRegExp in arContentRegExps:
        oConsole.fOutput("  + ", json.dumps(rContentRegExp.pattern)[1:-1]);
      if bUnicode:
        oConsole.fOutput("+ All '\\0' characters will be removed from the file contents before scanning,");
        oConsole.fOutput("  to convert UTF-16 Unicode encoded ASCII characters back to ASCII.");
      if asCommandTemplate:
        oConsole.fOutput("+ Command to be executed for each matched file:");
        oConsole.fOutput("  ", " ".join(asCommandTemplate));
      if bPause:
        oConsole.fOutput("+ After scanning is complete, wait for the user to press ENTER.");
    
    if asFolderPaths:
      doPathMatch_by_sSelectedFilePath.update(fdoMultithreadedFilePathMatcher(uMaxThreads, asFolderPaths, bRecursive, arPathRegExps, arNegativePathRegExps, bVerbose));
    if not doPathMatch_by_sSelectedFilePath:
      if arPathRegExps or arNegativePathRegExps:
        oConsole.fOutput(ERROR, "No files found that matched any of the path regular expressions.");
      else:
        oConsole.fOutput(ERROR, "No files found.");
      uResult = 0;
    elif not arContentRegExps and not arNegativeContentRegExps:
      for sFilePath in fasSortedAlphabetically(doPathMatch_by_sSelectedFilePath.keys()):
        oConsole.fOutput(sFilePath); # Strip "\\?\"
        if asCommandTemplate:
          oPathMatch = doPathMatch_by_sSelectedFilePath[sFilePath];
          fRunCommand(asCommandTemplate, sFilePath, oPathMatch);
      uResult = len(doPathMatch_by_sSelectedFilePath) > 0 and 1 or 0;
    else:
      oContentMatchingResults = foMultithreadedFileContentMatcher(uMaxThreads, list(doPathMatch_by_sSelectedFilePath.keys()), arContentRegExps, arNegativeContentRegExps, bUnicode, uNumberOfRelevantLinesBeforeMatch, uNumberOfRelevantLinesAfterMatch);
      if bVerbose:
        for sFilePath in oContentMatchingResults.asNotScannedFilePaths:
          oConsole.fOutput(DIM, "- ", sFilePath);
      if not oContentMatchingResults.dMatched_auLineNumbers_by_sFilePath:
        if arPathRegExps or arNegativePathRegExps:
          oConsole.fOutput(ERROR, "No match found in %d files that matched the path regular expressions." % len(doPathMatch_by_sSelectedFilePath));
        else:
          oConsole.fOutput(ERROR, "No match found in any files.");
        uResult = 0;
      else:
        uResult = 1;
        bFirst = True;
        bOutputRelevantLines = uNumberOfRelevantLinesBeforeMatch is not None or uNumberOfRelevantLinesAfterMatch is not None;
        for sFilePath in fasSortedAlphabetically(oContentMatchingResults.dMatched_auLineNumbers_by_sFilePath.keys()):
          auMatchedLineNumbers = sorted(oContentMatchingResults.dMatched_auLineNumbers_by_sFilePath[sFilePath]);
          if not bQuiet:
            if not bOutputRelevantLines:
              oConsole.fOutput(
                FILE_NAME, sFilePath,
                FILE_LINENO, "/", ",".join([str(u) for u in auMatchedLineNumbers]),
              );
            else:
              if bFirst:
                bFirst = False;
              else:
                # Separator between results for different files.
                oConsole.fOutput();
              uNextMatchedLineIndex = 0;
              oConsole.fOutput(
                FILE_BOX, " ",
                FILE_BOX_NAME, sFilePath,
                FILE_BOX_LINENO, "/%d" % auMatchedLineNumbers[uNextMatchedLineIndex],
                FILE_BOX, sPadding = " ",
              );
              auRelevantLineNumbers = sorted(oContentMatchingResults.dRelevant_asbLines_by_uLineNumber_by_sFilePath[sFilePath].keys());
              uPreviousLineNumber = None;
              for uRelevantLineNumber in auRelevantLineNumbers:
                # Seperator between non-sequential sections of file.
                if uPreviousLineNumber is not None and uRelevantLineNumber > uPreviousLineNumber + 1:
                  oConsole.fOutput(
                    FILE_BOX, " ",
                    FILE_CUT_LINENO_COLOMN, "\xB7" * 6,
                    LINENO_CONTENT_SEPARATOR, ":",
                    FILE_CUT_NAME, " ", sFilePath,
                    FILE_CUT_LINENO, "/%d" % auMatchedLineNumbers[uNextMatchedLineIndex],
                    FILE_CUT_PAD, " ", sPadding = "\xB7",
                 );
                sbRelevantLine = oContentMatchingResults.dRelevant_asbLines_by_uLineNumber_by_sFilePath[sFilePath][uRelevantLineNumber];
                bMatchedLine = uNextMatchedLineIndex < len(auMatchedLineNumbers) and uRelevantLineNumber == auMatchedLineNumbers[uNextMatchedLineIndex];
                if bMatchedLine:
                  uNextMatchedLineIndex += 1;
                oConsole.fOutput(
                  FILE_BOX, " ",
                  bMatchedLine and LINENO_COLOMN_MATCH or LINENO_COLOMN, "%6d" % uRelevantLineNumber,
                  bMatchedLine and LINENO_CONTENT_SEPARATOR_MATCH or LINENO_CONTENT_SEPARATOR, "\u2502",
                  bMatchedLine and CONTENT_MATCH or CONTENT, str(sbRelevantLine, 'latin1'),
                  CONTENT_EOL, "\u2190\u2193",
                  uConvertTabsToSpaces = uConvertTabsToSpaces,
                );
                uPreviousLineNumber = uRelevantLineNumber;
          if asCommandTemplate:
            oPathMatch = doPathMatch_by_sSelectedFilePath[sFilePath];
            fRunCommand(asCommandTemplate, sFilePath, oPathMatch, auMatchedLineNumbers);
        if not bFirst:
          oConsole.fOutput();
      if bVerbose:
        if oContentMatchingResults.asNotScannedFilePaths > 0:
          oConsole.fOutput("Scanned %d/%d files, %s bytes." % (
              len(doPathMatch_by_sSelectedFilePath) - len(oContentMatchingResults.asNotScannedFilePaths), len(doPathMatch_by_sSelectedFilePath), fsBytesToHumanReadableString(oContentMatchingResults.uScannedBytes)));
        else:
          oConsole.fOutput("Scanned %d files, %s bytes." % (len(doPathMatch_by_sSelectedFilePath), fsBytesToHumanReadableString(oContentMatchingResults.uScannedBytes)));
    if bPause:
      input();
    os._exit(uResult);

except Exception as oException:
  if m0DebugOutput:
    m0DebugOutput.fTerminateWithException(oException);
  raise;