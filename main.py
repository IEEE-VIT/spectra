from pynput import keyboard
from pynput import mouse
from PIL import Image, ImageGrab
from os.path import isfile
import json
import os

# Persistent history file
HISTORY_FILE = "color_history.json"

colorList = []

# ---------------- Persistence Functions ---------------- #
def load_history():
    global colorList
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, "r") as f:
                colorList = json.load(f)
            print(f"Loaded {len(colorList)} colors from history.")
        except Exception:
            print("History file is corrupted. Starting fresh.")
            colorList = []
    else:
        colorList = []

def save_history():
    with open(HISTORY_FILE, "w") as f:
        json.dump(colorList, f)

def clear_history():
    global colorList
    colorList = []
    save_history()
    print("History cleared.")

# ---------------- Utility Functions ---------------- #
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
    return ''.join(hex(v)[2:].upper().zfill(2) for v in rgb)

def hex_to_rgb(hexcode):
    hexcode = hexcode.lstrip('#')
    return tuple(int(hexcode[i:i+2], 16) for i in (0, 2, 4))

def getColor(x, y):
    return ImageGrab.grab().getpixel((x, y))

def onClick(x, y, button, press):
    if button == mouse.Button.right and press:
        color = getColor(x, y)
        hex_color = getHex(color)
        colorList.append(hex_color)
        save_history()  # persist immediately
        print(f"Color at mouse click (x={x}, y={y}): #{hex_color}")

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

# ---------------- Main Menu ---------------- #
if __name__ == "__main__":
    load_history()

    while True:
        print("\nColor Capture Tool")
        print("1. Start capturing colors")
        print("2. Export colors to a file")
        print("3. Show number of stored colors")
        print("4. Clear history")
        print("5. Exit")

        choice = input("Enter your choice (1-5): ")

        if choice == '1':
            start_color_capture()
        elif choice == '2':
            file_path = input("Enter the file path to export colors: ")
            export_colors_to_file(file_path)
        elif choice == '3':
            print(f"Total colors stored: {len(colorList)}")
        elif choice == '4':
            clear_history()
        elif choice == '5':
            print("Goodbye!")
            break
        else:
            print("Invalid choice. Please choose 1–5.")