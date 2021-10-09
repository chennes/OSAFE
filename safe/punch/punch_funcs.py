from typing import List, Union
import math

import FreeCAD
import Part


def remove_obj(name: str) -> None:
	o = FreeCAD.ActiveDocument.getObject(name)
	if hasattr(o, "Base") and o.Base:
		remove_obj(o.Base.Name)
	if hasattr(o, "Tool") and o.Tool:
		remove_obj(o.Tool.Name)
	if hasattr(o, "Shapes") and o.Shapes:
		for sh in o.Shapes:
			remove_obj(sh.Name)
	FreeCAD.ActiveDocument.removeObject(name)


def rectangle_face(
	center: FreeCAD.Vector,
	bx: Union[float, int],
	by: Union[float, int],
	):

	v1, v2, v3, v4 = rectangle_vertexes(center, bx, by)
	return Part.Face(Part.makePolygon([v1, v2, v3, v4, v1]))

def rectangle_vertexes(
                       center: FreeCAD.Vector,
                       bx: Union[float, int],
                       by: Union[float, int],
                       ):
	dx = bx / 2
	dy = by / 2
	v1 = center.add(FreeCAD.Vector(-dx, -dy, 0))
	v2 = center.add(FreeCAD.Vector(dx, -dy, 0))
	v3 = center.add(FreeCAD.Vector(dx, dy, 0))
	v4 = center.add(FreeCAD.Vector(-dx, dy, 0))
	return [v1, v2, v3, v4]

def punch_area_edges(
	sh1: Part.Shape,
	sh2: Part.Shape,
	):

	cut = sh1.cut(sh2)
	edges = []
	for e in cut.Edges:
		p1 = e.firstVertex().Point
		p2 = e.lastVertex().Point
		if sh2.isInside(p1, .1, True) and sh2.isInside(p2, .1, True):
			edges.append(e)
	return edges

def punch_faces(
	edges: List[Part.Edge],
	d: Union[float, int],
	):
	faces = []
	for e in edges:
		face = e.extrude(FreeCAD.Vector(0, 0, -d))
		faces.append(face)
	return faces

def lenght_of_edges(
	edges: List[Part.Edge],
	):
	length = 0
	for e in edges:
		length += e.Length
	return length

def area(
	faces: List[Part.Face],
	):
	area = 0
	for f in faces:
		area += f.Area
	return area

def center_of_mass(
	faces: List[Part.Face],
	) -> FreeCAD.Vector:
	'''
	gives faces and return the center of mass coordinate
	'''
	sorat_x = 0
	sorat_y = 0
	sorat_z = 0
	makhraj = 0

	for f in faces:
		area = f.Area
		x = f.CenterOfMass.x
		y = f.CenterOfMass.y
		z = f.CenterOfMass.z
		sorat_x += area * x
		sorat_y += area * y
		sorat_z += area * z
		makhraj += area
	if makhraj == 0:
		return None
	return FreeCAD.Vector(sorat_x / makhraj, sorat_y / makhraj, sorat_z / makhraj)

def moment_inersia(
	faces: List[Part.Face],
	):
	'''
	return rotational moment inersia of faces list Ixx, Iyy
	'''
	Ixx = 0
	Iyy = 0
	Ixy = 0
	com = center_of_mass(faces)
	if not com:
		return 0, 0, 0
	x_bar, y_bar, z_bar = com
	for f in faces:
		A = f.Area
		x = f.CenterOfMass.x
		y = f.CenterOfMass.y
		z = f.CenterOfMass.z
		ixx = f.MatrixOfInertia.A11
		iyy = f.MatrixOfInertia.A22
		dx = abs(x - x_bar)
		dy = abs(y - y_bar)
		# dz = z - z_bar
		normal = f.normalAt(0, 0)
		if normal.x:
			Ixx += ixx + A * dy ** 2
			Iyy += A * (dx ** 2)  # + dz ** 2)
		elif normal.y:
			Ixx += A * (dy ** 2)  # + dz ** 2)
			Iyy += iyy + A * dx ** 2
		Ixy += A * dx * dy
	return Ixx, Iyy, Ixy

def location_of_column(
	faces: List[Part.Face],
	) -> str:

	faces_normals = {'x': [], 'y': []}
	for f in faces:
		normal = f.normalAt(0, 0)
		normal_x = normal.x
		normal_y = normal.y
		if normal_x:
			if not normal_x in faces_normals['x']:
				faces_normals['x'].append(normal_x)
		if normal_y:
			if not normal_y in faces_normals['y']:
				faces_normals['y'].append(normal_y)
	if not (faces_normals['x'] and faces_normals['y']):
		return None

	no_of_faces = len(faces_normals['x'] + faces_normals['y'])
	if no_of_faces == 2:
		signx = faces_normals['x'][0] > 0
		signy = faces_normals['y'][0] > 0
		if not signy:
			if not signx:
				return 'Corner3'
			elif signx:
				return 'Corner4'
		elif signy:
			if signx:
				return 'Corner1'
			elif not signx:
				return 'Corner2'
		else:
			return 'Corner'
	elif no_of_faces == 3:
		sumx = sum(faces_normals['x'])
		sumy = sum(faces_normals['y'])
		if sumx == 0:
			if sumy == -1:
				return 'Edge3'
			elif sumy == 1:
				return 'Edge1'
		elif sumy == 0:
			if sumx == 1:
				return 'Edge4'
			elif sumx == -1:
				return 'Edge2'
		else:
			return 'Edge'
	else:
		return 'Interier'


def allowable_stress(bx, by, location, fc, b0, d, ACI2019=False, phi_c=.75):
	alpha_ss = {'interier': 40, 'edge': 30, 'corner': 20}
	b0d = b0 * d
	beta = bx / by
	if beta < 1:
		beta = by / bx
	if ACI2019:
		lambda_s = min(math.sqrt(2 / (1 + .004 * d)), 1)
	else:
		lambda_s = 1
	alpha_s = alpha_ss[location]
	one_way_shear_capacity = math.sqrt(fc) * b0d / 6 * phi_c * lambda_s
	Vc1 = one_way_shear_capacity * 2
	Vc2 = one_way_shear_capacity * (1 + 2 / beta)
	Vc3 = one_way_shear_capacity * (2 + alpha_s * d / b0) / 2
	Vc = min(Vc1, Vc2, Vc3)
	vc = Vc / (b0d)
	return vc

def gamma_v(
            bx: Union[float, int],
            by: Union[float, int],
            ) -> tuple:
	gamma_fx = 1 / (1 + (2 / 3) * math.sqrt(by / bx))
	gamma_fy = 1 / (1 + (2 / 3) * math.sqrt(bx / by))
	gamma_vx = 1 - gamma_fx
	gamma_vy = 1 - gamma_fy
	return (gamma_vx, gamma_vy)

def get_user_location_faces(
                            faces: List[Part.Face],
                            location: str,
                            ) -> List[Part.Face]:

	location_normals = {
			'Corner3': [(0, -1, 0), (-1, 0, 0)],
			'Corner4': [(0, -1, 0), (1, 0, 0)],
			'Corner1': [(0, 1, 0), (1, 0, 0)],
			'Corner2': [(0, 1, 0), (-1, 0, 0)],
			'Edge3': [(0, -1, 0), (-1, 0, 0), (1, 0, 0)],
			'Edge4': [(0, -1, 0), (1, 0, 0), (0, 1, 0)],
			'Edge1': [(0, 1, 0), (1, 0, 0), (-1, 0, 0)],
			'Edge2': [(0, 1, 0), (-1, 0, 0), (0, -1, 0)],
			'Interier': [(0, 1, 0), (-1, 0, 0), (0, -1, 0), (1, 0, 0)]
			}

	normals = location_normals[location]
	if len(normals) >= len(faces):
		return faces
	new_faces = []
	for f in faces:
		normal = tuple(f.normalAt(0, 0))
		if normal in normals:
			new_faces.append(f)
	return new_faces

def sort_vertex(coords):
	from functools import reduce
	import operator
	center = tuple(map(operator.truediv, reduce(lambda x, y: map(operator.add, x, y), coords), [len(coords)] * 2))
	return sorted(coords, key=lambda coord: (-135 - math.degrees(math.atan2(*tuple(map(operator.sub, coord, center))[::-1]))) % 360)

def get_sort_points(edges, vector=True):
	points = []
	edges = Part.__sortEdges__(edges)
	for e in edges:
		v = e.firstVertex()
		if vector is True:
			points.append(FreeCAD.Vector(v.X, v.Y, v.Z))
		else:
			points.append(v)
	return points

def get_obj_points_with_scales(
	shape : Part.Shape, 
	scales : list = [.75, .5],
	) -> list:
	vertexes, _ = get_sort_points(shape.Edges)
	center_of_mass = shape.CenterOfMass
	lines = []
	for v in vertexes:
		line = Part.makeLine(v, center_of_mass)
		lines.append(line)
	original_points = [FreeCAD.Vector(vec.x, vec.y, vec.z) for vec in vertexes]
	scale_points = []
	scale_points.append(original_points)
	for scale in scales:
		points = []
		for line in lines:
			point = line.valueAt((1 - scale) * line.Length)
			points.append(point)
		scale_points.append(points)
	return scale_points

def get_scale_area_points_with_scale(
	shape : Part.Shape, 
	scales : list = [.75, .5],
	) -> list:
	scale_points = get_obj_points_with_scales(shape, scales)
	area_points = []
	for points1, points2  in zip(scale_points[:-1], scale_points[1:]):
		n = len(points1) // 2
		points11 = points1[:n + 1]
		points12 = points1[n:]
		points21 = points2[:n + 1]
		points22 = points2[n:]
		points21.reverse()
		points22.reverse()
		area_points.extend((
			points11 + points21,
			points12 + points22,
			))
	area_points.append(scale_points[-1])
	return area_points

def split_face_with_scales(
	face : Part.Face,
	scales : list = [.75, .5],
	) -> list:
	from BOPTools.GeneralFuseResult import GeneralFuseResult
	s1 = face.copy().scale(scales[0])
	s2 = face.copy().scale(scales[1])
	center_of_mass = face.CenterOfMass
	tr1 = center_of_mass.sub(s1.CenterOfMass)
	s1.Placement.Base = tr1
	tr2 = center_of_mass.sub(s2.CenterOfMass)
	s2.Placement.Base = tr2
	area1 = face.cut(s1)
	area2 = s1.cut(s2)
	e1, e2 = sorted(face.Edges, key=lambda x: x.Length, reverse=True)[0:2]
	v1 = e1.CenterOfMass
	v2 = e2.CenterOfMass
	poly = Part.makePolygon([v1, center_of_mass, v2])
	faces = []
	for area in (area1, area2):
		pieces, map_ = area.generalFuse([poly])
		gr = GeneralFuseResult([area, poly], (pieces,map_))
		gr.splitAggregates()
		comp = Part.Compound(gr.pieces)
		faces.extend(comp.Faces)
	faces.append(Part.Face(s2))
	return faces

def get_sub_areas_points_from_face_with_scales(
	face : Part.Face,
	scales : list = [.75, .5],
	) -> list:
	faces = split_face_with_scales(face, scales)
	faces_points = []
	for f in faces:
		points = get_sort_points(f.Edges)
		faces_points.append(points)
	return faces_points

def get_points_connections_from_slabs(slabs):
	d = {}
	for s in slabs:
		v1 = s.start_point
		v2 = s.end_point
		for v in (v1, v2):
			p = (v.x, v.y, v.z)
			current_slabs = d.get(p, None)
			if current_slabs is None:
				d[p] = [s]
			else:
				d[p].append(s)
	return d
			
