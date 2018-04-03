import json
import textwrap
import os
from PIL import Image, ImageDraw, ImageFont, ImageOps
from PyPDF2 import PdfFileReader, PdfFileWriter
import pyodbc

class ConnectionString:
    """ Represents a pyodbc connection string. Reads the attributes from a config file
    """
    def __init__(self):
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
        self.build_calendar_strings()

    def get_calendar_data(self):
        with open('./cal_query.sql', 'r') as query_file:
            query = query_file.read()
            # Collects the calendar information from the database
            cursor = self.connection.cursor()
            cursor.execute(query, self.uprn)
            row = cursor.fetchone()
            self.black_bin_day = row.REFDay
            self.recycling_bin_day = row.RECYDay
            self.recycling_box_day = row.RECYDay
            self.green_bin_day = row.GWDay
    
    def build_calendar_strings(self):
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
            print(uprn_val + ': ')
            print(calendar.black_bin_str)
            print(calendar.recycling_bin_str)
            print(calendar.recycling_box_str)
            print(calendar.green_bin_str)
            print()
    CONN.close()
