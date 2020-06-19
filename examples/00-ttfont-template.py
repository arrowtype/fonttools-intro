"""
    Basic template to show simple TTFont setup. This script just prints name id=1 of a font file.

    Run it from the directory above with the following command:

    python examples/00-ttfont-template.py examples/Recursive_VF_1.053.ttf
"""

import sys
from fontTools.ttLib import TTFont

# sets 'fontPath' variable to use the font path you pass in
fontPath = sys.argv[1]

# MAIN FUNCTION

def main(fontPath):

    # open font with TTFont
    font = TTFont(fontPath)

    # font['name'] gets the name table, 
    # getName gets a specified name ID (1), platform (3 for Windows), and platEncID (1)
    name1 = str(font['name'].getName(1, 3, 1))

    # print the result
    print(f"\n\t→ name1 is '{name1}'\n")

    # help(font['name']) # use help() for more methods on a given table

# run main function
main(fontPath)
