from pynput import keyboard
from pynput import mouse
from PIL import ImageGrab
from os.path import isfile
import json
import csv

colorList = []
exit_requested = False

# ---------------- Utility Functions ---------------- #
def printColorList():
    print("Colors detected are:", end=" ")
    for color in colorList:
        print(f"#{color}", end=" ")
    print()

def getHex(rgb):
    return ''.join(hex(v)[2:].upper().zfill(2) for v in rgb)

def getColor(x, y):
    return ImageGrab.grab().getpixel((x, y))

def onClick(x, y, button, press):
    if button == mouse.Button.right and press:
        color = getColor(x, y)
        hex_color = getHex(color)
        colorList.append(hex_color)
        print(f"Color at mouse click (x={x}, y={y}): #{hex_color}")

# ---------------- Export Function ---------------- #
def exportToFile(file_path):
    if not colorList:
        print("Warning: No colors captured yet. Nothing to export.")
        return
    
    ext = file_path.lower().split('.')[-1]

    if ext == "txt":
        if isfile(file_path):
            print(f"Error: {file_path} already exists.")
            return
        with open(file_path, "w") as f:
            for color in colorList:
                f.write(f"#{color}\n")
        print(f"Colors exported to {file_path} (TXT format)")

    elif ext == "csv":
        if isfile(file_path):
            print(f"Error: {file_path} already exists.")
            return
        with open(file_path, "w", newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["HEX", "R", "G", "B"])
            for hex_color in colorList:
                r = int(hex_color[0:2], 16)
                g = int(hex_color[2:4], 16)
                b = int(hex_color[4:6], 16)
                writer.writerow([f"#{hex_color}", r, g, b])
        print(f"Colors exported to {file_path} (CSV format)")

    elif ext == "json":
        if isfile(file_path):
            print(f"Error: {file_path} already exists.")
            return
        with open(file_path, "w") as f:
            json.dump([f"#{c}" for c in colorList], f)
        print(f"Colors exported to {file_path} (JSON format)")

    elif ext == "html":
        if isfile(file_path):
            print(f"Error: {file_path} already exists.")
            return
        with open(file_path, "w") as f:
            f.write("<html><body><h2>Color Palette</h2>\n")
            for hex_color in colorList:
                f.write(f'<div style="display:inline-block;width:50px;height:50px;background-color:#{hex_color};margin:2px;"></div>\n')
            f.write("</body></html>")
        print(f"Colors exported to {file_path} (HTML format)")

    else:
        print(f"Error: Unsupported file extension '.{ext}'. Supported: txt, csv, json, html.")

# ---------------- Keyboard Listener ---------------- #
def onRel(key):
    global exit_requested
    try:
        if key.char and key.char.lower() == 'e':
            file_path = input("Enter file path to export colors: ")
            exportToFile(file_path)
    except AttributeError:
        if key == keyboard.Key.delete:
            print("Exiting color capture...")
            exit_requested = True
            return False

# ---------------- Main Capture ---------------- #
def main():
    print("Right-click on the screen to capture colors.")
    print("Press 'E' to export colors at any time.")
    print("Press Delete to exit.")
    with keyboard.Listener(on_release=onRel) as k:
        with mouse.Listener(on_click=onClick) as m:
            k.join()
            m.join()

if __name__ == "__main__":
    print("Color Capture Tool")
    start = input("Press Enter to start capturing colors...")
    main()