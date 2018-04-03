r""" generate_multi_image.py

Generates some postcards using some LLPG data.
Looks up some address and collection details and uses Pillow to write this on to a template
A refactoring of generate_image.py

Example:
    To run from the AddressCards directory:
    py -3 .\generate_multi_image.py
"""

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
            'Friday': 8}
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
            self.recycling_box_str = ''
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


class CalendarImage:
    """ Represents a single image of some bins with some calendar data on top
    """

    def __init__(self, calendar):
        """ Sets some values used to generate the correct image
        """
        self.calendar = calendar
        self.calendar_font = ImageFont.truetype('futura bold condensed italic bt.ttf', 61)
        self.load_calendar_image()
        self.build_calendar_image()

    def load_calendar_image(self):
        """ Loads the correct image based on image type
        """
        # If the recycling box and bins are collected simultaneously
        if self.calendar.recycling_box_str == '':
            self.image_type = 'SAME_COLLECTION'
            self.calendar_image = Image.open('./in/postcard-back-same-dates.jpg').convert('RGB')
            self.calendar_image.load()

    def build_calendar_image(self):
        """ Builds the correct image using the background and calendar data
        """
        black_bin_str = self.wrap_text(calendar.black_bin_str)
        black_bin_text = self.create_text_box(black_bin_str, 300, 450, 4)
        self.paste_text_box(black_bin_text, 350, 660)
        recycling_bin_str = self.wrap_text(calendar.recycling_bin_str)
        recycling_bin_text = self.create_text_box(recycling_bin_str, 300, 450, 4)
        self.paste_text_box(recycling_bin_text, 1045, 660)
        if self.image_type != 'SAME_COLLECTION':
            recycling_box_str = self.wrap_text(calendar.recycling_box_str)
            recycling_box_text = self.create_text_box(recycling_box_str, 400, 250, 4)
            self.paste_text_box(recycling_box_text, 880, 620)
        green_bin_str = self.wrap_text(calendar.green_bin_str)
        green_bin_text = self.create_text_box(green_bin_str, 300, 45, 4)
        self.paste_text_box(green_bin_text, 1945, 660)
        self.calendar_image.save(
            './out/{}.pdf'.format(self.calendar.uprn),
            resolution=100.0,
            quality=100
        )

    def wrap_text(self, string):
        """ Wraps the given calendar date on to multiple lines to fit the image
        """
        return textwrap.wrap(
            string,
            width=3,
            replace_whitespace=False,
            break_long_words=False)

    def create_text_box(self, string, width, height, rotation):
        """ Creates a text box to hold the calendar data
        """
        text_box = Image.new('L', (width, height))
        text_box_draw = ImageDraw.Draw(text_box)
        padding = 10
        current_height = 50
        for line in string:
            line_width, line_height = text_box_draw.textsize(line, font=self.calendar_font)
            # Writes the text to the box using the width and height so it's centre aligned
            text_box_draw.text(
                ((width - line_width) / 2, current_height),
                line,
                font=self.calendar_font,
                fill=255)
            current_height += line_height + padding
        return text_box.rotate(rotation, resample=Image.BICUBIC, expand=True)

    def paste_text_box(self, text_box, x_coord, y_coord):
        """ Pastes the text box on to the image given a set of coordinates
        """
        self.calendar_image.paste(
            ImageOps.colorize(
                text_box,
                (255, 255, 255),
                (255, 255, 255)),
            (x_coord, y_coord),
            text_box)


if __name__ == '__main__':
    pyodbc.pooling = False
    CONN_STRING = ConnectionString()
    CONN = pyodbc.connect(
        driver=CONN_STRING.driver,
        server=CONN_STRING.server,
        database=CONN_STRING.database,
        uid=CONN_STRING.uid,
        pwd=CONN_STRING.pwd)

    # Lists of UPRNs are split into four (maximum), one for each corner of the postcard group
    UPRN_LISTS = [
        ['010001279831', '100050380169', '100050359718', '010001285090'],
        ['100050370512', '100050366002', '010001286067']]
    for uprn_list in UPRN_LISTS:
        for uprn in uprn_list:
            calendar = Calendar(CONN, uprn)
            address = Address(CONN, uprn)
            calendar_image = CalendarImage(calendar)
    CONN.close()
