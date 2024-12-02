
from foConsoleLoader import foConsoleLoader;
from fOutputLogo import fOutputLogo;
from mColorsAndChars import *;
oConsole = foConsoleLoader();

def fOutputUsageInformation():
  oConsole.fLock();
  try:
    fOutputLogo();
    axBoolean = ["[=", COLOR_INFO, "true", COLOR_NORMAL, "|", COLOR_INFO, "false", COLOR_NORMAL, "]"];
    
    oConsole.fOutput(COLOR_HILITE, "Usage:");
    oConsole.fOutput();
    oConsole.fOutput(COLOR_INFO, "  rs.py [options] [<path> [<path> [...]]] [-- <command>]");
    oConsole.fOutput();
    oConsole.fOutput(COLOR_HILITE, "Options:");
    oConsole.fOutput("  ", COLOR_INFO, "-h", COLOR_NORMAL, ", ", COLOR_INFO, "--help");
    oConsole.fOutput("    This cruft.");
    oConsole.fOutput("  ", COLOR_INFO, "--version");
    oConsole.fOutput("    Show version information.");
    oConsole.fOutput("  ", COLOR_INFO, "--version-check");
    oConsole.fOutput("    Check for updates and show version information.");
    oConsole.fOutput("  ", COLOR_INFO, "--license");
    oConsole.fOutput("    Show license information.");
    oConsole.fOutput("  ", COLOR_INFO, "--license-update");
    oConsole.fOutput("    Download license updates and show license information.");
    oConsole.fOutput("  ", COLOR_INFO, "--arguments", COLOR_NORMAL, "=<", COLOR_INFO, "file path", COLOR_NORMAL, ">");
    oConsole.fOutput("    Load additional arguments from the provided value and insert them in place");
    oConsole.fOutput("    of this argument.");
    
    oConsole.fOutput("  ", COLOR_INFO, "-e", COLOR_NORMAL, ", ", COLOR_INFO, "--uedit", axBoolean);
    oConsole.fOutput("    Start UltraEdit 64-bit for each matched file and scroll to the first matched line (if any).");
    oConsole.fOutput("  ", COLOR_INFO, "-ng", COLOR_NORMAL, ", ", COLOR_INFO, "--no-git", axBoolean);
    oConsole.fOutput("    Exclude files or folders which' names start with `.git`.");
    oConsole.fOutput("  ", COLOR_INFO, "-l", COLOR_NORMAL, ", ", COLOR_INFO, "--lines <lines>");
    oConsole.fOutput("    Show the provided number of lines of the file's content around each match.");
    oConsole.fOutput("    ", COLOR_INFO, "<lines>", COLOR_NORMAL, " can take two formats: ", COLOR_INFO, "[-/+]N", COLOR_NORMAL, " and ", COLOR_INFO, "-N+N", COLOR_NORMAL, ".");
    oConsole.fOutput("    Where N is a integer number, positive/negative numbers determine the number");
    oConsole.fOutput("    of lines to show after/before the match respectively.");
    oConsole.fOutput("  ", COLOR_INFO, "-p", COLOR_NORMAL, ", ", COLOR_INFO, "--pause", axBoolean);
    oConsole.fOutput("    Wait for user to press ENTER before terminating.");
    oConsole.fOutput("  ", COLOR_INFO, "-q", COLOR_NORMAL, ", ", COLOR_INFO, "--quiet", axBoolean);
    oConsole.fOutput("    Output only essential information.");
    oConsole.fOutput("  ", COLOR_INFO, "-u", COLOR_NORMAL, ", ", COLOR_INFO, "--unicode", axBoolean);
    oConsole.fOutput("    Remove all '\0' chars from the file before scanning to improvise scanning");
    oConsole.fOutput("    utf-16 encoded ASCII characters.");
    oConsole.fOutput("  ", COLOR_INFO, "-v", COLOR_NORMAL, ", ", COLOR_INFO, "--verbose", axBoolean);
    oConsole.fOutput("    Verbose output.");
    oConsole.fOutput("  ", COLOR_INFO, "<path>", COLOR_NORMAL, " [", COLOR_INFO, "<path>", COLOR_NORMAL, " [", COLOR_INFO, "...", COLOR_NORMAL, "]]");
    oConsole.fOutput("    Apply matching only to the provided files/folders. If not path is");
    oConsole.fOutput("    provided, the current working directory is used.");
    oConsole.fOutput("  ", COLOR_INFO, "-r", COLOR_NORMAL, ", ", COLOR_INFO, "--recursive");
    oConsole.fOutput("    Apply matching to all files in all subfolders of the selected folders.");
    oConsole.fOutput("  ", COLOR_INFO, "-t", COLOR_NORMAL, ", ", COLOR_INFO, "--tabs[=number]");
    oConsole.fOutput("    Convert tabs in output to spaces. You can optionally provide a number of");
    oConsole.fOutput("    spaces to use. The default is 2.");
    oConsole.fOutput("  ", COLOR_INFO, "-u", COLOR_NORMAL, ", ", COLOR_INFO, "--unicode");
    oConsole.fOutput("    Assume files contain ASCII strings encoded with UTF-16 and remove all '\0'");
    oConsole.fOutput("    characters before scanning for regular expressions.");
    oConsole.fOutput("    spaces to use. The default is 2.");
    oConsole.fOutput("  ", COLOR_INFO, "-v", COLOR_NORMAL, ", ", COLOR_INFO, "--verbose", axBoolean);
    oConsole.fOutput("    Output non-essential information.");
    oConsole.fOutput("  ", COLOR_INFO, "<regular expression> [<regular expression> [...]]");
    oConsole.fOutput("    Match the content or full path and name of files against the given regular");
    oConsole.fOutput("    expression(s). You must provide at least one regular expression.");
    oConsole.fOutput(COLOR_HILITE, "Regular expression syntax:");
    oConsole.fOutput("  [", COLOR_INFO, "c", COLOR_NORMAL, "|", COLOR_INFO, "p", COLOR_NORMAL, "]",
                       "[", COLOR_INFO, "!", COLOR_NORMAL, "]",
                       "/", COLOR_INFO, "pattern", COLOR_NORMAL, "/",
                       "[", COLOR_INFO, "flags", COLOR_NORMAL, "]");
    oConsole.fOutput();
    oConsole.fOutput("  [", COLOR_INFO, "c", COLOR_NORMAL, "|", COLOR_INFO, "p", COLOR_NORMAL, "]");
    oConsole.fOutput("   ", COLOR_INFO, "c", COLOR_NORMAL, " indicates the regular expression should be matched against the file's content");
    oConsole.fOutput("   (default). ", COLOR_INFO, "p", COLOR_NORMAL, " indicates the regular expression should be matched against the");
    oConsole.fOutput("    file's full path and name.");
    oConsole.fOutput("  [", COLOR_INFO, "!", COLOR_NORMAL, "]");
    oConsole.fOutput("    If ", COLOR_INFO, "!", COLOR_NORMAL, "is present, the match is inverted: files that match this regular expression");
    oConsole.fOutput("    are ", CONSOLE_UNDERLINE, "excluded", COLOR_NORMAL, " from the result instead of included. File that ", CONSOLE_UNDERLINE, "do not", COLOR_NORMAL, " match");
    oConsole.fOutput("    this regular expression are included.");
    oConsole.fOutput("  ", COLOR_INFO, "pattern");
    oConsole.fOutput("    A regular expression pattern following Python syntax.");
    oConsole.fOutput("  ", COLOR_INFO, "flags");
    oConsole.fOutput("    Any one of the single-letter regular expression flags available in Python.");
    oConsole.fOutput();
    oConsole.fOutput("  For details on the syntax of Python regular expression patterns and flags");
    oConsole.fOutput("  please visit: ", COLOR_INFO, "https://docs.python.org/3/library/re.html", COLOR_NORMAL, ".");
    oConsole.fOutput("  ", COLOR_INFO, "--", COLOR_NORMAL, " <", COLOR_INFO, "command", COLOR_NORMAL, "> [", COLOR_INFO, "arguments", COLOR_NORMAL, "]");
    oConsole.fOutput("    Execute the specified command for all files that matched the given");
    oConsole.fOutput("    regular expressions. The command nad arguments can contain the following");
    oConsole.fOutput("    keys that will be replaced by the appropriate values:");
    oConsole.fOutput("      ", COLOR_INFO, "{d}", COLOR_NORMAL, " - the drive on which the file was found.");
    oConsole.fOutput("      ", COLOR_INFO, "{p}", COLOR_NORMAL, " - the folder path in which the file was found.");
    oConsole.fOutput("      ", COLOR_INFO, "{n}", COLOR_NORMAL, " - the name of the file (excluding the extension).");
    oConsole.fOutput("      ", COLOR_INFO, "{x}", COLOR_NORMAL, " - the extension of the file (including the dot).");
    oConsole.fOutput("      ", COLOR_INFO, "{f}", COLOR_NORMAL, " - the full path of the file (== ", COLOR_INFO, "{dpnx}", COLOR_NORMAL, ").");
    oConsole.fOutput("    Note: The above arguments can be combined: ", COLOR_INFO, "{dp}", COLOR_NORMAL, " will be replaced with the");
    oConsole.fOutput("    file's drive and path, and ", COLOR_INFO, "{nx}", COLOR_NORMAL, " will be replaced by the file's name and");
    oConsole.fOutput("    extension. The values for these keys will be surrounded by quotes unless");
    oConsole.fOutput("    preceed them with ", COLOR_INFO, "~", COLOR_NORMAL, " (e.g. ", COLOR_INFO, "\"{~n}{~x}\"", COLOR_NORMAL, " == ", COLOR_INFO, "{nx}", COLOR_NORMAL, ").");
    oConsole.fOutput("      ", COLOR_INFO, "{l}", COLOR_NORMAL, " - the line number on which the first match was found.");
    oConsole.fOutput("    Note: Repeating {l} gives you the next line number on which a match was");
    oConsole.fOutput("    found, or -1 if there are no more matches: {l},{l},{l} will be replaced with");
    oConsole.fOutput("    the line numbers of the first three matches, separated by commas.");
    oConsole.fOutput("      ", COLOR_INFO, "{1}", COLOR_NORMAL, ", ", COLOR_INFO, "{2}", COLOR_NORMAL, ", ", COLOR_INFO, "{3}", COLOR_NORMAL, "... - the ", CONSOLE_UNDERLINE, "first path", COLOR_NORMAL, " match's sub-matches.");
    oConsole.fOutput("    Note: You can use numbers to insert groups from the last match against the");
    oConsole.fOutput("    file name or path. This may be useful to mass-rename files. If both a name");
    oConsole.fOutput("    and a path match exists, the name match is used. You can use the prefixes");
    oConsole.fOutput("    \"n\" and \"p\" to force using the name or path match, as in {n1} or {p2}.");
    oConsole.fOutput("    For instance ", COLOR_INFO, "rs \"n/(.*)\\.old$/\" -- ren {f} {1}", COLOR_NORMAL, " will remove the \".old\" extension");
    oConsole.fOutput("    from all files in the current folder.");
    oConsole.fOutput();
    oConsole.fOutput(COLOR_HILITE, "Examples:");
    oConsole.fOutput("  ", COLOR_INFO, "rs /C+/ -p /P+/ -r");
    oConsole.fOutput("    Match all files in the current directory and all its sub-folders which path");
    oConsole.fOutput("    and name contains a sequence of 1 or more 'P'-s. Match the  content of ");
    oConsole.fOutput("    these files for a sequence of 1 or more 'C'-s. Output the path and name of");
    oConsole.fOutput("    the files that matched and the line number(s) on which the 'C'-s were found.");
    oConsole.fOutput();
    oConsole.fOutput("  ", COLOR_INFO, "rs -p /P+/i C:\\ -r");
    oConsole.fOutput("    Match all files in the root of the C: drive and all its sub-folders which");
    oConsole.fOutput("    path and name contains a sequence of 1 or more 'p'-s (either upper- or");
    oConsole.fOutput("    lowercase). Output the path and name of the files that matched.");
    oConsole.fOutput();
    oConsole.fOutput("  ", COLOR_INFO, "rs /class\\s+\\w+/m -p /\\.c(pp|xx)$/i -- notepad {f}");
    oConsole.fOutput("    Match all files in the current folder that have a .cpp or .cxx extension.");
    oConsole.fOutput("    Match the content of these files against a C++ class definitions. Output");
    oConsole.fOutput("    the path, name and line numbers of the files and open each one in Notepad.");
    oConsole.fOutput();
    oConsole.fOutput("  ", COLOR_INFO, "rs /struct\\s+some_struct\\s*{/m -r -p /\\.[ch](pp|xx)?$/i -l -1+16");
    oConsole.fOutput("    Match all files in the current folder that have a C/C++ extension.");
    oConsole.fOutput("    Match the content of these files against the struct some_struct");
    oConsole.fOutput("    definitions. Output the path and name of the matched file(s) and the line");
    oConsole.fOutput("    before and up to 16 lines after each match.");
    oConsole.fOutput();
    oConsole.fOutput(COLOR_HILITE, "Exit codes:");
    oConsole.fOutput("  ", COLOR_INFO, "0", COLOR_NORMAL," = rs did not match any files.");
    oConsole.fOutput("  ", COLOR_INFO, "1", COLOR_NORMAL," = rs matched one or more files.");
    oConsole.fOutput("  ", COLOR_ERROR, "2", COLOR_NORMAL, " = rs was unable to parse the command-line arguments provided.");
    oConsole.fOutput("  ", COLOR_ERROR, "3", COLOR_NORMAL, " = rs ran into an internal error: please report the details!");
  finally:             
    oConsole.fUnlock();