# ----------------------------------------------------------------------------
# -- Filter stage
# ----------------------------------------------------------------------------
# -- (c) Felipe Machado
# -- Area of Electronic Technology. Rey Juan Carlos University (urjc.es)
# -- https://github.com/felipe-m/freecad_filter_stage
# -- February-2018
# ----------------------------------------------------------------------------
# --- LGPL Licence
# ----------------------------------------------------------------------------
# 
#  Stage that includes:
#  - Filter holder
#  - Idler pulley and belt tensioner
#  - Stepper motor holder
#
#  -------------------- Filter holder:
#
#                     axis_h
#                        :
#                        :
#         ___    ___     :     ___    ___       ____
#        |   |  |   |    :    |   |  |   |     | || |
#        |...|__|___|____:____|___|__|...|     |_||_|
#        |         _           _         |     |  ..|
#        |        |o|         |o|        |     |::  |
#        |        |o|         |o|        |     |::  |
#        |                               |     |  ..|
#        |                               |     |  ..|
#        |      (O)             (O)      |     |::  |
#        |                               |     |  ..|
#        |                               |     |  ..|
#        |  (O)   (o)   (O)   (o)   (O)  |     |::  |
#        |_______________________________|     |  ..|
#        |_______________________________|     |     \_________________
#        |  :.........................:  |     |       :............:  |
#        |   :                       :   |     |        :          :   |
#        |___:___________x___________:___|     x________:__________:___|.>axis_d
#
#
#         _______________x_______________ ......> axis_w
#        |____|                     |____|
#        |____   <  )          (  >  ____|
#        |____|_____________________|____|
#        |_______________________________|
#        |  ___________________________  |
#        | | ......................... | |
#        | | :                       : | |
#        | | :                       : | |
#        | | :                       : | |
#        | | :.......................: | |
#        | |___________________________| |
#         \_____________________________/
#                        :
#                        :
#                        :
#                      axis_d
#
#
#  - Idler pulley and belt tensioner
#
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
import tensioner_clss # Idler pulley and belt tensioner 
import filter_holder_clss # Filter holder
import comps   # CAD components
import partgroup 
import parts
import partset

from fcfun import V0, VX, VY, VZ, V0ROT
from fcfun import VXN, VYN, VZN

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


doc = FreeCAD.newDocument()

# definition of the axes
axis_mov   = VY # the filter will move along axis Y
axis_front = VX
axis_up    = VZ

# distance in mm that the filter is going to move
mov_distance = 60.

# width of the timming belt
belt_w = 6.

# position of the filter
filter_pos = V0
# the point of this position is the filter center of symmetry and its base
filter_pos_d = 9
filter_pos_w = 0
filter_pos_h = 1

# width of the belt
belt_w =  6.
# height of the belt clamp
beltclamp_h = belt_w + 2
# length of the motor shaft
motorshaft_l = 24.

# width of the aluminum profile
aluprof_w = 20.

filter_holder = filter_holder_clss.PartFilterHolder(
                 filter_l = 60.,
                 filter_w = 25.,
                 filter_t = 2.5,
                 base_h = 6.,
                 hold_d = 12.,
                 filt_supp_in = 2.,
                 filt_rim = 3.,
                 filt_cen_d = 30,
                 fillet_r = 1.,
                 boltcol1_dist = 20/2.,
                 boltcol2_dist = 12.5,
                 boltcol3_dist = 25,
                 boltrow1_h = 0,
                 boltrow1_2_dist = 12.5,
                 boltrow1_3_dist = 20.,
                 boltrow1_4_dist = 25.,
                 bolt_cen_mtr = 4, 
                 bolt_linguide_mtr = 3,
                 beltclamp_t = 3.,
                 beltclamp_l = 12.,
                 beltclamp_h = beltclamp_h,
                 clamp_post_dist = 4.,
                 sm_beltpost_r = 1.,
                 tol = kcomp.TOL,
                 axis_d = axis_front,
                 axis_w = axis_mov,
                 axis_h = axis_up,
                 pos_d = filter_pos_d,
                 pos_w = filter_pos_w,
                 pos_h = filter_pos_h,
                 pos = filter_pos,
                 name = 'filter_holder')

filter_holder.set_color(fcfun.YELLOW_05)

# get the position of the belt of the filter, at center of symmetry
belt_pos = filter_holder.get_pos_dwh(2,0,7)

tensioner_pos = (  belt_pos
                 + DraftVecUtils.scale(axis_mov,
                                       mov_distance/2. + filter_holder.tot_w/2.)
                 + DraftVecUtils.scale(axis_up, belt_w/2.))

nemaholder_w_motor_pos = (
                   belt_pos
                 + DraftVecUtils.scale(axis_mov,
                                       - mov_distance/2.
                                       - filter_holder.tot_w/2.
                                       - aluprof_w)
                 + DraftVecUtils.scale(axis_up, belt_w/2.))

print (str(belt_pos))
print (str(tensioner_pos))

# at the end of the idler tensioner, when it is all the way out
tensioner_pos_d = 8
#tensioner_pos_d = 2
tensioner_pos_w = -1 # at the pulley radius
tensioner_pos_h = 3 # middle point of the pulley

tensioner = tensioner_clss.TensionerSet(
                     aluprof_w = 20.,
                     belt_pos_h = 30., 
                     hold_bas_h = 0,
                     hold_hole_2sides = 1,
                     boltidler_mtr = 3,
                     bolttens_mtr = 3,
                     boltaluprof_mtr = 3,
                     tens_stroke = 15. ,
                     wall_thick = 3.,
                     in_fillet = 2.,
                     pulley_stroke_dist = 0,
                     nut_holder_thick = 4. ,
                     opt_tens_chmf = 1,
                     tol = kcomp.TOL,
                     axis_d = axis_mov.negative(),
                     axis_w = axis_front.negative(),
                     axis_h = axis_up,
                     pos_d = tensioner_pos_d,
                     pos_w = tensioner_pos_w,
                     pos_h = tensioner_pos_h,
                     pos = tensioner_pos,
                     name = 'tensioner_set')

tensioner.set_color(fcfun.ORANGE,1)   #1: the tensioner
tensioner.set_color(fcfun.LSKYBLUE,2) #2: the holder

# set with:
# + motor holder
# + motor
# + pulley

motor_holder_pos = (  belt_pos
                  + DraftVecUtils.scale(axis_mov, - mov_distance)
                  + DraftVecUtils.scale(axis_up, -(motorshaft_l - beltclamp_h)))


nema_size = 11

nemaholder_w_motor = partset.NemaMotorPulleyHolderSet(
                        nema_size = nema_size, 
                        motor_base_l = 32.,
                        motor_shaft_l = motorshaft_l,
                        motor_circle_r = 11.,
                        motor_circle_h = 2.,
                        motor_chmf_r = 1.,

                        pulley_pitch = 2.,
                        pulley_n_teeth = 20,
                        pulley_toothed_h = 7.5,
                        pulley_top_flange_h = 1.,
                        pulley_bot_flange_h = 0,
                        pulley_tot_h = 16.,
                        pulley_flange_d = 15.,
                        pulley_base_d = 15.,
                        #pulley_tol = 0,
                        #pulley_pos_h = -1,                        
                        hold_wall_thick = 4.,
                        hold_motorside_thick = 4.,
                        hold_reinf_thick = 4.,
                        hold_rail_min_h = 10.,
                        hold_rail_max_h = 40,
                        hold_motor_xtr_space = 2.,
                        hold_bolt_wall_d = 4.,
                        # hold_chmf_r = 1.,
                        axis_h = axis_up,
                        axis_d = axis_mov.negative(),
                        pos_h = 11, # middle point of the pulley toothed part
                        pos_d = 0, #0: at the wall where this holder is attached
                        pos_w = 5, #5: inner radius of the pulley (to the back
                        pos = nemaholder_w_motor_pos)

nemaholder_w_motor.set_color(fcfun.GREEN_05,1)   #1: the tensioner


doc.recompute()
