[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

# USPTO Patent Data Extractor

## DOCUMENTATION

- clone the repo, and run `pip install -r requirements.txt` to install needed packages (`pipenv install` is also an option).

- Python >= 3.6 is required.

```
usage: patent_xml_to_csv.py -i XML_INPUT [XML_INPUT ...] -c CONFIG -d DTD_PATH -o OUTPUT_PATH
                            [--output-type {csv,sqlite}] [-r] [--validate] [--continue-on-error]
                            [--processes PROCESSES] [-h] [-v]

Description: /home/simon/CIDR/Patent-Data/patent_data_extractor/./patent_xml_to_csv.py

optional arguments:
  -i XML_INPUT [XML_INPUT ...], --xml-input XML_INPUT [XML_INPUT ...]
                        XML file or directory of XML files (*.{xml,XML}) to parse
                        (multiple arguments can be passed)
  -c CONFIG, --config CONFIG
                        config file (in YAML format)
  -d DTD_PATH, --dtd-path DTD_PATH
                        path to folder where dtds and related documents can be found
  -o OUTPUT_PATH, --output-path OUTPUT_PATH
                        path to folder in which to save output (will be created if necessary)
  --output-type {csv,sqlite}
                        output a sqlite database (default) or csv files (one per table)
  --sqlite-max-vars SQLITE_MAX_VARS
                        Override the maximum number of host parameters than can be passed in
                        a single SQLite statement (defaults to 999)
  -r, --recurse         search subdirectories for XML files (*.{xml,XML}) to parse
  --validate            validate input XML against DTDs
  --continue-on-error   output errors on parsing failure but don't exit
  --processes PROCESSES
                        number of processes to use for parallel processing of XML documents
                        (defaults to num_threads - 1)
  -v, --verbose         increase verbosity (can be passed multiple times)
  -h, --help            show this help message and exit
```

- e.g. `python3 patent_xml_to_csv.py --xml-input ../grants/pg030520.xml --config config/uspto-applications-0205.yaml --dtd-path .dtds --output ../output`

### CONFIG FILES

See [config/](config/) for examples -- proper documentation (perhaps in the wiki for this repo?) is required.

### UTILITY SCRIPTS

See [tools](tools/).
