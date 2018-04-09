# AddressCards
Generates some postcards using some LLPG data.  
Looks up some address and collection details and uses Pillow to write this on to a template

### How to run
In the AddressCards directory:  
`py -3 .\generate_image.py`

Wow!  
![output](https://i.imgur.com/QDF59iD.jpg)

### Changing positions of text boxes
Because I'm going to have to change them and I'll probably forget.  
The four calls to `build_text()` in `build_one_image()` specify the dimensions and co-ordinates of the box in the parameter, in  
the order `box width, box height, x co-ordinate, y co-ordinate`
