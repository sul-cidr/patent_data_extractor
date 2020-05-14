#!/usr/bin/env python3

""" patent_xml_to_csv.py """

import argparse
import csv
import logging
import re
from collections import defaultdict
from io import BytesIO
from pathlib import Path
from pprint import pformat

import yaml
from lxml import etree

try:
    from termcolor import colored
except ImportError:
    logging.debug("termcolor (pip install termcolor) not available")

    def colored(text, _color):
        """ Dummy function in case termcolor is not available. """
        return text


def replace_missing_mathml_ents(doc):
    """ Substitute out some undefined entities that appear in the XML -- see notes
        for further details. """
    doc = doc.replace("&IndentingNewLine;", "&#xF3A3;")
    doc = doc.replace("&LeftBracketingBar;", "&#xF603;")
    doc = doc.replace("&RightBracketingBar;", "&#xF604;")
    doc = doc.replace("&LeftDoubleBracketingBar;", "&#xF605;")
    doc = doc.replace("&RightDoubleBracketingBar;", "&#xF606;")
    return doc


def expand_paths(path_expr):
    path = Path(path_expr).expanduser()
    return Path(path.root).glob(
        str(Path("").joinpath(*path.parts[1:] if path.is_absolute() else path.parts))
    )


class DTDResolver(etree.Resolver):
    def __init__(self, dtd_path):
        self.dtd_path = Path(dtd_path)

    def resolve(self, system_url, _public_id, context):
        if system_url.startswith(str(self.dtd_path)):
            return self.resolve_filename(system_url, context)
        else:
            return self.resolve_filename(
                str((self.dtd_path / system_url).resolve()), context,
            )


class PatentXmlToTabular:
    def __init__(
        self, xml_input, config, dtd_path, output_path, logger, **kwargs,
    ):

        self.logger = logger

        self.xml_files = []
        for input_path in xml_input:
            for path in expand_paths(input_path):
                if path.is_file():
                    self.xml_files.append(path)
                elif path.is_dir():
                    self.xml_files.extend(
                        path.glob(f'{"**/" if kwargs["recurse"] else ""}*.[xX][mM][lL]')
                    )
                else:
                    self.logger.fatal("specified input is invalid")
                    exit(1)

        # do this now, because we don't want to process all that data and then find
        #  the output_path is invalid... :)
        self.output_path = Path(output_path)
        self.output_path.mkdir(parents=True, exist_ok=True)

        self.config = yaml.safe_load(open(config))

        self.tables = defaultdict(list)

        if kwargs["no_validate"]:
            self.parser = etree.XMLParser(
                load_dtd=True, resolve_entities=True, ns_clean=True
            )
        else:
            self.parser = etree.XMLParser(
                load_dtd=True, resolve_entities=True, ns_clean=True, dtd_validation=True
            )

        self.continue_on_error = kwargs["continue_on_error"]
        self.parser.resolvers.add(DTDResolver(dtd_path))

    @staticmethod
    def get_all_xml_docs(filepath):
        with open(filepath, "r") as _fh:
            data = _fh.read()
        return re.split(r"\n(?=<\?xml)", data)

    @staticmethod
    def yield_xml_doc(filepath):
        xml_doc = []
        with open(filepath, "r") as _fh:
            for line in _fh:
                if line.startswith("<?xml"):
                    if xml_doc and not xml_doc[1].startswith("<!DOCTYPE sequence-cwu"):
                        yield "".join(xml_doc)
                    xml_doc = []
                xml_doc.append(line)

    @staticmethod
    def get_text(xpath_result):
        if isinstance(xpath_result, str):
            return re.sub(r"\s+", " ", xpath_result).strip()
        return re.sub(
            r"\s+", " ", etree.tostring(xpath_result, method="text", encoding="unicode")
        ).strip()

    def get_pk(self, tree, config):
        if "pk" in config:
            elems = tree.findall("./" + config["pk"])
            assert len(elems) == 1
            return self.get_text(elems[0])
        return None

    def process_new_entity(
        self, tree, elems, config, parent_entity=None, parent_pk=None,
    ):
        """ Process a subtree of the xml as a new entity type, creating a new record in a new
            output table/file.
        """
        entity = config["entity"]
        for elem in elems:
            record = {}

            pk = self.get_pk(tree, config)
            if pk:
                record["id"] = pk
            else:
                record["id"] = f"{len(self.tables[entity])}"

            if parent_pk:
                record[f"{parent_entity}_id"] = parent_pk
            if "filename_field" in config:
                record[config["filename_field"]] = self.current_filename
            for subpath, subconfig in config["fields"].items():
                self.process_path(elem, subpath, subconfig, record, entity, pk)

            self.tables[entity].append(record)

    def process_path(
        self, tree, path, config, record, parent_entity=None, parent_pk=None,
    ):

        try:
            elems = [tree.getroot()]
        except AttributeError:
            elems = tree.xpath("./" + path)

        if isinstance(config, str):
            if elems:
                try:
                    assert len(elems) == 1
                except AssertionError as exc:
                    exc.msg = (
                        f"Multiple elements found for {path}! "
                        + "Should your config file include a joiner, or new entity "
                        + "definition?"
                        + "\n\n- "
                        + "\n- ".join(self.get_text(el) for el in elems)
                    )
                    raise

                # we've only one elem, and it's a simple mapping to a fieldname
                record[config] = self.get_text(elems[0])
            return

        if "entity" in config:
            # config is a new entity definition (i.e. a new record on a new table/file)
            self.process_new_entity(tree, elems, config, parent_entity, parent_pk)
            return

        if "fieldname" in config:
            # config is extra configuration for a field on this table/file
            if "joiner" in config:
                if elems:
                    record[config["fieldname"]] = config["joiner"].join(
                        [self.get_text(elem) for elem in elems]
                    )
                return

            if "enum_map" in config:
                if elems:
                    record[config["fieldname"]] = config["enum_map"].get(
                        self.get_text(elems[0])
                    )
                return

            if "enum_type" in config:
                if elems:
                    record[config["fieldname"]] = config["enum_type"]
                return

        raise LookupError(
            f'Invalid configuration for key "{parent_entity}":'
            + "\n "
            + "\n ".join(pformat(config).split("\n"))
        )

    def process_doc(self, doc):

        doc = replace_missing_mathml_ents(doc)

        tree = etree.parse(BytesIO(doc.encode("utf8")), self.parser)

        for path, config in self.config.items():
            self.process_path(tree, path, config, {})

    def convert(self):
        for input_file in self.xml_files:

            self.logger.info(colored("Processing %s...", "green"), input_file.resolve())
            self.current_filename = input_file.resolve().name

            for i, doc in enumerate(self.yield_xml_doc(input_file)):
                if i % 100 == 0:
                    self.logger.debug(
                        colored("Processing document %d...", "cyan"), i + 1
                    )
                try:
                    self.process_doc(doc)
                except LookupError as exc:
                    self.logger.warning(exc.args[0])
                    if not self.continue_on_error:
                        raise SystemExit()
                except (AssertionError, etree.XMLSyntaxError) as exc:
                    self.logger.debug(doc)
                    p_id = re.search(
                        r"<B210><DNUM><PDAT>(\d+)<\/PDAT><\/DNUM><\/B210>", doc
                    ).group(1)
                    self.logger.warning(
                        colored("ID %s: %s (record has not been parsed)", "red"),
                        p_id,
                        exc.msg,
                    )
                    if not self.continue_on_error:
                        raise SystemExit()

            self.logger.info(colored("...%d records processed!", "green"), i + 1)

    def get_fieldnames(self):
        """ On python >=3.7, dictionaries maintain key order, so fields are guaranteed to be
            returned in the order in which they appear in the config file.  To guarantee
            this on versions of python <3.7 (insofar as it matters),
            collections.OrderedDict would have to be used here.
        """

        fieldnames = defaultdict(list)

        def add_fieldnames(config, _fieldnames, parent_entity=None):
            if isinstance(config, str):
                if ":" in config:
                    _fieldnames.append(config.split(":")[0])
                    return
                _fieldnames.append(config)
                return

            if "fieldname" in config:
                _fieldnames.append(config["fieldname"])
                return

            if "entity" in config:
                entity = config["entity"]
                _fieldnames = []
                if "pk" in config or parent_entity:
                    _fieldnames.append("id")
                if parent_entity:
                    _fieldnames.append(f"{parent_entity}_id")
                if "filename_field" in config:
                    _fieldnames.append(config["filename_field"])
                for subconfig in config["fields"].values():
                    add_fieldnames(subconfig, _fieldnames, entity)
                # different keys may be appending rows to the same table(s), so we're
                #  appending to lists of fieldnames here.
                fieldnames[entity] = list(
                    dict.fromkeys(fieldnames[entity] + _fieldnames).keys()
                )
                return

            raise LookupError(
                "Invalid configuration:"
                + "\n "
                + "\n ".join(pformat(config).split("\n"))
            )

        for config in self.config.values():
            add_fieldnames(config, [])

        return fieldnames

    def write_csv_files(self):

        fieldnames = self.get_fieldnames()

        self.logger.info(
            colored("Writing csv files to %s ...", "green"), self.output_path.resolve()
        )
        for tablename, rows in self.tables.items():
            output_file = self.output_path / f"{tablename}.csv"
            with output_file.open("w") as _fh:
                writer = csv.DictWriter(_fh, fieldnames=fieldnames[tablename])
                writer.writeheader()
                writer.writerows(rows)

    def write_sqlitedb(self):
        try:
            from sqlite_utils import Database as SqliteDB
        except ImportError:
            self.logger.debug("sqlite_utils (pip3 install sqlite-utils) not available")
            raise

        fieldnames = self.get_fieldnames()
        db_path = (self.output_path / "db.sqlite").resolve()

        if db_path.exists():
            self.logger.warning(
                colored(
                    "Sqlite data base %s  exists; records will be appended.", "yellow"
                ),
                db_path,
            )

        db = SqliteDB(db_path)
        self.logger.info(
            colored("Writing records to %s ...", "green"), db_path,
        )
        for tablename, rows in self.tables.items():
            params = {"column_order": fieldnames[tablename]}
            if "id" in fieldnames[tablename]:
                params["pk"] = "id"
                params["not_null"] = {"id"}
            db[tablename].insert_all(rows, **params)


def main():
    """ Command-line entry-point. """
    arg_parser = argparse.ArgumentParser(description="Description: {}".format(__file__))

    arg_parser.add_argument(
        "-v", "--verbose", action="store_true", default=False, help="increase verbosity"
    )
    arg_parser.add_argument(
        "-q", "--quiet", action="store_true", default=False, help="quiet operation"
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
        "--no-validate",
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
        "--continue-on-error",
        action="store_true",
        help="output errors on parsing failure but don't exit",
    )

    args = arg_parser.parse_args()

    log_level = logging.DEBUG if args.verbose else logging.INFO
    log_level = logging.CRITICAL if args.quiet else log_level
    logger = logging.getLogger(__name__)
    logger.setLevel(log_level)  # format="%(message)s")
    logger.addHandler(logging.StreamHandler())

    if args.output_type == "sqlite":
        try:
            from sqlite_utils import Database as SqliteDB  # noqa
        except ImportError:
            logger.debug("sqlite_utils (pip3 install sqlite-utils) not available")
            raise

    convertor = PatentXmlToTabular(**vars(args), logger=logger)
    convertor.convert()

    if args.output_type == "csv":
        convertor.write_csv_files()

    if args.output_type == "sqlite":
        convertor.write_sqlitedb()


if __name__ == "__main__":
    main()
