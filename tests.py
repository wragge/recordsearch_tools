import unittest
import retrieve


class TestSeriesFunctions(unittest.TestCase):

    def setUp(self):
        self.rs = retrieve.RSClient()

    def test_get_page_total(self):
        pages = self.rs.get_page_total('3445411')
        self.assertEqual(pages, '47')

    def test_get_reference(self):
        reference = self.rs.get_reference('3445411')
        self.assertEqual(reference, {'series': u'B2455', 'control_symbol': u'WRAGGE C L E', 'digitised': True})

if __name__ == '__main__':
    unittest.main()
