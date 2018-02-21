import pyodbc

class Property:
    def __init__(self, name, firstAddr, secondAddr, town, county, postcode):
        self.name = name
        self.firstAddr = firstAddr
        self.secondAddr = secondAddr
        self.town = town
        self.county = county
        self.postcode = postcode

    # Loads and fills in the HTML template
    def build_html(self):
        with open('./out/template.html', 'r') as html_file:
            html = html_file.readlines()
        line = 10
        for attr, value in vars(self).items():
            html[line] = '\t\t\t\t' + value + '<br>\n'
            line += 1
        return html

    # Saves the HTML template to a file
    def export_html(self, html):
        file_name = './out/' + self.name + '.html'
        with open(file_name, 'w+') as out_file:
            out_file.write(''.join(html))

if __name__ == '__main__':
    # Connect to SQL Server
    conn = pyodbc.connect(
        r'DRIVER={ODBC Driver 13 for SQL Server};'
        r'SERVER=CCVSQL12\SQLInstance2;'
        r'DATABASE=Images;'
        r'UID=PACommentAutomation;'
        r'PWD=T5b}rh~Dq<kY2'
    )

    # Execute and read SQL query
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM dbo.FOLDER3 WHERE FOLDER3_REF = '010001280513'")
    rows = cursor.fetchall()
    for item in rows[0]:
        print(item)

    # Create Property objects
    prop = Property('James Whitehead', '9 White Rose House', 'Ainderby Gardens', 'Northallerton', 'North Yorkshire', 'DL7 8GT')
    html = prop.build_html()
    prop.export_html(html)
