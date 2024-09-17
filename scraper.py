import os
import time
from os import listdir
from os.path import isfile, join

import pandas as pd
import requests
from bs4 import BeautifulSoup

from file_utils import dir_exists

class Scraper:
    def __init__(self, headers: dict, website: dict, options: dict):
        self.headers = headers
        self.base_url = website['base_url']
        self.pagination_delimiter = website['pagination_delimiter']
        self.options = options
        self.save_folder = website['read_html_folder']
        self._item = []
        self._price = []

    def scrape(self) -> pd.DataFrame:
        if self.options['read_html_from_folder']:
            return self.scrape_from_folder(self.save_folder)
        else:
            return self.scrape_from_url()

    def scrape_from_folder(self, folder: str) -> pd.DataFrame:
        # List all files in with absolute paths from root directory.
        # https://www.askpython.com/python/examples/python-directory-listing
        files = [os.path.join(folder, f) for f in os.listdir(folder)]
        if not files:
            raise ValueError(f'No files in "{folder}" folder')

        return pd.concat([self.scrape_from_file(f) for f in files], ignore_index=True)

    def scrape_from_file(self, filename: str) -> pd.DataFrame:
        with open(filename, 'r') as f:
            soup = BeautifulSoup(f, 'lxml')

        names = []
        prices = []
        unit_costs = []

        product_name = soup.find_all('span',{'class': 'normal dark-gray mb0 mt1 lh-title f6 f5-l lh-copy'})
        cost_per_unit = soup.find_all('div',{'class': 'gray mr1 f6 f5-l flex items-end mt1'})
        price_dollars = soup.find_all('span',{'class': 'f2'})
        price_cents = soup.find_all('span',{'class': 'f6 f5-l', 'style': 'vertical-align:0.75ex'})

        for name, price_dollar, price_cent, unit_cost in zip (product_name, price_dollars, price_cents, cost_per_unit):
            names.append(name.string.string.strip())
            prices.append(int(price_dollar.string.strip()) + float('.' + price_cent.string.strip()))
            # unit_costs.append(unit_cost.string.strip())

        self._item += names                        
        self._price += prices
        return pd.DataFrame({'item': self._item, 'price': self._price})

    def scrape_from_url(self, url: str, sleep_time: int) -> list:
        time.sleep(sleep_time)
        pass