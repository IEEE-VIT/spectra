from pynput import keyboard
from pynput import mouse
from PIL import Image, ImageGrab
from os.path import isfile

# These are the dependencies we will be using, we use pynput to record the input from either the mouse or the keyboard,
# The cursor coordinates are used to capture the pixel the cursor is resting on, and whether or not the mouse has been clicked.

colorList = []

# Function to print the color detected
# Assuming it is stored hex code
# colorList is a global variable
def printColorList():
    print("Colors detected are:", end=" ")
    for color in colorList:
        print(f"#{color}", end=" ")
    print()

# Flag to indicate whether exit has been requested
exit_requested = False

# Since we cannot keep the script running all the time,
#  and it will only tell us the value of the color if we press the close button,
#  we'll need to code an exit in some way. So we use a key on the keyboard to terminate the program.
def onRel(key):
    global exit_requested
    #Setting Delete key as the exit key.
    if key == keyboard.Key.delete:
        #Stopping the Listener.
        print("Exiting color capture...")
        exit_requested = True
        return False

# Function to export the colors detected to file_path
# Assume that global colorList stores hexcodes of colors
# If file_path is already present it raises Error
def exportToFile(file_path):
    # Stop processing mouse clicks when exit is requested
    if exit_requested:
        return False  
    if isfile(file_path):
        raise FileExistsError(f"{file_path} is already present")
    with open(file_path, "w") as f:
        for color in colorList:
            f.write(f"#{color}\n")

# Function to get the hex code value which takes a tuple containing the red,green,blue values from 0-255.
def getHex(rgb):
    output = ''
    
    for value in rgb :
        output += hex(value)[2:].upper().zfill(2)
        
    return output

# Function to convert hex code to RGB format
def hex_to_rgb(hexcode):
    # Remove the '#' if present
    hexcode = hexcode.lstrip('#')
    
    # Convert hex to RGB
    rgb = tuple(int(hexcode[i:i+2], 16) for i in (0, 2, 4))
    return rgb

# The getColor function accepts 2 arguments, 1 x coordinate, 1 y coordinate, we capture or "grab" an image,
# and based on the x-y coordinates we get the color at that particular pixel. 
def getColor(x,y):
    coor = x,y
    
    return ImageGrab.grab().getpixel(coor)

# Function to record whether or not the mouse has been clicked, takes x, y coordinates as arguments,
#  and button specifies which particular botton is pressed(in our case, it would be 'right click'),
#  and press is a boolean indicating if it has been pressed or not.
def onClick(x,y,button,press):
    # check if the pressed mouse button is the right button
    if button == mouse.Button.right and press:
        # get the color of the pixel at the coordinates x and y
        color = getColor(x, y)
        # convert the color (RGB format) into a hexadecimal representation.
        hex_color = getHex(color)
        
        colorList.append(hex_color)
        print(f"Color at mouse click (x={x}, y={y}): #{hex_color}")

# The main function that runs, to listen for keyboard, mouse inputs.
def main():
    with keyboard.Listener(on_release=onRel) as k:
        with mouse.Listener(on_click=onClick) as m:
            k.join()
            m.join()    

#This function provides user instructions for capturing colors from the screen and exiting the color capture process in a larger program.
def start_color_capture():
    print("Right-click on the screen to capture colors.")
    print("Press the Delete key to exit.")
    main()

#This function exports detected colors to a file and provides user feedback on the export process, including success confirmation and error 
# handling for existing files.
def export_colors_to_file(file_path):
    print("Exporting detected colors to file...")
    try:
        exportToFile(file_path)
        print(f"Colors exported to {file_path}")
    except FileExistsError as e:
        print(f"Error: {e}")

#This code provides a user menu with options to capture colors or export colors to a file based on user input.
if __name__ == "__main__":
    print("Color Capture Tool")
    print("1. Start capturing colors")
    print("2. Export colors to a file")
    choice = input("Enter your choice (1/2): ")

    if choice == '1':
        start_color_capture()
    elif choice == '2':
        file_path = input("Enter the file path to export colors: ")
        export_colors_to_file(file_path)
    else:
        print("Invalid choice. Please choose 1 or 2.")
import os
import json
import csv
import sqlite3
import atexit
from datetime import datetime
import pyautogui
import time

# Configuration
HISTORY_DIR = os.path.expanduser("~/.spectra")
HISTORY_JSON = os.path.join(HISTORY_DIR, "history.json")
DEFAULT_STORAGE = "json"  # options: "json", "csv", "sqlite"
SQLITE_DB = os.path.join(HISTORY_DIR, "history.db")
CSV_PATH = os.path.join(HISTORY_DIR, "history.csv")

# In-memory history list of dicts: [{"r":..,"g":..,"b":..,"hex":"#rrggbb","time":"..."}]
colors_history = []

def ensure_history_dir():
    if not os.path.exists(HISTORY_DIR):
        os.makedirs(HISTORY_DIR, exist_ok=True)

def rgb_to_hex(r, g, b):
    return "#{:02X}{:02X}{:02X}".format(r, g, b)

def add_color(r, g, b, save_immediately=False):
    """Add a color to in-memory history (avoid consecutive duplicates)."""
    entry = {
        "r": int(r),
        "g": int(g),
        "b": int(b),
        "hex": rgb_to_hex(r, g, b),
        "time": datetime.utcnow().isoformat() + "Z"
    }
    if colors_history and colors_history[-1]["r"] == entry["r"] and colors_history[-1]["g"] == entry["g"] and colors_history[-1]["b"] == entry["b"]:
        # identical to last entry -> ignore
        return entry
    colors_history.append(entry)
    if save_immediately:
        save_history(DEFAULT_STORAGE)  # will write JSON by default
    return entry

def get_rgb_from_cursor():
    """Get pixel color at current mouse cursor (works with pyautogui)."""
    x, y = pyautogui.position()
    try:
        color = pyautogui.pixel(int(x), int(y))
    except Exception:
        # fallback: take small screenshot and get pixel
        im = pyautogui.screenshot()
        color = im.getpixel((int(x), int(y)))
    r, g, b = color, color, color
    return r, g, b

# ------- JSON storage -------
def load_history_json(path=HISTORY_JSON):
    if not os.path.exists(path):
        return []
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, list):
                return data
            return []
    except Exception:
        return []

def save_history_json(path=HISTORY_JSON):
    ensure_history_dir()
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(colors_history, f, indent=2)
        return True
    except Exception as e:
        print("Error saving JSON history:", e)
        return False

# ------- CSV storage -------
def save_history_csv(path=CSV_PATH):
    ensure_history_dir()
    try:
        with open(path, "w", newline="", encoding="utf-8") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["r", "g", "b", "hex", "time"])
            for c in colors_history:
                writer.writerow([c["r"], c["g"], c["b"], c["hex"], c["time"]])
        return True
    except Exception as e:
        print("Error saving CSV history:", e)
        return False

def load_history_csv(path=CSV_PATH):
    if not os.path.exists(path):
        return []
    try:
        data = []
        with open(path, "r", encoding="utf-8") as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                data.append({
                    "r": int(row["r"]),
                    "g": int(row["g"]),
                    "b": int(row["b"]),
                    "hex": row.get("hex") or rgb_to_hex(int(row["r"]), int(row["g"]), int(row["b"])),
                    "time": row.get("time") or ""
                })
        return data
    except Exception:
        return []

# ------- SQLite storage -------
def init_sqlite_db(path=SQLITE_DB):
    ensure_history_dir()
    con = sqlite3.connect(path)
    cur = con.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS colors (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        r INTEGER,
        g INTEGER,
        b INTEGER,
        hex TEXT,
        time TEXT
    )
    """)
    con.commit()
    con.close()

def save_history_sqlite(path=SQLITE_DB):
    try:
        init_sqlite_db(path)
        con = sqlite3.connect(path)
        cur = con.cursor()
        # Option: simple approach: clear table and reinsert
        cur.execute("DELETE FROM colors")
        for c in colors_history:
            cur.execute("INSERT INTO colors (r,g,b,hex,time) VALUES (?,?,?,?,?)",
                        (c["r"], c["g"], c["b"], c["hex"], c["time"]))
        con.commit()
        con.close()
        return True
    except Exception as e:
        print("Error saving SQLite history:", e)
        return False

def load_history_sqlite(path=SQLITE_DB):
    if not os.path.exists(path):
        return []
    try:
        con = sqlite3.connect(path)
        cur = con.cursor()
        cur.execute("SELECT r,g,b,hex,time FROM colors ORDER BY id")
        rows = cur.fetchall()
        con.close()
        return [{"r": r, "g": g, "b": b, "hex": hexv, "time": timev} for (r, g, b, hexv, timev) in rows]
    except Exception:
        return []

# ------- Generic load/save/clear/export -------
def load_history(storage=DEFAULT_STORAGE):
    global colors_history
    if storage == "json":
        colors_history = load_history_json()
    elif storage == "csv":
        colors_history = load_history_csv()
    elif storage == "sqlite":
        colors_history = load_history_sqlite()
    else:
        colors_history = load_history_json()
    return colors_history

def save_history(storage=DEFAULT_STORAGE):
    if storage == "json":
        return save_history_json()
    elif storage == "csv":
        return save_history_csv()
    elif storage == "sqlite":
        return save_history_sqlite()
    else:
        return save_history_json()

def clear_history(storage=DEFAULT_STORAGE):
    global colors_history
    colors_history = []
    # remove files if present
    try:
        if storage == "json":
            if os.path.exists(HISTORY_JSON):
                os.remove(HISTORY_JSON)
        elif storage == "csv":
            if os.path.exists(CSV_PATH):
                os.remove(CSV_PATH)
        elif storage == "sqlite":
            if os.path.exists(SQLITE_DB):
                os.remove(SQLITE_DB)
        else:
            if os.path.exists(HISTORY_JSON):
                os.remove(HISTORY_JSON)
    except Exception as e:
        print("Could not remove storage file:", e)

def export_history(path, fmt=None):
    fmt = (fmt or os.path.splitext(path).lstrip(".").lower()) or "json"
    if fmt == "json":
        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(colors_history, f, indent=2)
            return True
        except Exception as e:
            print("Export JSON failed:", e)
            return False
    elif fmt == "csv":
        try:
            with open(path, "w", newline="", encoding="utf-8") as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(["r", "g", "b", "hex", "time"])
                for c in colors_history:
                    writer.writerow([c["r"], c["g"], c["b"], c["hex"], c["time"]])
            return True
        except Exception as e:
            print("Export CSV failed:", e)
            return False
    elif fmt in ("sqlite", "db"):
        # create sqlite file and save
        try:
            init_sqlite_db(path)
            con = sqlite3.connect(path)
            cur = con.cursor()
            cur.execute("DELETE FROM colors")
            for c in colors_history:
                cur.execute("INSERT INTO colors (r,g,b,hex,time) VALUES (?,?,?,?,?)",
                            (c["r"], c["g"], c["b"], c["hex"], c["time"]))
            con.commit()
            con.close()
            return True
        except Exception as e:
            print("Export SQLite failed:", e)
            return False
    else:
        print("Unknown export format:", fmt)
        return False

# Auto-save at exit
ensure_history_dir()
load_history(DEFAULT_STORAGE)
atexit.register(lambda: save_history(DEFAULT_STORAGE))

# ------- User interaction / start capture -------
def print_history(limit=50):
    if not colors_history:
        print("No colors in history.")
        return
    print("History (most recent last). Total:", len(colors_history))
    start = max(0, len(colors_history) - limit)
    for i, c in enumerate(colors_history[start:], start=start+1):
        print(f"{i}. {c['hex']}  (r={c['r']}, g={c['g']}, b={c['b']})  captured: {c['time']}")

def start_color_capture():
    print("Spectra - Color Capture with persistent history")
    print("Commands:")
    print("  Enter  -> capture color under current mouse cursor")
    print("  v      -> view history")
    print("  e PATH -> export history to PATH (file extension decides format: .json .csv .db)")
    print("  clear  -> clear history")
    print("  q      -> quit")
    try:
        while True:
            cmd = input("> ").strip()
            if cmd == "":
                # capture
                r, g, b = get_rgb_from_cursor()
                entry = add_color(r, g, b, save_immediately=True)
                print("Captured:", entry["hex"], f"(r={r},g={g},b={b})")
            elif cmd.lower() == "v":
                print_history()
            elif cmd.lower().startswith("e "):
                path = cmd[2:].strip()
                if not path:
                    print("Specify path to export to: e /path/to/file.json")
                    continue
                ok = export_history(path)
                print("Exported to", path if ok else "FAILED")
            elif cmd.lower() == "clear":
                confirm = input("Really clear history? (yes/no): ").strip().lower()
                if confirm == "yes":
                    clear_history(DEFAULT_STORAGE)
                    print("History cleared.")
                else:
                    print("Canceled.")
            elif cmd.lower() == "q":
                print("Quitting. Saving history...")
                save_history(DEFAULT_STORAGE)
                break
            else:
                print("Unknown command. Press Enter to capture, 'v' view, 'e PATH' export, 'clear', 'q' quit.")
    except KeyboardInterrupt:
        print("\nInterrupted. Saving history and exiting.")
        save_history(DEFAULT_STORAGE)

# If this file is executed directly, start the capture loop
if __name__ == "__main__":
    start_color_capture()
