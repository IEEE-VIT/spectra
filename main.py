from pynput import keyboard
from pynput import mouse
from PIL import Image, ImageGrab
from os.path import isfile
import json

# Global list of captured colors
colorList = []

# File to store persistent history
HISTORY_FILE = "color_history.json"

# Load history from file at startup
def load_history():
    global colorList
    if isfile(HISTORY_FILE):
        with open(HISTORY_FILE, "r") as f:
            try:
                colorList = json.load(f)
            except json.JSONDecodeError:
                colorList = []
    else:
        colorList = []

# Save current colorList to file
def save_history():
    with open(HISTORY_FILE, "w") as f:
        json.dump(colorList, f)

# Print the captured colors
def printColorList():
    print("Colors detected are:", end=" ")
    for color in colorList:
        print(f"#{color}", end=" ")
    print()

# Flag to indicate exit
exit_requested = False

# Exit listener
def onRel(key):
    global exit_requested
    if key == keyboard.Key.delete:
        print("Exiting color capture...")
        exit_requested = True
        return False

# Export captured colors to file
def exportToFile(file_path):
    if exit_requested:
        return False
    if isfile(file_path):
        raise FileExistsError(f"{file_path} is already present")
    with open(file_path, "w") as f:
        for color in colorList:
            f.write(f"#{color}\n")

# Convert RGB to Hex
def getHex(rgb):
    return ''.join([hex(value)[2:].upper().zfill(2) for value in rgb])

# Convert Hex to RGB
def hex_to_rgb(hexcode):
    hexcode = hexcode.lstrip('#')
    return tuple(int(hexcode[i:i+2], 16) for i in (0, 2, 4))

# Get color at a coordinate
def getColor(x, y):
    return ImageGrab.grab().getpixel((x, y))

# Mouse click listener
def onClick(x, y, button, press):
    if button == mouse.Button.right and press:
        color = getColor(x, y)
        hex_color = getHex(color)
        colorList.append(hex_color)
        save_history()  # auto-save every capture
        print(f"Color at mouse click (x={x}, y={y}): #{hex_color}")

# Main listeners
def main():
    with keyboard.Listener(on_release=onRel) as k:
        with mouse.Listener(on_click=onClick) as m:
            k.join()
            m.join()

# Start capturing colors
def start_color_capture():
    print("Right-click on the screen to capture colors.")
    print("Press the Delete key to exit.")
    main()

# Export colors to file
def export_colors_to_file(file_path):
    print("Exporting detected colors to file...")
    try:
        exportToFile(file_path)
        print(f"Colors exported to {file_path}")
    except FileExistsError as e:
        print(f"Error: {e}")

# Clear history
def clear_history():
    global colorList
    colorList = []
    save_history()
    print("History cleared.")

# Show total colors stored
def show_history_count():
    print(f"Total colors stored: {len(colorList)}")

# =================== MAIN ===================
if __name__ == "__main__":
    load_history()  # Load previous session
    print("Color Capture Tool")
    print("1. Start capturing colors")
    print("2. Export colors to a file")
    print("3. Clear history")
    print("4. Show history count")
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
