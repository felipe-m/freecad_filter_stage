# ----------------------------------------------------------------------------
# -- Filter holder examples
# ----------------------------------------------------------------------------
# -- (c) Felipe Machado
# -- Area of Electronic Technology. Rey Juan Carlos University (urjc.es)
# -- https://github.com/felipe-m/freecad_filter_stage
# -- September-2018
# ----------------------------------------------------------------------------
# --- LGPL Licence
# ----------------------------------------------------------------------------
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




# the filter is referenced on 3 perpendicular axis:
# - axis_d: depth
# - axis_w: width
# - axis_h: height
#
# The reference position is marked with a x in the drawing

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
import partgroup 
import filter_holder_clss 

from fcfun import V0, VX, VY, VZ, V0ROT
from fcfun import VXN, VYN, VZN

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

doc = FreeCAD.newDocument()

fh1 = filter_holder_clss.PartFilterHolder(
                 filter_l = 60.,
                 filter_w = 25.,
                 filter_t = 2.5,
                 base_h = 6.,
                 hold_d = 12.,
                 filt_supp_in = 2.,
                 filt_rim = 3.,
                 filt_cen_d = 30,
                 fillet_r = 1.,
                 # linear guides SEBLV16 y SEBS15, y MGN12H:
                 boltcol1_dist = 20/2.,
                 boltcol2_dist = 12.5, #thorlabs breadboard distance
                 boltcol3_dist = 25,
                 boltrow1_h = 0,
                 boltrow1_2_dist = 12.5,
                 # linear guide MGN12H
                 boltrow1_3_dist = 20.,
                 # linear guide SEBLV16 and SEBS15
                 boltrow1_4_dist = 25.,

                 bolt_cen_mtr = 4, 
                 bolt_linguide_mtr = 3, # linear guide bolts

                 beltclamp_t = 3.,
                 beltclamp_l = 12.,
                 beltclamp_h = 8.,
                 clamp_post_dist = 4.,
                 sm_beltpost_r = 1.,

                 tol = kcomp.TOL,
                 axis_d = VX,
                 axis_w = VY,
                 axis_h = VZ,
                 pos_d = 0,
                 pos_w = 0,
                 pos_h = 0,
                 pos = V0)

fh1.set_color(fcfun.ORANGE_08)



fh2 = filter_holder_clss.PartFilterHolder(
                 filter_l = 100.,
                 filter_w = 50.,
                 filter_t = 3.5,
                 base_h = 10.,
                 hold_d = 12.,
                 filt_supp_in = 3.,
                 filt_rim = 5.,
                 filt_cen_d = 60,
                 fillet_r = 3.,
                 boltcol1_dist = 30/2.,
                 boltcol2_dist = 20, #thorlabs breadboard distance
                 boltcol3_dist = 40,
                 boltrow1_h = 20,
                 boltrow1_2_dist = 15,
                 boltrow1_3_dist = 30.,
                 # linear guide SEBLV16 and SEBS15
                 boltrow1_4_dist = 40.,

                 bolt_cen_mtr = 4, 
                 bolt_linguide_mtr = 3, # linear guide bolts

                 beltclamp_t = 3.,
                 beltclamp_l = 14.,
                 beltclamp_h = 10.,
                 clamp_post_dist = 4.,
                 sm_beltpost_r = 1.,

                 tol = kcomp.TOL,
                 axis_d = VX,
                 axis_w = VY,
                 axis_h = VZ,
                 pos_d = 0,
                 pos_w = 0,
                 pos_h = 0,
                 pos = FreeCAD.Vector(0,100,0))

fh2.set_color(fcfun.ORANGE_08)



#doc.recompute()
