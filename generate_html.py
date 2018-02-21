import pyodbc

class WasteProperty:
    def __init__(self, address, calendar):
        self.address = address
        self.calendar = calendar

class Property:
    def __init__(self, name, firstAddr, secondAddr, town, county, postcode, uprn, calendar):
        self.name = name.strip()
        self.firstAddr = firstAddr.strip()
        self.secondAddr = secondAddr.strip()
        self.town = town.strip()
        self.county = county.strip()
        self.postcode = postcode.strip()
        self.uprn = uprn
        self.calendar = calendar

    # Loads and fills in the HTML template
    def build_html(self):
        with open('./out/template.html', 'r') as html_file:
            html = html_file.readlines()
        # Fills in the address values
        line = 10
        for attr, value in vars(self).items():
            if attr != 'uprn' and attr != 'calendar':
                html[line] = '\t\t\t\t{}<br>\n'.format(value)
                line += 1
        # Fills in the calendar values
        html[25] = '\t\t\t\t\t\t\t\t<span>{}</span>\n'.format(self.calendar.refDay)
        html[27] = '\t\t\t\t\t\t\t<p class="week">Week {}</p>\n'.format(self.calendar.refWeek)
        html[34] = '\t\t\t\t\t\t\t\t<span>{}</span>\n'.format(self.calendar.recyDay)
        html[36] = '\t\t\t\t\t\t\t<p class="week">Week {}</p>\n'.format(self.calendar.recyWeek)
        html[44] = '\t\t\t\t\t\t\t\t<span>{}</span>\n'.format(self.calendar.gwDay)
        html[46] = '\t\t\t\t\t\t\t<p class="week">Week {}</p>\n'.format(self.calendar.gwWeek)
        return html

    # Saves the HTML template to a file
    def export_html(self, html):
        file_name = './out/{}.html'.format(self.uprn)
        with open(file_name, 'w+') as out_file:
            out_file.write(''.join(html))

class Calendar:
    def __init__(self, refDay, refWeek, recyDay, recyWeek, gwDay, gwWeek, glsDay, glsWeek):
        self.refDay = refDay
        self.refWeek = refWeek
        self.recyDay = recyDay
        self.recyWeek = recyWeek
        self.gwDay = gwDay
        self.gwWeek = gwWeek
        self.glsDay = glsDay
        self.glsWeek = glsWeek

def build_waste_property(conn, uprn):
    cursor = conn.cursor()
    with open ('./cal_query.sql', 'r') as query_file:
        query = query_file.read()
        cursor.execute(query, uprn)
        row = cursor.fetchone()
        cal_obj = Calendar(row.REFDay, row.REFWeek, row.RECYDay, row.RECYWeek, row.GWDay, row.GWWeek, row.RECYDay, row.RECYWeek)
        prop_obj = WasteProperty(row.addressBlock, cal_obj)
        return prop_obj

def build_html(prop_obj, uprn):
    with open('./out/template.html', 'r') as html_file:
        html = html_file.readlines()
        html[10] = '\t\t\t\t{}\n'.format(prop_obj.address)
        html[20] = '\t\t\t\t\t\t\t\t<span>{}</span>\n'.format(prop_obj.calendar.refDay)
        html[22] = '\t\t\t\t\t\t\t<p class="week">{}</p>\n'.format(prop_obj.calendar.refWeek)
        html[29] = '\t\t\t\t\t\t\t\t<span>{}</span>\n'.format(prop_obj.calendar.recyDay)
        html[31] = '\t\t\t\t\t\t\t<p class="week">{}</p>\n'.format(prop_obj.calendar.recyWeek)
        html[39] = '\t\t\t\t\t\t\t\t<span>{}</span>\n'.format(prop_obj.calendar.gwDay)
        html[41] = '\t\t\t\t\t\t\t<p class="week">{}</p>\n'.format(prop_obj.calendar.gwWeek)
        html[48] = '\t\t\t\t\t\t\t\t<span>{}</span>\n'.format(prop_obj.calendar.glsDay)
        html[50] = '\t\t\t\t\t\t\t<p class="week">{}</p>\n'.format(prop_obj.calendar.glsWeek)
    out_name = './out/{}.html'.format(uprn)
    with open(out_name, 'w+') as out_file:
        out_file.write(''.join(html))

def build_calendar(conn, uprn):
    cal_curs = conn.cursor()
    # Retrieves waste calendar information
    with open('./cal_query.sql', 'r') as query_file:
        query = query_file.read()
        cal_curs.execute(query, uprn)
        cal = cal_curs.fetchone()
        cal_obj = Calendar(cal.REFDay, cal.REFWeek, cal.RECYDay, cal.RECYWeek, cal.GWDay, cal.GWWeek, None, None)
        cal_curs.close()
        del cal_curs
        conn.close()
        return cal_obj

def build_property(conn, uprn, cal_obj):
    # Gets name associated with UPRN
    name_curs = conn.cursor()
    name_curs.execute("SELECT TOP 1 SURNAME FROM dbo.FOLDER1 WHERE FOLDER3_REF = '{}'".format(uprn))
    name = name_curs.fetchone()
    # Gets property associated with UPRN
    prop_curs = conn.cursor()
    prop_curs.execute("SELECT PAO, STREET, TOWN, COUNTY, POSTCODE FROM dbo.FOLDER3 WHERE FOLDER3_REF = '{}'".format(uprn))
    prop = prop_curs.fetchone()
    prop_obj = Property(name.SURNAME, prop.PAO, prop.STREET, prop.TOWN, prop.COUNTY, prop.POSTCODE, uprn, cal_obj)
    prop_curs.close()
    del prop_curs
    name_curs.close()
    del name_curs
    conn.close()
    return prop_obj

if __name__ == '__main__':
    pyodbc.pooling = False
    conn = pyodbc.connect(
        r'DRIVER={ODBC Driver 13 for SQL Server};'
        r'SERVER=CCVSQL12;'
        r'DATABASE=WaSSCollections;'
        r'UID=af_WaSSCollections_rw;'
        r'PWD=o~W\,W3tF%\~zz03'
    )
    uprns = ['010001279831','100050380169','100050359718','010001285090','100050370512','100050366002','010001286067']
    for uprn in uprns:
        waste_property = build_waste_property(conn, uprn)
        build_html(waste_property, uprn)
