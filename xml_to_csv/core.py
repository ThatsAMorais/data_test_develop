"""
An XML Parsing Library + Example script (for brevity)
"""

import urllib2
import uuid
import datetime
from collections import OrderedDict

import csv

from io import BytesIO

from lxml import etree


class XmlToCsv():
    """
    Utility class to convert data from XML based on XPath into a CSV file
    """

    def __init__(self, xml_file_url):
        # Parse the remote XML file into an lxml element tree
        self.doc = etree.parse(urllib2.urlopen(xml_file_url))

    def convert(
            self, fieldnames, criteria,
            sort_method=None, reverse=False, filename=str(uuid.uuid4())
            ):
        """
        Write XML records matching the XPATH criteria to a CSV. Optionally,
        sort the result set.
        :param fieldnames: fieldname map, e.g. {'Path/To/Field': 'Field'}
        :param criteria: the xpath query string used to filter the output
        :param sort_method: a function used to sort the result set
        :param reverse: whether or not to reverse the sorted order
        :param filename: how to name the file 
        """
        query_result = self.search_xml(criteria)
        if sort_method:
            query_result.sort(key=sort_method, reverse=reverse)
        rows = self._extract_xml_fields(query_result, fieldnames)
        csv_file = self._write_csv(fieldnames.values(), rows, filename)

    def search_xml(self, criteria):
        """
        Query the tree using XPATH with the given criteria
        :param criteria: an XPath query string
        """
        return self.doc.xpath(criteria)

    def _extract_xml_fields(self, xml_data, fieldnames):
        """
        Builds a dictionary containing the specified fields from the XML
        :param xml_data: List of XML elements
        :param fieldnames: fieldname map
        """
        rows = []
        for datum in xml_data:
            row = dict()
            for path, fieldname in fieldnames.iteritems():
                found = datum.find(path)
                if found is None:
                    continue
                # Determine if this element has children elements, i.e. <things><thing>value</thing></things>
                sub_elements = found.xpath('*[count(child::*) = 0]')
                if sub_elements:
                    row[fieldname] = ','.join([element.text[:200] for element in sub_elements])
                elif found.text:
                    row[fieldname] = found.text[:200]
            rows.append(row)
        return rows

    def _write_csv(self, fieldnames, rows, filename):
        """
        Create a CSV file containing a conversion of the given XML data.
        :param fieldnames: list of field names for the file
        :param rows: the list of row-dicts to be written
        :param filename: the desired filename for the output file
        """
        filename = filename if filename.endswith('.csv') else '%s.csv' % filename 
        print "Writing CSV data to %s" % filename
        with open(filename, 'w') as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames)
            writer.writeheader()
            writer.writerows(rows)
            

# Relevant input for the coding assignment
RAW_FEED = 'http://syndication.enterprise.websiteidx.com/feeds/BoojCodeTest.xml'


# Mapping of xml-dependent paths to field names for output CSV. An ordered-dict preserves the field order
OUTPUT_FIELD_NAMES = OrderedDict([
    ('ListingDetails/MlsId', 'MlsId'),
    ('ListingDetails/MlsName', 'MlsName'),
    ('ListingDetails/DateListed', 'DateListed'),
    ('Location/StreetAddress', 'StreetAddress'),
    ('ListingDetails/Price', 'Price'),
    ('BasicDetails/Bedrooms', 'Bedrooms'),
    ('BasicDetails/Bathrooms', 'Bathrooms'),
    ('BasicDetails/FullBathrooms', 'FullBathrooms'),
    ('BasicDetails/HalfBathrooms', 'HalfBathrooms'),
    ('BasicDetails/ThreeQuarterBathrooms', 'ThreeQuarterBathrooms'),
    ('RichDetails/Appliances', 'Appliances'),  # (all sub-nodes comma joined)
    ('RichDetails/Rooms', 'Rooms'),  # (all sub-nodes comma joined)
    ('BasicDetails/Description', 'Description'),  # (the first 200 characters)
])


# All 2016 properties (DateListed) whose Description contains the word "and"
QUERY_2016_AND = ("//Listing"
                  "["
                  " starts-with(ListingDetails/DateListed, '2016') "
                  " and "
                  " contains(BasicDetails/Description, 'and') "
                  "]")


# Lambda to Sort by DateListed
SORT_BY_DATELISTED = lambda x: datetime.datetime.strptime(
    x.findtext('ListingDetails/DateListed'), '%Y-%m-%d %H:%M:%S')


# Helpful for running the coding challenge
if __name__ == '__main__':
    parser = XmlToCsv(RAW_FEED)
    parser.convert(
        OUTPUT_FIELD_NAMES,
        QUERY_2016_AND,
        sort_method=SORT_BY_DATELISTED
    )
