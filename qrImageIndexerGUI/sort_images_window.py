from functools import partial
from threading import Thread
import os
from typing import Dict, List

import customtkinter as ctk
from customtkinter import ThemeManager
import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
from PIL import ImageTk, Image
import natsort

from qrImageIndexer import photo_sorter
from multiprocessing import Pool, cpu_count


DEFAULT_COLUMN_WIDTH = 400

class ImageScan(Thread):
    def __init__(self, files : List[str], prefix : str):
        Thread.__init__(self)

        self.results = {}
        self.done = 0
        self.percent = 0
        self.files = files
        self.prefix = prefix
        self.non_image_files = []

    def run(self):
        cores = cpu_count()
        self.non_image_files = [x for x in self.files if not photo_sorter.check_if_image(x)[0]]
        self.image_files = [x for x in self.files if photo_sorter.check_if_image(x)[0]]
        func = partial(photo_sorter.get_qr_mt, string_header=self.prefix, binarization=True)
        with Pool(processes=cores) as pool:
            self.done = 0
            self.percent
            for image_path, qr_string in pool.imap(func, self.image_files):
                self.done += 1
                self.percent = (self.done * 100)//len(self.image_files)
                if qr_string:
                    self.results[image_path] = qr_string

class ImageCopy(Thread):
    def __init__(self, scan_results : Dict[str, str], in_directory : str, out_directory : str):
        Thread.__init__(self)
        self.scan_results = scan_results
        self.in_directory = in_directory
        self.out_directory = out_directory

    def run(self):
        photo_sorter.sort_directory_exisitng_results(self.scan_results, self.in_directory, self.out_directory, False)

class ScanImagesWindow(ctk.CTkToplevel):
    def __init__(self, master, *args, **kwargs):
        ctk.CTkToplevel.__init__(self, master, *args, **kwargs)
        self.geometry("1200x800")
        self.title("Sort Images by QR Codes")
        self.button_frame = ctk.CTkFrame(self)
        self.scan_opts = ScanOptionsFrame(self)
        self.image_grid = ImageGrid(self)
        self.scan_dir_button = ctk.CTkButton(self.button_frame, text='Scan Images From Directory (Will clear existing results)',
                                        command=self.scan_button_clicked)
        self.save_sorted_images_button = ctk.CTkButton(self.button_frame, text='Save Sorted Images in Directory',
                                                command=self.save_button_clicked)
        self.progress = ctk.CTkProgressBar(self, orient=tk.HORIZONTAL, mode='determinate')
        self.progress.set(0)

        self.button_frame.pack(side=tk.TOP, fill=tk.X)
        self.progress.pack(side=tk.TOP, fill=tk.X)
        self.scan_opts.pack(side=tk.TOP, fill=tk.BOTH)
        self.image_grid.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)
        self.scan_dir_button.pack(side=tk.LEFT, fill=tk.X)
        self.save_sorted_images_button.pack(side=tk.RIGHT, fill=tk.X)

        self.in_directory = ''
        self.out_directory = ''

        self.non_image_files = []
        self.scan_results = {}

    def scan_button_clicked(self):
        directory = filedialog.askdirectory()

        if os.path.isdir(directory):
            self.in_directory = directory
            self.image_grid.clear_grid()
            files = [os.path.join(self.in_directory, x) for x in os.listdir(self.in_directory)]
            scan_thread = ImageScan(files, self.scan_opts.get_prefix())
            scan_thread.start()
            self.monitor_progress_image_scan(scan_thread)

    def save_button_clicked(self):
        if not os.path.isdir(self.in_directory) or not self.scan_results:
            messagebox.showerror('No Input Data', 'Did not detect appropriate input date. ' +
                                'Please make sure that you have scanned an input directory with QR codes.')
            return
        directory = filedialog.askdirectory()

        if os.path.isdir(directory):
            self.out_directory = directory
            save_thread = ImageCopy(self.scan_results, self.in_directory, self.out_directory)
            save_thread.start()
            self.monitor_progress_image_save(save_thread)

    def disable_buttons(self):
        """
            Disable buttons while processes running to avoid clash
        """
        self.save_sorted_images_button['state'] = tk.DISABLED
        self.scan_dir_button['state'] = tk.DISABLED

    def enable_buttons(self):
        """
            Enable buttons when processes done
        """
        self.save_sorted_images_button['state'] = tk.NORMAL
        self.scan_dir_button['state'] = tk.NORMAL

    def monitor_progress_image_scan(self, thread : ImageScan):
        if thread.is_alive():
            self.disable_buttons()
            self.progress.set(float(thread.percent)/100)
            self.after(100, lambda: self.monitor_progress_image_scan(thread))
        else:
            self.enable_buttons()
            self.progress.set(0)
            self.scan_results = ScanImagesWindow.sort_results_dict(thread.results)
            for file in self.scan_results:
                self.image_grid.add_image(file, self.scan_results[file])
            self.non_image_files = thread.non_image_files[:]
            self.image_grid.rebuild_grid()

    def monitor_progress_image_save(self, thread : ImageCopy):
        if thread.is_alive():
            self.disable_buttons()
            self.progress.configure(mode='indeterminate')
            self.after(100, lambda: self.monitor_progress_image_save(thread))
        else:
            self.enable_buttons()
            self.progress.configure(mode='determinate')
            self.progress.set(0)
            messagebox.showinfo('Copy Complete', 'Copying images to output directory is complete.')

    def sort_results_dict(dict : Dict[str, str]) -> Dict[str, str]:
        sorted_keys = natsort.natsorted(dict.keys())
        return {key:dict[key] for key in sorted_keys}

class ScanOptionsFrame(ctk.CTkFrame):
    def __init__(self, parent, *args, **kwargs):
        ctk.CTkFrame.__init__(self, parent, *args, **kwargs)

        self.has_prefix_chk_var = tk.BooleanVar()
        self.has_prefix_chk = ctk.CTkCheckBox(self, text='QR codes have prefix',
                                            variable=self.has_prefix_chk_var, onvalue=True,
                                            offvalue=False)
        self.prefix_frame = ctk.CTkFrame(self)
        self.prefix_label = ctk.CTkLabel(self.prefix_frame, text="Prefix:")
        self.prefix_input = ctk.CTkEntry(self.prefix_frame)
        
        self.has_prefix_chk_var.set(True)
        self.has_prefix_chk.pack(side=tk.TOP, fill=tk.BOTH)
        self.prefix_frame.pack(side=tk.TOP, fill=tk.BOTH)
        self.prefix_label.pack(side=tk.LEFT, fill=tk.BOTH)
        self.prefix_input.insert(0, r"{image}")
        self.prefix_input.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

    def get_prefix(self) -> str:
        if self.has_prefix_chk_var.get():
            return self.prefix_input.get()
        else:
            return ''


class ImageGrid(ctk.CTkFrame):
    def __init__(self, master, column_wdith :int = DEFAULT_COLUMN_WIDTH, *args, **kwargs):
        ctk.CTkFrame.__init__(self, master, *args, **kwargs)
        self.images : Dict[str, KeyImagePresent] = {}
        self.column_width = column_wdith

        self.vscrollbar = ctk.CTkScrollbar(self)
        self.scrolled_canvas = ctk.CTkCanvas(self, bd=0, highlightthickness=0, 
                                            bg=ThemeManager.single_color(self.fg_color, self.master.appearance_mode))
        self.frame = ctk.CTkFrame(self.scrolled_canvas)

        self.vscrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.scrolled_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.scrolled_canvas.create_window((0,0), window=self.frame, anchor=tk.NW,
                                            tags='self.frame')

        self.vscrollbar.configure(command=self.scrolled_canvas.yview)
        self.scrolled_canvas.configure(yscrollcommand=self.vscrollbar.set)

        self.scrolled_canvas.xview_moveto(0)
        self.scrolled_canvas.yview_moveto(0)

        self.scrolled_canvas.bind('<Configure>', self.resize_canvas)
        self.frame.bind('<Configure>', self.on_frame_configure)

        self.used_cols = 0

    @property
    def items_sorted(self):
        sorted_keys = natsort.natsorted(self.images.keys())
        return [self.images[x] for x in sorted_keys]

    def clear_grid(self):
        for key in self.images:
            self.images[key].destroy()
        self.images.clear()

    def on_frame_configure(self, event):
        self.scrolled_canvas.configure(scrollregion=self.scrolled_canvas.bbox(tk.ALL))

    def resize_canvas(self, event):
        """
            Resize has occurred, rebuild the grid based on the resize width/height
        """
        size = (event.width, event.height)
        self.rebuild_grid(size)

    def rebuild_grid(self, size = None):
        """
            Rebuild the grid based on the provided size
        """
        if size is None:
            size = (self.frame.winfo_width(), self.frame.winfo_height())
        columns = size[0]//self.column_width
        
        if columns == 0:
            columns = 1

        # Track the highest number of columns used so that they can
        # all be reset to empty if needed
        if columns > self.used_cols:
            self.used_cols = columns

        for i in range(columns):
            self.frame.columnconfigure(i, weight=1)

        if columns < self.used_cols:
            for i in range(columns, self.used_cols):
                self.frame.columnconfigure(i, weight=0)

        gridified_items = ImageGrid.gridify_items(self.items_sorted, columns)
        for irow, row in enumerate(gridified_items):
            item : KeyImagePresent
            for icol, item in enumerate(row):
                item.grid(column=icol, row=irow, sticky=tk.NSEW)

    def gridify_items(items : List, columns : int) -> List[List]:
        """
            Takes a single dimensional list and splits it into a list of
            lists that contains the specified number of columns
        """
        result = []
        current_row = None
        for index, item in enumerate(items):
            column = index % columns
            if column == 0:
                current_row = []
                result.append(current_row)
            current_row.append(item)
        
        return result

    def add_image(self, image_path : str, qr_value : str) -> None:
        image = KeyImagePresent(image_path, qr_value, self.frame)
        self.images[image_path] = image

class KeyImagePresent(ctk.CTkFrame):
    
    def __init__(self, image_path : str, extracted_path : str, master, *args, **kwargs):
        ctk.CTkFrame.__init__(self, master, *args, **kwargs)
        self.configure(highlightbackground='lightgrey', highlightthickness=1)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=0)
        self.rowconfigure(1, weight=1)
        self.rowconfigure(2, weight=0)
        
        self.original_image = Image.open(image_path)
        self.image = ImageTk.PhotoImage(self.original_image)
        self.image_canv = ctk.CTkCanvas(self, bd=0, highlightthickness=0)
        self.image_canv.create_image(0, 0, image=self.image, anchor=tk.NW, tags='IMG')
        # self.image_canv.pack(side=tk.TOP, fill=tk.BOTH)
        self.image_canv.grid(row=1, sticky=tk.NSEW)

        self.bind('<Configure>', self.resize)
        # self.image_lbl = tk.Label(self, image=self.image)
        # self.image_lbl.pack(side=tk.TOP, fill=tk.BOTH)

        self.path = extracted_path
        self.path_lbl = ctk.CTkLabel(self, text=self.path, justify=tk.CENTER)
        # self.path_lbl.pack(side=tk.BOTTOM, fill=tk.BOTH)
        self.path_lbl.grid(row=2, sticky=tk.NSEW)

        self.image_path = image_path
        self.image_path_lbl = ctk.CTkLabel(self, text=self.image_path, justify=tk.CENTER)
        # self.path_lbl.pack(side=tk.BOTTOM, fill=tk.BOTH)
        self.image_path_lbl.grid(row=0, sticky=tk.NSEW)

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
        self.path_lbl.configure(wraplength=event.width)
