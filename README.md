## DXF creator for kompas-3d
For version 0.5

### Описание и назначение
Макрос предназначен для ускоренного создания разверток в формате dxf из деталей kompas-3d (формат m3d). А так же создания pdf файла из чертежа.

Утилита для автоматического экспорта документов КОМПАС-3D:
- детали `.m3d` → DXF (развёртки листовых деталей, все исполнения)
- чертежи и спецификации `.cdw` `.spw` → PDF

## Требования
- Windows
- Установленный КОМПАС-3D (API7, библиотека Pdf2d.dll)
- Python 3.14 (для сборки из исходников)

## Использование
1. Запустить `main.exe` (или `python main.py`).
2. Перетащить файлы `.m3d`, `.cdw`, `.spw` в зону drag&drop.
3. Нажать «Создать группу».
4. Результат появится рядом с исходными файлами.

### Сборка проекта
Для сборки используется, но надо заменить путь

```cmd
pyinstaller --name dxf_creator --noconfirm --windowed --add-data "assets;assets" --add-data "C:\Users\rodchenko.aa\AppData\Local\Programs\Python\Python314\Lib\site-packages\tkinterdnd2;tkinterdnd2/" --collect-data customtkinter --hidden-import=win32timezone main.py
```
```cmd
Copy-Item README.md dist\dxf_creator\README.md
```