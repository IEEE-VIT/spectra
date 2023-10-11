from pynput import keyboard
from pynput import mouse
from PIL import Image, ImageGrab
from os.path import isfile

colorList = []

def printColorList():
    if colorList:
        print("Colors detected:")
        for color in colorList:
            print(f"#{color}")
    else:
        print("No colors detected.")

def exportToFile(file_path):
    if isfile(file_path):
        raise FileExistsError(f"{file_path} is already present")
    with open(file_path, "w") as f:
        for color in colorList:
            f.write(f"#{color}\n")
        print(f"Colors exported to {file_path}")

def getHex(rgb):
    return ''.join(hex(value)[2:].upper().zfill(2) for value in rgb)

def hex_to_rgb(hexcode):
    hexcode = hexcode.lstrip('#')
    return tuple(int(hexcode[i:i+2], 16) for i in (0, 2, 4))

def getColor(x, y):
    coor = x, y
    return ImageGrab.grab().getpixel(coor)

def onClick(x, y, button, press):
    if press:  # Check if the mouse button is pressed
        color = getColor(x, y)
        hex_color = getHex(color)
        colorList.append(hex_color)

def onRel(key):
    if key == keyboard.Key.delete:
        return False

def main():
    print("Color Picker Tool")
    print("Press the Delete key to stop capturing colors.")
    with keyboard.Listener(on_release=onRel) as k:
        with mouse.Listener(on_click=onClick) as m:
            k.join()
            m.join()

if __name__ == "__main__":
    main()
