# ----------------------------------------------------------------------------
# -- Examples of tensioners with different wall thickness
# ----------------------------------------------------------------------------
# -- (c) Felipe Machado
# -- Area of Electronic Technology. Rey Juan Carlos University (urjc.es)
# -- https://github.com/felipe-m/freecad_filter_stage
# -- January-2018
# ----------------------------------------------------------------------------
# --- LGPL Licence
# ----------------------------------------------------------------------------

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

aluprof_w1 = 10

doc = FreeCAD.newDocument()
t_set1 = tensioner_clss.TensionerSet(
                     aluprof_w = aluprof_w1,
                     #belt_pos_h = 32.5, #bottom of belt:30 + 2.5 to center
                     #belt_pos_h = 37.5, #bottom of belt:35 + 2.5 to center
                     #belt_pos_h = 47.5, #bottom of belt:45 + 2.5 to center
                     belt_pos_h = 20., # to center of belt
                     hold_bas_h = 0,
                     hold_hole_2sides = 1,
                     boltidler_mtr = 3,
                     bolttens_mtr = 3,
                     boltaluprof_mtr = 3,
                     tens_stroke = 12. ,
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
                     pos = FreeCAD.Vector(0,0,0),
                     name = 'tensioner_set_1')

# get the set, and the the part
t_set1.get_idler_tensioner().get_idler_tensioner().set_color(fcfun.ORANGE)
t_set1.get_tensioner_holder().set_color(fcfun.LSKYBLUE)


# position of the aluminum profile that supports the tensioner
# point at the base, at the end along axis w, centered along axis_d (bolts)
aluprof_tens1_pos = t_set1.get_pos_dwh (2,-4,0)
aluprof_tens1_l = t_set1.get_tensioner_holder().hold_bas_w

aluprof1_dict = kcomp.ALU_PROF[aluprof_w1]
aluprof_tens1 = comps.PartAluProf(depth = aluprof_tens1_l,
                                 aluprof_dict = aluprof1_dict,
                                 xtr_d = 0,
                                 #xtr_nd = aluprof_tens_l/2., # extra length
                                 xtr_nd = 0,
                                 axis_d = VYN,
                                 axis_w = VX,
                                 axis_h = VZ,
                                 pos_d = 1, #end not counting xtr_nd
                                 pos_w = 0, # centered
                                 pos_h = 3,
                                 pos = aluprof_tens1_pos)


# Bolts for the belt tensioner
max_tens1_bolt_l = (
                  aluprof_tens1.get_h_ab(3,1).Length # spacefor bolt inprofile
                + t_set1.get_tensioner_holder().hold_bas_h) # base thickness
for w_i in [-3, 3]: # position of bolts
    tens1_bolt_i_pos = t_set1.get_pos_dwh(2,w_i,1)
    tens1_bolt_i = partset.Din912BoltWashSet(
                                         metric  = 3,
                                         shank_l = max_tens1_bolt_l,
                                         # smaller considering the washer
                                         shank_l_adjust = -2,
                                         axis_h  = axis_up.negative(),
                                         pos_h   = 3,
                                         pos_d   = 0,
                                         pos_w   = 0,
                                         pos     = tens1_bolt_i_pos)


aluprof_w2 = 15
t_set2 = tensioner_clss.TensionerSet(
                     aluprof_w = aluprof_w2,
                     #belt_pos_h = 32.5, #bottom of belt:30 + 2.5 to center
                     #belt_pos_h = 37.5, #bottom of belt:35 + 2.5 to center
                     #belt_pos_h = 47.5, #bottom of belt:45 + 2.5 to center
                     belt_pos_h = 20., # to center of belt
                     hold_bas_h = 0,
                     hold_hole_2sides = 1,
                     boltidler_mtr = 3,
                     bolttens_mtr = 3,
                     boltaluprof_mtr = 3,
                     tens_stroke = 12. ,
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
                     pos = FreeCAD.Vector(50,0,0),
                     name = 'tensioner_set_2')

# get the set, and the the part
t_set2.get_idler_tensioner().get_idler_tensioner().set_color(fcfun.ORANGE)
t_set2.get_tensioner_holder().set_color(fcfun.LSKYBLUE)

# position of the aluminum profile that supports the tensioner
# point at the base, at the end along axis w, centered along axis_d (bolts)
aluprof_tens2_pos = t_set2.get_pos_dwh (2,-4,0)

aluprof_tens2_l = t_set2.get_tensioner_holder().hold_bas_w

aluprof2_dict = kcomp.ALU_PROF[aluprof_w2]
aluprof_tens2 = comps.PartAluProf(depth = aluprof_tens2_l,
                                 aluprof_dict = aluprof2_dict,
                                 xtr_d = 0,
                                 #xtr_nd = aluprof_tens_l/2., # extra length
                                 xtr_nd = 0,
                                 axis_d = VYN,
                                 axis_w = VX,
                                 axis_h = VZ,
                                 pos_d = 1, #end not counting xtr_nd
                                 pos_w = 0, # centered
                                 pos_h = 3,
                                 pos = aluprof_tens2_pos)

# Bolts for the belt tensioner
max_tens2_bolt_l = (
                  aluprof_tens2.get_h_ab(3,1).Length # spacefor bolt inprofile
                + t_set2.get_tensioner_holder().hold_bas_h) # base thickness
for w_i in [-3, 3]: # position of bolts
    tens2_bolt_i_pos = t_set2.get_pos_dwh(2,w_i,1)
    tens2_bolt_i = partset.Din912BoltWashSet(
                                         metric  = 3,
                                         shank_l = max_tens2_bolt_l,
                                         # smaller considering the washer
                                         shank_l_adjust = -2,
                                         axis_h  = axis_up.negative(),
                                         pos_h   = 3,
                                         pos_d   = 0,
                                         pos_w   = 0,
                                         pos     = tens2_bolt_i_pos)



aluprof_w3 = 20
t_set3 = tensioner_clss.TensionerSet(
                     aluprof_w = aluprof_w3,
                     #belt_pos_h = 32.5, #bottom of belt:30 + 2.5 to center
                     #belt_pos_h = 37.5, #bottom of belt:35 + 2.5 to center
                     #belt_pos_h = 47.5, #bottom of belt:45 + 2.5 to center
                     belt_pos_h = 20., # to center of belt
                     hold_bas_h = 0,
                     hold_hole_2sides = 1,
                     boltidler_mtr = 3,
                     bolttens_mtr = 3,
                     boltaluprof_mtr = 3,
                     tens_stroke = 12. ,
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
                     pos = FreeCAD.Vector(100,0,0),
                     name = 'tensioner_set_3')

# get the set, and the the part
t_set3.get_idler_tensioner().get_idler_tensioner().set_color(fcfun.ORANGE)
t_set3.get_tensioner_holder().set_color(fcfun.LSKYBLUE)


# position of the aluminum profile that supports the tensioner
# point at the base, at the end along axis w, centered along axis_d (bolts)
aluprof_tens3_pos = t_set3.get_pos_dwh (2,-4,0)
aluprof_tens3_l = t_set3.get_tensioner_holder().hold_bas_w

aluprof3_dict = kcomp.ALU_PROF[aluprof_w3]
aluprof_tens3 = comps.PartAluProf(depth = aluprof_tens3_l,
                                 aluprof_dict = aluprof3_dict,
                                 xtr_d = 0,
                                 #xtr_nd = aluprof_tens_l/2., # extra length
                                 xtr_nd = 0,
                                 axis_d = VYN,
                                 axis_w = VX,
                                 axis_h = VZ,
                                 pos_d = 1, #end not counting xtr_nd
                                 pos_w = 0, # centered
                                 pos_h = 3,
                                 pos = aluprof_tens3_pos)

# Bolts for the belt tensioner
max_tens3_bolt_l = (
                  aluprof_tens3.get_h_ab(3,1).Length # spacefor bolt inprofile
                + t_set3.get_tensioner_holder().hold_bas_h) # base thickness
for w_i in [-3, 3]: # position of bolts
    tens3_bolt_i_pos = t_set3.get_pos_dwh(2,w_i,1)
    tens3_bolt_i = partset.Din912BoltWashSet(
                                         metric  = 3,
                                         shank_l = max_tens3_bolt_l,
                                         # smaller considering the washer
                                         shank_l_adjust = -2,
                                         axis_h  = axis_up.negative(),
                                         pos_h   = 3,
                                         pos_d   = 0,
                                         pos_w   = 0,
                                         pos     = tens3_bolt_i_pos)

