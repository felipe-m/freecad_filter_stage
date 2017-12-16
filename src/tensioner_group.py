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
# :                      |  ___  |     ref_h:   |  __________  |---
# :                      | |   | |        4     | |__________| | : |
# :+hold_h              /| |___| |\       2,3    |________      |---
# :                    / |_______| \            |        |    /      
# :             . ____/  |       |  \____       |________|  /
# :..hold_bas_h:.|_::____|_______|____::_|1     |___::___|/......fc_axis_l
#                                               1    2           3: ref_l
#
#
#
#                 .... hold_bas_w ........
#                :        .hold_w.        :
#                :       :    wall_thick  :
#                :       :      +         :
#                :       :     : :        :
#       ref_w:   3__2____:___1_:_:________:........fc_axis_w
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
import FreeCAD
import FreeCADGui
import Part

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

from fcfun import V0, VX, VY, VZ, V0ROT
from fcfun import VXN, VYN, VZN

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
    :+hold_h              /| |___| |\       2     |________      |---
    :                    / |_______| \            |        |    /      
    :             . ____/  |       |  \____       |________|  /
    :..hold_bas_h:.|_::____|_______|____::_|1     |___::___|/......>fc_axis_l
                                                  1    2           3: pos_l
   
   
   
                    .... hold_bas_w ........
                   :        .hold_w.        :
                   :       :    wall_thick  :
                   :       :      +         :
                   :       :     : :        :
          pos_w:   3__2____:___1_:_:________:........>axis_w
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
      - pos_l: location of pos along the axis_l (1,2,3)
         - 1: at the back of the holder
         - 2: at the center of the base along axis_l, where the bolts to attach
              the holder base to the aluminum profile
         - 3: at the center of the idler pulley
      - pos_w: location of pos along the axis_w (1,2,3)
         - 1: at the center of symmetry
         - 2: at the center of the bolt holes to attach the holder base to the
              aluminum profile
         - 3: at the end of the piece along axis_w
              axes have direction. So if pos_w == 3, the piece will be drawn
              along the positive side of axis_w
      - pos_h: location of pos along the axis_h (1,2,3)
         - 1: at the bottom of the holder
         - 2: at the bottom of the idler tensioner
         - 3: at the bottom of the idler pulley
         - 4: at the center of the idler pulley

    Parameters
    ----------
    aluprof_w : float
        Width of the aluminum profile
    belt_pos_h : float
        The position along axis_h where the idle pulley that conveys the belt
        starts .This is the base of the bearing, when the pulley is made with
        washers and bearings
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
    axis_l : FreeCAD.Vector
        length vector of coordenate system
    axis_w : FreeCAD.Vector
        width vector of coordenate system
        if V0: it will be calculated using the cross product: axis_h x axis_w
    axis_h : FreeCAD.Vector
        height vector of coordenate system
    pos_l : int
        location of pos along the axis_l (1,2,3)
        1: at the back of the holder
        2: at the center of the base along axis_l, where the bolts to attach
           the holder base to the aluminum profile
        3: at the center of the idler pulley
    pos_w : int
        location of pos along the axis_w (1,2,3)
        1: at the center of symmetry
        2: at the center of the bolt holes to attach the holder base to the
           aluminum profile
        3: at the end of the piece along axis_w
           axes have direction. So if pos_w == 3, the piece will be drawn
           along the positive side of axis_w
    pos_h : int
        location of pos along the axis_h (1,2,3)
        1: at the bottom of the holder
        2: at the bottom of the idler tensioner
        3: at the bottom of the idler pulley
        4: at the center of the idler pulley
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


    Tensioner Holder arguments:
    -------------------------

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
        |:|  |:|      | ||_______|.......................bottom side of bearing
        |  --  |______| |_======_                       :
         \__________________::___|.: wall_thick         :
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
                 axis_l = VX,
                 axis_w = V0,
                 axis_h = VZ,
                 pos_l = 1,
                 pos_w = 1,
                 pos_h = 1,
                 pos = V0,
                 wfco = 1,
                 name= "tensioner"):

        # bring the active document:
        doc = FreeCAD.ActiveDocument

        # save the arguments as attributes:
        for key, value in kwargs.items():
            setattr(self, key, value)

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
        idlerpulley_l = kcomp.idpull_dict[boltidler_d]
        self.idlerpulley_l = idlerpulley_l
        self.idler_h = partgroup.getgroupheight(idlerpulley_l)
        self.idler_r = partgroup.getmaxwashdiam(idlerpulley_l)/2.
        self.idler_r_xtr = idler_r + 2.  #  +2: a little bit larger
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

        self.tens_w_tol = self.tens_w + TOL
        self.tens_h_tol = self.tens_h + TOL

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


AAAAAAAAAAAAAAAAA

        # ------ vector from the different position points
        # -- pos_l distances:
        # depends also on how much on the ratio the tensioner is inside
        dis_ax_l_3_1 = (  self.hold_l
                        + self.diler_r_xtr
                        + tens_in_ratio * tens_stroke)
        # -- pos_l vectors:
        ax_l_1 = {}
        #ax_l_2_1 = DraftVecUtils.scale(axis_h,-self.hold_bas_l/2.)
        ax_l_orig[2] = DraftVecUtils.scale(axis_h,-self.hold_bas_l/2.)
        #ax_l_3_1 = DraftVecUtils.scale(axis_h,-dis_ax_l_3_1)
        # vector from point 3 along axis_l to orig (point 1)
        ax_l_orig[3] = DraftVecUtils.scale(axis_h,-dis_ax_l_3_1)
        ax_l_orig[1] = V0
        pos_l_orig = ax_l_orig[pos_l]

        # -- pos_w distances:
        # depends also on how much on the ratio the tensioner is inside
        dis_ax_w_2_1 = self.hold_w/2. + aluprof_w/2.
        dis_ax_w_3_1 = self.hold_w/2. + aluprof_w
        # -- pos_w vectors:
        ax_w_2_1 = DraftVecUtils.scale(axis_h,-dis_ax_w_2_1)
        ax_w_3_1 = DraftVecUtils.scale(axis_h,-dis_ax_w_3_1)

        # -- pos_h distances:
        dis_ax_h_4_3 = self.largewasher_thick /2.
        dis_ax_h_4_1 = dist_ax_h_4_3 + -self.belt_pos_h
        # -- pos_h vectors:
        # use scale and not scaleTo because is equivalent since vectors are
        ax_h_2_1 = DraftVecUtils.scale(axis_h,-self.tens_pos_h)
        ax_h_3_1 = DraftVecUtils.scale(axis_h,-self.belt_pos_h)
        ax_h_4_1 = DraftVecUtils.scale(axis_h,-dis_ax_h_4_1)


        # ------ position of point: pos_l = 1, pos_w = 1, pos_h = 1
        # pos is the position of a point, the point depends on the 
        # values of pos_l, pos_w, pos_h
        # Now we calculate the position of a defined point, which is
        # pos_l = 1, pos_w = 1, pos_h = 1
        # along axis_l
        if pos_l == 1:
            pos_l_to_1 = V0 # the same position
        elif pos_l == 2:
            pos_l_to_1 = ax_l_2_1
        elif pos_l == 3:
            pos_l_to_1 = ax_l_3_1




        # distances
        axis_h_4_1 = DraftVecUtils.scale(axis_h,-self.belt_pos_h)
        # pos is the position of a point, the point depends on the 
        # values of pos_l, pos_w, pos_h
        # Now we calculate the position of a defined point, which is
        # pos_l = 1, pos_w = 1, pos_h = 1




        # since the position pos is relative to pos_l, pos_w, pos_h

        # normal axes to print
        self.tens_axis_prn = axis_w # for the idler tensioner
        self.hold_axis_prn = axis_l # for the tensioner holder


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
