from PyInstaller.compat import system
from win32com.client import Dispatch, gencache, VARIANT

api7 = gencache.EnsureModule("{69AC2981-37C0-4379-84FD-5DD2F3C0A520}", 0, 1, 0)
application = Dispatch("KOMPAS.Application.7")
kompas_document = application.ActiveDocument

kompas_document_3d_1 = api7.IKompasDocument3D1(kompas_document)
kompas_document_3d = api7.IKompasDocument3D(kompas_document)
view_projection_manager = kompas_document_3d_1.ViewProjectionManager

print(view_projection_manager.ViewProjection('kkk'))