from pynput import keyboard, mouse
from PIL import ImageGrab
from os.path import isfile
import json
import math

history_file = "color_history.json"

# Predefined CSS3 color names for mapping
CSS3_COLORS = {
    "White": (255, 255, 255), "Silver": (192, 192, 192), "Gray": (128, 128, 128),
    "Black": (0, 0, 0), "Red": (255, 0, 0), "Maroon": (128, 0, 0),
    "Yellow": (255, 255, 0), "Olive": (128, 128, 0), "Lime": (0, 255, 0),
    "Green": (0, 128, 0), "Aqua": (0, 255, 255), "Teal": (0, 128, 128),
    "Blue": (0, 0, 255), "Navy": (0, 0, 128), "Fuchsia": (255, 0, 255),
    "Purple": (128, 0, 128), "Orange": (255, 165, 0)
}

# Load history
if isfile(history_file):
    with open(history_file, "r") as f:
        colorList = json.load(f)
else:
    colorList = []

display_format_hex = True
exit_requested = False

# Helpers
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

def getHex(rgb):
    return ''.join([hex(v)[2:].upper().zfill(2) for v in rgb])

def hex_to_rgb(hexcode):
    hexcode = hexcode.lstrip('#')
    return tuple(int(hexcode[i:i+2], 16) for i in (0, 2, 4))

def get_nearest_color_name(rgb):
    min_dist, nearest = float('inf'), None
    for name, c_rgb in CSS3_COLORS.items():
        dist = math.sqrt(sum((a-b)**2 for a,b in zip(rgb, c_rgb)))
        if dist < min_dist:
            min_dist, nearest = dist, name
    return nearest

def printColorList():
    print("Colors detected:", end=" ")
    for color in colorList:
        print(f"#{color}" if display_format_hex else f"{hex_to_rgb(color)}", end=" ")
    print()

def getColor(x, y):
    return ImageGrab.grab().getpixel((x, y))

# Event handlers
def onRel(key):
    global exit_requested, display_format_hex
    try:
        if key == keyboard.Key.delete:
            print("Exiting color capture...")
            exit_requested = True
            return False
        elif hasattr(key, 'char') and key.char:
            if key.char.lower() == 'p':
                printColorList()
            elif key.char.lower() == 't':
                display_format_hex = not display_format_hex
                print(f"Display format toggled to {'HEX' if display_format_hex else 'RGB'}")
    except AttributeError:
        pass

def onClick(x, y, button, press):
    if button == mouse.Button.right and press:
        color = getColor(x, y)
        hex_color = getHex(color)
        colorList.append(hex_color)
        save_history()
        nearest_name = get_nearest_color_name(color)
        print(f"Color at ({x},{y}): #{hex_color} | RGB: {color} | Name: {nearest_name}")

# Export
def exportToFile(file_path):
    if isfile(file_path):
        raise FileExistsError(f"{file_path} already exists")
    with open(file_path, "w") as f:
        for color in colorList:
            f.write(f"#{color}\n" if display_format_hex else f"{hex_to_rgb(color)}\n")

def start_color_capture():
    print("Right-click to capture colors, Delete to exit, P to print, T to toggle HEX/RGB.")
    with keyboard.Listener(on_release=onRel) as k, mouse.Listener(on_click=onClick) as m:
        k.join()
        m.join()

def export_colors_to_file(file_path):
    try:
        exportToFile(file_path)
        print(f"Colors exported to {file_path}")
    except FileExistsError as e:
        print(f"Error: {e}")

# Main menu
if __name__ == "__main__":
    print("Color Capture Tool")
    choice = input("1.Start capture 2.Export 3.Clear history 4.Show count: ")
    if choice == '1':
        start_color_capture()
    elif choice == '2':
        export_colors_to_file(input("Enter file path: "))
    elif choice == '3':
        clear_history()
    elif choice == '4':
        show_history_count()
    else:
        print("Invalid choice")
