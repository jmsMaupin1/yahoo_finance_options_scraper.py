"""
This module is to scrape options data from yahoo finances
"""
__author__ = "jmsMaupin1"

import time
from datetime import date
import json

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import requests

chrome_options = Options()
chrome_options.add_argument("--headless")
browser = webdriver.Chrome(
    options=chrome_options, 
    executable_path='./chromedriver'
)


def get_html(timestamp=None):
    if timestamp:
        data_url = "https://finance.yahoo.com/quote/SPY/options?date={}"
    else:
        browser.get("https://finance.yahoo.com/quote/SPY/options")
        wait = WebDriverWait(browser, 20)
        wait.until(EC.visibility_of_element_located((By.TAG_NAME, 'select')))
        return browser.page_source

    return requests.get(data_url.format(timestamp)).content


def scrape(html):
    """
    First we need to grab all possible expiry dates then
    we iterate over them, requesting the HTML with the dates
    query parameter and send them to the scrape options method
    """
    beautiful_html = BeautifulSoup(html, 'html.parser')
    expiry_dates = beautiful_html.find('select')
    options = {}
    for option in expiry_dates:
        readable_expiry = option.get_text()
        timecode_expiry = option['value']
        options[readable_expiry] = scrape_options(
            get_html(timecode_expiry)
        )
        time.sleep(1)

    return options


def scrape_options(html):
    """ Given some html look for and scape options data from tables """
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
        out.write(json.dumps(options, indent=4))


if __name__ == '__main__':
    main()
