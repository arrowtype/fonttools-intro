"""
    Example of updating names with TTFont.

    Updates Name IDs 1, 3, 4, 6, and 16

    Run it from the directory above with the following command, include 1) a font path, and 2) a new family name:

    python examples/01-ttfont-name-updates.py examples/Recursive_VF_1.077.ttf "New Name"

    (The above will output NewName_VF_1.053.ttf)
"""

import sys
from fontTools.ttLib import TTFont

# sets 'fontPath' variable to use the font path you pass in
fontPath = sys.argv[1]
newFamilyName = sys.argv[2]

print(fontPath)
print(newFamilyName)


# GET / SET NAME HELPER FUNCTIONS

def getFontNameID(font, ID, platformID=3, platEncID=1):
    name = str(font['name'].getName(ID, platformID, platEncID))
    return name

def setFontNameID(font, ID, newName):
    
    print(f"\n\t• name {ID}:")
    macIDs = {"platformID": 3, "platEncID": 1, "langID": 0x409}
    winIDs = {"platformID": 1, "platEncID": 0, "langID": 0x0}

    oldMacName = font['name'].getName(ID, *macIDs.values())
    oldWinName = font['name'].getName(ID, *winIDs.values())

    if oldMacName != newName:
        print(f"\n\t\t Mac name was '{oldMacName}'")
        font['name'].setName(newName, ID, *macIDs.values())
        print(f"\n\t\t Mac name now '{newName}'")

    if oldWinName != newName:
        print(f"\n\t\t Win name was '{oldWinName}'")
        font['name'].setName(newName, ID, *winIDs.values())
        print(f"\n\t\t Win name now '{newName}'")

# MAIN FUNCTION

def main(fontPath, newFamilyName):
    # open font with TTFont
    font = TTFont(fontPath)

    # useful to go backwards to start with name16, the Typographic Family name
    # (sadly, name16 is not in every font; you may have to manually pass in an "Old Name" for other font files)

    # Name 16: Typographic Family name – "Recursive"
    name16 = getFontNameID(font, 16) # provides the basic family name 
    newName16 = name16.replace(name16, newFamilyName) # replaces family name
    setFontNameID(font, 16, newName16)

    # Name 6: PostScript name – "Recursive-SansLinearLight"
    name6 = getFontNameID(font, 6)
    newName6 = name6.replace(name6.replace(" ",""), newFamilyName.replace(" ","")) # update name, make sure you have no spaces
    setFontNameID(font, 6, newName6)

    # Name 4: Full font name – "Recursive Sans Linear Light"
    name4 = getFontNameID(font, 4)
    newName4 = name4.replace(name4, newFamilyName)
    setFontNameID(font, 4, newName4)

    # Name 3: Unique font identifier – "1.053;ARRW;Recursive-SansLinearLight"
    name3 = getFontNameID(font, 3)
    newName3 = name3.replace(name6, newName6) # name 3 includes name6 as a substring
    setFontNameID(font, 3, newName3)
    
    # Name 1: Font Family name – "Recursive Sans Linear Light"

    name1 = getFontNameID(font, 1) # provides the basic family name 
    newName1 = name1.replace(name1, newFamilyName) # replaces family name
    setFontNameID(font, 1, newName1)

    # make new path to save to (assume old family name is in path)
    savePath = fontPath.replace(name16.replace(" ",""), newFamilyName.replace(" ",""))

    font.save(savePath)


main(fontPath, newFamilyName)