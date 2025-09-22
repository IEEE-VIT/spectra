from pynput import keyboard, mouse
from PIL import ImageGrab
from os.path import isfile
import json
import threading
import sys

# Path for persistent storage
HISTORY_PATH = "color_history.json"

# Global history list storing hex strings WITHOUT the leading '#'
colorList = []

# Listener references so we can stop both from a callback
keyboard_listener = None
mouse_listener = None

# Lock for thread-safe access to colorList & file
history_lock = threading.Lock()

# Load history from HISTORY_PATH (JSON) into colorList
def load_history():
    global colorList
    try:
        if isfile(HISTORY_PATH):
            with open(HISTORY_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, list):
                    # Normalize: strip leading '#' if present and uppercase
                    colorList = [c.lstrip("#").upper() for c in data if isinstance(c, str)]
                else:
                    colorList = []
        else:
            colorList = []
    except Exception as e:
        print(f"Warning: failed to load history ({e}). Starting with empty history.")
        colorList = []

# Save current colorList to HISTORY_PATH
def save_history():
    with history_lock:
        try:
            # Write hex codes with leading '#'
            with open(HISTORY_PATH, "w", encoding="utf-8") as f:
                json.dump([f"#{c}" for c in colorList], f, indent=2)
        except Exception as e:
            print(f"Error saving history: {e}")

# Print the color list in a readable format (with '#')
def printColorList():
    with history_lock:
        print("Colors detected are:", end=" ")
        for color in colorList:
            print(f"#{color}", end=" ")
        print()

# Convert RGB tuple to hex string (without '#'), uppercase, zero-padded
def getHex(rgb):
    output = ''
    for value in rgb:
        output += hex(value)[2:].upper().zfill(2)
    return output

# Convert hex code string to RGB tuple
def hex_to_rgb(hexcode):
    hexcode = hexcode.lstrip('#')
    rgb = tuple(int(hexcode[i:i+2], 16) for i in (0, 2, 4))
    return rgb

# Get color at screen coordinate (x,y) using ImageGrab
def getColor(x, y):
    try:
        # ImageGrab.grab() returns an Image; getpixel returns an RGB tuple
        return ImageGrab.grab().getpixel((int(x), int(y)))
    except Exception as e:
        print(f"Failed to grab pixel at ({x},{y}): {e}")
        return (0, 0, 0)

# Mouse click handler
def onClick(x, y, button, pressed):
    # If right button pressed, capture the color at the location
    if button == mouse.Button.right and pressed:
        rgb = getColor(x, y)
        hex_color = getHex(rgb)
        with history_lock:
            colorList.append(hex_color)
            # Immediately persist when a color is captured
            save_history()
        print(f"Color at mouse click (x={x}, y={y}): #{hex_color}")

# Keyboard release handler (Delete key to exit)
def onRel(key):
    global keyboard_listener, mouse_listener
    try:
        if key == keyboard.Key.delete:
            print("Exiting color capture...")
            # Stop both listeners cleanly
            if mouse_listener is not None:
                mouse_listener.stop()
            if keyboard_listener is not None:
                keyboard_listener.stop()
            return False
    except Exception:
        # Some keys may raise on equality check; ignore
        pass

# Export to a user-specified file path.
# If file exists, raise FileExistsError unless overwrite=True.
def exportToFile(file_path, overwrite=False):
    if isfile(file_path) and not overwrite:
        raise FileExistsError(f"{file_path} is already present")
    with history_lock:
        with open(file_path, "w", encoding="utf-8") as f:
            for color in colorList:
                f.write(f"#{color}\n")

# Start listeners (keyboard + mouse)
def start_listeners():
    global keyboard_listener, mouse_listener
    # Start keyboard listener
    keyboard_listener = keyboard.Listener(on_release=onRel)
    mouse_listener = mouse.Listener(on_click=onClick)

    keyboard_listener.start()
    mouse_listener.start()

    print("Right-click on the screen to capture colors.")
    print("Press the Delete key to exit capturing.")

    # Wait for both listeners to finish (they stop when onRel triggers)
    keyboard_listener.join()
    mouse_listener.join()

# Export colors through UI wrapper that asks about overwriting if needed
def export_colors_to_file_ui():
    file_path = input("Enter the file path to export colors to: ").strip()
    if not file_path:
        print("No file path provided. Export cancelled.")
        return
    try:
        if isfile(file_path):
            resp = input(f"File '{file_path}' exists. Overwrite? (y/N): ").strip().lower()
            if resp != 'y':
                print("Export cancelled.")
                return
            exportToFile(file_path, overwrite=True)
        else:
            exportToFile(file_path, overwrite=False)
        print(f"Colors exported to {file_path}")
    except FileExistsError as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"Failed to export: {e}")

# Clear history (with confirmation)
def clear_history_ui():
    resp = input("Are you sure you want to CLEAR the history? This cannot be undone. (y/N): ").strip().lower()
    if resp == 'y':
        with history_lock:
            colorList.clear()
            try:
                # rewrite the history file as empty list
                with open(HISTORY_PATH, "w", encoding="utf-8") as f:
                    json.dump([], f)
                print("History cleared.")
            except Exception as e:
                print(f"Failed to clear history file: {e}")
    else:
        print("Clear cancelled.")

# Show total count of stored colors
def show_count():
    with history_lock:
        print(f"Total colors stored: {len(colorList)}")

def main_menu():
    load_history()
    print("Color Capture Tool (Persistent History)")
    while True:
        print("\nMenu:")
        print("1. Start capturing colors")
        print("2. Export colors to a file")
        print("3. Show how many colors are stored")
        print("4. Clear history")
        print("5. Show full color list")
        print("6. Exit")
        choice = input("Enter your choice (1-6): ").strip()

        if choice == '1':
            start_listeners()
        elif choice == '2':
            export_colors_to_file_ui()
        elif choice == '3':
            show_count()
        elif choice == '4':
            clear_history_ui()
        elif choice == '5':
            printColorList()
        elif choice == '6':
            print("Goodbye.")
            sys.exit(0)
        else:
            print("Invalid choice. Please choose 1-6.")

if __name__ == "__main__":
    main_menu()
