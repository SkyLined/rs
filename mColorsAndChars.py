# COMMONLY USED COLOR NAMES
COLOR_DIM                               = 0x0F08; # Dark gray
COLOR_NORMAL                            = 0x0F07; # Light gray
COLOR_INFO                              = 0x0F0B; # Bright cyan
COLOR_HILITE                            = 0x0F0F; # White

COLOR_BUSY                              = 0x0F03; # Cyan
COLOR_OK                                = 0x0F02; # Green
COLOR_WARNING                           = 0x0F06; # Brown
COLOR_ERROR                             = 0x0F04; # Red

COLOR_SELECT_YES                        = 0x0F0B; # Bright green
COLOR_SELECT_NO                         = 0x0F09; # Light blue

COLOR_INPUT                             = 0x0F0B; #
COLOR_OUTPUT                            = 0x0F07; #

COLOR_ADD                               = 0x0F0A; # Bright green
COLOR_MODIFY                            = 0x0F0B; # Bright cyan
COLOR_REMOVE                            = 0x0F0C; # Bright red

COLOR_PROGRESS_BAR                      = 0xFF19; # Bright blue on Dark blue
COLOR_PROGRESS_BAR_HILITE               = 0xFF91; # Dark blue on bright blue
COLOR_PROGRESS_BAR_SUBPROGRESS          = 0xFFB1; # Dark blue on bright cyan

CONSOLE_UNDERLINE                       = 0x10000;

# COMMONLY USED CHARS
CHAR_BUSY                               = "»";
CHAR_OK                                 = "√";
CHAR_WARNING                            = "▲";
CHAR_ERROR                              = "×";

CHAR_SELECT_YES                         = "■";
CHAR_SELECT_NO                          = "□";

CHAR_LIST                               = "•";
CHAR_INFO                               = "→";
CHAR_INPUT                              = "◄";
CHAR_OUTPUT                             = "►";

CHAR_ADD                                = "+";
CHAR_MODIFY                             = "≈";
CHAR_REMOVE                             = "-";
CHAR_IGNORE                             = "·";

# DEFAULTS
from mConsole import oConsole;
oConsole.uDefaultColor = COLOR_NORMAL;
oConsole.uDefaultBarColor = COLOR_PROGRESS_BAR;
oConsole.uDefaultProgressColor = COLOR_PROGRESS_BAR_HILITE;
oConsole.uDefaultSubProgressColor = COLOR_PROGRESS_BAR_SUBPROGRESS;

# APPLICATION SPECIFIC COLOR NAMES
FILE_NAME                               = 0xFF0B; # The file name
FILE_LINENO                             = 0xFF09; # The line numbers in the file after the file name.

FILE_BOX                                = 0xFFB0; # The content header
FILE_BOX_NAME                           = 0xFFB0; # The file name in the content header
FILE_BOX_LINENO                         = 0xFFB9; # The line number of the first match in the content header

FILE_CUT_LINENO_COLOMN                  = 0xFF08; 
FILE_CUT_NAME                           = 0xFF08; # The file name repeated when the content is cut into pieces
FILE_CUT_LINENO                         = 0xFF09; # The next match line number when the content is cut into pieces
FILE_CUT_PAD                            = 0xFF08; # The padding after the file name and line number when the content is cut into pieces

LINENO_COLOMN                           = 0xFF08; # The line number before unmatched file content lines
LINENO_COLOMN_MATCH                     = 0xFF19; # The line number before matched file content lines

LINENO_CONTENT_SEPARATOR                = 0xFF08; # The separator between the line number and the file content line
LINENO_CONTENT_SEPARATOR_MATCH          = 0xFF18; # The separator between the line number and the file content line

CONTENT                                 = 0xFF07; # The unmatched file content lines
CONTENT_MATCH                           = 0xFF1B; # The matched file content lines
CONTENT_EOL                             = 0xFF08; # End of file content line marker
CHAR_EOL                                = "←↓";