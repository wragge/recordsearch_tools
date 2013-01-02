'''
Created on 16/02/2011

@author: tim
'''
import re
from urllib import quote_plus
from bs4 import BeautifulSoup
import mechanize
#import logging

import utilities
from utilities import retry

#logger = logging.getLogger("mechanize")
#logger.addHandler(logging.StreamHandler(sys.stdout))
#logger.setLevel(logging.DEBUG)


RS_URLS = {
        'item': 'http://www.naa.gov.au/cgi-bin/Search?O=I&Number=',
        'series': 'http://www.naa.gov.au/cgi-bin/Search?Number=',
        'agency': 'http://www.naa.gov.au/cgi-bin/Search?Number=',
    }


class UsageError(Exception):
    pass


class ServerError(Exception):
    pass


class RSClient:

    def _create_browser(self):
        self.br = mechanize.Browser()
        self.br.addheaders = [('User-agent',
            'Mozilla/5.0 (Windows; U; Windows NT 6.0; en-US; rv:1.9.0.6')]
        self.br.set_handle_robots(False)

    @retry(ServerError, tries=10, delay=1)
    def _get_url(self, url):
        try:
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
            return response2
        except mechanize.HTTPError as e:
            print e.code
            if e.code == 503 or e.code == 504:
                raise ServerError("Server didn't respond")
            else:
                raise

    def _get_details(self, entity_id):
        '''
        Given an id retrieve the element containing the item details.
        '''
        if (not entity_id and self.entity_id) or (entity_id == self.entity_id):
            details = self.details
        else:
            url = '{}{}'.format(RS_URLS[self.entity_type], quote_plus(entity_id))
            response = self._get_url(url)
            soup = BeautifulSoup(response.read())
            details = soup.find('div', 'detailsTable')
            if details:
                self.entity_id = entity_id
                self.details = details
            else:
                raise UsageError('No details found for {}'.format(id))
        return details

    def _get_cell(self, label, entity_id):
        details = self._get_details(entity_id)
        try:
            cell = (
                        details.find(text=re.compile(label))
                        .parent.parent.findNextSiblings('td')[0]
                    )
        except (IndexError, AttributeError):
            # Sometimes the cell labels are inside an enclosing div,
            # but sometimes not. Try again assuming no div.
            try:
                cell = (
                        details.find(text=re.compile(label))
                        .parent.findNextSiblings('td')[0]
                    )
            except (IndexError, AttributeError):
                cell = None
        return cell

    def _get_value(self, label, entity_id):
        cell = self._get_cell(label, entity_id)
        try:
            value = ' '.join([string for string in cell.stripped_strings])
        except AttributeError:
            value = None
        return value

    def _get_formatted_dates(self, label, entity_id):
        try:
            date_str = self._get_value(label, entity_id)
        except AttributeError:
            start_date = None
            end_date = None
        else:
            date_dicts = utilities.process_date_string(date_str)
            #start_date = utilities.convert_date_to_iso(date_dicts[0])
            start_date = date_dicts[0]
            try:
                #end_date = utilities.convert_date_to_iso(date_dicts[1])
                end_date = date_dicts[1]
            except IndexError:
                end_date = None
        return {
                'date_str': date_str,
                'start_date': start_date,
                'end_date': end_date
                }

    def _get_relations(self, label, entity_id):
        cell = self._get_cell(label, entity_id)
        relations = []
        if cell is not None:
            for relation in cell.findAll('li'):
                try:
                    date_str = relation.find('div', 'dates').string
                except AttributeError:
                    start_date = None
                    end_date = None
                else:
                    date_dicts = utilities.process_date_string(date_str)
                    # start_date = utilities.convert_date_to_iso(date_dicts[0])
                    start_date = date_dicts[0]
                    try:
                        #end_date = utilities.convert_date_to_iso(date_dicts[1])
                        end_date = date_dicts[1]
                    except IndexError:
                        end_date = None
                details = [string for string in relation.find('div', 'linkagesInfo').stripped_strings]
                try:
                    identifier = details[0]
                    title = details[1][2:]
                except IndexError:
                    identifier = details[0]
                    title = details[0]
                relations.append({
                                    'date_str': date_str.strip(),
                                    'start_date': start_date,
                                    'end_date': end_date,
                                    'identifier': identifier,
                                    'title': title
                                }
                            )
        else:
            relations = None
        return relations

    def _get_advanced_items_search(self):
        '''
        Opens up the items advanced search form.
        Form fields can then be filled using self.br.form.
        '''
        url = 'http://recordsearch.naa.gov.au/scripts/Logon.asp?N=guest'
        self._get_url(url)
        self.br.open('http://recordsearch.naa.gov.au/SearchNRetrieve/Interface/SearchScreens/AdvSearchItems.aspx')
        self.br.select_form(name="aspnetForm")


class RSItemClient(RSClient):

    def __init__(self):
        self._create_browser()
        self.entity_type = 'item'
        self.entity_id = None
        self.details = None
        self.digitised = None

    def get_summary(self, entity_id=None):
        title = self.get_title(entity_id)
        control_symbol = self.get_control_symbol(entity_id)
        series = self.get_series(entity_id)
        identifier = self.get_identifier(entity_id)
        contents_dates = self.get_contents_dates(entity_id)
        digitised_status = self.get_digitised_status(entity_id)
        digitised_pages = self.get_digitised_pages(entity_id)
        access_status = self.get_access_status(entity_id)
        location = self.get_location(entity_id)

        return {
                'title': title,
                'identifer': identifier,
                'series': series,
                'control_symbol': control_symbol,
                'contents_dates': contents_dates,
                'digitised_status': digitised_status,
                'digitised_pages': digitised_pages,
                'access_status': access_status,
                'location': location
            }

    def get_title(self, entity_id=None):
        return self._get_value('Title', entity_id)

    def get_control_symbol(self, entity_id=None):
        return self._get_value('Control symbol', entity_id)

    def get_series(self, entity_id=None):
        cell = self._get_cell('Series number', entity_id)
        return cell.find('a').string.strip()

    def get_identifier(self, entity_id=None):
        return self._get_value('Item barcode', entity_id)

    def get_location(self, entity_id=None):
        return self._get_value('Location', entity_id)

    def get_access_status(self, entity_id=None):
        return self._get_value('Access status', entity_id)

    def get_digitised_status(self, entity_id=None):
        if self.digitised == None:
            self._get_details(entity_id)
        return self.digitised

    def get_contents_dates(self, entity_id=None):
        return self._get_formatted_dates('Contents date range', entity_id)

    def get_digitised_pages(self, entity_id=None):
        '''
        Returns the number of pages (images) in a digitised file.
        Note that you don't need a session id to access these pages,
        so there's no need to go through get_url().
        '''
        url = 'http://recordsearch.naa.gov.au/scripts/Imagine.asp?B=%s&I=1&SE=1' % entity_id
        response = self.br.open(url)
        soup = BeautifulSoup(response.read())
        try:
            pages = soup.find('input', attrs={'id': "Hidden3"})['value']
        except TypeError:
            pages = '0'
        return pages

    def _get_details(self, entity_id):
        '''
        Given an id retrieve the element containing the item details.
        Overwriting RSClient method to check if file is digitised.
        '''
        if (not entity_id and self.entity_id) or (entity_id == self.entity_id):
            details = self.details
        else:
            url = '{}{}'.format(RS_URLS[self.entity_type], entity_id)
            response = self._get_url(url)
            soup = BeautifulSoup(response.read())
            details = soup.find('div', 'detailsTable')
            if details:
                self.entity_id = entity_id
                self.details = details
                self.digitised = self._is_digitised(soup)
            else:
                raise UsageError('No details found for {}'.format(id))
        return details

    def _is_digitised(self, soup):
        if soup.find(text=re.compile("View digital copy")):
            digitised = True
        else:
            digitised = False
        return digitised

    def search_items(self, q=None, series=None, control_symbol=None):
        '''
        Retrieves basic item information from a search.
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
        response = self.br.open('http://recordsearch.naa.gov.au/SearchNRetrieve/Interface/ListingReports/ItemsListing.aspx?sort=9')
        return response

    def get_total_results(self, soup):
        element_id = 'ctl00_ContentPlaceHolderSNRMain_lblDisplaying'
        total = re.search(
                            r'of (\d+)',
                            soup.find('span', attrs={'id': element_id}).string
                        ).group(1)
        #total = soup.find('p').string
        return total


class RSSeriesClient(RSClient):

    def __init__(self):
        self._create_browser()
        self.entity_type = 'series'
        self.entity_id = None
        self.details = None

    def get_summary(self, entity_id=None):
        title = self.get_title(entity_id)
        contents_dates = self.get_contents_dates(entity_id)
        items_described = self.get_number_described(entity_id)
        items_digitised = self.get_number_digitised(entity_id)
        recording_agencies = self.get_recording_agencies(entity_id)
        locations = self.get_quantity_location(entity_id)
        return {'identifier': entity_id,
                'title': title,
                'contents_dates': contents_dates,
                'items_described': items_described,
                'items_digitised': items_digitised,
                'recording_agencies': recording_agencies,
                'locations': locations}

    def get_identifier(self, entity_id=None):
        return self._get_value('Series number', entity_id)

    def get_title(self, entity_id=None):
        return self._get_value('Title', entity_id)

    def get_accumulation_dates(self, entity_id=None):
        return self._get_formatted_dates('Accumulation dates', entity_id)

    def get_contents_dates(self, entity_id=None):
        return self._get_formatted_dates('Contents dates', entity_id)

    def get_number_described(self, entity_id=None):
        described = self._get_value('Items in this series on RecordSearch', entity_id)
        described_number, described_note = re.search(r'(\d+)(.*)', described).groups()
        return {'described_number': described_number, 'described_note': described_note.strip()}

    def get_recording_agencies(self, entity_id=None):
        return self._get_relations('recording', entity_id)

    def get_controlling_agencies(self, entity_id=None):
        return self._get_relations('controlling', entity_id)

    def get_quantity_location(self, entity_id=None):
        cell = self._get_cell('Quantity and location', entity_id)
        locations = []
        for location in cell.findAll('li'):
            try:
                quantity, location = re.search(r'(\d+\.*\d*) metres held in ([A-Z,a-z]+)', location.string).groups()
                quantity = float(quantity)
            except AttributeError:
                quantity = None
                location = None
            locations.append({
                                'quantity': quantity,
                                'location': location
                            })
        return locations

    def get_previous_series(self, entity_id=None):
        return self._get_relations('Previous series', entity_id)

    def get_subsequent_series(self, entity_id=None):
        return self._get_relations('Subsequent series', entity_id)

    def get_controlling_series(self, entity_id=None):
        return self._get_relations('Controlling series', entity_id)

    def get_related_series(self, entity_id=None):
        return self._get_relations('Related series', entity_id)

    def get_number_digitised(self, entity_id=None):
        '''
        Get the number of digitised files in a series.
        '''
        self._get_advanced_items_search()
        self.br.form['ctl00$ContentPlaceHolderSNRMain$txbSerNo'] = entity_id
        self.br.form.find_control('ctl00$ContentPlaceHolderSNRMain$cbxDigitalCopies').items[0].selected = True
        self.br.submit()
        self.br.select_form(nr=0)
        response = self.br.submit()
        soup = BeautifulSoup(response.read())
        try:
            displaying = soup.find('span', attrs={'id': 'ctl00_ContentPlaceHolderSNRMain_lblDisplaying'}).string
        except AttributeError:
            # Element not found
            # If more than 20000 results, RecordSearch gives you a warning.
            if soup.find('span', attrs={'id': 'ctl00_ContentPlaceHolderSNRMain_lblToManyRecordsError'}):
                digitised = '20000+'
            else:
                digitised = None
        else:
            try:
                digitised = re.search('Displaying \d+ to \d+ of (\d+)', displaying).group(1)
            except AttributeError:
                # Pattern not found
                digitised = None
        return digitised


class RSAgencyClient(RSClient):

    def __init__(self):
        self._create_browser()
        self.entity_type = 'agency'
        self.entity_id = None
        self.details = None

    def get_summary(self, entity_id=None):
        title = self.get_title(entity_id)
        return {
                    'title': title
            }

    def get_identifier(self, entity_id=None):
        return self._get_value('Agency number', entity_id)

    def get_title(self, entity_id=None):
        return self._get_value('Title', entity_id)

    def get_institution_title(self, entity_id=None):
        return self._get_value('Institution title', entity_id)

    def get_dates(self, entity_id=None):
        return self._get_formatted_dates('Date range', entity_id)

    def get_functions(self, entity_id=None):
        return self._get_relations('Function', entity_id)

    def get_previous_agencies(self, entity_id=None):
        return self._get_relations('Previous agency', entity_id)

    def get_subsequent_agencies(self, entity_id=None):
        return self._get_relations('Subsequent agency', entity_id)

    def get_superior_agencies(self, entity_id=None):
        return self._get_relations('Superior agency', entity_id)

    def get_controlled_agencies(self, entity_id=None):
        return self._get_relations('Previous agency', entity_id)

    def get_associated_people(self, entity_id=None):
        return self._get_relations('Persons associated', entity_id)


if __name__ == "__main__":
    ''' Example: perform search for documents by discipline and retrieve word counts for each'''
    rs = RSClient()
    #reference = rs.get_reference('3445411')
    #print reference
    #pages = rs.get_page_total('3445411')
    #print '%s, %s' % (reference['series'], reference['item'])
    #print 'Digitised?: %s' % reference['digitised']
    #print '%s pages' % pages
    #series = rs.get_series_summary('B13')
    #print series
    rs.get_number_digitised('B13')
    #rs.get_items('E752')
    #rs.search_items(control_symbol='kelly a*', series='B2455')
    #print rs.results
    #rs.get_total_results()
    #print rs.total_results
