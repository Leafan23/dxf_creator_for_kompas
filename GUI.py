import customtkinter as Tk
import API
from pathlib import Path
import pywinstyles

class App(Tk.CTk):
    def __init__(self):
        super().__init__()
        pywinstyles.apply_style(self, 'acrylic')
        self.files_for_dxf_creation = []

        self.drop_zone = Tk.CTkFrame(master=self, width=300, height=300)
        pywinstyles.apply_dnd(self.drop_zone, self.drop_func)
        self.drop_zone.pack()
        button_1 = Tk.CTkButton(self, text='Создать dxf', command=self.button_create_dxf)
        button_1.pack()
        button_2 = Tk.CTkButton(self, text='Создать группу dxf', command=self.create_dxf_pack)
        button_2.pack()



    def button_create_dxf(self):
        API.CreateDxf()

    def create_dxf_pack(self):
        if len(self.files_for_dxf_creation) > 0: # проверка на пустой список
            for i in self.files_for_dxf_creation:
                if Path(i).exists():
                    API.CreateDxf(i)

    def drop_func(self, pathfile):
        self.files_for_dxf_creation.extend(pathfile)
        self.files_for_dxf_creation = list(dict.fromkeys(self.files_for_dxf_creation))
        print(len(self.files_for_dxf_creation))

