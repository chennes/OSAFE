import pytest
import comtypes.client
from pathlib import Path
import sys

FREECADPATH = 'G:\\program files\\FreeCAD 0.19\\bin'
sys.path.append(FREECADPATH)
import FreeCAD

filename = Path(__file__).absolute().parent.parent / 'etabs_api' / 'test_files' / 'freecad' / '2.FCStd'
document= FreeCAD.openDocument(str(filename))

civil_path = Path(__file__).parent.parent.parent
sys.path.insert(0, str(civil_path))
from etabs_api import etabs_obj

@pytest.fixture
def shayesteh(edb="shayesteh.FDB", software='SAFE'):
    try:
        etabs = etabs_obj.EtabsModel(backup=False, software=software)
        if etabs.success:
            filepath = Path(etabs.SapModel.GetModelFilename())
            if 'test.' in filepath.name:
                return etabs
            else:
                raise NameError
    except:
        helper = comtypes.client.CreateObject(f'{software}v1.Helper') 
        helper = helper.QueryInterface(f'comtypes.gen.{software}v1.cHelper')
        ETABSObject = helper.CreateObjectProgID(f"CSI.{software}.API.ETABSObject")
        ETABSObject.ApplicationStart()
        SapModel = ETABSObject.SapModel
        SapModel.InitializeNewModel()
        SapModel.File.OpenFile(str(Path(__file__).parent / edb))
        asli_file_path = Path(SapModel.GetModelFilename())
        dir_path = asli_file_path.parent.absolute()
        test_file_path = dir_path / "test.FDB"
        SapModel.File.Save(str(test_file_path))
        etabs = etabs_obj.EtabsModel(backup=False)
        return etabs

def test_export_freecad_slabs(shayesteh):
    slabs = document.Foundation.tape_slabs
    shayesteh.area.export_freecad_slabs(slabs)
    assert shayesteh.SapModel.AreaObj.GetNameList()[0] == len(slabs)

if __name__ == '__main__':
    test_export_freecad_slabs(shayesteh)