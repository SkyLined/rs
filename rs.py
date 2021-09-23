import math, multiprocessing, os, re, sys;

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

guExitCodeInternalError = 1; # Just in case mExitCodes is not loaded, as we need this later.
try:
  from mConsole import oConsole;
  import mWindowsAPI;
  from mHumanReadable import fsBytesToHumanReadableString;
  
  from fasSortedAlphabetically import fasSortedAlphabetically;
  from fCheckPythonVersion import fCheckPythonVersion;
  from fdoMultithreadedFilePathMatcher import fdoMultithreadedFilePathMatcher;
  from foMultithreadedFileContentMatcher import foMultithreadedFileContentMatcher;
  from fatsArgumentLowerNameAndValue import fatsArgumentLowerNameAndValue;
  from mColorsAndChars import *;
  from mExitCodes import *;
  
  def frRegExp(sRegExp, sFlags):
    return re.compile(sRegExp, sum([
      {"i": re.I, "l":re.L, "m":re.M, "s": re.S, "u": re.U, "x": re.X}[sFlag]
      for sFlag in sFlags
    ]));
  
  def fsRegExpToString(rRegExp):
    return str(rRegExp.pattern, "ascii", "strict") if isinstance(rRegExp.pattern, bytes) else rRegExp.pattern;
    
  def fxProcessBooleanArgument(sArgumentName, s0Value, u0CanAlsoBeAnIntegerLargerThan = None):
    if s0Value is None or s0Value.lower() == "true":
      return True;
    if s0Value.lower() == "false":
      return False;
    if u0CanAlsoBeAnIntegerLargerThan is not None:
      try:
        uValue = int(s0Value);
      except:
        pass;
      else:
        if uValue > u0CanAlsoBeAnIntegerLargerThan:
          return uValue;
    oConsole.fOutput(
      COLOR_ERROR, CHAR_ERROR,
      COLOR_NORMAL, " The value for ",
      COLOR_INFO, sArgument,
      COLOR_NORMAL, " must be \"",
      COLOR_INFO, "true",
      COLOR_NORMAL, "\" (default) or \"",
      COLOR_INFO, "false",
      COLOR_NORMAL, "\"",
      [
        " or an integer larger than ", COLOR_INFO, str(u0CanAlsoBeAnIntegerLargerThan), COLOR_NORMAL,
      ] if u0CanAlsoBeAnIntegerLargerThan is not None else [],
      ".",
    );
    sys.exit(guExitCodeBadArgument);
  if __name__ == "__main__":
    asTestedPythonVersions = ["3.9.1"];
    
    sComSpec = os.environ["COMSPEC"];
    uMaxThreads = max(1, multiprocessing.cpu_count() - 1);
    grRegExpArgument = re.compile(
      r"\A"
      r"(!?[cpn]?|[cpn]?!?)"
      r"\/"
      r"(.+)"
      r"\/"
      r"([ilmsux]*)"
      r"\Z"
    );
    
    def fRunCommand(asCommandTemplate, sFilePath, o0LastPathMatch, auLineNumbers = []):
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
            sSubstitute = o0LastPathMatch.group(uIndex) if o0LastPathMatch else "";
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
    
    # Make sure the Python binary is up to date; we don't want our users to unknowingly run outdated software as this is
    # likely to cause unexpected issues.
    fCheckPythonVersion("rs", asTestedPythonVersions, "https://github.com/SkyLined/rs/issues/new")
    
    do0LastPathMatch_by_sSelectedFilePath = {};
    asFolderPaths = set();
    arContentRegExps = [];
    arNegativeContentRegExps = [];
    arPathRegExps = [];
    arNegativePathRegExps = [];
    arNameRegExps = [];
    arNegativeNameRegExps = [];
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
        bRecursive = fxProcessBooleanArgument(s0LowerName, s0Value);
      elif s0LowerName in ["q", "quiet"]:
        bQuiet = fxProcessBooleanArgument(s0LowerName, s0Value);
      elif s0LowerName in ["v", "verbose"]:
        bVerbose = fxProcessBooleanArgument(s0LowerName, s0Value);
      elif s0LowerName in ["p", "pause"]:
        bPause = fxProcessBooleanArgument(s0LowerName, s0Value);
      elif s0LowerName in ["u", "unicode"]:
        bUnicode = fxProcessBooleanArgument(s0LowerName, s0Value);
      elif s0LowerName in ["e", "uedit"]:
        bUseUEditCommandTemplate = fxProcessBooleanArgument(s0LowerName, s0Value);
      elif s0LowerName in ["t", "tabs"]:
        xValue = fxProcessBooleanArgument(s0LowerName, s0Value, u0CanAlsoBeAnIntegerLargerThan = 0);
        uConvertTabsToSpaces = xValue if isinstance(xValue, int) else 8;
      elif s0LowerName in ["l", "lines"]:
        # valid formats : "C" "-B", "-B+A" "+A"
        o0BeforeAfterMatch = re.match(r"^(?:(\d+)|(?:\-(\d+))?(?:(?:,|,?\+)(\d+))?)$", s0Value) if s0Value else None;
        if o0BeforeAfterMatch is None:
          oConsole.fOutput(
            COLOR_ERROR, CHAR_ERROR,
            COLOR_NORMAL,  " The value for ",
            COLOR_ERROR, s0LowerName,
            COLOR_NORMAL, " must be a valid range.");
          oConsole.fOutput("  Try ", COLOR_INFO, "N", COLOR_NORMAL, ", ", COLOR_INFO, "-N", COLOR_NORMAL, ", ", COLOR_INFO, "-N+N", COLOR_NORMAL, ", or ", COLOR_INFO, "+N", COLOR_NORMAL, ".");
          oConsole.fOutput("  Where each N is an integer. '-' prefix indicates before, '+' prefix indices after the match.");
          sys.exit(guExitCodeBadArgument);
        suBeforeAndAfer, suBefore, suAfter = o0BeforeAfterMatch.groups();
        if suBeforeAndAfer:
          uNumberOfRelevantLinesBeforeMatch = uNumberOfRelevantLinesAfterMatch = int(suBeforeAndAfer);
        else:
          uNumberOfRelevantLinesBeforeMatch = int(suBefore or 0);
          uNumberOfRelevantLinesAfterMatch = int(suAfter or 0);
      elif s0LowerName or s0Value: # arguments before "--"
        oRegExpMatch = grRegExpArgument.match(sArgument);
        if oRegExpMatch:
          sPrefixFlags, sRegExp, sFlags = oRegExpMatch.groups();
          bNegative = "!" in sPrefixFlags;
          bPath = "p" in sPrefixFlags;
          bFileOrFolderName = "n" in sPrefixFlags;
          # Paths are type string, file contents are type bytes; reg.exp. must conform:
          sxRegExp = sRegExp if (bPath or bFileOrFolderName) else bytes(sRegExp, 'latin1');
          try:
            rRegExp = frRegExp(sxRegExp, sFlags);
          except Exception as oException:
            oConsole.fOutput(
              COLOR_ERROR, CHAR_ERROR,
              COLOR_NORMAL,  " Invalid regular expressions ",
              COLOR_INFO, sPrefixFlags,
              COLOR_NORMAL, "/",
              COLOR_INFO, sRegExp,
              COLOR_NORMAL, "/",
              COLOR_INFO, sFlags
            );
            oConsole.fOutput("  ", COLOR_INFO, oException.message, COLOR_NORMAL, ".");
            sys.exit(guExitCodeBadArgument);
          else:
            if bPath:
              if bNegative:
                arNegativePathRegExps.append(rRegExp);
              else:
                arPathRegExps.append(rRegExp);
            elif bFileOrFolderName:
              if bNegative:
                arNegativeNameRegExps.append(rRegExp);
              else:
                arNameRegExps.append(rRegExp);
            else:
              if bNegative:
                arNegativeContentRegExps.append(rRegExp);
              else:
                arContentRegExps.append(rRegExp);
        elif os.path.isfile(sArgument):
          do0LastPathMatch_by_sSelectedFilePath[sArgument] = None; # User supplied; no regular expression match
        elif os.path.isdir(sArgument):
          asFolderPaths.add(sArgument);
        else:
          oConsole.fOutput(
            COLOR_ERROR, CHAR_ERROR,
            COLOR_NORMAL,  " Unknown argument: ",
            COLOR_INFO, sArgument,
            COLOR_NORMAL, ".",
          );
          sys.exit(guExitCodeBadArgument);
      else:
        asCommandTemplate.append(sArgument);
    
    # Check arguments and set some defaults
    if bUseUEditCommandTemplate:
      if asCommandTemplate:
        oConsole.fOutput(
          COLOR_ERROR, CHAR_ERROR,
          COLOR_NORMAL, "You cannot provide a commend template when using the -e option.",
        );
        sys.exit(guExitCodeBadArgument);
      if not arContentRegExps:
        asCommandTemplate = ["uedit64.exe", "{f}"];
      else:
        asCommandTemplate = ["uedit64.exe", '"{~f}/{l}"']; # line number must be inside quotes
    if (
      not arContentRegExps and not arNegativeContentRegExps
      and not arPathRegExps and not arNegativePathRegExps
      and not arNameRegExps and not arNegativeNameRegExps
    ):
      oConsole.fOutput(COLOR_ERROR, CHAR_ERROR, COLOR_NORMAL, " Missing regular expression.");
      sys.exit(guExitCodeBadArgument);
    if not do0LastPathMatch_by_sSelectedFilePath and not asFolderPaths:
      asFolderPaths.add(os.getcwd());
    if bRecursive:
      if not asFolderPaths:
        oConsole.fOutput(COLOR_ERROR, CHAR_ERROR, COLOR_NORMAL, "No folders to scan recursively!");
        sys.exit(guExitCodeBadArgument);
    
    # Show argument values in verbose mode
    if bVerbose:
      if asFolderPaths:
        oConsole.fOutput(COLOR_INFO, CHAR_INFO, COLOR_NORMAL, " Selected folders:");
        for sFolderPath in asFolderPaths:
          oConsole.fOutput("  ", CHAR_LIST, " ", sFolderPath);
      if bRecursive:
        oConsole.fOutput(COLOR_INFO, CHAR_INFO, COLOR_NORMAL, " Folders will be traversed recursively");
      
      if do0LastPathMatch_by_sSelectedFilePath:
        oConsole.fOutput(COLOR_INFO, CHAR_INFO, COLOR_NORMAL, " Selected files:");
        for sFilePath in fasSortedAlphabetically(do0LastPathMatch_by_sSelectedFilePath.keys()):
          oConsole.fOutput("  ", CHAR_LIST, " ", sFilePath);
      if arPathRegExps or arNegativePathRegExps:
        oConsole.fOutput(COLOR_INFO, CHAR_INFO, COLOR_NORMAL, " File path regular expressions:");
      for rNegativePathRegExp in arNegativePathRegExps:
        oConsole.fOutput("  ", COLOR_SELECT_NO, CHAR_SELECT_NO, COLOR_NORMAL, " ", fsRegExpToString(rNegativePathRegExp));
      for rPathRegExp in arPathRegExps:
        oConsole.fOutput("  ", COLOR_SELECT_YES, CHAR_SELECT_YES, COLOR_NORMAL, " ", fsRegExpToString(rPathRegExp));
      
      if arNameRegExps or arNegativeNameRegExps:
        oConsole.fOutput(COLOR_INFO, CHAR_INFO, COLOR_NORMAL, " File/folder name regular expressions:");
      for rNegativePathRegExp in arNegativeNameRegExps:
        oConsole.fOutput("  ", COLOR_SELECT_NO, CHAR_SELECT_NO, COLOR_NORMAL, " ", fsRegExpToString(rNegativePathRegExp));
      for rPathRegExp in arNameRegExps:
        oConsole.fOutput("  ", COLOR_SELECT_YES, CHAR_SELECT_YES, COLOR_NORMAL, " ", fsRegExpToString(rPathRegExp));
      
      if arContentRegExps or arNegativeContentRegExps:
        oConsole.fOutput(COLOR_INFO, CHAR_INFO, COLOR_NORMAL, " File content regular expressions:");
      for rNegativeContentRegExp in arNegativeContentRegExps:
        oConsole.fOutput("  ", COLOR_SELECT_NO, CHAR_SELECT_NO, COLOR_NORMAL, " ", fsRegExpToString(rNegativeContentRegExp));
      for rContentRegExp in arContentRegExps:
        oConsole.fOutput("  ", COLOR_SELECT_YES, CHAR_SELECT_YES, COLOR_NORMAL, " ", fsRegExpToString(rContentRegExp));
      if bUnicode:
        oConsole.fOutput(COLOR_INFO, CHAR_INFO, COLOR_NORMAL, " All '\\0' characters will be removed from the file contents before scanning,");
        oConsole.fOutput("  to convert UTF-16 Unicode encoded ASCII characters back to ASCII.");
      if asCommandTemplate:
        oConsole.fOutput(COLOR_INFO, CHAR_INFO, COLOR_NORMAL, " Command to be executed for each matched file:");
        oConsole.fOutput("  ", " ".join(asCommandTemplate));
      if bPause:
        oConsole.fOutput(COLOR_INFO, CHAR_INFO, COLOR_NORMAL, " After scanning is complete, wait for the user to press ENTER.");
    
    if asFolderPaths:
      do0LastPathMatch_by_sSelectedFilePath.update(fdoMultithreadedFilePathMatcher(
        uMaxThreads,
        asFolderPaths,
        bRecursive,
        arPathRegExps, arNegativePathRegExps,
        arNameRegExps, arNegativeNameRegExps,
        bVerbose
      ));
    if not do0LastPathMatch_by_sSelectedFilePath:
      if arPathRegExps or arNegativePathRegExps or arNameRegExps or arNegativeNameRegExps:
        oConsole.fOutput(
          COLOR_ERROR, CHAR_ERROR,
          COLOR_NORMAL, "- No files found that matched any of the ",
          " and ".join([s for s in [
            "path" if (arPathRegExps or arNegativePathRegExps) else None,
            "name" if (arNameRegExps or arNegativeNameRegExps) else None,
          ] if s]),
          " regular expressions.");
      else:
        oConsole.fOutput(COLOR_ERROR, CHAR_ERROR, COLOR_NORMAL, " No files found.");
      uExitCode = guExitCodeSuccess;
    elif not arContentRegExps and not arNegativeContentRegExps:
      for sFilePath in fasSortedAlphabetically(do0LastPathMatch_by_sSelectedFilePath.keys()):
        oConsole.fOutput(FILE_NAME, sFilePath); # Strip "\\?\"
        if asCommandTemplate:
          o0PathMatch = do0LastPathMatch_by_sSelectedFilePath[sFilePath];
          fRunCommand(asCommandTemplate, sFilePath, o0PathMatch);
      uExitCode = uExitCodeSuccess if len(do0LastPathMatch_by_sSelectedFilePath) > 0 else guExitCodeNoMatchesFound;
    else:
      oContentMatchingResults = foMultithreadedFileContentMatcher(uMaxThreads, list(do0LastPathMatch_by_sSelectedFilePath.keys()), arContentRegExps, arNegativeContentRegExps, bUnicode, uNumberOfRelevantLinesBeforeMatch, uNumberOfRelevantLinesAfterMatch);
      if bVerbose:
        for sFilePath in oContentMatchingResults.asNotScannedFilePaths:
          oConsole.fOutput(COLOR_DIM, "- ", sFilePath);
      if not oContentMatchingResults.dMatched_auLineNumbers_by_sFilePath:
        if arPathRegExps or arNegativePathRegExps or arNameRegExps or arNegativeNameRegExps:
          oConsole.fOutput(
            COLOR_ERROR, CHAR_ERROR,
            COLOR_NORMAL, " No match found in ",
            str(len(do0LastPathMatch_by_sSelectedFilePath)),
            " files that matched the ",
            " and ".join([s for s in [
              "path" if (arPathRegExps or arNegativePathRegExps) else None,
              "name" if (arNameRegExps or arNegativeNameRegExps) else None,
            ] if s]),
            " regular expressions.");
        else:
          oConsole.fOutput(COLOR_ERROR, CHAR_ERROR, COLOR_NORMAL, " No match found in any files.");
        uExitCode = guExitCodeNoMatchesFound;
      else:
        uExitCode = uExitCodeSuccess;
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
                  bMatchedLine and LINENO_CONTENT_SEPARATOR_MATCH or LINENO_CONTENT_SEPARATOR, "│",
                  bMatchedLine and CONTENT_MATCH or CONTENT, str(sbRelevantLine, 'latin1'),
                  CONTENT_EOL, CHAR_EOL,
                  uConvertTabsToSpaces = uConvertTabsToSpaces,
                );
                uPreviousLineNumber = uRelevantLineNumber;
          if asCommandTemplate:
            oPathMatch = do0LastPathMatch_by_sSelectedFilePath[sFilePath];
            fRunCommand(asCommandTemplate, sFilePath, oPathMatch, auMatchedLineNumbers);
        if not bFirst:
          oConsole.fOutput();
      if bVerbose:
        if len(oContentMatchingResults.asNotScannedFilePaths) > 0:
          oConsole.fOutput(COLOR_INFO, CHAR_INFO, COLOR_NORMAL, " Scanned %d/%d files, %s bytes." % (
            len(do0LastPathMatch_by_sSelectedFilePath) - len(oContentMatchingResults.asNotScannedFilePaths),
            len(do0LastPathMatch_by_sSelectedFilePath),
            fsBytesToHumanReadableString(oContentMatchingResults.uScannedBytes),
          ));
        else:
          oConsole.fOutput(COLOR_INFO, CHAR_INFO, COLOR_NORMAL, " Scanned %d files, %s bytes." % (
            len(do0LastPathMatch_by_sSelectedFilePath),
            fsBytesToHumanReadableString(oContentMatchingResults.uScannedBytes),
          ));
    if bPause:
      input();
    sys.exit(uExitCode);
  
except Exception as oException:
  if m0DebugOutput:
    m0DebugOutput.fTerminateWithException(oException, guExitCodeInternalError);
  raise;