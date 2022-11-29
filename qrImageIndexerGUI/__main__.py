from qrImageIndexerGUI import launch_window
import customtkinter as ctk

def main():
    print("launched")
    ctk.set_appearance_mode("System")
    ctk.set_default_color_theme("blue")
    app = ctk.CTk(className="qrImageIndexerGUI")
    launch_window.LaunchWindow(app)
    app.title('QR Image Indexer GUI')
    app.geometry("300x75")
    app.resizable(width=False, height=False)
    app.mainloop()
    

if __name__ == '__main__':
    main()


