# ----------------------------------------------------------------------------
# -- Linear filter with vertical adjustment
# -- comps library
# -- Python classes and functions to make belt tensioner in FreeCAD
# ----------------------------------------------------------------------------
# -- (c) Felipe Machado
# -- Area of Electronics. Rey Juan Carlos University (urjc.es)
# -- November-2016
# ----------------------------------------------------------------------------
# --- LGPL Licence
# ----------------------------------------------------------------------------

import FreeCAD;
import Part;
import Draft;


import os
# can be taken away after debugging
# directory this file is
filepath = os.getcwd()
import sys
# to get the components
# In FreeCAD can be added: Preferences->General->Macro->Macro path
sys.path.append(filepath)



import kcomp  # import material constants and other constants
import fcfun      # import my functions for freecad

#
#
#               _________________________
#                                        |
#                                        |
#                                        | H(z)
#                                        |
#                                        |
#               _________________________|
#              /  __________________    /
#             /  /                     /  
#            /  /________________     /   D (y)
#           /________________________/
#           |________________________|
#
#                      L (x)
#
#           ________________________________  __________________ 
#          |                                |      |  |        + RAIL_SUP_D
#          |                                |      + FILT_TO_RAIL
#          |________________________________|      |  |________|
#          |                                |      |  |
#          |    ________________________    | ______  |
#          |   |  ____________________  |   | ___  |  |
#          |   | |                    | |   |  |   |  |
#          |   | |                    | |   |  + FILT_SUP_D
#          |   | |                    | |   |  |   + FILT_D_TOL
#          |   | |____________________| |   | _|_  |  |
#          |   |________________________|   | _____|  + FILT_BASE_D
#          |                                |         |
#          |________________________________| ________|
#
#                |----- FILT_SUP_L ---|
#              |------- FILT_L_TOL -----|
#          |---------- FILT_BASE_L ---------|
#
#           ________________________________ ______________
#          |                                |             |
#          |                                |             + RAIL_SUP_H
#          |                                |             |
#          |                                |             |
#          |                                |             |
#          |________________________________| _________   |
#          |   :........................:   | ___+ FILT_H_HOLE
#          |     :                    :     |         + FILT_BASE_H 
#          |_____:____________________:_____| ________|___|

from fcfun import V0, VX, VY, VZ, V0ROT, addBox, addCyl, fillet_len
from fcfun import addBolt, addBoltNut_hole, NutHole
from kcomp import TOL

# Filter dimensions
# http://www.deltaopticalthinfilm.com/product/lv-vis-bandpass-filter-b/
FILT_L = 60.
FILT_D = 25.
FILT_H = 2.5
TOLFILT = 0.4
TOLFILT_L = 0.6
TOLFILT_D = 0.5

FILT_L_TOL = 60. + TOLFILT_L
FILT_D_TOL = 25. + TOLFILT_D
FILT_H_HOLE = 1.5

# Reduction to support the filter
FILT_REDU= 4.

FILT_SUP_L = FILT_L - FILT_REDU
FILT_SUP_D = FILT_D - FILT_REDU

FILT_BASE_L = 76.
FILT_TO_END = (FILT_BASE_L - FILT_L)/2.

# Distance from the begining of the filter to the rail
FILT_TO_RAIL = 21.

FILT_BASE_D = FILT_TO_RAIL + FILT_D_TOL + FILT_TO_END
FILT_BASE_H = 3.5

# The support dimensions
RAIL_SUP_D = 15.5
RAIL_SUP_H = 36.

# The bolts to attach the filter holder to the rail

BOLT_POS_Z = 19.5 # Last check
BOLT_SEP_X = 25.

# ON THE SUPPORT SIDE ATTACHED TO THE RAIL

# bolt shank 
#
#        |--|  BOLT_SHANK_THICK: bolt shank thickness, the rest if for the head
#        |   ___
#        |__|
#         __
#        |  |___
#

#BOLT_SHANK_THICK = RAIL_SUP_D - (kcomp.M4_HEAD_L + 3)
BOLT_SHANK_THICK = 4


RAIL_W = BOLT_SEP_X - 2*kcomp.M4_HEAD_R_TOL - 5
RAIL_H = RAIL_SUP_D - 3
RAIL_WS = RAIL_W * 0.5

RAIL_BLOCK_L = 15.
# relative position of the hole for the leadscrew
HOLERAIL_RELPOS_Z = 0.4
# the part on top that holds the leadscrew
HOLD_SCREW_TOP_H = 3

doc = FreeCAD.newDocument()

shp_filter_base = fcfun.shp_boxcenfill(
                                   x=FILT_BASE_L,
                                   y=FILT_BASE_D-RAIL_SUP_D,
                                   z=FILT_BASE_H,
                                   fillrad = 2,
                                   fx=0, fy=0, fz=1,
                                   cx=1, cy=0, cz=0,
                                   pos=FreeCAD.Vector(0,RAIL_SUP_D,0))

# the hole where the filter will be
filter_hole_pos = FreeCAD.Vector(0,FILT_TO_RAIL-TOLFILT_D/2.,
                                   FILT_BASE_H-FILT_H_HOLE)
shp_filter_hole = fcfun.shp_boxcen(
                                   x=FILT_L_TOL,
                                   y=FILT_D_TOL,
                                   z=FILT_H_HOLE + 1,
                                   cx=1, cy=0, cz=0,
                                   pos=filter_hole_pos)

# The filter through hole

filter_thrhole_pos = FreeCAD.Vector(0,FILT_TO_RAIL+FILT_REDU/2.-TOLFILT_D/2.,-1)
shp_filter_thrhole = fcfun.shp_boxcen(
                                      x=FILT_SUP_L,
                                      y=FILT_SUP_D,
                                      z=FILT_BASE_H + 1,
                                      cx=1, cy=0, cz=0,
                                      pos=filter_thrhole_pos)

shp_filter_holes = shp_filter_hole.fuse(shp_filter_thrhole)
shp_filter_basehole = shp_filter_base.cut(shp_filter_holes)


# the support part, that is fixed on the rail
shp_sup_box = fcfun.shp_boxcen(
                    x=FILT_BASE_L,
                    # Tolerance to avoid being too close to the moving part
                    y=RAIL_SUP_D-kcomp.TOL, 
                    z=RAIL_SUP_H,
                    cx=1, cy=0, cz=0,
                    pos=V0)


# Support bolts
bolt_pos0 = FreeCAD.Vector(-BOLT_SEP_X/2., -1, BOLT_POS_Z)
shp_bolt0 = fcfun.shp_cyl(r=kcomp.M4_SHANK_R_TOL, h=RAIL_SUP_D+1, 
                       normal = VY, pos=bolt_pos0)
bolt_pos1 = FreeCAD.Vector(BOLT_SEP_X/2., -1, BOLT_POS_Z)
shp_bolt1 = fcfun.shp_cyl(r=kcomp.M4_SHANK_R_TOL, h=RAIL_SUP_D+1, 
                       normal = VY, pos=bolt_pos1)
# Support bolt heads
bolth_pos0 = FreeCAD.Vector(-BOLT_SEP_X/2., BOLT_SHANK_THICK, BOLT_POS_Z)
shp_bolth0 = fcfun.shp_cyl(r=kcomp.M4_HEAD_R_TOL+0.5,
                           h=RAIL_SUP_D-BOLT_SHANK_THICK+1, 
                           normal = VY, pos=bolth_pos0)
bolth_pos1 = FreeCAD.Vector(BOLT_SEP_X/2., BOLT_SHANK_THICK, BOLT_POS_Z)
shp_bolth1 = fcfun.shp_cyl(r=kcomp.M4_HEAD_R_TOL+0.5,
                           h=RAIL_SUP_D-BOLT_SHANK_THICK+1, 
                           normal = VY, pos=bolth_pos1)

shp_tbolt0 = shp_bolt0.fuse(shp_bolth0)
shp_tbolt1 = shp_bolt1.fuse(shp_bolth1)
shp_bolts = shp_tbolt0.fuse(shp_tbolt1)

# Fixed part of support

#shp_fixsup_base = fcfun.shp_boxcen(
#                               x=FILT_BASE_L,
#                               y=RAIL_SUP_D - 4,
#                               z=RAIL_SUP_H,
#                               cx=1, cy=0, cz=0,
#                               pos=V0)

#Part.show(shp_fixsup_base)

#
#          |   |
#         /     \
#        |       |
#        |_______|
#
#
#

rail_pos_y = RAIL_SUP_D-RAIL_H # + 1 # +1 to have overlap
# position of the hole for the leadscrew
leadscrewhole_pos_y = rail_pos_y + HOLERAIL_RELPOS_Z * RAIL_H 

side_rail_pos_x = (   BOLT_SEP_X + kcomp.M4_HEAD_R_TOL + 0.5
                 + (FILT_BASE_L - BOLT_SEP_X - 2*kcomp.M4_HEAD_R_TOL -1)/2.)/2.

shp_leadscrewhole = fcfun.shp_cyl(kcomp.M3_SHANK_R_TOL, HOLD_SCREW_TOP_H+2, VZ, 
                       pos = FreeCAD.Vector(0,leadscrewhole_pos_y, 
                             RAIL_SUP_H-HOLD_SCREW_TOP_H-1))

shp_leadscrewhole1 = shp_leadscrewhole.copy()
shp_leadscrewhole1.Placement.Base.x = side_rail_pos_x
shp_leadscrewhole0 = shp_leadscrewhole.copy()
shp_leadscrewhole0.Placement.Base.x = -side_rail_pos_x

# a Hole to see nut below
shp_holesee = fcfun.shp_boxcen (x = kcomp.M3_2APOT_TOL,
                                y = rail_pos_y + 2,
                                z = RAIL_SUP_H * 0.75,
                                #fillrad = kcomp.M3_2APOT_TOL * 0.4,
                                #fx=1, fy=0, fz=0,
                                cx=1, cy=0, cz=0,
                                pos = FreeCAD.Vector(0,-1, RAIL_SUP_H * 0.125))

shp_holesee1 = shp_holesee.copy()
shp_holesee1.Placement.Base.x = side_rail_pos_x
shp_holesee0 = shp_holesee.copy()
shp_holesee0.Placement.Base.x = -side_rail_pos_x


shp_facerail = fcfun.shp_face_rail(rail_w = RAIL_W,
                                    rail_ws = RAIL_WS,
                                    rail_h = RAIL_H,
                                    rail_h_plus = 2,
                                    offs_w = 0,
                                    offs_h = 0,
                                    axis_l = 'z',
                                    axis_b = '-y',
                                    hole_d = 2*kcomp.M3_SHANK_R_TOL,
                                    hole_relpos_z = HOLERAIL_RELPOS_Z )


shp_facerail.Placement.Base = FreeCAD.Vector(0,rail_pos_y,0)

shp_rail = shp_facerail.extrude(FreeCAD.Vector(0,0,RAIL_BLOCK_L))

# Adding the hole for the nut

h_nuthole = fcfun.NutHole (
                        nut_r = kcomp.M3_NUT_R_TOL,
                        nut_h = kcomp.M3NUT_HOLE_H,
                        hole_h = leadscrewhole_pos_y + TOL,
                        name   = "nuthole",
                        extra  = 1,
                        # the height of the nut on the X axis
                        nuthole_x = 0,
                        cx = 1, # not centered on x
                        cy = 0, # centered on y, on the center of the hexagon
                        holedown = 0)

doc.recompute()

nuthole = h_nuthole.fco

nuthole.Placement.Rotation = FreeCAD.Rotation (VX,90)
nuthole.Placement.Base.z = (RAIL_BLOCK_L - kcomp.M3NUT_HOLE_H)/2.
nuthole.Placement.Base.y = leadscrewhole_pos_y + TOL 

rail = doc.addObject("Part::Feature","block")
rail.Shape = shp_rail

railnuth = doc.addObject("Part::Cut", "blocknut")
railnuth.Base = rail
railnuth.Tool = nuthole

railnuth0 = Draft.clone(railnuth)
railnuth0.Label = 'blocknut0'
railnuth0.Placement.Base.x= -side_rail_pos_x

railnuth1 = Draft.clone(railnuth)
railnuth1.Label = 'blocknut1'
railnuth1.Placement.Base.x= side_rail_pos_x

filter_basehole = doc.addObject("Part::Feature", 'filter_basehole')
filter_basehole.Shape = shp_filter_basehole

filter_mov = doc.addObject("Part::MultiFuse", 'filtermov')
filter_mov.Shapes = [filter_basehole,railnuth, railnuth0, railnuth1]

# chamfer of the union between the base and the rails

doc.recompute()
doc.recompute()

filter_mov_cmf = fcfun.filletchamfer (fco = filter_mov,
                                      e_len = RAIL_WS,
                                      name = 'filtermovchmf',
                                      fillet = 0, #chamfer
                                      radius = 2., 
                                      axis = 'x', 
                                      zpos_chk = 1, 
                                      zpos = FILT_BASE_H )





shp_face_railhole = fcfun.shp_face_rail(rail_w = RAIL_W, 
                                         rail_ws = RAIL_WS,
                                         rail_h = RAIL_H,
                                         rail_h_plus = 2.,
                                         offs_w = TOL/2.,
                                         offs_h = TOL/2.,
                                         axis_l = 'z',
                                         axis_b = '-y',
                                         hole_d = 0,
                                         hole_relpos_z = 0)


doc.recompute()

shp_face_railhole.Placement.Base = FreeCAD.Vector(0,rail_pos_y,0)

shp_railhole = shp_face_railhole.extrude(
               FreeCAD.Vector(0,0,RAIL_SUP_H-HOLD_SCREW_TOP_H))

shp_railhole1 = shp_railhole.copy()
shp_railhole1.Placement.Base.x = side_rail_pos_x

shp_railhole0 = shp_railhole.copy()
shp_railhole0.Placement.Base.x = -side_rail_pos_x
                            

#shp_filthold_mov = shp_filter_basehole.multiFuse(
                  #[shp_railnuth,shp_railnuth1, shp_railnuth0])
#Part.show(shp_filthold_mov)

shp_fix_holes = shp_bolts.multiFuse([shp_railhole,
                                     shp_railhole1,
                                     shp_railhole0,
                                     shp_leadscrewhole,
                                     shp_leadscrewhole0,
                                     shp_leadscrewhole1,
                                     shp_holesee,
                                     shp_holesee0,
                                     shp_holesee1,
]                                   )


shp_fix_support = shp_sup_box.cut(shp_fix_holes)

fix_support = doc.addObject("Part::Feature", 'fix_support')
fix_support.Shape = shp_fix_support

doc.recompute()


