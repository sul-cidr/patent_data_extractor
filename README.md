[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

# USPTO Patent Data Extractor

## DOCUMENTATION

* clone the repo, and run `pip install -r requirements.txt` to be sure needed packages are available (`lxml` and `pyyaml` are required -- `termcolor` is optional, and `sqlite-utils` is only required if you make use of the `--output-type sqlite` option).

* Python >= 3.7 is required.

```
usage: patent_xml_to_csv.py [-h] [-v] [-q] -i XML_INPUT [XML_INPUT ...] [-r] -c
                            CONFIG -d DTD_PATH [--validate] -o OUTPUT_PATH
                            [--output-type {csv,sqlite}] [--processes PROCESSES]
                            [--continue-on-error]

Description: ./patent_xml_to_csv.py

optional arguments:
  -h, --help            show this help message and exit
  -v, --verbose         increase verbosity  (can be passed multiple times)
  -i XML_INPUT [XML_INPUT ...], --xml-input XML_INPUT [XML_INPUT ...]
                        XML file or directory of XML files (*.{xml,XML}) to parse
                        recursively (multiple arguments can be passed)
  -r, --recurse         if supplied, the parser will search subdirectories for XML
                        files (*.{xml,XML}) to parse
  -c CONFIG, --config CONFIG
                        config file (in YAML format)
  -d DTD_PATH, --dtd-path DTD_PATH
                        path to folder where dtds and related documents can be found
  --validate            skip validation of input XML (for speed)
  -o OUTPUT_PATH, --output-path OUTPUT_PATH
                        path to folder in which to save output (will be created if
                        necessary)
  --output-type {csv,sqlite}
                        output csv files (one per table, default) or a sqlite
                        database
  --processes PROCESSES
                        number of processes to use for parallel processing of XML
                        documents (defaults to num_threads - 1)
  --continue-on-error   output errors on parsing failure but don't exit

```

* e.g. `python3 patent_xml_to_csv.py --xml-input ../SamplePatentFiles/pg030520.xml --config config/uspto-applications-0205.yaml --dtd-path ../dtds/grant_dtds --output ../output`



### CONFIG FILES
See [config/](config/) for examples -- proper documentation (perhaps in the wiki for this repo?) is required.


### UTILITY SCRIPTS
See [tools](tools/).
