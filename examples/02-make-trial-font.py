"""
    A script to create a trial font from an OpenType font file (OTF or TTF), keeping characters for specified unicodes, while hiding the rest with a "replacer" glyph.

    This allows trial-font users to see how a given font looks to type words, but makes it simple to restrict it from full use in documents.

    Hiding the extended character set under a "replacer" glyph prevents fallback fonts from easily being subbed in for unintended use.

    This script is licensed under Apache 2.0: you are free to use and modify this script for commercial work.

    USAGE:

    1. On the command line, install python requirement FontTools:

        pip install fonttools

    2. Run this script on font file(s), either from the command line or from a shell script:

        python3 <filepath>/02-make-trial-font.py <filepath>/font.ttf

    Or, to see optional arguments, run:

        python3 <filepath>/02-make-trial-font.py --help

    TODO:
    - Add trial suffix to variable postscript name IDs, if relevant. E.g. Recursive VF has nameIDs 275 RecursiveMonoLnr-Light, etc for each instance
    - Replacer glyph shouldn't actually need to have a *unicode* value; it just needs to have a glyph. Fix this.
    - Maybe: "hideRanges" should be an option. By default (as it works right now), the script justs hide anything that is in the font but not in the "unicodes" arg.

    LICENSE:
    
    Copyright 2021 Arrow Type LLC / Stephen Nixon

    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at

        http://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.

"""

import shutil
import os
from fontTools.ttLib import TTFont
from fontTools import subset

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

def listUnicodeRanges(unicodeRanges):
        # remove "U+"" from ranges
        unicodeRanges = unicodeRanges.replace("U+", "").replace(" ", "")
        # create set
        unicodesIncluded = set()
        # split up separate ranges by commas
        for unicodeChunk in unicodeRanges.split(","):
            # if it's a range...
            if "-" in unicodeChunk:
                # get start and end of range
                start, end = unicodeChunk.split("-")
                # go through range and add each value to the set
                for unicodeInteger in range(int(start,16), int(end,16)+1):
                    unicodesIncluded.add(unicodeInteger)
            # if it's a single unicode...
            else:
                unicodesIncluded.add(int(unicodeChunk,16))
        return unicodesIncluded

def main():
    # get arguments from argparse
    args = parser.parse_args()

    for fontPath in args.fontPaths:

        # open font at TTFont object
        ttfont = TTFont(fontPath)

        filetype = fontPath.split(".")[-1]

        # make path of temporary font for subsetting
        tempFontPath = fontPath.replace(f".{filetype}",f".temporary.{filetype}")

        if args.extended:
            shutil.copyfile(fontPath, tempFontPath)
            tempFont = TTFont(tempFontPath)


        if not args.extended:

            # get set of unicode ints in font
            rangeInFont = {x for x in ttfont["cmap"].getBestCmap()}

            unicodesToKeep = listUnicodeRanges(args.unicodes)

            unicodesToHide = {intUnicode for intUnicode in rangeInFont if intUnicode not in unicodesToKeep}

            # get cmap of font, find unicode for glyph with name of replacerGlyph
            try:
                if "U+" in args.replacer:
                    replacerGlyphUnicode = args.replacer.replace("U+","")
                else:
                    replacerGlyphUnicode = list(ttfont["cmap"].buildReversed()[args.replacer])[0]

                unicodesToKeep.add(replacerGlyphUnicode)

                if replacerGlyphUnicode in unicodesToHide:
                    unicodesToHide.remove(replacerGlyphUnicode) # TODO: check if this fails if item not in set

            except KeyError:
                print("\nReplacer glyph has no unicode; try checking the font file to copy in an exact name.\n")
                print("Try checking the font file to copy in an exact glyph name, e.g. 'asterisk' rather than '*'.\n")
                print("Stopping execution.\n")
                break


            unicodesToKeep = [hex(n) for n in unicodesToKeep]
            unicodesToKeep = ",".join(unicodesToKeep)

            # Subset input font. Keep specified unicodes only. Keep all font name IDs. Keep glyph names as-is. Keep notdef from font. Output to temporary path.
            # Note: you may wish to remove '--layout-features=*' from this list to limit opentype features.
            subset.main([fontPath, f'--unicodes={unicodesToKeep}', "--name-IDs=*", "--layout-features=*", "--glyph-names", '--notdef-outline', f'--output-file={tempFontPath}'])
            tempFont = TTFont(tempFontPath)

            # -------------------------------------------------------------------------------------------------
            # then, add many additional unicodes to the replacer glyph to cover all diacritics, etc

            for table in tempFont['cmap'].tables: 
                for c in unicodesToHide:
                    table.cmap[c] = args.replacer

        # -------------------------------------------------------------------------------------------------
        # update font names

        familyName = getFontNameID(ttfont, 16)

        nameSuffix = args.suffix

        # MUST check if familyName is not 'None', or this doesn't work (e.g. can't just check if None)
        if familyName != 'None':
            newFamName = familyName + f" {nameSuffix}"
            setFontNameID(tempFont, 16, newFamName)
        else:
            familyName = getFontNameID(ttfont, 1)
            newFamName = familyName + f" {nameSuffix}"

        print("familyName is", familyName)

        # UPDATE NAME ID 6, postscript name 
        # Format: FamilynameTrial-Stylename
        currentPsName = getFontNameID(ttfont, 6)
        newPsName = currentPsName.replace('-',f'{nameSuffix}-')
        setFontNameID(tempFont, 6, newPsName)

        # UPDATE NAME ID 4, full font name
        # Format: Familyname Trial Stylename
        currentFullName = getFontNameID(ttfont, 4)
        newFullName = currentFullName.replace(familyName,f'{familyName} {nameSuffix}')
        setFontNameID(tempFont, 4, newFullName)

        # UPDATE NAME ID 3, unique font ID
        # Format: 1.001;ARRW;FamilynameTrial-Stylename
        currentUniqueName = getFontNameID(ttfont, 3)
        newUniqueName = currentUniqueName.replace('-',f'{nameSuffix}-')
        setFontNameID(tempFont, 3, newUniqueName)

        # UPDATE NAME ID 1, unique font ID
        # Format: Familyname Trial OR Familyname Trial Style (if not Regular, Italic, Bold, or Bold Italic)
        currentFamName = getFontNameID(ttfont, 1)
        newFamNameOne = currentFamName.replace(familyName,newFamName)
        setFontNameID(tempFont, 1, newFamNameOne)

        # -------------------------------------------------------------------------------------------------
        # save font with suffix added to name
        tempFont.save(tempFontPath.replace(f".temporary.{filetype}",f".{nameSuffix}.{filetype}"))
        # clean up temp subset font
        os.remove(tempFontPath)


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Make a "trial font" from OpenType font files, keeping characters for specified unicodes, while hiding the rest.')
    parser.add_argument('fontPaths', 
                        help='Path(s) to font file(s)',
                        nargs="+")
    parser.add_argument("-x", "--extended",
                        action='store_true',
                        help='Skips character subsetting to make an "extended" trial font, with a full, unmodified character set.')
    parser.add_argument("-u", "--unicodes",
                        default="U+0020-0039, U+003A-005A, U+0061-007A, U+2018-201D, U+005B, U+005D",
                        help='String of unicodes or unicode ranges to keep, comma-separated. Default is a basic Latin set: "U+0020-0039, U+003A-005A, U+0061-007A, U+2018-201D, U+005B, U+005D"')
    parser.add_argument('-r','--replacer',
                        default="X",
                        help='Name of glyph that will replace unicodes to hide. If you wish to use unicode, start with "U+" like "U+0058". Glyph be in the font & cannnot be ".notdef". Default: "X". ')
    parser.add_argument('-s','--suffix',
                        default="Trial",
                        help='Suffix to add to trial font names. Default: "Trial".')

    main()
