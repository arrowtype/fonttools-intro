# An Intro to FontTools

This post is an introduction to FontTools and modern font development more generally.

It is written from the perspective of a beginner/intermediate font designer & developer (me, Stephen Nixon / @ArrowType), intended as an approachable introduction to font development for designers or developer hoping to better understand some common processes & tools of font development.

Basically, this is an attempt to write & present the guide I wish I had three years ago, when I first encountered font development as a student at KABK TypeMedia.

It is opinionated, limited to my current perspective, and possibly not 100% accurate. For this reason, I am presenting this at the [Typographics 2020 TypeLab](https://2020.typographics.com/typelab/) in hopes that more-experienced font developers might participate in coversation that can help me to correct any innaccuracies and improve this guide. Additionally, if you spot something here that is innacurate or if you have questions, please file an issue in this repo to help myself & others learn!

## Basic things to know about fonts & font development

Digital fonts, like any other digital media, are made up of data. Each glyph in a font is drawn from a collection of points on a coordinate grid, in scaleable curves called *Béziér* curves. Fonts have to map these drawings to [Unicode](https://en.wikipedia.org/wiki/List_of_Unicode_characters), so that the right glyph can display for each character in text on any computer. Fonts include a lot of other data: kerning, layout logic (e.g. for the place of accents, for stylistic sets, contextual alternates, etc), metrics for layout, family & style names for various software, license information, version numbers, and much more.

While some fonts are standalone, single-style things, many fonts are members of large font families (AKA typefaces) which have different but related styles.

Modern fonts follow the [OpenType specification](https://docs.microsoft.com/en-us/typography/opentype/spec/), which describes the data *tables* that all of this information is stored in. The OpenType spec is somewhat similar to the HTML, CSS, and JS specs that describe the “ground rules” that make up the modern web.

For end-users, the most common font file types are `TTF` and `OTF` (typically the latter are more specifically `CFF` or `CFF2` files). The biggest technical difference between `TTF` and `CFF` files is how they store glyph shapes. `CFF` fonts store glyphs as *Cubic* Béziér curves, which are similar to curves you may be familiar with from the pen tools of apps like Adobe Illustrator, Sketch, & Figma – these curves have two “offcurve points” between all main “oncurve” points. `TTF` fonts use *Quadratic* Béziér curves, which can have one to many offcurve points between oncurve points. The two formats also take different approaches to data compression and hinting, and have pros & cons in different software. However, both types are OpenType fonts, and both share many of the same data tables.

`TTF` and `OTF` files are called *binaries* because they are made up of code that is not human-readable. Font designers don’t work (typically) work directly in binaries. Instead, they work in source files which are often `.glyphs` (for [GlyphsApp](https://glyphsapp.com/)) or `.ufo` (the open-source format Unified Font Object, which is most commonly edited in [RoboFont](https://robofont.com/)). While `.glyphs` files can include multiple font sources to make up a single font family, `.ufo` sources are individual files, and `.designspace` files describe how multiple UFOs make up a given font family.

From these sources, binary files like OTF & TTF can be exported/built. For fonts on the web, these OTF/TTF files can then be further compressed into web-specific formats (the standard of which is now `woff2`).

At core, a lot of what FontTools does is to allow people to read & manipulate these different font filetypes with Python. In turn, this allows scripts & software that can create, modify, and build fonts.

## What is FontTools?

From the [FontTools repo](https://github.com/fonttools/fonttools/):

> fontTools is a library for manipulating fonts, written in Python.

For my purposes, FontTools is a set of code-based tools to read & manipulate:
- OTF & TTF font binaries
- UFO & Designspace font sources
- More font formats that I haven’t yet needed to work with

Rather than being one big thing, FontTools is a [*collection* of many tools](https://github.com/fonttools/fonttools/tree/master/Lib/fontTools), including:

- **cu2qu** for conversion between cubic & quadratic Béziér curves
- **designspaceLib** for reading & writing Designspace files
- **feaLib** for reading & writing OpenType features (e.g. accent placement, contextual glyph selection)
- **merge** to merge multiple font files into together
- **pens** that can read & draw different kinds of Béziér paths
- **subset** which can make font files smaller by eliminating (or subsetting) certain glyphs
- **ttLib** converts TrueType fonts to/from Python objects, and Python objects to/from TTX. This includes **ttFont** which can be used to read/edit data in font binaries
- **ttx** is a command-line tool to convert font binaries to/from human-readable [XML](https://developer.mozilla.org/en-US/docs/Web/XML/XML_introduction), allowing the data to be inspected or easily changed
- **ufoLib** allows the reading & writing of UFO files & the data within
- **varLib** allows the building of [variable fonts](https://variablefonts.io/), as well as the  instancing of variable fonts (trimming the amount of stylistic range in a variable font, either to make small variable fonts or single static fonts).

There are more tools than these, but I am still learning about them.

To learn more about FontTools, you can [read the docs](https://fonttools.readthedocs.io/), or browse the [source code](https://github.com/fonttools/fonttools) (which includes documentation inside of many functions).

### How is FontTools different from / related to FontParts? FontMake? FontBakery? AFDKO?

Parts of FontTools act as a major component of many other font-related tools.

As I was starting into font development, it was confusing to me that there were several tools with similar names and (sometimes) interdependencies. To be honest, I’m still learning things about how various Python libraries relate & interact, and others could speak in much more depth about how these things use FontTools. Here are four major tools that use FontTools in various ways:

**[FontParts](https://fontparts.robotools.dev/en/stable/)**

- Gives a logical structure to fonts, font info, glyphs, and contours (and [more](https://fontparts.robotools.dev/en/stable/objectref/objects/index.html)), and includes methods to manipulate these different objects to allow scripting workflows in type design.
- Can be used as a part of script tools in RoboFont (but is intended to be usable in any font editor)
- Can also be used in external Python scripts or via terminal commands to edit UFO files without requiring RoboFont.
- Uses FontTools

**[FontMake](https://github.com/googlefonts/fontmake/)**

- A command-line tool to build binary fonts from sources
- Can build `UFOs → OTF/TTF` or `Glyphs → UFOs → OTF/TTF`
  - Uses [glyphsLib](https://github.com/googlefonts/glyphsLib) to go from Glyphs files to UFOs + Designspace files
  - If building from Cubic (CFF) curves to Quadratic (TTF) curves, uses cu2qu for conversion
  - Uses FontTools to build output binaries
- Can also be used as a module in Python scripts for more-custom build setups
- Primarily sponsored & maintained by Google Fonts
- Uses FontTools to build prepared UFOs into OTFs & TTFs

**[AFDKO](https://github.com/adobe-type-tools/afdko/) (Adobe Font Development Kit for OpenType)**

- Somewhat similar functionality to FontMake, but primarily sponsored & maintained by Adobe
- Includes tools for proofing and validating font files
- “a set of tools for building OpenType font files from PostScript and TrueType font data”
- Has some advantages for building CFF fonts, like better CFF hinting & compression
- Uses FontTools to build prepared UFOs into OTFs & TTFs

**[FontBakery](https://github.com/googlefonts/fontbakery/)**

- A command-line tool to run quality-assurance checks on fonts in various formats: UFO, TTF, OTF
- The checks that run test for many things that can cause fonts to not work as expected. Examples:
  - Data tables that are missing or misformed
  - Font name entries that don’t match expectations (e.g. they are too long, they are different within the same font family, etc)
  - Font metrics that mismatch within a family
  - Variable axes with ranges that don’t conform to the OpenType spec
- There are some “universal” checks useful for almost any font, and there are checks specific to the expectations of individual font libraries such as Google Fonts or Adobe Fonts
- Uses FontTools to “inspect” font data in order to run checks


## The parts of FontTools which I use the most

To use FontTools, you first have to:

1. [Download Python](http://python.org/download/) and install it if you haven’t already.
2. Install FontTools. You can use the command `pip install fonttools` to do so.

### TTX

Just like web browsers have Developer Tools which allow you to “Inspect” the HTML, CSS, JS, and files that make up webpages, TTX allows you to convert binary fonts into human-readable XML so that you can inspect data.

A common way to use TTX is to simply build a XML from an OTF or TTF file (replacing the all-caps placeholders with an actual font filepath):

```bash
ttx -t name -o- FILEPATH/FONTNAME.ttf # makes the XML file FONTNAME.ttx
```

However, often, you only want to look at a single table of a font such as the `name` table. You also usually don’t need to save a new ttx file, but just want to check values. So, my favorite recipe is this:

```bash
ttx -t name -o- FILEPATH/FONTNAME.ttf
```

In that command, `-t name` specifies that only the name table should be converted to XML, and `-o-` specifies that the “output” should be nothing (and so, rather than a file, the XML is simply printed directly in the terminal). I remember this because `-o-` looks a bit like an emoticon owl.

TTX will also compile a TTX file back into a binary font file. So, it is possible to TTX a font, make changes in the `.ttx` file, and then run TTX to save those edits into a working font.

```bash
ttx FILEPATH/FONTNAME.ttf # outputs FILEPATH/FONTNAME.ttx
# you can make some edits, e.g. changing the font family name in name IDs 1, 3, 4, 6, and 16
ttx FILEPATH/FONTNAME.ttx # outputs FILEPATH/FONTNAME#1.ttf
```

However, editing font files by editing the TTX is relatively slow and hard to repeat. For example, if you are processing a folder containing many static fonts within a type family, it will take time to covert from OTF/TTF to TTX, time to make the changes (even if you write a script to do so), and time to convert back to OTF/TTF. It will probably take a few minutes, and chances are, you may have to run the process many times while developing it, making it painfully slow. So, TTX is really best used as a font inspector. 

To efficiently edit font data, it is much more useful to reach for `ttFont`.

## Editing Font Names with ttFont

- ttFont
- getName
- setName
- examples

## Editing other Font Data

- get cmap
- get an arbitrary table & entry within it
- set an arbitrary table & entry within it

## Subsetting a Font

- subsetter

## Instancing a Variable Font

- commandline
- python module

------------------------------------------------------------------

## Other useful tools

- https://github.com/google/woff2

## Please do these two things:

1. Check out https://arrowtype.github.io/vf-slnt-test/slnt-ital-tests/index.html, scroll to the bottom, and follow links to the Chromium & WebKit issues to voice your support for the prioritization of fixing the rendering of slnt & ital variable axes.

2. Check out https://github.com/fonttools/fonttools/issues/1994 & let me know if you have experienced the same font-menu issue in other fonts or if you know a solution (but this is probably a macOS issue, so at the very least it would be good to show that many people are having trouble here)
