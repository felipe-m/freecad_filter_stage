# ----------------------------------------------------------------------------
# -- Circuit models
# -- Python scripts to make circuit models
# ----------------------------------------------------------------------------
# -- (c) Felipe Machado
# -- Area of Electronics. Rey Juan Carlos University (urjc.es)
# -- February-2018
# ----------------------------------------------------------------------------
# --- LGPL Licence
# ----------------------------------------------------------------------------

# to execute from the FreeCAD console:
#  execute freecad from the cmd console on the directory
# "C:\Program Files\FreeCAD 0.16\bin\freecad" espira.py

# to excute from command line in windows:
# "C:\Program Files\FreeCAD 0.16\bin\freecadcmd" espira.py

import os
import sys
import inspect
import FreeCAD
import FreeCADGui
import Part
import Draft
import logging


# to get the current directory. Freecad has to be executed from the same
# directory this file is
filepath = os.getcwd()
#filepath = "./"
#filepath = "F/urjc/proyectos/2016_platform_cell/device/planos/python/"
#filepath = "C:/Users/felipe/urjc/proyectos/2016_platform_cell/device/planos/python/"


# to get the components
# In FreeCAD can be added: Preferences->General->Macro->Macro path
sys.path.append(filepath) 
# Either one of these 2 to select the path, inside the tree, copied by
# git subtree, or in its one place
#sys.path.append(filepath + '/' + 'modules/comps'
sys.path.append(filepath + '/' + '../comps')


import fcfun   # import my functions for freecad. FreeCad Functions
import kcomp   # import material constants and other constants
import comps   # import my CAD components
import parts   # import my CAD components to print
import shp_clss 
import fc_clss 

from fcfun import V0, VX, VY, VZ, VXN, VYN, VZN


logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)s - %(message)s')

#doc = FreeCAD.newDocument()

Gui.ActiveDocument = Gui.getDocument(doc.Label)
guidoc = Gui.getDocument(doc.Label)


class ShpSingleTurnConmut (shp_clss.Obj3D):
    """ Creates a single turn cable with a conmutator as a simple model of
    a DC motor)

          axis_d
             :
             :
        .....:w ..... 
       :     :      :                              pos_d
        ____________ ...... ...............          4
       /            \      :..corner_r  :
       |            |      :            :
       |            |      :            :
       |            |      + d          :            3
       |            |      :            :
       |            |      :            +cable_d
       |            |      :            :
        \___   ____/ ......:            :            2
            \ /            :            :
            | |            + conn_d     :
            | |            :            :
          __| |__ .........:............:            1
         |__|o|__|.........:.conmut_d......axis_w    0
         :  : :
         : conn_sep
         :   :
         :...:
            conmut_r
            ::
            conmut_sep

       3 2  10  pos_w

       pos_o (orig) is at pos_d=0, pos_w=0, marked with o

    Parameters:
    -----------
    d : float
        depth/length of the turn
    w : float
        width of the turn
    thick_d : float
        diameter of the wire
    corner_r : float
        radius of the corners
    conn_d : float
        depth/length of the connector part
        0: there is no connecting wire
    conn_sep : float
        separation of the connectors
    conmut_d : float
        depth of the conmutator
    conmut_r : float
        radius of the conmutator
    conmut_sep : float
        separation of the conmutator
    axis_d :  FreeCAD.Vector
        Coordinate System Vector along the depth
    axis_w :  FreeCAD.Vector
        Coordinate System Vector along the width
    pos_d : int
        location of pos along the axis_d (0,1,2,3,4), see drawing
        0: reference at the beginning of the conmutator
        1: reference at the beginning of the connector
        2: reference at the beginning of the turn, at the side of the connector
        3: reference at the middle of the turn
        4: reference at the end of the turn
    pos_w : int
        location of pos along the axis_w (0,1,2,3), see drawing
        0: reference at the center of simmetry
        1: reference at the cable end
        2: reference at the end of the conmutator
        3: reference at the end of the turn
    pos: FreeCAD vector of the position of the reference

    Attributes:
    -----------
    All the parameters and attributes of father class SinglePart
    Dimensional attributes:
    tot_d : float
        total length (depth)
    tot_w : float
        total width
    cable_d : float
        total length (depth) of the cable, not including conmutator



    """

    def __init__ (self, 
                  d, w,
                  conn_d, conn_sep = 2,
                  conmut_d = 2,
                  conmut_r = 4,
                  conmut_sep = 2,
                  thick_d = 1, corner_r = 0.5,
                  axis_d = VY,
                  axis_w = VX,
                  pos_d = 0,
                  pos_w = 0,
                  pos=V0):

        shp_clss.Obj3D.__init__(self, axis_d, axis_w)

        # save the arguments as attributes:
        frame = inspect.currentframe()
        args, _, _, values = inspect.getargvalues(frame)
        for i in args:
            if not hasattr(self,i):
                setattr(self, i, values[i])



        self.d0_cen = 0
        self.w0_cen = 1 # symmetrical

        self.tot_d = d + conn_d + conmut_d
        self.tot_w = max(conmut_d,w)
        self.cable_d = d + conn_d

        # distances from the pos_o to pos_d 
        self.d_o[0] = V0
        self.d_o[1] = self.vec_d(conmut_d)
        self.d_o[2] = self.d_o[1] + self.vec_d(conn_d)
        self.d_o[3] = self.d_o[2] + self.vec_d(d/2.)
        self.d_o[4] = self.d_o[2] + self.vec_d(d)

        # these are negative because actually the pos_w indicates a negative
        # position along axis_w
        self.w_o[0] = V0
        self.w_o[1] = self.vec_w(-conn_sep/2.)
        self.w_o[2] = self.vec_w(-conmut_r)
        self.w_o[3] = self.vec_w(-w/2.)

        # calculates the position of the origin, and keeps it in attribute pos_o
        self.set_pos_o()

        shp_cable = fcfun.shp_cableturn(d = d, w = w, thick_d = thick_d,
                                        corner_r = corner_r, conn_d = conn_d,
                                        xtr_conn_d = 1,
                                        conn_sep = conn_sep, closed = 0,
                                        axis_d = self.axis_d,
                                        axis_w = self.axis_w,
                                        pos_d = 0, pos_w = 0,
                                        pos = self.get_o_to_d(1))

        shp_cyl_conmut = fcfun.shp_cylcenxtr(r = conmut_r,
                                             h = conmut_d,
                                             normal = self.axis_d,
                                             ch = 0, pos = self.pos_o)


        #left cut the conmutator
        shp_conmut_divide_l = fcfun.shp_box_dir_xtr(
                                    box_w = conmut_sep,
                                    box_d = conmut_d,
                                    box_h = 2*conmut_r,
                                    fc_axis_h = self.axis_d.cross(self.axis_w),
                                    fc_axis_d = self.axis_d,
                                    fc_axis_w = self.axis_w,
                                    cw= 1, cd=0, ch=1,
                                    xtr_h = 1, xtr_nh = 1,
                                    xtr_d = 1, xtr_nd = 1,
                                    xtr_w = 0, xtr_nw = conmut_r,
                                    pos = self.pos_o)


        #right cut the conmutator
        shp_conmut_divide_r = fcfun.shp_box_dir_xtr(
                                    box_w = conmut_sep,
                                    box_d = conmut_d,
                                    box_h = 2*conmut_r,
                                    fc_axis_h = self.axis_d.cross(self.axis_w),
                                    fc_axis_d = self.axis_d,
                                    fc_axis_w = self.axis_w,
                                    cw= 1, cd=0, ch=1,
                                    xtr_h = 1, xtr_nh = 1,
                                    xtr_d = 1, xtr_nd = 1,
                                    xtr_w = conmut_r, xtr_nw = 0,
                                    pos = self.pos_o)

        shp_conmut_l = shp_cyl_conmut.cut(shp_conmut_divide_r)
        shp_conmut_r = shp_cyl_conmut.cut(shp_conmut_divide_l)

        self.shp_conmut_l = shp_conmut_l
        self.shp_conmut_r = shp_conmut_r
        self.shp_cable = shp_cable


turn = ShpSingleTurnConmut(d = 40, w=20,
                    conn_d=8, conn_sep=2,
                    conmut_d = 2,
                    conmut_r = 2,
                    conmut_sep = 1,
                    thick_d=1,
                    corner_r=0.5,
                    axis_d = VY,
                    #axis_w = FreeCAD.Vector(-1,0,0), # 180
                    #axis_w = FreeCAD.Vector(1,0,-1),
                    axis_w = FreeCAD.Vector(1,0,1),
                    #axis_w = FreeCAD.Vector(1,0,1),
                    #axis_w = FreeCAD.Vector(1,0,0),
                    pos_d = 0,
                    pos_w = 0,
                    pos=V0)


# the brushes:

shp_brush_l = fcfun.shp_box_dir_xtr(box_w = 2*turn.conmut_r,
                              box_d = turn.conmut_d,
                              box_h = turn.conmut_sep*0.9,
                              fc_axis_h = VZ,
                              fc_axis_d = VY,
                              fc_axis_w = VXN,
                              cw= 0, cd=0, ch=1,
                              xtr_h = 0, xtr_nh = 0,
                              xtr_d = 0, xtr_nd = 0,
                              xtr_w = 0, xtr_nw = 0,
                              pos = turn.pos_o)
                              
shp_cyl_conmut = fcfun.shp_cylcenxtr(r = turn.conmut_r,
                                     h = turn.conmut_d,
                                     normal = turn.axis_d,
                                     ch = 0, pos = turn.pos_o)
shp_brush_l = shp_brush_l.cut(shp_cyl_conmut)

shp_brush_r = fcfun.shp_box_dir_xtr(box_w = 2*turn.conmut_r,
                              box_d = turn.conmut_d,
                              box_h = turn.conmut_sep*0.9,
                              fc_axis_h = VZ,
                              fc_axis_d = VY,
                              fc_axis_w = VX,
                              cw= 0, cd=0, ch=1,
                              xtr_h = 0, xtr_nh = 0,
                              xtr_d = 0, xtr_nd = 0,
                              xtr_w = 0, xtr_nw = 0,
                              pos = turn.pos_o)
                              
shp_brush_r = shp_brush_r.cut(shp_cyl_conmut)

doc = FreeCAD.newDocument()

fco_cable = fcfun.add_fcobj(turn.shp_cable, "espira", doc)
fco_cable.ViewObject.ShapeColor = fcfun.YELLOW_05
fco_cable.ViewObject.LineWidth = 1
fco_conmut_l = fcfun.add_fcobj(turn.shp_conmut_l, "conmut1", doc)
fco_conmut_l.ViewObject.ShapeColor = fcfun.CIAN
fco_conmut_l.ViewObject.LineWidth = 1
fco_conmut_r = fcfun.add_fcobj(turn.shp_conmut_r, "conmut2", doc)
fco_conmut_r.ViewObject.ShapeColor = fcfun.RED
fco_conmut_r.ViewObject.LineWidth = 1
fco_brush_l = fcfun.add_fcobj(shp_brush_l, "escobilla1", doc)
fco_brush_l.ViewObject.ShapeColor = fcfun.ORANGE
fco_brush_l.ViewObject.LineWidth = 1
fco_brush_r = fcfun.add_fcobj(shp_brush_r, "escobilla2", doc)
fco_brush_r.ViewObject.ShapeColor = fcfun.GREEN
fco_brush_r.ViewObject.LineWidth = 1

#fcfun.RotateView(1,0,0,20)


axisX = 1
axisY = 0
axisZ = 0
angle = 20

Gui.ActiveDocument.ActiveView.viewFront()

import math
from pivy import coin
cam = Gui.ActiveDocument.ActiveView.getCameraNode()
rot = coin.SbRotation()
rot.setValue(coin.SbVec3f(axisX,axisY,axisZ),math.radians(angle))
nrot = cam.orientation.getValue() * rot
cam.orientation = nrot
print axisX," ",axisY," ",axisZ," ",angle


