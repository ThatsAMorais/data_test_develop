import mock
import datetime
import unittest

from io import BytesIO
from collections import OrderedDict

from xml_to_csv.core import XmlToCsv
from misc.data_for_tests import XML_FILE, OUTPUT_FIELD_NAMES, QUERY_2016_AND

class TestXmlToCsv(unittest.TestCase):
    """
    Verifies the contracts of the XmlToCsv tool. Some use of details related to 
    the assignment, but one could (and should) test other useful XML schema and 
    queries to ensure the reliability of the behavior for wider use.

    There is a blend of unit and functional testing in this class. In some 
    cases it was more convenient than mocking out calls to validate the correct
    behavior.
    """

    def setUp(self):
        xml_url = 'ignore this with patch'
        # Mock 
        with mock.patch('urllib2.urlopen', return_value=XML_FILE):
            self.xml_parser = XmlToCsv(xml_url)

    def test_convert__base_case(self):
        
        fieldnames = OrderedDict([
            ('field/path/field1','field1'),
            ('field/path/field2', 'field2')
        ])
        criteria = 'XPath Query String'
        sort_method = lambda x: x
        search_result = [111, 20, 350]
        rows = [dict(field1='1234', field2='test'),
                dict(field1='5678', field2='tset')]

        with mock.patch('xml_to_csv.core.XmlToCsv.search_xml', return_value=search_result) as mock_search_xml:
            with mock.patch('xml_to_csv.core.XmlToCsv._extract_xml_fields', return_value=rows) as mock_extract_xml_fields:
                with mock.patch('xml_to_csv.core.XmlToCsv._write_csv') as mock_write_csv:

                    self.xml_parser.convert(fieldnames, criteria, sort_method=sort_method)

                    mock_search_xml.assert_called_once_with(criteria)
                    mock_extract_xml_fields.assert_called_once_with(sorted(search_result, key=sort_method), fieldnames)
                    mock_write_csv.assert_called_once_with(fieldnames.values(), rows, mock.ANY)

    def test_convert__reversed_sort(self):
        """
        Verifies the reverse sort behavior
        """
        sort_method = lambda x: x
        search_result = [111, 20, 350]

        with mock.patch('xml_to_csv.core.XmlToCsv.search_xml', return_value=search_result):
            with mock.patch('xml_to_csv.core.XmlToCsv._extract_xml_fields') as mock_extract_xml_fields:
                with mock.patch('xml_to_csv.core.XmlToCsv._write_csv') as mock_write_csv:
                    
                    self.xml_parser.convert(dict(), '', reverse=True, sort_method=sort_method)
                    mock_extract_xml_fields.assert_called_once_with(
                        sorted(search_result, key=sort_method, reverse=True), mock.ANY)

    def test_search_xml__2016_and(self):
        """
        Verifies that a search on the test data for this compatible query returns the correct result
        """
        result = self.xml_parser.search_xml(QUERY_2016_AND)
        # There are 3 rows in the test data, and only 1 matches the query
        self.assertEqual(len(result), 1)

    def test_extract_xml_fields(self):
        result = self.xml_parser.search_xml(QUERY_2016_AND)
        rows = self.xml_parser._extract_xml_fields(result, OUTPUT_FIELD_NAMES)
        self.assertEqual(len(rows), 1)
        for fieldname in OUTPUT_FIELD_NAMES.values():
            self.assertIn(fieldname, rows[0])

    def test_write_csv(self):
        result = self.xml_parser.search_xml(QUERY_2016_AND)
        rows = self.xml_parser._extract_xml_fields(result, OUTPUT_FIELD_NAMES)
        with mock.patch('xml_to_csv.core.open', mock.mock_open(read_data=BytesIO(''))):
            self.xml_parser._write_csv(OUTPUT_FIELD_NAMES.values(), rows, 'filename')
        # This method is primarily I/O and library calls, but still a good idea to defend
        #  against any buggy changes. Nothing to assert.
