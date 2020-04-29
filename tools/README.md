## UTILITY SCRIPTS

### download_uspto.py

```
usage: download_uspto.py [-h] [-v] [-q] --years YEARS [YEARS ...]
                         [--record-type {application,grant}] -o OUTPUT_PATH

Description: ./download_uspto.py

optional arguments:
  -h, --help            show this help message and exit
  -v, --verbose         Increase verbosity
  -q, --quiet           quiet operation
  --years YEARS [YEARS ...]
                        years to retrieve
  --record-type {application,grant}
                        retrieve applications or grants
  -o OUTPUT_PATH, --output-path OUTPUT_PATH
                        path to folder in which to save output (will be
                        created if necessary)
```
* e.g. `python3 download_uspto.py --years 2005 2007 2010 --record-type application --output-path /path/to/applications/output/`
* e.g. `python3 download_uspto.py --years {2005,2007,2010} --record-type application --output-path /path/to/applications/output/`
* e.g. `python3 download_uspto.py --years {2004..2008} --record-type grant --output-path /path/to/grants/output/`

#### Notes:
* The latter two examples depend upon bash brace expansion -- multiple years can simply be specified in series on the command line in shells where this is not supported (i.e. POSIX shell).
* Output files that already exist will be skipped and not re-downloaded (so the script will only fetch needed files, but partial or failed downloads will need to be cleared manually).
* The script does not test the integrity of the downloaded files (this could be added?), and sometimes the USPTO site returns "503 Service Temporarily Unavailable" errors or other malformed file.
* To extract all the archives to a single folder (e.g. `extracted/`), something like the following can be used:

    ```
    for i in {2002..2008}/*.zip; do unzip -j "$i" "*.xml" "*.XML" -d extracted/; done;
    ```
    Some of the archives contain SGML files in addition to the XML, so this command will extract only the files that match `*.xml` and `*.XML` (because of course there are both).


### Document Extraction
Individual `.xml` files extracted from the USPTO bulk data actually contain many XML documents, so they cannot be parsed by XML parsers until they've been split into individual documents.  In addition, the files are very large which makes inspecting them with a text editor cumbersome at best.  It is useful, therefore, to be able to extract individual documents by document number (`PATDOC/SDOBI/B100/B110/DNUM`) or by line number (i.e. the document that contains the specified line will be returned).  These are simple conveniences, and not intended to be robust to all possible scenarios at this time.


#### extract_doc_by_dnum.py
```
usage: python 3 extract_doc_by_dnum.py /path/to/input.xml docnum
```

* e.g. `python 3 extract_doc_by_linenum.py pg030520.xml 08547691 > 08547691.xml`


#### extract_doc_by_linenum.py
```
usage: python 3 extract_doc_by_linenum.py /path/to/input.xml linenum
```

* e.g. `python 3 extract_doc_by_linenum.py pg030520.xml 84942 > 09904398.xml`



