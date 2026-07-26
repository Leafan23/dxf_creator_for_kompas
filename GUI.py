import customtkinter as Tk
import API
from pathlib import Path
from tkinterdnd2 import TkinterDnD, DND_ALL
import os.path
from PIL import Image



class App(Tk.CTk):
    def __init__(self):
        super().__init__()
        self.title("dxf creator")
        self.attributes("-topmost", True)
        self.main_frame = MainFrame(master=self)
        self.main_frame.pack()



class MainFrame(Tk.CTkFrame):
    def __init__(self, master, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.my_master = master
        self.label_list = []
        self.path_list = [] #  список путей на преобразование

        self.drop_zone = DndZone(master=self, width=300, height=300, corner_radius=15)
        self.drop_zone.grid(row=0, column=0, columnspan=2)

        button_1 = Tk.CTkButton(self, text='Создать dxf', command=API.CreateDxf)
        button_1.grid(row=1, column=0, sticky='ew', padx=3, pady=3)
        self.button_2 = Tk.CTkButton(self,
                                     text='Создать группу dxf',
                                     command=self.create_dxf_pack,
                                     state="disabled",
                                     fg_color='orange',
                                     text_color='black')
        self.button_2.grid(row=1, column=1, sticky='ew', padx=3, pady=3)

        self.icon_image = Tk.CTkImage(
            light_image=Image.open("assets/icon-trash-can.png"),
            dark_image=Image.open("assets/icon-trash-can.png"),
            size=(20, 20)
        )

        self.drawing_zone = DrawingZone(master=self)
        self.drawing_zone.grid(row=2, column=0, columnspan=2, sticky='ew')

        self.TkdndVersion = TkinterDnD._require(self)
        self.drop_target_register(DND_ALL)
        self.dnd_bind("<<Drop>>", self.get_path)

    def create_dxf_pack(self):
        if len(self.path_list) > 0:  # проверка на пустой список
            for i in self.path_list:
                if Path(i).exists():
                    API.CreateDxf(i)
        self.path_list = []
        self.button_2.configure(state="disabled")

    def get_path(self, event):
        dropped_file = self.my_master.splitlist(event.data)
        for i in dropped_file:
            extention = os.path.splitext(i)[1]
            if i not in self.path_list and extention == ".m3d": # добавляются только m3d и только те файлы, которых еще нет в списке
                self.label_list.append(SelectString(master=self.drawing_zone, text=i))
                self.label_list[-1].pack(fill='x')
                self.path_list.append(i)
        if self.path_list:
            self.button_2.configure(state="enabled")



class DndZone(Tk.CTkFrame):
    def __init__(self, master, *args, **kwargs):
        super().__init__(master, *args, **kwargs)

        label_1 = Tk.CTkLabel(master=self, width=300, height=300)
        label_1.configure(
            text='Перетащите сюда файлы \n деталей компас-3d (.m3d) \n и нажмите "Создать группу dxf"')
        label_1.pack()



class DrawingZone(Tk.CTkScrollableFrame):
    def __init__(self, master, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.my_master = master



class SelectString(Tk.CTkFrame):
    def __init__(self,master, text='test_string', *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.text = text
        self.my_master = master

        button = Tk.CTkButton(self, command=self.delete_string, image=self.my_master.my_master.icon_image, text="",
                              width=30, height=30, fg_color='#ef5350')
        button.pack(side="right")
        label = Tk.CTkLabel(self, text=os.path.basename(text))
        label.pack(side="right", padx=30)


    def delete_string(self):
        self.destroy()
        self.my_master.my_master.path_list.remove(self.text)
        if not self.my_master.my_master.path_list:
            self.my_master.my_master.button_2.configure(state="disabled")

