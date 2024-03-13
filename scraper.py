from time import sleep
from bs4 import BeautifulSoup
from selenium import webdriver
import re

import sqlimporter

site_url = 'https://www.domain.com.au/sale/townsville-and-district-qld/?page='
user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36'
not_specified = None

def create_browser():
    #create a selenium object that mimics the browser
    browser_options = webdriver.ChromeOptions()
    #headless tag created an invisible browser
    browser_options.add_argument("--headless=new")
    browser_options.add_argument('--no-sandbox')
    browser_options.add_argument('--disable-gpu')
    browser_options.add_argument("user-agent=" + user_agent)
    browser = webdriver.Chrome(options=browser_options)
    print("Done Creating Browser")
    return browser

def parse_page(broswer, URL):
    browser.get(URL)
    pageHTML = browser.page_source
    
    soup = BeautifulSoup(pageHTML, 'html.parser')
    listingsHTML = soup.find_all('li', attrs={'data-testid' : re.compile(r'^listing-\d{5,}$')})

    return listingsHTML

def create_listing_object(listingHTML):
    priceHTML = listingHTML.find('p', attrs={'data-testid' : 'listing-card-price'})

    address1HTML = listingHTML.find('span', attrs={'data-testid' : 'address-line1'})
    address2HTML = listingHTML.find('span', attrs={'data-testid' : 'address-line2'})

    bathHTML = listingHTML.find(string=re.compile(r'baths?', re.IGNORECASE))
    bedHTML = listingHTML.find(string=re.compile(r'beds?', re.IGNORECASE))
    parkingHTML = listingHTML.find(string=re.compile(r'parking', re.IGNORECASE))

    areaHTML = listingHTML.find(string=re.compile(r'm²', re.IGNORECASE))
    
    linkHTML = listingHTML.find('a')

    typeHTML = listingHTML.find('span', attrs={'class' : 'css-693528'})
    
    #description = listingHTML.find('div', attrs={'data-testid' : 'listing-details_description'})

    return {'price' : handle_price(priceHTML) if priceHTML else not_specified, 
            'address' : handle_address(address1HTML, address2HTML), 
            'bed' : int_from_html_parent(bedHTML) if bedHTML else not_specified, 
            'bath' : int_from_html_parent(bathHTML) if bathHTML else not_specified, 
            'parking' : int_from_html_parent(parkingHTML) if parkingHTML else not_specified, 
            'area' : handle_area(areaHTML) if areaHTML else not_specified,  
            'link' : handle_link(linkHTML) if linkHTML else not_specified,
            'type' : handle_type(typeHTML) if typeHTML else not_specified}

def handle_type(typeHTML):
    return typeHTML.text

def int_from_html_parent(html):
    htmlString = html.parent.parent.text.strip(r'\d+')[0]
    if "−" in htmlString: 
        return not_specified
    return int(htmlString)

def handle_link(linkHTML):
    return linkHTML.get('href')

def handle_area(areaHTML):
    areaString = re.search(r'\d+', areaHTML.replace(",", "")).group()
    return int(areaString)

def handle_price(priceHTML):
    text = priceHTML.text
    text = text.replace(",", "")
    match = re.search(r'\d+', text)
    return int(match.group()) if match else not_specified

def handle_address(address1HTML, address2HTML):
    if address1HTML and address2HTML:
        return address1HTML.text.strip() + " " + address2HTML.text.strip()
    elif address1HTML:
        return address1HTML.text.strip()
    elif address2HTML:
        return address2HTML.text.strip()
    else:
        return not_specified

# replace with number of pages
def parse_website(pages):
    for i in range(1, pages):
        listingsHTML = parse_page(broswer=browser, URL=site_url + str(i))
        for listing in listingsHTML:
            listingObject = create_listing_object(listing)
            print(listingObject)
            #sqlimporter.insert_data(connection=connection, data=listingObject)

browser = create_browser()
#connection = sqlimporter.connect()

parse_website(4)

#sqlimporter.disconnect(connection)