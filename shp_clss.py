# ----------------------------------------------------------------------------
# -- Obj3D class and children
# ----------------------------------------------------------------------------
# -- (c) Felipe Machado
# -- Area of Electronic Technology. Rey Juan Carlos University (urjc.es)
# -- January-2018
# ----------------------------------------------------------------------------
# --- LGPL Licence
# ----------------------------------------------------------------------------

import FreeCAD
import Part
import DraftVecUtils

import os
import sys
import math
import inspect
import logging

# directory this file is
filepath = os.getcwd()
import sys
# to get the components
# In FreeCAD can be added: Preferences->General->Macro->Macro path
sys.path.append(filepath)

import fcfun
import kcomp

from fcfun import V0, VX, VY, VZ, V0ROT
from fcfun import VXN, VYN, VZN

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class Obj3D (object):
    """ This is the the basic class, that provides reference axes and 
    methods to get positions

    It is the parent class of other classes, no instantiation of this class

    These objects have their own coordinate axes:
    axis_d: depth
    axis_w: width
    axis_h: height

    They have an origin point pos_o (created in a child class)
    and have different interesting points
    d_o
    w_o
    h_o

    and methods to get to them

    pos_o_adjustment : FreeCAD.Vector
        if not V0 indicates that shape has not been placed at pos_o, so the FreeCAD object
        will need to be placed at pos_o_adjust
            
    """
    def __init__(self, axis_d = None, axis_w = None, axis_h = None):
        # the TopoShape has an origin, and distance vectors from it to 
        # the different points along the coordinate system  
        self.d_o = {}  # along axis_d
        self.w_o = {}  # along axis_w
        self.h_o = {}  # along axis_h
        if axis_h is not None:
            axis_h = DraftVecUtils.scaleTo(axis_h,1)
        else:
            self.h_o[0] = V0
            self.pos_h = 0
            axis_h = V0
        self.axis_h = axis_h

        if axis_d is not None:
            axis_d = DraftVecUtils.scaleTo(axis_d,1)
        else:
            self.d_o[0] = V0
            self.pos_d = 0
            axis_d = V0
        self.axis_d = axis_d

        if axis_w is not None:
            axis_w = DraftVecUtils.scaleTo(axis_w,1)
        else:
            self.w_o[0] = V0
            self.pos_w = 0
            axis_w = V0
        self.axis_w = axis_w

        
        self.pos_o_adjust = V0



    def vec_d(self, d):
        """ creates a vector along axis_d (depth) with the length of argument d

        Returns a FreeCAD.Vector

        Parameter:
        ----------
        d : float
            depth: lenght of the vector along axis_d
        """

        # self.axis_d is normalized, so no need to use DraftVecUtils.scaleTo
        vec_d = DraftVecUtils.scale(self.axis_d, d)
        return vec_d


    def vec_w(self, w):
        """ creates a vector along axis_w (width) with the length of argument w

        Returns a FreeCAD.Vector

        Parameter:
        ----------
        w : float
            width: lenght of the vector along axis_w
        """

        # self.axis_w is normalized, so no need to use DraftVecUtils.scaleTo
        vec_w = DraftVecUtils.scale(self.axis_w, w)
        return vec_w


    def vec_h(self, h):
        """ creates a vector along axis_h (height) with the length of argument h

        Returns a FreeCAD.Vector

        Parameter:
        ----------
        h : float
            height: lenght of the vector along axis_h
        """

        # self.axis_h is normalized, so no need to use DraftVecUtils.scaleTo
        vec_h = DraftVecUtils.scale(self.axis_h, h)
        return vec_h

    def vec_d_w_h(self, d, w, h):
        """ creates a vector with:
            depth  : along axis_d
            width  : along axis_w
            height : along axis_h

        Returns a FreeCAD.Vector

        Parameters:
        ----------
        d, w, h : float
            depth, widht and height
        """

        vec = self.vec_d(d) + self.vec_w(w) + self.vec_h(h)
        return vec

    def set_pos_o(self, adjust=0):
        """ calculates the position of the origin, and saves it in
        attribute pos_o
        Parameters:
        -----------
        adjust : int
             1: If, when created, wasnt possible to set the piece at pos_o,
                and it was placed at pos, then the position will be adjusted
            
        """

        vec_from_pos_o =  (  self.d_o[self.pos_d]
                           + self.w_o[self.pos_w]
                           + self.h_o[self.pos_h])
        vec_to_pos_o =  vec_from_pos_o.negative()
        self.pos_o = self.pos + vec_to_pos_o
        if adjust == 1:
            self.pos_o_adjust = vec_to_pos_o # self.pos_o - self.pos

    def get_o_to_d(self, pos_d):
        """ returns the vector from origin pos_o to pos_d
        If it is symmetrical along axis_d, pos_d == 0 will be at the middle
        Then, pos_d > 0 will be the points on the positive side of axis_d
        and   pos_d < 0 will be the points on the negative side of axis_d

          d0_cen = 1
                :
           _____:_____
          |     :     |   self.d_o[1] is the vector from orig to -1
          |     :     |   self.d_o[0] is the vector from orig to 0
          |_____:_____|......> axis_d
         -2 -1  0  1  2

         o---------> A:  o to  1  :
         o------>    B:  o to  0  : d_o[0]
         o--->       C:  o to -1  : d_o[1]
         o    -->    D: -1 to  0  : d_o[0] - d_o[1] : B - C
                     A = B + D
                     A = B + (B-C) = 2B - C

        d0_cen = 0
          :
          :___________
          |           |   self.d_o[1] is the vector from orig to 1
          |           |
          |___________|......> axis_d
          0  1  2  3  4


        """
        abs_pos_d = abs(pos_d)
        if self.d0_cen == 1:
            if pos_d <= 0:
                try:
                    vec = self.d_o[abs_pos_d]
                except KeyError:
                    logger.error('pos_d key not defined ' + str(pos_d))
                else:
                    return vec
            else:
                try:
                    vec_0_to_d = (self.d_o[0]).sub(self.d_o[pos_d]) # D= B-C
                except KeyError:
                    logger.error('pos_d key not defined ' + str(pos_d))
                else:
                    vec_orig_to_d = self.d_o[0] + vec_0_to_d # A = B + D
                    return vec_orig_to_d
        else: #pos_d == 0 is at the end, distances are calculated directly
            try:
                vec = self.d_o[pos_d]
            except KeyError:
                logger.error('pos_d key not defined' + str(pos_d))
            else:
                return vec


    def get_o_to_w(self, pos_w):
        """ returns the vector from origin pos_o to pos_w
        If it is symmetrical along axis_w, pos_w == 0 will be at the middle
        Then, pos_w > 0 will be the points on the positive side of axis_w
        and   pos_w < 0 will be the points on the negative side of axis_w
        See get_o_to_d drawings
        """
        abs_pos_w = abs(pos_w)
        if self.w0_cen == 1:
            if pos_w <= 0:
                try:
                    vec = self.w_o[abs_pos_w]
                except KeyError:
                    logger.error('pos_w key not defined ' + str(pos_w))
                else:
                    return vec
            else:
                try:
                    vec_0_to_w = (self.w_o[0]).sub(self.w_o[pos_w]) # D= B-C
                except KeyError:
                    logger.error('pos_w key not defined ' + str(pos_w))
                else:
                    vec_orig_to_w = self.w_o[0] + vec_0_to_w # A = B + D
                    return vec_orig_to_w
        else: #pos_w == 0 is at the end, distances are calculated directly
            try:
                vec = self.w_o[pos_w]
            except KeyError:
                logger.error('pos_w key not defined' + str(pos_w))
            else:
                return vec

    def get_o_to_h(self, pos_h):
        """ returns the vector from origin pos_o to pos_h
        If it is symmetrical along axis_h, pos_h == 0 will be at the middle
        Then, pos_h > 0 will be the points on the positive side of axis_h
        and   pos_h < 0 will be the points on the negative side of axis_h
        See get_o_to_d drawings
        """
        abs_pos_h = abs(pos_h)
        if self.h0_cen == 1:
            if pos_h <= 0:
                try:
                    vec = self.h_o[abs_pos_h]
                except KeyError:
                    logger.error('pos_h key not defined ' + str(pos_h))
                else:
                    return vec
            else:
                try:
                    vec_0_to_h = (self.h_o[0]).sub(self.h_o[pos_h]) # D= B-C
                except KeyError:
                    logger.error('pos_h key not defined ' + str(pos_h))
                else:
                    vec_orig_to_h = self.h_o[0] + vec_0_to_h # A = B + D
                    return vec_orig_to_h
        else: #pos_h == 0 is at the end, distances are calculated directly
            try:
                vec = self.h_o[pos_h]
            except KeyError:
                logger.error('pos_h key not defined' + str(pos_h))
            else:
                return vec

    def get_d_ab(self, pta, ptb):
        """ returns the vector along axis_d from pos_d = pta to pos_d = ptb
        """
        vec = self.get_o_to_d(ptb).sub(self.get_o_to_d(pta))
        return vec

    def get_w_ab(self, pta, ptb):
        """ returns the vector along axis_h from pos_w = pta to pos_w = ptb
        """
        vec = self.get_o_to_w(ptb).sub(self.get_o_to_w(pta))
        return vec

    def get_h_ab(self, pta, ptb):
        """ returns the vector along axis_h from pos_h = pta to pos_h = ptb
        """
        vec = self.get_o_to_h(ptb).sub(self.get_o_to_h(pta))
        return vec


    def get_pos_d(self, pos_d):
        """ returns the absolute position of the pos_d point
        """
        return self.pos_o + self.get_o_to_d(pos_d)

    def get_pos_w(self, pos_w):
        """ returns the absolute position of the pos_w point
        """
        return self.pos_o + self.get_o_to_w(pos_w)

    def get_pos_h(self, pos_h):
        """ returns the absolute position of the pos_h point
        """
        return self.pos_o + self.get_o_to_h(pos_h)

    def get_pos_dwh(self, pos_d, pos_w, pos_h):
        """ returns the absolute position of the pos_d, pos_w, pos_h point
        """
        pos = (self.pos_o + self.get_o_to_d(pos_d)
                          + self.get_o_to_w(pos_w)
                          + self.get_o_to_h(pos_h))
        return pos



class ShpCyl (Obj3D):
    """
    Creates a shape of a cylinder
    Makes a cylinder in any position and direction, with optional extra
    heights and radius, and various locations in the cylinder

    Parameters:
    -----------
    r : float
        radius of the cylinder
    h : float
        height of the cylinder
    axis_h : FreeCAD.Vector
        vector along the cylinder height
    axis_d : FreeCAD.Vector
        vector along the cylinder radius, a direction perpendicular to axis_h
        It is not necessary if pos_d == 0
        It can be None, but if None, axis_w has to be None
    axis_w : FreeCAD.Vector
        vector along the cylinder radius
        a direction perpendicular to axis_h and axis_d
        It is not necessary if pos_w == 0
        It can be None
    pos_h : int
        location of pos along axis_h (0, 1)
        0: the cylinder pos is centered along its height
        1: the cylinder pos is at its base (not considering xtr_h)
    pos_d : int
        location of pos along axis_d (0, 1)
        0: pos is at the circunference center
        1: pos is at the circunsference, on axis_d, at r from the circle center
           (not at r + xtr_r)
    pos_w : int
        location of pos along axis_w (0, 1)
        0: pos is at the circunference center
        1: pos is at the circunsference, on axis_w, at r from the circle center
           (not at r + xtr_r)
    xtr_top : float
        Extra height on top, it is not taken under consideration when
        calculating the cylinder center along the height
    xtr_bot : float
        Extra height at the bottom, it is not taken under consideration when
        calculating the cylinder center along the height or the position of
        the base
    xtr_r : float
        Extra length of the radius, it is not taken under consideration when
        calculating pos_d or pos_w
    pos : FreeCAD.Vector
        Position of the cylinder, taking into account where the center is
    print_ax: FreeCAD.Vector
        The best direction to print, pointing upwards
        it can be V0 if there is no best direction

    Attributes:
    -----------
    pos_o : FreeCAD.Vector
        Position of the origin of the shape
    h_o : dictionary of FreeCAD.Vector
        vectors from the origin to the different points along axis_h
    d_o : dictionary of FreeCAD.Vector
        vectors from the origin to the different points along axis_d
    w_o : dictionary of FreeCAD.Vector
        vectors from the origin to the different points along axis_w
    h0_cen : int
    d0_cen : int
    w0_cen : int
        indicates if pos_h = 0 (pos_d, pos_w) is at the center along
        axis_h, axis_d, axis_w, or if it is at the end.
        1 : at the center (symmetrical, or almost symmetrical)
        0 : at the end
    shp : OCC Topological Shape
        The shape of this part


    
    pos_h = 1, pos_d = 0, pos_w = 0
    pos at 1:
            axis_w
              :
              :
             . .    
           .     .
         (    o    ) ---- axis_d       This o will be pos_o (origin)
           .     .
             . .    

           axis_h
              :
              :
          ...............
         :____:____:....: xtr_top
         |         |
         |         |
         |         |
         |         |
         |         |
         |         |
         |____1____|...............> axis_d
         :....o....:....: xtr_bot             This o will be pos_o


    pos_h = 0, pos_d = 1, pos_w = 0
    pos at x:

       axis_w
         :
         :
         :   . .    
         : .     .
         x         ) ----> axis_d
           .     .
             . .    

           axis_h
              :
              :
          ...............
         :____:____:....: xtr_top
         |         |
         |         |
         |         |
         x         |....>axis_d    h = 0
         |         |
         |         |
         |_________|.....
         :....o....:....: xtr_bot        This o will be pos_o


    pos_h = 0, pos_d = 1, pos_w = 1
    pos at x:

       axis_w
         :
         :
         :   . .    
         : .     .
         (         )
           .     .
         x   . .     ....> axis_d

        axis_h
         :
         :
          ...............
         :____:____:....: xtr_top
        ||         |
        ||         |
        ||         |
        |x         |....>axis_d
        ||         |
        ||         |
        ||_________|.....
        ::....o....:....: xtr_bot
        :;
        xtr_r

    """
    def __init__(self, 
                 r, h, axis_h = VZ, 
                 axis_d = None, axis_w = None,
                 pos_h = 0, pos_d = 0, pos_w = 0,
                 xtr_top=0, xtr_bot=0, xtr_r=0, pos = V0):

        Obj3D.__init__(self, axis_d, axis_w, axis_h)

        # save the arguments as attributes:
        frame = inspect.currentframe()
        args, _, _, values = inspect.getargvalues(frame)
        for i in args:
            if not hasattr(self,i): # so we keep the attributes already set
                setattr(self, i, values[i])

        # vectors from o (orig) along axis_h, to the pos_h points
        # h_o is a dictionary created in Obj3D.__init__
        self.h_o[0] =  self.vec_h(h/2. + xtr_bot)
        self.h_o[1] =  self.vec_h(xtr_bot)
        # pos_h = 0 is at the center
        self.h0_cen = 1

        self.d_o[0] = V0
        if self.axis_d is not None:
            self.d_o[1] = self.vec_d(-r)
        elif pos_d == 1:
            logger.error('axis_d not defined while pos_d ==1')
        # pos_d = 0 is at the center
        self.d0_cen = 1

        self.w_o[0] = V0
        if self.axis_w is not None:
            self.w_o[1] = self.vec_w(-r)
        elif pos_w == 1:
            logger.error('axis_w not defined while pos_w ==1')
        # pos_w = 0 is at the center
        self.w0_cen = 1

        # calculates the position of the origin, and keeps it in attribute pos_o
        self.set_pos_o()

        shpcyl = fcfun.shp_cyl (r      = r + xtr_r,         # radius
                                h      = h+xtr_bot+xtr_top, # height
                                normal = self.axis_h,       # direction
                                pos    = self.pos_o)        # Position

        self.shp = shpcyl

#cyl = ShpCyl (r=2, h=2, axis_h = VZ, 
#              axis_d = VX, axis_w = VY,
#              pos_h = 1, pos_d = 1, pos_w = 0,
#              xtr_top=0, xtr_bot=1, xtr_r=2,
#              pos = V0)
#              #pos = FreeCAD.Vector(1,2,0))
#Part.show(cyl.shp)



class ShpCylHole (Obj3D):
    """
    Creates a shape of a hollow cylinder
    Similar to fcfun shp_cylhole_gen, but creates the object with the useful
    attributes and methods
    Makes a hollow cylinder in any position and direction, with optional extra
    heights, and inner and outer radius, and various locations in the cylinder

    Parameters:
    -----------
    r_out : float
        radius of the outside cylinder
    r_in : float
        radius of the inner hole of the cylinder
    h : float
        height of the cylinder
    axis_h : FreeCAD.Vector
        vector along the cylinder height
    axis_d : FreeCAD.Vector
        vector along the cylinder radius, a direction perpendicular to axis_h
        it is not necessary if pos_d == 0
        It can be None, but if None, axis_w has to be None
    axis_w : FreeCAD.Vector
        vector along the cylinder radius,
        a direction perpendicular to axis_h and axis_d
        it is not necessary if pos_w == 0
        It can be None
    pos_h : int
        location of pos along axis_h (0, 1)
        0: the cylinder pos is centered along its height, not considering
           xtr_top, xtr_bot
        1: the cylinder pos is at its base (not considering xtr_h)
    pos_d : int
        location of pos along axis_d (0, 1)
        0: pos is at the circunference center
        1: pos is at the inner circunsference, on axis_d, at r_in from the
           circle center (not at r_in + xtr_r_in)
        2: pos is at the outer circunsference, on axis_d, at r_out from the
           circle center (not at r_out + xtr_r_out)
    pos_w : int
        location of pos along axis_w (0, 1)
        0: pos is at the circunference center
        1: pos is at the inner circunsference, on axis_w, at r_in from the
           circle center (not at r_in + xtr_r_in)
        2: pos is at the outer circunsference, on axis_w, at r_out from the
           circle center (not at r_out + xtr_r_out)
    xtr_top : float
        Extra height on top, it is not taken under consideration when
        calculating the cylinder center along the height
    xtr_bot : float
        Extra height at the bottom, it is not taken under consideration when
        calculating the cylinder center along the height or the position of
        the base
    xtr_r_in : float
        Extra length of the inner radius (hollow cylinder),
        it is not taken under consideration when calculating pos_d or pos_w.
        It can be negative, so this inner radius would be smaller
    xtr_r_out : float
        Extra length of the outer radius
        it is not taken under consideration when calculating pos_d or pos_w.
        It can be negative, so this outer radius would be smaller
    pos : FreeCAD.Vector
        Position of the cylinder, taking into account where the center is

    Attributes:
    -----------
    pos_o : FreeCAD.Vector
        Position of the origin of the shape
    h_o : dictionary of FreeCAD.Vector
        vectors from the origin to the different points along axis_h
    d_o : dictionary of FreeCAD.Vector
        vectors from the origin to the different points along axis_d
    w_o : dictionary of FreeCAD.Vector
        vectors from the origin to the different points along axis_w
    h0_cen : int
    d0_cen : int
    w0_cen : int
        indicates if pos_h = 0 (pos_d, pos_w) is at the center along
        axis_h, axis_d, axis_w, or if it is at the end.
        1 : at the center (symmetrical, or almost symmetrical)
        0 : at the end
    shp : OCC Topological Shape
        The shape of this part


    pos_h = 1, pos_d = 0, pos_w = 0
    pos at 1:
            axis_w
              :
              :
             . .    
           . . . .
         ( (  0  ) ) ---- axis_d
           . . . .
             . .    

           axis_h
              :
              :
          ...............
         :____:____:....: xtr_top
         | :     : |
         | :     : |
         | :     : |
         | :  0  : |     0: pos would be at 0, if pos_h == 0
         | :     : |
         | :     : |
         |_:__1__:_|....>axis_d
         :.:..o..:.:....: xtr_bot        This o will be pos_o (orig)
         : :  :
         : :..:
         :  + :
         :r_in:
         :    :
         :....:
           +
          r_out
         

    Values for pos_d  (similar to pos_w along it axis)


           axis_h
              :
              :
          ...............
         :____:____:....: xtr_top
         | :     : |
         | :     : |
         | :     : |
         2 1  0  : |....>axis_d    (if pos_h == 0)
         | :     : |
         | :     : |
         |_:_____:_|.....
         :.:..o..:.:....: xtr_bot        This o will be pos_o (orig)
         : :  :
         : :..:
         :  + :
         :r_in:
         :    :
         :....:
           +
          r_out

    """
    def __init__(self,
                 r_out, r_in, h,
                 axis_h = VZ, axis_d = None, axis_w = None,
                 pos_h = 0, pos_d = 0, pos_w = 0,
                 xtr_top=0, xtr_bot=0,
                 xtr_r_out=0, xtr_r_in=0,
                 pos = V0):


        Obj3D.__init__(self, axis_d, axis_w, axis_h)

        # save the arguments as attributes:
        frame = inspect.currentframe()
        args, _, _, values = inspect.getargvalues(frame)
        for i in args:
            if not hasattr(self,i):
                setattr(self, i, values[i])

        # vectors from o (orig) along axis_h, to the pos_h points
        # h_o is a dictionary created in Obj3D.__init__
        self.h_o[0] =  self.vec_h(h/2. + xtr_bot)
        self.h_o[1] =  self.vec_h(xtr_bot)
        # pos_h = 0 is at the center
        self.h0_cen = 1

        self.d_o[0] = V0
        if self.axis_d is not None:
            self.d_o[1] = self.vec_d(-r_in)
            self.d_o[2] = self.vec_d(-r_out)
        elif pos_d != 0:
            logger.error('axis_d not defined while pos_d != 0')
        # pos_d = 0 is at the center
        self.d0_cen = 1

        self.w_o[0] = V0
        if self.axis_w is not None:
            self.w_o[1] = self.vec_w(-r_in)
            self.w_o[2] = self.vec_w(-r_out)
        elif pos_w != 0:
            logger.error('axis_w not defined while pos_w != 0')
        # pos_w = 0 is at the center
        self.w0_cen = 1

        # calculates the position of the origin, and keeps it in attribute pos_o
        self.set_pos_o()

        shpcyl = fcfun.shp_cylholedir (r_out = r_out + xtr_r_out, #ext radius
                                       r_in  = r_in + xtr_r_in, #internal radius
                                       h     = h+xtr_bot+xtr_top, # height
                                       normal= self.axis_h,       # direction
                                       pos   = self.pos_o)        # Position

        self.shp = shpcyl
        self.prnt_ax = self.axis_h


#cyl = ShpCylHole (r_in=2, r_out=5, h=4,
#                       #axis_h = FreeCAD.Vector(1,1,0), 
#                       axis_h = VZ,
#                       #axis_d = VX, axis_w = VYN,
#                       axis_d = VX,
#                       pos_h = 1,  pos_d = 1, pos_w = 0,
#                       xtr_top=0, xtr_bot=0,
#                       xtr_r_in=0, xtr_r_out=0,
#                       pos = V0)
#                       #pos = FreeCAD.Vector(1,2,3))
#Part.show(cyl.shp)

