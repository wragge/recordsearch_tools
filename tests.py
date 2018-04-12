import unittest
import client
import utilities
import datetime


class TestSeriesFunctions(unittest.TestCase):

    def setUp(self):
        self.rs = client.RSSeriesClient()

    def test_get_identifier(self):
        identifier = self.rs.get_identifier('A1')
        self.assertEqual(identifier, 'A1')

    def test_get_title(self):
        test_title = (
            'Correspondence files, annual single number series '
            '[Main correspondence files series of the agency]'
        )
        title = self.rs.get_title('A1')
        self.assertEqual(title, test_title)

    def test_get_accumulation_dates(self):
        test_dates = {
            'date_str': '01 Jan 1903 - 31 Dec 1938',
            'start_date': {
                'date': datetime.datetime(1903, 1, 1, 0, 0),
                'day': True,
                'month': True
            },
            'end_date': {
                'date': datetime.datetime(1938, 12, 31, 0, 0),
                'day': True,
                'month': True
            }
        }
        accumulation_dates = self.rs.get_accumulation_dates('A1')
        self.assertEqual(accumulation_dates, test_dates)

    def test_get_contents_dates(self):
        test_dates = {
            'date_str': '01 Jan 1890 - 31 Dec 1969',
            'start_date': {
                'date': datetime.datetime(1890, 1, 1, 0, 0),
                'day': True,
                'month': True
            },
            'end_date': {
                'date': datetime.datetime(1969, 12, 31, 0, 0),
                'day': True,
                'month': True
            }
        }
        contents_dates = self.rs.get_contents_dates('A1')
        self.assertEqual(contents_dates, test_dates)

    def test_get_number_described(self):
        results = {
            'described_note': 'All items from this series are entered on RecordSearch.',
            'described_number': 64455
        }
        items_described = self.rs.get_number_described('A1')
        self.assertEqual(items_described, results)


class TestItemFunctions(unittest.TestCase):

    def setUp(self):
        self.rs = client.RSItemClient()

    def test_get_title(self):
        test_title = (
            'WRAGGE Clement Lionel Egerton : SERN 647 : '
            'POB Cheadle England : POE Enoggera QLD : '
            'NOK  (Father) WRAGGE Clement Lindley'
        )
        title = self.rs.get_title('3445411')
        self.assertEqual(title, test_title)

    def test_get_digitised_pages(self):
        pages = self.rs.get_digitised_pages('3445411')
        self.assertEqual(pages, 47)


class TestClosedItemDetails(unittest.TestCase):

        def setUp(self):
            self.rs = client.RSItemClient()

        def test_details(self):
            test_details = {
                'access_decision': {
                    'date_str': u'16 Jul 2012',
                    'end_date': None,
                    'start_date': {
                        'date': datetime.datetime(2012, 7, 16, 0, 0),
                        'day': True,
                        'month': True
                    }
                },
                'access_reason': [{'note': '', 'reason': u'Withheld pending adv'}],
                'access_status': u'Closed',
                'contents_dates': {
                    'date_str': u'1918 - 1925',
                    'end_date': {
                        'date': datetime.datetime(1925, 1, 1, 0, 0),
                        'day': False,
                        'month': False
                    },
                    'start_date': {
                        'date': datetime.datetime(1918, 1, 1, 0, 0),
                        'day': False,
                        'month': False
                    }
                },
                'control_symbol': u'G1924/3039',
                'digitised_pages': 0,
                'digitised_status': False,
                'identifier': u'55545',
                'location': u'Canberra',
                'series': u'A106',
                'title': u'Increments to Permanent Professional Officers.'
            }
            details = self.rs.get_summary('55545')
            self.assertEqual(details, test_details)


class TestAgencyFunctions(unittest.TestCase):

    def setUp(self):
        self.rs = client.RSAgencyClient()

    def test_get_identifier(self):
        identifier = self.rs.get_identifier('CA 12')
        self.assertEqual(identifier, 'CA 12')

    def test_get_title(self):
        test_title = (
            'Prime Minister\'s Department'
        )
        title = self.rs.get_title('CA 12')
        self.assertEqual(title, test_title)

    def test_get_dates(self):
        test_dates = {
            'date_str': '01 Jul 1911 -  12 Mar 1971',
            'start_date': {
                'date': datetime.datetime(1911, 7, 1, 0, 0),
                'day': True,
                'month': True
            },
            'end_date': {
                'date': datetime.datetime(1971, 3, 12, 0, 0),
                'day': True,
                'month': True
            }
        }
        dates = self.rs.get_dates('CA 12')
        self.assertEqual(dates, test_dates)


class TestAgencyDetails(unittest.TestCase):

    def setUp(self):
        self.rs = client.RSAgencyClient()

    def test_summary(self):
        test_details = {
            'agency_id': 'CA 100',
            'agency_status': u'Regional or State Office',
            'associated_people': None,
            'controlled_agencies': None,
            'dates': {'date_str': u'01 Oct 1926 -  31 Dec 1936',
                      'end_date': {'date': datetime.datetime(1936, 12, 31, 0, 0),
                                   'day': True,
                                   'month': True},
                      'start_date': {'date': datetime.datetime(1926, 10, 1, 0, 0),
                                     'day': True,
                                     'month': True}},
            'functions': [{'date_str': u'01 Oct 1926 - 31 Dec 1936',
                           'end_date': {'date': datetime.datetime(1936, 12, 31, 0, 0),
                                        'day': True,
                                        'month': True},
                           'identifier': u'HORTICULTURE',
                           'start_date': {'date': datetime.datetime(1926, 10, 1, 0, 0),
                                          'day': True,
                                          'month': True},
                           'title': u'HORTICULTURE'}],
            'location': u'Victoria',
            'previous_agencies': None,
            'subsequent_agencies': None,
            'superior_agencies': [{'date_str': u'01 Oct 1926 - 31 Jan 1928',
                                   'end_date': {'date': datetime.datetime(1928, 1, 31, 0, 0),
                                                'day': True,
                                                'month': True},
                                   'identifier': u'CA 20',
                                   'start_date': {'date': datetime.datetime(1926, 10, 1, 0, 0),
                                                  'day': True,
                                                  'month': True},
                                   'title': u'Department of Markets and Migration, Central Administration'},
                                  {'date_str': u'01 Jan 1928 - 31 Dec 1928',
                                   'end_date': {'date': datetime.datetime(1928, 12, 31, 0, 0),
                                                'day': True,
                                                'month': True},
                                   'identifier': u'CA 21',
                                   'start_date': {'date': datetime.datetime(1928, 1, 1, 0, 0),
                                                  'day': True,
                                                  'month': True},
                                   'title': u'Department of Markets [I], Central Office'},
                                  {'date_str': u'01 Dec 1928 - 30 Apr 1930',
                                   'end_date': {'date': datetime.datetime(1930, 4, 30, 0, 0),
                                                'day': True,
                                                'month': True},
                                   'identifier': u'CA 23',
                                   'start_date': {'date': datetime.datetime(1928, 12, 1, 0, 0),
                                                  'day': True,
                                                  'month': True},
                                   'title': u'Department of Markets and Transport, Central Office'},
                                  {'date_str': u'01 Apr 1930 - 30 Apr 1932',
                                   'end_date': {'date': datetime.datetime(1932, 4, 30, 0, 0),
                                                'day': True,
                                                'month': True},
                                   'identifier': u'CA 25',
                                   'start_date': {'date': datetime.datetime(1930, 4, 1, 0, 0),
                                                  'day': True,
                                                  'month': True},
                                   'title': u'Department of Markets [II], Central Office'},
                                  {'date_str': u'01 Apr 1932 - 31 Dec 1936',
                                   'end_date': {'date': datetime.datetime(1936, 12, 31, 0, 0),
                                                'day': True,
                                                'month': True},
                                   'identifier': u'CA 28',
                                   'start_date': {'date': datetime.datetime(1932, 4, 1, 0, 0),
                                                  'day': True,
                                                  'month': True},
                                   'title': u'Department of Commerce, Central Office'}],
            'title': u'State Advisory Fruit Board, Victoria'}
        details = self.rs.get_summary('CA 100')
        self.assertEqual(details, test_details)


class TestAgencySearch(unittest.TestCase):

    def setUp(self):
        self.rs = client.RSAgencySearchClient()

    def test_totals(self):
        test_total = '198'
        self.rs.search_agencies(function="MIGRATION")
        total = self.rs.total_results
        self.assertEqual(total, test_total)


class TestSeriesDetails(unittest.TestCase):

    def setUp(self):
        self.rs = client.RSSeriesClient()

    def test_details(self):
        test_details = {
            'access_status': {'CLOSED': 0, 'NYE': 0, 'OPEN': 27, 'OWE': 0},
            'accumulation_dates': {
                'date_str': u'20 Jan 1916 - 31 Jul 1916',
                'end_date': {'date': datetime.datetime(1916, 7, 31, 0, 0),
                             'day': True,
                             'month': True},
                'start_date': {'date': datetime.datetime(1916, 1, 20, 0, 0),
                               'day': True,
                               'month': True}},
            'arrangement': u'Single number system imposed by National Archives of Australia',
            'contents_dates': {
                'date_str': u'27 Aug 1914 - 22 Apr 1918',
                'end_date': {'date': datetime.datetime(1918, 4, 22, 0, 0),
                             'day': True,
                             'month': True},
                'start_date': {'date': datetime.datetime(1914, 8, 27, 0, 0),
                               'day': True,
                               'month': True}},
            'control_symbols': u'[1] - [27]',
            'controlling_agencies': [{
                'date_str': u'12 Mar 1971 -',
                'end_date': {'date': None,
                             'day': False,
                             'month': False},
                'identifier': u'CA 1401',
                'start_date': {'date': datetime.datetime(1971, 3, 12, 0, 0),
                               'day': True,
                               'month': True},
                'title': u'Department of the Prime Minister and Cabinet'}],
            'controlling_series': None,
            'identifier': 'CP359/2',
            'items_described': {'described_note': u'All items from this series are entered on RecordSearch.', 'described_number': 27},
            'items_digitised': 21,
            'locations': [{'location': u'ACT', 'quantity': 0.36}],
            'physical_format': u'PAPER FILES AND DOCUMENTS',
            'previous_series': None,
            'recording_agencies': [{'date_str': u'20 Jan 1916 - 31 Jul 1916',
                                    'end_date': {'date': datetime.datetime(1916, 7, 31, 0, 0),
                                                 'day': True,
                                                 'month': True},
                                    'identifier': u'CA 12',
                                    'start_date': {'date': datetime.datetime(1916, 1, 20, 0, 0),
                                                   'day': True,
                                                   'month': True},
                                    'title': u"Prime Minister's Department - Prime Minister's Office"},
                                   {'date_str': u'20 Jan 1916 - 31 Jul 1916',
                                    'end_date': {'date': datetime.datetime(1916, 7, 31, 0, 0),
                                                 'day': True,
                                                 'month': True},
                                    'identifier': u'CP 290',
                                    'start_date': {'date': datetime.datetime(1916, 1, 20, 0, 0),
                                                   'day': True,
                                                   'month': True},
                                    'title': u'The Rt Hon William Morris HUGHES PC, CH, KC'}],
            'related_series': None,
            'subsequent_series': None,
            'title': u'Subject files maintained by the Prime Minister (William Morris Hughes) during his visit to London, 1916'
        }
        details = self.rs.get_summary('CP359/2')
        self.assertEqual(details, test_details)


class TestSeriesSearch(unittest.TestCase):

    def setUp(self):
        self.rs = client.RSSeriesSearchClient()

    def test_totals(self):
        test_total = '429'
        self.rs.search_series(agency_recording="CA 12", page=1)
        total = self.rs.total_results
        self.assertEqual(total, test_total)


class TestUtilityFunctions(unittest.TestCase):

    def test_parse_date(self):
        cases = [
            ('2 June 1884', {'date': datetime.datetime(1884, 6, 2), 'day': True, 'month': True}),
            ('03 Jul 1921', {'date': datetime.datetime(1921, 7, 3), 'day': True, 'month': True}),
            ('13 Jul. 1921', {'date': datetime.datetime(1921, 7, 13), 'day': True, 'month': True}),
            ('Dec 1778', {'date': datetime.datetime(1778, 12, 1), 'day': False, 'month': True}),
            ('1962', {'date': datetime.datetime(1962, 1, 1), 'day': False, 'month': False}),
        ]
        for case in cases:
            self.assertEqual(utilities.parse_date(case[0]), case[1])

    def test_process_date_string(self):
        cases = [
            ('2 June 1884 - Sep 1884',
                {
                    'date_str': '2 June 1884 - Sep 1884',
                    'start_date': {'date': datetime.datetime(1884, 6, 2), 'day': True, 'month': True},
                    'end_date': {'date': datetime.datetime(1884, 9, 1), 'day': False, 'month': True},
                }),
        ]
        for case in cases:
            self.assertEqual(utilities.process_date_string(case[0]), case[1])

    def test_convert_date_to_iso(self):
        cases = [
            ({'date': datetime.datetime(1884, 6, 2), 'day': True, 'month': True}, '1884-06-02'),
            ({'date': datetime.datetime(1778, 12, 1), 'day': False, 'month': True}, '1778-12'),
            ({'date': datetime.datetime(1962, 1, 1), 'day': False, 'month': False}, '1962'),
        ]
        for case in cases:
            self.assertEqual(utilities.convert_date_to_iso(case[0]), case[1])


if __name__ == '__main__':
    unittest.main()
