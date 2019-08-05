#  Nema motor holder
#  check in the project for src/comps/parts.py
#  for a more complete version
# ----------------------------------------------------------------------------
# -- (c) Felipe Machado
# -- Area of Electronics Technology. Rey Juan Carlos University (urjc.es)
# -- https://github.com/felipe-m
# -- 2019
# ----------------------------------------------------------------------------
# --- LGPL Licence
# ----------------------------------------------------------------------------

from datetime import datetime
#import time

startdatetime = datetime.now()
#starttime = time.time()

import os
import sys
import FreeCAD
import FreeCADGui
import Part
import Mesh
import MeshPart

# to get the current directory. Freecad has to be executed from the same
# directory this file is
filepath = os.getcwd()
# to get the components
# In FreeCAD can be added: Preferences->General->Macro->Macro path
sys.path.append(filepath) 
#sys.path.append(filepath + '/' + 'comps')
sys.path.append(filepath + '/../../' + 'comps')

import kcomp
import fcfun   # import my functions for freecad. FreeCad Functions
import comps   # import my CAD components
import kidler  # import constants for the idler tensioner and holder
import kparts
import math

#exec(open("nemamotor_bracket_time.py").read())


"""
     Creates a holder for a Nema motor
         __________________
        ||                ||
        || O     __     O ||
        ||    /      \    ||
        ||   |   1    |   ||
        ||    \      /    ||
        || O     __     O ||
        ||________________|| ..... wall_thick
        ||_______2________|| ....................>Y
                                      
                                      
                                      motor_xtr_space_d
                                     :  :
         ________3_________        3_:__:____________ ..............> X
        |  ::  :    :  ::  |       |      :     :    |    + motor_thick
        |__::__:_1__:__::__|       2......:..1..:....|....:
        ||                ||       | :              /
        || ||          || ||       | :           /
        || ||          || ||       | :        /
        || ||          || ||       | :      /
        || ||          || ||       | :   /
        ||________________||       |_: /
        ::       :                 :                 :
         + reinf_thick             :....tot_d........:
                 :
                 :
                 Z


                  motor_hole_r
                 :  :  
               :    :
         ______:____:______ ..................................
        |  ::  :    :  ::  |                                  :
        |__::__:_1__:__::__|....................              :
        ||                ||....+ motor_min_h  :              :
        || ||          || ||                   :              +tot_h
        || ||          || ||                   + motor_max_h  :
        || ||          || ||                   :              :
        || ||          || ||...................:              :
        ||________________||...................:xtr_down......:
        :  :            :  :
        :  :            :  :
        :  :............:  :
        :   bolt_wall_sep  :
        :                  :
        :                  :
        :.....tot_w........:
                         ::
                          motor_xtr_space
"""

# --------------- PARAMETERS (can be changed) -------------------------
## Nema Size, choose the NEMA size of your motor: 8, 11, 14, 17, 23, 34, 42
nema_size = 17 

#  thickness in mm of the side where the holder will be screwed to
wall_thick = 4.

#  thickness in mm of the top side where the motor will be screwed to
motor_thick = 5.

#  thickness of the reinforcement walls
reinf_thick = 4.

#  distance of from the inner top side to the top hole of the bolts to 
#  attach the holder (see drawing)
motor_min_h = 10.

# distance of from the inner top side to the bottom hole of the bolts to 
# attach the holder
motor_max_h = 40.

# extra separation between the motor and the sides
motor_xtr_space = 5.

# extra separation between the motor and the side of the wall
motor_xtr_space_d = 6.

# extra space from the motor_max_h to the end
xtr_down = 5.

# separation of the wall bolts, if 0, it will be the motor width
# has to be smaller than the total width
bolt_wall_sep = 0

# metric of the bolts to attach the holder (diameter of the shank in mm)
bolt_wall_d = 4.

# radius of the chamfer
chmf_r = 2.

# motor hole radius: the hole for the motor circle that is with the axis
# if 0, will take the half of the distance of the bolts
motor_hole_r = 0

# tolerances: 0.4 or 0.3 mm
TOL = 0.3
STOL = TOL / 2.  #smaller tolerance

# ----- DO NOT CHANGE ANYTHING UNDER THIS LINE UNLESS YOU KNOW WHAT YOU 
# ---             ARE DOING


# width of the motor (both dimensions: it is a square) in mm
NEMA_W  = {
             8:   20.2,
             11:  28.2,
             14:  35.2,
             17:  42.3,
             23:  56.4,
             34:  86.0,
             42: 110.0 }

# Separation of the bolt holes of the motor  
NEMA_BOLT_SEP  = {
             8:   16.0,
             11:  23.0,
             14:  26.0,
             17:  31.0,
             23:  47.1,
             34:  69.6,
             42:  89.0 }

# motor bolt holes diameter
# check datasheet, dimensions may vary
NEMA_BOLT_D  = {
              8:   2.0,  # M2
             11:   2.5,  # M2.5
             14:   3.0,  # M3
             17:   3.0,  # M3
             23:   5.0,
             34:   5.0,
             42:   8.0 }

# width of the motor
motor_w = NEMA_W[nema_size]
# separation of the motor bolts
motor_bolt_sep = NEMA_BOLT_SEP[nema_size]
# diameter of these bolts
motor_bolt_d = NEMA_BOLT_D[nema_size]
# radius of the motor bolts including tolerances
motor_bolt_r_tol = motor_bolt_d/2. + STOL

# radius of the wall bolts including tolerances
bolt_wall_r_tol = bolt_wall_d/2. + STOL

# if not defined:
if motor_hole_r == 0:
    motor_hole_r = motor_bolt_sep/2.

# if not defined:
if bolt_wall_sep == 0:
    bolt_wall_sep = motor_w

# total width: the reinforcement + motor width + xtr_space
tot_w = 2* reinf_thick + motor_w + 2 * motor_xtr_space

# total height:
tot_h = motor_thick + motor_max_h + xtr_down

# total depth:
tot_d = wall_thick + motor_w + motor_xtr_space_d

def nemamotor_holder ():



    #  --------------- step 01 ---------------------------      
    #  rectangular cuboid with basic dimensions
    # 
    #                    Z
    #                    :
    #                    :
    #             :.....tot_w.......
    #             :______:__________:
    #             /                /|
    #            /                / |
    #           /                /  |
    #          /                /   |
    #       ../________________/    |
    #       : |                |    | 
    #       : |                |    |...............Y
    #       : |                |   /     . 
    #  tot_h: |                |  /     . tot_d
    #       : |                | /     . 
    #       :.|________________|/......
    #                .
    #               .
    #              X 
    #

    # creates the shape, you don't see it yet on FreeCAD Gui
    # centered along axis Y
    shp01 = fcfun.shp_boxcen(tot_d, tot_w, tot_h, cy = True)
    # creates a freecad object from the shape, to see it in FreeCAD Gui,
    # not necessary, but illustrative for this tutorial
    fcd01 = fcfun.add_fcobj(shp01, 'box01')


    #  --------------- step 02 ---------------------------      
    #  chamfering the 4 vertical edges (marked with H)
    # 
    #                    Z
    #                    :
    #                    :
    #             :.....tot_w.......
    #             :______:__________:
    #             /                /H chamfering
    #            /                / H
    #           /                /  H
    #          /                /   H
    #       ../________________/    H
    #       : H                H    H 
    #       : H                H    H...............Y
    #       : H                H   /     . 
    #  tot_h: H                H  /     . tot_d
    #       : H                H /     . 
    #       :.H________________H/......
    #                .
    #               .
    #              X 
    #

    fcd02 = fcfun.filletchamfer (fcd01, e_len = tot_h,
                                 name = 'step02',
                                 fillet = 0,
                                 radius = chmf_r,
                                 axis = 'z'  # axis to fillet
                                )

    #  --------------- step 03 ---------------------------      
    #  Horizontal chamfering the top edge to make a 'triangular' reinforcement
    # 
    #      Z
    #      :
    #      :___            . chmf_pos
    #      |    \
    #      |      \
    #      |        \
    #      |          \
    #      |            \
    #      |              \
    #      |________________.....X
    # 
    #
    # the radius is the smaller part
    chmf_reinf_r = min(tot_d - wall_thick, tot_h-motor_thick)

    fcd03 = fcfun.filletchamfer (fcd02, e_len = 0,
                                 name = 'step03',
                                 fillet = 0,
                                 radius = chmf_reinf_r,
                                 axis = 'y',  # axis to fillet
                                 xpos_chk = 1,
                                 zpos_chk = 1,
                                 xpos = tot_d, # position of the edge in x
                                 zpos = tot_h  # position of the edge in z
                                )

    #  --------------- step 04 ---------------------------      
    #  Hole for the motor
    # 
    #                Z                      Z
    #                :                      :
    #        ________:_________             :__
    #       | |              | |            | :  \        
    #       | |              | |            | :    \ 
    #       | |              | |            | :      \
    #       | |              | |            | :        \
    #       | |              | |            | :          \
    #       | |              | |            | :            \
    #       |_|______________|_|            | :..............\...motor_thick
    #       |_|______________|_|..Y         |_________________\..X
    #       : :                             : :
    #       : :                             : :
    #        reinf_thick                     wall_thick
    

    pos04 = FreeCAD.Vector(wall_thick,0,motor_thick)
    shp04cut = fcfun.shp_boxcen(tot_d, tot_w-2*reinf_thick, tot_h,
                             cy = True, pos=pos04)
    # creates a freecad object from the shape, to see it in FreeCAD Gui,
    # not necessary, but illustrative for this tutorial
    fcd04cut = fcfun.add_fcobj(shp04cut, 'motorhole')
    # difference (cut) of fcd01 and fcd02cut
    fcd04 = doc.addObject("Part::Cut", 'step04')
    fcd04.Base = fcd03
    fcd04.Tool = fcd04cut
    # the shape
    shp04 = fcd04.Shape

    doc.recompute()


    #  --------------- step 05 ---------------------------      
    #  Holes for motor bolts, and the central hole
    #
    #    ____________________...............................>Y
    #   | ___________________|.. wall_thick         
    #   | |                | |.. motor_xtr_space..... 
    #   | | O     __     O | | --                   :motor_w/2
    #   | |    /      \    | |   .                  :
    #   | |   |   1    |   | |   .+ motor_bolt_sep ---
    #   | |    \      /    | |   .
    #   | | O     __     O | | --
    #   |_|________________|_| ..... wall_thick
    #             :        : :
    #             :         reinf_thick
    #       :     X      :
    #       :            :
    #       :            :
    #       motor_bolt_sep

    # position of the motor axis z=-1 to do the cut
    pos05 = FreeCAD.Vector(wall_thick+motor_xtr_space+motor_w/2.,0,-1)
    shp05cenhole = fcfun.shp_cyl (r = motor_hole_r,
                                  h = motor_thick+2, # for the cut
                                  normal = fcfun.VZ,
                                  pos = pos05)
    # make a list of the bolt holes
    boltholes_shp_list = []
    # the four motor holes
    for x_side in [-1,1]:
        for y_side in [-1,1]:
            hole_pos = pos05 + FreeCAD.Vector(x_side*motor_bolt_sep/2.,
                                              y_side*motor_bolt_sep/2.,0)
            shp05bolthole = fcfun.shp_cyl (r = motor_bolt_r_tol,
                                  h = motor_thick+2, # for the cut
                                  normal = fcfun.VZ,
                                  pos = hole_pos)
            boltholes_shp_list.append(shp05bolthole)
    # fuse the 5 holes
    shp05cut = shp05cenhole.multiFuse(boltholes_shp_list)
    # not necessary to create a FreeCAD object, but illustrative for tutorial
    fcd05cut = fcfun.add_fcobj(shp05cut, 'boltholes')
    # difference (cut) of fcd04 and fcd05cut
    fcd05 = doc.addObject("Part::Cut", 'step05')
    fcd05.Base = fcd04
    fcd05.Tool = fcd05cut
    # the shape
    shp05 = fcd05.Shape

    doc.recompute()

    #  --------------- step 06 ---------------------------      
    #  Rails to attach the holder
    # 
    #            Z               
    #            :                
    #    ________:_________        
    #   | |              | |        
    #   | | ||        || | |-----------------------
    #   | | ||        || | |                       :
    #   | | ||        || | |                       +motor_max_h
    #   | | ||        || | |                       :
    #   | | ||        || | |-------                :
    #   |_|______________|_|.......:+ motor_min_h..: 
    #   |_|______________|_|....:+motor_thick............Y
    #        :         :                   
    #        :.........:
    #             bolt_wall_sep

    shp06_cut_list = []
    for y_side in [-1,1]:
        # the rails
        step06_bot_pos =FreeCAD.Vector(-1,y_side*bolt_wall_sep/2.,
                                         motor_thick+motor_min_h )
        shp06_rail = fcfun.shp_boxcen(wall_thick+2, 2*bolt_wall_r_tol,
                                      motor_max_h-motor_min_h,
                                      cy = True, pos = step06_bot_pos)
        shp06_cut_list.append(shp06_rail)
        # bottom end circle:
        shp06_hole = fcfun.shp_cyl (r = bolt_wall_r_tol,
                                    h = wall_thick+2, # for the cut
                                    normal = fcfun.VX,
                                    pos = step06_bot_pos)
        shp06_cut_list.append(shp06_hole)
        step06_top_pos =FreeCAD.Vector(-1,y_side*bolt_wall_sep/2.,
                                         motor_thick+motor_max_h )
        # top end circle:
        shp06_hole = fcfun.shp_cyl (r = bolt_wall_r_tol,
                                    h = wall_thick+2, # for the cut
                                    normal = fcfun.VX,
                                    pos = step06_top_pos)

        shp06_cut_list.append(shp06_hole)

    # fuse the rails
    shp06cut = fcfun.fuseshplist(shp06_cut_list)
    # not necessary to create a FreeCAD object, but illustrative for tutorial
    fcd06cut = fcfun.add_fcobj(shp06cut, 'rails')
    # difference (cut) of fcd04 and fcd05cut
    fcd06 = doc.addObject("Part::Cut", 'step06')
    fcd06.Base = fcd05
    fcd06.Tool = fcd06cut
    # the shape
    shp06 = fcd06.Shape

    doc.recompute()

    return fcd06
   

# creation of a new FreeCAD document
doc = FreeCAD.newDocument()
# creation of the idler tensioner
fcd_motor_holder = nemamotor_holder()

fcd_motor_holder.ViewObject.ShapeColor = fcfun.GREEN_05

fcad_time = datetime.now()

# default values for exporting to STL
LIN_DEFL_orig = 0.1
ANG_DEFL_orig = 0.523599 # 30 degree

#LIN_DEFL = LIN_DEFL_orig/2.
#ANG_DEFL = ANG_DEFL_orig/2.
LIN_DEFL = LIN_DEFL_orig
ANG_DEFL = ANG_DEFL_orig


# ---------- export to stl
stlPath = filepath + '/../stl/'
stlFileName = stlPath + 'simpler_motor_holder' + '.stl'
mesh_shp = MeshPart.meshFromShape(fcd_motor_holder.Shape,
                                  LinearDeflection=LIN_DEFL, 
                                  AngularDeflection=ANG_DEFL)

mesh_time = datetime.now()
fcad_elapsed_time = fcad_time - startdatetime
mesh_elapsed_time = mesh_time - fcad_time
total_time = mesh_time - startdatetime
print ('Lin Defl: ' + str(LIN_DEFL)) 
print ('Ang Defl: ' + str(math.degrees(ANG_DEFL))) 
print ('shape time: ' + str(fcad_elapsed_time))
print ('mesh time: ' + str(mesh_elapsed_time))
print ('total time: ' + str(total_time))
print ('Points: ' + str(mesh_shp.CountPoints))
print ('Edges: ' + str(mesh_shp.CountEdges))
print ('Faces: ' + str(mesh_shp.CountFacets))

#mesh_shp.write(stlFileName)
#del mesh_shp


# save the FreeCAD file
#freecadPath = filepath + '/../freecad/'
#freecadFileName = freecadPath + 'simpler_motor_holder' + '.FCStd'
#doc.saveAs (freecadFileName)
