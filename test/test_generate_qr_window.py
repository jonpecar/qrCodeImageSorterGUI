import pytest
import tkinter as tk
import customtkinter as ctk
from qrImageIndexerGUI import generate_qr_window

# Testing the behaviour of the checkboxes. Probably not the best practice, but wanted to make sure that
# they are representing the checked state of the appropriate checkboxes

@pytest.fixture
def options_frame() -> generate_qr_window.OptionsFrame:
    app = ctk.CTk()
    frame = generate_qr_window.OptionsFrame(app)
    yield frame
    app.destroy()


def test_sliceable_checkbox_check(options_frame : generate_qr_window.OptionsFrame):
    options_frame.sort_sliceable_chk.select()
    assert options_frame.get_check_states()['sliceable']

def test_sliceable_checkbox_uncheck(options_frame : generate_qr_window.OptionsFrame):
    options_frame.sort_sliceable_chk.deselect()
    assert not options_frame.get_check_states()['sliceable']

def test_qr_headings_checkbox_check(options_frame : generate_qr_window.OptionsFrame):
    options_frame.qr_for_headings_chk.select()
    assert options_frame.get_check_states()['qr_headings']

def test_qr_headings_checkbox_uncheck(options_frame : generate_qr_window.OptionsFrame):
    options_frame.qr_for_headings_chk.deselect()
    assert not options_frame.get_check_states()['qr_headings']

def test_repeat_headings_checkbox_check(options_frame : generate_qr_window.OptionsFrame):
    options_frame.repeat_headings_chk.select()
    assert options_frame.get_check_states()['repeat_headings']

def test_repeat_headings_checkbox_uncheck(options_frame : generate_qr_window.OptionsFrame):
    options_frame.repeat_headings_chk.deselect()
    assert not options_frame.get_check_states()['repeat_headings']

def test_use_prefix_checkbox_check(options_frame : generate_qr_window.OptionsFrame):
    options_frame.use_prefix_chk.select()
    assert options_frame.get_check_states()['use_prefix']

def test_use_prefix_checkbox_uncheck(options_frame : generate_qr_window.OptionsFrame):
    options_frame.use_prefix_chk.deselect()
    assert not options_frame.get_check_states()['use_prefix']

def test_get_prefix_option(options_frame : generate_qr_window.OptionsFrame):
    options_frame.prefix_input.delete(0, tk.END)
    options_frame.prefix_input.insert(0, 'prefix')
    assert options_frame.get_prefix() == 'prefix'

@pytest.fixture
def mocked_qr_generate_functions(mocker):

    get_check_states = mocker.patch('qrImageIndexerGUI.generate_qr_window.OptionsFrame.get_check_states')

    get_prefix = mocker.patch('qrImageIndexerGUI.generate_qr_window.OptionsFrame.get_prefix')

    load_lines = mocker.patch('qrImageIndexerGUI.generate_qr_window.load_lines', return_value=[
                                ['Line 1', ''],
                                ['', 'Line 1 Indent']
                            ])

    generate_qr_pdf = mocker.patch('qrImageIndexerGUI.generate_qr_window.generate_qr_pdf', 
                                return_value='pdf_document')
    
    return (get_check_states, get_prefix, load_lines, generate_qr_pdf)


@pytest.fixture
def generate_qr(mocker) -> generate_qr_window.GenerateQRWindow:
    mocker.patch('qrImageIndexerGUI.generate_qr_window.GenerateQRWindow.update_pdf_sample')
    app = tk.Tk()
    frame = generate_qr_window.GenerateQRWindow(app)
    frame.enter_txt.delete("1.0", tk.END)
    frame.enter_txt.insert("1.0", "Input Text")
    yield frame
    app.destroy()

def test_generate_pdf_all_opts(mocked_qr_generate_functions, generate_qr : generate_qr_window.GenerateQRWindow):
    (get_check_states, get_prefix, load_lines, generate_qr_pdf) = mocked_qr_generate_functions
    get_check_states.return_value = {
            'sliceable' : True,
            'qr_headings' : True,
            'repeat_headings' : True,
            'use_prefix' : True,
    }

    get_prefix.return_value = r'{prefix}'

    result = generate_qr.generate_pdf()
    get_check_states.assert_called_once_with()
    load_lines.assert_called_once_with(["Input Text", ""])
    generate_qr_pdf.assert_called_once_with(load_lines.return_value, True,
                                            True, True, get_prefix.return_value)
    assert result == generate_qr_pdf.return_value

def test_generate_pdf_no_slice(mocked_qr_generate_functions, generate_qr : generate_qr_window.GenerateQRWindow):
    (get_check_states, get_prefix, load_lines, generate_qr_pdf) = mocked_qr_generate_functions
    get_check_states.return_value = {
            'sliceable' : False,
            'qr_headings' : True,
            'repeat_headings' : True,
            'use_prefix' : True,
    }

    get_prefix.return_value = r'{prefix}'

    result = generate_qr.generate_pdf()
    get_check_states.assert_called_once_with()
    load_lines.assert_called_once_with(["Input Text", ""])
    generate_qr_pdf.assert_called_once_with(load_lines.return_value, True,
                                            True, False, get_prefix.return_value)
    assert result == generate_qr_pdf.return_value

def test_generate_pdf_no_qr_heading(mocked_qr_generate_functions, generate_qr : generate_qr_window.GenerateQRWindow):
    (get_check_states, get_prefix, load_lines, generate_qr_pdf) = mocked_qr_generate_functions
    get_check_states.return_value = {
            'sliceable' : True,
            'qr_headings' : False,
            'repeat_headings' : True,
            'use_prefix' : True,
    }

    get_prefix.return_value = r'{prefix}'

    result = generate_qr.generate_pdf()
    get_check_states.assert_called_once_with()
    load_lines.assert_called_once_with(["Input Text", ""])
    generate_qr_pdf.assert_called_once_with(load_lines.return_value, False,
                                            True, True, get_prefix.return_value)
    assert result == generate_qr_pdf.return_value

def test_generate_pdf_no_repeat_heading(mocked_qr_generate_functions, generate_qr : generate_qr_window.GenerateQRWindow):
    (get_check_states, get_prefix, load_lines, generate_qr_pdf) = mocked_qr_generate_functions
    get_check_states.return_value = {
            'sliceable' : True,
            'qr_headings' : True,
            'repeat_headings' : False,
            'use_prefix' : True,
    }

    get_prefix.return_value = r'{prefix}'

    result = generate_qr.generate_pdf()
    get_check_states.assert_called_once_with()
    load_lines.assert_called_once_with(["Input Text", ""])
    generate_qr_pdf.assert_called_once_with(load_lines.return_value, True,
                                            False, True, get_prefix.return_value)
    assert result == generate_qr_pdf.return_value

def test_generate_pdf_no_prefix(mocked_qr_generate_functions, generate_qr : generate_qr_window.GenerateQRWindow):
    (get_check_states, get_prefix, load_lines, generate_qr_pdf) = mocked_qr_generate_functions
    get_check_states.return_value = {
            'sliceable' : True,
            'qr_headings' : True,
            'repeat_headings' : True,
            'use_prefix' : False,
    }

    get_prefix.return_value = r'{prefix}'

    result = generate_qr.generate_pdf()
    get_check_states.assert_called_once_with()
    load_lines.assert_called_once_with(["Input Text", ""])
    generate_qr_pdf.assert_called_once_with(load_lines.return_value, True,
                                            True, True, '')
    assert result == generate_qr_pdf.return_value