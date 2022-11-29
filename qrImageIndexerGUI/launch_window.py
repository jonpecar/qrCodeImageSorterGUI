import customtkinter as ctk
from qrImageIndexerGUI import generate_qr_window
from qrImageIndexerGUI.sort_images_window import ScanImagesWindow

class LaunchWindow(ctk.CTkFrame):
    def __init__(self, parent, *args, **kwargs):
        ctk.CTkFrame.__init__(self, parent, *args, **kwargs)
        self.parent = parent

        self.generate_button = ctk.CTkButton(master=self, text='Generate QR Codes', command=self.click_generate_button)
        self.generate_button.pack(fill='both', side='top', expand=True)
        self.sort_button = ctk.CTkButton(master=self, text='Sort Images', command=self.click_sort_button)
        self.sort_button.pack(fill='both', side='bottom', expand=True)

        self.pack(side='top', fill='both', expand=True)

    def click_generate_button(self):
        generate_qr_window.GenerateQRWindow(self)

    def click_sort_button(self):
        ScanImagesWindow(self)