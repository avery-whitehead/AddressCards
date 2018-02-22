import pyodbc

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
        Potential day values: Mon, Tue, Wed, Thu, Fri.
        Potential week values: 1, 2.
        Recycling bin days/weeks and glass bin days/weeks are often the same

    Args:
        refDay (str): The day normal refuse bins are collected
        refWeek (str): The week normal refuse bins are collected
        recyDay (str): The day recycling bins are collected
        recyWeek (str): The week recycling bins are collected
        gwDay (str): The day garden waste bins are collected
        gwWeek (str): The week garden waste bins are collected
        glsDay (str): The day glass refuse bins are collected
        glsWeek (str): The week glass refuse bins are collected
    """
    def __init__(self, refDay, refWeek, recyDay, recyWeek, gwDay, gwWeek, glsDay, glsWeek):
        self.refDay = refDay
        self.refWeek = refWeek
        self.recyDay = recyDay
        self.recyWeek = recyWeek
        self.gwDay = gwDay
        self.gwWeek = gwWeek
        self.glsDay = glsDay
        self.glsWeek = glsWeek

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
    addr_format = '\t\t\t\t{}\n'
    day_format = '\t\t\t\t\t\t\t\t<span>{}</span>\n'
    week_format = '\t\t\t\t\t\t\t<p class="week">{}</p>\n'

    with open('./out/template-front.html', 'r') as address_file:
        address_page = address_file.readlines()
        address_page[10] = addr_format.format(post_obj.address)

    with open('./out/template-back.html', 'r') as calendar_file:
        calendar_page = calendar_file.readlines()
        # Fills in the day and week information on the correct HTML lines
        line = 14
        for i in range(0, len(attrs), 2):
            calendar_page[line] = day_format.format(attrs[i])
            # Week line is two lines after day line
            calendar_page[line + 2] = week_format.format(attrs[i + 1])
            # Next day line is nine lines after previous day line
            line += 9

    address_out_name = './out/{}-addr.html'.format(uprn)
    calendar_out_name = './out/{}-cal.html'.format(uprn)
    with open(address_out_name, 'w+') as address_out:
        address_out.write(''.join(address_page))
    with open(calendar_out_name, 'w+') as calendar_out:
        calendar_out.write(''.join(calendar_page))

if __name__ == '__main__':
    pyodbc.pooling = False

    conn = pyodbc.connect(
        r'DRIVER={ODBC Driver 13 for SQL Server};'
        r'SERVER=CCVSQL12;'
        r'DATABASE=WaSSCollections;'
        r'UID=af_WaSSCollections_rw;'
        r'PWD=o~W\,W3tF%\~zz03'
    )

    uprns = ['010001285090']
    for uprn in uprns:
        postcard = build_postcard(conn, uprn)
        build_html(postcard, uprn)

    conn.close()
