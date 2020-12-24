#!/home/ubuntu/anaconda2/envs/python_scraper/bin/python
# -*- coding: utf-8 -*-
"""
Created on Thu Apr  2 18:32:35 2020

@author: Konstantin S.
"""
import requests
from bs4 import BeautifulSoup
import datetime
import os
from links import * #keys, filepath_insolvenz, filepath_ebay, user, pw, info, msg_dict, port, ebay_link
import pandas as pd
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email import encoders
import time


def update_df_rows_if_exists(overall_df, df2, merge_column):
    '''
    Function updates the excel file insolvenz.xlsx with new 
    scraped entries. If something allready in overall_df it 
    will be scipped.
    
    Parameters
    ----------
    overall_df : DataFrame
        The loaded data as DataFrame with all past finding 
    df2 : DataFrame
        the new scraped unique data as DataFrame
    merge_column: String
        indicates the column which will be checked as primary key 
        to find duplicates
        
    Returns
    -------
    overall_df : DataFrame
        Updates the given old DataFrame

    '''
    for nr, row in df2.iterrows():
        if overall_df[merge_column].str.contains(row[merge_column], regex = False).any():
            pass
        else:
            overall_df = overall_df.append(df2.loc[nr])
    
    return overall_df

def populate_df(keys, URL):
    '''
    Populate the a dataframe with scraped information from 
    insolvenzregister
    

    Parameters
    ----------
    keys : List with String
        All keys one is looking for in insolvenzregister e.g. ['geschäft', 'Haus', etc]
    URL : String
        The URL to the insolvenzregister

    Returns
    -------
    df : DataFrame
        populated Dataframe with scraped information.

    '''
    
    df = pd.DataFrame(columns = ['ergebnisse','key', 'timestamp','bekanntmachung'])
    NUMBER = 0
    
    for key in keys:
        payload = ('Suchfunktion=uneingeschr'
                   '&Absenden=Suche+starten'
                   '&Bundesland=Berlin'
                   '&Gericht=--+Alle+Insolvenzgerichte+--'
                   '&Datum1=&Datum2='
                   '&Name=' + key +''
                   '&Sitz=&Abteilungsnr=&Registerzeichen=--&Lfdnr=&Jahreszahl=--&Registerart=--+keine+Angabe+--'
                   '&select_registergericht=&Registergericht=--+keine+Angabe+--'
                   '&Registernummer=&Gegenstand=--+Alle+Bekanntmachungen+innerhalb+des+Verfahrens+--'
                   '&matchesperpage=30'
                   '&page=1'
                   '&sortedby=Datum')
        
        with requests.Session() as s:
            s.headers={"User-Agent":"Mozilla/5.0"}
            s.headers.update({'Content-Type': 'application/x-www-form-urlencoded'})
            res = s.post(URL, data = payload)
            soup = BeautifulSoup(res.text, "lxml")
            anzahl = soup.select('p b')
            try:
                anzahl = [int(s) for s in anzahl[2].get_text().split() if s.isdigit()][0]
            except :
                anzahl = 0
            
            if anzahl > 0:
                for item in soup.select("b li a"):
                    #+ '/' + item.get('href')[item.get('href').find('?'):item.get('href').find('\')')]
                    #respond = s.get( URL )
                    #print('respond\n' + respond.get_text())
                    text = item.get_text()
                    timestamp = text[:text.find('\n')]
                    bekanntmachung = text[text.find('\n'):].strip()
                    df.loc[NUMBER] = [anzahl, key, timestamp, bekanntmachung]
                    NUMBER += 1
    
    return df
 
    
def update_excel_file(original_df, scraped_df, source, filepath, dict_excel):
    '''
    Update old DataFrame with new entries if exist and 
    create new formated excelfile

    Parameters
    ----------
    original_df : DataFrame
        Loaded DataFrame from the original Excelfile
    scraped_df : DataFrame
        concatenated data which 
        holds new scraped data along with old one if exists
    source : String
        String flag holds the scraping source 
    filepath : String
        Path to the old excelfile
    dict_excel : Dictionary
        Holds the Rows as keys and the width as values
        e.g {'A:A':10}

    Returns
    -------
    None.

    '''
    
    sheet_name = os.path.basename(filepath).split('.')[0]
    if not original_df.equals(scraped_df):
        scraped_df['quelle'] = source
        
        # Format Excel file and save
        writer = pd.ExcelWriter(filepath, engine='xlsxwriter')
        scraped_df.to_excel(writer, sheet_name=sheet_name, index=False)
        worksheet = writer.sheets[sheet_name]
        
        for key, pair in dict_excel.items():
            worksheet.set_column(str(key), pair)
        
        writer.save()
        
        msg_dict['Subject'] = 'Neue ' + source + ' entdeckt. ' + msg_dict['Subject']
        time.sleep(15)
        send_email(user = user,
                   pw = pw, 
                   msg_dict = msg_dict,
                   info = info, 
                   port = port, 
                   filepaths_list = filepath)
        
        print('Neue ' + source + ' entdeckt')
    else:
        print('Keine neue '+ source +' hinzugefügt')

def send_email(user, pw, msg_dict, info, port, filepaths_list):
    '''
    Send emails with multiple attachments

    Parameters
    ----------
    user : String
        The credentials user from sftp (amazon simple email )
    pw : String
        the credfentials password from sftp (amazon simple email )
    msg_dict : Dictionary
        Dictionary containing the following keys
        {'From':'mail@mail.de', 
        'To':'mail@mail_to.com',
        'Subject': 'Subject messega',
        'Text': 'email text'}
    info : String
        Server Info connection
    port : Int
        The open port to establish a connection
    filepaths_list : String/ List
        Either a string or a list containing the paths to files which 
        schould be attached

    Returns
    -------
    None.

    '''
    
    msg = MIMEMultipart()
    msg['From']= msg_dict['From']
    msg['To'] = msg_dict['To']
    msg['Subject'] = msg_dict['Subject']
    msg.attach(MIMEText(msg_dict['Text']))
    
    if isinstance(filepaths_list, list):
        for path in filepaths_list:
            part = MIMEBase('application', 'octet-stream') 
            part.set_payload(open(path, 'rb').read())
            encoders.encode_base64(part)
            part.add_header('Content-Disposition', 'attachment', filename=os.path.basename(filepaths_list))
            msg.attach(part)
    else:
        part = MIMEBase('application', 'octet-stream') 
        part.set_payload(open(filepaths_list, 'rb').read())
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', 'attachment', filename=os.path.basename(filepaths_list))
        msg.attach(part)
    try:
        s =  smtplib.SMTP(info, port)
        s.ehlo()
        s.starttls()
        s.login(user,pw)
        s.sendmail(msg_dict['From'], msg_dict['To'], msg.as_string())
        s.quit()
    except Exception as e:
        print(e)
        
def main():
    overall_df = pd.read_excel(filepath_insolvenz) 
    URL = 'https://www.insolvenzbekanntmachungen.de/cgi-bin/bl_suche.pl'
    
    df = populate_df(keys = keys, URL = URL)
    
    # process craped dataframe 
    df = df.drop_duplicates()
    df['timestamp'] = pd.to_datetime(df['timestamp'], format='%Y-%m-%d')
    df['timestamp'] = df['timestamp'].dt.strftime('%d.%m.%Y')
    df[u'hinzugefügt am'] = datetime.date.today().strftime('%d.%m.%Y')
    
    # update
    result = update_df_rows_if_exists(overall_df, df, 'bekanntmachung')
   
    update_excel_file(original_df=overall_df, 
                      scraped_df=result, 
                      source='Insolvenzbekanntmachungen', 
                      filepath=filepath_insolvenz, 
                      dict_excel={'A:B':10,
                                  'C:C':34,
                                  'D:D':23,
                                  'E:E':13})
    
if __name__ == '__main__':
    main()


