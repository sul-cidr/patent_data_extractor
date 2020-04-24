#!/usr/bin/env python3

""" extract_doc_by_linenum.py

    Usage e.g.: ./extract_doc_by_linenum.py /path/to/input.xml linenum > /path/to/output.xml
"""

import logging
import sys


def yield_xml_doc(filepath):
    xml_doc = []
    start_line = 0
    with open(filepath, "r") as _fh:
        for i, line in enumerate(_fh):
            if line.startswith("<?xml"):
                if xml_doc:
                    yield {"doc": "".join(xml_doc), "start": start_line, "end": i - 1}
                xml_doc = []
                start_line = i
            xml_doc.append(line)


def main():
    """ Command-line entry-point. """
    logging.basicConfig(level=logging.INFO, format="%(message)s")

    for xml_doc in yield_xml_doc(sys.argv[1]):
        if xml_doc["start"] < int(sys.argv[2]) < xml_doc["end"]:
            print(xml_doc["doc"])
            break


if __name__ == "__main__":
    main()
