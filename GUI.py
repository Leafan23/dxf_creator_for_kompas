import customtkinter as Tk
import API
from pathlib import Path
import pywinstyles

class App(Tk.CTk):
    def __init__(self):
        super().__init__()
        self.title("dxf creator")
        self.attributes("-topmost", True)
        self.files_for_dxf_creation = []
        #pywinstyles.apply_style(self, "transparent")
        #pywinstyles.change_header_color(self, color="blue")

        self.drop_zone = DndZone(master=self, width=300, height=300, corner_radius=15)
        self.drop_zone.grid(row=0, column=0, columnspan=2)
        #self.drop_zone.bind('<Enter>', self.on_start_hover)
        #self.drop_zone.bind('<Leave>', self.on_end_hover)

        button_1 = Tk.CTkButton(self, text='Создать dxf', command=self.button_create_dxf)
        button_1.grid(row=1, column=0)
        self.button_2 = Tk.CTkButton(self,
                                     text='Создать группу dxf',
                                     command=self.create_dxf_pack,
                                     state="disabled",
                                     fg_color='orange',
                                     text_color='black')
        self.button_2.grid(row=1, column=1)



    def button_create_dxf(self):
        API.CreateDxf()

    def create_dxf_pack(self):
        if len(self.files_for_dxf_creation) > 0: # проверка на пустой список
            for i in self.files_for_dxf_creation:
                if Path(i).exists():
                    API.CreateDxf(i)
        self.files_for_dxf_creation = []
        self.button_2.configure(state="disabled")

    def on_start_hover(self):
        self.drop_zone.width = 330
        self.drop_zone.height = 330

    def on_end_hover(self):
        self.drop_zone.width = 300
        self.drop_zone.height = 300



class DndZone(Tk.CTkFrame):
    def __init__(self, master, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        pywinstyles.apply_dnd(self, self.drop_func)

        label_1 = Tk.CTkLabel(master=self, width=300, height=300,)
        label_1.configure(text='Перетащите сюда файлы')
        label_1.pack()

    def drop_func(self, pathfile):
        self.master.files_for_dxf_creation.extend(pathfile)
        self.master.files_for_dxf_creation = list(dict.fromkeys(self.master.files_for_dxf_creation))
        print(len(self.master.files_for_dxf_creation))
        self.master.button_2.configure(state="normal")