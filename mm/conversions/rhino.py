#  Copyright (c) 2022. Computational Geometry, Digital Engineering and Optimizing your construction processe"
import warnings

import compas_occ.geometry
import numpy as np
import rhino3dm

from mm.baseitems import Item


class RhinoBind(Item):
    source_cls = None

    def __init__(self, *args, **kwargs):
        super().__init__()
        self.source = self.source_cls(*args, **kwargs)


class RhDesc:
    def __set_name__(self, own, name):
        self.name = name

    def __get__(self, inst, ow=None):
        return getattr(inst.source, self.name)

    def __set__(self, inst, v):
        setattr(inst.source, self.name, v)


class RhinoPoint(RhinoBind):
    source_cls = rhino3dm.Point3d
    X = RhDesc()
    Y = RhDesc()
    Z = RhDesc()
    DistanceTo = RhDesc()

    @property
    def xyz(self):
        return self.X, self.Y, self.Z

    def __str__(self):
        return f"RhinoPoint({self.__array__()})"

    def __repr__(self):
        return f"RhinoPoint({self.__array__()})"

    def __list__(self):
        return list(self.xyz)

    def __array__(self):
        return np.array(self.xyz)

    def __sub__(self, other):
        return self.__class__(self.X - other.X, self.Y - other.Y, self.Z - other.Z)

    def __add__(self, other):
        return self.__class__(self.X + other.X, self.Y + other.Y, self.Z + other.Z)


class RhinoAxis(RhinoBind):
    """
    >>> ax = RhinoAxis(RhinoPoint(1, 2, 3), RhinoPoint(12, 2, 3))
    >>> ax.end
    RhinoPoint([12.  2.  3.])
    >>> ax.end.DistanceTo(ax.start.source)
    11.0

    """
    source_cls = rhino3dm.Line
    From = RhDesc()
    To = RhDesc()

    def __init__(self, start, end, **kwargs):
        super().__init__(start.source, end.source, **kwargs)

    @property
    def start(self):
        return RhinoPoint(self.From.X, self.From.Y, self.From.Z)

    @property
    def end(self):
        return RhinoPoint(self.To.X, self.To.Y, self.To.Z)


class RhinoCircle(RhinoBind):
    source_cls = rhino3dm.Circle
    radius = 1.0
    Center = RhDesc()
    Plane = RhDesc()


class RhinoRuledSurf(RhinoBind):
    source_cls = rhino3dm.NurbsSurface.CreateRuledSurface
    curve_a = None
    curve_b = None

    def __init__(self, curve_a, curve_b, **kwargs):
        super().__init__(curve_a.source.ToNurbsCurve(), curve_b.source.ToNurbsCurve(), **kwargs)


class RhinoBiCone:
    source_cls = rhino3dm.NurbsSurface.CreateRuledSurface
    radius_start = 1.0
    radius_end = 0.5
    point_start = RhinoPoint(22, 22, -11)
    point_end = RhinoPoint(1, 0, 1)

    def __init__(self, *args, **kwargs):
        super().__init__()
        self.__dict__ |= kwargs

    @property
    def plane1(self):
        return rhino3dm.Plane(self.point_start.source,
                              rhino3dm.Vector3d(*(self.point_end - self.point_start).__array__()))

    @property
    def plane2(self):
        return rhino3dm.Plane(self.point_end.source,
                              rhino3dm.Vector3d(*(self.point_end - self.point_start).__array__()))

    @property
    def c1(self):
        T = cg.Transformation.from_frame(
            cg.Frame.from_plane(
                cg.Plane(list([self.plane1.Origin.X, self.plane1.Origin.Y, self.plane1.Origin.Z]),
                         list([self.plane1.ZAxis.X, self.plane1.ZAxis.Y, self.plane1.ZAxis.Z]))))
        t = rhino3dm.Transform(1.0)
        c = rhino3dm.Circle(self.radius_start)
        i, j = np.asarray(T.matrix).shape
        for ii in range(i):
            for jj in range(j):
                setattr(t, f"M{ii}{jj}", float(np.asarray(T.matrix)[ii, jj]))
        # print(t)
        n = c.ToNurbsCurve()
        n.Transform(t)

        return n

    @property
    def c2(self):
        T = cg.Transformation.from_frame(
            cg.Frame.from_plane(
                cg.Plane(list([self.plane2.Origin.X, self.plane2.Origin.Y, self.plane2.Origin.Z]),
                         list([self.plane2.ZAxis.X, self.plane1.ZAxis.Y, self.plane1.ZAxis.Z]))))
        t = rhino3dm.Transform(1.0)
        c = rhino3dm.Circle(self.radius_end)

        i, j = np.asarray(T.matrix).shape
        for ii in range(i):
            for jj in range(j):
                setattr(t, f"M{ii}{jj}", float(np.asarray(T.matrix)[ii, jj]))
        # print(t)
        n = c.ToNurbsCurve()
        n.Transform(t)
        return n

    @property
    def source(self):
        return self.source_cls(self.c1, self.c2)


import compas.geometry as cg


def rhino_crv_from_compas(nurbs_curves: list) -> list[
    rhino3dm.NurbsCurve]:
    """
    Convert list of compas-like Nurbs curves to Rhino Nurbs Curves
    :param nurbs_curves:
    :type
    :return:
    :rtype:
    """
    return list(map(lambda x: rhino3dm.NurbsCurve.Create(
        x.is_periodic,
        x.degree,
        list(map(lambda y: rhino3dm.Point3d(*y), x.points))), nurbs_curves))


def list_curves_to_polycurves(curves):
    poly = rhino3dm.PolyCurve()
    for curve in curves:
        poly.AppendSegment(curve)
    return poly


def polyline_from_pts(pts):
    polyline = rhino3dm.Polyline(0)
    for pt in pts:
        polyline.Add(*pt)
    if polyline.IsValid:
        return polyline
    else:
        warnings.warn("InValid Rhino Object")
        return polyline
