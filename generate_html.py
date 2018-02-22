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
    with open('./out/template-front.html', 'r') as address_file:
        address_page = address_file.readlines()
        address_page[10] = '\t\t\t\t{}\n'.format(prop_obj.address)
    with open('./out/template-back.html', 'r') as calendar_file:
        calendar_page = calendar_file.readlines()
        calendar_page[14] = '\t\t\t\t\t\t\t\t<span>{}</span>\n'.format(prop_obj.calendar.refDay)
        calendar_page[16] = '\t\t\t\t\t\t\t<p class="week">{}</p>\n'.format(prop_obj.calendar.refWeek)
        calendar_page[23] = '\t\t\t\t\t\t\t\t<span>{}</span>\n'.format(prop_obj.calendar.recyDay)
        calendar_page[25] = '\t\t\t\t\t\t\t<p class="week">{}</p>\n'.format(prop_obj.calendar.recyWeek)
        calendar_page[32] = '\t\t\t\t\t\t\t\t<span>{}</span>\n'.format(prop_obj.calendar.gwDay)
        calendar_page[34] = '\t\t\t\t\t\t\t<p class="week">{}</p>\n'.format(prop_obj.calendar.gwWeek)
        calendar_page[41] = '\t\t\t\t\t\t\t\t<span>{}</span>\n'.format(prop_obj.calendar.glsDay)
        calendar_page[43] = '\t\t\t\t\t\t\t<p class="week">{}</p>\n'.format(prop_obj.calendar.glsWeek)
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
    uprns = ['010001279831','100050380169','100050359718','010001285090','100050370512','100050366002','010001286067']
    for uprn in uprns:
        waste_property = build_waste_property(conn, uprn)
        build_html(waste_property, uprn)
