from os import listdir
from PyPDF2 import PdfFileWriter, PdfFileReader
pdf_dir = 'C:/Program Files/wkHTMLtoPDF/bin'
# Get a list of generated PDFs
pdfs = [f for f in listdir(pdf_dir) if f.endswith('.pdf')]
for pdf in pdfs:
    pdf_path = '{}/{}'.format(pdf_dir, pdf)
    in_pdf = PdfFileReader(pdf_path, 'rb')
    output = PdfFileWriter()

    output.addPage(in_pdf.getPage(0))
    output.addPage(in_pdf.getPage(2))

    out_path = './pdfs/{}'.format(pdf)
    with open(out_path, 'wb') as out_f:
        output.write(out_f)
