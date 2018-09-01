# ----------------------------------------------------------------------------
# -- Examples of different paramenters: different stroke
# ----------------------------------------------------------------------------
# -- (c) Felipe Machado
# -- Area of Electronic Technology. Rey Juan Carlos University (urjc.es)
# -- https://github.com/felipe-m/freecad_filter_stage
# -- January-2018
# ----------------------------------------------------------------------------
# --- LGPL Licence
# ----------------------------------------------------------------------------


#                           axis_h            axis_h 
#                            :                  :
# ....................... ___:___               :______________
# :                      |  ___  |     pos_h:   |  __________  |---
# :                      | |   | |        3     | |__________| | : |
# :+hold_h              /| |___| |\       1,2   |________      |---
# :                    / |_______| \            |        |    /      
# :             . ____/  |       |  \____       |________|  /
# :..hold_bas_h:.|_::____|_______|____::_|0     |___::___|/......axis_d
#                                               0    1           2: pos_d
#
#
#
#                 .... hold_bas_w ........
#                :        .hold_w.        :
#              aluprof_w :    wall_thick  :
#                :..+....:      +         :
#                :       :     : :        :
#       pos_w:   2__1____:___0_:_:________:........axis_w
#                |    |  | :   : |  |     |    :
#                |  O |  | :   : |  |  O  |    + hold_bas_d
#                |____|__| :   : |__|_____|....:
#                        | :   : |
#                        |_:___:_|
#                          |   |
#                           \_/
#                            :
#                            :
#                           axis_d
#
# min_width = 1 Mininum width
#
#                 .... hold_bas_w ........
#                :        .hold_w.        :
#             washer diam:    wall_thick  :
#                :..+....:      +         :
#                :       :     : :        :
#       pos_w:   2__1____:___0_:_:________:........axis_w
#                |    |  | :   : |  |     |    :
#                |  O |  | :   : |  |  O  |    + hold_bas_d
#                |____|__| :   : |__|_____|....:
#                        | :   : |
#                        |_:___:_|
#                          |   |
#                           \_/
#                            :
#                            :
#                           axis_d


# the tensioner set is referenced on 3 perpendicular axis:
# - axis_d: depth
# - axis_w: width
# - axis_h: height
# There is a position of the piece:
# - that can be in a different point

import os
import sys
import inspect
import logging
import math
import FreeCAD
import FreeCADGui
import Part
import DraftVecUtils

# to get the current directory. Freecad has to be executed from the same
# directory this file is
filepath = os.getcwd()
# to get the components
# In FreeCAD can be added: Preferences->General->Macro->Macro path
sys.path.append(filepath) 
#sys.path.append(filepath + '/' + 'comps')
sys.path.append(filepath + '/../../' + 'comps')

# path to save the FreeCAD files
fcad_path = filepath + '/../freecad/'

# path to save the STL files
stl_path = filepath + '/../stl/'

import kcomp   # import material constants and other constants
import fcfun   # import my functions for freecad. FreeCad Functions
import shp_clss # import my TopoShapes classes 
import fc_clss # import my freecad classes 
import comps   # import my CAD components
import partset
import tensioner_clss

from fcfun import V0, VX, VY, VZ, V0ROT
from fcfun import VXN, VYN, VZN


doc = FreeCAD.newDocument()
t_set1 = tensioner_clss.TensionerSet(
                     aluprof_w = 20.,
                     #belt_pos_h = 32.5, #bottom of belt:30 + 2.5 to center
                     #belt_pos_h = 37.5, #bottom of belt:35 + 2.5 to center
                     #belt_pos_h = 47.5, #bottom of belt:45 + 2.5 to center
                     belt_pos_h = 20., # to center of belt
                     hold_bas_h = 0,
                     hold_hole_2sides = 1,
                     boltidler_mtr = 3,
                     bolttens_mtr = 3,
                     boltaluprof_mtr = 3,
                     tens_stroke = 10. ,
                     wall_thick = 3.,
                     in_fillet = 2.,
                     pulley_stroke_dist = 0,
                     nut_holder_thick = 3. ,
                     opt_tens_chmf = 0,
                     min_width = 0,
                     tol = kcomp.TOL,
                     axis_d = VX,
                     axis_w = VYN,
                     axis_h = VZ,
                     pos_d = 0,
                     pos_w = 0,
                     pos_h = 0,
                     #pos = FreeCAD.Vector(1,0,10),
                     pos = FreeCAD.Vector(0,0,0),
                     name = 'tensioner_set')

# get the set, and the the part
t_set1.get_idler_tensioner().get_idler_tensioner().set_color(fcfun.ORANGE)
t_set1.get_tensioner_holder().set_color(fcfun.LSKYBLUE)


t_set2 = tensioner_clss.TensionerSet(
                     aluprof_w = 20.,
                     #belt_pos_h = 32.5, #bottom of belt:30 + 2.5 to center
                     #belt_pos_h = 37.5, #bottom of belt:35 + 2.5 to center
                     #belt_pos_h = 47.5, #bottom of belt:45 + 2.5 to center
                     belt_pos_h = 20., # to center of belt
                     hold_bas_h = 0,
                     hold_hole_2sides = 1,
                     boltidler_mtr = 3,
                     bolttens_mtr = 3,
                     boltaluprof_mtr = 3,
                     tens_stroke = 20. ,
                     wall_thick = 3.,
                     in_fillet = 2.,
                     pulley_stroke_dist = 0,
                     nut_holder_thick = 3. ,
                     opt_tens_chmf = 0,
                     min_width = 0,
                     tol = kcomp.TOL,
                     axis_d = VX,
                     axis_w = VYN,
                     axis_h = VZ,
                     pos_d = 0,
                     pos_w = 0,
                     pos_h = 0,
                     pos = FreeCAD.Vector(
                           t_set1.get_idler_tensioner().tens_d + 10,0,0),
                     name = 'tensioner_set_stroke20')

# get the set, and the the part
t_set2.get_idler_tensioner().get_idler_tensioner().set_color(fcfun.ORANGE)
t_set2.get_tensioner_holder().set_color(fcfun.LSKYBLUE)
#t_set2.set_pos_tensioner(1)


# --------- 


t_set3 = tensioner_clss.TensionerSet(
                     #belt_pos_h = 32.5, #bottom of belt:30 + 2.5 to center
                     #belt_pos_h = 37.5, #bottom of belt:35 + 2.5 to center
                     #belt_pos_h = 47.5, #bottom of belt:45 + 2.5 to center
                     belt_pos_h = 20., # to center of belt
                     hold_bas_h = 0,
                     hold_hole_2sides = 1,
                     boltidler_mtr = 3,
                     bolttens_mtr = 3,
                     boltaluprof_mtr = 3,
                     tens_stroke = 30. ,
                     wall_thick = 3.,
                     in_fillet = 2.,
                     pulley_stroke_dist = 0,
                     nut_holder_thick = 3. ,
                     opt_tens_chmf = 0,
                     min_width = 0,
                     tol = kcomp.TOL,
                     axis_d = VX,
                     axis_w = VYN,
                     axis_h = VZ,
                     pos_d = 0,
                     pos_w = 0,
                     pos_h = 0,
                     pos = FreeCAD.Vector(
                               t_set1.get_idler_tensioner().tens_d
                               + t_set2.get_idler_tensioner().tens_d + 20
                               ,0,0),
                     name = 'tensioner_set_stroke40')

# get the set, and the the part
t_set3.get_idler_tensioner().get_idler_tensioner().set_color(fcfun.ORANGE)
t_set3.get_tensioner_holder().set_color(fcfun.LSKYBLUE)



