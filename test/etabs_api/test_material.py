import pytest
import comtypes.client
from pathlib import Path
import sys

civil_path = Path(__file__).parent.parent.parent
sys.path.insert(0, str(civil_path))
from etabs_api import etabs_obj

@pytest.fixture
def shayesteh(edb="shayesteh.EDB"):
    try:
        etabs = etabs_obj.EtabsModel(backup=False)
        if etabs.success:
            filepath = Path(etabs.SapModel.GetModelFilename())
            if 'test.' in filepath.name:
                return etabs
            else:
                raise NameError
    except:
        helper = comtypes.client.CreateObject('ETABSv1.Helper') 
        helper = helper.QueryInterface(comtypes.gen.ETABSv1.cHelper)
        ETABSObject = helper.CreateObjectProgID("CSI.ETABS.API.ETABSObject")
        ETABSObject.ApplicationStart()
        SapModel = ETABSObject.SapModel
        SapModel.InitializeNewModel()
        SapModel.File.OpenFile(str(Path(__file__).parent / edb))
        asli_file_path = Path(SapModel.GetModelFilename())
        dir_path = asli_file_path.parent.absolute()
        test_file_path = dir_path / "test.EDB"
        SapModel.File.Save(str(test_file_path))
        etabs = etabs_obj.EtabsModel(backup=False)
        return etabs

@pytest.mark.getmethod
def test_all_material(shayesteh):
    names = shayesteh.material.all_material()
    assert len(names) == 8

@pytest.mark.getmethod
def test_get_material_of_type(shayesteh):
    names = shayesteh.material.get_material_of_type(2)
    assert set(names) == {'CONC', 'FLOOR'}
    names = shayesteh.material.get_material_of_type(1)
    assert set(names) == {'STEEL'}