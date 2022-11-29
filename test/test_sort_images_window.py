from qrImageIndexerGUI import sort_images_window
import pytest
import tkinter as tk
import customtkinter as ctk
from unittest.mock import MagicMock, call, Mock

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
    app = ctk.CTk()
    image_grid = sort_images_window.ImageGrid(app)
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
    app = ctk.CTk()
    image_grid = sort_images_window.ImageGrid(app)
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

def is_image_side_effect(image_path):
    if 'non-image' in image_path:
        return (False, image_path)
    else:
        return (True, image_path)

def get_qr_mt_side_effect(image_path, string_header, binarization):
    if not binarization:
        assert False
    if 'qr' in image_path:
        qr = image_path[image_path.find('qr')+2:]
        if string_header in qr:
            return image_path, qr[len(string_header):]
    return image_path, None

@pytest.fixture
def mocked_image_sort_functions(mocker):
    is_image = mocker.patch('qrImageIndexerGUI.sort_images_window.photo_sorter.check_if_image',
                            side_effect=is_image_side_effect)

    # get_qr_mt = mocker.patch('qrImageIndexerGUI.sort_images_window.photo_sorter.get_qr_mt',
    #                         side_effect=get_qr_mt_side_effect)
    
    get_qr_mt = None

    #Due to the use of multiprocessing, this function could not easily be mocked as MagicMock could not be pickled
    #so for now just going to directly replace the function.
    sort_images_window.photo_sorter.get_qr_mt = get_qr_mt_side_effect

    return (is_image, get_qr_mt)



def test_image_scan_no_qr(mocked_image_sort_functions):
    is_image : Mock
    get_qr_mt : Mock
    (is_image, get_qr_mt) = mocked_image_sort_functions
    files = [
        'image1',
        'image2',
        'image3'
    ]
    thread = sort_images_window.ImageScan(files, '')
    thread.start()
    thread.join()

    assert 0 == len(thread.results)
    assert 3 == len(thread.files)
    assert 3 == len(thread.image_files)
    assert 0 == len(thread.non_image_files)

    is_image.assert_has_calls([call(x) for x in files])
    # get_qr_mt.assert_has_calls([call(x, '', True) for x in files])


def test_image_scan_1_qr(mocked_image_sort_functions):
    is_image : Mock
    get_qr_mt : Mock
    (is_image, get_qr_mt) = mocked_image_sort_functions
    files = [
        'image1',
        'image2qr123',
        'image3'
    ]
    thread = sort_images_window.ImageScan(files, '')
    thread.start()
    thread.join()

    assert 1 == len(thread.results)
    assert '123' == thread.results['image2qr123']
    assert 3 == len(thread.files)
    assert 3 == len(thread.image_files)
    assert 0 == len(thread.non_image_files)

    is_image.assert_has_calls([call(x) for x in files])

def test_image_scan_1_non_image(mocked_image_sort_functions):
    is_image : Mock
    get_qr_mt : Mock
    (is_image, get_qr_mt) = mocked_image_sort_functions
    files = [
        'image1',
        'image2qr123',
        'image3non-image'
    ]
    thread = sort_images_window.ImageScan(files, '')
    thread.start()
    thread.join()

    assert 1 == len(thread.results)
    assert '123' == thread.results['image2qr123']
    assert 3 == len(thread.files)
    assert 2 == len(thread.image_files)
    assert 1 == len(thread.non_image_files)
    assert thread.non_image_files == ['image3non-image']

    is_image.assert_has_calls([call(x) for x in files])

def test_sort_dict_function():
    input = {
        'a':123,
        'b':456,
        'c':789
    }

    expect_keys = ['a', 'b', 'c']
    
    assert expect_keys == list(sort_images_window.ScanImagesWindow.sort_results_dict(input).keys())

def test_sort_dict_function_unergdered():
    input = {
        'a':123,
        'c':789,
        'b':456
    }

    expect_keys = ['a', 'b', 'c']
    
    assert expect_keys == list(sort_images_window.ScanImagesWindow.sort_results_dict(input).keys())