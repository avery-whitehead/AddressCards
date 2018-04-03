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
        cursor = connection.cursor()
        with open('./cal_query.sql', 'r') as query_file:
            query = query_file.read()
            # Collects the calendar information from the database
            cursor.execute(query, uprn)
            row = cursor.fetchone()
            self.black_bin_day = row.REFDay

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
        for uprn in uprn_list:
            calendar = Calendar(CONN, uprn)
            print(calendar.black_bin_day)
    CONN.close()
