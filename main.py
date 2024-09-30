import argparse
from datetime import datetime

import pandas as pd
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
    dataframes = []

    for website in configs['websites']:
        print(website)
        scraper = Scraper(website,
                          configs['headers'],
                          configs['websites'][website],
                          configs['options']
                          )
        
        df = scraper.scrape()
        dataframes.append(df)
        print(df)

    file_name = datetime.today().strftime('%Y-%m-%d-%H:%M:%S') + '-grocery-prices.csv'
    all_data = pd.concat(dataframes)
    all_data.to_csv(file_name)

if __name__ == '__main__':
    main()
