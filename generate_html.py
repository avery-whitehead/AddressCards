import pyodbc

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

def build_calendar(conn, uprn):
    cal_curs = conn.cursor()
    # Retrieves waste calendar information
    cal_curs.execute("""
        select
           p.uprn
           ,replace(replace(l.ADDRESS_BLOCK_ORG,'North Yorkshire'+char(13)+char(10),''),char(13)+char(10),'<BR>') as addressBlock
           ,case
                  when ref.ScheduleDayID < 8 then 1
                  when ref.ScheduleDayID > 7 then 2
           end as REFWeek
           ,case
                  when ref.ScheduleDayID in (1,8) then 'Mon'
                  when ref.ScheduleDayID in (2,9) then 'Tue'
                  when ref.ScheduleDayID in (3,10) then 'Wed'
                  when ref.ScheduleDayID in (4,11) then 'Thu'
                  when ref.ScheduleDayID in (5,12) then 'Fri'
           end as REFDay
           ,case
                  when recy.ScheduleDayID < 8 then 1
                  when recy.ScheduleDayID > 7 then 2
           end as RECYWeek
           ,case
                  when recy.ScheduleDayID in (1,8) then 'Mon'
                  when recy.ScheduleDayID in (2,9) then 'Tue'
                  when recy.ScheduleDayID in (3,10) then 'Wed'
                  when recy.ScheduleDayID in (4,11) then 'Thu'
                  when recy.ScheduleDayID in (5,12) then 'Fri'
           end as RECYDay
           ,case
                  when gw.ScheduleDayID < 8 then 1
                  when gw.ScheduleDayID > 7 then 2
           end as GWWeek
           ,case
                  when gw.ScheduleDayID in (1,8) then 'Mon'
                  when gw.ScheduleDayID in (2,9) then 'Tue'
                  when gw.ScheduleDayID in (3,10) then 'Wed'
                  when gw.ScheduleDayID in (4,11) then 'Thu'
                  when gw.ScheduleDayID in (5,12) then 'Fri'
           end as GWDay
           from properties p
           join LLPG_ADDRESS_CURRENT_SPATIAL l
                         on p.uprn=l.uprn
           join (select * from PropertyServiceRounds where serviceid = 'REF' and RoundEra=2) psr_ref
                  on p.uprn=psr_ref.uprn
           left join (select * from rounds where serviceid = 'REF' and RoundEra=2)  ref
                  on psr_ref.RoundID=ref.RoundID
           join (select * from PropertyServiceRounds where serviceid = 'RECY' and RoundEra=2) psr_recy
                  on p.uprn=psr_recy.uprn
           left join (select * from rounds where serviceid = 'RECY' and RoundEra=2)  recy
                  on psr_recy.RoundID=recy.RoundID
           join (select * from PropertyServiceRounds where serviceid = 'GW' and RoundEra=2) psr_gw
                  on p.uprn=psr_gw.uprn
           left join (select * from rounds where serviceid = 'GW' and RoundEra=2)  gw
                  on psr_gw.RoundID=gw.RoundID
                  where p.uprn in (?) and psr_ref.RoundEra=2
    """, uprn)
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
    cal_conn = pyodbc.connect(
        r'DRIVER={ODBC Driver 13 for SQL Server};'
        r'SERVER=CCVSQL12;'
        r'DATABASE=WaSSCollections;'
        r'UID=af_WaSSCollections_rw;'
        r'PWD=o~W\,W3tF%\~zz03'
    )
    prop_conn = pyodbc.connect(
        r'DRIVER={ODBC Driver 13 for SQL Server};'
        r'SERVER=CCVSQL12\SQLInstance2;'
        r'DATABASE=Images;'
        r'UID=PACommentAutomation;'
        r'PWD=T5b}rh~Dq<kY2'
    )
    uprns = ['100050380169']
    for uprn in uprns:
        cal_obj = build_calendar(cal_conn, uprn)
        prop_obj = build_property(prop_conn, uprn, cal_obj)
        html = prop_obj.build_html()
        prop_obj.export_html(html)
