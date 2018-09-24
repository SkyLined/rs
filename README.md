```

          dS'                          dS'
         dS' .cid ,dSSc  ,dS"*sd      dS'   /R/egular expression /S/earch
        dS'    SS;' '*'  YS(   Y     dS'
       dS'     SS`        `*%s,     dS'
      dS'      SS        b   )Sb   dS'
     dS'     .dSSb.      P*ssSP'  dS'
    dS'                          dS'
Usage:

  rs.py [options] [<path> [<path> [...]]] [-- <command>]

Options:
  -h, --help
    This cruft.
  -q, --quiet
    Output only essential information.
  -v, --verbose
    Verbose output.
  --version
    Show version information and check for updates.
  -c <regular expression> [<regular expression> [...]]
    Match the content of files against the given regular expression(s).
  -p <regular expression> [<regular expression> [...]]
    Match the full path and name of files against the given regular
    expression(s).
  Notes: you must provide at least one -c or -p regular expression. If a
  regular expression is not preceded by either -c or -p, it is used as a
  content regular expression.
  -w, --wait
    Wait for user to press ENTER before terminating.
  -u, --unicode
    Remove all ' ' chars from the file before scanning to convert utf-16
    encoded ASCII characters back to ASCII.
  -l, --lines <lines>
    Show the provided number of lines of the file's content around each match.
    <lines> can take two formats: [-/+]N and -N+N.
    Where N is a integer number, positive/negative numbers determine the number
    of lines to show after/before the match respectively.
  <path> [<path> [...]]
    Apply matching only to the provided files/folders. If not path is
    provided, the current working directory is used.
  -r, --recursive
    Apply matching to all files in all subfolders of the selected folders.
  -- <command>
    Execute the specified command for all files that matched the given
    regular expressions. The command can contain the following variables:
      %d - the drive on which the file was found.
      %p - the folder path in which the file was found.
      %n - the name of the file (excluding the extension).
      %x - the extension of the file (including the dot).
    Note: The above arguments can be combined: %dp will be replaced with the
    file's drive and path, and %nx will be replaced by the file's name and
    extension.
      %f - the full path of the file (== %dpns).
      %l - the line number on which the first match was found.
    Note: Repeating %l gives you the next line number on which a match was
    found, or -1 if there are no more matches: %l %l %l will be replaced with
    the line numbers of the first three matches

Regular expression syntax:
  [!]/pattern/[flags]

  !
    Filter out files that match this regular expression. (Normally, files whose
    content or full path and name do NOT match the regular expression are
    filtered out.
  pattern
    A regular expression pattern following Python syntax.
  flags
    Any one of the single-letter regular expression flags available in Python.
  Notes: details on the syntax of Python regular expression patterns and flags
  can be found at https://docs.python.org/2/library/re.html.
  By specifying '?' in place of any regular expression on the command line,
  the user will be asked to enter a regular expression manually to take the
  place of the '?'. Specifying '-' in place of any regular expression will be
  ignored; this may be useful when scripting rs.py

Examples:
  rs /C+/ -p /P+/ -r
    Match all files in the current directory and all its sub-folders which path
    and name contains a sequence of 1 or more 'P'-s. Match the  content of
    these files for a sequence of 1 or more 'C'-s. Output the path and name of
    the files that matched and the line number(s) on which the 'C'-s were found.

  rs -p /P+/i C:\ -r
    Match all files in the root of the C: drive and all its sub-folders which
    path and name contains a sequence of 1 or more 'p'-s (either upper- or
    lowercase). Output the path and name of the files that matched.

  rs /class\s+\w+/m -p /\.c(pp|xx)$/i -- notepad %f
    Match all files in the current folder that have a .cpp or .cxx extension.
    Match the content of these files against a C++ class definitions. Output
    the path, name and line numbers of the files and open each one in Notepad.

  rs /struct\s+some_struct\s*{/m -r -p /\.[ch](pp|xx)?$/i -l -1+16
    Match all files in the current folder that have a C/C++ extension.
    Match the content of these files against the struct some_struct
    definitions. Output the path and name of the matched file(s) and the line
    before and up to 16 lines after each match.

Exit codes:
  0 = rs did not match any files.
  1 = rs matched one or more files.
  2 = rs was unable to parse the command-line arguments provided.
  3 = rs ran into an internal error: pleace report the details!
  5 = You do not have a valid license.
```
