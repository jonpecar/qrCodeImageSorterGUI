import customtkinter as ctk

import tkinter as tk
from tkinter import filedialog, messagebox
from typing import Dict

from PIL import Image

import io

import fitz
from qrImageIndexer.qr_generator import load_lines
from qrImageIndexer.write_pdf_fpf2 import FPDF
from qrImageIndexer.generate_qr_wrapper import generate_qr_pdf

from qrImageIndexerGUI.image_grid import ImageGrid

FRAME_PAD_PX = 10

SAMPLE_TEXT = """Line 1
\tLine 1 indented
\t\tLine 1 twice indented
Line 2
Line 3
\tLine 3 indented"""

class PDFViewer(ImageGrid):
    def __init__(self, master, *args, **kwargs):
        ImageGrid.__init__(self, master, 'FILL', *args, **kwargs)
    
    def show(self, pdf_file, stream=None):
        self.clear_grid()
        pdf = fitz.Document(pdf_file, stream=stream) # open the PDF file
        for i, page in enumerate(pdf):
            pix = page.get_pixmap(dpi=300)
            pix1 = fitz.Pixmap(pix, 0) if pix.alpha else pix
            photo = Image.open(io.BytesIO(pix1.tobytes('png')))
            # insert into the text box
            self.add_plain_image(photo, i)
        self.rebuild_grid()


class OptionsFrame(ctk.CTkFrame):
    def __init__(self, parent, *args, **kwargs):
        ctk.CTkFrame.__init__(self, parent, *args, **kwargs)
        self.parent = parent

        self.sort_sliceable_chk_var = tk.BooleanVar()
        self.sort_sliceable_chk_var.set(True)
        self.sort_sliceable_chk = ctk.CTkCheckBox(self, text='Sort PDF to be sliceable (cut through page for ordered slips)', 
                                        variable=self.sort_sliceable_chk_var, onvalue=True,
                                        offvalue=False)

        self.sort_sliceable_chk.pack(side=tk.TOP, fill=tk.BOTH)

        self.qr_for_headings_chk_var = tk.BooleanVar()
        self.qr_for_headings_chk_var.set(True)
        self.qr_for_headings_chk = ctk.CTkCheckBox(self, text='Include QR codes for heading all lines (not just last level)', 
                                        variable=self.qr_for_headings_chk_var, onvalue=True,
                                        offvalue=False)

        self.qr_for_headings_chk.pack(side=tk.TOP, fill=tk.BOTH)

        self.repeat_headings_chk_var = tk.BooleanVar()
        self.repeat_headings_chk_var.set(True)
        self.repeat_headings_chk = ctk.CTkCheckBox(self, text='Repeat heading text on every line', 
                                        variable=self.repeat_headings_chk_var, onvalue=True,
                                        offvalue=False)

        self.repeat_headings_chk.pack(side=tk.TOP, fill=tk.BOTH)

        self.use_prefix_chk_var = tk.BooleanVar()
        self.use_prefix_chk_var.set(True)
        self.use_prefix_chk = ctk.CTkCheckBox(self, text='Include prefix in QR code text', 
                                        variable=self.use_prefix_chk_var, onvalue=True,
                                        offvalue=False, command=self.prefix_toggle)

        self.use_prefix_chk.pack(side=tk.TOP, fill=tk.BOTH)

        self.prefix_frame = ctk.CTkFrame(self)
        self.prefix_frame.pack(side=tk.TOP, fill=tk.BOTH)

        self.prefix_label = ctk.CTkLabel(self.prefix_frame, text="Prefix:")
        self.prefix_label.pack(side=tk.LEFT, fill=tk.BOTH)

        self.prefix_input = ctk.CTkEntry(self.prefix_frame)
        self.prefix_input.insert(0, r"{image}")
        self.prefix_input.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)




    def get_check_states(self) -> Dict[str, bool]:
        return {
            'sliceable' : self.sort_sliceable_chk_var.get(),
            'qr_headings' : self.qr_for_headings_chk_var.get(),
            'repeat_headings' : self.repeat_headings_chk_var.get(),
            'use_prefix' : self.use_prefix_chk_var.get(),
        }

    def get_prefix(self) -> str:
        return self.prefix_input.get()
    
    def prefix_toggle(self):
        if not self.use_prefix_chk_var.get():
            self.prefix_frame.pack_forget()
        else:
            self.prefix_frame.pack(side=tk.TOP, fill=tk.BOTH)




class GenerateQRWindow(ctk.CTkToplevel):
    def __init__(self, master, *args, **kwargs):
        ctk.CTkToplevel.__init__(self, master, *args, **kwargs)
        self.geometry("1200x800")
        self.title("Generate QR Codes")

        self.top_frame = ctk.CTkFrame(self)
        self.top_frame.pack(fill='x', side=tk.TOP)

        self.save_button = ctk.CTkButton(self.top_frame, text='Save PDF to File', command=self.save_pdf)
        self.save_button.pack(fill='x', side=tk.LEFT, expand=True)

        self.generate_sample_button = ctk.CTkButton(self.top_frame, text='Update PDF Sample', command=self.update_pdf_sample)
        self.generate_sample_button.pack(fill='x', side=tk.RIGHT, expand=True)

        self.left_frame = ctk.CTkFrame(self)
        self.left_frame.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)

        self.right_frame = ctk.CTkFrame(self)
        self.right_frame.pack(fill=tk.BOTH, expand=True, side=tk.RIGHT)

        self.opt_frame = OptionsFrame(self.left_frame)
        self.opt_frame.pack(fill=tk.BOTH, side=tk.TOP)

        self.enter_txt = ctk.CTkTextbox(self.left_frame)
        self.enter_txt.insert("1.0", text=SAMPLE_TEXT)
        self.enter_txt.pack(fill=tk.BOTH, expand=True, side='bottom',
                            padx=FRAME_PAD_PX, pady=FRAME_PAD_PX)

        self.doc_viewer = PDFViewer(self.right_frame)#,
            # bg=self.cget('fg_color')[1] if ctk.get_appearance_mode() == 'Dark' else self.cget('fg_color')[0])
        self.doc_viewer.pack(fill=tk.BOTH, expand=True, side=tk.TOP,
                            padx=FRAME_PAD_PX, pady=FRAME_PAD_PX)

        self.update_pdf_sample() #Update the PDF here so that it will contain the sample text and use all the default settings

    def save_pdf(self):
        if self.has_invalid_path_chars():
            proceed = messagebox.askyesno('Found Invalid File Characters', 
                                             "One or more of the following characters were found in your text:"
                                              + " '<', '>', ':', '\"', '|', '\\', '/', '?', '*'. "
                                              + "These are not valid characters for file paths in Windows." 
                                              + " If you proceed these will be removed when sorting the images"
                                              + " except for '\\' and '/' which will create new folders." 
                                              + "\n\nDo you wish to proceed?")
            if not proceed: return
        
        file = filedialog.asksaveasfile(mode='wb', confirmoverwrite=True, defaultextension='.pdf',
                                        filetypes=[['PDF Files', '*.pdf']])
        pdf = self.generate_pdf()
        pdf.output(file)
        file.close()
        messagebox.showinfo("File Saved", "File successfully saved.")

    def update_pdf_sample(self):
        self.doc_viewer.show(None, self.generate_pdf().output())

    def generate_pdf(self) -> FPDF:
        check_states = self.opt_frame.get_check_states()
        text = self.enter_txt.get("1.0", tk.END)
        text = text.split('\n')
        data = load_lines(text)
        prefix = ''
        if check_states['use_prefix']:
            prefix = self.opt_frame.get_prefix()
        return generate_qr_pdf(data, check_states['qr_headings'], check_states['repeat_headings'],
                                check_states['sliceable'], prefix)
    
    def has_invalid_path_chars(self) -> bool:
        invalid_chars_windows = ['<', '>', ':', '"', '|', '\\', '/', '?', '*']
        text = self.enter_txt.get("1.0", tk.END)
        has_invalid_chars = [char in text for char in invalid_chars_windows]
        return True in has_invalid_chars