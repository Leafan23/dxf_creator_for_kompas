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

        # В MainFrame.__init__, после создания button_1 и button_2:
        self.button_pdf = Tk.CTkButton(self, text='Создать PDF', command=self.create_pdf_pack)
        self.button_pdf.grid(row=1, column=2, sticky='ew', padx=3, pady=3)

        button_1 = Tk.CTkButton(self, text='Создать dxf', command=API.CreateDxf)
        button_1.grid(row=1, column=0, sticky='ew', padx=3, pady=3)
        self.button_2 = Tk.CTkButton(self,
                                     text='Создать группу dxf',
                                     command=self.create_dxf_pack,
                                     fg_color='orange',
                                     hover_color='#d97706',
                                     text_color='black',
                                     state="disabled")
        self.button_2.grid(row=1, column=1, sticky='ew', padx=3, pady=3)

        self.icon_image = Tk.CTkImage(
            light_image=Image.open("assets/icon-trash-can.png"),
            dark_image=Image.open("assets/icon-trash-can.png"),
            size=(20, 20)
        )

        self.drawing_zone = DrawingZone(master=self)
        self.drawing_zone.grid(row=2, column=0, columnspan=2, sticky='ew')

        self.ready_label = None

        self.TkdndVersion = TkinterDnD._require(self)
        self.drop_target_register(DND_ALL)
        self.dnd_bind("<<DropEnter>>", self.drop_enter)
        self.dnd_bind("<<DropLeave>>", self.drop_leave)
        self.dnd_bind("<<Drop>>", self.get_path)

    def create_pdf_pack(self):
        """Пакетная обработка чертежей .cdw и спецификаций .spw → PDF."""
        for i in self.label_list:
            i.destroy()
        self.button_2.configure(state="disabled")
        self.label_list = []
        self.update()

        if len(self.path_list) > 0:
            for i in self.path_list:
                if Path(i).exists() and os.path.splitext(i)[1].lower() in (".cdw", ".spw"):
                    API.CreatePdf(i)

        self.path_list = []
        self.ready_label = Tk.CTkLabel(self, text='Готово', bg_color='green')
        self.ready_label.grid(row=3, column=0, columnspan=2, sticky='ew')

    def create_dxf_pack(self):
        """Пакетная обработка деталей .m3d → DXF."""
        for i in self.label_list:
            i.destroy()
        self.button_2.configure(state="disabled")
        self.label_list = []
        self.update()

        if len(self.path_list) > 0:
            for i in self.path_list:
                if Path(i).exists() and os.path.splitext(i)[1].lower() == ".m3d":
                    API.CreateDxf(i)

        self.path_list = []
        self.ready_label = Tk.CTkLabel(self, text='Готово', bg_color='green')
        self.ready_label.grid(row=3, column=0, columnspan=2, sticky='ew')

    def drop_enter(self, event):
        self.drop_zone.label.configure(border_width=2)

    def drop_leave(self, event):
        self.drop_zone.label.configure(border_width=0)

    def get_path(self, event):
        if self.ready_label is not None:
            self.ready_label.destroy()
            self.ready_label = None
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
            text='Перетащите сюда файлы \n деталей (.m3d) или чертежей (.cdw) \n и нажмите "Создать группу"')
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

