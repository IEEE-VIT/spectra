from PIL import Image, ImageGrab
from pynput import keyboard, mouse

# These are the dependencies we will be using, we use pynput to record the input from either the mouse or the keyboard,
# The cursor coordinates are used to capture the pixel the cursor is resting on, and whether or not the mouse has been clicked.

# Function to get the hex code value which takes a tuple containing the red,green,blue values from 0-255.
def getHex(rgb):
    output = ''
    
    for value in rgb :
        output += hex(value)[2:].upper().zfill(2)
        
    return output

# Function to convert hex code to RGB format
def hex_to_rgb(hexcode):
    # Remove the '#' if present
    hexcode = hexcode.lstrip('#')
    
    # Convert hex to RGB
    rgb = tuple(int(hexcode[i:i+2], 16) for i in (0, 2, 4))
    return rgb

# The getColor function accepts 2 arguments, 1 x coordinate, 1 y coordinate, we capture or "grab" an image,
# and based on the x-y coordinates we get the color at that particular pixel. 
def getColor(x,y):
    coor = x,y
    
    return ImageGrab.grab().getpixel(coor)

# Function to record whether or not the mouse has been clicked, takes x, y coordinates as arguments,
#  and button specifies which particular botton is pressed(in our case, it would be 'right click'),
#  and press is a boolean indicating if it has been pressed or not.
def onClick(x,y,button,press):
    # check if the pressed mouse button is the right button
    if button == mouse.Button.right and press:
        # get the color of the pixel at the coordinates x and y
        color = getColor(x, y)
        # convert the color (RGB format) into a hexadecimal representation.
        hex_color = getHex(color)
        print(f"Color at mouse click (x={x}, y={y}): #{hex_color}")

# Since we cannot keep the script running all the time,
#  and it will only tell us the value of the color if we press the close button,
#  we'll need to code an exit in some way. So we use a key on the keyboard to terminate the program.
def onRel(key):
    #Setting Delete key as the exit key.
    if (key==keyboard.Key.delete):
        #Stopping the Listener.
        return False

# The main function that runs, to listen for keyboard, mouse inputs.
def main():
    with keyboard.Listener(on_release=onRel) as k:
        with mouse.Listener(on_click=onClick) as m:
            k.join()
            m.join()    

if __name__ =="__main__":
    main()
