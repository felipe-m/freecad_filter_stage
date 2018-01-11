# ----------------------------------------------------------------------------
# -- Set of idler tensioner and its holder
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

# the tensioner set is referenced on 3 perpendicular axis:
# - fc_axis_d: depth
# - fc_axis_w: width
# - fc_axis_h: height
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
import partgroup 

from fcfun import V0, VX, VY, VZ, V0ROT
from fcfun import VXN, VYN, VZN

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class ShpIdlerTensioner (shp_clss.Obj3D):
    """ Creates the idler pulley tensioner shape and FreeCAD object
    Returns the FreeCAD object created

                       nut_space 
                       .+..
                       :  :
       nut_holder_thick:  :nut_holder_thick
                      +:  :+
                     : :  : :    pulley_stroke_dist
           :         : :  : :       .+.
           :         : :  : :       : : idler_r_ext
           :         : :  : :       : :.+..
           :         : :  : :       : :   : idler_r_int
           :         : :  : :       : :   :.+...
           :         : :  : :       : :   :    :
        ________     : :__:_:_______:_:___:____:..................
       |___::___|     /       ____     __:_:___|.....+wall_thick :
       |    ....|    |  __   /     \  |            :             + tens_h
       |   ()...|    |:|  |:|       | |            + idler_h     :
       |________|    |  --   \_____/  |________....:             :
       |___::___|     \__________________:_:___|.................:
       :        :    :      :       :          :
       :........:    :      :...+...:          :
           +         :......:  tens_stroke     :
         tens_w      :  +                      :
    (2*idler_r_int)  : nut_holder_tot          :
                     :                         :
                     :.........tens_d..........:


                 pos_h
        ________       ________________________
       |___::___|     /       ____     ___::___|
       |    ....|    |  __   /     \  | 
       |   ()...|  0 o:|  |:|       | |        -----> axis_d
       |________|  1 |  --   \_____/  |________
       |___::___|  2  \___________________::___|
       1   0         0  1   2       3      4   5  : pos_d 
       pos_w

        pos_o (origin) is at pos_d=0, pos_w=0, pos_h=0, It marked with o

    Parameters:
    -----------
    wall_thick : float
        Thickness of the walls
    tens_stroke : float
        Length of the idler tensioner body, the stroke. Not including the pulley
        neither the space for the tensioner bolt
    pulley_stroke_dist : float
        Distance along axis_d from between the end of the pulley and the stroke
        Not including the pulley. See picture dimensions
        if 0: it will be the same as wall_thick
    nut_holder_thick : float
        Length of the space along axis_d above and below the nut, for the bolt
    in_fillet: float
        radius of the inner fillets
    idler_h : float
        height of the idler pulley
    idler_r_in : float
        internal radius of the idler pulley. This is the radius of the surface
        where the belt goes
    idler_r_ext : float
        external radius of the idler pulley. This is the most external part of
        the pulley (for example the radius of the large washer)
    boltidler_d : float
        diameter (metric) of the bolt for the idler pulley
    bolttens_d : float
        diameter (metric) of the bolt for the tensioner
    opt_tens_chmf : int
        1: there is a chamfer at every edge of tensioner, inside the holder
        0: there is a chamfer only at the edges along axis_w, not along axis_h
    tol : float
        Tolerances to print
    axis_d : FreeCAD.Vector
        length vector of coordinate system
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
                 idler_h ,
                 idler_r_in ,
                 idler_r_ext ,
                 in_fillet = 2.,
                 wall_thick = 5.,
                 tens_stroke = 20. ,
                 pulley_stroke_dist = 0,
                 nut_holder_thick = 4. ,
                 boltidler_d = 3,
                 bolttens_d = 3,
                 opt_tens_chmf = 1,
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
        if pulley_stroke_dist == 0: # default value
            self.pulley_stroke_dist = wall_thick

        # dictionary of the bolt for the idler pulley
        # din 912 bolts are used:
        self.boltidler_dict = kcomp.D912[boltidler_d]
        self.boltidler_r_tol = self.boltidler_dict['shank_r_tol']

        # --- tensioner bolt and nut values
        # dictionary of the bolt tensioner
        self.bolttens_dict = kcomp.D912[bolttens_d]
        # the shank radius including tolerance
        self.bolttens_r_tol = self.bolttens_dict['shank_r_tol']
        # dictionary of the nut
        self.nuttens_dict = kcomp.D934[bolttens_d]
        self.nut_space = kcomp.NUT_HOLE_MULT_H + self.nuttens_dict['l_tol']
        self.nut_holder_tot = self.nut_space + 2* self.nut_holder_thick
        # the apotheme of the nut
        self.tensnut_ap_tol = (self.nuttens_dict['a2']+tol/2.)/2.

        # --- idler tensioner dimensions
        self.tens_h = self.idler_h + 2*wall_thick
        self.tens_d = (  self.nut_holder_tot
                       + tens_stroke
                       + self.pulley_stroke_dist
                       + idler_r_ext
                       + idler_r_in)

        self.tens_w = 2 * idler_r_in 

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

        # ------------- building of the piece --------------------

        #  --------------- step 01-04 ------------------------      
        #  rectangular cuboid with basic dimensions, but chamfered
        #  at the inner end
        # 
        #       axis_h
        #          : .....tens_l.......
        #          : : ________________:
        #          : /               /|
        #           /               / |
        #       .. /_______________/  |.......
        #       : /                |  /     . 
        # tens_h  |                | /     . tens_w
        #       :. \_______________|/......
        #
        #
        #     o: shows the position of the origin: pos_o
        #
        #                axis_h       axis_h
        #                  :            :
        #         .... ____:____        : ______________________
        #         :   |.........|     ch2/                      |
        #         :   |:       :|       |                       |      
        #  tens_h +   |:   o   :|       o                       |-----> axis_d
        #         :   |:.......:|       |                       |
        #         :...|_________|     ch1\______________________|
        #             :         :       :                       :
        #             :.tens_h..:       :...... tens_l .........:
        #
        #              ____o____ ....> axis_w
        #          ch3/_________\ch4
        #             |         |          chamfer ch3 and ch4 are optional
        #             |         |          Depending on opt_tens_chmf
        #             |         |
        #             |         |
        #             |         |
        #             |         |
        #             |.........|
        #             |         |
        #             |         |
        #             |         |
        #             |_________|
        #                  :
        #                  :
        #                  V
        #                 axis_d

        if opt_tens_chmf == 0: # no optional chamfer, only along axis_w
            edge_dir = self.axis_w
        else:
            edge_dir = V0
   
        shp01chmf = fcfun.shp_boxdir_fillchmfplane(
                               box_w = self.tens_w,
                               box_d = self.tens_d,
                               box_h = self.tens_h,
                               axis_d = self.axis_d,
                               axis_h = self.axis_h,
                               cd=0, cw=1, ch=1,
                               # no tolerances, this is the piece
                               fillet = 0, # chamfer
                               radius = 2*in_fillet,
                               plane_fill = self.axis_d.negative(),
                               both_planes = 0,
                               edge_dir = edge_dir,
                               pos = self.pos_o)
        #  --------------- step 02 ---------------------------  
        # Space for the idler pulley
        #    axis_h
        #      :
        #      : ______________________
        #       /               _______|....
        #      |               |           + idler_h
        #      |               |       5   :----------->axis_d
        #      |               |_______....:
        #       \______________________|...wall_thick
        #                      :       :
        #                      :.......:
        #                         +
        #                       2 * idler_r_xtr
        #
        # the position is pos_d = 5
        # maybe should be advisable to have tolerance, but usually, the 
        # washers have tolerances, and usually are less thick than the nominal
        idler_h_hole =  idler_h # + tol
        if idler_h_hole != idler_h:
            self.idler_h_hole = idler_h_hole
        # NO CHAMFER to be able to fit the pulley well
        shp02cut = fcfun.shp_box_dir_xtr(
                               box_w = self.tens_w,
                               box_d = idler_r_in + idler_r_ext,
                               box_h = idler_h_hole,
                               fc_axis_d = self.axis_d.negative(),
                               fc_axis_h = self.axis_h,
                               cd=0, cw=1, ch=1,
                               xtr_w = 1,
                               xtr_nw = 1,
                               xtr_nd = 1, # extra along axis_d (positive)
                               pos = self.get_pos_d(5))
        shp02 = shp01chmf.cut(shp02cut)
        shp02 = shp02.removeSplitter() # refine shape
        #  --------------- step 03 --------------------------- 
        # Fillets at the idler end:
        #
        #    axis_h
        #      :
        #      :_______________________f2
        #      |                 ______|
        #      |                /      f4
        #      |               |       5    ------> axis_d
        #      |                \______f3...
        #      |_______________________|....+ wall_thick.....> Y
        #      :                       f1
        #      :...... tens_l .........:
        #
        pt_f1 = self.get_pos_d(5) + self.vec_h( -self.tens_h/2.)
        pt_f2 = self.get_pos_d(5) + self.vec_h(  self.tens_h/2.)
        pt_f3 = self.get_pos_d(5) + self.vec_h( -idler_h_hole/2.)
        pt_f4 = self.get_pos_d(5) + self.vec_h(  idler_h_hole/2.)
        shp03 = fcfun.shp_filletchamfer_dirpts (
                                            shp=shp02,
                                            fc_axis=self.axis_w,
                                            fc_pts=[pt_f1,pt_f2, pt_f3, pt_f4],
                                            fillet = 1,
                                            radius=in_fillet)
        #  --------------- step 04 done at step 01 ------------------------ 

        #  --------------- step 05 --------------------------- 
        # Shank hole for the idler pulley:

        #    axis_h                  idler_r_xtr
        #      :                    .+..
        #      : ___________________:__:
        #       /                __:_:_|
        #      |                /             
        #      |               |    4   ----------> axis_d
        #      |                \______
        #       \__________________:_:_|
        #      :                       :
        #      :...... tens_d .........:
        #                     
        # pos_d = 4
        shp05 = fcfun.shp_cylcenxtr (r = self.boltidler_r_tol,
                                     h = self.tens_h,
                                     normal = self.axis_h,
                                     ch = 1, xtr_top = 1, xtr_bot = 1,
                                     pos = self.get_pos_d(4))
        #  --------------- step 06 --------------------------- 
        # Hole for the leadscrew (stroke):

        #    axis_h
        #      :
        #      : ______________________
        #       /      _____     __:_:_|
        #      |    f2/     \f4 /             
        #      |     2       | |        -------> axis_d
        #      |    f1\_____/f3 \______
        #       \__________________:_:_|
        #      :     :       :         :
        #      :     :.......:         :
        #      :     :   +             :
        #      :.....:  tens_stroke    :
        #      :  +                    :
        #      : nut_holder_tot        :
        #      :                       :
        #      :...... tens_d .........:
        # 
        #  pos_d = 2
        shp06a = fcfun.shp_box_dir_xtr(box_w = self.tens_w,
                                       box_d = self.tens_stroke,
                                       box_h = self.idler_h,
                                       fc_axis_h = self.axis_h,
                                       fc_axis_d = self.axis_d,
                                       xtr_w = 1, xtr_nw = 1,
                                       cw=1, cd=0, ch=1,
                                       pos=self.get_pos_d(2))
        shp06 =  fcfun.shp_filletchamfer_dir (shp=shp06a,
                                              fc_axis=self.axis_w,
                                              fillet = 0, radius=self.in_fillet)

        #  --------------- step 07 --------------------------- 
        # Hole for the leadscrew shank at the beginning

        #    axis_h
        #      :
        #      : ______________________
        #       /      _____     __:_:_|
        #      |      /     \   /
        #      |:::::|       | |        ---->axis_d
        #      |      \_____/   \______
        #       \__________________:_:_|
        #      :     :                 :
        #      :     :                 :
        #      :     :                 :
        #      :.....:                 :
        #      :  +                    :
        #      : nut_holder_tot        :
        #      :                       :
        #      :...... tens_d .........:
        #
        shp07 = fcfun.shp_cylcenxtr (r = self.bolttens_r_tol,
                                     h = self.nut_holder_tot,
                                     normal = self.axis_d,
                                     ch = 0, xtr_top = 1, xtr_bot = 1,
                                     pos = self.pos_o)
        #  --------------- step 08 --------------------------- 
        # Hole for the leadscrew nut

        #    axis_h
        #      :
        #      : ______________________
        #       /      _____     __:_:_|
        #      |  _   /     \   /
        #      |:1_|:|       | |       -----> axis_d
        #      |      \_____/   \______
        #       \__________________:_:_|
        #      : :   :                 :
        #      :+    :                 :
        #      :nut_holder_thick       :
        #      :.....:                 :
        #      :  +                    :
        #      : nut_holder_total      :
        #      :                       :
        #      :...... tens_d .........:
        #
        # position at pos_d = 1

        shp08 = fcfun.shp_nuthole (
                               nut_r = self.bolttens_r_tol + kcomp.STOL,
                               nut_h = self.nut_space,
                               hole_h = self.tens_w/2,
                               xtr_nut = 1, xtr_hole = 1, 
                               fc_axis_nut = self.axis_d,
                               fc_axis_hole = self.axis_w,
                               ref_nut_ax = 2, # pos not centered on axis nut 
                               # pos at center of nut on axis hole 
                               ref_hole_ax = 1, 
                               pos = self.get_pos_d(1))

        # --------- step 09:
        # --------- Last step, union and cut of the steps 05, 06, 07, 08
        shp09cut = fcfun.fuseshplist([shp05, shp06, shp07, shp08])
        shp09_final = shp03.cut(shp09cut)

        self.shp = shp09_final

        # normal axes to print without support
        self.prnt_ax = self.axis_w


#shp= ShpIdlerTensioner(idler_h = 10. ,
#                 idler_r_in  = 5,
#                 idler_r_ext = 6,
#                 in_fillet = 2.,
#                 wall_thick = 5.,
#                 tens_stroke = 20. ,
#                 pulley_stroke_dist = 0,
#                 nut_holder_thick = 4. ,
#                 boltidler_d = 3,
#                 bolttens_d = 3,
#                 opt_tens_chmf = 1,
#                 tol = kcomp.TOL,
#                 axis_d = VX,
#                 axis_w = VY,
#                 axis_h = VZ,
#                 pos_d = 0,
#                 pos_w = 0,
#                 pos_h = 0,
#                 pos = V0)

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
                 boltidler_d = 3,
                 bolttens_d = 3,
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
                                  boltidler_d = boltidler_d,
                                  bolttens_d = bolttens_d,
                                  opt_tens_chmf = opt_tens_chmf,
                                  tol = tol,
                                  axis_d = axis_d,
                                  axis_w = axis_w,
                                  axis_h = axis_h,
                                  pos_d = pos_d,
                                  pos_w = pos_w,
                                  pos_h = pos_h,
                                  pos = V0)

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
#                 boltidler_d = 3,
#                 bolttens_d = 3,
#                 opt_tens_chmf = 1,
#                 tol = kcomp.TOL,
#                 axis_d = VX,
#                 axis_w = VY,
#                 axis_h = VZ,
#                 pos_d = 0,
#                 pos_w = 0,
#                 pos_h = 0,
#                 pos = V0)


class IdlerTensionerSet (fc_clss.PartsSet):
    """ Integration of a ShpIdlerTensioner object into a PartIlderTensioner
    object, so it is a FreeCAD object that can be visualized in FreeCAD

    Parameter:
    ---------
    in_fillet: float
        radius of the inner fillets
    pos_d : int
        location of pos along the axis_d (0,1,2,3,4,5), see drawing
        0: at the back of the holder
        1: at the beginning of the hole for the nut (position for the nut)
        2: at the beginning of the tensioner stroke hole
        3: at the end of the tensioner stroke hole
        4: at the inner end of the bearing. It didnt exist in ShpIdlerTensioner
           Therefore, from this, numbers change compared with ShpIdlerTensioner
        5: at the center of the idler pulley hole
           (it is 4 in ShpIdlerTensioner)
        6: at the end of the piece (it is 5 in ShpIdlerTensioner)
    pos_w : int
        location of pos along the axis_w (0,1) almost symmetrical
        0: at the center of symmetry
        1: at the end of the tensioner along axis_w
        2: at the end of the larger washer along axis_w
    pos_h : int
        location of pos along the axis_h (0,1,2), symmetrical
        0: at the center of symmetry
        1: at the inner base: where the base of the pulley goes
        2: at the bottom of the piece
    pos : FreeCAD.Vector
        position of the piece
    See drawing:

                      nut_holder_thick:  :nut_holder_thick
                                     +:  :+
                                    : :  : :    pulley_stroke_dist
                                    : :  : :       .+.
                                    : :  : :       : :
                                    : :  : :       : :  boltidler_metric
                                    : :  : :       : :   +
        ________                    : :__:_:_______:_:__:_:___ ....
       |___::___|                    /       ____     __:_:___|....+wall_thick
       |    ....|                   |  __   /     \  |
       |   ()...|  bolttens_metric::|:|  |:|       | |
       |________|                   |  --   \_____/  |________
       |___::___|                    \__________________:_:___|
                                           :       :
                                           :...+...:
                                              tens_stroke

       origin: pos_o is at point o


          axis_h 
            :                                             pos_h
        ____:____              ____________________________
       |___:_:___|            /       ____     _____:_:____|
      |___________|          |       /     \  ||____:_:____|  large washer
       |_________|           |      |       | |   |_:_:_|     regular wahser
       |     ....|           |  ..  |       | |   | : : |     bearing
       |   :o:   |->axis_w   o::  ::|       | |   | : : |   0 -----> axis_d
       |_________|           |  ..  |       | |   |_:_:_|
       |_________|           |      |       | | __|_:_:_|__ 1
      |___________|          |       \_____/  ||___________|2
       |___:_:___|            \_____________________:_:____|3
      21    0                0  1   2       3     4  5     6 : pos_d 
       pos_w


       tensioner_width is the same as the idler internal diameter



    """

    def __init__(self, 
                 boltidler_metric = 3,
                 bolttens_metric = 3,
                 tens_stroke = 20. ,
                 wall_thick = 5.,
                 in_fillet = 2.,
                 pulley_stroke_dist = 0,
                 nut_holder_thick = 4. ,
                 opt_tens_chmf = 1,
                 tol = kcomp.TOL,
                 axis_d = VX,
                 axis_w = VY,
                 axis_h = VZ,
                 pos_d = 0,
                 pos_w = 0,
                 pos_h = 0,
                 pos = V0,
                 name = ''):

        default_name = 'idler_tensioner_set'
        self.set_name (name, default_name, change = 0)

        fc_clss.PartsSet.__init__(self, axis_d = axis_d,
                                  axis_w = axis_w, axis_h = axis_h)

        # save the arguments as attributes:
        frame = inspect.currentframe()
        args, _, _, values = inspect.getargvalues(frame)
        for i in args:
            if not hasattr(self,i): # so we keep the attributes by CylHole
                setattr(self, i, values[i])

        # pos_h/w = 0 are at the center, not pos_d
        self.d0_cen = 0
        self.w0_cen = 1
        self.h0_cen = 1

        # before creating the idler_pulley and the tensioner, we dont
        # know their dimensions and positions. We could calculate them
        # here, but it would be to calculate twice. Instead, we create
        # them, and then move them and calculate the vectors h_o, d_o, w_o

        # Creation of the idler pulley, we put it in the center
        pulley = fc_clss.BearWashSet(metric = bolttens_metric,
                                            axis_h = axis_h, pos_h = 0,
                                            axis_d = axis_d, pos_d = 0,
                                            axis_w = axis_w, pos_w = 0,
                                            pos = pos)
        self.append_part(pulley)
        #self.pulley_h =  pulley.tot_h
        #self.pulley_r_in =  pulley.r_in
        #self.pulley_r_ext =  pulley.r_ext
        # Creation of the tensioner, with pos_h,d,w = 0 because we dont know
        # the dimensions yet
        idler_tens_part =  PartIdlerTensioner(
                                     idler_h     = pulley.tot_h ,
                                     idler_r_in  = pulley.r_in,
                                     idler_r_ext = pulley.r_ext,
                                     in_fillet   = in_fillet,
                                     wall_thick  = wall_thick,
                                     tens_stroke = tens_stroke ,
                                     pulley_stroke_dist = pulley_stroke_dist,
                                     nut_holder_thick = nut_holder_thick,
                                     boltidler_d = boltidler_metric,
                                     bolttens_d  = bolttens_metric,
                                     opt_tens_chmf = opt_tens_chmf,
                                     tol    = tol,
                                     axis_d = self.axis_d,
                                     axis_w = self.axis_w,
                                     axis_h = self.axis_h,
                                     pos_d  = 0,
                                     pos_w  = 0,
                                     pos_h  = 0,
                                     pos    = pos)
        self.append_part(idler_tens_part)

        

        # Now we have to move them and calculate the distance vectors h_o,..
        # pos_d, pos_w, pos_w: are different for the components and the set
        #       axis_h 
        #         :                                     pos_h for Pulley-\
        #         :                           pos_h for idlerTensPart-\
        #         :                         pos_h for TensionerSet-\
        #     ____:____              ____________________________   3  2
        #    |___:_:___|            /       ____     _____:_:____|  2  1  3
        #   |___________|          |       /     \  ||____:_:____|        2
        #    |_________|           |      |       | |   |_:_:_|     1     1
        #    |     ....|           |  ..  |       | |   | : : |   
        #    |   :o:   |           o::  ::|       | |   | : : |     0  0  0
        #    |_________|           |  ..  |       | |   |_:_:_|          -1
        #    |_________|           |      |       | | __|_:_:_|__  -1    -2
        #   |___________|          |       \_____/  ||___________| -2 -1 -3
        #    |___:_:___|            \_____________________:_:____| -3 -2
        #  -21    0    12  TensSet 0  1   2       3     4  5     6 : pos_d 
        #   -1    0    1 iTensPart 0  1   2       3        4     5
        #  -32  -101   23   Pulley                  -3 -2-101 2  3  
        #
        #         |-->axis_w       |---> axis_d

        # When pos_d,w,h are centered, d0_cen, w0_cen, h0_cen = 1
        # h_o[1] is the distance from o to -1, or from 1 to o
        self.d_o[0] = V0
        self.d_o[1] = idler_tens_part.d_o[1]
        self.d_o[2] = idler_tens_part.d_o[2]
        self.d_o[3] = idler_tens_part.d_o[3]
        # He have to add them because pulley.d_o is in opposite direction
        # pulley.d_o[2] is the  distance from o to -2, or from 2 to o
        #             pulley axis -->        + axis to pulley r_in  <--
        self.d_o[4] = idler_tens_part.d_o[4] + pulley.d_o[2]
        self.d_o[5] = idler_tens_part.d_o[4]
        self.d_o[6] = idler_tens_part.d_o[5]

        self.w_o[0] = V0
        self.w_o[1] = pulley.w_o[2]
        self.w_o[2] = pulley.w_o[3]

        # h_o[1] is the distance from o to -1, or from 1 to o
        self.h_o[0] = V0
        self.h_o[1] = pulley.h_o[2]
        self.h_o[2] = pulley.h_o[3]
        self.h_o[3] = idler_tens_part.h_o[2]

        # Now we place the idler tensioner according to pos_d,w,h
        self.set_pos_o()

        # Now we have the position where the origin is, but:
        # - we havent located the idler_tensioner at pos_o
        # - we havent located the pulley at pos_o + dist to axis

        # we should have call PartIdlerTensioner (pos = self.pos_o)
        # instead, we have it at (pos = self.pos)
        # so we have to move PartIdlerTensioner self.pos_o - self.pos
        self.add_part_place(idler_tens_part)

        self.add_part_place(pulley, self.get_o_to_d(5))



partset= IdlerTensionerSet (
                 boltidler_metric = 3,
                 bolttens_metric = 3,
                 tens_stroke = 20. ,
                 wall_thick = 5.,
                 in_fillet = 2.,
                 pulley_stroke_dist = 0,
                 nut_holder_thick = 4. ,
                 opt_tens_chmf = 1,
                 tol = kcomp.TOL,
                 axis_d = VX,
                 axis_w = VY,
                 axis_h = VZ,
                 pos_d = 0,
                 pos_w = 0,
                 pos_h = 0,
                 pos = V0,
                 name = 't')

