import pyodbc
import json
import textwrap
from PIL import Image, ImageDraw, ImageFont, ImageOps
from enum import Enum


class DatabaseConn:
    """ Represents a pyodbc connection string. Reads the attributes from a config file.
    """
    def __init__(self):
        with open('generate_html.config') as config_file:
            config = json.load(config_file)
            self.driver = config['driver']
            self.server = config['server']
            self.database = config['database']
            self.uid = config['uid']
            self.pwd = config['pwd']


class Postcard:
    """ Represents a postcard, with an address on one side and calendar on the other.

    Args:
        address (str): An address block, each line separated with HTML <br> tags
        calendar (:obj:Calendar): A Calendar object containing collection information
    """
    def __init__(self, address, calendar):
        self.address = address
        self.calendar = calendar


class Calendar:
    """ Represents a collection calendar, detailing which bin is collected on which day on which week.

    Note:
        Potential day values: Monday, Tuesday, Wednesday, Thursday, Friday.
        Potential week values: 1, 2.
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
    """ Represents an image to hold some collection data in.

    Args:
        text_image (:obj:PIL.Image.Image): An image containing the text
        x_offset(int): How far along the x-coordinate the base image is
        y_offset(int): How far along the y-coordinate the base image is
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
        conn (:obj:pyodbc.Connection): An open pyodbc database connection object
        uprn (str): A UPRN (Unique Property Reference Number) to look up on the database
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
    addr_img = Image.open('./out/postcard-front-4x4.png').convert('RGBA')
    cal_img = Image.open('./out/postcard-back-4x4.png').convert('RGBA')
    addr_img.load()
    cal_img.load()
    for position, postcard in enumerate(postcard_list):
        text_boxes = build_one_image(postcard, position)
        #print('Image: {}\nX: {}\nY: {}\nX (with offset):{}\nY (with offset){}'.format(
            #text_box.text_image, text_box.x_coord, text_box.y_coord, text_box.x_coord + text_box.x_offset, text_box.y_coord + text_box.y_offset))
        # Overlays the rotated box on to the image
        for text_box in text_boxes:
            cal_img.paste(ImageOps.colorize(
                text_box.text_image, (0, 0, 0), (255, 255, 255)),
                ((text_box.x_coord + text_box.x_offset), (text_box.y_coord + text_box.y_offset)), text_box.text_image)
    out_file = '{}.png'.format('-'.join(uprn_list))
    cal_img.save(out_file)


def build_one_image(postcard, position):
    # Wraps the strings over separate lines
    ref_string = textwrap.wrap(postcard.calendar.ref_string, width=9)
    recy_string = textwrap.wrap(postcard.calendar.recy_string, width=9)
    gw_string = textwrap.wrap(postcard.calendar.gw_string, width=9)
    gls_string = textwrap.wrap(postcard.calendar.gls_string, width=12)

    # Creates the text boxes
    ref_text = build_text(ref_string, 260, 350, 250, 890, position, 4)
    recy_text = build_text(recy_string, 260, 350, 860, 890, position, 4)
    gw_text = build_text(gw_string, 260, 350, 2000, 890, position, 4)
    gls_text = build_text(gls_string, 310, 180, 1420, 980, position, 2)

    return [ref_text, recy_text, gw_text, gls_text]


def build_text(string, width, height, x_coord, y_coord, position, rotation):
    addr_font = ImageFont.truetype('arial.ttf', 60)
    cal_font = ImageFont.truetype('futura bold condensed italic bt.ttf', 57)
    # Creates a box to hold the text in
    text_box = Image.new('L', (width, height))
    text_draw = ImageDraw.Draw(text_box)
    # The current height in the box
    curr_h = 50
    # The padding between lines
    pad = 10
    for line in string:
        # Calculates the width and height of each line
        w, h = text_draw.textsize(line, font=cal_font)
        # Writes the text to the box using the width and height so it's centre aligned
        text_draw.text(((250 - w) / 2, curr_h), line, font=cal_font, fill=255)
        # Move the height cursor down
        curr_h += h + pad
    # Rotates the box
    return TextBox(text_box.rotate(rotation, resample=Image.BICUBIC, expand=True), x_coord, y_coord, position)


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

    uprn_lists = [['010001279831', '100050380169', '100050359718', '010001285090'], ['100050370512', '100050366002', '010001286067']]
    for uprn_list in uprn_lists:
        postcard_list = []
        for uprn in uprn_list:
            postcard = build_postcard(conn, uprn)
            postcard_list.append(postcard)
        build_all_images(postcard_list, uprn_list)

    conn.close()
