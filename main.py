import argparse

import pandas as pd
import requests
from bs4 import BeautifulSoup

from scraper import *
from file_utils import get_json_from_file, make_directory_if_not_exists


def get_args():
    parser = argparse.ArgumentParser(description='Get grocery prices from grocery store sites')
    parser.add_argument('-c', '--config', default='config.json',
                        help='JSON formatted file containing URL(s) to scrape')
    return parser.parse_args()

def main():
    args = get_args()
    configs = get_json_from_file(args.config)

    for website in configs['websites']:
        print(website)
        scraper = Scraper(website,
                          configs['headers'],
                          configs['websites'][website],
                          configs['options']
                          )
        
        print(scraper.scrape())

if __name__ == '__main__':
    main()
