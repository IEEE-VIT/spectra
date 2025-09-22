#!/usr/bin/env python3
"""
Color Capture Tool
- Right-click to capture color under mouse pointer.
- Press Delete to exit.
- Press 'P' to print tracked colors.
- Press 'T' to toggle display between HEX and RGB.
"""

from pynput import keyboard, mouse
from PIL import ImageGrab
from os.path import isfile
import json
import math
import time
from typing import Tuple, Optional, List

history_file = "color_history.json"

# Predefined CSS3 color names for mapping (small set; extend as needed)
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
    # extend with more colors as needed
}

# Globals
mouse_listener: Optional[mouse.Listener] = None
keyboard_listener: Optional[keyboard.Listener] = None
exit_requested = False
display_format_hex = True  # True -> show hex; False -> show rgb

# Load history on startup
if isfile(history_file):
    try:
        with open(history_file, "r", encoding="utf-8") as f:
            colorList: List[str] = json.load(f)
            # Normalize stored hex values (remove '#', uppercase)
            colorList = [c.lstrip("#").upper() for c in colorList]
    except Exception:
        colorList = []
else:
    colorList = []


def save_history() -> None:
    """Save color history to JSON file (include # when writing)."""
    try:
        with open(history_file, "w", encoding="utf-8") as f:
            json.dump([f"#{c}" for c in colorList], f, indent=2)
    except Exception as e:
        print(f"Error saving history: {e}")


def clear_history() -> None:
    global colorList
    colorList = []
    save_history()
    print("Color history cleared.")


def show_history_count() -> None:
    print(f"Total colors stored: {len(colorList)}")


def get_nearest_color_name(rgb: Tuple[int, int, int]) -> Optional[str]:
    """Return nearest named color by Euclidean distance in RGB space."""
    min_distance = float("inf")
    nearest_color = None
    for name, c_rgb in CSS3_COLORS.items():
        distance = math.sqrt(sum((a - b) ** 2 for a, b in zip(rgb, c_rgb)))
        if distance < min_distance:
            min_distance = distance
            nearest_color = name
    return nearest_color


def printColorList() -> None:
    """Print saved colors in current display format."""
    if not colorList:
        print("No colors tracked yet.")
        return

    print("Colors detected:", end=" ")
    for color in colorList:
        if display_format_hex:
            print(f"#{color}", end=" ")
        else:
            rgb = hex_to_rgb(color)
            print(f"{rgb}", end=" ")
    print()


def exportToFile(file_path: str, overwrite: bool = False) -> None:
    """
    Export colorList to file.
    Raises FileExistsError if file exists and overwrite is False.
    """
    if isfile(file_path) and not overwrite:
        raise FileExistsError(f"{file_path} is already present")
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            for color in colorList:
                if display_format_hex:
                    f.write(f"#{color}\n")
                else:
                    f.write(f"{hex_to_rgb(color)}\n")
    except Exception as e:
        raise e


def getHex(rgb: Tuple[int, int, int]) -> str:
    """Return hex string (without '#') from an RGB tuple. Uppercase, two-digit per channel."""
    return "".join(f"{int(v):02X}" for v in rgb)


def hex_to_rgb(hexcode: str) -> Tuple[int, int, int]:
    """Convert hex code (with or without '#') to an (R, G, B) tuple of ints."""
    hexcode = hexcode.lstrip("#")
    if len(hexcode) != 6:
        raise ValueError(f"Invalid hex color: {hexcode}")
    return tuple(int(hexcode[i : i + 2], 16) for i in (0, 2, 4))


def getColor(x: int, y: int) -> Tuple[int, int, int]:
    """Get RGB color at screen coordinate (x, y)."""
    try:
        img = ImageGrab.grab()
        return img.getpixel((int(x), int(y)))
    except Exception as e:
        raise RuntimeError(f"Failed to grab screen pixel at ({x},{y}): {e}")


def onClick(x: int, y: int, button: mouse.Button, pressed: bool) -> None:
    """Mouse callback: capture color on right-click press."""
    global colorList
    if pressed and button == mouse.Button.right:
        try:
            color = getColor(x, y)
        except Exception as e:
            print(e)
            return

        hex_color = getHex(color)
        colorList.append(hex_color)
        save_history()
        nearest_name = get_nearest_color_name(color)
        print(f"Color at mouse click (x={x}, y={y}): #{hex_color} | RGB: {color} | Name: {nearest_name}")


def onRel(key: keyboard.Key) -> bool:
    """
    Keyboard release callback.
    - Delete: stop capturing (stops both keyboard and mouse listeners)
    - 'p': print list
    - 't': toggle display format
    Return False to stop the keyboard listener.
    """
    global exit_requested, display_format_hex, mouse_listener
    try:
        if key == keyboard.Key.delete:
            print("Exiting color capture...")
            exit_requested = True
            # stop mouse listener as well (if running)
            if mouse_listener is not None:
                try:
                    mouse_listener.stop()
                except Exception:
                    pass
            return False  # stop keyboard listener
        # character keys
        if hasattr(key, "char") and key.char:
            ch = key.char.lower()
            if ch == "p":
                printColorList()
            elif ch == "t":
                display_format_hex = not display_format_hex
                fmt = "HEX" if display_format_hex else "RGB"
                print(f"Display format toggled to {fmt}")
    except AttributeError:
        pass
    return True


def main() -> None:
    """Start keyboard and mouse listeners and wait until exit_requested."""
    global mouse_listener, keyboard_listener

    keyboard_listener = keyboard.Listener(on_release=onRel)
    mouse_listener = mouse.Listener(on_click=onClick)

    keyboard_listener.start()
    mouse_listener.start()

    # Wait until keyboard listener stops (onRel returns False) or exit_requested flag is set
    try:
        while not exit_requested:
            time.sleep(0.1)
    except KeyboardInterrupt:
        pass
    finally:
        # Ensure listeners are stopped
        if mouse_listener is not None and mouse_listener.running:
            try:
                mouse_listener.stop()
            except Exception:
                pass
        if keyboard_listener is not None and keyboard_listener.running:
            try:
                keyboard_listener.stop()
            except Exception:
                pass


def start_color_capture() -> None:
    print("Right-click on the screen to capture colors.")
    print("Press the Delete key to exit.")
    print("Press P to print tracked colors.")
    print("Press T to toggle display format between HEX and RGB.")
    main()


def export_colors_to_file(file_path: str, overwrite: bool = False) -> None:
    print("Exporting detected colors to file...")
    try:
        exportToFile(file_path, overwrite=overwrite)
        print(f"Colors exported to {file_path}")
    except FileExistsError as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"Failed to export: {e}")


if __name__ == "__main__":
    print("Color Capture Tool")
    print("1. Start capturing colors")
    print("2. Export colors to a file")
    print("3. Clear color history")
    print("4. Show total colors stored")
    choice = input("Enter your choice (1/2/3/4): ").strip()

    if choice == "1":
        start_color_capture()
    elif choice == "2":
        file_path = input("Enter the file path to export colors: ").strip()
        if not file_path:
            print("No file path given.")
        else:
            # Ask user whether to overwrite if file exists
            if isfile(file_path):
                yn = input(f"File {file_path} exists. Overwrite? (y/n): ").strip().lower()
                export_colors_to_file(file_path, overwrite=(yn == "y"))
            else:
                export_colors_to_file(file_path, overwrite=False)
    elif choice == "3":
        clear_history()
    elif choice == "4":
        show_history_count()
    else:
        print("Invalid choice. Please choose 1, 2, 3, or 4.")
