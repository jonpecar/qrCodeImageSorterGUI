from qrImageIndexerGUI import sort_images_window
import pytest
import tkinter as tk

def test_gridify_items_multiline():
    input = [1, 2, 3, 4, 5, 6, 7, 8, 9]
    columns = 4
    expected = [
        [1, 2, 3, 4],
        [5, 6, 7, 8],
        [9]
    ]

    assert expected == sort_images_window.ImageGrid.gridify_items(input, columns)

def test_gridify_items_oneline():
    input = [1, 2, 3, 4, 5, 6, 7]
    columns = 8
    expected = [
        [1, 2, 3, 4, 5, 6, 7]
    ]

    assert expected == sort_images_window.ImageGrid.gridify_items(input, columns)

def test_gridify_items_noitems():
    input = []
    columns = 5
    expected = [

    ]
    assert expected == sort_images_window.ImageGrid.gridify_items(input, columns)

@pytest.fixture
def options_frame() -> sort_images_window.ScanOptionsFrame:
    app = tk.Tk()
    frame = sort_images_window.ScanOptionsFrame(app)
    yield frame
    app.destroy()

def test_get_prefix_checked(options_frame : sort_images_window.ScanOptionsFrame):
    options_frame.has_prefix_chk.select()
    options_frame.prefix_input.delete(0, tk.END)
    options_frame.prefix_input.insert(0, 'prefix')
    assert 'prefix' == options_frame.get_prefix()

def test_get_prefix_unchecked(options_frame : sort_images_window.ScanOptionsFrame):
    options_frame.has_prefix_chk.deselect()
    options_frame.prefix_input.delete(0, tk.END)
    options_frame.prefix_input.insert(0, 'prefix')
    assert '' == options_frame.get_prefix()

def test_sorted_keys_in_order():
    image_grid = sort_images_window.ImageGrid(None)
    image_grid.images['a'] = 'TEST A'
    image_grid.images['b'] = 'TEST B'
    image_grid.images['c'] = 'TEST C'
    image_grid.images['d'] = 'TEST D'

    expected = [
        'TEST A',
        'TEST B',
        'TEST C',
        'TEST D',
        ]
    
    assert expected == image_grid.items_sorted



def test_sorted_keys_out_of_order():
    image_grid = sort_images_window.ImageGrid(None)
    image_grid.images['a'] = 'TEST A'
    image_grid.images['c'] = 'TEST C'
    image_grid.images['b'] = 'TEST B'
    image_grid.images['d'] = 'TEST D'

    expected = [
        'TEST A',
        'TEST B',
        'TEST C',
        'TEST D',
        ]
    
    assert expected == image_grid.items_sorted