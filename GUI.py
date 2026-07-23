import customtkinter as Tk
import API
from pathlib import Path
import pywinstyles

class App(Tk.CTk):
    def __init__(self):
        super().__init__()
        self.files_for_dxf_creation = []

        self.drop_zone = DndZone(master=self, width=300, height=300, corner_radius=15)
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


class DndZone(Tk.CTkFrame):
    def __init__(self, master, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        pywinstyles.apply_dnd(self, self.drop_func)

        label_1 = Tk.CTkLabel(master=self, text='Перетащите сюда файлы', width=300, height=300,)
        label_1.pack()

    def drop_func(self, pathfile):
        self.master.files_for_dxf_creation.extend(pathfile)
        self.master.files_for_dxf_creation = list(dict.fromkeys(self.master.files_for_dxf_creation))
        print(len(self.master.files_for_dxf_creation))