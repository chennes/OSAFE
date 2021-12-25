

class CivilWorkbench(Workbench):

    def __init__(self):

        from pathlib import Path
        import civilwelcome
        self.__class__.Icon = str(Path(civilwelcome.__file__).parent.absolute() / 'images' / 'civil-engineering.png')
        self.__class__.MenuText = "Civil"
        self.__class__.ToolTip = "Civil Workbench"

    def Initialize(self):
        from pathlib import Path
        from PySide2 import QtCore
        import civilGui

        command_list = civilGui.command_list
        export_list = civilGui.export_list
        draw_list = civilGui.draw_list
        assign_list = civilGui.assign_list
        civiltools_list = civilGui.civiltools_list

        self.appendToolbar(str(QtCore.QT_TRANSLATE_NOOP("Civil", "Civil tools")), command_list)
        self.appendToolbar(str(QtCore.QT_TRANSLATE_NOOP("Civil", "Civil Export")), export_list)
        self.appendToolbar(str(QtCore.QT_TRANSLATE_NOOP("Civil", "Civil Draw")), draw_list)
        self.appendToolbar(str(QtCore.QT_TRANSLATE_NOOP("Civil", "Civil Assign")), assign_list)
        self.appendToolbar(str(QtCore.QT_TRANSLATE_NOOP("Civil", "civiltools")), civiltools_list)
        self.appendMenu(str(QtCore.QT_TRANSLATE_NOOP("Civil", "Civil")), command_list)
        self.appendMenu(str(QtCore.QT_TRANSLATE_NOOP("Civil", "Export")), export_list)
        self.appendMenu(str(QtCore.QT_TRANSLATE_NOOP("Civil", "Draw")), draw_list)
        self.appendMenu(str(QtCore.QT_TRANSLATE_NOOP("Civil", "Assign")), assign_list)

        pref_visual_ui_abs_path = str(Path(civilGui.__file__).parent.absolute() / 'ui' / 'preferences-punch_visual.ui')
        Gui.addPreferencePage(pref_visual_ui_abs_path, "punch")
        Gui.addIconPath(
            str(
                Path(civilGui.__file__).parent.absolute()
                / "images"
                )
            )

    def Activated(self):
        if FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/Civil").GetBool("FirstTime", True):
            from DraftGui import todo
            todo.delay(Gui.runCommand, "Civil_welcome")


Gui.addWorkbench(CivilWorkbench())
