import pyodbc
import json
import textwrap
import os
from PIL import Image, ImageDraw, ImageFont, ImageOps
from PyPDF2 import PdfFileReader, PdfFileWriter


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
    """ Represents a collection calendar, detailing which bin is collected on which day on which week

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
    def __init__(self, ref_day, ref_week, recy_day, recy_week, gw_day, gw_week, gls_day, gls_week):
        dates = {
            'Monday': 7,
            'Tuesday': 8,
            'Wednesday': 9,
            'Thursday': 10,
            'Friday': 11
        }
        # Represents the text that will be shown for each collection
        self.ref_string = '{} {}, {} May'.format(ref_day, str(dates[ref_day]), str(dates[ref_day] + 14))
        self.recy_string = '{} {}, {} May'.format(recy_day, str(dates[recy_day]), str(dates[recy_day] + 14))
        if gw_day == '-':
            self.gw_string = 'Not collected'
        else:
            self.gw_string = '{} {}, {} May'.format(gw_day, str(dates[gw_day]), str(dates[gw_day] + 14))
        self.gls_string = '{} {}, {} May'.format(gls_day, str(dates[gls_day]), str(dates[gls_day] + 14))


class TextBox:
    """ Represents an image to hold some collection data text in

    Args:
        text_image (obj:PIL.Image.Image): An image containing the text
        x_coord(int): How far along the x co-ordinate the text box should be placed on the base image
        y_coord(int): How far along the y co-ordinate the text box should be placed on the base image
        x_offset(int): How far along the x co-ordinate the base image itself is (calculated based on position)
        y_offset(int): How far along the y co-ordinate the base image itself is (calculated based on position)
    """
    def __init__(self, text_image, x_coord, y_coord, position):
        self.text_image = text_image
        self.x_coord = x_coord
        self.y_coord = y_coord
        # Top left
        if position == 0:
            self.x_offset = 0
            self.y_offset = 0
        # Top right
        if position == 1:
            self.x_offset = 2480
            self.y_offset = 0
        # Bottom left
        if position == 2:
            self.x_offset = 0
            self.y_offset = 1754
        # Bottom right
        if position == 3:
            self.x_offset = 2480
            self.y_offset = 1754


def build_postcard(conn, uprn):
    """ Creates a Postcard object for a property

    Args:
        conn (obj:pyodbc.Connection): An open pyodbc database connection object
        uprn (str): A UPRN (Unique Property Reference Number) to look up on the database

    Returns:
        (obj:Postcard): A Postcard object containing the address and calendar data
    """
    cursor = conn.cursor()
    with open('./cal_query.sql', 'r') as query_file:
        query = query_file.read()
        # Runs the SQL query to return an address block and collection information associated with a UPRN
        cursor.execute(query, uprn)
        row = cursor.fetchone()
        # Builds a Calendar object based on the collection information
        cal_obj = Calendar(
            row.REFDay, row.REFWeek, row.RECYDay, row.RECYWeek, row.GWDay, row.GWWeek, row.RECYDay, row.RECYWeek)
        # Builds a Postcard object based on the address and collection calendar
        post_obj = Postcard(row.addressBlock, cal_obj)

        # Cleans up leftover cursors
        cursor.close()
        del cursor

        return post_obj


def build_all_images(postcard_list, uprn_list):
    """ Given a list of four postcards and UPRNs, pastes text boxes on to each bin section in each card and saves as PDF

    Args:
        postcard_list(list:Postcard): A list of four (or less) Postcard objects
        uprn_list(list:str): An equivalent list of four (or less) UPRNs

    Returns:
        (list:str) A list of the file paths for the two created PDFs
    """
    addr_img = Image.open('./in/postcard-front-4x4.png')
    cal_img = Image.open('./in/postcard-back-4x4.png')
    addr_img.load()
    cal_img.load()

    for position, postcard in enumerate(postcard_list):
        # Position is based on the index in the postcard_list
        text_boxes = build_one_image(postcard, position)
        # Overlays each box on to the image
        for text_box in text_boxes:
            cal_img.paste(ImageOps.colorize(
                text_box.text_image, (255, 255, 255), (255, 255, 255)),
                ((text_box.x_coord + text_box.x_offset), (text_box.y_coord + text_box.y_offset)), text_box.text_image)

        address = build_address(postcard, 220, 610, position)
        addr_img.paste(ImageOps.colorize(
            address.text_image, (0, 0, 0), (0, 0, 0)),
            ((address.x_coord + address.x_offset), (address.y_coord + address.y_offset)), address.text_image)

    addr_file = './out/addr-{}.pdf'.format('-'.join(uprn_list))
    cal_file = './out/cal-{}.pdf'.format('-'.join(uprn_list))

    addr_img.save(addr_file, 'PDF', resolution=100.0, quality=100)
    cal_img.save(cal_file, 'PDF', resolution=100.0, quality=100)

    return [addr_file, cal_file]


def build_one_image(postcard, position):
    """ Given a single postcard, creates the strings and calls buiild_text to create the four text boxes for each bin

    Args:
        postcard(obj:Postcard): A Postcard object used to get the string data
        position: The position [top-left, top-right, bottom-left, bottom-right] of this postcard in the image

    Returns:
        (list:obj:TextBox): A list of the four TextBox objects used in each calendar image
    """
    # Wraps the strings over separate lines
    ref_string = textwrap.wrap(postcard.calendar.ref_string, width=9)
    recy_string = textwrap.wrap(postcard.calendar.recy_string, width=9)
    gw_string = textwrap.wrap(postcard.calendar.gw_string, width=9)
    gls_string = textwrap.wrap(postcard.calendar.gls_string, width=12)

    # Creates the text boxes
    ref_text = build_text(ref_string, 260, 350, 285, 890, position, 4)
    recy_text = build_text(recy_string, 260, 350, 860, 890, position, 4)
    gw_text = build_text(gw_string, 260, 350, 2000, 890, position, 4)
    # Glass box is unused by most postcards - need to add a special flag for the properties that are
    gls_text = build_text(gls_string, 0, 0, 0, 0, position, 2)
    # gls_text = build_text(gls_string, 310, 180, 1420, 980, position, 2)

    # Returns the text boxes
    return [ref_text, recy_text, gw_text, gls_text]


def build_text(string, width, height, x_coord, y_coord, position, rotation):
    """ Creates a text box to be overlaid on to a single bin in the overall image

    Args:
        string(str): The string contained in the text box
        width(int): The width of the text box (pixels)
        height(int): The height of the text box (pixels)
        x_coord(int): The x co-ordinate of the top-left corner of the text box on the single image (pixels)
        y_coord(int): The y co-ordinate of the top-left corner of the text box on the single image (pixels)
        position(int): The position of the single image in the overall image
        rotation(int): The angular rotation to draw the text box at (degrees)

    Returns:
        (obj:TextBox): A TextBox object containing the collection days
    """
    cal_font = ImageFont.truetype('futura bold condensed italic bt.ttf', 57)

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
        w, h = text_draw.textsize(line, font=cal_font)
        # Writes the text to the box using the width and height so it's centre aligned
        text_draw.text(((250 - w) / 2, curr_h), line, font=cal_font, fill=255)
        # Move the height cursor down
        curr_h += h + pad

    # Rotates the box
    return TextBox(text_box.rotate(rotation, resample=Image.BICUBIC, expand=True), x_coord, y_coord, position)


def build_address(postcard, x_coord, y_coord, position):
    """ Creates a text box to contain the address of a property

    Args:
        postcard(obj:Postcard): A Postcard object used to get the address data
        x_coord(int): The x co-ordinate of the top-left corner of the text box on the single image (pixels)
        y_coord(int): The y co-ordinate of the top-left corner of the text box on the single image (pixels)
        position(int): The position of the single image in the overall image

    Returns:
        (obj:TextBox): A TextBox containing the address of the property
    """
    addr_font = ImageFont.truetype('arial.ttf', 120)

    # Changes HTML line break to Python line break
    addr_string = (postcard.address).replace('<br>', '\n')
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
    conn_data = DatabaseConn()
    conn = pyodbc.connect(
        driver=conn_data.driver,
        server=conn_data.server,
        database=conn_data.database,
        uid=conn_data.uid,
        pwd=conn_data.pwd
    )

    # Lists of UPRNs are split into four, one for each corner of the 4x4 A3 sheet
    uprn_lists = [['010001279831', '100050380169', '100050359718', '010001285090'], ['100050370512', '100050366002', '010001286067']]
    for uprn_list in uprn_lists:
        postcard_list = []
        for uprn in uprn_list:
            # Creates a Postcard object for each UPRN
            postcard = build_postcard(conn, uprn)
            postcard_list.append(postcard)
        paths = build_all_images(postcard_list, uprn_list)
        status = append_pdfs(paths, uprn_list)
        print(status)

    conn.close()
