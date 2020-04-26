#!/usr/bin/env python3

""" download_uspto.py """

import argparse
import logging
from pathlib import Path

import requests
from bs4 import BeautifulSoup

try:
    from termcolor import colored
except ImportError:
    logging.debug("termcolor (pip install termcolor) not available")

    def colored(text, _color):
        """ Dummy function in case termcolor is not available. """
        return text


URLBASE = "https://bulkdata.uspto.gov/data/patent/{record_type}/redbook/fulltext/"


def fmt_size(num, suffix="B"):
    for unit in ["", "Ki", "Mi", "Gi", "Ti", "Pi", "Ei", "Zi"]:
        if abs(num) < 1024.0:
            return f"{num:3.2f}{unit}{suffix}"
        num /= 1024.0
    return f"{num:.2f}Yi{suffix}"


def get_urls(record_type, year):
    """  """
    response = requests.get(f"{URLBASE.format(record_type=record_type)}{year}")
    soup = BeautifulSoup(response.text, "html.parser")
    return [
        f"{URLBASE.format(record_type=record_type)}{year}/{link['href']}"
        for link in soup.select("a[href$=.zip]")
    ]


def get_file(url, output_folder="."):
    """ Retrieve a file from a URL link and store to `output_folder`. """

    output_path = Path(output_folder)
    output_path.mkdir(parents=True, exist_ok=True)
    assert output_path.is_dir()

    filename = output_path / url.split("/")[-1]

    if filename.exists():
        logging.warning(
            colored('Output file "%s" exists, not overwriting!', "yellow"), filename
        )
        return

    with filename.open("wb") as _fh:
        logging.info("\nDownloading %s...", filename)
        response = requests.get(url, allow_redirects=True, stream=True)
        total_length = response.headers.get("content-length")

        if total_length is None:
            _fh.write(response.content)
        else:
            downloaded = 0
            total_length = int(total_length)
            for data in response.iter_content(
                chunk_size=max(min(total_length // 100, 2 ** 20), 2 ** 12)
            ):
                downloaded += len(data)
                _fh.write(data)
                done = int(50 * downloaded / total_length)
                print(
                    f"\r[{'=' * done}{' ' * (50 - done)}] "
                    f"({fmt_size(downloaded)} / {fmt_size(total_length)})",
                    end=" " * 5,
                )
            print()


def main():
    """ Command-line entry-point. """

    logging.basicConfig(level=logging.INFO, format="%(message)s")

    parser = argparse.ArgumentParser(description="Description: {}".format(__file__))

    parser.add_argument(
        "-v", "--verbose", action="store_true", default=False, help="Increase verbosity"
    )
    parser.add_argument(
        "-q", "--quiet", action="store_true", default=False, help="quiet operation"
    )

    parser.add_argument(
        "--years", action="store", nargs="+", required=True, help="years to retrieve",
    )

    parser.add_argument(
        "--record-type",
        choices=["application", "grant"],
        action="store",
        help="retrieve applications or grants",
    )

    parser.add_argument(
        "-o",
        "--output-path",
        action="store",
        required=True,
        help="path to folder in which to save output (will be created if necessary)",
    )

    args = parser.parse_args()

    log_level = logging.DEBUG if args.verbose else logging.INFO
    log_level = logging.CRITICAL if args.quiet else log_level
    logging.basicConfig(level=log_level, format="%(message)s")

    for year in args.years:
        output_path = Path(args.output_path) / year
        output_path.mkdir(parents=True, exist_ok=True)
        logging.info(
            colored("Writing files for %s to %s...", "blue"), year, output_path
        )
        urls = get_urls(args.record_type, year)
        for url in urls:
            get_file(url, output_folder=output_path)


if __name__ == "__main__":
    main()
