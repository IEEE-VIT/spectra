import tkinter as tk
from tkinter import messagebox, filedialog
from pynput import keyboard, mouse
from PIL import ImageGrab
import json
import os

# Persistent history file
HISTORY_FILE = "color_history.json"
colorList = []
exit_requested = False
listener_running = False

# ---------------- Persistence Functions ---------------- #
def load_history():
    global colorList
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, "r") as f:
                colorList = json.load(f)
        except Exception:
            colorList = []
    else:
        colorList = []

def save_history():
    with open(HISTORY_FILE, "w") as f:
        json.dump(colorList, f)

def clear_history():
    global colorList
    colorList = []
    save_history()
    update_listbox()
    messagebox.showinfo("Info", "History cleared.")

# ---------------- Utility Functions ---------------- #
def getHex(rgb):
    return ''.join(hex(v)[2:].upper().zfill(2) for v in rgb)

def getColor(x, y):
    return ImageGrab.grab().getpixel((x, y))

def onClick(x, y, button, press):
    global listener_running
    if button == mouse.Button.right and press and listener_running:
        color = getColor(x, y)
        hex_color = getHex(color)
        colorList.append(hex_color)
        save_history()
        update_listbox()

def onRel(key):
    global exit_requested, listener_running
    if key == keyboard.Key.delete and listener_running:
        exit_requested = True
        listener_running = False
        messagebox.showinfo("Capture Stopped", "Stopped capturing colors. (Delete pressed)")
        return False

def start_capture():
    global listener_running, exit_requested
    if listener_running:
        messagebox.showwarning("Warning", "Capture is already running!")
        return
    exit_requested = False
    listener_running = True
    messagebox.showinfo("Instructions", "Right-click to capture colors.\nPress Delete to stop.")
    with keyboard.Listener(on_release=onRel) as k:
        with mouse.Listener(on_click=onClick) as m:
            k.join()
            m.join()

def export_colors():
    if not colorList:
        messagebox.showwarning("Warning", "No colors to export!")
        return
    file_path = filedialog.asksaveasfilename(
        defaultextension=".txt",
        filetypes=[("Text files", "*.txt")]
    )
    if not file_path:
        return
    if os.path.exists(file_path):
        messagebox.showerror("Error", f"{file_path} already exists.")
        return
    try:
        with open(file_path, "w") as f:
            for color in colorList:
                f.write(f"#{color}\n")
        messagebox.showinfo("Success", f"Colors exported to {file_path}")
    except Exception as e:
        messagebox.showerror("Error", str(e))

# ---------------- GUI ---------------- #
def update_listbox():
    listbox.delete(0, tk.END)
    for c in colorList:
        listbox.insert(tk.END, f"#{c}")
    count_label.config(text=f"Total Colors: {len(colorList)}")

def exit_app():
    root.destroy()

# Load history initially
load_history()

# Build GUI
root = tk.Tk()
root.title("Color Capture Tool")
root.geometry("400x400")

btn_start = tk.Button(root, text="Start Capturing", command=lambda: root.after(100, start_capture))
btn_start.pack(pady=5)

btn_export = tk.Button(root, text="Export Colors", command=export_colors)
btn_export.pack(pady=5)

btn_clear = tk.Button(root, text="Clear History", command=clear_history)
btn_clear.pack(pady=5)

count_label = tk.Label(root, text=f"Total Colors: {len(colorList)}")
count_label.pack(pady=5)

listbox = tk.Listbox(root, height=10, width=30)
listbox.pack(pady=5)

btn_exit = tk.Button(root, text="Exit", command=exit_app)
btn_exit.pack(pady=10)

update_listbox()
root.mainloop()