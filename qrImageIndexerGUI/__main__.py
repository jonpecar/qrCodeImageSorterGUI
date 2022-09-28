from qrImageIndexerGUI import launch_window
import tkinter as tk

def main():
    print("launched")
    app = tk.Tk(className="qrImageIndexerGUI")
    launch_window.LaunchWindow(app)
    app.title('QR Image Indexer GUI')
    app.geometry("300x75")
    app.resizable(width=False, height=False)
    app.mainloop()
    

if __name__ == '__main__':
    main()


