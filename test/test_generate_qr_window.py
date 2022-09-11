import pytest
import tkinter as tk
from qrImageIndexerGUI import generate_qr_window

# Testing the behaviour of the checkboxes. Probably not the best practice, but wanted to make sure that
# they are representing the checked state of the appropriate checkboxes

@pytest.fixture
def options_frame() -> generate_qr_window.OptionsFrame:
    app = tk.Tk()
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