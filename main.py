#TODO v0.3 Сделать пакетное открываение деталей
#TODO v0.3 Сделать GUI интерфейс

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
        self.sheet_thickness = None # Толщина материала

        if kompas_document is None:
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
            if self.selection_manager.SelectedObjects is None:
                self.select_max_face()
            self.embodiments_manager = self.api7.IEmbodimentsManager(self.part_7)
            self.current_embodiment_marking = self.embodiments_manager.GetCurrentEmbodimentMarking(-1, False)
            self.embodiment = self.embodiments_manager.SetCurrentEmbodiment
            self.sheet_metal_container = self.api7.ISheetMetalContainer(self.part_7)
            self.sheet_metal_bodies = self.sheet_metal_container.SheetMetalBodies
            self.sheet_metal_body = self.sheet_metal_bodies.SheetMetalBody(0)
            self.converts_to_sheet_metals = self.sheet_metal_container.ConvertsToSheetMetals
            self.convert_to_sheet_metal = self.converts_to_sheet_metals.ConvertToSheetMetal(0)

            if self.sheet_metal_body is None and self.convert_to_sheet_metal is None:
                self.is_sheet_metal = False
            else:
                self.is_sheet_metal = True

            # Определение толщины
            feature_7 = self.api7.IFeature7(self.part_7)
            if self.is_sheet_metal:
                variables_7 = feature_7.Variables(False, True)
                for i in variables_7:
                    if i.Name == 'SM_Thickness':
                        self.sheet_thickness = float(i.Value)
            else:
                self.body_7 = feature_7.ResultBodies
                useless_variable, x_1, y_1, z_1, x_2, y_2, z_2 = self.body_7.GetGabarit()
                self.sheet_thickness = min((x_2 - x_1, y_2 - y_1, z_2 - z_1))

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
            self.embodiments_manager = None
            self.embodiment = None
            self.layout_sheets = self.kompas_document.LayoutSheets
            self.layout_sheet = self.layout_sheets.ItemByNumber(1)
        else:
            self.application.MessageBoxEx("Данный макрос работает только с деталью",
                                          "Документ не является деталью", 0)
            sys.exit(1)

    def select_max_face(self):
        feature_7 = self.api7.IFeature7(self.part_7)
        model_objects = feature_7.ModelObjects(6)
        flat_face = []
        for i in model_objects:
            if i.IsPlanar:
                flat_face.append(i)
        flat_face_dim = []
        for i in flat_face:
            flat_face_dim.append(i.GetArea(1))
        self.selection_manager.Select(flat_face[flat_face_dim.index(max(flat_face_dim))])

    def add_drawing_object(self):
        if self.view is not None:
            self.drawing_object = self.api7.IDrawingObject(self.view)

    def add_view(self, view_name):
        """Добавить вид с именем. Обновляет вид, если уже есть с таким именем"""
        # Удалить вид если такое имя уже существует
        if self.view_projection_manager.ViewProjection(view_name) is not None:
            view_projection_7 = self.view_projection_manager.ViewProjection(view_name)
            view_projection_7.Delete()
        view_projection_7 = self.view_projection_manager.Add()
        view_projection_7.Name = view_name
        view_projection_7.Update()


class CreateDxf:
    def __init__(self):
        api = KompasAPI()

        # Сделать нормально к выделенной поверхности
        api.view_projection_manager.OrientationNormalTo(api.selection_manager.SelectedObjects)
        sleep(
            1)  # надо для того, что бы камера успела навестись в положение "Нормально к..", иначе вид получается промежуточный

        # Создать ориентацию вида по этой поверхности
        api.add_view('Для развертки')

        # Создать пустой чертеж, без рамки
        api_drawing = KompasAPI(api.documents.Add(1, True))
        api_drawing.application.HideMessage = 1

        # Вставить вид с модели с сохраненным видом, удалить рамку
        api_drawing.views.AddStandartViews(api.kompas_document.PathName, 'Для развертки', 0, 0, 0, 1, 0, 0)
        api_drawing.view = api_drawing.views.View(1)
        api_drawing.association_view = api_drawing.api7.IAssociationView(api_drawing.view)
        if api.is_sheet_metal:
            api_drawing.association_view.Unfold = True
        api_drawing.embodiments_manager = api_drawing.api7.IEmbodimentsManager(api_drawing.association_view)
        api_drawing.embodiments_manager.SetCurrentEmbodiment(api.current_embodiment_marking)
        api_drawing.association_view.Update()
        api_drawing.kompas_document_2d_1.RebuildDocument()  # перестроение всего документа, скорее всего излишнее действие
        api_drawing.layout_sheet.Delete()

        # Сохранить как dxf
        api_drawing.convert = api_drawing.application.Converter(api_drawing.lib_path)
        api_drawing.convert.Convert(api_drawing.kompas_document.PathName,
                                    api.kompas_document.PathName.rpartition('.')[0] +
                                    api.embodiments_manager.GetCurrentEmbodimentMarking(2, False) + ' ' +
                                    str(api.sheet_thickness) + ' мм ' +
                                    ".dxf", 1, False)
        api_drawing.application.HideMessage = 0

        # Закрыть чертеж
        api_drawing.kompas_document.Close(0)


if __name__ == '__main__':
    create_dxf = CreateDxf()




