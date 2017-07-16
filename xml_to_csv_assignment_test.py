

from xml_to_csv.core import XmlToCsv
from misc.data_for_tests import QUERY_2016_AND, OUTPUT_FIELD_NAMES, SORT_BY_DATELISTED 

# Relevant input for the coding assignment
RAW_FEED = 'http://syndication.enterprise.websiteidx.com/feeds/BoojCodeTest.xml'


# Helpful for running the coding challenge
if __name__ == '__main__':
    parser = XmlToCsv(RAW_FEED)
    parser.convert(
        OUTPUT_FIELD_NAMES,
        QUERY_2016_AND,
        sort_method=SORT_BY_DATELISTED
    )
