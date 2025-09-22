from pynput import keyboard
from pynput import mouse
from PIL import Image, ImageGrab
from os.path import isfile
import webcolors

# These are the dependencies we will be using, we use pynput to record the input from either the mouse or the keyboard,
# The cursor coordinates are used to capture the pixel the cursor is resting on, and whether or not the mouse has been clicked.

colorList = []

# Function to print the color detected
# Assuming it is stored hex code
# colorList is a global variable
def printColorList():
    print("Colors detected are:", end=" ")
    for color in colorList:
        print(f"#{color}", end=" ")
    print()

# Flag to indicate whether exit has been requested
exit_requested = False

# Since we cannot keep the script running all the time,
#  and it will only tell us the value of the color if we press the close button,
#  we'll need to code an exit in some way. So we use a key on the keyboard to terminate the program.
def onRel(key):
    global exit_requested
    #Setting Delete key as the exit key.
    if key == keyboard.Key.delete:
        #Stopping the Listener.
        print("Exiting color capture...")
        exit_requested = True
        return False

# Function to export the colors detected to file_path
# Assume that global colorList stores hexcodes of colors
# If file_path is already present it raises Error
def exportToFile(file_path):
    # Stop processing mouse clicks when exit is requested
    if exit_requested:
        return False  
    if isfile(file_path):
        raise FileExistsError(f"{file_path} is already present")
    with open(file_path, "w") as f:
        for color in colorList:
            f.write(f"#{color}\n")

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
        
        colorList.append(hex_color)
        print(f"Color at mouse click (x={x}, y={y}): #{hex_color}")

# The main function that runs, to listen for keyboard, mouse inputs.
def main():
    with keyboard.Listener(on_release=onRel) as k:
        with mouse.Listener(on_click=onClick) as m:
            k.join()
            m.join()    

#This function provides user instructions for capturing colors from the screen and exiting the color capture process in a larger program.
def start_color_capture():
    print("Right-click on the screen to capture colors.")
    print("Press the Delete key to exit.")
    main()

#This function exports detected colors to a file and provides user feedback on the export process, including success confirmation and error 
# handling for existing files.
def export_colors_to_file(file_path):
    print("Exporting detected colors to file...")
    try:
        exportToFile(file_path)
        print(f"Colors exported to {file_path}")
    except FileExistsError as e:
        print(f"Error: {e}")

#This code provides a user menu with options to capture colors or export colors to a file based on user input.
if __name__ == "__main__":
    print("Color Capture Tool")
    print("1. Start capturing colors")
    print("2. Export colors to a file")
    choice = input("Enter your choice (1/2): ")

    if choice == '1':
        start_color_capture()
    elif choice == '2':
        file_path = input("Enter the file path to export colors: ")
        export_colors_to_file(file_path)
    else:
        print("Invalid choice. Please choose 1 or 2.")

def closest_colour(requested_rgb):
    min_colours={}
    for hex_code,name in webcolors.CSS3_HEX_TO_NAMES.items():
        r_c,g_c, b_c = webcolors.hex_to_rgb(hex_code)
        dist=(r_c - requested_rgb[0])**2+ (g_c - requested_rgb[1])**2 +(b_c - requested_rgb[2])**2
        min_colours[dist] = name
        return
    min_colours[min(min_colours.keys())]
        
