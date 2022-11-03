import math
import os

try:
    rs = __import__("rhinoscriptsyntax")
except:
    import rhinoscript as rs

import Rhino.Geometry as rh
import sys
import imp

if os.getenv("USER") == "sofyadobycina":
    PWD = os.getenv("HOME") + "/Documents/GitHub/mmodel/panels_gh"
    sys.path.extend([os.getenv("HOME") + "/Documents/GitHub/mmodel/panels_gh",
                     os.getenv("HOME") + "/Documents/GitHub/mmodel/panels_gh/main_sides",
                     os.getenv("HOME") + "/Documents/GitHub/mmodel/panels_gh/main_panels"])
else:
    PWD = os.getenv("MMODEL_DIR") + "/panels_gh"
    sys.path.extend(
        [os.getenv("MMODEL_DIR") + "/panels_gh", os.getenv("MMODEL_DIR") + "/panels_gh/cogs"])

sidesfile, sidesfilename, (sidessuffix, sidesmode, sidestype) = imp.find_module("main_sides", path=[PWD])
main_sides = imp.load_module("main_sides", sidesfile, sidesfilename, (sidessuffix, sidesmode, sidestype))

main_sides.__init__("main_sides", "generic nodule")
from main_sides import BendSide, Niche, Bottom, Side, NicheShortened

reload(main_sides)

panelfile, panelfilename, (panelsuffix, panelmode, paneltype) = imp.find_module("main_panels", path=[PWD])
main_panels = imp.load_module("main_panels", panelfile, panelfilename, (panelsuffix, panelmode, paneltype))

main_panels.__init__("main_panels", "generic nodule")
from main_panels import MainPanel, NicheSide

reload(main_panels)


def bound_rec(crv):
    join = rh.Curve.JoinCurves(crv)[0]
    bound_rec = rh.PolyCurve.GetBoundingBox(join, rh.Plane.WorldXY)
    return bound_rec


class P_1(MainPanel):
    def __init__(self, surface, cogs_bend=None, tag=None):
        MainPanel.__dict__['__init__'](self, surface, cogs_bend, tag)


class P_2(MainPanel):

    @property
    def bound_plane(self):
        j = rh.Curve.JoinCurves([self.side[0].join, self.niche.join, self.side[1].join, self.bottom.fres])[0]
        b_r = j.GetBoundingBox(rh.Plane.WorldXY)
        fr = self.side[1].fres.FrameAt(self.side[1].fres.Domain[0])[1]
        bound_plane = rh.Plane(b_r.Max, fr.XAxis, fr.YAxis)
        tr = rh.Transform.PlaneToPlane(bound_plane, rh.Plane.WorldXY)
        return tr

    @property
    def frame_dict(self):
        diag = self.diag_side([self.top_parts[1].PointAtEnd, self.top_parts[2].PointAtStart, self.fres[1].PointAtEnd])
        top = self.top_side()
        p_niche = self.fres[1]
        p_bend = self.fres[2]
        order = [[p_bend, self.bend_ofs, 'st'], [diag, self.diag, False], [p_niche, self.niche_ofs, 'both'],
                 [top, self.top_ofs, 'e']]
        bridge = [[2, self.top_parts[1], None], [0, self.top_parts[2], None]]

        return {'p_niche': p_niche, 'p_bend': p_bend, 'order': order, 'bridge': bridge}

    def __init__(self, surface, cogs_bend=None, tag=None):
        MainPanel.__dict__['__init__'](self, surface, cogs_bend, tag)

    def gen_side_types(self):
        self.niche = Niche(self.edges[2])
        self.bottom = Bottom(self.edges[0])
        self.side = [Side(self.edges[1], False), Side(self.edges[3], True)]

        self.side_types = [self.niche, self.bottom, self.side[0], self.side[1]]
        self.intersect()


class N_1(NicheSide):

    @property
    def bound_plane(self):
        j = rh.Curve.JoinCurves([self.side[0].join, self.niche.join, self.side[1].join, self.bottom.fres])[0]
        b_r = j.GetBoundingBox(rh.Plane.WorldXY)
        fr = self.niche.fres.FrameAt(self.niche.fres.Domain[0])[1]
        bound_plane = rh.Plane(rh.Point3d(b_r.Max[0], b_r.Min[1], 0), fr.XAxis, -fr.YAxis)
        tr = rh.Transform.PlaneToPlane(bound_plane, rh.Plane.WorldXY)
        return tr

    def __init__(self, surface, rib=None, back=None, cogs_bend=None, tag=None):
        NicheSide.__dict__['__init__'](self, surface, rib, back, cogs_bend, tag)


class N_3(NicheSide):
    @property
    def bound_plane(self):
        j = rh.Curve.JoinCurves([self.side[0].join, self.niche.join, self.side[1].join, self.bottom.fres])[0]
        b_r = j.GetBoundingBox(rh.Plane.WorldXY)
        fr = self.niche.fres.FrameAt(self.niche.fres.Domain[0])[1]
        bound_plane = rh.Plane(rh.Point3d(b_r.Min[0], b_r.Max[1], 0), fr.XAxis, -fr.YAxis)
        tr = rh.Transform.PlaneToPlane(bound_plane, rh.Plane.WorldXY)
        return tr

    @property
    def frame_dict(self):
        diag = self.diag_side([self.top_parts[2].PointAtEnd, self.top_parts[1].PointAtStart, self.fres[1].PointAtStart])
        top = self.top_side()
        p_niche = self.fres[1]
        p_bend = self.fres[2]
        order = [[p_niche, self.niche_ofs, 'st'], [diag, self.diag, False], [p_bend, self.bend_ofs, 'both'],
                 [top, self.top_ofs, 'e']]
        bridge = [[0, self.top_parts[1], None], [2, self.top_parts[2], None]]

        return {'p_niche': p_niche, 'p_bend': p_bend, 'order': order, 'bridge': bridge}

    def __init__(self, surface, rib=None, back=None, cogs_bend=None, tag=None):
        NicheSide.__dict__['__init__'](self, surface, rib, back, cogs_bend, tag)

    def gen_side_types(self):
        self.niche = NicheShortened(self.edges[0])
        self.bottom = Bottom(self.edges[2])
        self.side = [Side(self.edges[1], True), Side(self.edges[3], False)]

        self.side_types = [self.niche, self.bottom, self.side[0], self.side[1]]
        self.intersect()


class N_2(NicheSide):
    bend_ofs = 45
    top_ofs = 0
    niche_ofs = 10

    bottom_rec = 30
    side_rec = 30

    @property
    def bound_plane(self):
        vec = rh.Vector3d(self.top.fres.PointAtEnd - self.top.fres.PointAtStart)
        rot = rh.Vector3d(self.top.fres.PointAtEnd - self.top.fres.PointAtStart)

        rot.Rotate(math.pi / 2, rh.Plane.WorldXY.ZAxis)

        bound_plane = rh.Plane(self.top.fres.PointAtStart, vec, rot)
        tr = rh.Transform.PlaneToPlane(bound_plane, rh.Plane.WorldXY)
        return tr

    @property
    def fres(self):
        fres = [rh.Curve.DuplicateCurve(self.side[0].fres), rh.Curve.DuplicateCurve(self.side[1].fres)]
        [i.Transform(self.bound_plane) for i in fres]
        return fres

    @property
    def cut(self):
        cut = [rh.Curve.JoinCurves([self.side[0].join, self.top.fres, self.side[1].join, self.bottom.fres])[0]]
        [i.Transform(self.bound_plane) for i in cut]
        return cut

    @property
    def grav(self):
        new = self.mark_back
        return new

    @property
    def top_parts(self):
        top = [self.side[0].top_part.DuplicateCurve(), self.side[1].top_part.DuplicateCurve()]
        [i.Transform(self.bound_plane) for i in top]
        return top

    @property
    def frame_dict(self):
        # diag = self.diag_side([self.top_parts[2].PointAtEnd, self.top_parts[1].PointAtStart, self.fres[
        # 1].PointAtStart])
        bf = self.top.fres.DuplicateCurve()
        bf.Transform(self.bound_plane)
        p_niche = bf
        p_bend = self.fres[0]

        ll = self.fres
        ll.append(p_niche)
        bound = bound_rec(ll)
        top = bound.GetEdges()[2].ToNurbsCurve()

        order = [[p_niche, self.niche_ofs, 'st'], [p_bend, self.bend_ofs, 'both'],
                 [top, self.top_ofs, 'e']]
        bridge = [[0, p_niche, None], [1, self.top_parts[0], True]]

        return {'p_niche': p_niche, 'p_bend': p_bend, 'order': order, 'bridge': bridge}

    def __init__(self, surface, rib=None, tag=None):
        NicheSide.__dict__['__init__'](self, surface, rib, tag)

        self.extend = self.extend_surf()
        self.rev_surf = self.surf.Surfaces[0].Reverse(1).ToBrep()

        unrol = rh.Unroller(self.rev_surf)

        if rib is not None:
            self.rebra = rib
            self.intersections = self.rebra_intersect()
            unrol.AddFollowingGeometry(curves=self.intersections)
        else:
            pass

        self.unrol = unrol.PerformUnroll()

        self.unrol_surf = self.unrol[0][0]
        self.edges = self.unrol_surf.Curves3D
        self.gen_side_types()

    def gen_side_types(self):
        self.top = Bottom(self.edges[1])
        self.bottom = Bottom(self.edges[3])
        self.side = [Side(self.edges[0]), Side(self.edges[2])]

        self.side_types = [self.top, self.bottom, self.side[0], self.side[1]]
        self.intersect()

    def extend_surf(self):
        surf = self.surf.Surfaces[0].Duplicate()
        interv = surf.Domain(0)
        interv = rh.Interval(interv[0] - 50, interv[1] + 50)

        surf.Extend(0, interv)
        extr = rh.Surface.ToBrep(surf)
        print(extr)

        return extr