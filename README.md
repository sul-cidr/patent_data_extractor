# Patent Data Extractor

## DOCUMENTATION

* clone the repo, and run `pip install -r requirements.txt` to be sure needed packages are available (currently only `lxml` is required -- `termcolor` is optional, and `sqlite-utils` is only required if you make use of the `--output-type sqlite` option).

```
usage: patent_xml_to_csv.py [-h] [-v] [-q] -i XML_INPUT [-r] -c CONFIG -d
                            DTD_PATH -o OUTPUT_PATH [--no-validate]

Description: ./patent_xml_to_csv.py

optional arguments:
  -h, --help            show this help message and exit
  -v, --verbose         increase verbosity
  -q, --quiet           quiet operation
  -i XML_INPUT, --xml-input XML_INPUT
                        "XML" file or directory to parse recursively
  -r, --recurse         if supplied, the parser will search subdirectories for
                        "XML" files to parse
  -c CONFIG, --config CONFIG
                        config file (in JSON format) describing the fields to
                        extract from the XML
  -d DTD_PATH, --dtd-path DTD_PATH
                        path to folder where dtds and related documents can be
                        found
  -o OUTPUT_PATH, --output-path OUTPUT_PATH
                        path to folder in which to save output (will be
                        created if necessary)
  --output-type {csv,sqlite}
                        output csv files (one per table, default) or a sqlite
                        database
  --continue-on-error   output errors on parsing failure but don't exit
  --no-validate         skip validation of input XML (for speed)
```

* e.g. `python3 patent_xml_to_csv.py --xml-input ../SamplePatentFiles/pg030520.xml --config config/docdb.json --dtd-path ../dtds/grant_dtds --output ../output`



### CONFIG FILES
see [config/docdb.json](config/docdb.json)
* for config values of the form `field:value` (i.e. with a colon), the text is not retrieved; the presence of the element causes `field` to be set to `value`. (This is to handle self-closing tags.)
* for config values that begin with a pipe `|`, values for multiple occurrences are concatenated together with the pipe as a separator.

## TODO
* (Option to?) write records to disk as they're parsed, so as to avoid keeping large amounts of data in memory
	- Note that the 331mb sample file I've been working with results in a peak memory consumption (RSS) of about 140mb, that's all, so the speed advantage (admittedly as-yet unquantified) probably outweighs the likelihood of encountering memory shortages.
* modularize the output code, leaving scope to output other kinds of files (SQL statements, pSQL scripts, sqlite DBs, HDF5 / arrow / other columnar formats, write directly to a DB server, etc.)
* convert config to YAML (which, for these purposes, is a superset of JSON anyway) so as to be able to add comments?  or use hJSON or another JSON parser that allows comments?
* probably lots more...

