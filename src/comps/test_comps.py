# ----------------------------------------------------------------------------
# -- Test Components
# -- Test classes and functions of comps
# ----------------------------------------------------------------------------
# -- (c) Felipe Machado
# -- Area of Electronics. Rey Juan Carlos University (urjc.es)
# -- October-2016
# ----------------------------------------------------------------------------
# --- LGPL Licence
# ----------------------------------------------------------------------------


# to test the classes and functions of comps
#  execute freecad from the cmd console on the directory
# "C:\Program Files\FreeCAD 0.16\bin\freecad" test_comps.py

# to excute from command line in windows:
# "C:\Program Files\FreeCAD 0.16\bin\freecadcmd" test_comps.py

import os
import sys
import FreeCAD;
import FreeCADGui;
import Part;
import Draft;
import logging  # to avoid using print statements
#import copy;
#import Mesh;


# to get the current directory. Freecad has to be executed from the same
# directory this file is
filepath = os.getcwd()

# to get the components
# In FreeCAD can be added: Preferences->General->Macro->Macro path
sys.path.append(filepath) 

import fcfun   # import my functions for freecad. FreeCad Functions
import kcomp   # import material constants and other constants
import comps   # import my CAD components

from fcfun import V0, VX, VY, VZ, V0ROT, addBox, addCyl, fillet_len
from fcfun import addBolt, addBoltNut_hole, NutHole
from kcomp import TOL


logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)s - %(message)s')

doc = FreeCAD.newDocument()

"""

# Aluminum profiles for the citometer base

#  ------------- X alum profiles
# fb: front (y=0) bottom (z=0)
"""
h_alu_x_fb = comps.MisumiAlu30s6w8 (40,
                                  "alu_x_fb", axis= 'x', cx=1, cy=1, cz=0)
alu_x_fb = h_alu_x_fb.fco # the FreeCad Object

# bb: back (y=0) bottom (z=0)
alu_x_bb = Draft.clone(alu_x_fb)
alu_x_bb.Label = "alu_x_bb"
alu_x_bb.Placement.Base = ( FreeCAD.Vector ( 0, 50,0)) 

# ------------------ Shaft holders SK12 ------------------------------
# f= f; r: right. hole_x = 0 -> hole facing Y axis
h_sk12_fr = comps.Sk(size=12, name="sk12_fr", hole_x = 0, cx=1, cy=1)
sk12_fr = h_sk12_fr.fco # the FreeCad Object
# ROD_Y_SEP is the separation of the Y RODs
sk12_fr.Placement.Base = FreeCAD.Vector (20, 15, 30)
# f= front; l: left
sk12_fl = Draft.clone(sk12_fr)
sk12_fl.Label = "sk12_fl"
sk12_fl.Placement.Base = FreeCAD.Vector (-20, 15, 30)
#alu_y_lb.Placement.Base = alu_y_basepos + alu_y_xendpos

#sk12_fl = comps.Sk(size=12, name="sk12_000", hole_x = 0, cx=0, cy=0)
# b= back; l: left
#sk12_bl = comps.Sk(size=12, name="sk12_000", hole_x = 0, cx=0, cy=0)

# the shaft support on the left back

doc = FreeCAD.ActiveDocument

#sk12_000 = comps.Sk(size=12, name="sk12_000", hole_x = 0, cx=0, cy=0)
#sk12_001 = comps.Sk(size=12, name="sk12_001", hole_x = 0,  cx=0, cy=1)
#sk12_100 = comps.Sk(size=12, name="sk12_100", hole_x = 1,  cx=0, cy=0)
#sk12_101 = comps.Sk(size=12, name="sk12_101", hole_x = 1,  cx=0, cy=1)
#sk12_110 = comps.Sk(size=12, name="sk12_110", hole_x = 1,  cx=1, cy=0)
#sk12_111 = comps.Sk(size=12, name="sk12_111", hole_x = 1,  cx=1, cy=1)
#mi_x000 = comps.MisumiAlu30s6w8 (30, "x_000", axis= 'x')
#mi_y000 = comps.MisumiAlu30s6w8 (30, "y_000", axis= 'y')
#mi_z000 = comps.MisumiAlu30s6w8 (30, "z_000", axis= 'z')
#mi_x111 = comps.MisumiAlu30s6w8 (30, "x_111", axis= 'x', cx=1, cy=1, cz=1)
#mi_y111 = comps.MisumiAlu30s6w8 (30, "y_111", axis= 'y', cx=1, cy=1, cz=1)
#mi_z111 = comps.MisumiAlu30s6w8 (30, "z_111", axis= 'z', cx=1, cy=1, cz=1)
#mi_x110 = comps.MisumiAlu30s6w8 (30, "x_110", axis= 'x', cx=1, cy=1, cz=0)
#mi_y101 = comps.MisumiAlu30s6w8 (30, "y_101", axis= 'y', cx=1, cy=0, cz=1)
#mi_z011 = comps.MisumiAlu30s6w8 (30, "z_011", axis= 'z', cx=0, cy=1, cz=1)

doc = FreeCAD.ActiveDocument

# ---- rounded bars
#rectrndbar_z_x_cy = comps.RectRndBar (Base = 20, Height =10, Length = 30,
#                 Radius =2,
#                 Thick = 4, 
#                 inrad_same = True, axis = 'z',
#                 baseaxis = 'x', name = "rectrndbar_z_x_cy",
#                 cx=False, cy=True, cz=False)

#ectrndbar_x_z = comps.RectRndBar (Base = 20, Height =10, Length = 30,
#                 Radius =2,
#                 Thick = 2, 
#                 inrad_same = True, axis = 'x',
#                 baseaxis = 'z', name = "rectrndbar_x_z",
#                 cx=False, cy=False, cz=False)

#ectrndbar_y_x_cxy = comps.RectRndBar (Base = 20, Height =10, Length = 30,
#                 Radius =2,
#                 Thick = 1, 
#                 inrad_same = False, axis = 'y',
#                 baseaxis = 'x', name = "rectrndbar_y_x_cxy",
#                  cx=True, cy=True, cz=False)

#ectrndbar_y_z_cyz = comps.RectRndBar (Base = 20, Height =10, Length = 40,
#                 Radius =0.5,
#                 Thick = 4, 
#                 inrad_same = True, axis = 'y',
#                 baseaxis = 'z', name = "rectrndbar_y_z_cyz",
#                 cx=False, cy=True, cz=True)



# to test T8 Nut and Nut housing
T8 = comps.T8NutHousing (name="T8NutHousing", nutaxis='-x',
                         screwface_axis ='-z', cx=0, cy = 1, cz=1)
nutt8 = comps.T8Nut("nutt8", nutaxis = '-x' )
doc.recompute()

T8moved = comps.T8NutHousing (name="T8NutHousing_desp", nutaxis='x',
                              screwface_axis ='-z', cx=1, cy = 1, cz=1)

T8moved.fco.Placement.Base = fcfun.calc_desp_ncen (
                                            Length = T8moved.Length,
                                            Width = T8moved.Width,
                                            Height = T8moved.Height,
                                            vec1 = (0,0,1),
                                            vec2 = (-1,0,0),
                                            cx=0, cy = 1, cz=0)

T8moved.fco.Placement.Rotation = fcfun.calc_rot (
                                            vec1 = (0,0,1),
                                            vec2 = (-1,0,0))


Gui.ActiveDocument = Gui.getDocument(doc.Label)
guidoc = Gui.getDocument(doc.Label)
Gui.ActiveDocument.ActiveView.setAxisCross(True)

doc.recompute()













