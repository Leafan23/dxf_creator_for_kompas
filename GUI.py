import customtkinter as Tk
import API

class App(Tk.CTk):
    def __init__(self):
        super().__init__()
        button_1 = Tk.CTkButton(self, text='Создать dxf', command=self.button_create_dxf)
        button_1.pack()

    def button_create_dxf(self):
        API.CreateDxf()
