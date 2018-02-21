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
    prop = Property('James Whitehead', '9 White Rose House', 'Ainderby Gardens', 'Northallerton', 'North Yorkshire', 'DL7 8GT')
    html = prop.build_html()
    prop.export_html(html)
