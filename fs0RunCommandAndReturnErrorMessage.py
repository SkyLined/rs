import os, re;

from mWindowsAPI import cConsoleProcess;

sComSpec = os.environ["COMSPEC"];

rSubstitudeTemplate = re.compile(
  r"(\\)?"
  r"\{"
    r"(~?)"
    r"("
      r"l"
    r"|"
      r"(n|p)?[0-9]+"
    r"|"
      r"[fdpnx]+"
    r")"
  r"\}"
);

def fs0RunCommandAndReturnErrorMessage(asCommandTemplate, sFilePath, o0LastNameMatch, o0LastPathMatch, auLineNumbers = []):
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
  
  def fsSubstitudeTemplate(oMatch):
    sEscape, sDoNotQuote, sChars, s0IndexAppliesToNameOrPath = oMatch.groups();
    if sEscape:
      return "{" + sDoNotQuote + sChars + "}"; # do not replace.
    if sChars == "l":
      if fsSubstitudeTemplate.uCurrentLineNumberIndex < len(auLineNumbers):
        fsSubstitudeTemplate.uCurrentLineNumberIndex += 1;
        return "%d" % auLineNumbers[fsSubstitudeTemplate.uCurrentLineNumberIndex - 1];
      return "-1";
    if sChars[0] in "0123456789":
      o0LastNameOrPathMatch = (
        o0LastNameMatch if s0IndexAppliesToNameOrPath == "n" else
        o0LastPathMatch if s0IndexAppliesToNameOrPath == "p" else
        (o0LastNameMatch or o0LastPathMatch)
      );
      assert o0LastNameOrPathMatch, \
        "There is no %s match from which to extract group %s" % (
          {"n": "name", "p": "path"}.get(s0IndexAppliesToNameOrPath, "name or path"),
          sChars
        )
      try:
        sSubstitute = o0LastNameOrPathMatch.group(int(sChars));
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
  fsSubstitudeTemplate.uCurrentLineNumberIndex = 0;
  
  asCommandLine = [
    # match everything "{" replacement "}", and note if "{" is escaped as "\\{"
    rSubstitudeTemplate.sub(fsSubstitudeTemplate, sTemplate)
    for sTemplate in asCommandTemplate
  ];
  try:
    oProcess = cConsoleProcess.foCreateForBinaryPathAndArguments(
      sBinaryPath = asCommandLine[0],
      asArguments = asCommandLine[1:],
      bRedirectStdOut = False,
      bRedirectStdErr = False,
    );
  except FileNotFoundError:
    return "Cannot find binary named '%s'" % asCommandLine[0];
  oProcess.fWait();
  return None;
