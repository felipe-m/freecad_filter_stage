# ----------------------------------------------------------------------------
# -- Filter holder
# ----------------------------------------------------------------------------
# -- (c) Felipe Machado
# -- Area of Electronic Technology. Rey Juan Carlos University (urjc.es)
# -- https://github.com/felipe-m/freecad_filter_stage
# -- February-2018
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

from fcfun import V0, VX, VY, VZ, V0ROT
from fcfun import VXN, VYN, VZN

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class ShpFilterHolder (shp_clss.Obj3D):
    """ Creates the filter holder shape



                        axis_h
                         :
                         :
          ___    ___     :     ___    ___ 
         |   |  |   |    :    |   |  |   |
         |...|__|___|____:____|___|__|...|...
         |         _           _         |   2 * bolt_linguide_head_r_tol
         |        |o|         |o|        |-----------------------
         |        |o|         |o|        |--------------------  +boltrow1_4_dist
         |                               |                   :  :
         |                               |                   +boltrow1_3_dist
         |      (O)             (O)      |--:                :  :
         |                               |  +boltrow1_2_dist :  :
         |                               |  :                :  :
         | (O)    (o)   (O)   (o)    (O) |--:----------------:--:
         |_______________________________|  + boltrow1_h
         |_______________________________|..:..................
         |  :.........................:  |..: filt_hole_h  :
         |   :                       :   |                 + base_h
         |___:___________x___________:___|.................:........axis_w
                         :     : :    :
                         :.....: :    :
                         : + boltcol1_dist
                         :       :    :
                         :.......:    :
                         : + boltcol2_dist
                         :            :
                         :............:
                            boltcol3_dist




                                     belt_clamp_l
                                    ..+...
                                    :    :
          _______________x__________:____:...................> axis_w
         |____|                     |____|..                :
         |____   <  )          (  >  ____|..: belt_clamp_t  :+ hold_d
         |____|_____________________|____|..................:
         |_______________________________|
         |  ___________________________  |.................
         | | ......................... | |..filt_supp_in   :
         | | :                       : | |  :              :
         | | :                       : | |  :              :+filt_hole_d
         | | :                       : | |  + filt_supp_d  :
         | | :.......................: | |..:              :
         | |___________________________| |.................:
          \_____________________________/.....filt_rim
         : : :                       : : :
         : : :                       : : :
         : : :                       :+: :
         : : :            filt_supp_in : :
         : : :                       : : :
         : : :.... filt_supp_w ......: : :
         : :                           : :
         : :                           : :
         : :...... filt_hole_w   ......: :
         :                             :+:
         :                      filt_rim :
         :                               :
         :....... tot_w .................:




                ____...............................
               | || |   + belt_clamp_h            :
               |_||_|...:................         :
               |  ..|                   :         :
               |::  |                   :         :
               |::  |                   :         :
               |  ..|                   :         :
               |  ..|                   :         :+ tot_h
               |::  |                   :         :
               |  ..|                   :+hold_h  :
               |  ..|                   :         :
               |::  |                   :         :
               |  ..|                   :         :
               |     \________________  :         :
               |       :...........:  | :         :
               |        :         :   | :         :
               x________:_________:___|.:.........:...>axis_d
               :                      :
               :                      :
               :...... tot_d .........:
 
 


        pos_o (origin) is at pos_d=0, pos_w=0, pos_h=0, It marked with x

    Parameters:
    -----------
    filter_l : float
        length of the filter (it will be along axis_w). Larger dimension
    filter_w : float
        width of the filter (it will be along axis_d). Shorter dimension
    filter_t : float
        thickness/height of the filter (it will be along axis_h). Very short
    base_h : float
        height of the base
    hold_d : float
        depth of the holder (just the part that holds)
    filt_supp_in : float
        how much the filter support goes inside from the filter hole
    filt_cen_d : float
        distance from the filter center to the beginning of the filter holder
        along axis_d
        0: it will take the minimum distance
           or if it is smaller than the minimum distance
    filt_rim : float
        distance from the filter to the edge of the base
    filllet_r : float
        radius of the fillets
    boltcol1_dist : float
        distance to the center along axis_w of the first column of bolts
    boltcol2_dist : float
        distance to the center along axis_w of the 2nd column of bolts
    boltcol3_dist : float
        distance to the center along axis_w of the 3rd column of bolts
        This column could be closer to the center than the 2nd, if distance
        is smaller
    boltrow1_h : float
        distance from the top of the filter base to the first row of bolts
        0: the distance will be the largest head diameter in the first row
           in any case, it has to be larger than this
    boltrow1_2_dist : float
        distance from the first row of bolts to the second
    boltrow1_3_dist : float
        distance from the first row of bolts to the third
    boltrow1_4_dist : float
        distance from the first row of bolts to the 4th
    bolt_cen_mtr : integer (could be float: 2.5)
        diameter (metric) of the bolts at the center or at columns other than
        2nd column
    bolt_linguide_mtr : integer (could be float: 2.5)
        diameter (metric) of the bolts at the 2nd column, to attach to a
        linear guide


    tol : float
        Tolerances to print
    axis_d : FreeCAD.Vector
        length/depth vector of coordinate system
    axis_w : FreeCAD.Vector
        width vector of coordinate system
        if V0: it will be calculated using the cross product: axis_d x axis_h
    axis_h : FreeCAD.Vector
        height vector of coordinate system
    pos_d : int
        location of pos along the axis_d (0,1,2,3,4,5), see drawing
        0: at the back of the holder
        1: at the beginning of the hole for the nut (position for the nut)
        2: at the beginning of the tensioner stroke hole
        3: at the end of the tensioner stroke hole
        4: at the center of the idler pulley hole
        5: at the end of the piece
    pos_w : int
        location of pos along the axis_w (0,1) almost symmetrical
        0: at the center of symmetry
        1: at the end of the piece along axis_w at the negative side
    pos_h : int
        location of pos along the axis_h (0,1,2), symmetrical
        0: at the center of symmetry
        1: at the inner base: where the base of the pulley goes
        2: at the bottom of the piece (negative side of axis_h)
    pos : FreeCAD.Vector
        Position of the cylinder, taking into account where the center is

    Attributes:
    -----------
    All the parameters and attributes of father class SinglePart

    Dimensional attributes:
    filt_hole_d : float
        depth of the hole for the filter (for filter_w)
    filt_hole_w : float
        width of the hole for the filter (for filter_l)
    filt_hole_h : float
        height of the hole for the filter (for filter_t)

    tens_d : float
        total length (depth) of the idler tensioner
    tens_w : float
        total width of the idler tensioner
    tens_h : float
        total height of the idler tensioner
    tens_d_inside : float
        length (depth) of the idler tensioner that can be inside the holder

    prnt_ax : FreeCAD.Vector
        Best axis to print (normal direction, pointing upwards)
    d0_cen : int
    w0_cen : int
    h0_cen : int
        indicates if pos_h = 0 (pos_d, pos_w) is at the center along
        axis_h, axis_d, axis_w, or if it is at the end.
        1 : at the center (symmetrical, or almost symmetrical)
        0 : at the end

    """
    def __init__(self,
                 filter_l = 60.,
                 filter_w = 25.,
                 filter_t = 2.5,
                 base_h = 8.,
                 hold_d = 12.,
                 filt_supp_in = 2.,
                 fillet_r = 1.,
                 # linear guides SEBLV16 y SEBS15, y MGN12H:
                 boltcol1_dist = 20/2.,
                 boltcol2_dist = 12.5, #thorlabs breadboard distance
                 boltcol3_dist = 25,
                 boltrow1_h = 0,
                 boltrow1_2_dist : 12.5,
                 # linear guide MGN12H
                 boltrow1_3_dist = 20.,
                 # linear guide SEBLV16 and SEBS15
                 boltrow1_4_dist = 25.,

                 bolt_cen_mtr = 4, 
                 bolt_linguide_mtr = 3, # linear guide bolts

                 belt_clamp_t = 2.8,
                 belt_clamp_l = 12.,
                 belt_clamp_h = 8.,

                 tol = kcomp.TOL,
                 axis_d = VX,
                 axis_w = VY,
                 axis_h = VZ,
                 pos_d = 0,
                 pos_w = 0,
                 pos_h = 0,
                 pos = V0):
        
        shp_clss.Obj3D.__init__(self, axis_d, axis_w, axis_h)


        # save the arguments as attributes:
        frame = inspect.currentframe()
        args, _, _, values = inspect.getargvalues(frame)
        for i in args:
            if not hasattr(self,i):
                setattr(self, i, values[i])

        # calculation of the dimensions:
        # hole for the filter, including tolerances:
        # Note that now the dimensions width and length are changed.
        # to depth and width
        # they are relative to the holder, not to the filter
        self.filt_hole_d = filter_w + tol # depth
        self.filt_hole_w = filter_l + tol # width in holder axis
        self.filt_hole_h = filter_t + tol/2. # 0.5 tolerance for height

        # The hole under the filter to let the light go through
        # and big enough to hold the filter
        # we could take filter_hole dimensions or filter dimensiones
        # just the tolerance difference
        self.filt_supp_d = self.filt_hole_d - 2 * filt_supp_in
        self.filt_supp_w = self.filt_hole_w - 2 * filt_supp_in

        # look for the largest bolt head in the first row:
        # dictionary of the center bolt and 2nd and 3rd column
        self.bolt_cen_dict = kcomp.D912[bolt_cen_mtr]
        self.bolt_cen_head_r_tol = self.bolt_cen_dict['head_r_tol']
        self.bolt_cen_r_tol = self.bolt_cen_dict['shank_r_tol']
        self.bolt_cen_head_l = self.bolt_cen_dict['head_l']

        # dictionary of the 1st column bolts (for the linear guide)
        self.bolt_linguide_dict = kcomp.D912[bolt_linguide_mtr]
        self.bolt_linguide_head_r_tol = self.bolt_linguide_dict['head_r_tol']
        self.bolt_linguide_r_tol = self.bolt_linguide_dict['shank_r_tol']
        self.bolt_linguide_head_l = self.bolt_linguide_dict['head_l']

        max_row1_head_r_tol = max(self.bolt_linguide_head_r_tol,
                                  self.bolt_cen_head_r_tol)

        if boltrow1_h == 0:
            self.boltrow1_h = 2* max_row1_head_r_tol
        elif boltrow1_h < 2 * max_row1_head_r_tol:
            self.boltrow1_h = 2* max_row1_head_r_tol
            msg1 = 'boltrow1_h smaller than bolt head diameter'
            msg2 = 'boltrow1_h will be bolt head diameter' 
            logger.warning(msg1 + msg2 + str(self.boltrow1_h)
        # else # it will be as it is

        self.hold_h = (base_h + self.boltrow1_h + boltrow1_4_dist
                       + 2 * self.bolt_linguide_head_r_tol)
        self.tot_h = self.hold_h + belt_clamp_h



        # CHANGE:

        self.d0_cen = 0
        self.w0_cen = 1 # symmetrical
        self.h0_cen = 1 # symmetrical

        self.d_o[0] = V0
        self.d_o[1] = self.vec_d(nut_holder_thick)
        self.d_o[2] = self.vec_d(self.nut_holder_tot)
        self.d_o[3] = self.vec_d(self.nut_holder_tot + tens_stroke)
        self.d_o[4] = self.vec_d(self.tens_d - idler_r_in)
        self.d_o[5] = self.vec_d(self.tens_d)

        # these are negative because actually the pos_w indicates a negative
        # position along axis_w
        self.w_o[0] = V0
        self.w_o[1] = self.vec_w(-self.tens_w/2.)

        self.h_o[0] = V0
        self.h_o[1] = self.vec_h(-idler_h/2.)
        self.h_o[2] = self.vec_h(-self.tens_h/2.)

        # calculates the position of the origin, and keeps it in attribute pos_o
        self.set_pos_o()



#shp= ShpIdlerTensioner(idler_h = 10. ,
#                 idler_r_in  = 5,
#                 idler_r_ext = 6,
#                 in_fillet = 2.,
#                 wall_thick = 5.,
#                 tens_stroke = 20. ,
#                 pulley_stroke_dist = 0,
#                 nut_holder_thick = 4. ,
#                 boltidler_mtr = 3,
#                 bolttens_mtr = 3,
#                 opt_tens_chmf = 1,
#                 tol = kcomp.TOL,
#                 axis_d = VX,
#                 axis_w = VY,
#                 axis_h = VZ,
#                 pos_d = 0,
#                 pos_w = 0,
#                 pos_h = 0,
#                 pos = V0)

# CHANGE:
class PartIdlerTensioner (fc_clss.SinglePart, ShpIdlerTensioner):
    """ Integration of a ShpIdlerTensioner object into a PartIlderTensioner
    object, so it is a FreeCAD object that can be visualized in FreeCAD
    """

    def __init__(self,
                 idler_h ,
                 idler_r_in ,
                 idler_r_ext ,
                 in_fillet = 2.,
                 wall_thick = 5.,
                 tens_stroke = 20. ,
                 pulley_stroke_dist = 0,
                 nut_holder_thick = 4. ,
                 boltidler_mtr = 3,
                 bolttens_mtr = 3,
                 opt_tens_chmf = 1,
                 tol = kcomp.TOL,
                 axis_d = VX,
                 axis_w = VY,
                 axis_h = VZ,
                 pos_d = 0,
                 pos_w = 0,
                 pos_h = 0,
                 pos = V0,
                 model_type = 0, # exact
                 name = ''):

        default_name = 'idler_tensioner'
        self.set_name (name, default_name, change = 0)
        # First the shape is created
        ShpIdlerTensioner.__init__(self,
                                  idler_h = idler_h ,
                                  idler_r_in  = idler_r_in,
                                  idler_r_ext = idler_r_ext,
                                  in_fillet = in_fillet,
                                  wall_thick = wall_thick,
                                  tens_stroke = tens_stroke,
                                  pulley_stroke_dist = pulley_stroke_dist,
                                  nut_holder_thick = nut_holder_thick ,
                                  boltidler_mtr = boltidler_mtr,
                                  bolttens_mtr = bolttens_mtr,
                                  opt_tens_chmf = opt_tens_chmf,
                                  tol = tol,
                                  axis_d = axis_d,
                                  axis_w = axis_w,
                                  axis_h = axis_h,
                                  pos_d = pos_d,
                                  pos_w = pos_w,
                                  pos_h = pos_h,
                                  pos = pos)

        # Then the Part
        fc_clss.SinglePart.__init__(self)

        # save the arguments as attributes:
        frame = inspect.currentframe()
        args, _, _, values = inspect.getargvalues(frame)
        for i in args:
            if not hasattr(self,i): # so we keep the attributes by CylHole
                setattr(self, i, values[i])

#part= PartIdlerTensioner(idler_h = 10. ,
#                 idler_r_in  = 5,
#                 idler_r_ext = 6,
#                 in_fillet = 2.,
#                 wall_thick = 5.,
#                 tens_stroke = 20. ,
#                 pulley_stroke_dist = 0,
#                 nut_holder_thick = 4. ,
#                 boltidler_mtr = 3,
#                 bolttens_mtr = 3,
#                 opt_tens_chmf = 1,
#                 tol = kcomp.TOL,
#                 axis_d = VX,
#                 axis_w = VY,
#                 axis_h = VZ,
#                 pos_d = 0,
#                 pos_w = 0,
#                 pos_h = 0,
#                 pos = V0)


