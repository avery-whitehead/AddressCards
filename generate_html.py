import pyodbc

class WasteProperty:
    def __init__(self, address, calendar):
        self.address = address
        self.calendar = calendar

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
        html[38] = '\t\t\t\t\t\t\t\t<span>{}</span>\n'.format(prop_obj.calendar.gwDay)
        html[40] = '\t\t\t\t\t\t\t<p class="week">{}</p>\n'.format(prop_obj.calendar.gwWeek)
        html[47] = '\t\t\t\t\t\t\t\t<span>{}</span>\n'.format(prop_obj.calendar.glsDay)
        html[49] = '\t\t\t\t\t\t\t<p class="week">{}</p>\n'.format(prop_obj.calendar.glsWeek)
    out_name = './out/{}.html'.format(uprn)
    with open(out_name, 'w+') as out_file:
        out_file.write(''.join(html))

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
