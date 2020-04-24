#!/usr/bin/env python3

""" extract_doc_by_dnum.py

    Usage e.g.: ./extract_doc_by_dnum.py /path/to/input.xml docnum > /path/to/output.xml
"""

import logging
import sys


def yield_xml_doc(filepath):
    xml_doc = []
    with open(filepath, "r") as _fh:
        for line in _fh:
            if line.startswith("<?xml"):
                if xml_doc:
                    yield "".join(xml_doc)
                xml_doc = []
            xml_doc.append(line)


def main():
    """ Command-line entry-point. """
    logging.basicConfig(level=logging.INFO, format="%(message)s")

    for xml_doc in yield_xml_doc(sys.argv[1]):
        if f"<B210><DNUM><PDAT>{sys.argv[2]}</PDAT></DNUM></B210>" in xml_doc:
            print(xml_doc)
            break


if __name__ == "__main__":
    main()
