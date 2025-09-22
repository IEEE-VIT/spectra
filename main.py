import tkinter as tk
from tkinter import messagebox, filedialog
from pynput import keyboard, mouse
from PIL import ImageGrab
from os.path import isfile

colorList = []
exit_requested = False

# ================= Utility Functions ================= #
def getHex(rgb):
    return ''.join([hex(v)[2:].upper().zfill(2) for v in rgb])

def hex_to_rgb(hexcode):
    hexcode = hexcode.lstrip('#')
    return tuple(int(hexcode[i:i+2], 16) for i in (0, 2, 4))

def getColor(x, y):
    return ImageGrab.grab().getpixel((x, y))

# ================= Mouse & Keyboard Handlers ================= #
def onClick(x, y, button, pressed):
    if button == mouse.Button.right and pressed:
        color = getColor(x, y)
        hex_color = getHex(color)
        colorList.append(hex_color)
        listbox.insert(tk.END, f"#{hex_color}")

def onRel(key):
    global exit_requested
    if key == keyboard.Key.delete:
        exit_requested = True
        print("Exiting color capture...")
        return False

# ================= GUI Action Functions ================= #
def start_capture():
    global exit_requested
    exit_requested = False
    messagebox.showinfo("Instructions", "Right-click on the screen to capture colors.\nPress the Delete key to stop capturing.")

    # Start listeners
    with keyboard.Listener(on_release=onRel) as k_listener:
        with mouse.Listener(on_click=onClick) as m_listener:
            k_listener.join()
            m_listener.join()
    messagebox.showinfo("Info", "Color capture stopped.")

def export_colors():
    if not colorList:
        messagebox.showwarning("Warning", "No colors to export!")
        return
    file_path = entry_path.get()
    if not file_path:
        file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text Files","*.txt")])
        if not file_path:
            return
    if isfile(file_path):
        messagebox.showerror("Error", f"{file_path} already exists!")
        return
    with open(file_path, "w") as f:
        for color in colorList:
            f.write(f"#{color}\n")
    messagebox.showinfo("Success", f"Colors exported to {file_path}")

def clear_colors():
    colorList.clear()
    listbox.delete(0, tk.END)

# ================= GUI Setup ================= #
root = tk.Tk()
root.title("Color Capture Tool")
root.geometry("500x400")

# Buttons
btn_start = tk.Button(root, text="Start Capturing Colors", command=start_capture, width=25)
btn_start.pack(pady=10)

btn_clear = tk.Button(root, text="Clear Colors", command=clear_colors, width=25)
btn_clear.pack(pady=5)

btn_export = tk.Button(root, text="Export Colors", command=export_colors, width=25)
btn_export.pack(pady=5)

# Entry for file path
entry_path = tk.Entry(root, width=40)
entry_path.pack(pady=5)
entry_path.insert(0, "Enter file path or leave empty to choose...")

# Listbox to display captured colors
listbox = tk.Listbox(root, width=50)
listbox.pack(pady=10, expand=True, fill=tk.BOTH)

# Exit button
btn_exit = tk.Button(root, text="Exit", command=root.destroy, width=25)
btn_exit.pack(pady=10)

root.mainloop()
