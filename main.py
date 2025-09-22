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
        print("Invalid choice. Please choose 1 or 2.")'''
'''from pynput import keyboard
from pynput import mouse
from PIL import ImageGrab
from os.path import isfile
import webcolors

colorList = []

# Function to print the color detected
def printColorList():
    print("Colors detected are:", end=" ")
    for color in colorList:
        print(f"#{color}", end=" ")
    print()

# Flag to indicate whether exit has been requested
exit_requested = False

def onRel(key):
    global exit_requested
    # Setting Delete key as the exit key.
    if key == keyboard.Key.delete:
        print("Exiting color capture...")
        exit_requested = True
        return False

# Export detected colors to a file
def exportToFile(file_path):
    if exit_requested:
        return False
    if isfile(file_path):
        raise FileExistsError(f"{file_path} is already present")
    with open(file_path, "w") as f:
        for color in colorList:
            f.write(f"#{color}\n")

# Convert RGB → Hex
def getHex(rgb):
    return ''.join(hex(value)[2:].upper().zfill(2) for value in rgb)

# Convert Hex → RGB
def hex_to_rgb(hexcode):
    hexcode = hexcode.lstrip('#')
    return tuple(int(hexcode[i:i+2], 16) for i in (0, 2, 4))

# Get pixel color at coordinates
def getColor(x, y):
    return ImageGrab.grab().getpixel((x, y))

# Find the closest color name
def closest_color_name(rgb):
    try:
        # Try exact match
        return webcolors.rgb_to_name(rgb, spec='css3')
    except ValueError:
        # If no exact match, find the nearest
        min_colors = {}
        for hex_code, name in webcolors.CSS3_HEX_TO_NAMES.items():
            r_c, g_c, b_c = webcolors.hex_to_rgb(hex_code)
            dist = (r_c - rgb[0]) ** 2 + (g_c - rgb[1]) ** 2 + (b_c - rgb[2]) ** 2
            min_colors[dist] = name
        return min_colors[min(min_colors.keys())]

# Mouse click handler
def onClick(x, y, button, press):
    if button == mouse.Button.right and press:
        color = getColor(x, y)
        hex_color = getHex(color)
        colorList.append(hex_color)
        color_name = closest_color_name(color)
        print(f"Color at (x={x}, y={y}): #{hex_color} | RGB {color} | Name: {color_name}")

# Main listeners
def main():
    with keyboard.Listener(on_release=onRel) as k:
        with mouse.Listener(on_click=onClick) as m:
            k.join()
            m.join()

# User instructions
def start_color_capture():
    print("Right-click on the screen to capture colors.")
    print("Press the Delete key to exit.")
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
        print("Invalid choice. Please choose 1 or 2.")'''
'''from pynput import keyboard
from pynput import mouse
from PIL import Image, ImageGrab
from os.path import isfile

# These are the dependencies we will be using, we use pynput to record the input from either the mouse or the keyboard,
# The cursor coordinates are used to capture the pixel the cursor is resting on, and whether or not the mouse has been clicked.

colorList = []
# Current format can be 'HEX' or 'RGB'
current_format = 'HEX' 

# Function to print the color detected
# Assuming it is stored hex code
# colorList is a global variable
def printColorList():
    print(f"Colors detected in {current_format} format:")
    if not colorList:
        print("No colors have been captured yet.")
        return
    for color in colorList:
        if current_format == 'HEX':
            print(f"#{color}", end=" ")
        else: # RGB format
            rgb_color = hex_to_rgb(color)
            print(f"({rgb_color[0]}, {rgb_color[1]}, {rgb_color[2]})", end=" ")
    print()

# Flag to indicate whether exit has been requested
exit_requested = False

# Since we cannot keep the script running all the time,
# and it will only tell us the value of the color if we press the close button,
# we'll need to code an exit in some way. So we use a key on the keyboard to terminate the program.
def onRel(key):
    global exit_requested
    global current_format

    try:
        if key == keyboard.Key.delete:
            # Stopping the Listener.
            print("Exiting color capture...")
            exit_requested = True
            return False
        elif key.char == 'p' or key.char == 'P':
            printColorList()
        elif key.char == 't' or key.char == 'T':
            if current_format == 'HEX':
                current_format = 'RGB'
            else:
                current_format = 'HEX'
            print(f"Toggled format to {current_format}")
    except AttributeError:
        # This handles special keys that don't have a .char attribute
        pass

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
            if current_format == 'HEX':
                f.write(f"#{color}\n")
            else:
                rgb_color = hex_to_rgb(color)
                f.write(f"({rgb_color[0]}, {rgb_color[1]}, {rgb_color[2]})\n")

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
# and button specifies which particular botton is pressed(in our case, it would be 'right click'),
# and press is a boolean indicating if it has been pressed or not.
def onClick(x,y,button,press):
    # check if the pressed mouse button is the right button
    if button == mouse.Button.right and press:
        # get the color of the pixel at the coordinates x and y
        color = getColor(x, y)
        # convert the color (RGB format) into a hexadecimal representation.
        hex_color = getHex(color)
        
        colorList.append(hex_color)
        print(f"Color captured at mouse click (x={x}, y={y}): #{hex_color}")

# The main function that runs, to listen for keyboard, mouse inputs.
def main():
    with keyboard.Listener(on_release=onRel) as k:
        with mouse.Listener(on_click=onClick) as m:
            k.join()
            m.join()    

# This function provides user instructions for capturing colors from the screen and exiting the color capture process in a larger program.
def start_color_capture():
    print("Right-click on the screen to capture colors.")
    print("Press 'P' to print captured colors.")
    print("Press 'T' to toggle between HEX and RGB format.")
    print("Press the 'Delete' key to exit.")
    main()

# This function exports detected colors to a file and provides user feedback on the export process, including success confirmation and error 
# handling for existing files.
def export_colors_to_file(file_path):
    print("Exporting detected colors to file...")
    try:
        exportToFile(file_path)
        print(f"Colors exported to {file_path}")
    except FileExistsError as e:
        print(f"Error: {e}")

# This code provides a user menu with options to capture colors or export colors to a file based on user input.
if __name__ == "__main__":
    print("Color Capture Tool")
    print("1. Start capturing colors")
    print("2. Export colors to a file")
    print("3. Print all captured colors")
    choice = input("Enter your choice (1/2/3): ")

    if choice == '1':
        start_color_capture()
    elif choice == '2':
        file_path = input("Enter the file path to export colors: ")
        export_colors_to_file(file_path)
    elif choice == '3':
        printColorList()
    else:
        print("Invalid choice. Please choose 1, 2, or 3.")'''
'''from pynput import keyboard
from pynput import mouse
from PIL import Image, ImageGrab
from os.path import isfile, splitext, basename, join
from os import path

# These are the dependencies we will be using, we use pynput to record the input from either the mouse or the keyboard,
# The cursor coordinates are used to capture the pixel the cursor is resting on, and whether or not the mouse has been clicked.

colorList = []
# Current format can be 'HEX' or 'RGB'
current_format = 'HEX' 

# Function to print the color detected
# Assuming it is stored hex code
# colorList is a global variable
def printColorList():
    print(f"Colors detected in {current_format} format:")
    if not colorList:
        print("No colors have been captured yet.")
        return
    for color in colorList:
        if current_format == 'HEX':
            print(f"#{color}", end=" ")
        else: # RGB format
            rgb_color = hex_to_rgb(color)
            print(f"({rgb_color[0]}, {rgb_color[1]}, {rgb_color[2]})", end=" ")
    print()

# Flag to indicate whether exit has been requested
exit_requested = False

# Since we cannot keep the script running all the time,
# and it will only tell us the value of the color if we press the close button,
# we'll need to code an exit in some way. So we use a key on the keyboard to terminate the program.
def onRel(key):
    global exit_requested
    global current_format

    try:
        if key == keyboard.Key.delete:
            # Stopping the Listener.
            print("Exiting color capture...")
            exit_requested = True
            return False
        elif key.char == 'p' or key.char == 'P':
            printColorList()
        elif key.char == 't' or key.char == 'T':
            if current_format == 'HEX':
                current_format = 'RGB'
            else:
                current_format = 'HEX'
            print(f"Toggled format to {current_format}")
    except AttributeError:
        # This handles special keys that don't have a .char attribute
        pass

# Function to export the colors detected to file_path
# Assume that global colorList stores hexcodes of colors
# If file_path is already present it raises Error
def exportToFile(file_path, mode='w'):
    # Stop processing mouse clicks when exit is requested
    if exit_requested:
        return False
    with open(file_path, mode) as f:
        for color in colorList:
            if current_format == 'HEX':
                f.write(f"#{color}\n")
            else:
                rgb_color = hex_to_rgb(color)
                f.write(f"({rgb_color[0]}, {rgb_color[1]}, {rgb_color[2]})\n")

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
# and button specifies which particular botton is pressed(in our case, it would be 'right click'),
# and press is a boolean indicating if it has been pressed or not.
def onClick(x,y,button,press):
    # check if the pressed mouse button is the right button
    if button == mouse.Button.right and press:
        # get the color of the pixel at the coordinates x and y
        color = getColor(x, y)
        # convert the color (RGB format) into a hexadecimal representation.
        hex_color = getHex(color)
        
        colorList.append(hex_color)
        print(f"Color captured at mouse click (x={x}, y={y}): #{hex_color}")

# The main function that runs, to listen for keyboard, mouse inputs.
def main():
    with keyboard.Listener(on_release=onRel) as k:
        with mouse.Listener(on_click=onClick) as m:
            k.join()
            m.join()    

# This function provides user instructions for capturing colors from the screen and exiting the color capture process in a larger program.
def start_color_capture():
    print("Right-click on the screen to capture colors.")
    print("Press 'P' to print captured colors.")
    print("Press 'T' to toggle between HEX and RGB format.")
    print("Press the 'Delete' key to exit.")
    main()

# This function exports detected colors to a file and provides user feedback on the export process, including success confirmation and error 
# handling for existing files.
def export_colors_to_file(file_path):
    print("Exporting detected colors to file...")
    if isfile(file_path):
        print(f"File '{file_path}' already exists.")
        print("1. Overwrite the file")
        print("2. Append to the existing file")
        print("3. Auto-generate a new filename")
        choice = input("Enter your choice (1/2/3): ")

        if choice == '1':
            exportToFile(file_path, 'w')
            print(f"Colors overwritten to '{file_path}'.")
        elif choice == '2':
            exportToFile(file_path, 'a')
            print(f"Colors appended to '{file_path}'.")
        elif choice == '3':
            base, ext = splitext(file_path)
            i = 1
            new_path = f"{base}_{i}{ext}"
            while isfile(new_path):
                i += 1
                new_path = f"{base}_{i}{ext}"
            exportToFile(new_path, 'w')
            print(f"Colors exported to new file: '{new_path}'.")
        else:
            print("Invalid choice. Export aborted.")
            return
    else:
        exportToFile(file_path, 'w')
        print(f"Colors exported to '{file_path}'.")

# This code provides a user menu with options to capture colors or export colors to a file based on user input.
if __name__ == "__main__":
    print("Color Capture Tool")
    print("1. Start capturing colors")
    print("2. Export colors to a file")
    print("3. Print all captured colors")
    choice = input("Enter your choice (1/2/3): ")

    if choice == '1':
        start_color_capture()
    elif choice == '2':
        file_path = input("Enter the file path to export colors: ")
        export_colors_to_file(file_path)
    elif choice == '3':
        printColorList()
    else:
        print("Invalid choice. Please choose 1, 2, or 3.")'''
'''import csv
import json
from pynput import keyboard
from pynput import mouse
from PIL import Image, ImageGrab
from os.path import isfile, splitext

# These are the dependencies we will be using, we use pynput to record the input from either the mouse or the keyboard,
# The cursor coordinates are used to capture the pixel the cursor is resting on, and whether or not the mouse has been clicked.

colorList = []
# Current format can be 'HEX' or 'RGB'
current_format = 'HEX' 

# Function to print the color detected
# Assuming it is stored hex code
# colorList is a global variable
def printColorList():
    print(f"Colors detected in {current_format} format:")
    if not colorList:
        print("No colors have been captured yet.")
        return
    for color in colorList:
        if current_format == 'HEX':
            print(f"#{color}", end=" ")
        else: # RGB format
            rgb_color = hex_to_rgb(color)
            print(f"({rgb_color[0]}, {rgb_color[1]}, {rgb_color[2]})", end=" ")
    print()

# Flag to indicate whether exit has been requested
exit_requested = False

# Since we cannot keep the script running all the time,
# and it will only tell us the value of the color if we press the close button,
# we'll need to code an exit in some way. So we use a key on the keyboard to terminate the program.
def onRel(key):
    global exit_requested
    global current_format

    try:
        if key == keyboard.Key.delete:
            # Stopping the Listener.
            print("Exiting color capture...")
            exit_requested = True
            return False
        elif key.char == 'p' or key.char == 'P':
            printColorList()
        elif key.char == 't' or key.char == 'T':
            if current_format == 'HEX':
                current_format = 'RGB'
            else:
                current_format = 'HEX'
            print(f"Toggled format to {current_format}")
    except AttributeError:
        # This handles special keys that don't have a .char attribute
        pass

# Function to export the colors detected to file_path
# Assumes that global colorList stores hexcodes of colors.
# This function is now generalized to handle different file formats.
def exportToFile(file_path):
    # Stop processing mouse clicks when exit is requested
    if exit_requested:
        return False

    _, ext = splitext(file_path.lower())
    
    if ext == '.txt':
        with open(file_path, "w") as f:
            for color in colorList:
                f.write(f"#{color}\n")
    
    elif ext == '.csv':
        with open(file_path, 'w', newline='') as csvfile:
            csv_writer = csv.writer(csvfile)
            if current_format == 'HEX':
                csv_writer.writerow(['Hex Code'])
                for color in colorList:
                    csv_writer.writerow([f"#{color}"])
            else:
                csv_writer.writerow(['Red', 'Green', 'Blue'])
                for color in colorList:
                    rgb_color = hex_to_rgb(color)
                    csv_writer.writerow(list(rgb_color))
    
    elif ext == '.json':
        with open(file_path, 'w') as json_file:
            hex_colors = [f"#{color}" for color in colorList]
            json.dump(hex_colors, json_file, indent=4)
            
    elif ext == '.html':
        html_content = """
<!DOCTYPE html>
<html>
<head>
<title>Color Palette</title>
<style>
body { font-family: sans-serif; }
.color-container {
    display: flex;
    flex-wrap: wrap;
    gap: 10px;
    padding: 20px;
}
.color-box {
    width: 100px;
    height: 100px;
    border: 1px solid #ccc;
    display: flex;
    flex-direction: column;
    justify-content: flex-end;
    align-items: center;
    text-align: center;
}
.color-text {
    background-color: rgba(255, 255, 255, 0.7);
    width: 100%;
    padding: 5px 0;
    font-size: 0.8em;
}
</style>
</head>
<body>
<h1>Color Palette</h1>
<div class="color-container">
"""
        for color in colorList:
            hex_code = f"#{color}"
            rgb_code = hex_to_rgb(color)
            html_content += f"""
    <div class="color-box" style="background-color: {hex_code};">
        <span class="color-text">{hex_code}<br>({rgb_code[0]}, {rgb_code[1]}, {rgb_code[2]})</span>
    </div>
"""
        html_content += """
</div>
</body>
</html>
"""
        with open(file_path, "w") as f:
            f.write(html_content)
    
    else:
        raise ValueError(f"Unsupported file extension: {ext}. Please use .txt, .csv, .json, or .html.")

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
# and button specifies which particular botton is pressed(in our case, it would be 'right click'),
# and press is a boolean indicating if it has been pressed or not.
def onClick(x,y,button,press):
    # check if the pressed mouse button is the right button
    if button == mouse.Button.right and press:
        # get the color of the pixel at the coordinates x and y
        color = getColor(x, y)
        # convert the color (RGB format) into a hexadecimal representation.
        hex_color = getHex(color)
        
        colorList.append(hex_color)
        print(f"Color captured at mouse click (x={x}, y={y}): #{hex_color}")

# The main function that runs, to listen for keyboard, mouse inputs.
def main():
    with keyboard.Listener(on_release=onRel) as k:
        with mouse.Listener(on_click=onClick) as m:
            k.join()
            m.join()    

# This function provides user instructions for capturing colors from the screen and exiting the color capture process in a larger program.
def start_color_capture():
    print("Right-click on the screen to capture colors.")
    print("Press 'P' to print captured colors.")
    print("Press 'T' to toggle between HEX and RGB format.")
    print("Press the 'Delete' key to exit.")
    main()

# This function exports detected colors to a file and provides user feedback on the export process, including success confirmation and error 
# handling for existing files.
def export_colors_to_file(file_path):
    print("Exporting detected colors to file...")
    try:
        exportToFile(file_path)
        print(f"Colors exported to {file_path}")
    except ValueError as e:
        print(f"Error: {e}")

# This code provides a user menu with options to capture colors or export colors to a file based on user input.
if __name__ == "__main__":
    print("Color Capture Tool")
    print("1. Start capturing colors")
    print("2. Export colors to a file")
    print("3. Print all captured colors")
    choice = input("Enter your choice (1/2/3): ")

    if choice == '1':
        start_color_capture()
    elif choice == '2':
        file_path = input("Enter the file path to export colors: ")
        export_colors_to_file(file_path)
    elif choice == '3':
        printColorList()
    else:
        print("Invalid choice. Please choose 1, 2, or 3.")'''
'''import csv
import json
from pynput import keyboard
from pynput import mouse
from PIL import Image, ImageGrab
from os.path import isfile, splitext, basename

# These are the dependencies we will be using, we use pynput to record the input from either the mouse or the keyboard,
# The cursor coordinates are used to capture the pixel the cursor is resting on, and whether or not the mouse has been clicked.

colorList = []
current_format = 'HEX'

# Function to print the color detected
# Assuming it is stored hex code
# colorList is a global variable
def printColorList():
    print(f"Colors detected in {current_format} format:")
    if not colorList:
        print("No colors have been captured yet.")
        return
    for color in colorList:
        if current_format == 'HEX':
            print(f"#{color}", end=" ")
        else: # RGB format
            rgb_color = hex_to_rgb(color)
            print(f"({rgb_color[0]}, {rgb_color[1]}, {rgb_color[2]})", end=" ")
    print()

# Flag to indicate whether exit has been requested
exit_requested = False

# This function provides a menu for exporting colors.
def export_menu():
    if not colorList:
        print("No colors to export. Capture some colors first.")
        return
    
    file_path = input("Enter the file path to export colors: ")
    print("Exporting detected colors to file...")
    try:
        exportToFile(file_path)
        print(f"Colors exported to {file_path}")
    except ValueError as e:
        print(f"Error: {e}")

# Since we cannot keep the script running all the time,
# and it will only tell us the value of the color if we press the close button,
# we'll need to code an exit in some way. So we use a key on the keyboard to terminate the program.
def onRel(key):
    global exit_requested
    global current_format

    try:
        if key == keyboard.Key.delete:
            # Stopping the Listener.
            print("Exiting color capture...")
            exit_requested = True
            return False
        elif key.char == 'p' or key.char == 'P':
            printColorList()
        elif key.char == 't' or key.char == 'T':
            if current_format == 'HEX':
                current_format = 'RGB'
            else:
                current_format = 'HEX'
            print(f"Toggled format to {current_format}")
        elif key.char == 'e' or key.char == 'E':
            export_menu()

    except AttributeError:
        # This handles special keys that don't have a .char attribute
        pass

# Function to export the colors detected to file_path
# Assume that global colorList stores hexcodes of colors
# If file_path is already present it raises Error
def exportToFile(file_path):
    # Stop processing mouse clicks when exit is requested
    if exit_requested:
        return False
        
    _, ext = splitext(file_path.lower())

    if ext == '.txt':
        with open(file_path, "w") as f:
            for color in colorList:
                f.write(f"#{color}\n")
    
    elif ext == '.csv':
        with open(file_path, 'w', newline='') as csvfile:
            csv_writer = csv.writer(csvfile)
            if current_format == 'HEX':
                csv_writer.writerow(['Hex Code'])
                for color in colorList:
                    csv_writer.writerow([f"#{color}"])
            else:
                csv_writer.writerow(['Red', 'Green', 'Blue'])
                for color in colorList:
                    rgb_color = hex_to_rgb(color)
                    csv_writer.writerow(list(rgb_color))
    
    elif ext == '.json':
        with open(file_path, 'w') as json_file:
            hex_colors = [f"#{color}" for color in colorList]
            json.dump(hex_colors, json_file, indent=4)
            
    elif ext == '.html':
        html_content = """
<!DOCTYPE html>
<html>
<head>
<title>Color Palette</title>
<style>
body { font-family: sans-serif; }
.color-container {
    display: flex;
    flex-wrap: wrap;
    gap: 10px;
    padding: 20px;
}
.color-box {
    width: 100px;
    height: 100px;
    border: 1px solid #ccc;
    display: flex;
    flex-direction: column;
    justify-content: flex-end;
    align-items: center;
    text-align: center;
}
.color-text {
    background-color: rgba(255, 255, 255, 0.7);
    width: 100%;
    padding: 5px 0;
    font-size: 0.8em;
}
</style>
</head>
<body>
<h1>Color Palette</h1>
<div class="color-container">
"""
        for color in colorList:
            hex_code = f"#{color}"
            rgb_code = hex_to_rgb(color)
            html_content += f"""
    <div class="color-box" style="background-color: {hex_code};">
        <span class="color-text">{hex_code}<br>({rgb_code[0]}, {rgb_code[1]}, {rgb_code[2]})</span>
    </div>
"""
        html_content += """
</div>
</body>
</html>
"""
        with open(file_path, "w") as f:
            f.write(html_content)
    
    else:
        raise ValueError(f"Unsupported file extension: {ext}. Please use .txt, .csv, .json, or .html.")

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
# and button specifies which particular botton is pressed(in our case, it would be 'right click'),
# and press is a boolean indicating if it has been pressed or not.
def onClick(x,y,button,press):
    # check if the pressed mouse button is the right button
    if button == mouse.Button.right and press:
        # get the color of the pixel at the coordinates x and y
        color = getColor(x, y)
        # convert the color (RGB format) into a hexadecimal representation.
        hex_color = getHex(color)
        
        colorList.append(hex_color)
        print(f"Color captured at mouse click (x={x}, y={y}): #{hex_color}")

# The main function that runs, to listen for keyboard, mouse inputs.
def main():
    with keyboard.Listener(on_release=onRel) as k:
        with mouse.Listener(on_click=onClick) as m:
            k.join()
            m.join()    

# This function provides user instructions for capturing colors from the screen and exiting the color capture process in a larger program.
def start_color_capture():
    print("Right-click on the screen to capture colors.")
    print("Press 'E' to export colors.")
    print("Press 'P' to print captured colors.")
    print("Press 'T' to toggle between HEX and RGB format.")
    print("Press the 'Delete' key to exit.")
    main()

# The user menu is now simplified to just start the capture process.
if __name__ == "__main__":
    start_color_capture()'''
import tkinter as tk
from tkinter import filedialog, messagebox
from pynput import keyboard, mouse
from PIL import ImageGrab
import threading

# Global variables
colorList = []
listener_thread = None
is_capturing = False

# Function to update the GUI listbox with captured colors
def update_listbox():
    listbox.delete(0, tk.END)
    for color in colorList:
        listbox.insert(tk.END, f"#{color}")

# The GUI application class
class ColorCaptureApp:
    def __init__(self, master):
        self.master = master
        master.title("Color Capture Tool")
        master.geometry("400x500")

        # Create widgets
        self.label = tk.Label(master, text="Click Start to begin capturing colors.", pady=10)
        self.label.pack()

        self.start_button = tk.Button(master, text="Start Capture", command=self.start_capture)
        self.start_button.pack(pady=5)

        self.stop_button = tk.Button(master, text="Stop Capture", command=self.stop_capture, state=tk.DISABLED)
        self.stop_button.pack(pady=5)

        self.export_button = tk.Button(master, text="Export Colors", command=self.export_colors, state=tk.DISABLED)
        self.export_button.pack(pady=5)
        
        self.clear_button = tk.Button(master, text="Clear Colors", command=self.clear_colors)
        self.clear_button.pack(pady=5)

        self.listbox_label = tk.Label(master, text="Captured Colors (Hex):")
        self.listbox_label.pack(pady=5)

        self.listbox = tk.Listbox(master)
        self.listbox.pack(pady=5, padx=10, fill=tk.BOTH, expand=True)

    def start_capture(self):
        global is_capturing, listener_thread
        if not is_capturing:
            self.label.config(text="Right-click on the screen to capture colors.")
            self.start_button.config(state=tk.DISABLED)
            self.stop_button.config(state=tk.NORMAL)
            self.export_button.config(state=tk.NORMAL)
            is_capturing = True

            # Start listeners in a separate thread
            listener_thread = threading.Thread(target=self.run_listeners, daemon=True)
            listener_thread.start()

    def stop_capture(self):
        global is_capturing
        if is_capturing:
            self.label.config(text="Color capture stopped.")
            self.start_button.config(state=tk.NORMAL)
            self.stop_button.config(state=tk.DISABLED)
            is_capturing = False
            
            # Stop the pynput listeners
            if keyboard_listener:
                keyboard_listener.stop()
            if mouse_listener:
                mouse_listener.stop()

    def clear_colors(self):
        global colorList
        colorList = []
        update_listbox()
        messagebox.showinfo("Cleared", "Captured colors have been cleared.")

    def export_colors(self):
        if not colorList:
            messagebox.showinfo("No Colors", "There are no colors to export.")
            return

        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text file", "*.txt"), ("CSV file", "*.csv"), ("JSON file", "*.json"), ("HTML file", "*.html")],
            title="Export Colors"
        )
        if not file_path:
            return

        try:
            self.exportToFile(file_path)
            messagebox.showinfo("Success", f"Colors successfully exported to {file_path}")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")

    def run_listeners(self):
        global keyboard_listener, mouse_listener
        with keyboard.Listener(on_release=self.on_keyboard_release) as keyboard_listener:
            with mouse.Listener(on_click=self.on_mouse_click) as mouse_listener:
                keyboard_listener.join()
                mouse_listener.join()

    def on_keyboard_release(self, key):
        if key == keyboard.Key.delete:
            self.stop_capture()
            return False

    def on_mouse_click(self, x, y, button, pressed):
        if button == mouse.Button.right and pressed and is_capturing:
            color = self.getColor(x, y)
            hex_color = self.getHex(color)
            colorList.append(hex_color)
            self.master.after(0, update_listbox) # Use .after to update GUI from a different thread
            print(f"Color captured: #{hex_color}")

    def getColor(self, x, y):
        return ImageGrab.grab().getpixel((x, y))

    def getHex(self, rgb):
        return ''.join([hex(val)[2:].upper().zfill(2) for val in rgb])

    def hex_to_rgb(self, hexcode):
        hexcode = hexcode.lstrip('#')
        return tuple(int(hexcode[i:i+2], 16) for i in (0, 2, 4))
    
    def exportToFile(self, file_path):
        _, ext = splitext(file_path.lower())

        if ext == '.txt':
            with open(file_path, "w") as f:
                for color in colorList:
                    f.write(f"#{color}\n")
        
        elif ext == '.csv':
            import csv
            with open(file_path, 'w', newline='') as csvfile:
                csv_writer = csv.writer(csvfile)
                csv_writer.writerow(['Hex Code', 'Red', 'Green', 'Blue'])
                for color in colorList:
                    rgb_color = self.hex_to_rgb(color)
                    csv_writer.writerow([f"#{color}", rgb_color[0], rgb_color[1], rgb_color[2]])
        
        elif ext == '.json':
            import json
            with open(file_path, 'w') as json_file:
                hex_colors = [f"#{color}" for color in colorList]
                json.dump(hex_colors, json_file, indent=4)
                
        elif ext == '.html':
            html_content = """<!DOCTYPE html><html><head><title>Color Palette</title><style>body {font-family: sans-serif;}.color-container {display: flex;flex-wrap: wrap;gap: 10px;padding: 20px;}.color-box {width: 100px;height: 100px;border: 1px solid #ccc;display: flex;flex-direction: column;justify-content: flex-end;align-items: center;text-align: center;}.color-text {background-color: rgba(255, 255, 255, 0.7);width: 100%;padding: 5px 0;font-size: 0.8em;}</style></head><body><h1>Color Palette</h1><div class="color-container">"""
            for color in colorList:
                hex_code = f"#{color}"
                rgb_code = self.hex_to_rgb(color)
                html_content += f"""<div class="color-box" style="background-color: {hex_code};"><span class="color-text">{hex_code}<br>({rgb_code[0]}, {rgb_code[1]}, {rgb_code[2]})</span></div>"""
            html_content += """</div></body></html>"""
            with open(file_path, "w") as f:
                f.write(html_content)
        
        else:
            raise ValueError("Unsupported file extension. Please use .txt, .csv, .json, or .html.")

# Main application execution
if __name__ == "__main__":
    root = tk.Tk()
    app = ColorCaptureApp(root)
    root.mainloop()

