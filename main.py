#TODO v0.2 Сделать пакетное открываение деталей
#TODO v0.2 Сделать автоматическое определение самой большой поверхности
#TODO v0.2 Сделать определение толщины для листовых и не для листовых деталей
#TODO v0.2 Добавить работу с исполнениями (сейчас сохраняется только первое исполнение)

from time import sleep
from win32com.client import Dispatch, gencache, VARIANT
import sys


class KompasAPI:
    def __init__(self, kompas_document=None):
        #  Подключим описание интерфейсов API7
        self.api7 = gencache.EnsureModule("{69AC2981-37C0-4379-84FD-5DD2F3C0A520}", 0, 1, 0)
        self.application = Dispatch("KOMPAS.Application.7")

        system_settings = self.application.SystemSettings
        self.lib_path = system_settings.SystemPath(1) + r"\ImpExp\dwgdxfExp.rtw"
        self.is_sheet_metal = None # Признак детали как листового тела

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
            self.part_7 = self.kompas_document_3d.TopPart
            self.sheet_metal_container = self.api7.ISheetMetalContainer(self.part_7)
            self.sheet_metal_bodies = self.sheet_metal_container.SheetMetalBodies
            self.sheet_metal_body = self.sheet_metal_bodies.SheetMetalBody(0)
            self.converts_to_sheet_metals = self.sheet_metal_container.ConvertsToSheetMetals
            self.convert_to_sheet_metal = self.converts_to_sheet_metals.ConvertToSheetMetal(0)

            if self.sheet_metal_body is None and self.convert_to_sheet_metal is None:
                self.is_sheet_metal = False
            else:
                self.is_sheet_metal = True
            # Создание развертки и ее обновление по выделенной поверхности
            if self.is_sheet_metal:
                self.sheet_metal_bend_unfold_parameters = self.sheet_metal_container.SheetMetalBendUnfoldParameters
                if self.sheet_metal_bend_unfold_parameters.IsCreated:
                    self.sheet_metal_bend_unfold_parameters.FixedFaces = None
                    self.sheet_metal_bend_unfold_parameters.UpdateParam()
                    self.sheet_metal_bend_unfold_parameters.FixedFaces = self.selection_manager.SelectedObjects
                    self.sheet_metal_bend_unfold_parameters.UpdateParam()
                else:
                    self.sheet_metal_bend_unfold_parameters.FixedFaces = self.selection_manager.SelectedObjects
                    self.sheet_metal_bend_unfold_parameters.UpdateParam()

        elif self.kompas_document.DocumentType == 1: # ksDocumentDrawing 1 Чертеж
            self.kompas_document_2d = self.api7.IKompasDocument2D(self.kompas_document)
            self.kompas_document_2d_1 = self.api7.IKompasDocument2D1(self.kompas_document)
            self.view_layers_manager = self.kompas_document_2d.ViewsAndLayersManager
            self.views = self.view_layers_manager.Views
            self.view = None
            self.view_designation = None
            self.drawing_object = None
            self.association_view = None

            self.layout_sheets = self.kompas_document.LayoutSheets
            self.layout_sheet = self.layout_sheets.ItemByNumber(1)
        else:
            #TODO Сделать всплывающее окно
            print('Ошибка, макрос работает только с деталью')
            sys.exit()

    def add_drawing_object(self):
        if self.view is not None:
            self.drawing_object = self.api7.IDrawingObject(self.view)

    def print_view_propertys(self):
        print('view.Angle = ', self.view.Angle)
        print('view.Background = ', self.view.Background)
        print('view.Color = ', self.view.Color)
        print('view.Comment = ', self.view.Comment)
        print('view.Current = ', self.view.Current)
        print('view.Name = ', self.view.Name)
        print('view.Number = ', self.view.Number)
        print('view.ObjectCount = ', self.view.ObjectCount)
        print('view.Scale = ', self.view.Scale)

    def add_view(self, view_name):
        """Добавить вид с именем. Обновляет вид, если уже есть с таким именем"""
        # Удалить вид если такое имя уже существует
        if self.view_projection_manager.ViewProjection(view_name) is not None:
            view_projection_7 = self.view_projection_manager.ViewProjection(view_name)
            view_projection_7.Delete()
        view_projection_7 = self.view_projection_manager.Add()
        view_projection_7.Name = view_name
        view_projection_7.Update()


if __name__ == '__main__':
    api = KompasAPI()

    # Сделать нормально к выделенной поверхности
    api.view_projection_manager.OrientationNormalTo(api.selection_manager.SelectedObjects)
    sleep(1) # надо для того, что бы камера успела навестись в положение "Нормально к..", иначе вид получается промежуточный

    # Создать ориентацию вида по этой поверхности
    api.add_view('Для развертки')

    # Создать пустой чертеж, без рамки
    api_drawing = KompasAPI(api.documents.Add(1,True))
    api_drawing.application.HideMessage = 1

    # Вставить вид с модели с сохраненным видом, удалить рамку
    api_drawing.views.AddStandartViews(api.kompas_document.PathName,'Для развертки', 0, 0,0,1,0,0)
    if api.is_sheet_metal is True:
        api_drawing.view = api_drawing.views.View(1)
        api_drawing.association_view = api_drawing.api7.IAssociationView(api_drawing.view)
        api_drawing.association_view.Unfold = True
        api_drawing.association_view.Update() # возможно не нужно, заменяется следующей командой на перестройку
    api_drawing.kompas_document_2d_1.RebuildDocument() # перестроение всего документа, скорее всего излишнее действие
    api_drawing.layout_sheet.Delete()

    # Сохранить как dxf
    api_drawing.convert = api_drawing.application.Converter(api_drawing.lib_path)
    api_drawing.convert.Convert(api_drawing.kompas_document.PathName,
                                api.kompas_document.PathName.rpartition('.')[0]+".dxf", 1, False)
    api_drawing.application.HideMessage = 0

    # Закрыть чертеж
    api_drawing.kompas_document.Close(0)




