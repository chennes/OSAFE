from pathlib import Path

from PySide2.QtWidgets import QMessageBox

import FreeCAD
import FreeCADGui as Gui

from safe.punch.py_widget import resource_rc

punch_path = Path(__file__).parent.parent.parent


class Form:

    def __init__(self):
        self.form = Gui.PySideUic.loadUi(str(punch_path / 'Resources' / 'ui' / 'export_to_dxf.ui'))
        self.fill_filename()
        self.create_connections()

    def fill_filename(self):
        doc = FreeCAD.ActiveDocument
        name = Path(doc.FileName).with_suffix('.dxf')
        self.form.filename.setText(str(name))

    def create_connections(self):
        self.form.browse.clicked.connect(self.browse)
        self.form.export_button.clicked.connect(self.export)

    def browse(self):
        ext = '.dxf'
        from PySide2.QtWidgets import QFileDialog
        filters = f"{ext[1:]} (*{ext})"
        filename, _ = QFileDialog.getSaveFileName(None, 'select file',
                                                None, filters)
        if not filename:
            return
        if not filename.lower().endswith(ext):
            filename += ext
        self.form.filename.setText(filename)

    def export(self):
        filename = self.form.filename.text()
        if not filename:
            return
        from safe.punch import export
        ret = export.to_dxf(
            filename,
            columns=self.form.columns_checkbox.isChecked(),
            punches=self.form.punches_checkbox.isChecked(),
        )
        if ret:
            QMessageBox.information(None, 'Successful', f'Model has been exported to {filename}')

    
    def accept(self):
        Gui.Control.closeDialog()
