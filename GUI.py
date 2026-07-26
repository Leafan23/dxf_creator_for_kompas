import customtkinter as Tk
import API
from pathlib import Path
from tkinterdnd2 import TkinterDnD, DND_ALL



class App(Tk.CTk):
    def __init__(self):
        super().__init__()
        self.title("dxf creator")
        self.attributes("-topmost", True)
        self.main_fraim = MainFrame(master=self)
        self.main_fraim.pack()



class MainFrame(Tk.CTkFrame):
    def __init__(self, master, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.files_for_dxf_creation = []
        self.label_list = []
        self.path_list = [] # то же самое что и self.files_for_dxf_creation - список путей на преобразование

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

        dropped_file = event.data.replace("{", "").replace("}", "")
        new_string = dropped_file.split(' ')
        for i in new_string:
            if i not in self.path_list:
                self.label_list.append(SelectString(master=self.drawing_zone, text=i))
                self.label_list[-1].pack()
                self.path_list.append(i)
        print(self.path_list != [])
        if self.path_list:
            self.button_2.configure(state="enabled")



class DndZone(Tk.CTkFrame):
    def __init__(self, master, *args, **kwargs):
        super().__init__(master, *args, **kwargs)

        label_1 = Tk.CTkLabel(master=self, width=500, height=300)
        label_1.configure(
            text='Перетащите сюда файлы \n деталей компас-3d (.m3d) \n и нажмите "Создать группу dxf"')
        label_1.pack()

    def drop_func(self, pathfile):
        self.master.files_for_dxf_creation.extend(pathfile)
        self.master.files_for_dxf_creation = list(dict.fromkeys(self.master.files_for_dxf_creation))
        print(len(self.master.files_for_dxf_creation))
        self.master.button_2.configure(state="normal")
        self.master.drawing_zone.create_string()



class DrawingZone(Tk.CTkScrollableFrame):
    def __init__(self, master, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.my_master = master



class SelectString(Tk.CTkFrame):
    def __init__(self,master, text='test_string', *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.text = text
        self.my_master = master

        label = Tk.CTkLabel(self, text=text)
        label.pack(side='left')
        button = Tk.CTkButton(self, command=self.delete_string)
        button.pack(side='left')

    def delete_string(self):
        self.destroy()
        self.my_master.my_master.path_list.remove(self.text)
        print(self.my_master.my_master.path_list)
        if not self.my_master.my_master.path_list:
            self.my_master.my_master.button_2.configure(state="disabled")

        #self.my_master.my_master.label_list = []
