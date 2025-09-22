from pynput import keyboard
from pynput import mouse
from PIL import Image, ImageGrab
from os.path import isfile
import tkinter as tk
from tkinter import messagebox, filedialog, simpledialog
import threading

# These are the dependencies we will be using, we use pynput to record the input from either the mouse or the keyboard,
# The cursor coordinates are used to capture the pixel the cursor is resting on, and whether or not the mouse has been clicked.

colorList = []
mouse_listener = None
keyboard_listener = None

# Function to print the color detected
# Assuming it is stored hex code
# colorList is a global variable
def printColorList():
    print("Colors detected are:", end=" ")
    for color in colorList:
        print(f"#{color}", end=" ")
    print()

def getColorListStr():
    return [f"#{color}" for color in colorList]


exit_requested = False
# Function to export the colors detected to file_path
# Assume that global colorList stores hexcodes of colors
# If file_path is already present it raises Error
def exportToFile(file_path):
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
def onClick(x, y, button, press):
    if button == mouse.Button.right and press:
        color = getColor(x, y)
        hex_color = getHex(color)
        colorList.append(hex_color)
        print(f"Color at mouse click (x={x}, y={y}): #{hex_color}")
        # If GUI is running, update the color list display
        if 'update_color_list_gui' in globals():
            update_color_list_gui()

# The main function that runs, to listen for keyboard, mouse inputs.
def main():
    global mouse_listener, keyboard_listener
    with keyboard.Listener(on_release=onRel) as k:
        with mouse.Listener(on_click=onClick) as m:
            mouse_listener = m
            keyboard_listener = k
            k.join()
            m.join()

#This function provides user instructions for capturing colors from the screen and exiting the color capture process in a larger program.
def start_color_capture():
    print("Right-click on the screen to capture colors.")
    print("Press the Delete key to exit.")
    main()
def onRel(key):
    global exit_requested
    if key == keyboard.Key.delete:
        exit_requested = True
        print("Exiting color capture...")
        return False
def clear_colors():
    colorList.clear()
    update_color_list_gui()

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
def run_color_capture_thread():
    # Run color capture in a thread so GUI doesn't freeze
    t = threading.Thread(target=start_color_capture)
    t.daemon = True
    t.start()

def gui_export_colors():
    if not colorList:
        messagebox.showinfo("No Colors", "No colors to export.")
        return
    file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
    if not file_path:
        return
    try:
        exportToFile(file_path)
        messagebox.showinfo("Export Successful", f"Colors exported to {file_path}")
    except FileExistsError:
        messagebox.showerror("File Exists", f"{file_path} already exists.")
    except Exception as e:
        messagebox.showerror("Error", str(e))

    if 'color_listbox' in globals():
        color_listbox.delete(0, tk.END)
        for color in getColorListStr():
            color_listbox.insert(tk.END, color)

    if 'color_listbox' in globals():
        color_listbox.delete(0, tk.END)
        for color in getColorListStr():
            color_listbox.insert(tk.END, color)

def launch_gui():
    global color_listbox, file_path_entry, update_color_list_gui
    root = tk.Tk()
    root.title("Color Capture Tool")
    root.geometry("500x350")

    tk.Label(root, text="Color Capture Tool", font=("Arial", 16, "bold")).pack(pady=8)

    # File path entry
    entry_frame = tk.Frame(root)
    entry_frame.pack(pady=2)
    tk.Label(entry_frame, text="Export file path:").pack(side=tk.LEFT, padx=2)
    file_path_entry = tk.Entry(entry_frame, width=35)
    file_path_entry.pack(side=tk.LEFT, padx=2)
    browse_btn = tk.Button(entry_frame, text="Browse", command=lambda: file_path_entry.insert(0, filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt"), ("All files", "*.*")])))
    browse_btn.pack(side=tk.LEFT, padx=2)

    # Listbox for colors
    tk.Label(root, text="Colors detected:").pack()
    color_listbox = tk.Listbox(root, width=40, height=7, bg="#f0f0f0", font=("Consolas", 11))
    color_listbox.pack(padx=10, pady=4)

    # Buttons
    btn_frame = tk.Frame(root)
    btn_frame.pack(pady=8)
    tk.Button(btn_frame, text="Start Capturing Colors", command=run_color_capture_thread, width=22).grid(row=0, column=0, padx=5)
    tk.Button(btn_frame, text="Export Colors", command=lambda: gui_export_colors_with_entry(), width=22).grid(row=0, column=1, padx=5)
    tk.Button(btn_frame, text="Clear Colors", command=clear_colors, width=22).grid(row=1, column=0, padx=5, pady=4)
    tk.Button(btn_frame, text="Instructions", command=show_instructions, width=22).grid(row=1, column=1, padx=5, pady=4)
    tk.Button(root, text="Exit", command=root.destroy, width=15).pack(pady=4)

    # Make update_color_list_gui accessible to mouse callback
    globals()['update_color_list_gui'] = update_color_list_gui

    root.mainloop()

def show_instructions():
    messagebox.showinfo("Instructions", "Click 'Start Capturing Colors' and right-click anywhere on the screen to capture a color.\nPress the Delete key to stop capturing.")

    global color_listbox, file_path_entry, update_color_list_gui
    root = tk.Tk()
    root.title("Color Capture Tool")
    root.geometry("500x350")

    tk.Label(root, text="Color Capture Tool", font=("Arial", 16, "bold")).pack(pady=8)

    # File path entry
    entry_frame = tk.Frame(root)
    entry_frame.pack(pady=2)
    tk.Label(entry_frame, text="Export file path:").pack(side=tk.LEFT, padx=2)
    file_path_entry = tk.Entry(entry_frame, width=35)
    file_path_entry.pack(side=tk.LEFT, padx=2)
    browse_btn = tk.Button(entry_frame, text="Browse", command=lambda: file_path_entry.insert(0, filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt"), ("All files", "*.*")])))
    browse_btn.pack(side=tk.LEFT, padx=2)

    # Listbox for colors
    tk.Label(root, text="Colors detected:").pack()
    color_listbox = tk.Listbox(root, width=40, height=7, bg="#f0f0f0", font=("Consolas", 11))
    color_listbox.pack(padx=10, pady=4)

    # Buttons
    btn_frame = tk.Frame(root)
    btn_frame.pack(pady=8)
    tk.Button(btn_frame, text="Start Capturing Colors", command=run_color_capture_thread, width=22).grid(row=0, column=0, padx=5)
    tk.Button(btn_frame, text="Export Colors", command=lambda: gui_export_colors_with_entry(), width=22).grid(row=0, column=1, padx=5)
    tk.Button(btn_frame, text="Clear Colors", command=clear_colors, width=22).grid(row=1, column=0, padx=5, pady=4)
    tk.Button(btn_frame, text="Instructions", command=show_instructions, width=22).grid(row=1, column=1, padx=5, pady=4)
    tk.Button(root, text="Exit", command=root.destroy, width=15).pack(pady=4)

    # Make update_color_list_gui accessible to mouse callback
    globals()['update_color_list_gui'] = update_color_list_gui

    root.mainloop()

# New export function using entry
def gui_export_colors_with_entry():
    if not colorList:
        messagebox.showinfo("No Colors", "No colors to export.")
        return
    file_path = file_path_entry.get().strip()
    if not file_path:
        messagebox.showwarning("Missing Path", "Please enter a file path for export.")
        return
    try:
        exportToFile(file_path)
        messagebox.showinfo("Export Successful", f"Colors exported to {file_path}")
    except FileExistsError:
        messagebox.showerror("File Exists", f"{file_path} already exists.")
    except Exception as e:
        messagebox.showerror("Error", str(e))

#This code provides a user menu with options to capture colors or export colors to a file based on user input.
if __name__ == "__main__":
    launch_gui()
