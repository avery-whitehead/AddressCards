""" generate_image.py

Generates some postcards using some LLPG data.
Looks up some address and collection details and uses Pillow to write this on to a template

Example:
    To run from the AddressCards directory:
    py -3 .\generate_image.py

Todo:
    Functionality to read in UPRNs from file in groups of four instead
    of list of lists
    When recycling bin and box days are the same, don't render box dates
    React to any changes made to the template
"""

import json
import textwrap
import os
from PIL import Image, ImageDraw, ImageFont, ImageOps
from PyPDF2 import PdfFileReader, PdfFileWriter
import pyodbc


class DatabaseConn:
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


class Postcard:
    """ Represents a postcard, with an address on one side and calendar on the other

    Args:
        address (str): An address block, each line separated with HTML <br> tags
        calendar (obj:Calendar): A Calendar object containing collection information
    """
    def __init__(self, address, calendar):
        self.address = address
        self.calendar = calendar


class Calendar:
    """ Represents a collection calendar, detailing which bin is collected on which day

    Note:
        Potential day values: Monday, Tuesday, Wednesday, Thursday, Friday
        Potential week values: 1, 2
        Recycling bin days/weeks and glass bin days/weeks are often the same

    Args:
        ref_day (str)
        ref_week (str)
        recy_day (str)
        recy_week (str)
        gw_day (str)
        gw_week (str)
        gls_day (str)
        gls_week (str)
    """
    def __init__(self, ref_day, recy_day, gw_day, gls_day):
        dates = {
            'Monday': 7,
            'Tuesday': 8,
            'Wednesday': 9,
            'Thursday': 10,
            'Friday': 11
        }
        # Represents the text that will be shown for each collection
        self.ref_str = '{} {}, {} May'.format(
            ref_day, str(dates[ref_day]), str(dates[ref_day] + 14))
        self.recy_str = '{} {}, {} May'.format(
            recy_day, str(dates[recy_day]), str(dates[recy_day] + 14))
        if gw_day == '-':
            self.gw_str = 'Not collected'
        else:
            self.gw_str = '{} {}, {} May'.format(
                gw_day, str(dates[gw_day]), str(dates[gw_day] + 14))
        self.gls_str = '{} {}, {} May'.format(
            gls_day, str(dates[gls_day]), str(dates[gls_day] + 14))


class TextBox:
    """ Represents an image to hold some collection data text in

    Args:
        text_image (obj:PIL.Image.Image): An image containing the text
        x_coord(int): How far along the x co-ord the text box should be placed on the base image
        y_coord(int): How far along the y co-ord the text box should be placed on the base image
        x_offset(int): How far along the x co-ord the base image itself is (uses position)
        y_offset(int): How far along the y co-ord the base image itself is (uses position)
    """
    def __init__(self, text_image, x_coord, y_coord, position):
        self.text_image = text_image
        self.x_coord = x_coord
        self.y_coord = y_coord
        # Top left
        if position == 0:
            self.x_offset = 66
            self.y_offset = 44
        # Top right
        if position == 1:
            self.x_offset = 1773
            self.y_offset = 44
        # Bottom left
        if position == 2:
            self.x_offset = 66
            self.y_offset = 1263
        # Bottom right
        if position == 3:
            self.x_offset = 1773
            self.y_offset = 1263


def build_postcard(connector, card_uprn):
    """ Creates a Postcard object for a property

    Args:
        connector (obj:pyodbc.Connection): An open pyodbc database connection object
        uprn (str): A UPRN (Unique Property Reference Number) to look up on the database

    Returns:
        (obj:Postcard): A Postcard object containing the address and calendar data
    """
    cursor = connector.cursor()
    with open('./cal_query.sql', 'r') as query_file:
        query = query_file.read()
        # Runs the SQL query to return an address block and collection information
        cursor.execute(query, card_uprn)
        row = cursor.fetchone()
        # Builds a Calendar object based on the collection information
        cal_obj = Calendar(
            row.REFDay, row.RECYDay, row.GWDay, row.RECYDay)
        # Builds a Postcard object based on the address and collection calendar
        post_obj = Postcard(row.addressBlock, cal_obj)

        # Cleans up leftover cursors
        cursor.close()
        del cursor

        return post_obj


def build_all_images(postcard_lst, uprn_lst):
    """ Given a list of four postcards and UPRNs, pastes text boxes on to each bin section in
    each card and saves as PDF

    Args:
        postcard_lst(list:Postcard): A list of four (or less) Postcard objects
        uprn_lst(list:str): An equivalent list of four (or less) UPRNs

    Returns:
        (list:str) A list of the file paths for the two created PDFs
    """
    addr_img = Image.open('./in/postcard-front-4x4.png').convert('RGB')
    cal_img = Image.open('./in/postcard-back-4x4.png').convert('RGB')
    addr_img.load()
    cal_img.load()

    for position, card in enumerate(postcard_lst):
        # Position is based on the index in the postcard_lst
        text_boxes = build_one_image(card, position)
        # Overlays each box on to the image
        for text_box in text_boxes:
            cal_img.paste(ImageOps.colorize(
                # Fill and outline RGB values of text
                text_box.text_image, (255, 255, 255), (255, 255, 255)),
                          ((text_box.x_coord + text_box.x_offset),
                           (text_box.y_coord + text_box.y_offset)),
                          text_box.text_image)

        address = build_address(card, 400, 300, position)
        addr_img.paste(ImageOps.colorize(
            address.text_image, (0, 0, 0), (0, 0, 0)),
                       ((address.x_coord + address.x_offset),
                        (address.y_coord + address.y_offset)),
                       address.text_image)

    addr_file = './out/addr-{}.pdf'.format('-'.join(uprn_lst))
    cal_file = './out/cal-{}.pdf'.format('-'.join(uprn_lst))

    addr_img.save(addr_file, 'PDF', resolution=100.0, quality=100)
    cal_img.save(cal_file, 'PDF', resolution=100.0, quality=100)

    return [addr_file, cal_file]


def build_one_image(card, position):
    """ Given a single postcard, creates the strings and calls buiild_text to create the four
    text boxes for each bin

    Args:
        card(obj:Postcard): A Postcard object used to get the string data
        position: The position [top-left, top-right, bottom-left, bottom-right] of this postcard
        in the image

    Returns:
        (list:obj:TextBox): A list of the four TextBox objects used in each calendar image
    """
    # Wraps the strings over separate lines
    ref_str = textwrap.wrap(card.calendar.ref_str, width=9)
    recy_str = textwrap.wrap(card.calendar.recy_str, width=9)
    gw_str = textwrap.wrap(card.calendar.gw_str, width=9)
    gls_str = textwrap.wrap(card.calendar.gls_str, width=12)

    # Creates the text boxes
    ref_text = build_text(ref_str, 260, 350, 155, 580, position, 4)
    recy_text = build_text(recy_str, 260, 350, 545, 580, position, 4)
    gw_text = build_text(gw_str, 260, 350, 1325, 580, position, 4)
    # Glass box is unused by most postcards - need to add a special flag for the properties that are
    # gls_text = build_text(gls_str, 0, 0, 0, 0, position, 2)
    gls_text = build_text(gls_str, 380, 230, 880, 620, position, 4)

    # Returns the text boxes
    return [ref_text, recy_text, gw_text, gls_text]


def build_text(string, width, height, x_coord, y_coord, position, rotation):
    """ Creates a text box to be overlaid on to a single bin in the overall image

    Args:
        string(str): The string contained in the text box
        width(int): The width of the text box
        height(int): The height of the text box
        x_coord(int): The x co-ord of the top-left corner of the text box on the single imag
        y_coord(int): The y co-ord of the top-left corner of the text box on the single image
        position(int): The position of the single image in the overall image
        rotation(int): The angular rotation to draw the text box at

    Returns:
        (obj:TextBox): A TextBox object containing the collection days
    """
    cal_font = ImageFont.truetype('futura bold condensed italic bt.ttf', 42)

    # Creates a box to hold the text in
    text_box = Image.new('L', (width, height))
    text_draw = ImageDraw.Draw(text_box)

    # The padding between lines
    pad = 10
    # The current height in the box
    curr_h = 50

    # Writes each line to the text box
    for line in string:
        # Calculates the width and height of each line
        wid, hei = text_draw.textsize(line, font=cal_font)
        # Writes the text to the box using the width and height so it's centre aligned
        text_draw.text(((width - wid) / 2, curr_h), line, font=cal_font, fill=255)
        # Move the height cursor down
        curr_h += hei + pad

    # Rotates the box
    return TextBox(text_box.rotate(rotation, resample=Image.BICUBIC, expand=True),
                   x_coord, y_coord, position)


def build_address(card, x_coord, y_coord, position):
    """ Creates a text box to contain the address of a property

    Args:
        card(obj:Postcard): A Postcard object used to get the address data
        x_coord(int): The x co-ord of the top-left corner of the text box on the single image
        y_coord(int): The y co-ordinate of the top-left corner of the text box on the single image
        position(int): The position of the single image in the overall image

    Returns:
        (obj:TextBox): A TextBox containing the address of the property
    """
    addr_font = ImageFont.truetype('arial.ttf', 60)

    # Changes HTML line break to Python line break
    addr_string = (card.address).replace('<br>', '\n')
    text_box = Image.new('L', (1900, 850))
    text_draw = ImageDraw.Draw(text_box)
    text_draw.multiline_text((0, 0), addr_string, font=addr_font, fill=255, spacing=20)

    return TextBox(text_box, x_coord, y_coord, position)


def append_pdfs(paths, uprns):
    """ Appends the two created PDFs into one file

    Args:
        paths(list:str): The file paths of the two PDFs to append
        uprns(list:str): The UPRNs of the postcards in the PDF

    Returns:
        (str): A success message with the name of the file created
    """
    # Opens the two PDFs
    combined = PdfFileWriter()
    first_file = open(paths[0], 'rb')
    second_file = open(paths[1], 'rb')
    first = PdfFileReader(first_file)
    second = PdfFileReader(second_file)

    # Creates the combined PDF
    combined.addPage(first.getPage(0))
    combined.addPage(second.getPage(0))

    # Writes the combined PDF to file
    out_file = './out/{}.pdf'.format('-'.join(uprns))
    stream = open(out_file, 'wb')
    combined.write(stream)
    stream.close()

    # Cleans up the separate PDFs
    first_file.close()
    second_file.close()
    os.remove(paths[0])
    os.remove(paths[1])

    return 'Created PDF {}'.format(out_file)


if __name__ == '__main__':
    pyodbc.pooling = False
    CONN_DATA = DatabaseConn()
    CONN = pyodbc.connect(
        driver=CONN_DATA.driver,
        server=CONN_DATA.server,
        database=CONN_DATA.database,
        uid=CONN_DATA.uid,
        pwd=CONN_DATA.pwd
    )

    # Lists of UPRNs are split into four, one for each corner of the 4x4 A3 sheet
    UPRN_LISTS = [['010001279831', '100050380169', '100050359718', '010001285090'],
                  ['100050370512', '100050366002', '010001286067']]
    for uprn_list in UPRN_LISTS:
        postcard_list = []
        for uprn in uprn_list:
            # Creates a Postcard object for each UPRN
            postcard = build_postcard(CONN, uprn)
            postcard_list.append(postcard)
        out_paths = build_all_images(postcard_list, uprn_list)
        status = append_pdfs(out_paths, uprn_list)
        print(status)

    CONN.close()
