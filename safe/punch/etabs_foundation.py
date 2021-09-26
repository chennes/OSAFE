from os.path import join, dirname, abspath
from typing import Union

import FreeCAD
import FreeCADGui
import Part


class Foundation:
	def __init__(self, obj):
		obj.Proxy = self
		self.Type = "Foundation"
		self.set_properties(obj)

	def set_properties(self, obj):

		if not hasattr(obj, "fc"):
			obj.addProperty(
				"App::PropertyPressure",
				"fc",
				"Foundation",
				)

		if not hasattr(obj, "height"):
			obj.addProperty(
				"App::PropertyLength",
				"height",
				"Foundation",
				)

		if not hasattr(obj, "cover"):
			obj.addProperty(
				"App::PropertyLength",
				"cover",
				"Foundation",
				)
		if not hasattr(obj, "d"):
			obj.addProperty(
				"App::PropertyLength",
				"d",
				"Foundation",
				)

		if not hasattr(obj, "tape_slabs"):
			obj.addProperty(
				"App::PropertyLinkList",
				"tape_slabs",
				"Foundation",
				)

		if not hasattr(obj, "plane"):
			obj.addProperty(
				"Part::PropertyPartShape",
				"plane",
				"Foundation",
				)
		if not hasattr(obj, "openings"):
			obj.addProperty(
				"App::PropertyLinkList",
				"openings",
				"Foundation",
				)

	def execute(self, obj):
		doc = obj.Document
		tape_slabs = []
		for o in doc.Objects:
			if all(
				[hasattr(o, "Proxy"),
				hasattr(o.Proxy, "Type"),
				o.Proxy.Type in ("tape_slab", "trapezoidal_slab"),
				]):
				tape_slabs.append(o)
		obj.tape_slabs = tape_slabs
		new_shape = tape_slabs[0].solid
		new_shape = new_shape.fuse([i.solid for i in tape_slabs[1:]])
		if len(obj.openings) > 0:
			new_shape = new_shape.cut([o.Shape for o in obj.openings])
		obj.Shape = new_shape.removeSplitter()
		for f in obj.Shape.Faces:
			if f.BoundBox.ZLength == 0 and f.BoundBox.ZMax == 0:
				foundation_plane = f
				break
		obj.plane = foundation_plane
		obj.d = obj.height - obj.cover

	def onDocumentRestored(self, obj):
		obj.Proxy = self
		self.set_properties(obj)
        
class ViewProviderFoundation:

	def __init__(self, vobj):

		vobj.Proxy = self
		vobj.Transparency = 40
		vobj.ShapeColor = (0.32,0.42,1.00)
		vobj.DisplayMode = "Shaded"

	def attach(self, vobj):
		self.ViewObject = vobj
		self.Object = vobj.Object

	def getIcon(self):
		return join(dirname(abspath(__file__)), "Resources", "icons","foundation.png")

	def __getstate__(self):
		return None

	def __setstate__(self, state):
		return None

	def claimChildren(self):
		children=[FreeCAD.ActiveDocument.getObject(o.Name) for o in self.Object.tape_slabs] + \
				[FreeCAD.ActiveDocument.getObject(o.Name) for o in self.Object.openings]
		return children

def make_foundation(
	cover: float = 75,
	fc: int = 25,
	height : int = 800,
	):
	obj = FreeCAD.ActiveDocument.addObject("Part::FeaturePython", "Foundation")
	# obj = FreeCAD.ActiveDocument.addObject("Part::MultiFuse", "Fusion")
	Foundation(obj)
	if FreeCAD.GuiUp:
		ViewProviderFoundation(obj.ViewObject)
	obj.cover = cover
	obj.fc = f"{fc} MPa"
	obj.height = height
	obj.d = height - cover
	FreeCAD.ActiveDocument.recompute()
	return obj




		