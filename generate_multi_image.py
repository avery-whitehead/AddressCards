import json
import textwrap
import os
from PIL import Image, ImageDraw, ImageFont, ImageOps
from PyPDF2 import PdfFileReader, PdfFileWriter
import pyodbc

class ConnectionString:
    """ Represents a pyodbc connection string
    """

    def __init__(self):
        """ Reads the attributes from a config file
        """
        with open('.config') as config_file:
            config = json.load(config_file)
            self.driver = config['driver']
            self.server = config['server']
            self.database = config['database']
            self.uid = config['uid']
            self.pwd = config['pwd']

class Calendar:
    """ Represents a set of days on which particular bins are collected.
    """

    def __init__(self, connection, uprn):
        """ Maps each day to a date and calls the methods to create the calendar
        """
        self.dates = {
            'Monday': 4,
            'Tuesday': 5,
            'Wednesday': 6,
            'Thursday': 7,
            'Friday': 8
        }
        self.connection = connection
        self.uprn = uprn
        self.get_calendar_data()
        self.format_calendar_strings()

    def get_calendar_data(self):
        """ Queries the database using to get the calendar data
        """
        with open('./cal_query.sql', 'r') as query_file:
            query = query_file.read()
            cursor = self.connection.cursor()
            cursor.execute(query, self.uprn)
            row = cursor.fetchone()
            self.black_bin_day = row.REFDay
            self.recycling_bin_day = row.RECYDay
            self.recycling_box_day = row.RECYDay
            self.green_bin_day = row.GWDay
            cursor.close()

    def format_calendar_strings(self):
        """ Formats the calendar data to match the design of the card
        """
        self.black_bin_str = '{}   from   {} June 2018'.format(
            self.black_bin_day, str(self.dates[self.black_bin_day]))
        self.recycling_bin_str = '{}   from   {} June 2018'.format(
            self.recycling_bin_day, str(self.dates[self.recycling_bin_day]))
        if self.recycling_box_day == self.recycling_bin_day:
            self.recycling_box_str = 'Same day for box and bin'
        else:
            self.recycling_box_str = '{}   from   {} June 2018'.format(
                self.recycling_box_day, str(self.dates[self.recycling_box_day]))
        if self.green_bin_day == '-':
            self.green_bin_str = 'Not collected'
        else:
            self.green_bin_str = '{}   from   {} June 2018'.format(
                self.green_bin_day, str(self.dates[self.green_bin_day]))


class Address:
    """ Represents a Royal Mail standard address of a property
    """
    def __init__(self, connection, uprn):
        """ Calls the methods to create an address
        """
        self.connection = connection
        self.uprn = uprn
        self.get_address_data()
        self.format_address_string()

    def get_address_data(self):
        """ Queries the database to get the address data
        """
        with open('./cal_query.sql', 'r') as query_file:
            query = query_file.read()
            cursor = self.connection.cursor()
            cursor.execute(query, self.uprn)
            row = cursor.fetchone()
            self.address_block = row.addressBlock

    def format_address_string(self):
        """ Formats the address data to match the design of the card
        """
        self.address_block = self.address_block.replace('<br>', '\n')


if __name__ == '__main__':
    pyodbc.pooling = False
    CONN_STRING = ConnectionString()
    CONN = pyodbc.connect(
        driver=CONN_STRING.driver,
        server=CONN_STRING.server,
        database=CONN_STRING.database,
        uid=CONN_STRING.uid,
        pwd=CONN_STRING.pwd
    )

    # Lists of UPRNs are split into four (maximum), one for each corner of the postcard group
    UPRN_LISTS = [
        ['010001279831', '100050380169', '100050359718', '010001285090'],
        ['100050370512', '100050366002', '010001286067']]
    for uprn_list in UPRN_LISTS:
        for uprn_val in uprn_list:
            calendar = Calendar(CONN, uprn_val)
            address = Address(CONN, uprn_val)
            print(calendar.uprn + ': ')
            print(address.address_block)
            print(calendar.black_bin_str)
            print(calendar.recycling_bin_str)
            print(calendar.recycling_box_str)
            print(calendar.green_bin_str)
            print()
    CONN.close()
