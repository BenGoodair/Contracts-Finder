# -*- coding: utf-8 -*-
"""
Created on Mon Jan 30 15:16:06 2023

@author: bengo
"""

# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""



#My aim with this was to scrape every single awarded contract on contracts finder.
#So I wanted to perform an empty search for all 'awarded' contracts, click on each contract in turn, 
#scrape all available information from the html and repeat until 20 contracts had passed
#then click 'next page' and repeat thousands of times over
#This process was partially because I wanted the data (which I've still done nothing with)
#But also partially a learning exercise to try an emulate my academic computer science idols...


#packages

import scrapy
import selenium
import requests
import time
import pandas
import pandas as pd
from bs4 import BeautifulSoup
import time


from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.keys import Keys




options = webdriver.ChromeOptions() 
#can't remember if these arguments to disable infobars were necessary or just copied from internet
options.add_argument("start-maximized")
options.add_argument('disable-infobars')

#set link to chromedriver app on local machine
driver = webdriver.Chrome(chrome_options=options, executable_path=r'C:\Users\bengo\chromedriver.exe')
#set contracts finder search website
driver.get("https://www.contractsfinder.service.gov.uk/Search")


#Here the driver scrolls down, unticks the pre-ticked options that we don't want and ticks the 'awarded contracts' and presses search
#Driver wait times were very important going inbetween contracts but generally fine here

driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, ".//*[contains(text(),'Awarded')]"))).click()
WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, ".//*[contains(text(),'opportunity')]"))).click()
WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, ".//*[contains(text(),'Opportunity')]"))).click()
WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, ".//*[contains(text(),'engagement')]"))).click()
WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, ".//*[contains(text(),'Search')]"))).click()

time.sleep(1)

#Because my driver would crash, I needed to set it off again starting at a certain date 
#The following code clicks and searches for contracts before a certain time
WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, ".//*[contains(text(),'Date range')]"))).click()
WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, ".//*[contains(text(),'Contract awarded date')]"))).click()
inputElement_day = driver.find_element("id", "awarded_date_to-day")
inputElement_day.send_keys('01')
inputElement_month = driver.find_element("id","awarded_date_to-month")
inputElement_month.send_keys('06')
inputElement_year = driver.find_element("id","awarded_date_to-year")
inputElement_year.send_keys('2015')
WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, ".//*[contains(text(),'Update results')]"))).click()

#Time sleeps were generally important for me
time.sleep(1)

#A lazy coding habit I have is to create one df first, then run a loop to append all the others to that first df
#Below I create 'master_df' for the first contract which is where all results will be binded
#Click on contract
content = driver.find_elements(By.CLASS_NAME,"search-result-header")
WebDriverWait(driver, 20).until(EC.element_to_be_clickable(content[0])).click()
#Take source code
html_source_code = driver.execute_script("return document.body.innerHTML;")
soup = BeautifulSoup(html_source_code, 'html.parser')
#extract title of contract
result_header = soup.find_all(class_="govuk-heading-l break-word")
#extract commissioner
commissioner = soup.find_all(lambda tag: tag.name == 'div' and 
                           tag.get('class') == ['standard-col'])[0]
#extract date
publication_date = soup.find_all(lambda tag: tag.name == 'div' and 
                           tag.get('class') == ['search-no-top-margin'])
#extract content block
contract_details = list(soup.find_all(lambda tag: tag.name == 'div' and 
                           tag.get('class') == ['content-block']))
#rewrite content block as string
contract_details2=list([element.get_text() for element in contract_details])
string_version = "".join(contract_details2)
string_version="".join([s for s in string_version.strip().splitlines(True) if s.strip()])

#create master df (first observation)
master_df = pd.DataFrame()
#assign columns
master_df = master_df.assign(
commissioner = [element.get_text() for element in commissioner],
reference_no = string_version[string_version.find('Procurement reference'):string_version.find('Published date',string_version.find('Procurement reference'))], 
title = list([element.get_text() for element in result_header[0:len(result_header)]]),
description = string_version[string_version.find('Description')+len('Description'):string_version.rfind('More')], 
contract_SIC =string_version[string_version.find('Industry')+len('Industry'):string_version.rfind('Location')],
contract_location =string_version[string_version.find('Location of contract')+len('Location of contract'):string_version.find('Value',string_version.find('Location of contract') )],
published_date = string_version[string_version.find('Published date')+len('Published date'):string_version.find('Closing date', string_version.find('Published date'))], 
closing_date = string_version[string_version.find('Closing date')+len('Closing date'):string_version.rfind('Closing time')], 
awarded_date = string_version[string_version.find('Awarded date')+len('Awarded date'):string_version.rfind('Contract start date')], 
contract_start_date = string_version[string_version.find('Contract start date\n')+len('Contract start date\n'):string_version.find('Contract end date',string_version.find('Contract start date') )], 
contract_end_date = string_version[string_version.find('Contract end date')+len('Contract end date'):string_version.rfind('Contract type')], 
contract_type = string_version[string_version.find('Contract type')+len('Contract type'):string_version.rfind('Procedure type')], 
#procedure_type = string_version[string_version.find('Procedure type')+len('Procedure type'):string_version.rfind('What')], 
suitable_for_SMEs = string_version[string_version.find('SMEs?')+len('SMEs?'):string_version.rfind('Contract is suitable for VCSEs')], 
suitable_for_VCSEs = string_version[string_version.find('VCSEs?')+len('VCSEs?'):string_version.rfind('Description')], 
Advertised_value = string_version[string_version.find('Value of contract')+len('Value of contract'):string_version.rfind('Procurement reference')], 
Awarded_value = string_version[string_version.find('Total value of contract')+len('Total value of contract'):string_version.rfind('This contract')], 
suppliers_n = string_version[string_version.find('was awarded to')+len('was awarded to'):string_version.find('\n',string_version.find('was awarded to') )], 
#shared_supplier_name_rest = string_version[string_version.find('is VCSE?')+len('is VCSE?'):string_version.find('Show supplier information', string_version.find('is VCSE?'))], 
supplier_address = string_version[string_version.find('Address')+len('Address'):string_version.find('Reference', string_version.find('Address'))], 
supplier_is_SME = string_version[string_version.find('is SME?')+len('is SME?'):string_version.find('Supplier', string_version.find('is SME?'))], 
supplier_is_VCSE = string_version[string_version.find('is VCSE?')+len('is VCSE?'):string_version.find('About the buyer', string_version.find('is VCSE?'))], 
supplier_reference = string_version[string_version.find('Reference')+len('Reference'):string_version.find('Supplier is SME?', string_version.find('Reference'))], 
commissioner_name = string_version[string_version.find('Contact name')+len('Contact name'):string_version.rfind('Address')], 
commissioner_address = string_version[string_version.find('Contact name')+len('Contact name'):string_version.rfind('Email')])
#Sometimes there are multiple suppliers, websites, procedure types etc. - so extracting needs to vary depending on info
if 'supplier.' in string_version:
        supplier_name = string_version[string_version.find('supplier.')+len('supplier.'):string_version.find('Show supplier')],
else:
        supplier_name = string_version[string_version.find('suppliers.')+len('suppliers.'):string_version.find('Show supplier')], 

if 'suppliers.' in string_version:
    shared_supplier_information_ = string_version[string_version.find('is VCSE?')+len('is VCSE?'):string_version.find('About the buyer', string_version.find('is VCSE?'))] 
else:
    shared_supplier_information_ = 'na'

if 'Website' in string_version:
        commissioner_website=string_version[string_version.find('Website')+len('Website'):string_version.rfind('/')]
else:
        commissioner_website='na'
        
if 'Procedure type' in string_version:
        procedure_type = string_version[string_version.find('Procedure type')+len('Procedure type'):string_version.rfind('What')]
else:
        procedure_type='na'
#add the varying columns        
master_df=master_df.assign(commissioner_website=commissioner_website,
                           supplier_name=supplier_name,
                           shared_supplier_information_= shared_supplier_information_,
                           procedure_type=procedure_type)

#return to search list
driver.back()

#now repeat for the next 19 contracts on the page
for x in range(1,20):

    
    content = driver.find_elements(By.CLASS_NAME,"search-result-header")
    WebDriverWait(driver, 20).until(EC.element_to_be_clickable(content[x])).click()
    html_source_code = driver.execute_script("return document.body.innerHTML;")
    soup = BeautifulSoup(html_source_code, 'html.parser')
    result_header = soup.find_all(class_="govuk-heading-l break-word")
    commissioner = soup.find_all(lambda tag: tag.name == 'div' and 
                               tag.get('class') == ['standard-col'])[0]
    publication_date = soup.find_all(lambda tag: tag.name == 'div' and 
                               tag.get('class') == ['search-no-top-margin'])
    
    contract_details = list(soup.find_all(lambda tag: tag.name == 'div' and 
                               tag.get('class') == ['content-block']))
    
    contract_details2=list([element.get_text() for element in contract_details])
    string_version = "".join(contract_details2)
    string_version="".join([s for s in string_version.strip().splitlines(True) if s.strip()])
    
    df = pd.DataFrame()
    df = df.assign(
    commissioner = [element.get_text() for element in commissioner],
    reference_no = string_version[string_version.find('Procurement reference'):string_version.find('Published date',string_version.find('Procurement reference'))], 
    title = list([element.get_text() for element in result_header[0:len(result_header)]]),
    description = string_version[string_version.find('Description')+len('Description'):string_version.rfind('More')], 
    contract_SIC =string_version[string_version.find('Industry')+len('Industry'):string_version.rfind('Location')],
    contract_location =string_version[string_version.find('Location of contract')+len('Location of contract'):string_version.find('Value',string_version.find('Location of contract') )],
    published_date = string_version[string_version.find('Published date')+len('Published date'):string_version.find('Closing date', string_version.find('Published date'))], 
    closing_date = string_version[string_version.find('Closing date')+len('Closing date'):string_version.rfind('Closing time')], 
    awarded_date = string_version[string_version.find('Awarded date')+len('Awarded date'):string_version.rfind('Contract start date')], 
    contract_start_date = string_version[string_version.find('Contract start date\n')+len('Contract start date\n'):string_version.find('Contract end date',string_version.find('Contract start date') )], 
    contract_end_date = string_version[string_version.find('Contract end date')+len('Contract end date'):string_version.rfind('Contract type')], 
    contract_type = string_version[string_version.find('Contract type')+len('Contract type'):string_version.rfind('Procedure type')], 
   #procedure_type = string_version[string_version.find('Procedure type')+len('Procedure type'):string_version.rfind('What')], 
    suitable_for_SMEs = string_version[string_version.find('SMEs?')+len('SMEs?'):string_version.rfind('Contract is suitable for VCSEs')], 
    suitable_for_VCSEs = string_version[string_version.find('VCSEs?')+len('VCSEs?'):string_version.rfind('Description')], 
    Advertised_value = string_version[string_version.find('Value of contract')+len('Value of contract'):string_version.rfind('Procurement reference')], 
    Awarded_value = string_version[string_version.find('Total value of contract')+len('Total value of contract'):string_version.rfind('This contract')], 
    suppliers_n = string_version[string_version.find('was awarded to')+len('was awarded to'):string_version.find('\n',string_version.find('was awarded to') )], 
 #   supplier_name = string_version[string_version.find('supplier.')+len('supplier.'):string_version.find('Show supplier')], 
  #  shared_supplier_name_1 = string_version[string_version.find('suppliers.')+len('suppliers.'):string_version.find('Show supplier')], 
  #  shared_supplier_name_rest = string_version[string_version.find('is VCSE?')+len('is VCSE?'):string_version.find('Show supplier information', string_version.find('is VCSE?'))], 
    supplier_address = string_version[string_version.find('Address')+len('Address'):string_version.find('Show supplier', string_version.find('Address'))], 
    supplier_is_SME = string_version[string_version.find('is SME?')+len('is SME?'):string_version.find('Supplier', string_version.find('is SME?'))], 
    supplier_is_VCSE = string_version[string_version.find('is VCSE?')+len('is VCSE?'):string_version.find('About the buyer', string_version.find('is VCSE?'))], 
    supplier_reference = string_version[string_version.find('Reference')+len('Reference'):string_version.find('Supplier is SME?', string_version.find('Reference'))], 
    commissioner_name = string_version[string_version.find('Contact name')+len('Contact name'):string_version.rfind('Address')], 
    commissioner_address = string_version[string_version.find('Contact name')+len('Contact name'):string_version.rfind('Email')])
   # commissioner_website = string_version[string_version.find('Website')+len('Website'):string_version.rfind('/')])
    
    if 'supplier.' in string_version:
        supplier_name = string_version[string_version.find('supplier.')+len('supplier.'):string_version.find('Show supplier')],
    else:
        supplier_name = string_version[string_version.find('suppliers.')+len('suppliers.'):string_version.find('Show supplier')], 

    if 'suppliers.' in string_version:
        shared_supplier_information_ = string_version[string_version.find('is VCSE?')+len('is VCSE?'):string_version.find('About the buyer', string_version.find('is VCSE?'))] 
    else:
        shared_supplier_information_ = 'na'

    if 'Website' in string_version:
        commissioner_website=string_version[string_version.find('Website')+len('Website'):string_version.rfind('/')]
    else:
        commissioner_website='na'
        
    if 'What is a' in string_version:
        procedure_type = string_version[string_version.find('Procedure type')+len('Procedure type'):string_version.rfind('What')]
    else:
        procedure_type= string_version[string_version.find('Procedure type')+len('Procedure type'):string_version.find('Contract is suitable', string_version.find('Procedure type'))]
        

        
    df=df.assign(commissioner_website=commissioner_website,
                           supplier_name=supplier_name,
                           shared_supplier_information_= shared_supplier_information_,
                           procedure_type=procedure_type)

    
    
    master_df = master_df.append(df, ignore_index=True)
    driver.back()
    time.sleep(1)
    
    
    
#click to the next page 
WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, ".//*[contains(@class, 'standard-paginate-next govuk-link break-word')]"))).click()

#Now repeat 301 times

for y in range(301):

  for x in range(20):

    
    content = driver.find_elements(By.CLASS_NAME,"search-result-header")
    WebDriverWait(driver, 20).until(EC.element_to_be_clickable(content[x])).click()
    html_source_code = driver.execute_script("return document.body.innerHTML;")
    soup = BeautifulSoup(html_source_code, 'html.parser')
    result_header = soup.find_all(class_="govuk-heading-l break-word")
    commissioner = soup.find_all(lambda tag: tag.name == 'div' and 
                               tag.get('class') == ['standard-col'])[0]
    publication_date = soup.find_all(lambda tag: tag.name == 'div' and 
                               tag.get('class') == ['search-no-top-margin'])
    
    contract_details = list(soup.find_all(lambda tag: tag.name == 'div' and 
                               tag.get('class') == ['content-block']))
    
    contract_details2=list([element.get_text() for element in contract_details])
    string_version = "".join(contract_details2)
    string_version="".join([s for s in string_version.strip().splitlines(True) if s.strip()])
    
    df = pd.DataFrame()
    df = df.assign(
    commissioner = [element.get_text() for element in commissioner],
    reference_no = string_version[string_version.find('Procurement reference'):string_version.find('Published date',string_version.find('Procurement reference'))], 
    title = list([element.get_text() for element in result_header[0:len(result_header)]]),
    description = string_version[string_version.find('Description')+len('Description'):string_version.rfind('More')], 
    contract_SIC =string_version[string_version.find('Industry')+len('Industry'):string_version.rfind('Location')],
    contract_location =string_version[string_version.find('Location of contract')+len('Location of contract'):string_version.find('Value',string_version.find('Location of contract') )],
    published_date = string_version[string_version.find('Published date')+len('Published date'):string_version.find('Closing date', string_version.find('Published date'))], 
    closing_date = string_version[string_version.find('Closing date')+len('Closing date'):string_version.rfind('Closing time')], 
    awarded_date = string_version[string_version.find('Awarded date')+len('Awarded date'):string_version.rfind('Contract start date')], 
    contract_start_date = string_version[string_version.find('Contract start date\n')+len('Contract start date\n'):string_version.find('Contract end date',string_version.find('Contract start date') )], 
    contract_end_date = string_version[string_version.find('Contract end date')+len('Contract end date'):string_version.rfind('Contract type')], 
    contract_type = string_version[string_version.find('Contract type')+len('Contract type'):string_version.rfind('Procedure type')], 
    procedure_type = string_version[string_version.find('Procedure type')+len('Procedure type'):string_version.rfind('What')], 
    suitable_for_SMEs = string_version[string_version.find('SMEs?')+len('SMEs?'):string_version.rfind('Contract is suitable for VCSEs')], 
    suitable_for_VCSEs = string_version[string_version.find('VCSEs?')+len('VCSEs?'):string_version.rfind('Description')], 
    Advertised_value = string_version[string_version.find('Value of contract')+len('Value of contract'):string_version.rfind('Procurement reference')], 
    Awarded_value = string_version[string_version.find('Total value of contract')+len('Total value of contract'):string_version.rfind('This contract')], 
    suppliers_n = string_version[string_version.find('was awarded to')+len('was awarded to'):string_version.find('\n',string_version.find('was awarded to') )], 
 #   supplier_name = string_version[string_version.find('supplier.')+len('supplier.'):string_version.find('Show supplier')], 
  #  shared_supplier_name_1 = string_version[string_version.find('suppliers.')+len('suppliers.'):string_version.find('Show supplier')], 
  #  shared_supplier_name_rest = string_version[string_version.find('is VCSE?')+len('is VCSE?'):string_version.find('Show supplier information', string_version.find('is VCSE?'))], 
    supplier_address = string_version[string_version.find('Address')+len('Address'):string_version.find('Show supplier', string_version.find('Address'))], 
    supplier_is_SME = string_version[string_version.find('is SME?')+len('is SME?'):string_version.find('Supplier', string_version.find('is SME?'))], 
    supplier_is_VCSE = string_version[string_version.find('is VCSE?')+len('is VCSE?'):string_version.find('About the buyer', string_version.find('is VCSE?'))], 
    supplier_reference = string_version[string_version.find('Reference')+len('Reference'):string_version.find('Supplier is SME?', string_version.find('Reference'))], 
    commissioner_name = string_version[string_version.find('Contact name')+len('Contact name'):string_version.rfind('Address')], 
    commissioner_address = string_version[string_version.find('Contact name')+len('Contact name'):string_version.rfind('Email')])
   # commissioner_website = string_version[string_version.find('Website')+len('Website'):string_version.rfind('/')])
    
    if 'supplier.' in string_version:
        supplier_name = string_version[string_version.find('supplier.')+len('supplier.'):string_version.find('Show supplier')],
    else:
        supplier_name = string_version[string_version.find('suppliers.')+len('suppliers.'):string_version.find('Show supplier')], 

    if 'suppliers.' in string_version:
        shared_supplier_information_ = string_version[string_version.find('is VCSE?')+len('is VCSE?'):string_version.find('About the buyer', string_version.find('is VCSE?'))] 
    else:
        shared_supplier_information_ = 'na'


    if 'Website' in string_version:
        commissioner_website=string_version[string_version.find('Website')+len('Website'):string_version.rfind('/')]
    else:
        commissioner_website='na'
        
    if 'Procedure type' in string_version:
        procedure_type = string_version[string_version.find('Procedure type')+len('Procedure type'):string_version.rfind('What')]
    else:
        procedure_type='na'
        

        
    df=df.assign(commissioner_website=commissioner_website,
                           supplier_name=supplier_name,
                           shared_supplier_information_= shared_supplier_information_,
                           procedure_type=procedure_type)

    
    
    master_df = master_df.append(df, ignore_index=True)
    driver.back()
    time.sleep(1)
    
    
    
    
  WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, ".//*[contains(@class, 'standard-paginate-next govuk-link break-word')]"))).click()





