from typing import Dict, List, Union

import tkinter as tk
import customtkinter as ctk
import natsort
from PIL import ImageTk, Image

DEFAULT_COLUMN_WIDTH = 400

class PlainImagePresent(ctk.CTkFrame):
    
    def __init__(self, master, image: Image.Image, *args, **kwargs):
        ctk.CTkFrame.__init__(self, master, *args, **kwargs)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        
        self.original_image: Image.Image = image
        self.image = ImageTk.PhotoImage(self.original_image)
        self.image_canv = ctk.CTkCanvas(self, bd=0, highlightthickness=0)
        self.image_canv.create_image(0, 0, image=self.image, anchor=tk.NW, tags='IMG')
        # self.image_canv.pack(side=tk.TOP, fill=tk.BOTH)
        self.image_canv.grid(row=0, sticky=tk.NSEW)

        self.bind('<Configure>', self.resize)
        # self.image_lbl = tk.Label(self, image=self.image)
        # self.image_lbl.pack(side=tk.TOP, fill=tk.BOTH)

    def resize_by_width(self, width):
        image_ar = self.original_image.size[1] / self.original_image.size[0]
        adjusted_size = (width, int(width * image_ar))
        resized = self.original_image.copy()
        resized.thumbnail(adjusted_size,Image.ANTIALIAS)
        background = Image.new('RGBA', adjusted_size, (255, 255, 255, 0))
        background.paste(
            resized, (int((adjusted_size[0] - resized.size[0]) / 2), int((adjusted_size[1] - resized.size[1]) / 2))
        )
        self.image = ImageTk.PhotoImage(background)
        self.image_canv.delete('IMG')
        self.image_canv.create_image(0, 0, image=self.image, anchor=tk.NW, tags='IMG')
        self.image_canv.configure(width=adjusted_size[0], height=adjusted_size[1])

    def resize(self, event):
        self.resize_by_width(event.width)


class KeyImagePresent(ctk.CTkFrame):
    
    def __init__(self, master, image_path : str, extracted_path : str, *args, **kwargs):
        ctk.CTkFrame.__init__(self, master, *args, **kwargs)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=0)
        self.rowconfigure(1, weight=1)
        self.rowconfigure(2, weight=0)
        
        self.original_image = Image.open(image_path)
        self.image = ImageTk.PhotoImage(self.original_image)
        self.image_canv = ctk.CTkCanvas(self, bd=0, highlightthickness=0)
        self.image_canv.create_image(0, 0, image=self.image, anchor=tk.NW, tags='IMG')
        # self.image_canv.pack(side=tk.TOP, fill=tk.BOTH)
        self.image_canv.grid(row=0, sticky=tk.NSEW)

        self.bind('<Configure>', self.resize)
        # self.image_lbl = tk.Label(self, image=self.image)
        # self.image_lbl.pack(side=tk.TOP, fill=tk.BOTH)

        self.path = extracted_path
        self.path_lbl = ctk.CTkLabel(self, text=self.path, justify=tk.CENTER)
        # self.path_lbl.pack(side=tk.BOTTOM, fill=tk.BOTH)
        self.path_lbl.grid(row=1, sticky=tk.NSEW)

        self.image_path = image_path
        self.image_path_lbl = ctk.CTkLabel(self, text=self.image_path, justify=tk.CENTER)
        # self.path_lbl.pack(side=tk.BOTTOM, fill=tk.BOTH)
        self.image_path_lbl.grid(row=2, sticky=tk.NSEW)

    def resize_by_width(self, width):
        image_ar = self.original_image.size[1] / self.original_image.size[0]
        adjusted_size = (width, int(width * image_ar))
        resized = self.original_image.copy()
        resized.thumbnail(adjusted_size,Image.ANTIALIAS)
        background = Image.new('RGBA', adjusted_size, (255, 255, 255, 0))
        background.paste(
            resized, (int((adjusted_size[0] - resized.size[0]) / 2), int((adjusted_size[1] - resized.size[1]) / 2))
        )
        self.image = ImageTk.PhotoImage(background)
        self.image_canv.delete('IMG')
        self.image_canv.create_image(0, 0, image=self.image, anchor=tk.NW, tags='IMG')
        self.image_canv.configure(width=adjusted_size[0], height=adjusted_size[1])

    def resize(self, event):
        self.resize_by_width(event.width)


class ImageGrid(ctk.CTkFrame):
    def __init__(self, master, column_width: Union[int, str] = DEFAULT_COLUMN_WIDTH, *args, **kwargs):
        ctk.CTkFrame.__init__(self, master, *args, **kwargs)
        self.images : Dict[str, Union[PlainImagePresent, KeyImagePresent]] = {}
        self._column_width_setting = column_width

        self.vscrollbar = ctk.CTkScrollbar(self)
        self.scrolled_canvas = ctk.CTkCanvas(self, bd=0, highlightthickness=0,
                            bg=self.cget('fg_color')[1] if ctk.get_appearance_mode() == 'Dark' else self.cget('fg_color')[0])
        self.frame = ctk.CTkFrame(self.scrolled_canvas)

        self.vscrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.scrolled_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.scrolled_canvas.create_window((0,0), window=self.frame, anchor=tk.NW,
                                            tags='self.frame')

        self.vscrollbar.configure(command=self.scrolled_canvas.yview)
        self.scrolled_canvas.configure(yscrollcommand=self.vscrollbar.set)

        self.scrolled_canvas.xview_moveto(0)
        self.scrolled_canvas.yview_moveto(0)

        self.bind('<Configure>', self.resize_canvas)
        self.frame.bind('<Configure>', self.on_frame_configure)

        self.used_cols = 0

    @property
    def column_width(self) -> int:
        if isinstance(self._column_width_setting, int):
            return self._column_width_setting
        elif isinstance(self._column_width_setting, str) and self._column_width_setting == 'FILL':
            return self.winfo_width()
        else:
            raise ValueError(f'Invalid setting for column width: {self._column_width_setting}')

    @property
    def is_single_full_width(self) -> bool:
        if self._column_width_setting == 'FILL':
            return True
        else:
            return False

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
            item : ctk.CTkFrame
            for icol, item in enumerate(row):
                item.grid(column=icol, row=irow, sticky=tk.NSEW)
                if self.is_single_full_width: item.resize_by_width(self.column_width)

    @staticmethod
    def gridify_items(items : List, columns : int) -> List[List[Union[PlainImagePresent, KeyImagePresent]]]:
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

    def add_key_image(self, image_path : str, qr_value : str) -> None:
        image = KeyImagePresent(self.frame, image_path, qr_value)
        self.images[image_path] = image

    def add_plain_image(self, image_in: tk.PhotoImage, index: int) -> None:
        image = PlainImagePresent(self.frame, image_in)
        self.images[str(index)] = image
