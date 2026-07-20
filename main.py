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
        self.application = self.api7.IApplication(
            Dispatch("Kompas.Application.7")._oleobj_.QueryInterface(self.api7.IApplication.CLSID,
                                                                     pythoncom.IID_IDispatch))
        if not None:
            self.kompas_document = self.application.ActiveDocument
        else:
            self.kompas_document = kompas_document
        self.documents = self.application.Documents
        if self.kompas_document.DocumentType == 4:
            self.kompas_document_3d_1 = self.api7.IKompasDocument3D1(self.kompas_document)
            self.kompas_document_3d = self.api7.IKompasDocument3D(self.kompas_document)
            self.view_projection_manager = self.kompas_document_3d_1.ViewProjectionManager
            self.selection_manager = self.kompas_document_3d.SelectionManager
            print(self.selection_manager.SelectedObjects)


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
    print(api.view_projection_manager.BaseUserOrientation)
    print(api.view_projection_manager.Count)
    print(api.view_projection_manager.Matrix3D)
    print(api.view_projection_manager.Scale)
    print(api.view_projection_manager.ViewProjectionScheme)

    for i in range(api.view_projection_manager.Count):
        ViewProjectionManager = api.view_projection_manager.ViewProjection(i)
        print(ViewProjectionManager.Name)
        print(ViewProjectionManager.Current)
        print(ViewProjectionManager.Scale)
        print(ViewProjectionManager.UserProjectionIndex)
        print(ViewProjectionManager.ViewProjectonType)
        print('-------------------------------')
        ViewProjectionManager.Update()

    # Создать пустой чертеж, без рамки
    api_drawing = KompasAPI(api.documents.Add(1,True))
    print(api_drawing.kompas_document.DocumentType)

