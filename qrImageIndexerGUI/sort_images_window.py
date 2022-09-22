from textwrap import wrap
import tkinter as tk
from PIL import ImageTk, Image, ImageOps

class ImageGrid(tk.Frame):
    def __init__(self, master, *args, **kwargs):
        tk.Frame.__init__(self, master, *args, **kwargs)


class KeyImagePresent(tk.Frame):
    
    def __init__(self, image_path : str, extracted_path : str, master, *args, **kwargs):
        tk.Frame.__init__(self, master, *args, **kwargs)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=0)
        
        self.original_image = Image.open(image_path)
        self.image = ImageTk.PhotoImage(self.original_image)
        self.image_canv = tk.Canvas(self, bd=0, highlightthickness=0)
        self.image_canv.create_image(0, 0, image=self.image, anchor=tk.NW, tags='IMG')
        # self.image_canv.pack(side=tk.TOP, fill=tk.BOTH)
        self.image_canv.grid(row=0, sticky=tk.NSEW)

        self.bind('<Configure>', self.resize)
        # self.image_lbl = tk.Label(self, image=self.image)
        # self.image_lbl.pack(side=tk.TOP, fill=tk.BOTH)

        self.path_lbl = tk.Label(self, text=extracted_path, justify=tk.CENTER)
        # self.path_lbl.pack(side=tk.BOTTOM, fill=tk.BOTH)
        self.path_lbl.grid(row=1, sticky=tk.NSEW)

    def resize(self, event):
        size = (event.width, event.height)
        resized = self.original_image.copy()
        resized.thumbnail(size,Image.ANTIALIAS)
        background = Image.new('RGBA', size, (255, 255, 255, 0))
        background.paste(
            resized, (int((size[0] - resized.size[0]) / 2), int((size[1] - resized.size[1]) / 2))
        )
        self.image = ImageTk.PhotoImage(background)
        self.image_canv.delete('IMG')
        self.image_canv.create_image(0, 0, image=self.image, anchor=tk.NW, tags='IMG')
        self.path_lbl.config(wraplength=event.width)
