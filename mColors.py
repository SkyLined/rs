from oConsole import oConsole;

# Colors used in output for various types of information:
NORMAL =            0x0F07; # Light gray
DIM =               0x0F08; # Dark gray
INFO =              0x0F0B; # Bright blue
HILITE =            0x0F0F; # Bright white
ERROR =             0x0F04; # Red
ERROR_INFO =        0x0F0C; # Bright red
WARNING =           0x0F06; # Yellow
WARNING_INFO =      0x0F0E; # Bright yellow
UNDERLINE =        0x10000;

oConsole.uDefaultColor = NORMAL;
oConsole.uDefaultBarColor = 0xFF1B; # Light cyan on Dark blue
oConsole.uDefaultProgressColor = 0xFFB1; # Dark blue on light cyan

FILE_NAME =         0xFF0B; # The file name
FILE_LINENO =       0xFF09; # The line numbers in the file after the file name.

FILE_BOX =          0xFFB0; # The content header
FILE_BOX_NAME =     0xFFB0; # The file name in the content header
FILE_BOX_LINENO =   0xFFB9; # The line number of the first match in the content header

FILE_CUT_LINENO_COLOMN = 0xFF08; 
FILE_CUT_NAME =     0xFF08; # The file name repeated when the content is cut into pieces
FILE_CUT_LINENO =   0xFF09; # The next match line number when the content is cut into pieces
FILE_CUT_PAD =      0xFF08; # The padding after the file name and line number when the content is cut into pieces

LINENO_COLOMN =     0xFF08; # The line number before unmatched file content lines
LINENO_COLOMN_MATCH = 0xFF90; # The line number before matched file content lines

LINENO_CONTENT_SEPARATOR = 0xFF08; # The separator between the line number and the file content line

CONTENT =           0xFF07; # The unmatched file content lines
CONTENT_MATCH =     0xFF0B; # The matched file content lines
CONTENT_EOL =       0xFF08; # End of file content line marker

