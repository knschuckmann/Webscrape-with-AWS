#!/home/ubuntu/anaconda2/envs/python_scraper/bin/python
# -*- coding: utf-8 -*-
"""
Created on Sun Dec 20 13:29:28 2020

@author: Konstantin S.
"""

import requests
from bs4 import BeautifulSoup
import datetime
import re
from links import * #ebay_link, filepath_ebay
from insolvenzregister import update_df_rows_if_exists, update_excel_file
import pandas as pd
import os

def populate_df(URL, headers, base_url):
    '''
    Populate the a dataframe with scraped information from 
    Ebay Kleinanzeigen

    Parameters
    ----------
    URL : String
         The additional URL indicating all search options
         everything that comes after www.ebay-kleinanzeigen.de 
    headers : Dictionary
        Indicating which user agent is scraping with more metadata
    base_url : String
        The URL to the Ebay Kleinanzeigen.

    Returns
    -------
    df : DataFrame
        Updates the given old DataFrame

    '''

    df = pd.DataFrame(columns = ['titel', 'release date','url', 
                                 'price', 'qm', 'zip', 'ort'])
    
    # get whole page
    response = requests.get(url=URL, headers=headers)
    page = response.content
    soup = BeautifulSoup(page, "html.parser")

    # validate amount
    result_number = soup.find_all('span', class_='breadcrump-summary', text=True)
    number_pattern = re.compile('\d+')
    amount_results = int(re.findall(number_pattern, result_number[0].get_text())[2])
    # get only validated results
    results = soup.find_all('ul', id='srchrslt-adtable')
    results = results[0].find_all('article', class_='aditem')
    
    if amount_results == len(results):
        for nr, result in enumerate(results):    
            # df titel
            title = result.find_all('a', class_='ellipsis')[0].get_text()
            # df qm    
            qm = result.find_all('span', class_='simpletag')[0].get_text().strip()
            # df url
            sub_url = base_url + result.find_all('a', class_='ellipsis')[0]['href']
            # df price, zip, ort
            text = result.find_all('div', class_='aditem-details')[0].get_text()
            list_text = text.strip().split('\n')
            price, zip_code, ort = [list_text[0].strip(),
                                    list_text[2].strip(),
                                    list_text[3].strip()]
            
            # df released
            rel_date = result.find_all('div', 
                                       class_='aditem-addon')[0].get_text().strip()
            
            df.loc[nr] = [title, rel_date, 
                         sub_url, price, qm,
                         zip_code, ort]
    return df


def main():

    # All findings until now 
    overall_df = pd.read_excel(filepath_ebay, encoding='utf-8')

    base_url = 'https://www.ebay-kleinanzeigen.de'
    
    # e.g. ebay_link:= /s-immobilien/berlin/....
    URL = base_url + ebay_link
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.125 Safari/537.36 Edg/84.0.522.59',
    }

    df = populate_df(URL=URL, headers=headers, base_url=base_url)
    # process craped dataframe 
    df = df.drop_duplicates()
    df[u'hinzugefügt am'] = datetime.date.today().strftime('%d.%m.%Y')
    # update
    result = update_df_rows_if_exists(overall_df, df, 'titel')
    
    update_excel_file(original_df=overall_df, 
                      scraped_df=result, 
                      source='Ebay kleinanzeigen', 
                      filepath=filepath_ebay, 
                      dict_excel={'A:A':15,
                                  'B:B':10,
                                  'C:C':34,
                                  'D:D':15,
                                  'G:I':13})

if __name__ =='__main__':
    main()





    