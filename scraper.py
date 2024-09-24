import os
import time
from datetime import datetime

import pandas as pd
import requests
from bs4 import BeautifulSoup

from file_utils import dir_exists


class Scraper:
    def __init__(self, website_name: str, headers: dict, website: dict, options: dict):
        self.website_name = website_name
        self.headers = headers
        self.base_url = website['base_url']
        self.pagination_delimiter = website['pagination_delimiter']
        self.options = options
        self.read_from_folder = website['read_html_folder']
        self.write_to_folder = website['write_html_folder']
        self._item = []
        self._price = []

        self.urls = self.construct_urls(self.base_url,
                                        self.options['search_terms'],
                                        self.pagination_delimiter,
                                        self.options['how_many_html_pages_to_read'],
                                        )

    def construct_urls(self, base_url: str, search_terms: list, pagination: str, pages: int = None) -> list:
        urls = []
        # No point in specifying page number 1 in the URL, the websites will do that automatically if needed.
        if pages and pages != 1:
            for term in search_terms:
                # Pagination can't start at 0 so start at 1 and add 1 to the total page number to adjust.
                for i in range(1,pages+1):
                    urls.append(base_url+term+pagination+str(i))
        else:
            urls = [base_url+term for term in search_terms]
        return urls

    def scrape(self) -> pd.DataFrame:
        if self.options['read_html_from_folder']:
            return self.scrape_from_folder(self.read_from_folder)
        else:
            return self.scrape_from_urls(self.urls, self.options['sleep_time_between_requests'])

    def scrape_from_folder(self, folder: str) -> pd.DataFrame:
        # List all files in with absolute paths from root directory.
        # https://www.askpython.com/python/examples/python-directory-listing
        files = [os.path.join(folder, f) for f in os.listdir(folder)]
        if not files:
            raise ValueError(f'No files in "{folder}" folder')

        return pd.concat([self.scrape_from_file(f) for f in files], ignore_index=True)

    def scrape_from_file(self, filename: str) -> pd.DataFrame:
        with open(filename, 'r') as f:
            return self.scrape_from_soup(BeautifulSoup(f, 'lxml'))

    def scrape_from_urls(self, urls: list, sleep_time: int) -> list:
        return pd.concat([self.scrape_from_url(url, sleep_time) for url in urls], ignore_index=True)

    def scrape_from_url(self, url: str, sleep_time: int) -> pd.DataFrame:
        print(f'Scraping {url}')
        html = requests.get(url, headers=self.headers)
        soup = BeautifulSoup(html.text, 'lxml')

        if self.options['save_html_to_folder']:
            file_name = datetime.today().strftime('%Y-%m-%d-%H:%M:%S') + f'-{self.website_name}.html'
            write_path = self.write_to_folder + file_name
            with open(write_path, 'w') as writer:
                writer.write(soup.prettify())

        dataframe = self.scrape_from_soup(soup)
        print(f'Sleeping {sleep_time} seconds')
        time.sleep(sleep_time)
        return dataframe

    def scrape_from_soup(self, soup: BeautifulSoup) -> pd.DataFrame:
        names = []
        prices = []
        # unit_costs = []

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
