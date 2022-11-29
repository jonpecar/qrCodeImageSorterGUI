import customtkinter as ctk
from tkinter import Pack, Grid, Place
from tkinter.constants import RIGHT, LEFT, Y, BOTH

class CustomScrolledText(ctk.CTkTextbox):
    def __init__(self, master=None, **kw):
        self.frame = ctk.CTkFrame(master)
        self.vbar = ctk.CTkScrollbar(self.frame)
        self.vbar.pack(side=RIGHT, fill=Y)

        kw.update({'yscrollcommand': self.vbar.set})
        ctk.CTkTextbox.__init__(self, self.frame, **kw)
        self.pack(side=LEFT, fill=BOTH, expand=True)
        self.vbar['command'] = self.yview

        # Copy geometry methods of self.frame without overriding Text
        # methods -- hack!
        text_meths = vars(ctk.CTkTextbox).keys()
        methods = vars(Pack).keys() | vars(Grid).keys() | vars(Place).keys()
        methods = methods.difference(text_meths)

        for m in methods:
            if m[0] != '_' and m != 'config' and m != 'configure':
                setattr(self, m, getattr(self.frame, m))

    def __str__(self):
        return str(self.frame)