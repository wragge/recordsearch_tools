import re
from urllib import quote_plus
from robobrowser import RoboBrowser
from werkzeug.exceptions import BadRequestKeyError
import utilities
import time
# from utilities import retry

RS_URLS = {
    'item': 'http://www.naa.gov.au/cgi-bin/Search?O=I&Number=',
    'series': 'http://www.naa.gov.au/cgi-bin/Search?Number=',
    'agency': 'http://www.naa.gov.au/cgi-bin/Search?Number=',
    'search_results': 'http://recordsearch.naa.gov.au/SearchNRetrieve/Interface/ListingReports/ItemsListing.aspx',
    'ns_results': 'http://recordsearch.naa.gov.au/NameSearch/Interface/ItemsListing.aspx',
    'agency_results': 'http://recordsearch.naa.gov.au/SearchNRetrieve/Interface/ListingReports/AgencyListing.aspx'
}

ITEM_FORM = {
    'kw': {
        'id': 'ctl00$ContentPlaceHolderSNR$txbKeywords',
        'type': 'input',
    },
    'kw_options': {
        'id': 'ctl00$ContentPlaceHolderSNR$ddlUsingKeywords',
        'type': 'select'
    },
    'kw_exclude': {
        'id': 'ctl00$ContentPlaceHolderSNR$txbExKeywords',
        'type': 'input'
    },
    'kw_exclude_options': {
        'id': 'ctl00$ContentPlaceHolderSNR$ddlUsingExKwd',
        'type': 'select'
    },
    # Set to 'on' to search in item notes
    # It's a checkbox, but uses Javascript to set text value.
    # Pretend it's a select for validation purposes.
    'search_notes': {
        'id': 'ctl00$ContentPlaceHolderSNR$cbxKwdTitleNotes',
        'type': 'select'
    },
    'series': {
        'id': 'ctl00$ContentPlaceHolderSNR$txbSerNo',
        'type': 'input'
    },
    'series_exclude': {
        'id': 'ctl00$ContentPlaceHolderSNR$txbExSerNo',
        'type': 'input'
    },
    'control': {
        'id': 'ctl00$ContentPlaceHolderSNR$txbIteControlSymb',
        'type': 'input'
    },
    'control_exclude': {
        'id': 'ctl00$ContentPlaceHolderSNR$txbExIteControlSymb',
        'type': 'input'
    },
    'barcode': {
        'id': 'ctl00$ContentPlaceHolderSNR$txbIteBarcode',
        'type': 'input'
    },
    'date_from': {
        'id': 'ctl00$ContentPlaceHolderSNR$txbDateFrom',
        'type': 'input'
    },
    'date_to': {
        'id': 'ctl00$ContentPlaceHolderSNR$txbDateTo',
        'type': 'input'
    },
    # Select lists (options below)
    'formats': {
        'id': 'ctl00$ContentPlaceHolderSNR$ddlPhysFormat',
        'type': 'select'
    },
    'formats_exclude': {
        'id': 'ctl00$ContentPlaceHolderSNR$ddlExPhysFormat',
        'type': 'select'
    },
    'locations': {
        'id': 'ctl00$ContentPlaceHolderSNR$ddlLocation',
        'type': 'select'
    },
    'locations_exclude': {
        'id': 'ctl00$ContentPlaceHolderSNR$ddlExLocation',
        'type': 'select'
    },
    'access': {
        'id': 'ctl00$ContentPlaceHolderSNR$ddlAccessStatus',
        'type': 'select'
    },
    'access_exclude': {
        'id': 'ctl00$ContentPlaceHolderSNR$ddlExAccessStatus',
        'type': 'select'
    },
    # Checkbox
    'digital': {
        'id': 'ctl00$ContentPlaceHolderSNR$cbxDigitalCopies',
        'type': 'checkbox'
    }
}

KW_OPTIONS = [
    'ALL',
    'ANY',
    'EXACT'
]

FORMATS = [
    'Paper files and documents',
    'Index cards',
    'Bound volumes',
    'Cartographic records',
    'Photographs',
    'Microforms',
    'Audio-visual records',
    'Audio records',
    'Electronic records',
    '3-dimensional records',
    'Scientific specimens',
    'Textiles'
]

LOCATIONS = [
    'NAT,ACT',
    'Adelaide',
    'Australian War Memorial',
    'Brisbane',
    'Darwin',
    'Hobart',
    'Melbourne',
    'Perth',
    'Sydney'
]

ACCESS = [
    'OPEN',
    'OWE',
    'CLOSED',
    'NYE'
]

NS_CATEGORIES = {
    "2": "Australian Defence Forces personnel records",
    "3": "Army personnel records",
    "4": "Boer War",
    "5": "World War I",
    "6": "World War II",
    "7": "Pre WWI, Inter war, post WWII",
    "8": "Air Force personnel records",
    "9": "Navy personnel records",
    "10": "Other defence records",
    "11": "Service pay records",
    "12": "RAAF accident reports",
    "13": "Australian Prisoners of War records",
    "14": "Court martial records",
    "15": "Repatriation cases (Boer War &amp; WWI)",
    "16": "War gratuity records",
    "17": "Civilian service records",
    "18": "Army Inventions Directorate",
    "19": "Papua New Guinea evacuees records",
    "20": "Immigration and naturalisation records",
    "21": "Other records",
    "22": "Security and intelligence records",
    "23": "Arts and science records",
    "24": "Australian Broadcasting Commission",
    "25": "Commonwealth Literary Fund",
    "26": "Copyright, patents, trademarks",
    "27": "High Court cases"
}

AGENCY_FORM = {
    'kw': {
        'id': 'ctl00_ContentPlaceHolderSNR_txbKeywords',
        'type': 'input'
    },
    'kw_options': {
        'id': 'ctl00_ContentPlaceHolderSNR_ddlUsingKeywords',
        'type': 'select'
    },
    'kw_exclude': {
        'id': 'ctl00_ContentPlaceHolderSNR_txbExcludeKeywords',
        'type': 'input'
    },
    'kw_exclude_options': {
        'id': 'ctl00_ContentPlaceHolderSNR_ddlExcludeUsingKeywords',
        'type': 'select'
    },
    'function': {
        'id': 'ctl00$ContentPlaceHolderSNR$txtFunctions',
        'type': 'input'
    }
}

SERIES_FORM = {
    'kw': {
        'id': 'ctl00$ContentPlaceHolderSNR$txbKeywords',
        'type': 'input'
    },
    'series_id': {
        'id': 'ctl00$ContentPlaceHolderSNR$txbSerNo',
        'type': 'input'
    },
    'agency_recording': {
        'id': 'ctl00$ContentPlaceHolderSNR$txbAgencyRecording',
        'type': 'input'
    },
    'agency_controlling': {
        'id': 'ctl00$ContentPlaceHolderSNR$txbAgencyControlling',
        'type': 'input'
    },
    'date_from': {
        'id': 'ctl00$ContentPlaceHolderSNR$txbDateFrom',
        'type': 'input'
    },
    'date_to': {
        'id': 'ctl00$ContentPlaceHolderSNR$txbDateTo',
        'type': 'input'
    }
}


class UsageError(Exception):
    pass


class ServerError(Exception):
    pass


class TooManyError(Exception):
    pass


class RSClient():

    def __init__(self):
        self._create_browser()

    def _create_browser(self):
        url = 'http://recordsearch.naa.gov.au/scripts/Logon.asp?N=guest'
        self.br = RoboBrowser(parser='lxml', user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/43.0.2357.81 Safari/537.36', history=False)
        self.br.open(url)
        form = self.br.get_form(id='t')
        self.br.submit_form(form)

    def _open_url(self, url):
        '''
        RecordSearch inserts a page that needs to have an embedded form
        automatically submitted before you get what you actually want.
        '''
        self.br.open(url)
        form = self.br.get_form(id='t')
        self.br.submit_form(form)

    def _get_details(self, entity_id):
        '''
        Given an id retrieve the element containing the item details.
        '''
        if (not entity_id and self.entity_id) or (entity_id == self.entity_id):
            details = self.details
        else:
            url = '{}{}'.format(RS_URLS[self.entity_type], quote_plus(entity_id))
            self._open_url(url)
            details = self.br.find('div', 'detailsTable')
            if details:
                self.entity_id = entity_id
                self.details = details
            else:
                raise UsageError('No details found for {}'.format(entity_id))
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
            cell.decompose()
        except AttributeError:
            value = None
        return value

    def _get_formatted_dates(self, label, entity_id, date_format):
        try:
            date_str = self._get_value(label, entity_id)
        except AttributeError:
            dates = {'date_str': date_str, 'start_date': None, 'end_date': None}
        else:
            if date_str:
                dates = utilities.process_date_string(date_str)
                if date_format == 'iso':
                    formatted_dates = {
                        'date_str': date_str,
                        'start_date': utilities.convert_date_to_iso(dates['start_date']),
                        'end_date': utilities.convert_date_to_iso(dates['end_date']),
                    }
                elif date_format == 'obj':
                    formatted_dates = dates
            else:
                formatted_dates = {'date_str': None, 'start_date': None, 'end_date': None}
        return formatted_dates

    def _get_relations(self, label, entity_id, date_format):
        cell = self._get_cell(label, entity_id)
        relations = []
        if cell is not None:
            for relation in cell.findAll('li'):
                try:
                    date_str = relation.find('div', 'dates').string.strip()
                except AttributeError:
                    date_str = ''
                    dates = {'date_str': '', 'start_date': None, 'end_date': None}
                else:
                    dates = utilities.process_date_string(date_str)
                if date_format == 'iso':
                    formatted_dates = {
                        'date_str': date_str,
                        'start_date': utilities.convert_date_to_iso(dates['start_date']),
                        'end_date': utilities.convert_date_to_iso(dates['end_date']),
                    }
                elif date_format == 'obj':
                    formatted_dates = dates
                details = [string for string in relation.find('div', 'linkagesInfo').stripped_strings]
                try:
                    identifier = details[0]
                    title = details[1][2:]
                except IndexError:
                    identifier = details[0]
                    title = details[0]
                relations.append({
                    'date_str': formatted_dates['date_str'],
                    'start_date': formatted_dates['start_date'],
                    'end_date': formatted_dates['end_date'],
                    'identifier': identifier,
                    'title': title
                })
                relation.decompose()
            cell.decompose()
        else:
            relations = None
        return relations

    def get_digitised_pages(self, entity_id=None):
        '''
        Returns the number of pages (images) in a digitised file.
        Note that you don't need a session id to access these pages,
        so there's no need to go through get_url().
        '''
        # url = 'http://recordsearch.naa.gov.au/scripts/Imagine.asp?B={}&I=1&SE=1'.format(entity_id)
        url = 'http://recordsearch.naa.gov.au/SearchNRetrieve/Interface/ViewImage.aspx?B={}'.format(entity_id)
        br = RoboBrowser(parser='lxml')
        br.open(url)
        try:
            pages = int(br.find('span', attrs={'id': "lblEndPage"}).string)
        except AttributeError:
            pages = 0
        return pages

    def _get_advanced_search_form(self):
        # Added header 10 June 2015 -- otherwise causes error
        self.br.session.headers.update({'Referer': 'http://recordsearch.naa.gov.au/SearchNRetrieve/Interface/SearchScreens/BasicSearch.aspx'})
        self.br.open('http://recordsearch.naa.gov.au/SearchNRetrieve/Interface/SearchScreens/AdvSearchItems.aspx')
        search_form = self.br.get_form(id="formSNRMaster")
        return search_form


class RSItemClient(RSClient):

    def __init__(self):
        self._create_browser()
        self.entity_type = 'item'
        self.entity_id = None
        self.details = None
        self.digitised = None

    def get_summary(self, entity_id=None, date_format='obj'):
        title = self.get_title(entity_id)
        control_symbol = self.get_control_symbol(entity_id)
        series = self.get_series(entity_id)
        identifier = self.get_identifier(entity_id)
        contents_dates = self.get_contents_dates(entity_id, date_format)
        digitised_status = self.get_digitised_status(entity_id)
        digitised_pages = self.get_digitised_pages(entity_id)
        access_status = self.get_access_status(entity_id)
        access_reason = self.get_access_reason(entity_id)
        access_decision = self.get_access_decision(entity_id, date_format)
        location = self.get_location(entity_id)

        return {
            'title': title,
            'identifier': identifier,
            'series': series,
            'control_symbol': control_symbol,
            'contents_dates': contents_dates,
            'digitised_status': digitised_status,
            'digitised_pages': digitised_pages,
            'access_status': access_status,
            'access_reason': access_reason,
            'access_decision': access_decision,
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

    def get_access_reason(self, entity_id=None):
        cell = self._get_cell('Reason for restriction', entity_id)
        reasons = []
        if cell:
            for link in cell.find_all('a'):
                reason = link.string.strip()
                # 9 October 2016 -- noticed the links on reasons now go to glossary
                # text = re.search(r'openWin\((.*)\)', link['onclick']).group(1)
                # note = text.split(',')[0].strip("'").replace(reason, '', 1).strip()
                note = ""
                reasons.append({'reason': reason, 'note': note})
        return reasons

    def get_access_decision(self, entity_id=None, date_format='iso'):
        return self._get_formatted_dates('Date of decision', entity_id, date_format)

    def get_digitised_status(self, entity_id=None):
        if self.digitised is None:
            self._get_details(entity_id)
        return self.digitised

    def get_contents_dates(self, entity_id=None, date_format='iso'):
        return self._get_formatted_dates('Contents date range', entity_id, date_format)

    def _get_details(self, entity_id):
        '''
        Given an id retrieve the element containing the item details.
        Overwriting RSClient method to check if file is digitised.
        '''
        if (not entity_id and self.entity_id) or (entity_id == self.entity_id):
            details = self.details
        else:
            url = '{}{}'.format(RS_URLS[self.entity_type], entity_id)
            self._open_url(url)
            details = self.br.find('div', class_='detailsTable')
            if details:
                self.entity_id = entity_id
                self.details = details
                self.digitised = self._is_digitised()
            else:
                raise UsageError('No details found for {}'.format(entity_id))
        return details

    def _is_digitised(self):
        if self.br.find(text=re.compile("View digital copy")):
            digitised = True
        else:
            digitised = False
        return digitised


class RSSeriesClient(RSClient):

    def __init__(self):
        self._create_browser()
        self.entity_type = 'series'
        self.entity_id = None
        self.details = None

    def get_summary(self, entity_id=None, date_format='obj'):
        title = self.get_title(entity_id)
        contents_dates = self.get_contents_dates(entity_id, date_format)
        accumulation_dates = self.get_accumulation_dates(entity_id, date_format)
        recording_agencies = self.get_recording_agencies(entity_id, date_format)
        controlling_agencies = self.get_controlling_agencies(entity_id, date_format)
        locations = self.get_quantity_location(entity_id)
        items_described = self.get_number_described(entity_id)
        items_digitised = self.get_number_digitised(entity_id)
        access_status = self.get_access_status(entity_id)
        previous = self.get_previous_series(entity_id)
        subsequent = self.get_subsequent_series(entity_id)
        controlling = self.get_controlling_series(entity_id)
        related = self.get_related_series(entity_id)
        physical_format = self.get_format(entity_id)
        arrangement = self.get_arrangement(entity_id)
        control_symbols = self.get_control(entity_id)
        return {'identifier': entity_id,
                'title': title,
                'contents_dates': contents_dates,
                'accumulation_dates': accumulation_dates,
                'physical_format': physical_format,
                'arrangement': arrangement,
                'control_symbols': control_symbols,
                'items_described': items_described,
                'items_digitised': items_digitised,
                'recording_agencies': recording_agencies,
                'controlling_agencies': controlling_agencies,
                'locations': locations,
                'access_status': access_status,
                'previous_series': previous,
                'subsequent_series': subsequent,
                'controlling_series': controlling,
                'related_series': related
                }

    def get_identifier(self, entity_id=None):
        return self._get_value('Series number', entity_id)

    def get_title(self, entity_id=None):
        return self._get_value('Title', entity_id)

    def get_accumulation_dates(self, entity_id=None, date_format='obj'):
        return self._get_formatted_dates('Accumulation dates', entity_id, date_format)

    def get_contents_dates(self, entity_id=None, date_format='obj'):
        return self._get_formatted_dates('Contents dates', entity_id, date_format)

    def get_format(self, entity_id=None):
        return self._get_value('Predominant physical format', entity_id)

    def get_arrangement(self, entity_id=None):
        return self._get_value('System of arrangement/ control', entity_id)

    def get_control(self, entity_id=None):
        return self._get_value('Range of control symbols', entity_id)

    def get_number_described(self, entity_id=None):
        described = self._get_value('Items in this series on RecordSearch', entity_id)
        try:
            described_number, described_note = re.search(r'(\d+)(.*)', described).groups()
            try:
                described_number = int(described_number)
            except ValueError:
                pass
        except AttributeError:
            described_number = 0
            described_note = described
        except TypeError:
            described_number = 0
            described_note = ''
        return {'described_number': described_number, 'described_note': described_note.strip()}

    def get_recording_agencies(self, entity_id=None, date_format='obj'):
        return self._get_relations('recording', entity_id, date_format)

    def get_controlling_agencies(self, entity_id=None, date_format='obj'):
        return self._get_relations('controlling', entity_id, date_format)

    def get_quantity_location(self, entity_id=None):
        cell = self._get_cell('Quantity and location', entity_id)
        locations = []
        if cell:
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

    def get_previous_series(self, entity_id=None, date_format='obj'):
        return self._get_relations('Previous series', entity_id, date_format)

    def get_subsequent_series(self, entity_id=None, date_format='obj'):
        return self._get_relations('Subsequent series', entity_id, date_format)

    def get_controlling_series(self, entity_id=None, date_format='obj'):
        return self._get_relations('Controlling series', entity_id, date_format)

    def get_related_series(self, entity_id=None, date_format='obj'):
        return self._get_relations('Related series', entity_id, date_format)

    def _get_number_results(self):
        displaying = self.br.find(string=re.compile(r'\d+\s+(?:to \d+ )?of\s+(\d+)', re.MULTILINE))
        if displaying:
            number = re.search(r'of\s+(\d+)', displaying, re.MULTILINE).group(1)
            try:
                number = int(number)
            except ValueError:
                pass
        # If more than 20000 results, RecordSearch gives you a warning.
        elif self.br.find('span', attrs={'id': 'ContentPlaceHolderSNR_lblToManyRecordsError'}):
            number = '20000+'
        elif self.br.find('span', attrs={'id': 'ContentPlaceHolderSNR_lblNoRecordsError'}):
            number = 0
        else:
            number = None
        return number

    def get_number_digitised(self, entity_id=None):
        '''
        Get the number of digitised files in a series.
        '''
        search_form = self._get_advanced_search_form()
        search_form['ctl00$ContentPlaceHolderSNR$txbSerNo'] = entity_id
        search_form['ctl00$ContentPlaceHolderSNR$cbxDigitalCopies'] = ['on']
        submit = search_form['ctl00$ContentPlaceHolderSNR$btnSearch']
        self.br.submit_form(search_form, submit=submit)
        running_form = self.br.get_form(id='Form1')
        self.br.submit_form(running_form)
        number = self._get_number_results()
        return number

    def get_access_status(self, entity_id=None):
        '''
        Get the number of files with each access status.
        '''
        access_status = {}
        for status in ACCESS:
            search_form = self._get_advanced_search_form()
            search_form['ctl00$ContentPlaceHolderSNR$txbSerNo'] = entity_id
            search_form['ctl00$ContentPlaceHolderSNR$ddlAccessStatus'] = status
            submit = search_form['ctl00$ContentPlaceHolderSNR$btnSearch']
            self.br.submit_form(search_form, submit=submit)
            running_form = self.br.get_form(id='Form1')
            self.br.submit_form(running_form)
            number = self._get_number_results()
            access_status[status] = number
            time.sleep(0.5)
        return access_status


class RSSeriesSearchClient(RSSeriesClient):

    # Only working with series, agency and date searches at the moment.

    def __init__(self):
        self._create_browser()
        self.entity_type = 'series'
        self.entity_id = None
        self.details = None
        self.total_results = None
        self.results_per_page = 20
        self.results = None
        self.page = 1
        self.entity_id = None

    def _get_series_search_form(self):
        url = 'http://recordsearch.naa.gov.au/SearchNRetrieve/Interface/SearchScreens/AdvSearchSeries.aspx'
        self.br.open(url)
        search_form = self.br.get_form(id="formSNRMaster")
        return search_form

    def search_series(self, page=None, results_per_page=None, sort=None, **kwargs):
        self._prepare_search(**kwargs)
        if page:
            self.br.open('http://recordsearch.naa.gov.au/SearchNRetrieve/Interface/ListingReports/SeriesListing.aspx?sort=1')
            self.br.open('http://recordsearch.naa.gov.au/SearchNRetrieve/Interface/ListingReports/SeriesListing.aspx?page={}'.format(int(page) - 1))
            self.page = page
        if results_per_page == 0:
            items = []
        else:
            items = self._process_page()
            self.results = items
        return {
            'total_results': self.total_results,
            'page': self.page,
            'results': items
        }

    def _prepare_search(self, **kwargs):
        search_form = self._get_series_search_form()
        for key, value in kwargs.items():
            search_form[SERIES_FORM[key]['id']].value = value
        submit = search_form['ctl00$ContentPlaceHolderSNR$btnSearch']
        self.br.submit_form(search_form, submit=submit)
        running_form = self.br.get_form(id='Form1')
        self.br.submit_form(running_form)
        self.total_results = self.get_total_results()

    def _process_page(self):
        items = []
        if self.br.find(id='ContentPlaceHolderSNR_tblSeriesDetails') is not None:
            results = self.br.find(
                'table',
                attrs={'id': 'ContentPlaceHolderSNR_tblSeriesDetails'}
            ).findAll('tr')[1:]
            items = []
            for row in results:
                item = {}
                cells = row.findAll('td')
                series_id = cells[1].a.string.strip()
                item = self.get_summary(entity_id=series_id)
                items.append(item)
        elif self.br.find(id='ContentPlaceHolderSNR_ucSeriesDetails_ctl01') is not None:
            items.append(self.get_summary())
        return items

    def get_total_results(self):
        total = None
        if self.br.find('span', attrs={'id': re.compile('lblDisplaying$')}) is not None:
            total_text = self.br.find('span', attrs={'id': re.compile('lblDisplaying$')}).text
            total = re.search(r'of (\d+)', total_text).group(1)
        elif self.br.find('span', text='Displaying'):
            total = '1'
        return total


class RSAgencyClient(RSClient):

    def __init__(self):
        self._create_browser()
        self.entity_type = 'agency'
        self.entity_id = None
        self.details = None

    def get_summary(self, entity_id=None, date_format='obj'):
        title = self.get_title(entity_id)
        dates = self.get_dates(entity_id)
        status = self.get_agency_status(entity_id)
        location = self.get_location(entity_id)
        functions = self.get_functions(entity_id)
        previous = self.get_previous_agencies(entity_id)
        subsequent = self.get_subsequent_agencies(entity_id)
        superior = self.get_superior_agencies(entity_id)
        controlled = self.get_controlled_agencies(entity_id)
        people = self.get_associated_people(entity_id)
        return {
            'agency_id': entity_id,
            'title': title,
            'dates': dates,
            'agency_status': status,
            'location': location,
            'functions': functions,
            'previous_agencies': previous,
            'subsequent_agencies': subsequent,
            'superior_agencies': superior,
            'controlled_agencies': controlled,
            'associated_people': people
        }

    def get_identifier(self, entity_id=None):
        return self._get_value('Agency number', entity_id)

    def get_title(self, entity_id=None):
        return self._get_value('Title', entity_id)

    def get_institution_title(self, entity_id=None):
        return self._get_value('Institution title', entity_id)

    def get_dates(self, entity_id=None, date_format='obj'):
        return self._get_formatted_dates('Date range', entity_id, date_format)

    def get_agency_status(self, entity_id=None):
        return self._get_value('Agency status', entity_id)

    def get_location(self, entity_id=None):
        return self._get_value('Location', entity_id)

    def get_functions(self, entity_id=None, date_format='obj'):
        return self._get_relations('Function', entity_id, date_format)

    def get_previous_agencies(self, entity_id=None, date_format='obj'):
        return self._get_relations('Previous agency', entity_id, date_format)

    def get_subsequent_agencies(self, entity_id=None, date_format='obj'):
        return self._get_relations('Subsequent agency', entity_id, date_format)

    def get_superior_agencies(self, entity_id=None, date_format='obj'):
        return self._get_relations('Superior agency', entity_id, date_format)

    def get_controlled_agencies(self, entity_id=None, date_format='obj'):
        return self._get_relations('Previous agency', entity_id, date_format)

    def get_associated_people(self, entity_id=None, date_format='obj'):
        return self._get_relations('Persons associated', entity_id, date_format)


class RSAgencySearchClient(RSAgencyClient):

    # Only working with function searches at the moment.

    def __init__(self):
        self._create_browser()
        self.entity_type = 'agency'
        self.entity_id = None
        self.details = None
        self.total_results = None
        self.results_per_page = 20
        self.results = None
        self.page = 1
        self.entity_id = None

    def _get_agency_search_form(self):
        url = 'http://recordsearch.naa.gov.au/SearchNRetrieve/Interface/SearchScreens/AdvSearchAgencies.aspx'
        self.br.open(url)
        search_form = self.br.get_form(id="formSNRMaster")
        return search_form

    def search_agencies(self, page=None, results_per_page=None, sort=None, **kwargs):
        self._prepare_search(**kwargs)
        if page:
            self.br.open('http://recordsearch.naa.gov.au/SearchNRetrieve/Interface/ListingReports/AgencyListing.aspx?sort=1')
            self.br.open('http://recordsearch.naa.gov.au/SearchNRetrieve/Interface/ListingReports/AgencyListing.aspx?page={}'.format(int(page) - 1))
            self.page = page
        if results_per_page == 0:
            items = []
        else:
            items = self._process_page()
            self.results = items
        return {
            'total_results': self.total_results,
            'page': self.page,
            'results': items
        }

    def _prepare_search(self, **kwargs):
        search_form = self._get_agency_search_form()
        for key, value in kwargs.items():
            search_form[AGENCY_FORM[key]['id']].value = value
        submit = search_form['ctl00$ContentPlaceHolderSNR$btnSearch']
        self.br.submit_form(search_form, submit=submit)
        running_form = self.br.get_form(id='Form1')
        self.br.submit_form(running_form)
        self.total_results = self.get_total_results()

    def _process_page(self):
        items = []
        if self.br.find(id='ctl00_ContentPlaceHolderSNR_ucAgencyListing_tblProvDetails') is not None:
            results = self.br.find(
                'table',
                attrs={'id': 'ctl00_ContentPlaceHolderSNR_ucAgencyListing_tblProvDetails'}
            ).findAll('tr')[1:]
            items = []
            for row in results:
                item = {}
                cells = row.findAll('td')
                agency_id = cells[1].a.string.strip()
                item = self.get_summary(entity_id=agency_id)
                items.append(item)
        elif self.br.find(id='ctl00_ContentPlaceHolderSNR_ucAgencyDetails_ctl01') is not None:
            items.append(self.get_summary())
        return items

    def get_total_results(self):
        total = None
        if self.br.find('span', attrs={'id': re.compile('lblDisplaying$')}) is not None:
            total_text = self.br.find('span', attrs={'id': re.compile('lblDisplaying$')}).text
            total = re.search(r'of (\d+)', total_text).group(1)
        elif self.br.find('span', text='Displaying'):
            total = '1'
        return total


class RSSearchClient(RSItemClient):

    def __init__(self):
        self._create_browser()
        self.total_results = None
        self.results = None
        self.page = 1
        self.results_per_page = 20
        self.entity_id = None
        self.digitised = None
        self.get_digitised = True

    def _get_name_search_form(self):
        url = 'http://recordsearch.naa.gov.au/Scripts/SessionManagement/SessionManager.asp?Module=NameSearch&Location=home'
        self._open_url(url)
        search_form = self.br.get_form(id="NameSearchForm")
        return search_form

    def search_names(self, page=None, results_per_page=None, sort=None, **kwargs):
        surname = kwargs.get('surname')
        category = kwargs.get('category', '5')
        other_names = kwargs.get('other_names', '')
        service_number = kwargs.get('service_number', '')
        search_form = self._get_name_search_form()
        search_form['txtFamilyName'].value = surname
        search_form['ddlCategory'].value = category
        submit = search_form['btnSearch']
        self.br.submit_form(search_form, submit=submit)
        running_form = self.br.get_form(attrs={'name': 'Form1'})
        self.br.submit_form(running_form)
        ns_form = self.br.get_form(id='NameSearchResultForm')
        if other_names or service_number:
            try:
                self.br.submit_form(ns_form, submit=ns_form['btnRefineSearch'])
            except BadRequestKeyError:
                pass
            else:
                # refine_form = self.br.get_form(id='RefineNameSearchForm2')
                refine_form = self.br.get_forms()[0]
                refine_form['txtGivenName'].value = other_names
                if category == '5' and service_number:
                    refine_form['txtServiceNumber'].value = service_number
                self.br.submit_form(refine_form, refine_form['btnSearch'])
                # Returns a 'search running' page, submit again to move on.
                running_form = self.br.get_form(attrs={'name': 'Form1'})
                self.br.submit_form(running_form)
                ns_form = self.br.get_form(id='NameSearchResultForm')
        try:
            self.br.submit_form(ns_form, submit=ns_form['btnDisplay'])
            self._get_html('ns_results', page, sort, results_per_page)
            items = self._process_page()
        except BadRequestKeyError:
            self.total_results = '0'
            self.results_per_page = results_per_page
            items = []
        return {
            'total_results': self.total_results,
            'page': self.page,
            'results_per_page': self.results_per_page,
            'results': items
        }

    def search(self, page=None, results_per_page=None, sort=None, digitised=True, **kwargs):
        self.get_digitised = digitised
        if kwargs:
            self._prepare_search(**kwargs)
            self._get_html('search_results', page, sort, results_per_page)
            items = self._process_page()
        elif self.results is not None:
            if not page and not results_per_page and not sort:
                items = self.results
            else:
                self._get_html('search_results', page, sort, results_per_page)
                try:
                    items = self._process_page()
                except:
                    raise
        self.results = items
        return {
            'total_results': self.total_results,
            'page': self.page,
            'results_per_page': self.results_per_page,
            'results': items
        }

    def _get_html(self, search_type, page, sort, results_per_page):
        '''
        Sort options:
            1 -- series and control symbol,
            3 -- title,
            5 -- start date,
            7 -- digitised images first,
            12 -- pdfs first,
            9 -- barcode,
            11 -- av first
        '''
        if results_per_page:
            form = self.br.get_form(id="formSNRMaster")
            form['ctl00$ContentPlaceHolderSNR$ddlResultsPerPage'].value = str(results_per_page)
            submit = form['ctl00$ContentPlaceHolderSNR$btnGo']
            self.br.submit_form(form, submit=submit)
            self.results_per_page = results_per_page
        if sort:
            self.br.open('{}?sort={}'.format(RS_URLS[search_type], sort))
        if page:
            self.br.open('{}?page={}'.format(RS_URLS[search_type], int(page) - 1))
            self.page = page

    def _prepare_search(self, **kwargs):
        search_form = self._get_advanced_search_form()
        for key, value in kwargs.items():
            search_form[ITEM_FORM[key]['id']].value = value
        submit = search_form['ctl00$ContentPlaceHolderSNR$btnSearch']
        self.br.submit_form(search_form, submit=submit)
        running_form = self.br.get_form(id='Form1')
        self.br.submit_form(running_form)

    def _process_page(self):
        # This will fail if there's only one result
        # Also if there's more than 20000 results
        if self.br.find(id='ctl00_ContentPlaceHolderSNR_lblToManyRecordsError') is not None:
            # Too many results
            raise TooManyError
        elif self.br.find(id=re.compile('tblItemDetails$')) is not None:
            items = self._process_list()
            self.total_results = self.get_total_results()
        elif self.br.find(id=re.compile('ContentPlaceHolderSNR_ucItemDetails_phDetailsView')) is not None:
            self.details = self.br.find('div', 'detailsTable')
            items = [self.get_summary()]
            self.total_results = 1
        else:
            items = []
            self.total_results = 0
        return items

    def _process_list(self):
        results = self.br.find(
            'table',
            attrs={'id': re.compile('tblItemDetails$')}
        ).findAll('tr')[1:]
        items = []
        for row in results:
            item = self._process_row(row)
            items.append(item)
        return items

    def _process_row(self, row):
        item = {}
        cells = row.findAll('td')
        item['series'] = cells[1].string.strip()
        item['control_symbol'] = cells[2].a.string.strip()
        item['title'] = cells[3].contents[0].string.strip()
        access_string = cells[3].find('div', 'CombinedTitleBottomLeft').string
        item['access_status'] = re.search(r'Access status: (\w+)', access_string).group(1)
        location_string = cells[3].find('div', 'CombinedTitleBottomRight').string
        item['location'] = re.search(r'Location: (\w+)', location_string).group(1)
        date_str = cells[4].string.strip()
        dates = utilities.process_date_string(date_str)
        date_range = {'date_str': date_str}
        date_range['start_date'] = utilities.convert_date_to_iso(dates['start_date'])
        date_range['end_date'] = utilities.convert_date_to_iso(dates['end_date'])
        item['contents_dates'] = date_range
        barcode = cells[7].string.strip()
        if cells[5].find('a') is not None:
            item['digitised_status'] = True
            if self.get_digitised:
                item['digitised_pages'] = self.get_digitised_pages(barcode)
        else:
            item['digitised_status'] = False
            if self.get_digitised:
                item['digitised_pages'] = 0
        item['identifier'] = barcode
        return item

    def get_total_results(self):
        total_text = self.br.find('span', attrs={'id': re.compile('lblDisplaying$')}).text
        total = re.search(r'of (\d+)', total_text).group(1)
        return total
