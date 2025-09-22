import json
import os
from pynput import keyboard, mouse
from PIL import ImageGrab
from os.path import isfile

HISTORY_FILE = "color_history.json"
colorList = []
display_format = "HEX"  # Can be "HEX" or "RGB"

# ------------------- Persistence -------------------
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

def save_history():
    with open(HISTORY_FILE, "w") as f:
        json.dump(colorList, f, indent=2)

def clear_history():
    global colorList
    colorList = []
    save_history()
    print("✅ Color history cleared.")

# ------------------- Utilities -------------------
def getHex(rgb):
    return ''.join(hex(value)[2:].upper().zfill(2) for value in rgb)

def hex_to_rgb(hexcode):
    hexcode = hexcode.lstrip('#')
    return tuple(int(hexcode[i:i+2], 16) for i in (0, 2, 4))

def printColorList():
    if not colorList:
        print("⚠️ No colors stored yet.")
        return
    print(f"🎨 Colors in {display_format} format:")
    for color in colorList:
        if display_format == "HEX":
            print(f"   #{color}")
        else:
            print(f"   {hex_to_rgb(color)}")

def getColor(x, y):
    return ImageGrab.grab().getpixel((x, y))

# ------------------- Capture Logic -------------------
def onRel(key):
    global display_format
    try:
        if key == keyboard.Key.delete:
            print("🛑 Exiting color capture...")
            save_history()
            return False
        elif key.char.lower() == 'p':
            printColorList()
        elif key.char.lower() == 't':
            display_format = "RGB" if display_format == "HEX" else "HEX"
            print(f"🔄 Display format toggled to {display_format}")
    except AttributeError:
        # Special keys (like Delete) do not have 'char'
        pass

def onClick(x, y, button, press):
    if button == mouse.Button.right and press:
        color = getColor(x, y)
        hex_color = getHex(color)
        if hex_color not in colorList:  # avoid duplicates
            colorList.append(hex_color)
            save_history()
        # Show color in current display format
        if display_format == "HEX":
            print(f"Captured color at ({x},{y}): #{hex_color}")
        else:
            print(f"Captured color at ({x},{y}): {color}")

# ------------------- Export -------------------
def exportToFile(file_path):
    if os.path.exists(file_path):
        overwrite = input(f"{file_path} already exists. Overwrite? (y/n): ")
        if overwrite.lower() != 'y':
            print("❌ Export canceled.")
            return
    with open(file_path, "w") as f:
        for color in colorList:
            if display_format == "HEX":
                f.write(f"#{color}\n")
            else:
                f.write(f"{hex_to_rgb(color)}\n")

def export_colors_to_file(file_path):
    if not colorList:
        print("⚠️ No colors to export.")
        return
    print("📤 Exporting detected colors...")
    exportToFile(file_path)
    print(f"✅ Colors exported to {file_path}")

# ------------------- Main -------------------
def main():
    with keyboard.Listener(on_release=onRel) as k:
        with mouse.Listener(on_click=onClick) as m:
            k.join()
            m.join()

def start_color_capture():
    print("👉 Right-click on the screen to capture colors.")
    print("👉 Press the Delete key to exit.")
    print("👉 Press 'P' to print captured colors.")
    print("👉 Press 'T' to toggle display format between HEX/RGB.")
    main()

if __name__ == "__main__":
    load_history()  # Load history at startup

    while True:
        print("\n--- 🎨 Color Capture Tool ---")
        print("1. Start capturing colors")
        print("2. Export colors to a file")
        print("3. Show color history")
        print("4. Clear color history")
        print("5. Show total stored colors")
        print("6. Exit")

        choice = input("Enter your choice (1-6): ")

        if choice == '1':
            start_color_capture()
        elif choice == '2':
            file_path = input("Enter the file path to export colors: ")
            export_colors_to_file(file_path)
        elif choice == '3':
            printColorList()
        elif choice == '4':
            clear_history()
        elif choice == '5':
            print(f"📦 Total stored colors: {len(colorList)}")
        elif choice == '6':
            save_history()
            print("👋 Goodbye!")
            break
        else:
            print("⚠️ Invalid choice. Please choose 1–6.")



