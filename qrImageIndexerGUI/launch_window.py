import tkinter as tk
from qrImageIndexerGUI import generate_qr_window
from qrImageIndexerGUI.sort_images_window import ScanImagesWindow

class LaunchWindow(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent

        self.generate_button = tk.Button(master=self, text='Generate QR Codes', command=self.click_generate_button)
        self.generate_button.pack(fill='both', side='top', expand=True)
        self.sort_button = tk.Button(master=self, text='Sort Images', command=self.click_sort_button)
        self.sort_button.pack(fill='both', side='bottom', expand=True)

        self.pack(side='top', fill='both', expand=True)

    def click_generate_button(self):
        generate_qr_window.GenerateQRWindow(self)

    def click_sort_button(self):
        ScanImagesWindow(self)