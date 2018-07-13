# ----------------------------------------------------------------------------
# -- Set of idler tensioner and its holder
# ----------------------------------------------------------------------------
# -- (c) Felipe Machado
# -- Area of Electronic Technology. Rey Juan Carlos University (urjc.es)
# -- https://github.com/felipe-m/freecad_filter_stage
# -- December-2017
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
# :..hold_bas_h:.|_::____|_______|____::_|0     |___::___|/......axis_l
#                                               0    1           2: pos_l
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
#                |  O |  | :   : |  |  O  |    + hold_bas_l
#                |____|__| :   : |__|_____|....:
#                        | :   : |
#                        |_:___:_|
#                          |   |
#                           \_/
#                            :
#                            :
#                           axis_l

# the tensioner set is referenced on 3 perpendicular axis:
# - fc_axis_l: length
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
import Mesh
import MeshPart
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
import comps   # import my CAD components
import partgroup 
import kparts 

from fcfun import V0, VX, VY, VZ, V0ROT
from fcfun import VXN, VYN, VZN

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class Tensioner (object):
    """
    Creates a belt tensioner set:
    - holder
    - idler tensioner
    - idler pulley


                              axis_h            axis_h 
                               :                  :
    ....................... ___:___               :______________
    :                      |  ___  |     pos_h:   |  __________  |---
    :                      | |   | |        3     | |__________| | : |
    :+hold_h              /| |___| |\       1,2   |________      |---
    :                    / |_______| \            |        |    /      
    :             . ____/  |       |  \____       |________|  /
    :..hold_bas_h:.|_::____|_______|____::_|0     |___::___|/......>axis_l
                                                  0    1           2: pos_l
   
   
   
                    .... hold_bas_w ........
                   :        .hold_w.        :
                   :       :    wall_thick  :
                   :       :      +         :
                   :       :     : :        :
          pos_w:   2__1____:___0_:_:________:........>axis_w
                   |    |  | :   : |  |     |    :
                   |  O |  | :   : |  |  O  |    + hold_bas_l
                   |____|__| :   : |__|_____|....:
                           | :   : |
                           |_:___:_|
                             |   |
                              \_/
                               :
                               :
                             axis_l

    The set is referenced along 3 perpendicular axis
      (cartesian coordinate systems):
      - axis_l: length
      - axis_w: width
      - axis_h: height
    There is a position of the piece:
      - pos: FreeCAD Vector
    This position of the piece (pos) can be at different locations within
      the piece. These locations are defined by:
      - pos_l: location of pos along the axis_l (0,1,2)
         - 0: at the back of the holder
         - 1: at the center of the base along axis_l, where the bolts to attach
              the holder base to the aluminum profile
         - 2: at the center of the idler pulley
      - pos_w: location of pos along the axis_w (0,1,2)
         - 0: at the center of symmetry
         - 1: at the center of the bolt holes to attach the holder base to the
              aluminum profile
         - 2: at the end of the piece along axis_w
              axes have direction. So if pos_w == 3, the piece will be drawn
              along the positive side of axis_w
      - pos_h: location of pos along the axis_h (0,1,2,3)
         - 0: at the bottom of the holder
         - 1: at the bottom of the idler tensioner
         - 2: at the bottom of the idler pulley
         - 3: at the center of the idler pulley

    Parameters
    ----------
    aluprof_w : float
        Width of the aluminum profile
    belt_pos_h : float
        The position along axis_h where the idle pulley that conveys the belt
        starts. This is the base of the small washer just under the bearing,
        when the pulley is made with washers and bearings
    wall_thick : float
        Thickness of the walls
    tens_stroke : float
        Length of the ilder tensioner body, the stroke. Not including the pulley
        neither the space for the tensioner bolt
    pulley_stroke_dist : float
        Distance along axis_l from between the end of the pulley and the stroke
        Not including the pulley. See picture dimensions
        if 0: it will be the same as wall_thick
    nut_holder_thick : float
        Length of the space along axis_l above and below the nut, for the bolt
    in_fillet: float
        radius of the inner fillets
    boltaluprof_d : float
        diameter (metric) of the bolt that attachs the tensioner holder to the
        aluminum profile (or whatever is attached to)
    boltidler_d : float
        diameter (metric) of the bolt for the idler pulley
    bolttens_d : float
        diameter (metric) of the bolt for the tensioner
    hold_bas_h : float
        height of the base of the tensioner holder
    tens_in_ratio : float
        from 0 to 1, the ratio of the stroke that the tensioner is inside.
        if 1: it is all the way inside
        if 0: it is all the way outside (all the tens_stroke)
    opt_tens_chmf : int
        1: there is a chamfer at every edge of tensioner, inside the holder
        0: there is a chamfer only at the edges along axis_w, not along axis_h
    hold_hole_2sides : int
        In the tensioner holder there is a hole to see inside, it can be at
        each side of the holder or just on one side
        0: only at one side
        1: at both sides
    axis_l : FreeCAD.Vector
        length vector of coordinate system
    axis_w : FreeCAD.Vector
        width vector of coordinate system
        if V0: it will be calculated using the cross product: axis_l x axis_h
    axis_h : FreeCAD.Vector
        height vector of coordinate system
    pos_l : int
        location of pos along the axis_l (0,1,2)
        0: at the back of the holder
        1: at the center of the base along axis_l, where the bolts to attach
           the holder base to the aluminum profile
        2: at the center of the idler pulley
    pos_w : int
        location of pos along the axis_w (0,1,2)
        0: at the center of symmetry
        1: at the center of the bolt holes to attach the holder base to the
           aluminum profile
        2: at the end of the piece along axis_w
           axes have direction. So if pos_w == 3, the piece will be drawn
           along the positive side of axis_w
    pos_h : int
        location of pos along the axis_h (0,1,2,3)
        0: at the bottom of the holder
        1: at the bottom of the idler tensioner
        2: at the bottom of the idler pulley
        3: at the center of the idler pulley
    pos : FreeCAD.Vector
        position of the piece
    wfco : int
        if a FreeCAD object is created, or only shapes
        1: object will be created
    name : str
        prefix for the name of the freecad objects

    Attributes:
    -----------------------
    All the parameters are attributes

    fco_l : list of FreeCAD objects
        list of all the FreeCAD objects that are in this set:
        tensioner_holder, idler_holder, idler

    name_l : list of str
        list of all the names (prefixes) of the pieces FreeCAD objects that
        are in this set:
        tensioner_holder, idler_holder, idler
        with the same order and index than fco_l

    pos0_l : list of FreeCAD.Vector
        Absolute position of the origin of the different parts
        with the same order and index than fco_l

    place : FreeCAD.Vector
        Position of the tensioner set.
        There is the parameter pos, where the piece is built and can be at
        any position.
        Once the piece is built, its placement (Placement.Base) is at V0:
        FreeCAD.Vector(0,0,0), however it can be located at any place, since
        pos could have been set anywhere.
        The attribute place will move again the whole piece, including its parts

    color : Tuple of 3 elements, each of them from 0 to 1
        They define the RGB colors.
        0: no color on that channel
        1: full intesity on that channel

    -- print axes (best direction to print, pointing upwards) 
    prnt_ax_l : list of FreeCAD.Vector
        with the same order and index than fco_l

    prnt_ax_idl_tens : FreeCAD.Vector
        Best axis to print for the idler tensioner
    prnt_ax_tens_hold : FreeCAD.Vector
        Best axis to print for the tensioner holder

    -- bolt idler attributes --
    d_boltidler : dictionary
        dictionary of the bolt for the idler pulley. see kcomp
    boltidler_r_tol : float
        the shank radius including tolerance
    idlerpulley_l : list
        the idler group list resulting from the bolt idler. see partgroup
    idler_h : float
        height of the idler pulley, made out of washers and bearings
    idler_r : float
        radius of the idler pulley, made out of washers and bearings 
        radius of the bearing
    idler_r_xtr : float
        radius of the idler pulley plus an extra
    largewasher_thick : float
        thickness (height) of the largest washer of the idler

    -- bolt tensioner attributes --
    d_bolttens : dictionary
        dictionary of the bolt tensioner, see kcomp
    bolttens_r_tol : float
        the shank radius including tolerance
    d_nuttens : dictionary
        dictionary of the nut used in the tensioner, see kcomp
    nut_space : float
        height to have space to insert the nut
    nut_holder_total : float
        all the length of the nut holder, the space and 2*nut_holder_thick
    tensnut_ap_tol : float
        the apotheme of the nut of the tensioner

    -- bolt to attach to the aluminum profile attributes --
    d_boltaluprof : dictionary
        dictionary of the bolt, see kcomp
    boltaluprof_head_r_tol : float
        radius of the bolt head, including tolerance
    boltaluprof_r_tol : float
        radius of the bolt shank, including tolerance
    boltaluprof_head_l : float
        length of the bolt head

    -- idler tensioner dimensions attributes --
    tens_l : float
        tensioner length
    tens_w : float
        tensioner width
    tens_h : float
        tensioner height
    tens_w_tol : float
        tensioner width including tolerance to make a hole in the
        tensioner holder
    tens_h_tol : float
        tensioner height including tolerance to make a hole in the
        tensioner holder
    tens_pos_h : float 
        vertical distance from the bottom of the base of the idler tensioner
    vh_0to_tens0: FreeCAD.Vector
        Vector along axis_h from the base to the center of the tensioner
    vl_0to_tens0: FreeCAD.Vector
        Vector along axis_l from the base to the center of the tensioner
    pos_tens0: FreeCAD.Vector
        absolute position of the center of the tensioner.
        The center of the tensioner is:
        - at its symmetry point along axis_w and axis_h
        - at the lower point along axis_l
        - considering that the tensioner is all the way inside. So actually
          that point is at the tensioner holder
    tens_l_inside : float 
        the part of the tensioner that will be inside when it is all the way in
        
    -- tensioner holder dimensions attributes --
    hold_l : float
        tensioner holder length
    hold_w : float
        tensioner holder width
    hold_h : float
        tensioner holder height
    hold_bas_w : float
        tensioner holder base width
    hold_bas_l : float
        tensioner holder base length (along axis_l)

    -- tensioner holder attributes created in tensioner_holder method
    shp_tens_hold : shape
        Shape of the tensioner holder
    fco_tens_hold : FreeCAD object
        FreeCAD object of the tensioner holder
    axprn_tens_hold: FreeCAD.Vector
        FreeCAD vector for the best direction to print.
        It has to be aligned with axis Z

    Idler Tensioner arguments drawings:
    -----------------------------------

          axis_h
            :
            :                   nut_holder_thick    boltidler_d
            :                      +                   +
      .. ________                 : :_________________:_:_....
      : |___::___|                 /      _____     __:_:_|..:+wall_thick
      : |    ....|              ..|  _   /     \   /             
      : |   ()...|    bolttens_d..|:|_|:|       | |        
      : |________|                |      \_____/   \______
      :.|___::___|                 \__________________:_:_|.....> axis_l
                                        :       : :        
                                        :       :.:        
                                        :       :+         
                                        :.......:pulley_stroke_dist
                                            +              
                                           tens_stroke     


    Tensioner Holder arguments drawings:
    ------------------------------------

                              axis_h            axis_h 
                               :                  :
                            ___:___               :______________
                           |  ___  |              |  __________  |---
                           | |   | |              | |__________| | : |
    .---- belt_pos_h------/| |___| |\             |________      |---
    :                    / |_______| \            |        |    /      
    :             . ____/  |       |  \____       |________|  /
    :..hold_bas_h:.|_::____|_______|____::_|      |___::___|/......>axis_l
   
                                wall_thick
                                  +
                                 : :         
                    _____________:_:________.........>axis_w
                   |    |  | :   : |  |     |    :
                   |  O |  | :   : |  |  O  |    + aluprof_w
                   |____|__| :   : |__|_____|....:
                           | :   : |
                           |_:___:_|
                             |   |
                              \_/
                               :
                               :
                             axis_l


   idler_tensioner postion relative to the bottom of the holder:
          _______________________
         /      ______   ___::___|
        |  __  |      | | _______  
        *:|  |:|      | ||_______|.......................bottom side of small
        |  --  |______| |_======_                       :  washer just below
         \__________________::___|.: wall_thick         :  the bearing
                                     :                  :
        * pos_tens0                  :                  + belt_pos_h
                                     :                  :
                                     +tens_pos_h        :
                                     :                  :
                                     :                  :
        _____________________________:__________________:_________________
                            aluminum profile where the hodler is attached


    Idler Tensioner attributes:
    ---------------------------
          axis_h
            :
            :                   nut_holder_thick
            :                      + 
            :                     : :nut_space
            :                     : :+
            :                     : : :nut_holder_thick
            :                     : : :+
            :                     : : : :
         ________                 : :_:_:__________________....
        |___::___|                 /      _____     __:_:_|  :
        |    ....|              ..|  _   /     \   /         :    
        |   ()...|    bolttens_d..|:|_|:|       | |          + tens_h
        |________|                |      \_____/   \______   :
        |___::___|...> axis_w      \__________________:_:_|..:..> axis_l
        :        :                :     :       : :       :
        :........:                :     :       : :.......:
            +                     :     :       : :  +    :
         tens_w                   :     :       :.: 2*idler_r_xtr
                                  :     :       :+        :
                                  :     :.......:pulley_stroke_dist
                                  :     :   +             :
      opt_tens_chmf = 0           :.....:  tens_stroke    :
         ________                 :  +                    :
        |___::___|                : nut_holder_total      :
        |  ......|                :                       :
        |  :.....|                :...... tens_l .........:
        |   ::   |
        |........|
        |        |
        |        |
        |........|
        |........|
        |        |
        |   ()   |
        |        |
        |________|
            :
            :
          axis_l


      opt_tens_chmf = 1
         ________.......> axis_w
        /___::___\
        |  ......|
        |  :.....|
        |   ::   |
        |........|
        |        |
            :
            :
          axis_l


     pos_tens0: is at point 0 in the drawing, considering the tensioner all the
                way inside
         ________                    _____________________
        |___::___|                 /      _____     __:_:_|
        |    ....|                |  _   /     \   /             
        |   0....|                0:|_|:|       | |        
        |________|                |      \_____/   \______
        |___::___|                 \__________________:_:_|

  
    """

    def __init__(self,
                 aluprof_w = 30.,
                 belt_pos_h = 30.,
                 wall_thick = 5.,
                 tens_stroke = 20.,
                 pulley_stroke_dist = 0,
                 nut_holder_thick = 4.,
                 in_fillet = 2.,
                 boltaluprof_d = 4.,
                 boltidler_d = 4.,
                 bolttens_d = 4.,
                 hold_bas_h = 4.,
                 tens_in_ratio = 1.,
                 opt_tens_chmf = 1,
                 hold_hole_2sides = 1,
                 axis_l = VX,
                 axis_w = V0,
                 axis_h = VZ,
                 pos_l = 0,
                 pos_w = 0,
                 pos_h = 0,
                 pos = V0,
                 #wfco = 1,
                 name= "tensioner"):

        # bring the active document:
        doc = FreeCAD.ActiveDocument

        # save the arguments as attributes:
        frame = inspect.currentframe()
        args, _, _, values = inspect.getargvalues(frame)
        for i in args:
            setattr(self, i, values[i])
        #for key, value in inspect.getargspec(__init__):
            #setattr(self, key, value)

        # normalize axes:
        # axis_l.normalize() could be used, but would change the vector
        # used as parameter
        axis_l = DraftVecUtils.scaleTo(axis_l,1)
        axis_h = DraftVecUtils.scaleTo(axis_h,1)
        if axis_w == V0:
            axis_w = axis_l.cross(axis_h)
        else:
            axis_w = DraftVecUtils.scaleTo(axis_w,1)
        self.axis_l = axis_l
        self.axis_w = axis_w
        self.axis_h = axis_h

        # placement of the piece at V0, altough pos can set it anywhere
        self.place = V0

        # ---------------------- calculated values:
        if pulley_stroke_dist == 0: # default value
            pulley_stroke_dist = wall_thick
            self.pulley_stroke_dist = pulley_stroke_dist

        # --- idler pulley values
        # dictionary of the bolt for the idler pulley
        d_boltidler = kcomp.D912[boltidler_d]
        self.d_boltidler = d_boltidler
        # the shank radius including tolerance
        self.boltidler_r_tol = d_boltidler['shank_r_tol']
        # the idler group list resulting from this bolt:
        idlerpulley_l = kcomp.idpullmin_dict[boltidler_d]
        self.idlerpulley_l = idlerpulley_l
        self.idler_h = partgroup.getgroupheight(idlerpulley_l)
        self.idler_r = partgroup.getmaxwashdiam(idlerpulley_l)/2.
        self.idler_r_xtr = self.idler_r + 2.  #  +2: a little bit larger
        self.largewasher_thick = partgroup.getmaxwashthick(idlerpulley_l)

        # --- tensioner bolt and nut values
        # dictionary of the bolt tensioner
        d_bolttens = kcomp.D912[bolttens_d]
        self.d_bolttens = d_bolttens
        # the shank radius including tolerance
        self.bolttens_r_tol = d_bolttens['shank_r_tol']
        # dictionary of the nut
        self.d_nuttens = kcomp.D934[bolttens_d]
        self.nut_space = kcomp.NUT_HOLE_MULT_H + self.d_nuttens['l_tol']
        self.nut_holder_total = self.nut_space + 2* self.nut_holder_thick

        # circum diameter of the nut
        self.tensnut_circ_d = self.d_nuttens['circ_d']
        # circum radius of the nut, with tolerance
        self.tensnut_circ_r_tol = self.d_nuttens['circ_r_tol']

        # the apotheme of the nut
        self.tensnut_ap_tol = (self.d_nuttens['a2']+kcomp.STOL)/2.

        # --- bolt to attach to the aluminum profile
        # dictionary of the bolt
        d_boltaluprof = kcomp.D912[boltaluprof_d]
        self.d_boltaluprof = d_boltaluprof
        self.boltaluprof_head_r_tol = d_boltaluprof['head_r_tol']
        self.boltaluprof_r_tol = d_boltaluprof['shank_r_tol']
        self.boltaluprof_head_l = d_boltaluprof['head_l']

        # --- idler tensioner dimensions
        self.tens_h = self.idler_h + 2*wall_thick
        self.tens_l = (  self.nut_holder_total
                       + tens_stroke
                       + 2 * self.idler_r_xtr
                       + pulley_stroke_dist)
        self.tens_w = max(2 * self.idler_r_xtr, self.tensnut_circ_d)

        self.tens_w_tol = self.tens_w + kcomp.TOL
        self.tens_h_tol = self.tens_h + kcomp.TOL

        # vertical distance from the bottom of the base of the tensioner
        self.tens_pos_h = belt_pos_h - wall_thick -self.largewasher_thick 

        #  The part of the tensioner that will be inside
        self.tens_l_inside = self.tens_l - 2 * self.idler_r_xtr

        # --- tensioner holder dimensions
        self.hold_w = self.tens_w + 2*wall_thick
        self.hold_l = self.tens_l_inside + wall_thick
        self.hold_h = self.tens_pos_h + self.tens_h + wall_thick
        # base of the tensioner holder
        self.hold_bas_w = self.hold_w + 2*aluprof_w
        self.hold_bas_l = aluprof_w

        # ------ vectors from the different position points
        # -- pos_l distances:
        # it doesnt depend on how much on the ratio the tensioner is inside
        # it will be moved afterwards. So this is commented
        #        + (1-tens_in_ratio) * tens_stroke)
        # distance along axis_l from point 2 to point 0 (orig)
        dis_l_0to2 = (  self.hold_l
                      + self.idler_r_xtr)
        # -- pos_l vectors:
        l0to = {0 : V0} #l0to[0] = V0 # no distance from 0 to 0
        # vector along axis l from 0 to 1:
        # use scale and not scaleTo because is equivalent since vectors length
        # is 1, and scale is simpler to calculate
        l0to[1] = DraftVecUtils.scale(axis_l, self.hold_bas_l/2.)
        # vector from point 3 along axis_l to orig (point 1)
        l0to[2] = DraftVecUtils.scale(axis_l, dis_l_0to2)

        # -- pos_w distances:
        # depends also on how much on the ratio the tensioner is inside
        dis_w_0to1 = self.hold_w/2. + aluprof_w/2.
        dis_w_0to2 = self.hold_w/2. + aluprof_w
        # -- pos_w vectors:
        w0to = {}
        w0to[0] = V0
        # vector along axis w from 0 to 1:
        w0to[1] = DraftVecUtils.scale(axis_w, dis_w_0to1)
        w0to[2] = DraftVecUtils.scale(axis_w, dis_w_0to2)

        # -- pos_h distances:
        dis_h_2to3 = (self.idler_h - self.largewasher_thick) /2.
        dis_h_0to2 = self.belt_pos_h
        dis_h_0to3 = dis_h_0to2 + dis_h_2to3
        # -- pos_h vectors:
        h0to = {}
        h0to[0] = V0
        h0to[1] = DraftVecUtils.scale(axis_h,self.tens_pos_h)
        h0to[2] = DraftVecUtils.scale(axis_h,dis_h_0to2)
        h0to[3] = DraftVecUtils.scale(axis_h,dis_h_0to3)
        #self.h0to = h0to

        # ------ position of the origin. Point: pos_l = 0, pos_w = 0, pos_h = 0
        # pos is the position of a point, the point depends on the 
        # values of pos_l, pos_w, pos_h
        # use negative because the vectors are from 0 to (pos_l, pos_w, pos_h)
        #pos0 = pos + DraftVecUtils.neg(l0to[pos_l] + w0to[pos_w] + h0to[pos_h])
        pos0 = pos + (l0to[pos_l] + w0to[pos_w] + h0to[pos_h]).negative()
        self.pos0 = pos0

        # position of the origin of the tensioner
        self.vh_0to_tens0 = DraftVecUtils.scale(axis_h,
                                                self.tens_pos_h + self.tens_h/2)
        self.vl_0to_tens0 = DraftVecUtils.scale(axis_l, wall_thick)
        self.pos_tens0 = pos + self.vl_0to_tens0 + self.vh_0to_tens0 
        

        # these 3 list are synchronized in their indexes, so the index
        # refers to the same object in the 3 lists
        self.fco_l = []   # list of freecad objects of this class
        self.name_l = []   # list of names (prefixes) of the pieces
        # list of positions of the origin of the different parts
        self.pos0_l = []
        self.prnt_ax_l = []   # list of FreeCAD.Vector axes to print

        # tensioner holder
        fco_tens_hold = self.tensioner_holder()
        self.fco_l.append(fco_tens_hold)  # add to the FreeCAD object list
        self.name_l.append('tensioner_holder')
        self.pos0_l.append(pos0)
        self.prnt_ax_l.append(self.prnt_ax_tens_hold) # axis to print

        fco_idl_tens = self.idler_tensioner()
        self.fco_l.append(fco_idl_tens)  # add to the FreeCAD object list
        self.name_l.append('idler_tensioner')
        self.pos0_l.append(self.pos_tens0)
        self.prnt_ax_l.append(self.prnt_ax_idl_tens) # axis to print

        self.set_pos_tensioner() # set the position of the tensioner


    # ---------------------------------------------------------
    # -------------------- tensioner holder -------------------
    # ---------------------------------------------------------
    def tensioner_holder(self):
        """ Creates the tensioner holder shape and FreeCAD object
        Returns the FreeCAD object created
        """
        # bring the active document
        doc = FreeCAD.ActiveDocument

        # --------------- step 01 --------------------------- 
        #    the base, to attach it to the aluminum profiles
        #    
        #
        #                         axis_h                axis_h
        #                            :                  :
        #              .. ___________:___________       :________
        #  hold_bas_h.+..|___________:___________|      |________|...axis_l
        #
        #                 .... hold_bas_w ........
        #                :                        :
        #                :________________________:......axis_w
        #                |           :            |    :
        #                |           :            |    + hold_bas_l
        #                |___________:____________|....:
        #                            :            :
        #                          axis_l
        shp01 = fcfun.shp_box_dir(box_w = self.hold_bas_w,
                                  box_d = self.hold_bas_l,
                                  box_h = self.hold_bas_h,
                                  fc_axis_h = self.axis_h,
                                  fc_axis_d = self.axis_l,
                                  cw=1, cd=0, ch=0, pos=self.pos0)
        #    --------------- step 02 --------------------------- 
        #    Fillet the base
        #    The piece will be printed on the h w plane, so this fillet will be 
        #    raising
        #  
        #                          axis_h
        #                             :
        #                f4___________:___________f2
        #                 (_______________________)... axis_w
        #                f3                        f1
        #
        bas_fil_r = self.in_fillet
        if self.hold_bas_h/2. <= self.in_fillet:
            logger.debug("Radius of holder base fillet is larger than")
            logger.debug("2 x base height, making fillet smaller")
            bas_fil_r = self.hold_bas_h /2. - 0.1
        # fillet along axis_l :
        shp02 = fcfun.shp_filletchamfer_dir (shp=shp01, fc_axis=self.axis_l,
                                            fillet = 1, radius=bas_fil_r)
        #    --------------- step 03 --------------------------- 
        #    The main box
        #                          axis_h              axis_h
        #                             :    aluprof_w     :
        #                             :    ..+....       :
        #           .............. ___:___:       :      :____________
        #           :             |       |       :      |            |
        #           :             |       |       :      |            |
        #   hold_h +:             |       |       :      |            |
        #           :             |       |       :      |            |     
        #           :      _______|       |_______:      |________    |
        #           :.....(_______|_______|_______)      |________|___|...axis_l
        #                                                :            :
        #                  .... hold_bas_w ........      :.. hold_l...:
        #                 :                        :
        #                 :        .hold_w.        :
        #                 :       :       :        :
        #                 :_______:_______:________:.......axis_w
        #                 |       |       |        |    :
        #                 |       |       |        |    + hold_bas_l
        #                 |_______|       |________|....:
        #                         |       |
        #                         |_______|
        #                             :
        #                             :
        #                           axis_l 

        shp03 = fcfun.shp_box_dir(box_w = self.hold_w,
                                  box_d = self.hold_l,
                                  box_h = self.hold_h,
                                  fc_axis_h = self.axis_h,
                                  fc_axis_d = self.axis_l,
                                  cw=1, cd=0, ch=0, pos=self.pos0)
        #    --------------- step 04 --------------------------- 
        #    Fillets on top
        #                          axis_h   aluprof_w
        #                             :    ..+....:
        #           ............. C___A___B       : 
        #           :             /       \       :
        #           :             |       |       :
        #   hold_h +:             |       |       :
        #           :             |       |       :
        #           :      _______|       |_______:
        #           :.....(_______|_______|_______).... axis_w
    
        #                 :_______C___A___B________:.......axis_w
        #                 |       |       |        |    :
        #                 |       |       |        |    + hold_bas_l
        #                 |_______|       |________|....:
        #                         |       |
        #                         |_______|

        # fillet along axis_l and the vertex should contain points B and C
        # point A:
        pt_a = self.pos0 + DraftVecUtils.scale(self.axis_h, self.hold_h)
        # list containing points B and C
        pts_list = [pt_a + DraftVecUtils.scale(self.axis_w, self.hold_w/2.),
                    pt_a + DraftVecUtils.scale(self.axis_w, -self.hold_w/2.)]
        shp04 = fcfun.shp_filletchamfer_dirpts (shp=shp03,
                                                fc_axis=self.axis_l,
                                                fc_pts=pts_list,
                                                fillet = 1,
                                                radius=self.in_fillet)
        #    --------------- step 05 --------------------------- 
        #    large chamfer at the bottom

        #                axis_h                 axis_h
        #                  :                      :
        #   Option A    ___:___                   :____________
        #              /       \                  |            |
        #              |       |                  |            |
        #              |_______|                  |            |
        #              |       |                  |           /       
        #       _______|_______|_______           |________ /  
        #      (___________C___________)..axis_w  |________|...C...axis_l

        #  
        #               axis_h                 axis_h
        #                  :                      :
        #   Option B    ___:___                   :____________
        #              /       \                  |            |
        #              |       |                  |            |
        #              |       |                  |            |
        #              |_______|                  |            |      
        #       _______|       |_______           |________   /  
        #      (_______|___C___|_______)..axis_w  |________|/..C...axis_l
        #                                         :            :
        #                                         :............:
        #                                               +  
        #                                             hold_l
        #
        # option B: using more material (probably sturdier)
        #chmf_rad = min(self.hold_l - self.hold_bas_l,
        #               self.hold_h - (self.tens_h + 2*self.wall_thick))
        # option A: using less material
        chmf_rad = min(self.hold_l-self.hold_bas_l + self.hold_bas_h,
                       self.hold_h - (self.tens_h + 2*self.wall_thick))
        # Find a point along the vertex that is going to be chamfered.
        # See drawings: Point C:
        pt_c = self.pos0 + DraftVecUtils.scale(self.axis_l, self.hold_l)
        
        shp05 = fcfun.shp_filletchamfer_dirpt (shp = shp04,
                                               fc_axis = self.axis_w,
                                               fc_pt = pt_c,
                                               fillet = 0,
                                               radius = chmf_rad)

        #    --------------- step 06 --------------------------- 
        #    Hole for the tensioner
        #                                             axis_h
        #                                                :
        #                                                : tensioner_inside
        #                        axis_h                  :  ....+.....
        #                       ___:___                  :_:__________:
        #                      /  ___  \                 |  ..........|
        #                      | | A | |                 | A          |
        #            ..........| |___| |                 | :..........|
        # tens_pos_h +         |_______|                 |            |      
        #            :  _______|       |_______          |________   /  
        #            :.(_______|_______|_______).axis_w  |________|/....axis_l
        #                                                : :          :
        #                                                :+           :
        #                                                :wall_thick  :
        #                                                :            :
        #                                                :............:
        #                                                      +
        #                                                    hold_l
        #

        # position of point A is pos_tens0
        if self.opt_tens_chmf == 0: # no optional chamfer, only along axis_w
            edge_dir = self.axis_w
        else:
            edge_dir = V0
   
        shp06 = fcfun.shp_boxdir_fillchmfplane(
                               box_w = self.tens_w,
                               box_d = self.hold_l,
                               box_h = self.tens_h,
                               axis_d = self.axis_l,
                               axis_h = self.axis_h,
                               cd=0, cw=1, ch=1,
                               xtr_w = kcomp.TOL/2.,  #tolerances on each side
                               xtr_nw = kcomp.TOL/2.,
                               xtr_h = kcomp.TOL/2.,
                               xtr_nh = kcomp.TOL/2.,
                               fillet = 0, # chamfer
                               radius = 2*self.in_fillet-kcomp.TOL,
                               plane_fill = self.axis_l.negative(),
                               both_planes = 0,
                               edge_dir = edge_dir,
                               pos = self.pos_tens0)
        #    --------------- step 07 --------------------------- 
        #    A hole to be able to see inside, could be on one side or both
        #
        #    hold_hole_2sides = 1:
        #              axis_h                   axis_h
        #                :                        :
        #             ___:___                     :____________
        #            /  ___  \                    |  ._______ .|
        #            |:|   |:|                    | :|_______| |
        #            | |___| |                    |  ..........|
        #            |_______|                    |            |      
        #     _______|       |_______             |________   /  
        #    (_______|_______|_______)..>axis_w   |________|/......>axis_l
        #
        #    hold_hole_2sides = 0:
        #              axis_h                   axis_h
        #                :                        :
        #             ___:___                     :____________
        #            /  ___  \                    |  ._______ .|
        #            7:|   | |<-Not a hole here   | :7_______| |
        #            | |___| |                    |  ..........|
        #            |_______|                    |            |      
        #     _______|       |_______             |________   /  
        #    (_______|_______|_______)..>axis_w   |________|/......>axis_l

        if self.hold_hole_2sides == 1:
            hold_hole_w = self.hold_w
        else:
            hold_hole_w = self.wall_thick
        # position of point 7:
        # height of point 7, is the center of the tensioner:
        pos07 = (  self.pos_tens0
                 + DraftVecUtils.scale(self.axis_l, self.nut_holder_thick)
                 + DraftVecUtils.scale(self.axis_w, -self.hold_w/2.))
        shp07 = fcfun.shp_box_dir_xtr (
                                       box_w = hold_hole_w,
                                       box_d =  self.hold_l
                                              - self.nut_holder_thick
                                              - 2*self.wall_thick,
                                       box_h = 2*self.tensnut_ap_tol,
                                       fc_axis_h = self.axis_h,
                                       fc_axis_d = self.axis_l,
                                       fc_axis_w = self.axis_w,
                                       ch = 1, cd = 0, cw = 0,
                                       xtr_w = 1, xtr_nw = 1,
                                       pos=pos07)
        # /* --------------- step 08 --------------------------- 
        #    A hole for the leadscrew
        #            axis_h             axis_h
        #              :                  :
        #           ___:___               :____________
        #          /  ___  \              |  ._______ .|
        #          |:| O |:|              |::|_______| |
        #          | |___| |              |  ..........|
        #          |_______|              |            |      
        #   _______|       |_______       |________   /  
        #  (_______|_______|_______)      |________|/......> axis_l
        #
        shp08 = fcfun.shp_cylcenxtr (r = self.bolttens_r_tol,
                                     h = self.wall_thick,
                                     normal = self.axis_l.negative(),
                                     ch = 0, xtr_top=1, xtr_bot=1,
                                     pos = self.pos_tens0)
        #    --------------- step 09 --------------------------- 
        #    09a: Fuse all the elements to cut
        #    09b: Cut the box with the elements to cut
        #    09c: Fuse the base with the holder
        #    09d: chamfer the union
        #            axis_h           axis_h
        #              :               :
        #           ___:___            :____________
        #          /  ___  \           |  ._______ .|
        #          |:| O |:|           |::|_______| |...
        #         /| |___| |\          |  ..........|...tens_h/2 -tensnut_ap_tol
        #        / |_______| \         |            |  :+tens_pos_h
        #   ____/__A   C   B__\____    A________   /   :  ...
        #  (_______|_______|_______)   |________|/.....:.....hold_bas_h
        #
        shp09a = fcfun.fuseshplist([shp06, shp07, shp08])
        shp09b = shp05.cut(shp09a)
        shp09c = shp09b.fuse(shp02) # fuse with the base
        shp09c = shp09c.removeSplitter() # refine shape
 
        # chamfer the union, points A and B:
        # Radius of chamfer
        chmf_rad = min(self.aluprof_w/2,
                         self.tens_pos_h + self.tens_h/2
                       - self.tensnut_ap_tol - self.hold_bas_h);
        # first point C:
        pt_c = self.pos0 + DraftVecUtils.scale(self.axis_h, self.hold_bas_h)
        pt_a = pt_c + DraftVecUtils.scale(self.axis_w,-self.hold_w/2.)
        pt_b = pt_c + DraftVecUtils.scale(self.axis_w, self.hold_w/2.)
        shp09d = fcfun.shp_filletchamfer_dirpts (shp=shp09c,
                                                 fc_axis=self.axis_l,
                                                 fc_pts=[pt_a,pt_b],
                                                 fillet = 0,
                                                 radius=chmf_rad)
        shp09d = shp09d.removeSplitter() # refine shape

        #    --------------- step 10 --------------------------- 
        #    Bolt holes to attach the piece to the aluminum profile
        #                                
        #             axis_h            axis_h
        #            ___:___              :____________
        #           /  ___  \             |  ._______ .|
        #           |:| O |:|             |::|_______| |
        #          /| |___| |\            |  ..........|
        #         / |_______| \           |            |
        #    ____/__|       |__\____      |________   /
        #   (__:A___|___C___|___B:__)     |___::___|/....axis_l
        #
        #             hold_w   aluprof_w
        #            ...+... ...+...
        #    _______:_______:_______:.......axis_w
        #   |       |       |       |    :
        #   |   A   |   C   |   B   |    + hold_bas_l
        #   |_______|       |_______|....:
        #           |       |   :
        #           |_______|   :
        #               :       :
        #               :.......:
        #                   +
        #               (hold_w+aluprof_w)/2

        # first get the position of point C
        pt_c = self.pos0 + DraftVecUtils.scale(self.axis_l, self.hold_bas_l/2.)
        # distance C - A
        dis_w_0to_alubolt = (self.hold_w + self.aluprof_w)/2.

 
        shp_bolt_list = []
        for sign in [-1,1]:
            pt_i = pt_c + DraftVecUtils.scale(self.axis_w,
                                              sign * dis_w_0to_alubolt)
            shp_i = fcfun.shp_bolt_dir(
                         r_shank = self.boltaluprof_r_tol,
                         l_bolt = self.hold_bas_h + self.boltaluprof_head_r_tol,
                         r_head = self.boltaluprof_head_r_tol,
                         l_head = self.boltaluprof_head_l,
                         xtr_head = 1, xtr_shank = 1,
                         support = 0,
                         fc_normal = self.axis_h.negative(),
                         pos_n = 2, #at the end of the shank
                         pos = pt_i)
            shp_bolt_list.append(shp_i)
        shp10_bolts = fcfun.fuseshplist(shp_bolt_list)
        shp10_final = shp09d.cut(shp10_bolts)
        shp10_final = shp10_final.removeSplitter()

        self.shp_tens_hold = shp10_final

        # --- FreeCAD object creation
        fco = doc.addObject("Part::Feature", self.name + '_holder' )
        fco.Shape = shp10_final
        self.fco_tens_hold = fco
        # normal axes to print without support
        self.prnt_ax_tens_hold = self.axis_l
        return fco

    # ---------------------------------------------------------
    # -------------------- idler pulley tensioner -------------
    # ---------------------------------------------------------
    def idler_tensioner(self):
        """ Creates the idler pulley tensioner shape and FreeCAD object
        Returns the FreeCAD object created

                           nut_space 
                           .+..
                           :  :
           nut_holder_thick:  :nut_holder_thick
                          +:  :+
                         : :  : :    pulley_stroke_dist
               :         : :  : :       .+.  2*idler_r_xtr
               :         : :  : :      :  :...+....
               :         : :  : :      :  :       :
            ________     : :__:_:______:__:_______:.................
           |___::___|     /      ______   ___::___|.....+wall_thick :
           |    ....|    |  __  |      | |            :             + tens_h
           |   ()...|    |:|  |:|      | |            + idler_h     :
           |________|    |  --  |______| |________....:             :
           |___::___|     \__________________::___|.................:
           :        :    :      :      :          :
           :........:    :      :...+..:          :
               +         :......:  tens_stroke    :
             tens_w      :  +                     :
        (2*idler_r_xtr)  : nut_holder_tot         :
                         :                        :
                         :.........tens_l.........:


        """
        # bring the active document
        doc = FreeCAD.ActiveDocument


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
        #     0: shows the position of pos_tens0
        #
        #                axis_h       axis_h
        #                  :            :
        #         .... ____:____        : ______________________
        #         :   |.........|     ch2/                      |
        #         :   |:       :|       |                       |      
        #  tens_h +   |:   0   :|       0                       |-----> axis_l
        #         :   |:.......:|       |                       |
        #         :...|_________|     ch1\______________________|
        #             :         :       :                       :
        #             :.tens_h..:       :...... tens_l .........:
        #
        #              ____0____ ....> axis_w
        #          ch3/_________\ch4
        #             |         |          chamfer ch3 and ch4 are optional
        #             |         |          Depend on opt_tens_chmf
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
        #                 axis_l

        if self.opt_tens_chmf == 0: # no optional chamfer, only along axis_w
            edge_dir = self.axis_w
        else:
            edge_dir = V0
   
        shp01chmf = fcfun.shp_boxdir_fillchmfplane(
                               box_w = self.tens_w,
                               box_d = self.tens_l,
                               box_h = self.tens_h,
                               axis_d = self.axis_l,
                               axis_h = self.axis_h,
                               cd=0, cw=1, ch=1,
                               # no tolerances, this is the piece
                               fillet = 0, # chamfer
                               radius = 2*self.in_fillet,
                               plane_fill = self.axis_l.negative(),
                               both_planes = 0,
                               edge_dir = edge_dir,
                               pos = self.pos_tens0)
        #  --------------- step 02 ---------------------------  
        # Space for the idler pulley
        #    axis_h
        #      :
        #      :_______________________
        #      |                 ______|....
        #      |                /          + idler_h
        #      |               |       2   :----------->axis_l
        #      |                \______....:
        #      |_______________________|...wall_thick
        #                      :       :
        #                      :.......:
        #                         +
        #                       2 * idler_r_xtr
        #
        # pos02 is at the end, and the box will be drawn along axis_l.negative()
        pos02 = self.pos_tens0 + DraftVecUtils.scale(self.axis_l, self.tens_l)
        # maybe should be advisable to have tolerance, but usually, the 
        # washers have tolerances, and usually are less thick than the nominal
        idler_h_hole =  self.idler_h # + kcomp.TOL
        shp02cut = fcfun.shp_boxdir_fillchmfplane(
                               box_w = self.tens_w,
                               box_d = 2*self.idler_r_xtr,
                               box_h = idler_h_hole,
                               axis_d = self.axis_l.negative(),
                               axis_h = self.axis_h,
                               cd=0, cw=1, ch=1,
                               xtr_w = 1,
                               xtr_nw = 1,
                               xtr_nd = 1, # extra along axis_l (positive)
                               fillet = 0, # chamfer
                               radius = self.in_fillet,
                               plane_fill = self.axis_l.negative(),
                               both_planes = 0,
                               edge_dir = self.axis_w,
                               pos = pos02)
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
        #      |               |       2    ------> axis_l
        #      |                \______f3...
        #      |_______________________|....+ wall_thick.....> Y
        #      :                       f1
        #      :...... tens_l .........:
        #
        pt_f1 = pos02 + DraftVecUtils.scale(self.axis_h, -self.tens_h/2.)
        pt_f2 = pos02 + DraftVecUtils.scale(self.axis_h,  self.tens_h/2.)
        pt_f3 = pos02 + DraftVecUtils.scale(self.axis_h, -idler_h_hole/2.)
        pt_f4 = pos02 + DraftVecUtils.scale(self.axis_h,  idler_h_hole/2.)
        shp03 = fcfun.shp_filletchamfer_dirpts (
                                            shp=shp02,
                                            fc_axis=self.axis_w,
                                            fc_pts=[pt_f1,pt_f2, pt_f3, pt_f4],
                                            fillet = 1,
                                            radius=self.in_fillet)
        #  --------------- step 04 done at step 01 ------------------------ 

        #  --------------- step 05 --------------------------- 
        # Shank hole for the idler pulley:

        #    axis_h                  idler_r_xtr
        #      :                    .+..
        #      : ___________________:__:
        #       /                __:_:_|
        #      |                /             
        #      |               |        ----------> axis_l
        #      |                \______
        #       \__________________:_:_|
        #      :                       :
        #      :...... tens_l .........:
        #                     
        pos05 = (self.pos_tens0 + DraftVecUtils.scale(self.axis_l,
                                      self.tens_l-self.idler_r_xtr))
        shp05 = fcfun.shp_cylcenxtr (r = self.boltidler_r_tol,
                                     h = self.tens_h,
                                     normal = self.axis_h,
                                     ch = 1, xtr_top = 1, xtr_bot = 1,
                                     pos = pos05)
        #  --------------- step 06 --------------------------- 
        # Hole for the leadscrew (stroke):

        #    axis_h
        #      :
        #      : ______________________
        #       /      _____     __:_:_|
        #      |    f2/     \f4 /             
        #      |     |       | |        -------> axis_l
        #      |    f1\_____/f3 \______
        #       \__________________:_:_|
        #      :     :       :         :
        #      :     :.......:         :
        #      :     :   +             :
        #      :.....:  tens_stroke    :
        #      :  +                    :
        #      : nut_holder_total      :
        #      :                       :
        #      :...... tens_l .........:
        # 
        pos06 = (self.pos_tens0 + DraftVecUtils.scale(self.axis_l,
                                            self.nut_holder_total))
        shp06a = fcfun.shp_box_dir_xtr(box_w = self.tens_w,
                                       box_d = self.tens_stroke,
                                       box_h = self.idler_h,
                                       fc_axis_h = self.axis_h,
                                       fc_axis_d = self.axis_l,
                                       xtr_w = 1, xtr_nw = 1,
                                       cw=1, cd=0, ch=1, pos=pos06)
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
        #      |:::::|       | |        ---->axis_l
        #      |      \_____/   \______
        #       \__________________:_:_|
        #      :     :                 :
        #      :     :                 :
        #      :     :                 :
        #      :.....:                 :
        #      :  +                    :
        #      : nut_holder_total      :
        #      :                       :
        #      :...... tens_l .........:
        #
        shp07 = fcfun.shp_cylcenxtr (r = self.bolttens_r_tol,
                                     h = self.nut_holder_total,
                                     normal = self.axis_l,
                                     ch = 0, xtr_top = 1, xtr_bot = 1,
                                     pos = self.pos_tens0)
        #  --------------- step 08 --------------------------- 
        # Hole for the leadscrew nut

        #    axis_h
        #      :
        #      : ______________________
        #       /      _____     __:_:_|
        #      |  _   /     \   /
        #      |:|_|:|       | |       -----> axis_l
        #      |      \_____/   \______
        #       \__________________:_:_|
        #      : :   :                 :
        #      :+    :                 :
        #      :nut_holder_thick       :
        #      :.....:                 :
        #      :  +                    :
        #      : nut_holder_total      :
        #      :                       :
        #      :...... tens_l .........:

        pos08 = (self.pos_tens0 + DraftVecUtils.scale(self.axis_l,
                                           self.nut_holder_thick))
        shp08 = fcfun.shp_nuthole (
                               nut_r = self.tensnut_circ_r_tol,
                               nut_h = self.nut_space,
                               hole_h = self.tens_w/2,
                               xtr_nut = 1, xtr_hole = 1, 
                               fc_axis_nut = self.axis_l,
                               fc_axis_hole = self.axis_w,
                               ref_nut_ax = 2, # pos not centered on axis nut 
                               # pos at center of nut on axis hole 
                               ref_hole_ax = 1, 
                               pos = pos08)

        # --------- step 09:
        # --------- Last step, union and cut of the steps 05, 06, 07, 08
        shp09cut = fcfun.fuseshplist([shp05, shp06, shp07, shp08])
        shp09_final = shp03.cut(shp09cut)

        self.shp_idl_tens = shp09_final

        # --- FreeCAD object creation
        fco = doc.addObject("Part::Feature", 'idler_' + self.name)
        fco.Shape = shp09_final
        self.fco_idl_tens = fco
        # normal axes to print without support
        self.prnt_ax_idl_tens = self.axis_w
        return fco

    # ---------------------------------------------------------
    # -------------------- Other methods ----------------------
    # ---------------------------------------------------------
    # ----- 
    def set_pos_tensioner (self, new_tens_in_ratio = None):
        """ Sets the tensioner place, depending on the attributes tens_in_ratio
        and tens_stroke
        Parameters:
        -----------
        new_tens_in_ratio : float [0,1]
            ratio of the tensioner that is inside.
            It can be any value from 0 to 1
            0: maximum value outside (tens_stroke)
            1: all the way inside
        """
        if new_tens_in_ratio is not None:
            # set the new tens_in_ratio
            self.tens_in_ratio = new_tens_in_ratio
        tens_out = (1-self.tens_in_ratio) * self.tens_stroke
        self.fco_idl_tens.Placement.Base = (self.place + 
                                   DraftVecUtils.scale(self.axis_l, tens_out))


    # ----- 
    def set_color (self, color = (1.,1.,1.), part_i = 0):
        """ Sets a new color for the whole set of pieces or for the selected
        pieces

        Parameters:
        -----------
        color : tuple of 3 floats from 0. to 1.
            RGB colors
        part_i : int
            index of the piece to change the color
            0: all the pieces
            1: the tensioner holder
            2: the idler tensioner
            3: the idler pulley

        """
        # just in case the value is 0 or 1, and it is an int
        color = (float(color[0]),float(color[1]), float(color[2]))
        if part_i == 0:
            self.color = color #only if all the pieces have the same color
            for fco_i in self.fco_l:
                fco_i.ViewObject.ShapeColor = color
        else:
            self.fco_l[part_i-1].ViewObject.ShapeColor = color

    # ----- 
    def set_place (self, place = V0):
        """ Sets a new placement for the whole set of pieces

        Parameters:
        -----------

        place : FreeCAD.Vector
            new position of the pieces
        """
        if type(place) is tuple:
            place = FreeCAD.Vector(place) # change to FreeCAD.Vector
        if type(place) is FreeCAD.Vector:
            # set the new position for every freecad object
            for fco_i in self.fco_l:
                fco_i.Placement.Base = place
            self.place = place
            # set the position of the tensioner
            self.set_pos_tensioner()

    # ----- Export to STL method
    def export_stl(self, part_i = 0, name = "set_"):
        """ exports to stl the piece or the pieces to print
        Save them in a STL file

        Parameters:

        part_i : int
            index of the piece to print
            0: all the printable pieces
            1: the tensioner holder
            2: the idler tensioner

        name : str
            Name or prefix of the piece
        """

        doc = FreeCAD.ActiveDocument
        if part_i == 0:
            for fco_i, name_i, prnt_ax_i in zip(self.fco_l, self.name_l,
                                                self.prnt_ax_l):
                rotation = fcfun.get_rot(prnt_ax_i, VZ)
                shp = fco_i.Shape
                shp.Placement.Base = self.pos.negative() + self.place.negative()
                shp.Placement.Rotation = rotation
                Part.show(shp)
                shp.Placement.Base = self.pos + self.place
                shp.Placement.Rotation = fcfun.V0ROT
        else:
            fco_i = self.fco_l[part_i - 1]
            prnt_ax_i = self.prnt_ax_l[part_i - 1]
            name_i = name + self.name_l[part_i - 1]
            pos0_i = self.pos0_l[part_i - 1]
            rotation = FreeCAD.Rotation(prnt_ax_i, VZ)
            shp = fco_i.Shape
            # ----------- moving the shape doesnt work:
            # I think that is because it is bound to a FreeCAD object
            #shp.Placement.Base = self.pos.negative() + self.place.negative()
            #shp.translate (self.pos.negative() + self.place.negative())
            #shp.rotate (V0, rotation.Axis, math.degrees(rotation.Angle))
            #shp.Placement.Base = self.place
            #shp.Placement.Rotation = fcfun.V0ROT
            # ----------- option 1. making a copy of the shape
            # and then deleting it (nullify)
            #shp_cpy = shp.copy()
            #shp_cpy.translate (pos0_i.negative() + self.place.negative())
            #shp_cpy.rotate (V0, rotation.Axis, math.degrees(rotation.Angle))
            #shp_cpy.exportStl(stl_path + name_i + 'shp.stl')
            #shp_cpy.nullify()
            # ----------- option 2. moving the freecad object
            fco_i.Placement.Base = pos0_i.negative() + self.place.negative()
            fco_i.Placement.Rotation = rotation
            doc.recompute()
            # exportStl is not working well with FreeCAD 0.17
            #fco_i.Shape.exportStl(stl_path + name_i + '.stl')
            mesh_shp = MeshPart.meshFromShape(shp,
                                             LinearDeflection=kparts.LIN_DEFL, 
                                             AngularDeflection=kparts.ANG_DEFL)
            mesh_shp.write(stl_path + name_i + '.stl')
            del mesh_shp
            fco_i.Placement.Base = self.place
            fco_i.Placement.Rotation = V0ROT
            self.set_pos_tensioner() # position of the tensioner
            doc.recompute()

    def save_fcad(self, name = "tensioner_set"):
        """ Save the FreeCAD document

        Parameters:
        -----------
        name : str
            if name = '' then it will take self.name

        """
        doc = FreeCAD.ActiveDocument
        if name:  
            name = name
        else: # if name == '' 
            name = self.name
        fcad_filename = fcad_path + name + '.FCStd'
        print fcad_filename
        doc.saveAs (fcad_filename)


"""
IDLER_TENS = { 'boltidler_d' : boltidler_d,
               'wall_thick' : wall_thick,
               'tens_stroke' : tens_stroke,
               'pulley_stroke_dist' : pulley_stroke_dist,
               'nut_holder_thick' : nut_holder_thick,
               'bolttens_d' : bolttens_d,
               'nut_space' : nut_space,
               'in_fillet' : 2.
              }
"""
               



doc = FreeCAD.newDocument()
h = Tensioner(axis_l=VX, axis_h = VZ, pos=FreeCAD.Vector(0,0,0))
h.set_color(fcfun.LSKYBLUE,1) #tensioner holder light sky blue
h.set_color(fcfun.ORANGE,2) #idler tensioner orange
h.set_pos_tensioner(0.5) # have the tensioner half way out
h.export_stl(1) # export the tensioner holder to STL
h.export_stl(2) # export the idler tensioner to STL
h.save_fcad() # save FreeCAD document


