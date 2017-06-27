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
            'described_number': '64453'
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


class TestAgencySearchFunctions(unittest.TestCase):

    def setUp(self):
        self.rs = client.RSAgencySearchClient()

    def test_totals(self):
        test_total = '191'
        self.rs.search_agencies(function="MIGRATION")
        total = self.rs.total_results
        self.assertEqual(total, test_total)


class TestSeriesFunctions(unittest.TestCase):

    def setUp(self):
        self.rs = client.RSSeriesClient()

    def test_get_identifier(self):
        identifier = self.rs.get_identifier('CP359/2')
        self.assertEqual(identifier, 'CP359/2')

    def test_get_title(self):
        test_title = (
            'Subject files maintained by the Prime Minister (William Morris Hughes) during his visit to London, 1916'
        )
        title = self.rs.get_title('CP359/2')
        self.assertEqual(title, test_title)

    def test_get_dates(self):
        test_dates = {
            'date_str': '27 Aug 1914 - 22 Apr 1918',
            'start_date': {
                'date': datetime.datetime(1914, 8, 27, 0, 0),
                'day': True,
                'month': True
            },
            'end_date': {
                'date': datetime.datetime(1918, 4, 22, 0, 0),
                'day': True,
                'month': True
            }
        }
        dates = self.rs.get_contents_dates('CP359/2')
        self.assertEqual(dates, test_dates)


class TestSeriesSearchFunctions(unittest.TestCase):

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
