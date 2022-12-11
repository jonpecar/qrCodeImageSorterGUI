from functools import partial
from threading import Thread
import os
from typing import Dict, List
import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox

import customtkinter as ctk
import natsort

from qrImageIndexer import photo_sorter
from multiprocessing import Pool, cpu_count
from .image_grid import ImageGrid




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
        self.progress = ctk.CTkProgressBar(self, mode='determinate')
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
                self.image_grid.add_key_image(file, self.scan_results[file])
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

    @staticmethod
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