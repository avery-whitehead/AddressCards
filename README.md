# AddressCards

Generates some postcards about bin collection data using data from the Local Land and Property Gazetteer (LLPG).

## How to run

The program doesn't take any command line arguments, so it can be run however you would run a Python 3 script:

If Python 3 is the only environment installed:

* `python .\generate_multi_image.py`

If Python 2 is installed as well and you're using some variant of the Windows launcher:

* `python3 .\generate_multi_image.py`

* `py -3 .\generate_multi_image.py`

## How it works

1. get_uprns() returns a list of Unique Property Reference Numbers (UPRNs) used to identify each property that bins are collected from.
2. The list of UPRNs is split into sublists of four UPRNs each, because the generated postcards are four A5 cards in a grid on an A3 (or SRA3) sheet.
3. For each single UPRN in a list of four, a Calendar object and an Address object are created. A Calendar object contains the data for when the bins are collected, and the Address object contains the address data for the property.
4. A CalendarImage object and AddressImage object are created using the Calendar and Address objects. The attributes calendar_image and address_image are PIL.Image types from the Pillow imaging library. The attributes calendar and address are the parent Calendar and Address objects. This creates a list of four CalendarImages and four AddressImages.
5. The eight images are arranged in a grid into a CalendarSide and an AddressSide themselves being PIL.Image tyoes, which are saved as two separate JPEG images.
6. The images are converted into PDFs and merged together into groups of 150.

## Notes for the future

Assuming the data follows the same format as these SQL queries, this program should be very extensible for use in the future. There may be a few caveats and important things to note, however:

* This was written in Python 3.6.4 using Pillow 5.0.0. It won't work on Python 2, but should be simple enough to work on any future versions.
* The centring of text on the bins is _really_ awkward. Pillow has no concept of centre-aligning text, so each string has to be split into separate lines using textwrap.wrap(), and the width of each line needs to be calculated so the text can be placed relative to each other so it's 'centred'. The string splits nicely into lines of 7 characters, but if the string changes in the future, this value might have to change.
* The program takes about five hours to process 5000 UPRNs and doesn't handle crashes gracefully. Crashes can be caused by unexpected NULLs in the SQL results or by the SQL server itself going down, as well as anything happening locally on the machine running it. Leave plenty of time spare to produce things.
* The template images may need to be converted from the CMYK colour space to RGB if the colours look too bright. A good place to do this is here https://www.cmyk2rgb.com/
* This could be a lot more nicely object-oriented, but as it stands, CalendarSide and AddressSide are annoyingly separate. Any changes that need to be made to both sides will need to be made in both sides.
* This doesn't generate different images for properties that have their recycling bins and glass recycling bins collected on different days. This may be needed for a later batch. Some of the very basic templates are there, but don't actually do anything.
* Powershell sometimes gets stuck while running it. I don't know why, and it's not great, so you'll have to keep an eye on it and tap a key to get it running again.