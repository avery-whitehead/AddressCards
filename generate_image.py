import pyodbc
import json
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
        self.ref_string = '{}\n{}, {}\nMay'.format(ref_day, str(dates[ref_day]), str(dates[ref_day] + 14))
        self.recy_string = '{}\n{}, {}\nMay'.format(recy_day, str(dates[recy_day]), str(dates[recy_day] + 14))
        if gw_day == '-':
            self.gw_string = 'Not\ncollected'
        else:
            self.gw_string = '{}\n{}, {}\nMay'.format(gw_day, str(dates[gw_day]), str(dates[gw_day] + 14))
        self.gls_string = '{}\n{}, {} May'.format(gls_day, str(dates[gls_day]), str(dates[gls_day] + 14))


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
        cal_obj = Calendar(row.REFDay, row.REFWeek, row.RECYDay, row.RECYWeek, row.GWDay, row.GWWeek, row.RECYDay, row.RECYWeek)
        # Builds a Postcard object based on the address and collection calendar
        post_obj = Postcard(row.addressBlock, cal_obj)

        # Cleans up leftover cursors
        cursor.close()
        del cursor
        return post_obj


def build_image(post_obj_list, uprn_list):
    class Positions(Enum):
        TOP_LEFT = 0
        TOP_RIGHT = 1
        BOTTOM_LEFT = 2
        BOTTOM_RIGHT = 3

    addr_font = ImageFont.truetype('arial.ttf', 60)
    cal_font = ImageFont.truetype('futura bold condensed italic bt.ttf', 62)

    addr_img = Image.open('./out/postcard-front-4x4.png').convert('RGBA')
    cal_img = Image.open('./out/postcard-back-4x4.png').convert('RGBA')

    for position, postcard in enumerate(post_obj_list):
        if position == Positions.TOP_LEFT.value:
            # Creates a box to hold the text in
            text_box = Image.new('L', (250, 330))
            text_draw = ImageDraw.Draw(text_box)
            # Writes the text to the box
            text_draw.text((0, 0), postcard.calendar.ref_string, font=cal_font, fill=255)
            # Rotates the box
            rotate = text_box.rotate(4, resample=Image.BICUBIC, expand=True)
            # Overlays the rotated box on to the image
            cal_img.paste(ImageOps.colorize(rotate, (0, 0, 0), (255, 255, 255)), (310, 890), rotate)

    cal_img.save('new.png')



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
        build_image(postcard_list, uprn_list)


    conn.close()
