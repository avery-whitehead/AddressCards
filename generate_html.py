import pyodbc
import json

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
        ref_day (str): The day normal refuse bins are collected
        ref_week (str): The week normal refuse bins are collected
        recy_day (str): The day recycling bins are collected
        recy_week (str): The week recycling bins are collected
        gw_day (str): The day garden waste bins are collected
        gw_week (str): The week garden waste bins are collected
        gls_day (str): The day glass refuse bins are collected
        gls_week (str): The week glass refuse bins are collected
    """
    def __init__(self, ref_day, ref_week, recy_day, recy_week, gw_day, gw_week, gls_day, gls_week):
        dates = {
            'Monday': 7,
            'Tuesday': 8,
            'Wednesday': 9,
            'Thursday': 10,
            'Friday': 11
        }
        # Strings representing the text that will be shown for each collection
        self.ref_string = '{}<br>{}, {}<br>May'.format(ref_day, str(dates[ref_day]), str(dates[ref_day] + 14))
        self.recy_string = '{}<br>{}, {}<br>May'.format(recy_day, str(dates[recy_day]), str(dates[recy_day] + 14))
        if gw_day == '-':
            self.gw_string = 'Not<br>collected'
        else:
            self.gw_string = '{}<br>{}, {}<br>May'.format(gw_day, str(dates[gw_day]), str(dates[gw_day] + 14))
        self.gls_string = '{}<br>{}, {} May'.format(gls_day, str(dates[gls_day]), str(dates[gls_day] + 14))

def build_postcard(conn, uprn):
    """ Creates a Postcard object for a property

    Args:
        conn (:obj:pyodbc.Connection): An open pyodbc database connection object
        uprn (str): A UPRN (Unique Property Reference Number) to look up on the database
    """
    cursor = conn.cursor()

    with open ('./cal_query.sql', 'r') as query_file:
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

def build_html(post_obj, uprn):
    """ Fills in the HTML templates with the address and calendar

    Args:
        post_obj (:obj:Postcard): A Postcard object associated with a property, contains address and calendar information
        uprn (str): A UPRN (Unique Property Reference Number) used to name the output file
    """
    # Creates a list of the attribute values in the Calendar object
    attrs = list(post_obj.calendar.__dict__.values())
    # Formats of HTML lines for address block, collection day and collection week
    addr_format = '\t\t<div class="address">{}</div>\n'

    with open('./out/template-front.html', 'r') as address_file:
        # Fills in the address information on the correct HTML lines
        address_page = address_file.readlines()
        address_page[25] = '\t\t<div class="address">{}</div>\n'.format(post_obj.address)

    with open('./out/template-back.html', 'r') as calendar_file:
        calendar_page = calendar_file.readlines()
        # Fills in the collection information on the correct HTML lines
        calendar_page[60] = '\t\t\t\t{}\n'.format(post_obj.calendar.ref_string)
        calendar_page[65] = '\t\t\t\t{}\n'.format(post_obj.calendar.recy_string)
        calendar_page[70] = '\t\t\t\t{}\n'.format(post_obj.calendar.gls_string)
        calendar_page[75] = '\t\t\t\t{}\n'.format(post_obj.calendar.gw_string)

    address_out_name = './out/{}-addr.html'.format(uprn)
    calendar_out_name = './out/{}-cal.html'.format(uprn)
    with open(address_out_name, 'w+') as address_out:
        address_out.write(''.join(address_page))
    with open(calendar_out_name, 'w+') as calendar_out:
        calendar_out.write(''.join(calendar_page))

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

    uprns = ['010001279831','100050380169','100050359718','010001285090','100050370512','100050366002','010001286067']
    for uprn in uprns:
        postcard = build_postcard(conn, uprn)
        build_html(postcard, uprn)

    conn.close()
