#!/usr/bin/env python3

""" patent_xml_to_csv.py """

import argparse
import logging

from xmltotabular import XmlCollectionToTabular


def replace_missing_ents(doc):
    """
    Substitute out some undefined entities that appear in the XML

    * IndentingNewLine
    * LeftBracketingBar
    * LeftDoubleBracketingBar
    * RightBracketingBar

      These seem to be MathML symbols, but the mappings that I've used (deriving from,
      e.g., https://reference.wolfram.com/language/ref/character/LeftBracketingBar.html
      and http://www.mathmlcentral.com/characters/glyphs/LeftBracketingBar.html) point to
      code points in the PUA of the Unicode BMP -- i.e., they're only going to work with
      specific fonts.

      It seems like they should be part of mmlextra (see
      https://www.w3.org/TR/REC-MathML/chap6/byalpha.html), but they're not in any of the
      versions (plural!) of this file that I have available, or can find documented
      online (see, e.g., https://www.w3.org/TR/MathML2/mmlextra.html,
      https://www.w3.org/2003/entities/mathmldoc/mmlextra.html etc.)

      Alternative renderings are included in mmlalias.ent -- unclear where these come
      from.

      The version of mmlextra.ent from here:
      https://github.com/martinklepsch/patalyze/blob/master/resources/parsedir/mmlextra.ent
      seems to have what's required, and uses the PUA renderings in line with
      mathmlcentral.com and reference.wolfram.com

    ----

    * LeftSkeleton
    * RightSkeleton

      More MathML symbols, but there is a discrepancy here in that
      https://reference.wolfram.com/ and https://www.mathmlcentral.com/ use U+F761 and
      U+F762 for LeftSkeleton and RightSkeleton respectively, and my copy of mmlextra.ent
      uses U+E850 and U+E851.

    ----

    * hearts

      This entity appears in the detailed description for, e.g., 09489911 (note that this
      description is not extracted by the parser according to the current version of the
      config file at config/uspto-grants-0105.yaml).

      In the same context the suit "diamonds" is represented by &diams;, and clubs and
      hearts are presented by <CUSTOM-CHARACTER> elements which reference external TIFF
      files... (sigh).  This is despite the face that the appropriate XML entities
      (&hearts;, &diams;, &clubs;, and &spades;) are all defined in the DTDs and .ent
      files available, but for some reason &hearts; (and &hearts; alone) is missing from
      isopub.ent, which is the file actually invoked by the DTD specified in the XML
      (double sigh).

      In some of the DTD files the symbols specified for the suits are the white glpyhs
      (i.e. &#x2661, &#x2662, &#x2664, and &#x2667 for hearts, diamonds, spades and clubs
      respectively), and in others they are the black glyphs (i.e. &#x2665, &#x2666,
      &#x2660, and &#x2663) -- see, e.g.
      https://en.wikipedia.org/wiki/List_of_Unicode_characters#Miscellaneous_Symbols.

      I've chose the black variant here, as the black variants are used in isopub.ent
      -- but note that Google Patents has used the black variants for diamonds
      (presumably from isopub.ent), the white variant for hearts (coopted from another
      DTD?), and has dropped the <CUSTOM-CHARACTER> elements for spades and clubs (see
      https://patents.google.com/patent/US6612926).

    """

    doc = doc.replace("&IndentingNewLine;", "&#xF3A3;")
    doc = doc.replace("&LeftBracketingBar;", "&#xF603;")
    doc = doc.replace("&RightBracketingBar;", "&#xF604;")
    doc = doc.replace("&LeftDoubleBracketingBar;", "&#xF605;")
    doc = doc.replace("&RightDoubleBracketingBar;", "&#xF606;")

    doc = doc.replace("&LeftSkeleton;", "&#xF761;")
    doc = doc.replace("&RightSkeleton;", "&#xF762;")

    doc = doc.replace("&hearts;", "&#x2665;")
    return doc


def main():
    """ Command-line entry-point. """
    arg_parser = argparse.ArgumentParser(description="Description: {}".format(__file__))

    arg_parser.add_argument(
        "-v",
        "--verbose",
        action="count",
        default=0,
        help="increase verbosity (can be passed multiple times)",
    )

    arg_parser.add_argument(
        "-i",
        "--xml-input",
        action="store",
        nargs="+",
        required=True,
        help="XML file or directory of XML files (*.{xml,XML}) to parse recursively"
        " (multiple arguments can be passed)",
    )

    arg_parser.add_argument(
        "-r",
        "--recurse",
        action="store_true",
        help="if supplied, the parser will search subdirectories for"
        " XML files (*.{xml,XML}) to parse",
    )

    arg_parser.add_argument(
        "-c",
        "--config",
        action="store",
        required=True,
        help="config file (in YAML format)",
    )

    arg_parser.add_argument(
        "-d",
        "--dtd-path",
        action="store",
        required=True,
        help="path to folder where dtds and related documents can be found",
    )

    arg_parser.add_argument(
        "--validate",
        action="store_true",
        help="skip validation of input XML (for speed)",
    )

    arg_parser.add_argument(
        "-o",
        "--output-path",
        action="store",
        required=True,
        help="path to folder in which to save output (will be created if necessary)",
    )

    arg_parser.add_argument(
        "--output-type",
        choices=["csv", "sqlite"],
        action="store",
        default="csv",
        help="output csv files (one per table, default) or a sqlite database",
    )

    arg_parser.add_argument(
        "--processes",
        action="store",
        type=int,
        help="number of processes to use for parallel processing of XML documents"
        " (defaults to num_threads - 1)",
    )

    arg_parser.add_argument(
        "--continue-on-error",
        action="store_true",
        help="output errors on parsing failure but don't exit",
    )

    args = arg_parser.parse_args()

    log_level = (logging.WARN, logging.INFO, logging.DEBUG)[args.verbose]

    convertor = XmlCollectionToTabular(
        **vars(args), preprocess_doc=replace_missing_ents, log_level=log_level
    )
    convertor.convert()


if __name__ == "__main__":
    main()
