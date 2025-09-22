
# --- Existing imports ---
from pynput import keyboard
from pynput import mouse
from PIL import Image, ImageGrab
from os.path import isfile

# --- New imports for GUI ---
import tkinter as tk
from tkinter import messagebox, filedialog
import threading

# These are the dependencies we will be using, we use pynput to record the input from either the mouse or the keyboard,
# The cursor coordinates are used to capture the pixel the cursor is resting on, and whether or not the mouse has been clicked.


# Global color list
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

# For CLI/keyboard listener exit
exit_requested = False

# Since we cannot keep the script running all the time,
#  and it will only tell us the value of the color if we press the close button,
#  we'll need to code an exit in some way. So we use a key on the keyboard to terminate the program.

def onRel(key):
    global exit_requested
    # Setting Delete key as the exit key.
    if key == keyboard.Key.delete:
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
    for value in rgb:
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

def getColor(x, y):
    coor = x, y
    return ImageGrab.grab().getpixel(coor)

# Function to record whether or not the mouse has been clicked, takes x, y coordinates as arguments,
#  and button specifies which particular botton is pressed(in our case, it would be 'right click'),
#  and press is a boolean indicating if it has been pressed or not.

def onClick(x, y, button, press):
    # check if the pressed mouse button is the right button
    if button == mouse.Button.right and press:
        color = getColor(x, y)
        hex_color = getHex(color)
        colorList.append(hex_color)
        print(f"Colorat mouse click (x={x}, y={y}): #{hex_color}")
        # If GUI is running, update the listbox
        if 'update_gui_color_list' in globals():
            update_gui_color_list()

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


# --- Tkinter GUI Implementation ---
def run_gui():
    global update_gui_color_list

    root = tk.Tk()
    root.title("Color Capture Tool")
    root.geometry("400x400")

    # --- Functions for GUI actions ---
    def start_capture_thread():
        # Run color capture in a thread so GUI doesn't freeze
        def capture():
            messagebox.showinfo("Instructions", "Right-click anywhere on the screen to capture colors.\nPress the Delete key to stop capturing.")
            # Use local exit_requested for GUI
            global exit_requested
            exit_requested = False
            with keyboard.Listener(on_release=onRel) as k:
                with mouse.Listener(on_click=onClick) as m:
                    k.join()
                    m.join()
        t = threading.Thread(target=capture, daemon=True)
        t.start()

    def export_colors():
        file_path = file_entry.get()
        if not file_path:
            messagebox.showerror("Error", "Please enter a file path.")
            return
        if isfile(file_path):
            messagebox.showerror("Error", f"{file_path} already exists.")
            return
        try:
            exportToFile(file_path)
            messagebox.showinfo("Success", f"Colors exported to {file_path}")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def clear_colors():
        colorList.clear()
        update_gui_color_list()

    def update_gui_color_list():
        color_listbox.delete(0, tk.END)
        for color in colorList:
            color_listbox.insert(tk.END, f"#{color}")

    def browse_file():
        file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
        if file_path:
            file_entry.delete(0, tk.END)
            file_entry.insert(0, file_path)

    # --- GUI Layout ---
    tk.Label(root, text="Captured Colors:").pack(pady=(10, 0))
    color_listbox = tk.Listbox(root, height=8, width=30)
    color_listbox.pack(pady=5)

    btn_frame = tk.Frame(root)
    btn_frame.pack(pady=10)

    start_btn = tk.Button(btn_frame, text="Start Capturing Colors", command=start_capture_thread)
    start_btn.grid(row=0, column=0, padx=5)

    clear_btn = tk.Button(btn_frame, text="Clear/Reset", command=clear_colors)
    clear_btn.grid(row=0, column=1, padx=5)

    # File path entry
    file_frame = tk.Frame(root)
    file_frame.pack(pady=5)
    tk.Label(file_frame, text="Export File Path:").grid(row=0, column=0, padx=2)
    file_entry = tk.Entry(file_frame, width=22)
    file_entry.grid(row=0, column=1, padx=2)
    browse_btn = tk.Button(file_frame, text="Browse", command=browse_file)
    browse_btn.grid(row=0, column=2, padx=2)

    export_btn = tk.Button(root, text="Export Captured Colors", command=export_colors)
    export_btn.pack(pady=5)

    exit_btn = tk.Button(root, text="Exit", command=root.destroy)
    exit_btn.pack(pady=5)

    # Make update_gui_color_list available globally for mouse callback
    globals()['update_gui_color_list'] = update_gui_color_list

    # Initial update
    update_gui_color_list()

    root.mainloop()

#This code provides a user menu with options to capture colors or export colors to a file based on user input.

if __name__ == "__main__":
    # Launch the GUI instead of CLI menu
    run_gui()
