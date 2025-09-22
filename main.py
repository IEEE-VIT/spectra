from pynput import keyboard
from pynput import mouse
from PIL import Image, ImageGrab
from os.path import isfile
import json
import math

history_file = "color_history.json"

# Predefined CSS3 color names for mapping
CSS3_COLORS = {
    "White": (255, 255, 255),
    "Silver": (192, 192, 192),
    "Gray": (128, 128, 128),
    "Black": (0, 0, 0),
    "Red": (255, 0, 0),
    "Maroon": (128, 0, 0),
    "Yellow": (255, 255, 0),
    "Olive": (128, 128, 0),
    "Lime": (0, 255, 0),
    "Green": (0, 128, 0),
    "Aqua": (0, 255, 255),
    "Teal": (0, 128, 128),
    "Blue": (0, 0, 255),
    "Navy": (0, 0, 128),
    "Fuchsia": (255, 0, 255),
    "Purple": (128, 0, 128),
    "Orange": (255, 165, 0),
    # Add more colors as needed
}

# FEATURE: Function to get nearest color name
def get_nearest_color_name(rgb):
    min_distance = float('inf')
    nearest_color = None
    for name, c_rgb in CSS3_COLORS.items():
        distance = math.sqrt(sum((a - b) ** 2 for a, b in zip(rgb, c_rgb)))
        if distance < min_distance:
            min_distance = distance
            nearest_color = name
    return nearest_color

# Load history on startup
if isfile(history_file):
    with open(history_file, "r") as f:
        colorList = json.load(f)
else:
    colorList = []

def save_history():
    with open(history_file, "w") as f:
        json.dump(colorList, f)

def clear_history():
    global colorList
    colorList = []
    save_history()
    print("Color history cleared.")

def show_history_count():
    print(f"Total colors stored: {len(colorList)}")

def printColorList():
    print("Colors detected are:", end=" ")
    for color in colorList:
        print(f"#{color}", end=" ")
    print()

exit_requested = False

def onRel(key):
    global exit_requested
    if key == keyboard.Key.delete:
        print("Exiting color capture...")
        exit_requested = True
        return False

def exportToFile(file_path):
    if exit_requested:
        return False
    if isfile(file_path):
        raise FileExistsError(f"{file_path} is already present")
    with open(file_path, "w") as f:
        for color in colorList:
            f.write(f"#{color}\n")

def getHex(rgb):
    output = ''
    for value in rgb:
        output += hex(value)[2:].upper().zfill(2)
    return output

def hex_to_rgb(hexcode):
    hexcode = hexcode.lstrip('#')
    rgb = tuple(int(hexcode[i:i+2], 16) for i in (0, 2, 4))
    return rgb

def getColor(x, y):
    coor = x, y
    return ImageGrab.grab().getpixel(coor)

def onClick(x, y, button, press):
    if button == mouse.Button.right and press:
        color = getColor(x, y)
        hex_color = getHex(color)
        colorList.append(hex_color)
        save_history()
        # FEATURE: Show hex, RGB, and nearest color name
        nearest_name = get_nearest_color_name(color)
        print(f"Color at mouse click (x={x}, y={y}): #{hex_color} | RGB: {color} | Name: {nearest_name}")

def main():
    with keyboard.Listener(on_release=onRel) as k:
        with mouse.Listener(on_click=onClick) as m:
            k.join()
            m.join()

def start_color_capture():
    print("Right-click on the screen to capture colors.")
    print("Press the Delete key to exit.")
    main()

def export_colors_to_file(file_path):
    print("Exporting detected colors to file...")
    try:
        exportToFile(file_path)
        print(f"Colors exported to {file_path}")
    except FileExistsError as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    print("Color Capture Tool")
    print("1. Start capturing colors")
    print("2. Export colors to a file")
    print("3. Clear color history")
    print("4. Show total colors stored")
    choice = input("Enter your choice (1/2/3/4): ")

    if choice == '1':
        start_color_capture()
    elif choice == '2':
        file_path = input("Enter the file path to export colors: ")
        export_colors_to_file(file_path)
    elif choice == '3':
        clear_history()
    elif choice == '4':
        show_history_count()
    else:
        print("Invalid choice. Please choose 1, 2, 3, or 4.")
