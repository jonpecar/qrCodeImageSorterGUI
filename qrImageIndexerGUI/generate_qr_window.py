import tkinter as tk
from tkinter.scrolledtext import ScrolledText
from typing import Dict
import fitz

SAMPLE_TEXT = """Line 1
\tLine 1 indented
\t\tLine 1 twice indented
Line 2
Line 3
\tLine 3 indented"""

class PDFViewer(ScrolledText):
    def show(self, pdf_file):
        self.delete('1.0', 'end') # clear current content
        pdf = fitz.open(pdf_file) # open the PDF file
        self.images = []   # for storing the page images
        for page in pdf:
            pix = page.get_pixmap()
            pix1 = fitz.Pixmap(pix, 0) if pix.alpha else pix
            photo = tk.PhotoImage(data=pix1.tobytes('ppm'))
            # insert into the text box
            self.image_create('end', image=photo)
            self.insert('end', '\n')
            # save the image to avoid garbage collected
            self.images.append(photo)


class OptionsFrame(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent

        self.sort_sliceable_chk_var = tk.BooleanVar()
        self.sort_sliceable_chk_var.set(True)
        self.sort_sliceable_chk = tk.Checkbutton(self, text='Sort PDF to be sliceable (cut through page for ordered slips)', 
                                        variable=self.sort_sliceable_chk_var, onvalue=True,
                                        offvalue=False)

        self.sort_sliceable_chk.pack(side='top', fill='both')

        self.qr_for_headings_chk_var = tk.BooleanVar()
        self.qr_for_headings_chk_var.set(True)
        self.qr_for_headings_chk = tk.Checkbutton(self, text='Include QR codes for heading all lines (not just last level)', 
                                        variable=self.qr_for_headings_chk_var, onvalue=True,
                                        offvalue=False)

        self.qr_for_headings_chk.pack(side='top', fill='both')

        self.repeat_headings_chk_var = tk.BooleanVar()
        self.repeat_headings_chk_var.set(True)
        self.repeat_headings_chk = tk.Checkbutton(self, text='Repeat heading text on every line', 
                                        variable=self.repeat_headings_chk_var, onvalue=True,
                                        offvalue=False)

        self.repeat_headings_chk.pack(side='top', fill='both')

        self.use_prefix_chk_var = tk.BooleanVar()
        self.use_prefix_chk_var.set(True)
        self.use_prefix_chk = tk.Checkbutton(self, text='Include prefix in QR code text', 
                                        variable=self.use_prefix_chk_var, onvalue=True,
                                        offvalue=False, command=self.prefix_toggle)

        self.use_prefix_chk.pack(side='top', fill='both')

        self.prefix_frame = tk.Frame(self)
        self.prefix_frame.pack(side='top', fill='both')

        self.prefix_label = tk.Label(self.prefix_frame, text="Prefix:")
        self.prefix_label.pack(side='left', fill='both')

        self.prefix_input = tk.Entry(self.prefix_frame)
        self.prefix_input.insert(0, r"{image}")
        self.prefix_input.pack(side='right', fill='both', expand=True)




    def get_check_states(self) -> Dict[str, bool]:
        return {
            'sliceable' : self.sort_sliceable_chk_var.get(),
            'qr_headings' : self.qr_for_headings_chk_var.get(),
            'repeat_headings' : self.repeat_headings_chk_var.get(),
            'include_prefix' : self.use_prefix_chk_var.get(),
        }

    def get_prefix(self) -> str:
        return self.prefix_input.get(0, tk.END)
    
    def prefix_toggle(self):
        if not self.use_prefix_chk_var.get():
            self.prefix_frame.pack_forget()
        else:
            self.prefix_frame.pack(side='top', fill='both')




class GenerateQRWindow(tk.Toplevel):
    def __init__(self, master, *args, **kwargs):
        tk.Toplevel.__init__(self, master, *args, **kwargs)
        self.geometry("1200x800")
        self.title("Generate QR Codes")

        self.top_frame = tk.Frame(self)
        self.top_frame.pack(fill='x', side='top')

        self.save_button = tk.Button(self.top_frame, text='Save PDF to File', command=self.save_pdf)
        self.save_button.pack(fill='x', side='left', expand=True)

        self.generate_sample_button = tk.Button(self.top_frame, text='Update PDF Sample', command=self.update_pdf_sample)
        self.generate_sample_button.pack(fill='x', side='right', expand=True)

        self.left_frame = tk.Frame(self)
        self.left_frame.pack(fill='both', expand=True, side='left')

        self.right_frame = tk.Frame(self)
        self.right_frame.pack(fill='both', expand=True, side='right')

        self.chk_box_frame = OptionsFrame(self.left_frame)
        self.chk_box_frame.pack(fill='both', side='top')

        self.enter_txt = ScrolledText(self.left_frame)
        self.enter_txt.insert("1.0", chars=SAMPLE_TEXT)
        self.enter_txt.pack(fill='both', expand=True, side='bottom')

        self.doc_viewer = PDFViewer(self.right_frame)
        self.doc_viewer.pack(fill='both', expand=True, side='top')
        self.doc_viewer.show('test.pdf')

    def save_pdf(self):
        print('save button')

    def text_changed(self):
        print('text changed')

    def update_pdf_sample(self):
        print('updated sample view')