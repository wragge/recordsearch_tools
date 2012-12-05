'''
Created on 16/02/2011

@author: tim
'''
import os.path
import urllib2
import urllib
import cookielib
import sys
import re
import string
from lxml.builder import E
from lxml import etree
from BeautifulSoup import BeautifulSoup
import mechanize
import logging

import utilities
#logger = logging.getLogger("mechanize")
#logger.addHandler(logging.StreamHandler(sys.stdout))
#logger.setLevel(logging.DEBUG)

#COOKIEFILE = 'cookies.lwp'


#Load Search page to set cookies - http://naa12.naa.gov.au/scripts/Logon.asp?N=guest


#Construct search and POST to search.asp

#Extract search number and other params from Display button 

#Construct items_listing.asp url

#loop over display items pages until all items have been displayed

#harvest details of items 

class RSClient:
    
    def __init__(self):
        self.br = mechanize.Browser()
        self.br.addheaders = [('User-agent', 'Mozilla/5.0 (Windows; U; Windows NT 6.0; en-US; rv:1.9.0.6')]
        self.br.set_handle_robots(False)
        self.response = None
        self.results = None
        self.total_results = None
        
    def get_page(self, url):
        response1 = self.br.open(url)
        # Recordsearch returns a page with a form that submits on page load.
        # Have to make sure the session id is submitted with the form.
        # Extract the session id.
        session_id = re.search(r"value={(.*)}", response1.read()).group(1)
        self.br.select_form(name="t")
        self.br.form.set_all_readonly(False)
        # Add session id to the form.
        self.br.form['NAASessionID'] = '{%s}' % session_id
        response2 = self.br.submit()
        self.response = response2
        
    def get_reference(self, barcode):
        url = 'http://www.naa.gov.au/cgi-bin/Search?O=I&Number=%s' % barcode
        self.get_page(url)
        soup = BeautifulSoup(self.response.read())
        series = soup.find(text="Series number").parent.parent.findNextSiblings()[0].a.string
        control_symbol = soup.find(text="Control symbol").parent.parent.findNextSiblings()[0].string
        if soup.find(text="View digital copy "):
            digitised = True
        else:
            digitised = False
        return {'series': series, 'control_symbol': control_symbol, 'digitised': digitised}
    
    def get_total_results(self, soup):
        total = re.search('of (\d+)', soup.find('span', attrs={'id': 'ctl00_ContentPlaceHolderSNRMain_lblDisplaying'}).string).group(1)
        #total = soup.find('p').string
        self.total_results = total
    
    def get_page_total(self, barcode):
        url = 'http://recordsearch.naa.gov.au/scripts/Imagine.asp?B=%s&I=1&SE=1' % barcode
        response = self.br.open(url)
        soup = BeautifulSoup(response.read())
        pages = soup.find('input', attrs={'id': "Hidden3"})['value']
        return pages
    
    def get_series_summary(self, series_id):
        url = 'http://www.naa.gov.au/cgi-bin/Search?Number=%s' % series_id
        self.get_page(url)
        soup = BeautifulSoup(self.response.read())
        details = soup.find('div', 'detailsTable')
        identifier = details.find(text=re.compile("Series number")).parent.parent.findNextSiblings('td')[0].string
        title = details.find(text=re.compile("Title")).parent.parent.findNextSiblings('td')[0].string
        accumulation_dates = {}
        try:
            accumulation_dates['date_range'] = details.find(text=re.compile("Accumulation dates")).parent.parent.findNextSiblings('td')[0].string
        except AttributeError:
            pass
        else:
            accumulation_date_parsed = utilities.process_date(accumulation_dates['date_range'])
            accumulation_dates['start_date'], accumulation_dates['start_day'], accumulation_dates['start_month'], accumulation_dates['start_year'] = accumulation_date_parsed[0]
            if len(accumulation_date_parsed) == 2:
                accumulation_dates['end_date'], accumulation_dates['end_day'], accumulation_dates['end_month'], accumulation_dates['end_year'] = accumulation_date_parsed[1]
            else:
                accumulation_dates['end_date'], accumulation_dates['end_day'], accumulation_dates['end_month'], accumulation_dates['end_year'] = (None, 0, 0, 0)
        contents_dates = {}
        try:
            contents_dates['date_range'] = details.find(text=re.compile("Contents dates")).parent.parent.findNextSiblings('td')[0].string
        except AttributeError:
            pass
        else:
            contents_date_parsed = utilities.process_date(contents_dates['date_range'])
            contents_dates['start_date'], contents_dates['start_day'], contents_dates['start_month'], contents_dates['start_year'] = contents_date_parsed[0]
            if len(contents_date_parsed) == 2:
                contents_dates['end_date'], contents_dates['end_day'], contents_dates['end_month'], contents_dates['end_year'] = contents_date_parsed[1]
            else:
                contents_dates['end_date'], contents_dates['end_day'], contents_dates['end_month'], contents_dates['end_year'] = (None, 0, 0, 0)
        agencies = []
        for agency in details.find(text=re.compile("recording")).parent.findNextSiblings('td')[0].findAll('li'):
            date_range = agency.find('div', 'dates').string
            agency_id = agency.find('div', 'linkagesInfo').a.string
            agency_name = agency.find('div', 'linkagesInfo').contents[1].string[2:]
            agencies.append({'agency_dates': date_range, 'agency_id': agency_id, 'agency_name': agency_name})
        quantity_location = []
        for q_loc in details.find(text=re.compile("Quantity and location")).parent.findNextSiblings('td')[0].findAll('li'):
            try:
                quantity, location = re.search(r'(\d+\.*\d*) metres held in ([A-Z,a-z]+)', q_loc.string).groups()
                quantity = float(quantity)
            except AttributeError:
                quantity = None
                location = None
            quantity_location.append({'string': q_loc.string, 'quantity': quantity, 'location': location})
        items = soup.find(text="Items in this series on RecordSearch").parent.parent.findNextSiblings()[0].a.string
        self.results = {'identifier': identifier,
                        'title': title,
                        'accumulation_dates': accumulation_dates,
                        'contents_dates': contents_dates,
                        'items_described': items,
                        'recording_agencies': agencies,
                        'quantity_location': quantity_location}
        
    def get_advanced_items_search(self):
        '''
        Opens up the items advanced search form.
        Form fields can then be filled using self.br.form.
        '''
        url = 'http://recordsearch.naa.gov.au/scripts/Logon.asp?N=guest'
        self.get_page(url)
        self.br.open('http://recordsearch.naa.gov.au/SearchNRetrieve/Interface/SearchScreens/AdvSearchItems.aspx')
        self.br.select_form(name="aspnetForm")
    
    def search_items(self, q=None, series=None, control_symbol=None):
        '''
        Retrieves basic item information from a search.
        Results stored in self.results.
        '''
        self.get_advanced_items_search()
        if q:
            self.br.form['ctl00$ContentPlaceHolderSNRMain$txbKeywords'] = q
        if series:
            self.br.form['ctl00$ContentPlaceHolderSNRMain$txbSerNo'] = series
        if control_symbol:
            self.br.form['ctl00$ContentPlaceHolderSNRMain$txbIteControlSymb'] = control_symbol
        self.br.submit()
        self.br.select_form(nr=0)
        self.br.submit()
        #sort by barcode
        self.response = self.br.open('http://recordsearch.naa.gov.au/SearchNRetrieve/Interface/ListingReports/ItemsListing.aspx?sort=9')
        self.extract_items()
    
    def get_search_page_number(self, page):
        self.response = self.br.open('http://recordsearch.naa.gov.au/SearchNRetrieve/Interface/ListingReports/ItemsListing.aspx?page=%s' % page)
        self.extract_items()
    
    def get_items(self, series_id):
        url = 'http://www.naa.gov.au/cgi-bin/Search?Number=%s' % series_id
        self.get_page(url)
        self.br.follow_link(url_regex=r'ItemSearch_Result\.aspx')
        self.response = self.br.open('http://recordsearch.naa.gov.au/SearchNRetrieve/Interface/ListingReports/ItemsListing.aspx?sort=9')
        #self.get_total_results()
        #self.get_page(url)
        #self.response = self.br.open(url)
        self.extract_items()
        
    def extract_items(self):
        results = []
        soup = BeautifulSoup(self.response.read())
        if not self.total_results:
            self.get_total_results(soup)
        try:
            rows = soup.find('table', 'SearchResults').findAll('tr')[1:]
        except AttributeError:
            pass
        else:
            for row in rows:
                result = {}
                result['series'] = row.findAll('td')[1].string.strip()
                result['control_symbol'] = row.findAll('td')[2].a.string.strip()
                result['title'] = row.findAll('td')[3].contents[0].strip()
                result['access'] = row.findAll('td')[3].find('div', 'CombinedTitleBottomLeft').string.strip()[15:]
                result['location'] = row.findAll('td')[3].find('div', 'CombinedTitleBottomRight').string.strip()[10:]
                result['dates'] = row.findAll('td')[4].string.strip()
                result['barcode'] = row.findAll('td')[6].string.strip()
                if row.find('td', attrs={'title': 'View digital copy'}):
                    result['digitised'] = 'yes'
                    result['pages'] = self.get_page_total(result['barcode'])
                else:
                    result['digitised'] = 'no'
                    result['pages'] = 'unknown'
                results.append(result)
            self.results = results
            
if __name__ == "__main__":
    ''' Example: perform search for documents by discipline and retrieve word counts for each'''
    rs = RSClient()
    #reference = rs.get_reference('3445411')
    #print reference
    #pages = rs.get_page_total('3445411')
    #print '%s, %s' % (reference['series'], reference['item'])
    #print 'Digitised?: %s' % reference['digitised']
    #print '%s pages' % pages
    series = rs.get_series_summary('B13')
    #print series
    #rs.get_items('E752')
    #rs.search_items(control_symbol='kelly a*', series='B2455')
    print rs.results
    #rs.get_total_results()
    print rs.total_results