from time import sleep

import pythoncom
from win32com.client import Dispatch, gencache, VARIANT
import datetime as dt
import configparser
import os.path
import sys


class KompasAPI:
    def __init__(self, kompas_document=None):
        self.ShowOnSheet = 0
        #  Подключим описание интерфейсов API7
        self.api7 = gencache.EnsureModule("{69AC2981-37C0-4379-84FD-5DD2F3C0A520}", 0, 1, 0)
        self.application = Dispatch("KOMPAS.Application.7")

        system_settings = self.application.SystemSettings
        self.lib_path = system_settings.SystemPath(1) + r"\ImpExp\dwgdxfExp.rtw"

        if not None:
            self.kompas_document = self.application.ActiveDocument
        else:
            self.kompas_document = kompas_document
        self.documents = self.application.Documents
        if self.kompas_document.DocumentType == 4: # ksDocumentPart 4 Деталь
            self.kompas_document_3d_1 = self.api7.IKompasDocument3D1(self.kompas_document)
            self.kompas_document_3d = self.api7.IKompasDocument3D(self.kompas_document)
            self.view_projection_manager = self.kompas_document_3d_1.ViewProjectionManager
            self.selection_manager = self.kompas_document_3d.SelectionManager
            print(self.selection_manager.SelectedObjects)
        elif self.kompas_document.DocumentType == 1: # ksDocumentDrawing 1 Чертеж
            self.kompas_document_2d = self.api7.IKompasDocument2D(self.kompas_document)
            self.view_layers_manager = self.kompas_document_2d.ViewsAndLayersManager
            self.views = self.view_layers_manager.Views
            self.view = None
            self.drawing_object = None
            self.association_view = None

            self.layout_sheets = self.kompas_document.LayoutSheets
            self.layout_sheet = self.layout_sheets.ItemByNumber(1)

    def add_drawing_object(self):
        if self.view is not None:
            self.drawing_object = self.api7.IDrawingObject(self.view)

    def add_view(self, view_name):
        """добавить вид с именем"""
        view_projection_7 = self.view_projection_manager.Add()
        view_projection_7.Name = view_name
        view_projection_7.Update()


if __name__ == '__main__':
    # Сделать нормально к выделенной поверхности
    # Создать ориентацию вида по этой поверхности
    # Создать пустой чертеж, без рамки
    # Вставить вид с модели с сохраненным видом
    # Сохранить как dxf
    # Закрыть чертеж

    api = KompasAPI()
    print(api.view_projection_manager.OrientationNormalTo(api.selection_manager.SelectedObjects))
    sleep(1)
    api.view_projection_manager.OrientationNormalTo(api.selection_manager.SelectedObjects)
    api.add_view('kkk1')

    # Создать пустой чертеж, без рамки
    api_drawing = KompasAPI(api.documents.Add(1,True))

    api_drawing.views.AddStandartViews(api.kompas_document.PathName,'kkk1', 0, 0,0,1,0,0)
    api_drawing.layout_sheet.Delete()

    api_drawing.convert = api_drawing.application.Converter(api_drawing.lib_path)
    print(api_drawing.convert) # почему-то None
    api_drawing.convert.Convert(api_drawing.kompas_document.PathName,
                                api.kompas_document.PathName.rpartition('.')[0]+".dxf", 1, False)
    api_drawing.kompas_document.Close(0)

    print(os.path.splitext(api.kompas_document.PathName))
    print(api.kompas_document.PathName.rpartition('.')[0])




