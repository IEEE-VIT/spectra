'''from pynput import keyboard
from pynput import mouse
from PIL import Image, ImageGrab
from os.path import isfile

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
from pynput import keyboard
from pynput import mouse
from PIL import Image, ImageGrab
from os.path import isfile
import webcolors   # NEW: for human-readable color names

# Global list of captured colors
colorList = []

# Exit flag
exit_requested = False


# Try to get a human-readable color name
def get_color_name(hexcode):
    try:
        # Exact match
        return webcolors.hex_to_name(f"#{hexcode}", spec='css3')
    except ValueError:
        # No exact match → find the closest color
        rgb = hex_to_rgb(hexcode)
        min_colors = {}
        for name, hex_value in webcolors.CSS3_HEX_TO_NAMES.items():
            r_c, g_c, b_c = webcolors.hex_to_rgb(name)
            rd = (r_c - rgb[0]) ** 2
            gd = (g_c - rgb[1]) ** 2
            bd = (b_c - rgb[2]) ** 2
            min_colors[(rd + gd + bd)] = hex_value
        closest_hex = min_colors[min(min_colors.keys())]
        return webcolors.CSS3_HEX_TO_NAMES[closest_hex]


# Print captured colors
def printColorList():
    if not colorList:
        print("No colors captured yet.")
    else:
        print("Colors detected:")
        for color in colorList:
            rgb = hex_to_rgb(color)
            name = get_color_name(color)
            print(f"  #{color}  RGB{rgb}  → {name}")


# Export colors to file
def exportToFile(file_path):
    if exit_requested:
        return False
    if isfile(file_path):
        raise FileExistsError(f"{file_path} is already present")
    if not colorList:
        print("No colors captured. Nothing to export.")
        return
    with open(file_path, "w") as f:
        for color in colorList:
            rgb = hex_to_rgb(color)
            name = get_color_name(color)
            f.write(f"#{color}  RGB{rgb}  {name}\n")


# Convert RGB → Hex
def getHex(rgb):
    return "".join(hex(value)[2:].upper().zfill(2) for value in rgb)


# Convert Hex → RGB
def hex_to_rgb(hexcode):
    hexcode = hexcode.lstrip('#')
    return tuple(int(hexcode[i:i+2], 16) for i in (0, 2, 4))


# Capture color at (x,y)
def getColor(x, y):
    return ImageGrab.grab().getpixel((x, y))


# Mouse listener
def onClick(x, y, button, press):
    if exit_requested:
        return False
    if button == mouse.Button.right and press:
        color = getColor(x, y)
        hex_color = getHex(color)
        if hex_color not in colorList:  # avoid duplicates
            colorList.append(hex_color)
        rgb = hex_to_rgb(hex_color)
        name = get_color_name(hex_color)
        print(f"Color at (x={x}, y={y}): #{hex_color}  RGB{rgb}  → {name}")


# Keyboard listener
def onRel(key):
    global exit_requested
    try:
        if key == keyboard.Key.delete:
            print("Exiting color capture...")
            exit_requested = True
            return False

        elif key.char == 'p':
            printColorList()

        elif key.char == 'c':
            colorList.clear()
            print("Color list cleared.")

        elif key.char == 'r':
            if colorList:
                last_color = colorList[-1]
                rgb = hex_to_rgb(last_color)
                name = get_color_name(last_color)
                print(f"Last color: #{last_color}  RGB{rgb}  → {name}")
            else:
                print("No colors captured yet.")
    except AttributeError:
        pass


# Main loop
def main():
    with keyboard.Listener(on_release=onRel) as k:
        with mouse.Listener(on_click=onClick) as m:
            k.join()
            m.join()


# Start capture
def start_color_capture():
    print("Right-click to capture colors.")
    print("Shortcuts: [P] Print | [C] Clear | [R] Show last | [Delete] Exit")
    main()


# Export colors
def export_colors_to_file(file_path):
    print("Exporting detected colors to file...")
    try:
        exportToFile(file_path)
        print(f"Colors exported to {file_path}")
    except FileExistsError as e:
        print(f"Error: {e}")


# Menu
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
from pynput import keyboard
from pynput import mouse
from PIL import Image, ImageGrab
from os.path import isfile

# Global list of captured colors (stored in HEX internally)
colorList = []

# Exit flag
exit_requested = False

# Global display format (HEX or RGB)
display_format = "HEX"


# Function to print the color list
def printColorList():
    if not colorList:
        print("No colors captured yet.")
        return

    print(f"Colors detected ({display_format}):", end=" ")

    for color in colorList:
        if display_format == "HEX":
            print(f"#{color}", end=" ")
        else:  # RGB mode
            rgb = hex_to_rgb(color)
            print(f"{rgb}", end=" ")
    print()


# Function to export the colors detected to file_path
def exportToFile(file_path):
    if exit_requested:
        return False
    if isfile(file_path):
        raise FileExistsError(f"{file_path} is already present")
    if not colorList:
        print("No colors to export.")
        return

    with open(file_path, "w") as f:
        for color in colorList:
            if display_format == "HEX":
                f.write(f"#{color}\n")
            else:
                f.write(f"{hex_to_rgb(color)}\n")


# Convert RGB tuple to HEX string
def getHex(rgb):
    return "".join(hex(value)[2:].upper().zfill(2) for value in rgb)


# Convert HEX string to RGB tuple
def hex_to_rgb(hexcode):
    hexcode = hexcode.lstrip('#')
    return tuple(int(hexcode[i:i+2], 16) for i in (0, 2, 4))


# Capture pixel color at (x, y)
def getColor(x, y):
    return ImageGrab.grab().getpixel((x, y))


# Mouse listener
def onClick(x, y, button, press):
    if exit_requested:
        return False
    if button == mouse.Button.right and press:
        color = getColor(x, y)
        hex_color = getHex(color)
        colorList.append(hex_color)

        if display_format == "HEX":
            print(f"Color at (x={x}, y={y}): #{hex_color}")
        else:
            rgb = hex_to_rgb(hex_color)
            print(f"Color at (x={x}, y={y}): {rgb}")


# Keyboard listener
def onRel(key):
    global exit_requested, display_format

    try:
        if key == keyboard.Key.delete:
            print("Exiting color capture...")
            exit_requested = True
            return False

        elif key.char.lower() == 'p':  # Print colors
            printColorList()

        elif key.char.lower() == 't':  # Toggle format
            display_format = "RGB" if display_format == "HEX" else "HEX"
            print(f"Switched display/export format to {display_format}.")

    except AttributeError:
        # Ignore special keys that don't have .char
        pass


# Main listener loop
def main():
    with keyboard.Listener(on_release=onRel) as k:
        with mouse.Listener(on_click=onClick) as m:
            k.join()
            m.join()


# Start capturing
def start_color_capture():
    print("Right-click on the screen to capture colors.")
    print("Keyboard shortcuts:")
    print("  [P] → Print all tracked colors")
    print("  [T] → Toggle between HEX and RGB mode")
    print("  [Delete] → Exit capture")
    main()


# Export detected colors
def export_colors_to_file(file_path):
    print("Exporting detected colors to file...")
    try:
        exportToFile(file_path)
        print(f"Colors exported to {file_path}")
    except FileExistsError as e:
        print(f"Error: {e}")


# CLI menu
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
        print("Invalid choice. Please choose 1 or 2.")'''
from pynput import keyboard 
from pynput import mouse
from PIL import Image, ImageGrab
from os.path import isfile, splitext
import os

# Global list of captured colors
colorList = []

# Flag to indicate whether exit has been requested
exit_requested = False

# Function to print captured colors
def printColorList():
    print("Colors detected are:", end=" ")
    for color in colorList:
        print(f"#{color}", end=" ")
    print()


# Convert RGB tuple to hex
def getHex(rgb):
    return "".join(hex(value)[2:].upper().zfill(2) for value in rgb)


# Convert hex to RGB tuple
def hex_to_rgb(hexcode):
    hexcode = hexcode.lstrip('#')
    return tuple(int(hexcode[i:i+2], 16) for i in (0, 2, 4))


# Capture color at coordinates
def getColor(x, y):
    return ImageGrab.grab().getpixel((x, y))


# Handle mouse clicks
def onClick(x, y, button, press):
    if exit_requested:
        return False
    if button == mouse.Button.right and press:
        color = getColor(x, y)
        hex_color = getHex(color)
        colorList.append(hex_color)
        print(f"Color at mouse click (x={x}, y={y}): #{hex_color}")


# Handle keyboard events
def onRel(key):
    global exit_requested
    if key == keyboard.Key.delete:
        print("Exiting color capture...")
        exit_requested = True
        return False


# Export colors to file with options
def exportToFile(file_path):
    if exit_requested:
        return False  

    if isfile(file_path):
        print(f"The file '{file_path}' already exists.")
        print("Choose an option:")
        print("1: Overwrite")
        print("2: Append")
        print("3: Auto-generate new filename")
        option = input("Enter 1, 2, or 3: ").strip()

        if option == '1':
            mode = 'w'
        elif option == '2':
            mode = 'a'
        elif option == '3':
            base, ext = splitext(file_path)
            counter = 1
            new_file = f"{base}_{counter}{ext}"
            while isfile(new_file):
                counter += 1
                new_file = f"{base}_{counter}{ext}"
            file_path = new_file
            mode = 'w'
            print(f"Auto-generated filename: {file_path}")
        else:
            print("Invalid option. Export cancelled.")
            return

    else:
        mode = 'w'

    with open(file_path, mode) as f:
        for color in colorList:
            f.write(f"#{color}\n")


# Main function to listen for keyboard and mouse
def main():
    with keyboard.Listener(on_release=onRel) as k:
        with mouse.Listener(on_click=onClick) as m:
            k.join()
            m.join()


# Start color capture
def start_color_capture():
    print("Right-click on the screen to capture colors.")
    print("Press the Delete key to exit.")
    main()


# Export colors with feedback
def export_colors_to_file(file_path):
    print("Exporting detected colors to file...")
    try:
        exportToFile(file_path)
        print(f"Colors exported to {file_path}")
    except Exception as e:
        print(f"Error: {e}")


# CLI menu
if __name__ == "__main__":
    print("Color Capture Tool")
    print("1. Start capturing colors")
    print("2. Export colors to a file")
    choice = input("Enter your choice (1/2): ").strip()

    if choice == '1':
        start_color_capture()
    elif choice == '2':
        file_path = input("Enter the file path to export colors: ").strip()
        export_colors_to_file(file_path)
    else:
        print("Invalid choice. Please choose 1 or 2.")
