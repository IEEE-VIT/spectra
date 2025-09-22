from pynput import keyboard
from pynput import mouse
from PIL import ImageGrab
from os.path import isfile

colorList = []
exit_requested = False

# ---------------- Utility Functions ---------------- #
def printColorList():
    print("Colors detected are:", end=" ")
    for color in colorList:
        print(f"#{color}", end=" ")
    print()

def exportToFile(file_path):
    if not colorList:
        print("Warning: No colors captured yet. Nothing to export.")
        return
    if isfile(file_path):
        print(f"Error: {file_path} already exists.")
        return
    try:
        with open(file_path, "w") as f:
            for color in colorList:
                f.write(f"#{color}\n")
        print(f"Colors exported to {file_path}")
    except Exception as e:
        print(f"Error exporting: {e}")

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

# ---------------- Keyboard Listener ---------------- #
def onRel(key):
    global exit_requested
    try:
        if key.char and key.char.lower() == 'e':
            file_path = input("Enter file path to export colors: ")
            exportToFile(file_path)
        # Exit key
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