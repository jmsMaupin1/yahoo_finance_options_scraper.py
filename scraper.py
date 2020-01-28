#!/usr/bin/env python3
"""
This module is to scrape options data from yahoo finances
"""
__author__ = "jmsMaupin1"

from bs4 import BeautifulSoup
from datetime import date
import requests


def get_html():
    data_url = "https://finance.yahoo.com/quote/SPY/options"
    return requests.get(data_url).content


def scrape(html):
    option_types = ['calls', 'puts']
    html = BeautifulSoup(html, 'html.parser')
    tables = html.find_all('table')
    options_data = {}

    # There are two tables, first is calls second table is puts
    # We use the index with the options_types array to determine
    # Wether we are looking at calls or puts and place them in the
    # correct kevy under options_data
    for i, table in enumerate(tables):
        headers = []
        options = {}

        # Pull out cell header titles
        for cell in table.thead.tr:
            headers.append(cell.get_text())

        # Grab all the data and associate it in the dict
        # with its table header
        for row in table.tbody:
            option = {}
            for j, cell in enumerate(row):
                if j == 0:
                    continue

                option[headers[j]] = cell.get_text()
            options[row.td.get_text()] = option

        options_data[option_types[i]] = options

    return options_data


def main():
    # Opents a file named after todays date in the format of
    # YYYY-MM-DD.json, then writes the parsed options_data object
    # To the file
    with open("{}.json".format(date.today()), 'w+') as out:
        options = scrape(get_html())
        out.write(str(options))


if __name__ == '__main__':
    main()
