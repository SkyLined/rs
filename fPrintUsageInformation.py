from oConsole import oConsole;
from mColors import *;

def fPrintUsageInformation():
  oConsole.fLock();
  try:
    oConsole.fPrint(HILITE,"Usage:");
    oConsole.fPrint();
    oConsole.fPrint(INFO,"  rs.py [options] [<path> [<path> [...]]] [-- <command>]");
    oConsole.fPrint();
    oConsole.fPrint(HILITE, "Options:");
    oConsole.fPrint(INFO, "  -h, --help");
    oConsole.fPrint("    This cruft.");
    oConsole.fPrint(INFO, "  -q, --quiet");
    oConsole.fPrint("    Output only essential information.");
    oConsole.fPrint(INFO, "  -v, --verbose");
    oConsole.fPrint("    Verbose output.");
    oConsole.fPrint(INFO, "  --version");
    oConsole.fPrint("    Show version information and check for updates.");
    oConsole.fPrint(INFO, "  -c <regular expression> [<regular expression> [...]]");
    oConsole.fPrint("    Match the content of files against the given regular expression(s).");
    oConsole.fPrint(INFO, "  -p <regular expression> [<regular expression> [...]]");
    oConsole.fPrint("    Match the full path and name of files against the given regular");
    oConsole.fPrint("    expression(s).");
    oConsole.fPrint("  Notes: you must provide at least one -c or -p regular expression. If a");
    oConsole.fPrint("  regular expression is not preceded by either -c or -p, it is used as a");
    oConsole.fPrint("  content regular expression.");
    oConsole.fPrint(INFO, "  -w, --wait");
    oConsole.fPrint("    Wait for user to press ENTER before terminating.");
    oConsole.fPrint(INFO, "  -u, --unicode");
    oConsole.fPrint("    Remove all '\0' chars from the file before scanning to convert utf-16");
    oConsole.fPrint("    encoded ASCII characters back to ASCII.");
    oConsole.fPrint(INFO, "  -l, --lines <lines>");
    oConsole.fPrint("    Show the provided number of lines of the file's content around each match.");
    oConsole.fPrint("    ", INFO, "<lines>", NORMAL, " can take two formats: ", INFO, "[-/+]N", NORMAL, " and ", INFO, "-N+N", NORMAL, ".");
    oConsole.fPrint("    Where N is a integer number, positive/negative numbers determine the number");
    oConsole.fPrint("    of lines to show after/before the match respectively.");
    oConsole.fPrint(INFO, "  <path> [<path> [...]]");
    oConsole.fPrint("    Apply matching only to the provided files/folders. If not path is");
    oConsole.fPrint("    provided, the current working directory is used.");
    oConsole.fPrint(INFO, "  -r, --recursive");
    oConsole.fPrint("    Apply matching to all files in all subfolders of the selected folders.");
    oConsole.fPrint(INFO, "  -- <command>");
    oConsole.fPrint("    Execute the specified command for all files that matched the given");
    oConsole.fPrint("    regular expressions. The command can contain the following replacements:");
    oConsole.fPrint("      ", INFO, "{d}", NORMAL, " - the drive on which the file was found.");
    oConsole.fPrint("      ", INFO, "{p}", NORMAL, " - the folder path in which the file was found.");
    oConsole.fPrint("      ", INFO, "{n}", NORMAL, " - the name of the file (excluding the extension).");
    oConsole.fPrint("      ", INFO, "{x}", NORMAL, " - the extension of the file (including the dot).");
    oConsole.fPrint("      ", INFO, "{f}", NORMAL, " - the full path of the file (== ", INFO, "{dpnx}", NORMAL, ").");
    oConsole.fPrint("    Note: The above arguments can be combined: ", INFO, "{dp}", NORMAL, " will be replaced with the");
    oConsole.fPrint("    file's drive and path, and ", INFO, "{nx}", NORMAL, " will be replaced by the file's name and");
    oConsole.fPrint("    extension.");
    oConsole.fPrint("      ", INFO, "{l}", NORMAL, " - the line number on which the first match was found.");
    oConsole.fPrint("    Note: Repeating {l} gives you the next line number on which a match was");
    oConsole.fPrint("    found, or -1 if there are no more matches: {l},{l},{l} will be replaced with");
    oConsole.fPrint("    the line numbers of the first three matches, separated by commas.");
    oConsole.fPrint("      ", INFO, "{1}", NORMAL, ", ", INFO, "{2}", NORMAL, ", ", INFO, "{3}", NORMAL, "... - the ", UNDERLINE, "first path", NORMAL, " match's sub-matches.");
    oConsole.fPrint("    Note: You can use {1} - {9} to insert parts of the first match against the");
    oConsole.fPrint("    file path. This may be useful to mass-rename files.");
    oConsole.fPrint();
    oConsole.fPrint(HILITE, "Regular expression syntax:");
    oConsole.fPrint("  [", INFO, "!", NORMAL, "]/", INFO, "pattern", NORMAL, "/[", INFO, "flags", NORMAL, "]");
    oConsole.fPrint();
    oConsole.fPrint(INFO, "  !");
    oConsole.fPrint("    Filter out files that match this regular expression. (Normally, files whose");
    oConsole.fPrint("    content or full path and name do ", UNDERLINE, "NOT", NORMAL, " match the regular expression are");
    oConsole.fPrint("    filtered out.");
    oConsole.fPrint(INFO, "  pattern");
    oConsole.fPrint("    A regular expression pattern following Python syntax.");
    oConsole.fPrint(INFO, "  flags");
    oConsole.fPrint("    Any one of the single-letter regular expression flags available in Python.");
    oConsole.fPrint("  Notes: details on the syntax of Python regular expression patterns and flags");
    oConsole.fPrint("  can be found at ", INFO, "https://docs.python.org/2/library/re.html", NORMAL, ".");
    oConsole.fPrint("  By specifying '?' in place of any regular expression on the command line,");
    oConsole.fPrint("  the user will be asked to enter a regular expression manually to take the");
    oConsole.fPrint("  place of the '?'. Specifying '-' in place of any regular expression will be");
    oConsole.fPrint("  ignored; this may be useful when scripting rs.py");
    oConsole.fPrint();
    oConsole.fPrint(HILITE, "Examples:");
    oConsole.fPrint(INFO, "  rs /C+/ -p /P+/ -r");
    oConsole.fPrint("    Match all files in the current directory and all its sub-folders which path");
    oConsole.fPrint("    and name contains a sequence of 1 or more 'P'-s. Match the  content of ");
    oConsole.fPrint("    these files for a sequence of 1 or more 'C'-s. Output the path and name of");
    oConsole.fPrint("    the files that matched and the line number(s) on which the 'C'-s were found.");
    oConsole.fPrint();
    oConsole.fPrint(INFO, "  rs -p /P+/i C:\\ -r");
    oConsole.fPrint("    Match all files in the root of the C: drive and all its sub-folders which");
    oConsole.fPrint("    path and name contains a sequence of 1 or more 'p'-s (either upper- or");
    oConsole.fPrint("    lowercase). Output the path and name of the files that matched.");
    oConsole.fPrint();
    oConsole.fPrint(INFO, "  rs /class\\s+\\w+/m -p /\\.c(pp|xx)$/i -- notepad %f");
    oConsole.fPrint("    Match all files in the current folder that have a .cpp or .cxx extension.");
    oConsole.fPrint("    Match the content of these files against a C++ class definitions. Output");
    oConsole.fPrint("    the path, name and line numbers of the files and open each one in Notepad.");
    oConsole.fPrint();
    oConsole.fPrint(INFO, "  rs /struct\s+some_struct\s*{/m -r -p /\\.[ch](pp|xx)?$/i -l -1+16");
    oConsole.fPrint("    Match all files in the current folder that have a C/C++ extension.");
    oConsole.fPrint("    Match the content of these files against the struct some_struct");
    oConsole.fPrint("    definitions. Output the path and name of the matched file(s) and the line");
    oConsole.fPrint("    before and up to 16 lines after each match.");
    oConsole.fPrint();
    oConsole.fPrint(HILITE, "Exit codes:");
    oConsole.fPrint("  ", INFO, "0", NORMAL," = rs did not match any files.");
    oConsole.fPrint("  ", INFO, "1", NORMAL," = rs matched one or more files.");
    oConsole.fPrint("  ", ERROR_INFO, "2", NORMAL, " = rs was unable to parse the command-line arguments provided.");
    oConsole.fPrint("  ", ERROR_INFO, "3", NORMAL, " = rs ran into an internal error: please report the details!");
  finally:             
    oConsole.fUnlock();