from oConsole import oConsole;
from mColors import *;

asBugIdLogo = [s.rstrip() for s in """
          dS'                          dS'                                      
         dS' .cid ,dSSc  ,dS"*sd      dS'   /R/egular expression /S/earch       
        dS'    SS;' '*'  YS(   Y     dS'                                        
       dS'     SS`        `*%s,     dS'                                         
      dS'      SS        b   )Sb   dS'                                          
     dS'     .dSSb.      P*ssSP'  dS'                                           
    dS'                          dS'                                            """.split("""
""")];

# We can now add color to console output, so let's create a second version of
# the above logo, but with color information (" " = default terminal color, hex
# digit = color number.
asBugIdLogoColors = [s.rstrip() for s in """
          999                          999                                      
         999 BBBB BBBBB  BBBBBBB      999   BBB77777777777777777 BBB77777       
        999    BBBB BBB  BBB   B     999                                        
       999     BBB        BBBBB     999                                         
      999      BB        B   BBB   999                                          
     999     BBBBBB      BBBBBBB  999                                           
    999                          999                                            """.split("""
""")];

def fPrintLogo():
  # We will use the above ASCII and color data to create a list of arguments
  # that can be passed to oConsole.fPrint in order to output the logo in color:
  oConsole.fLock();
  try:
    for uLineIndex in xrange(len(asBugIdLogo)):
      uCurrentColor = NORMAL;
      bUnderlined = False;
      asBugIdLogoPrintArguments = [""];
      sCharsLine = asBugIdLogo[uLineIndex];
      sColorsLine = asBugIdLogoColors[uLineIndex];
      uColorIndex = 0;
      for uColumnIndex in xrange(len(sCharsLine)):
        sColor = sColorsLine[uColorIndex];
        uColorIndex += 1;
        if sColor == "_":
          bUnderlined = not bUnderlined;
          sColor = sColorsLine[uColorIndex];
          uColorIndex += 1;
        uColor = (sColor != " " and (0x0F00 + long(sColor, 16)) or NORMAL) + (bUnderlined and UNDERLINE or 0);
        if uColor != uCurrentColor:
          asBugIdLogoPrintArguments.extend([uColor, ""]);
          uCurrentColor = uColor;
        sChar = sCharsLine[uColumnIndex];
        asBugIdLogoPrintArguments[-1] += sChar;
      oConsole.fPrint(*asBugIdLogoPrintArguments);
  finally:
    oConsole.fUnlock();
