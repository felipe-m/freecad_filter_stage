# ----------------------------------------------------------------------------
# -- Group of idler tensioner and its holder
# ----------------------------------------------------------------------------
# -- (c) Felipe Machado
# -- Area of Electronic Technology. Rey Juan Carlos University (urjc.es)
# -- https://github.com/felipe-m/freecad_filter_stage
# -- December-2017
# ----------------------------------------------------------------------------
# --- LGPL Licence
# ----------------------------------------------------------------------------


#                        fc_axis_h            fc_axis_h 
#                            :                  :
# ....................... ___:___               :______________
# :                      |  ___  |     pos_h:   |  __________  |---
# :                      | |   | |        3     | |__________| | : |
# :+hold_h              /| |___| |\       1,2   |________      |---
# :                    / |_______| \            |        |    /      
# :             . ____/  |       |  \____       |________|  /
# :..hold_bas_h:.|_::____|_______|____::_|0     |___::___|/......fc_axis_l
#                                               0    1           2: pos_l
#
#
#
#                 .... hold_bas_w ........
#                :        .hold_w.        :
#              aluprof_w :    wall_thick  :
#                :..+....:      +         :
#                :       :     : :        :
#       pos_w:   2__1____:___0_:_:________:........fc_axis_w
#                |    |  | :   : |  |     |    :
#                |  O |  | :   : |  |  O  |    + hold_bas_l
#                |____|__| :   : |__|_____|....:
#                        | :   : |
#                        |_:___:_|
#                          |   |
#                           \_/
#                            :
#                            :
#                        fc_axis_l

# the group is referenced on 3 perpendicular axis:
# - fc_axis_l: length
# - fc_axis_w: width
# - fc_axis_h: height
# There is a position of the piece:
# - that can be in a different point

import os
import sys
import inspect
import logging
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
sys.path.append(filepath + '/' + 'comps')
#sys.path.append(filepath + '/../../' + 'comps')

import kcomp   # import material constants and other constants
import fcfun   # import my functions for freecad. FreeCad Functions
import comps   # import my CAD components
import partgroup 

from fcfun import V0, VX, VY, VZ, V0ROT
from fcfun import VXN, VYN, VZN

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class Tensioner (object):
    """
    Creates a belt tensioner group:
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
    :..hold_bas_h:.|_::____|_______|____::_|0     |___::___|/......>fc_axis_l
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

    The group is referenced along 3 perpendicular axis
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
        length vector of coordenate system
    axis_w : FreeCAD.Vector
        width vector of coordenate system
        if V0: it will be calculated using the cross product: axis_h x axis_w
    axis_h : FreeCAD.Vector
        height vector of coordenate system
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
    vh_0to_tens_cen: FreeCAD.Vector
        Vector along axis_h from the base to the center of the tensioner
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
        |:|  |:|      | ||_______|.......................bottom side of small
        |  --  |______| |_======_                       :  washer just below
         \__________________::___|.: wall_thick         :  the bearing
                                     :                  :
                                     :                  + belt_pos_h
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
                 wfco = 1,
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
            axis_w = axis_h.cross(axis_l)
        else:
            axis_w = DraftVecUtils.scaleTo(axis_w,1)
        self.axis_l = axis_l
        self.axis_w = axis_w
        self.axis_h = axis_h

        # ---------------------- calculated values:
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
        self.tens_w = 2 * self.idler_r_xtr 

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
        # it will be moved afterwards. So this will be commented
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

        self.tensioner_holder()

        # normal axes to print
        self.tens_axis_prn = axis_w # for the idler tensioner
        self.hold_axis_prn = axis_l # for the tensioner holder

    # -------------------- tensioner holder -------------------
    def tensioner_holder(self):
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
        print self.in_fillet
        bas_fil_r = self.in_fillet
        if self.hold_bas_h/2. <= self.in_fillet:
            logger.warning("Radius of holder base fillet is larger than")
            logger.warning("2 x base height, making fillet smaller")
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
        #                      | |   | |                 | :          |
        #            ..........| |_A_| |                 | A..........|
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

        # position of point A:
        pos06 = (  self.pos0
                 + DraftVecUtils.scale(self.axis_l,
                                       self.hold_l-self.tens_l_inside)
                 #+ self.h0to[1]):
                 + DraftVecUtils.scale(self.axis_h, self.tens_pos_h))
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
                               cd = 0, ch=0,
                               xtr_w = kcomp.TOL/2.,  #tolerances on each side
                               xtr_nw = kcomp.TOL/2.,
                               xtr_h = kcomp.TOL/2.,
                               xtr_nh = kcomp.TOL/2.,
                               fillet = 0, # chamfer
                               radius = 2*self.in_fillet-kcomp.TOL,
                               plane_fill = self.axis_l.negative(),
                               both_planes = 0,
                               edge_dir = edge_dir,
                               pos = pos06)
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
        vh_0to_tens_cen = DraftVecUtils.scale(self.axis_h,
                                              self.tens_pos_h + self.tens_h/2)
        self.vh_0to_tens_cen = vh_0to_tens_cen
        pos07 = (  self.pos0
                 + DraftVecUtils.scale(self.axis_l,
                                       self.wall_thick + self.nut_holder_thick)
                 + DraftVecUtils.scale(self.axis_w, -self.hold_w/2.)
                 # vector along h from base to tensioner center:
                 + vh_0to_tens_cen)
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
        pos08 = self.pos0 + vh_0to_tens_cen
        shp08 = fcfun.shp_cylcenxtr (r = self.bolttens_r_tol,
                                     h = self.wall_thick,
                                     normal = self.axis_l,
                                     ch = 0, xtr_top=1, xtr_bot=1, pos = pos08)
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

        self.hold_bas_w = self.hold_w + 2*self.aluprof_w
        #
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




        Part.show(shp10_final)

    """
            shp06a = fcfun.shp_box_dir_xtr(
                               box_w = self.tens_w,
                               box_d = self.hold_l,
                               box_h = self.tens_h,
                               fc_axis_h = self.axis_h,
                               fc_axis_d = self.axis_l,
                               cw=1, cd=0, ch=0,
                               xtr_w = kcomp.TOL/2.,  #tolerances on each side
                               xtr_nw = kcomp.TOL/2.,
                               xtr_h = kcomp.TOL/2.,
                               xtr_nh = kcomp.TOL/2.,
                               pos=self.pos06)
            # list of points that are on edges to be chamfered
            pts_list = [pos06]
            pts_list.append(pos06

            shp06 = fcfun.shp_filletchamfer_dirpts (shp=shp06a,
                                                fc_axis=self.axis_w,
                                                fc_pts=pts_list,
                                                fillet = 1,
                                                radius=self.in_fillet)

    """

    """
          axis_h
            :
            :                   nut_holder_thick
            :                      +
      .. ________                 : :_____________________
      : |___::___|                 /      _____     __:_:_|
      : |    ....|              ..|  _   /     \   /             
      : |   ()...|    bolttens_d..|:|_|:|       | |        
      : |________|                |      \_____/   \______
      :.|___::___|                 \__________________:_:_|.....> axis_l
                                  :     :       : :       :
                                  :     :       : :.......:
                                  :     :       : :  +    :
                                  :     :       :.:       :
                                  :     :       :+        :
                                  :     :.......:pulley_stroke_dist
                                  :     :   +             :
                                  :.....:  tens_stroke    :
                                  :  +                    :
                                  : nut_holder_total      :
                                  :                       :
                                  :...... tens_l .........:

    """


#                        fc_axis_h            fc_axis_h 
#                            :                  :
#                         ___:___               :______________
#                        |  ___  |              |  __________  |---
#                        | |   | |              | |__________| |   |
#                       /| |___| |\             |________      |---
#                      / |_______| \            |        |    /      
#              .. ____/  |       |  \____       |________|  /
#              ..|_::____|_______|____::_|      |___::___|/......fc_axis_l
#
#
#
#
#                 .... hold_bas_w ........
#                :        .hold_w.        :
#                :       :    wall_thick  :
#                :       :      +         :
#                :       :     : :        :
#                :_______:_____:_:________:........fc_axis_w
#                |    |  | :   : |  |     |    :
#                |  O |  | :   : |  |  O  |    + hold_bas_l
#                |____|__| :   : |__|_____|....:
#                        | :   : |
#                        |_:___:_|
#                          |   |
#                           \_/
#                            :
#                            :
#                        fc_axis_l





#
#  Tensioner holder:
#                    ________   
#                   /______ /|  
#                  |  ___  | |     Z               
#                  | |   | |/\     :
#                  | |___| |\ \    :
#              ____|_______| \ \___:
#      X....../___/ \       \ \/__/| 
#             |______\_______\____|/
#                                 .
#                                .
#                               .
#                              Y
#                                              Z      Z
#                                              :      :
#                               _______        :      :______________
#                              |  ___  |       :      |  __________  |
#                              | |   | |       :      | |__________| |
#                             /| |___| |\      :      |________      |
#                            / |_______| \     :      |        |    /      
#                    .. ____/  |       |  \____:      |________|  /
#        hold_bas_h.+..|_::____|_______|____::_|      |___::___|/......Y
# 
#                       .... hold_bas_w ........
#                      :        .hold_w.        :
#                      :       :    wall_thick  :
#                      :       :      +         :
#                      :       :     : :        :
#               X......:_______:_____:_:________:....
#                      |    |  | :   : |  |     |    :
#                      |  O |  | :   : |  |  O  |    + hold_bas_l
#                      |____|__| :   : |__|_____|....:
#                              | :   : |        :
#                              |_:___:_|        :
#                                               :
#                                               :
#                                               :
#                                               Y
# 
# Idler tensioner:
# 
#           Z
#           :              ........ tens_l ........
#           :             :                        :
#          .. ________       _______________________
#          : |___::___|     /      ______   ___::___|
#          : |    ....|    |  __  |      | |
#   tens_h + |   ()...|    |:|  |:|      | |         
#          : |________|    |  --  |______| |________
#          :.|___::___|     \__________________::___|.......> Y
# 
# 
#             ________ ....> X
#            |___::___|
#            |  ......|
#            |  :.....|
#            |   ::   |
#            |........|
#            |        |
#            |        |
#            |........|
#            |........|
#            |        |
#            |   ()   |
#            |        |
#            |________|
#            :        :
#            :........:
#                +
#               tens_w



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
Tensioner()


class IdlerTens (object):

    """
    Makes a tensioner for an idler pulley
    Arguments:
    boltidler_d : diameter of the bolt that holds the idler pulley
    wall_thick  : general thickness of the walls
    tens_stroke : tensioner stroke (length)
    pulley_stroke_dist : distance from the end of the pulley to the end point
                         of the stroke (when closest to the idler pulley)
    nut_holder_thick : the thickness on both sides outside of the space for the
                       nut for the tensioner
    bolttens_d : diameter of the bolt for the tensioner
    nut_space_h_times : the space for the nut height, will be calculated
                      multipliying this multiplier by the nut height, 
    in_fillet : inner fillet
             
    fc_axis_h = axis on the height direction
    fc_axis_l = axis on the length direction
    fc_axis_w = axis on the width direction, pointing to the nut hole
                if V0, it doesnt matter and it will be calculated by the
                cross product of fc_axis_l x fc_axis_h
    ref_h : reference on the height direction
             1: reference at the middle of the idler
             2: reference at the base on height
    ref_l: 1: reference at the back
           2:  reference at the back axis of the bolt of the idler pulley
    pos: FreeCAD Vector for the position of the reference point
    name: name of the FreeCAD object

             fc_axis_h
               :
               :
            ________       _______________________
           |___::___|     /      ______   ___::___|
           |    ....|    |  __  |      | |
           |   ()...|    1:|  |:|      | |   2     .......> fc_axis_l
           |________|    |  --  |______| |________
           |___::___|    2\__________________::___|


            ________ ....> fc_axis_w
           |___::___|
           |  ......|
           |  :.....|
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
           :        :
           :        :

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

    def __init__(self,
                 boltidler_d,
                 wall_thick = 3.,
                 tens_stroke = 20.,
                 pulley_stroke_dist = 6.,
                 nut_holder_thick = 3.,
                 bolttens_d = 3.,
                 nut_space_h_times = 2.,
                 in_fillet = 2.,
                 fc_axis_h = VZ,
                 fc_axis_l = VY,
                 fc_axis_w = V0,
                 ref_h = 1,
                 ref_l = 1,
                 pos = V0,
                 wfco = 1,
                 name= "idler_tens"):


        # normalize de axis
        axis_h = DraftVecUtils.scaleTo(fc_axis_h,1)
        axis_l = DraftVecUtils.scaleTo(fc_axis_l,1)
        if fc_axis_w == V0:
            axis_w = axis_l.cross(axis_h)
        else:
            axis_w = DraftVecUtils.scaleTo(fc_axis_w,1)

        nut_space = nut_space_h_mult * kcomp.NUT_D934_L[bolttens_d] + kcomp.TOL;
        nut_holder_total = nut_space + 2*nut_holder_thick;

        self.tens_l = (  nut_holder_total
                  + tensioner_stroke
                  + 2 * idler_r_xtr
                  + pulley_stroke_dist)
        self.tens_h = idler_h + 2*wall_thick
        self.tens_w = 2 * idler_r_xtr





class IdlerHolder (object):



    """

                  fc_axis_h
                ___:____   
               /___:__ /|  
              |  ___  | |                    
              | |   | |/\   
              | |___| |\ \
              |_______| \ \___
          ___/ \       \ \/__/| 
         |______\_______\____|/...... fc_axis_w 
                  .
                 .
                .
           fc_axis_l
                              fc_axis_h
                                  :
                             . ___:___                ______________
                              |  ___  |              |  __________  |
                              | |   | |              | |__________| |
                             /| |___| |\             |________      |
                            / |_______| \            |        |    /      
                    .. ____/  |       |  \____       |________|  /
        hold_bas_h.+..|_::____|_______|____::_|      |___::___|/
 
                       .... hold_base_w .......
                      :        .hold_w.        :
                      :       :    wall_thick  :
                      :       :      +         :
                      :       :     : :        :
                    ..:_______:_____:_:________:
                   :  |    |  | :   : |  |     |
         hold_bas_l+  |  O |  | :   : |  |  O  |.....fc_axis_w
                   :..|____|__| :   : |__|_____|
                              | :   : |
                 .............|_:___:_|
                                  :
                                  :
                                  :
                               fc_axis_l


                              fc_axis_h
                                  :
                             . ___:___                ______________
                              |  ___  |              |  __________  |
                              | |   | |              | |__________| |
                             /| |___| |\             |________      |
                            / |_______| \            |        |    /      
                    .. ____/  |       |  \____       |________|  /
     holder_base_z.+..|_::____|_______|____::_|      |___::___|/
 


                      :________________________
                      |    |  | :   : |  |     |
                      |  O |  | :   : |  |  O  |
                      |____|__| :   : |__|_____|
                              | :   : |
                              |_:___:_|


                                 ref_h
                               ___:___                ______________
                              |  ___  |              |  __________  |
                              | | 1 | |              | |__________| |
                             /| |___| |\             |________      |
                            / |_______| \            |        |    /      
                       ____/  |       |  \____       |________|  /
                      |_::____|___2___|____::_|      2___1:___|/  ref_l
 


                      :________________________
                      |    |  | :   : |  |     |
                      |  2 |  | : 1 : |  |  O  | ref_w
                      |____|__| :   : |__|_____|
                              | :   : |
                              |_:___:_|


                   ___:___          
                  |  ___  |         
                  | | 1 | |         
                 /| |___| |\       
                / |_______| \      
           ____/  |       |  \____ ...
          |_::____|___2___|____::_|..: holder_base_z



    fc_axis_h = axis on the height direction
    fc_axis_l = axis on the length
    fc_axis_w = width (perpendicular) dimension
    ref_h :  1: reference at the middle of the idler
             2: reference at the base on height
    ref_l: 1: reference at the bolt position on fc_axis_l
           2  reference at the back
    ref_w: 1: reference at the center (symmetry)
           2: reference at the bolt hole

    """

    # separation of the upper side (it is not defined). Change it
    # measured for sk12 is 1.2
    up_sep_dist = 1.2

    # tolerances for holes 
    holtol = 1.1

    #def __init__(self, size,
