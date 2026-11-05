import customtkinter as Tk
import API
from pathlib import Path
from tkinterdnd2 import TkinterDnD, DND_ALL
import os.path
import sys
import os
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

        button_1 = Tk.CTkButton(self, text='Создать одиночный', command=self.create_current)
        button_1.grid(row=1, column=0, sticky='ew', padx=3, pady=3)
        self.button_2 = Tk.CTkButton(self,
                                     text='Создать множество',
                                     command=self.create,
                                     fg_color='orange',
                                     hover_color='#d97706',
                                     text_color='black',
                                     state="disabled")
        self.button_2.grid(row=1, column=1, sticky='ew', padx=3, pady=3)

        self.ready_label = Tk.CTkLabel(self, text='')
        self.ready_label.grid(row=3, column=0, columnspan=2, sticky='ew')
        self.ready_label.grid_remove()  # скрыт до первого запуска

        self.icon_image = Tk.CTkImage(
            light_image=Image.open(get_asset_path("icon-trash-can.png")),
            dark_image=Image.open(get_asset_path("icon-trash-can.png")),
            size=(20, 20)
        )

        self.drawing_zone = DrawingZone(master=self)
        self.drawing_zone.grid(row=2, column=0, columnspan=2, sticky='ew')

        self.TkdndVersion = TkinterDnD._require(self)
        self.drop_target_register(DND_ALL)
        self.dnd_bind("<<DropEnter>>", self.drop_enter)
        self.dnd_bind("<<DropLeave>>", self.drop_leave)
        self.dnd_bind("<<Drop>>", self.get_path)

    def create(self):
        """Пакетная обработка чертежей .cdw и спецификаций .spw → PDF.
        Пакетная обработка деталей .m3d → DXF."""

        self.ready_label.grid(row=3, column=0, columnspan=2, sticky='ew')

        for i in self.label_list:
            i.destroy()
        self.button_2.configure(state="disabled")
        self.label_list = []

        if len(self.path_list) > 0:
            for i in self.path_list:
                self.ready_label.configure(text='Cоздается файл... '+os.path.basename(i), bg_color='orange', text_color='Black')
                self.update()
                if Path(i).exists() and os.path.splitext(i)[1].lower() in (".cdw", ".spw"):
                    API.CreatePdf(i)
                elif Path(i).exists() and os.path.splitext(i)[1].lower() == ".m3d":
                    API.CreateDxf(i)

        self.path_list = []
        self.ready_label.configure(text='Готово', bg_color='green', text_color='White')

    def create_current(self):
        app = API.Dispatch("KOMPAS.Application.7")
        doc = app.ActiveDocument
        if doc is None:
            app.MessageBoxEx("В КОМПАС нет открытого документа", "Нет документа", 0)
            return

        self.ready_label.configure(
            text='Создается файл... ' + os.path.basename(doc.PathName),
            fg_color='orange', text_color='black')
        self.update()

        try:
            API.CreateCurrent()
            self.ready_label.configure(text='Готово', bg_color='green', text_color='white')
        except Exception as e:
            self.ready_label.configure(text=f'Ошибка: {e}', bg_color='red', text_color='white')
        self.update()

    def drop_enter(self, event):
        self.drop_zone.label.configure(border_width=2)

    def drop_leave(self, event):
        self.drop_zone.label.configure(border_width=0)

    def get_path(self, event):
        if self.ready_label is not None:
            self.ready_label.grid_remove()
        self.drop_zone.label.configure(border_width=0)
        dropped_file = self.my_master.splitlist(event.data)
        for i in dropped_file:
            extention = os.path.splitext(i)[1].lower()
            if i not in self.path_list and extention in (".m3d", ".cdw", ".spw"):
                self.label_list.append(SelectString(master=self.drawing_zone, text=i))
                self.label_list[-1].pack(fill='x', pady=1)
                self.path_list.append(i)
        if self.path_list:
            self.button_2.configure(state="normal")
        return event.action



class DndZone(Tk.CTkFrame):
    def __init__(self, master, *args, **kwargs):
        super().__init__(master, *args, **kwargs)

        self.label = Tk.CTkLabel(master=self, width=300, height=300, bg_color="transparent", corner_radius=10, border_width=0, border_color="orange")
        self.label.configure(
            text='Перетащите сюда файлы \n деталей (.m3d) или чертежей (.cdw) \n и нажмите "Создать множество"')
        self.label.pack()



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

def get_asset_path(filename):
    """Путь к файлу в папке assets — работает и из исходников, и из exe."""
    if getattr(sys, 'frozen', False):
        # В PyInstaller 6+ sys._MEIPASS указывает на папку _internal
        base_path = sys._MEIPASS
    else:
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, "assets", filename)