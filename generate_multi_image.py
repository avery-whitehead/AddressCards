r""" generate_multi_image.py

Generates some postcards using some LLPG data.
Looks up some address and collection details and uses Pillow to write this
on to a template. A refactoring of generate_image.py

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
        """ Maps each day to a date and calls the methods to create the
        calendar
        """
        self.dates = {
            'Monday': 0,
            'Tuesday': 1,
            'Wednesday': 2,
            'Thursday': 3,
            'Friday': 4}
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
            self.black_bin_week = row.REFWeek
            self.recycling_bin_day = row.RECYDay
            self.recycling_bin_week = row.RECYWeek
            self.recycling_box_day = row.RECYDay
            self.recycling_box_week = row.RECYWeek
            self.green_bin_day = row.GWDay
            self.green_bin_week = row.GWWeek
            cursor.close()

    def format_calendar_strings(self):
        """ Formats the calendar data to match the design of the card
        """
        self.black_bin_str = '{}   from   {} June 2018'.format(
            self.black_bin_day,
            str((self.black_bin_week * 7) + self.dates[self.black_bin_day] + 4))
        self.recycling_bin_str = '{}   from   {} June 2018'.format(
            self.recycling_bin_day,
            str((self.recycling_bin_week * 7) + self.dates[self.recycling_bin_day] + 4))
        if self.recycling_box_day == self.recycling_bin_day:
            self.recycling_box_str = ''
        else:
            self.recycling_box_str = '{}   from   {} June 2018'.format(
                self.recycling_box_day,
                str((self.recycling_box_week * 7) + self.dates[self.recycling_bin_day] + 4))
        if self.green_bin_day == '-':
            self.green_bin_str = 'Not collected'
        else:
            self.green_bin_str = '{}   from   {} June 2018'.format(
                self.green_bin_day,
                str((self.green_bin_week * 7) + self.dates[self.green_bin_day] + 4))


class CalendarImage:
    """ Represents a single image of some bins with some calendar data on top
    """

    def __init__(self, calendar):
        """ Sets some values used to generate the correct image
        """
        self.calendar = calendar
        self.calendar_font = ImageFont.truetype(
            'futura bold condensed italic bt.ttf', 59)
        self.load_calendar_image()
        self.image = self.build_calendar_image()

    def load_calendar_image(self):
        """ Loads the correct image based on image type
        """
        # If the recycling box and bins are collected simultaneously
        if self.calendar.recycling_box_str == '':
            self.image_type = 'SAME_COLLECTION'
            self.calendar_image = Image.open(
                './in/postcard-back-same-dates.jpg').convert('RGB')
            self.calendar_image.load()

    def build_calendar_image(self):
        """ Builds the correct image using the background and calendar data
        """
        if self.image_type == 'SAME_COLLECTION':
            black_bin_str = wrap_text(calendar.black_bin_str, 7)
            # Width, height and rotation of the text box
            black_bin_text = create_text_box(
                black_bin_str,
                300, 450, 4,
                self.calendar_font,
                255,
                False)
            # X and Y coordinate of the text box
            paste_text_box(
                self.calendar_image,
                black_bin_text,
                415, 750,
                #325, 655,
                (255, 255, 255),
                (255, 255, 255))
            recycling_bin_str = wrap_text(calendar.recycling_bin_str, 7)
            recycling_bin_text = create_text_box(
                recycling_bin_str,
                300, 450, 4,
                self.calendar_font,
                255,
                False)
            paste_text_box(
                self.calendar_image,
                recycling_bin_text,
                1105, 750,
                (255, 255, 255),
                (255, 255, 255))
            recycling_box_str = wrap_text(calendar.recycling_box_str, 7)
            recycling_box_text = create_text_box(
                recycling_box_str,
                400, 250, 4,
                self.calendar_font,
                255,
                False)
            paste_text_box(
                self.calendar_image,
                recycling_box_text,
                970, 750,
                (255, 255, 255),
                (255, 255, 255))
            green_bin_str = wrap_text(calendar.green_bin_str, 7)
            green_bin_text = create_text_box(
                green_bin_str,
                300, 450, 4,
                self.calendar_font,
                255,
                False)
            paste_text_box(
                self.calendar_image,
                green_bin_text,
                2010, 750,
                (255, 255, 255),
                (255, 255, 255))
        if self.image_type == 'DIFFERENT_COLLECTION':
            print('TODO: handle different image collection')
        return self.calendar_image


class CalendarSide:
    """ Represents a collection of four CalendarImage objects pasted on a
    blank image
    """

    def __init__(self, calendar_image_list):
        """ Defines the positions for the calendar images
        """
        self.calendar_image_list = calendar_image_list
        # X and y offsets for top-left, top-right, bottom-left, bottom-right
        self.positions = [(0, 0), (2655, 0), (0, 1929), (2655, 1929)]
        self.calendar_side_image = Image.open(
            './in/blank_a3.jpg').convert('RGB')
        self.calendar_side_image.load()
        self.build_calendar_side()
        filename = ['cal']
        for calendar_image in self.calendar_image_list:
            filename.append(calendar_image.calendar.uprn)
        self.new_file = save_image(
            '-'.join(filename), self.calendar_side_image)

    def build_calendar_side(self):
        """ Pastes each CalendarImage at the correct position on the blank
        page to create a 4x4 grid
        """
        for position, calendar_image in enumerate(self.calendar_image_list):
            paste_image(
                self.calendar_side_image,
                calendar_image.image,
                self.positions[position][0],
                self.positions[position][1])


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


class AddressImage:
    """ Represents a single image of a postal address
    """

    def __init__(self, address):
        """ Sets some values used to generate the correct images
        """
        self.address = address
        self.address_font = ImageFont.truetype('arial.ttf', 60)
        self.address_image = Image.open(
            './in/postcard-front.jpg').convert('RGB')
        self.address_image.load()
        self.build_address_image()

    def build_address_image(self):
        """ Builds the correct image using the background and address data
        """
        text_box = create_text_box(
            self.address.address_block,
            1900, 850, 0,
            self.address_font,
            255,
            True)
        paste_text_box(
            self.address_image,
            text_box,
            500, 600,
            (0, 0, 0),
            (0, 0, 0))


class AddressSide:
    """ Represents a collection of four AddressSide objects pasted on a blank
    image
    """

    def __init__(self, address_image_list):
        """ Defines the positions for the calendar images
        """
        self.address_image_list = address_image_list
        # X and y offsets for top-left, top-right, bottom-left, bottom-right
        self.positions = [(0, 0), (2655, 0), (0, 1929), (2655, 1929)]
        self.address_side_image = Image.open(
            './in/blank_a3.jpg').convert('RGB')
        self.address_side_image.load()
        self.build_address_side()
        filename = ['addr']
        for address_image in self.address_image_list:
            filename.append(address_image.address.uprn)
        self.new_file = save_image('-'.join(filename), self.address_side_image)

    def build_address_side(self):
        """ Pastes each AddressImage at the correct position on the blank page
        to create a 4x4 grid
        """
        for position, address_image in enumerate(self.address_image_list):
            paste_image(
                self.address_side_image,
                address_image.address_image,
                self.positions[position][0],
                self.positions[position][1])


def wrap_text(string, width):
    """ Wraps a given string on to multiple lines to fit the image
    """
    return textwrap.wrap(
        string,
        width=width,
        replace_whitespace=False,
        break_long_words=False)

def create_text_box(string, width, height, rotation, font, fill, multiline):
    """ Creates a text box to hold some string data
    """
    text_box = Image.new('L', (width, height))
    text_box_draw = ImageDraw.Draw(text_box)
    # If the string doesn't have built-in linebreaks (i.e. calendar string)
    if not multiline:
        padding = 10
        current_height = 50
        for line in string:
            line_width, line_height = text_box_draw.textsize(line, font=font)
            # Writes the text to the box so it's centre aligned
            text_box_draw.text(
                ((width - line_width) / 2, current_height),
                line,
                font=font,
                fill=fill)
            current_height += line_height + padding
    else:
        text_box_draw.multiline_text(
            (0, 0), string, font=font, fill=fill, spacing=20)
    return text_box.rotate(rotation, resample=Image.BICUBIC, expand=True)

def paste_text_box(base_image, text_box, x_coord, y_coord, rgb_black, rgb_white):
    """ Pastes a text box on to an image, given a set of coordinates
    """
    base_image.paste(
        ImageOps.colorize(
            text_box,
            rgb_black,
            rgb_white),
        (x_coord, y_coord),
        text_box)

def paste_image(base_image, image_to_paste, x_coord, y_coord):
    """ Pasts an image on to another image, given a set of coordinates
    """
    base_image.paste(image_to_paste, (x_coord, y_coord))

def save_image(filename, image):
    """ Saves an image to file as a PDF
    """
    out_path = './out/{}.jpg'.format(filename)
    image.save(out_path, resolution=100.0, quality=100, dpi=(300,300))
    return out_path

def append_pdfs(paths, uprns):
    """ Appends the two created PDFs into one file
    """
    # Opens and combines the two files
    combined = PdfFileWriter()
    first_file = open(paths[0], 'rb')
    second_file = open(paths[1], 'rb')
    first = PdfFileReader(first_file)
    second = PdfFileReader(second_file)
    combined.addPage(first.getPage(0))
    combined.addPage(second.getPage(0))
    # Writes the new file
    out_file = './out/{}.pdf'.format('-'.join(uprns))
    stream = open(out_file, 'wb')
    combined.write(stream)
    # Cleans up the stream and the old files
    stream.close()
    first_file.close()
    second_file.close()
    os.remove(paths[0])
    os.remove(paths[1])
    return 'Created PDF {}'.format(out_file)

if __name__ == '__main__':
    pyodbc.pooling = False
    CONN_STRING = ConnectionString()
    CONN = pyodbc.connect(
        driver=CONN_STRING.driver,
        server=CONN_STRING.server,
        database=CONN_STRING.database,
        uid=CONN_STRING.uid,
        pwd=CONN_STRING.pwd)
    # Lists of UPRNs are split into max four, one for each corner the card
    UPRN_LISTS = [
        ['010001279831', '100050380169', '100050359718', '010001285090'],
        ['100050370512', '100050366002', '010001286067']]
    for uprn_list in UPRN_LISTS:
        calendar_images = []
        address_images = []
        for uprn in uprn_list:
            calendar = Calendar(CONN, uprn)
            address = Address(CONN, uprn)
            # calendar_image.image: PIL.Image type, calendar_image.calendar: Calender type
            calendar_image = CalendarImage(calendar)
            calendar_images.append(calendar_image)
            address_image = AddressImage(address)
            address_images.append(address_image)
        calendar_side = CalendarSide(calendar_images)
        address_side = AddressSide(address_images)
        #print(append_pdfs((address_side.new_file, calendar_side.new_file), uprn_list))
    CONN.close()
