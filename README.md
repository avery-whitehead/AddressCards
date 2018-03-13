# AddressCards
Generates some postcards using some LLPG data.

Looks up some address and collection details and fills in an HTML template with these values.

Attempts to make a nice-looking A5 pdf from the HTML.

### How to run
In the AddressCards directory, to create the webpages:

`py -3 .\generate_html.py`

In the wkHTMLtoPDF directory, to convert the webpages to PDFs:

`.\auto_pdf.ps1`

In the AddressCards directory, to remove blank pages from the PDFs:

`py -3 .\trim_pdf.py`

Final PDF files are put in the PDF directory and named after their UPRN.
