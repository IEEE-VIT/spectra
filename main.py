from pynput import keyboard
from pynput import mouse
from PIL import Image, ImageGrab

# These are the dependencies we will be using, we use pynput to record the input from either the mouse or the keyboard,
# The cursor coordinates are used to capture the pixel the cursor is resting on, and whether or not the mouse has been clicked.

hexColor = "-1"
rgbColor = "-1"

# Function to get the hex code value which takes a tuple containing the red,green,blue values from 0-255.
def getHex(rgb):
    global hexColor
    hexColor = '%02x%02x%02x' % rgb

# The getColor function accepts 2 arguments, 1 x coordinate, 1 y coordinate, we capture or "grab" an image,
# and based on the x-y coordinates we get the color at that particular pixel. 
def getColor(x,y):
    coor = x,y
    rgb = ImageGrab.grab().getpixel(coor)
    global rgbColor
    rgbColor = rgb
    return rgb

# Function to record whether or not the mouse has been clicked, takes x, y coordinates as arguments,
#  and button specifies which particular botton is pressed(in our case, it would be 'right click'),
#  and press is a boolean indicating if it has been pressed or not.
def onClick(x,y,button,press):
    if press and button == mouse.Button.right:
        getHex(getColor(x,y))

# Since we cannot keep the script running all the time,
#  and it will only tell us the value of the color if we press the close button,
#  we'll need to code an exit in some way. So we use a capslock on the keyboard to terminate the program.
def onRel(key):
    if key == keyboard.Key.caps_lock:
        if hexColor != "-1" and rgbColor != "-1":
            print("Hex value -> #{0}".format(hexColor))
            print("RGB value -> rgb{0}".format(rgbColor))
        k.stop()
        m.stop()


# Make the listener to listen for keyboard, mouse inputs.
with keyboard.Listener(on_release=onRel) as k:
    with mouse.Listener(on_click=onClick) as m:
        k.join()
        m.join()    
