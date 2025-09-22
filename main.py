"""
Color Capture Tool GUI

This Tkinter-based application allows users to capture colors from the screen by right-clicking,
display them as hexadecimal codes in a list, export them to a file, clear the list, and exit the program.
"""

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
        return False

# ================= GUI Action Functions ================= #
def start_capture():
    global exit_requested
    exit_requested = False
    messagebox.showinfo("Instructions", "Right-click anywhere on your screen to capture colors.\nPress Delete to stop capturing.")
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
    if not file_path.strip():
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
root.geometry("500x450")

# Description Label
desc = "Capture colors from your screen by right-clicking.\nView hex codes, export to file, or clear the list."
label_desc = tk.Label(root, text=desc, justify=tk.LEFT, wraplength=480)
label_desc.pack(pady=10)

# Buttons
tk.Button(root, text="Start Capturing Colors", command=start_capture, width=30).pack(pady=5)
tk.Button(root, text="Clear Colors", command=clear_colors, width=30).pack(pady=5)
tk.Button(root, text="Export Colors", command=export_colors, width=30).pack(pady=5)

# Entry for file path
entry_path = tk.Entry(root, width=50)
entry_path.pack(pady=5)
entry_path.insert(0, "Enter file path or leave empty to choose...")

# Listbox to show captured colors
listbox = tk.Listbox(root, width=50)
listbox.pack(pady=10, expand=True, fill=tk.BOTH)

# Exit Button
tk.Button(root, text="Exit", command=root.destroy, width=30).pack(pady=10)

root.mainloop()
