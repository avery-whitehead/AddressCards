import pyodbc

class Property:
    def __init__(self, name, firstAddr, secondAddr, town, county, postcode, uprn):
        self.name = name
        self.firstAddr = firstAddr
        self.secondAddr = secondAddr
        self.town = town
        self.county = county
        self.postcode = postcode
        self.uprn = uprn

    # Loads and fills in the HTML template
    def build_html(self):
        with open('./out/template.html', 'r') as html_file:
            html = html_file.readlines()
        line = 10
        for attr, value in vars(self).items():
            if attr != 'uprn':
                html[line] = '\t\t\t\t{}<br>\n'.format(value)
                line += 1
        return html

    # Saves the HTML template to a file
    def export_html(self, html):
        file_name = './out/{}.html'.format(self.uprn.strip())
        with open(file_name, 'w+') as out_file:
            out_file.write(''.join(html))

if __name__ == '__main__':
    # Connects to SQL Server
    conn = pyodbc.connect(
        r'DRIVER={ODBC Driver 13 for SQL Server};'
        r'SERVER=CCVSQL12\SQLInstance2;'
        r'DATABASE=Images;'
        r'UID=PACommentAutomation;'
        r'PWD=T5b}rh~Dq<kY2'
    )

    # Gets name and UPRN
    uprn_curs = conn.cursor()
    uprn_curs.execute("SELECT TOP 1 SURNAME, FOLDER3_REF AS UPRN FROM dbo.FOLDER1 WHERE FOLDER1_REF2 LIKE '%_%'")
    uprns = uprn_curs.fetchall()
    for uprn in uprns:
        # Gets property associated with UPRN
        prop_curs = conn.cursor()
        prop_curs.execute("SELECT PAO, STREET, TOWN, COUNTY, POSTCODE FROM dbo.FOLDER3 WHERE FOLDER3_REF = '{}'".format(uprn.UPRN))
        props = prop_curs.fetchall()
        # Builds property object
        for prop in props:
            prop_obj = Property(uprn.SURNAME, prop.PAO, prop.STREET, prop.TOWN, prop.COUNTY, prop.POSTCODE, uprn.UPRN)
            html = prop_obj.build_html()
            prop_obj.export_html(html)
        # Cleans up connections
        prop_curs.close()
        del prop_curs
    uprn_curs.close()
    del uprn_curs
    conn.close()
