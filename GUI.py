import customtkinter as Tk
import API

class App(Tk.CTk):
    def __init__(self):
        super().__init__()

        self.files_for_dxf_creation = [r"C:\Users\rodchenko.aa\Desktop\Delete\C исполнениями.m3d", r"C:\Users\rodchenko.aa\Desktop\Delete\ГКЮШ.111.m3d", r"C:\Users\rodchenko.aa\Desktop\Delete\Деталь.m3d"]

        button_1 = Tk.CTkButton(self, text='Создать dxf', command=self.button_create_dxf)
        button_1.pack()
        button_2 = Tk.CTkButton(self, text='Создать группу dxf', command=self.create_dxf_pack)
        button_2.pack()

    def button_create_dxf(self):
        API.CreateDxf()

    def create_dxf_pack(self):
        if not self.files_for_dxf_creation:
            pass
        else:
            for i in self.files_for_dxf_creation:
                API.CreateDxf(i)
