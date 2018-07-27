# ----------------------------------------------------------------------------
# -- Components
# -- parts_set library
# -- Python classes that creates useful sets of parts for FreeCAD
# ----------------------------------------------------------------------------
# -- (c) Felipe Machado
# -- Area of Electronic Technology. Rey Juan Carlos University (urjc.es)
# -- July-2018
# ----------------------------------------------------------------------------
# --- LGPL Licence
# ----------------------------------------------------------------------------


import FreeCAD
import Part
import logging
import os
import inspect
import Draft
import DraftGeomUtils
import DraftVecUtils
import math
#import copy;
#import Mesh;

# ---------------------- can be taken away after debugging
# directory this file is
filepath = os.getcwd()
import sys
# to get the components
# In FreeCAD can be added: Preferences->General->Macro->Macro path
sys.path.append(filepath)
# ---------------------- can be taken away after debugging

import kcomp # before, it was called mat_cte
import fcfun
import comps
import shp_clss
import fc_clss

from fcfun import V0, VX, VY, VZ
from fcfun import VXN, VYN, VZN


logging.basicConfig(level=logging.DEBUG,
                    format='%(%(levelname)s - %(message)s')

logger = logging.getLogger(__name__)



class BearWashSet (fc_clss.PartsSet):
    """ A set of bearings and washers, usually to make idle pulleys

    Parameters:
    -----------
    metric : int
        Metric (diameter) of the bolt that holds the set
    axis_h : FreeCAD.Vector
        vector along the cylinder height
    pos_h : int
        location of pos along axis_h (0,1,2,3)
        0: pos is centered along its height
        1: pos is at the base of the bearing
        2: pos is at the base of the regular washer
        3: pos is at the base of the large washer (this is the bottom)
    axis_d : FreeCAD.Vector
        vector perpendicular to the axis_h, along the radius
    pos_d : int
        location of pos along axis_d (0,1,2,3)
        0: pos is centered at the cylinder axis
        1: pos is at the bearing internal radius (defined by netric)
        2: pos is at the bearing external radius
        3: pos is at the large washer external radius
    axis_w : FreeCAD.Vector
        vector perpendicular to the axis_h and axis_d, along the radius
    pos_w : int
        location of pos along axis_w (0,1,2,3)
        0: pos is centered at the cylinder axis
        1: pos is at the bearing internal radius (defined by netric)
        2: pos is at the bearing external radius
        3: pos is at the large washer external radius
        
    group : int
        1: make a group
        0: leave as individual componentes
        
    pos : FreeCAD.Vector
        Position of the cylinder, taking into account where the center is

    Attributes:
    -----------
    metric : int or float (in case of M2.5) or even str for inches ?
        Metric of the washer

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

    tot_h : float
        Total height of the set: idler pulley
    r_in : float
        inner radius, the radius of the bearing
    r_ext : float
        external radius, the radius of the large washer


    idler pulley without the washer for the bolt because it is between a holder,
    The holder is in dots, not in the group
    pos_o is at the bottom: see o in the drawing

                 axis_h
                   :            pos_h
                ...:...
                :     :                  bolt head
      ..........:.....:........
                               :         Holder for the pulley group
      ....._________________...:
          |_________________|            large washer
              |_________|                regular washer
              |         |
              |         |         0      bearing
              |_________|         1
           ___|_________|___      2      regular washer
      ....|________o________|..   3      large washer
                               :
      .........................:         Holder for the pulley group
                :.....:                  nut
                  :.:                    bolt shank
 
                   01   2   3   pos_d, pos_w
    """

    # large washer (din9021) metric
    lwash_m_dict = { 3: 4, 4: 6}
    # regular washer (din125) has the same metric as the pulley
    # bearing tipe
    bear_m_dict = { 3: 603, 4: 624}

    def __init__(self, metric,
                 axis_h, pos_h,
                 axis_d = None, pos_d = 0,
                 axis_w = None, pos_w = 0,
                 pos = V0,
                 group = 1,
                 name = ''):

        default_name = 'bearing_idlpulley_m' + str(metric)
        self.set_name (name, default_name, change = 0)

        fc_clss.PartsSet.__init__(self,
                          axis_d = axis_d, axis_w = axis_w, axis_h = axis_h)

        # save the arguments as attributes:
        frame = inspect.currentframe()
        args, _, _, values = inspect.getargvalues(frame)
        for i in args:
            if not hasattr(self,i): # so we keep the attributes by CylHole
                setattr(self, i, values[i])

        try:
            # lwash_m is the size (metric) of the large washer
            self.lwash_m = self.lwash_m_dict[metric]
            # bear_type is the type of bearing, such as 603, 624,...
            self.bear_type = self.bear_m_dict[metric]
            # lwash_dict is the dictionary with the dimensions of large washer
            self.lwash_dict = kcomp.D9021[self.lwash_m]
            # rwash_dict is the dictionary with the dimensions of regular washer
            self.rwash_dict = kcomp.D125[metric]
            # bear is the dictionary with the dimensions of the bearing
            self.bear_dict = kcomp.BEARING[self.bear_type]
        except KeyError:
            logger.error('Bearing/washer key not found: ' + str(metric))
        else:
            # dimensions of each element
            # height, along axis_h
            self.lwash_h     = self.lwash_dict['t'] # height (thickness)
            self.lwash_r_out = self.lwash_dict['do']/2.
            self.rwash_h     = self.rwash_dict['t'] # height (thickness)
            self.rwash_r_out = self.rwash_dict['do']/2.
            self.bear_h      = self.bear_dict['t'] # height (thickness)
            self.bear_r_out  = self.bear_dict['do']/2.
            # total height:
            self.tot_h = 2 * (self.lwash_h + self.rwash_h) + self.bear_h
            #  inner radius of the pulley, the radius of the bearing
            self.r_in = self.bear_r_out
            # external radius, the radius of the large washer
            self.r_ext = self.lwash_r_out

            # pos_h/d/w = 0 are at the center
            self.h0_cen = 1
            self.d0_cen = 1
            self.w0_cen = 1

            # the origin (pos_o) is at the base
            # vectors from o (orig) along axis_h, to the pos_h points
            # h_o is a dictionary created in Obj3D.__init__
            self.h_o[0] = self.vec_h(  self.bear_h/2.
                                     + self.rwash_h
                                     + self.lwash_h)
            self.h_o[1] = self.vec_h(self.rwash_h + self.lwash_h)
            self.h_o[2] = self.vec_h(self.lwash_h)
            self.h_o[3] = V0

            self.d_o[0] = V0
            if self.axis_d is not None:
                self.d_o[1] = self.vec_d(-metric/2.)
                self.d_o[2] = self.vec_d(-self.bear_r_out)
                self.d_o[3] = self.vec_d(-self.lwash_r_out)
            elif pos_d != 0:
                logger.error('axis_d not defined while pos_d != 0')

            self.w_o[0] = V0
            if self.axis_d is not None:
                self.w_o[1] = self.vec_w(-self.metric/2.)
                self.w_o[2] = self.vec_w(-self.bear_r_out)
                self.w_o[3] = self.vec_w(-self.lwash_r_out)
            elif pos_w != 0:
                logger.error('axis_w not defined while pos_w != 0')

            # calculates the position of the origin, and keeps it in attribute
            # pos_o
            self.set_pos_o()

            # creation of the bottom large washer
            lwash_b = fc_clss.Din9021Washer(metric= self.lwash_m,
                                    axis_h = self.axis_h,
                                    pos_h = 1,
                                    pos = self.pos_o,
                                    name = 'idlpull_lwash_bt')
            self.append_part(lwash_b)
            # creation of the bottom regular washer
            rwash_b = fc_clss.Din125Washer(metric= metric,
                                   axis_h = self.axis_h,
                                   pos_h = 1,
                                   pos = lwash_b.get_pos_h(1),
                                   name = 'idlpull_rwash_bt')
            self.append_part(rwash_b)
            # creation of the bearing
            bearing = fc_clss.BearingOutl(bearing_nb = self.bear_type,
                                  axis_h = self.axis_h,
                                  pos_h = 1,
                                  axis_d = self.axis_d,
                                  axis_w = self.axis_w,
                                  pos = rwash_b.get_pos_h(1),
                                  name = 'idlpull_bearing')
            self.append_part(bearing)
            # creation of the top regular washer
            rwash_t = fc_clss.Din125Washer(metric= metric,
                                   axis_h = self.axis_h,
                                   pos_h = 1,
                                   pos = bearing.get_pos_h(1),
                                   name = 'idlpull_rwash_tp')
            self.append_part(rwash_t)
            # creation of the top large washer
            lwash_t = fc_clss.Din9021Washer(metric= self.lwash_m,
                                    axis_h = self.axis_h,
                                    pos_h = 1,
                                    pos = rwash_t.get_pos_h(1),
                                    name = 'idlpull_lwash_bt')
            self.append_part(lwash_t)
            if group == 1:
                self.make_group ()




#doc = FreeCAD.newDocument()
#idle_pulley = BearWashSet( metric=3,
#                 axis_h = VZ, pos_h = 0,
#                 axis_d = None, pos_d = 0,
#                 axis_w = None, pos_w = 0,
#                 pos = V0,
#                 name = '')



class NemaMotorPulleySet (fc_clss.PartsSet):
    """ Set composed of a Nema Motor and a pulley

    Number positions of the pulley will be after the positions of the motor


            axis_h
                :
                :
         _______:_______ .....11 <-> 5
        |______:_:______|.....10 <-> 4
            |  : :  |
            |  : :  |........9 <-> 3
            |  : :  |
         ___|__:_:__|___ .....8 <-> 2
        |______:_:______|.....7 <-> 1
         |     : :     | 
         |     : :     | 
         |     : :     | 
         |_____:o:_____|......6 <-> 0 (for the pulley)
         :      :   :
         :      :   :
                0...56789.......axis_d, axis_w
                    |
                    12345 (for the pulley)

              axis_h
                  :
                  :
                  5 ............................
                 | |                           :
                 | |                           + shaft_l
              ___|4|___.............           :
        _____|____3____|_____......:..circle_h.:
       | ::       2       :: |     :  
       |                     |     :
       |                     |     :
       |                     |     + base_l
       |                     |     :
       |                     |     :
       |                     |     :
       |__________1__________|.....:
                 : :               :
                 : :               :
                 : :               :+ rear_shaft_l (optional)
                 : :               :
                 :01...2..3..4.....:...........axis_d (same as axis_w)



                axis_w
                  :
                  :
        __________:__________.....
       /                     \....: chmf_r
       |  O               O  |
       |          _          |
       |        .   .        |
       |      (  ( )  )      |........axis_d
       |        .   .        |
       |          -          |
       |  O               O  |
       \_____________________/
       :                     :
       :.....................:
                  +
               motor_w (same as d): Nema size in inches /10

    pos_o (origin) is at pos_d=0, pos_w=0, pos_h=1

    Parameters:
    -----------

    pulley_pos_h : float
        position in mm of the pulley along the shaft
        0:  it is at the base of the shaft
        -1: the top of the pulley will be aligned with the end of the shaft
    """

    def __init__ (self,
                  # motor parameters
                  nema_size = 17,
                  base_l = 32.,
                  shaft_l = 24.,
                  shaft_r = 0,
                  circle_r = 11.,
                  circle_h = 2.,
                  chmf_r = 1, 
                  rear_shaft_l=0,
                  bolt_depth = 3.,
                  # pulley parameters
                  pulley_pitch = 2.,
                  pulley_n_teeth = 20,
                  pulley_toothed_h = 7.5,
                  pulley_top_flange_h = 1.,
                  pulley_bot_flange_h = 0,
                  pulley_tot_h = 16.,
                  pulley_flange_d = 15.,
                  pulley_base_d = 15.,
                  pulley_tol = 0,
                  pulley_pos_h = -1,
                  # general parameters
                  axis_d = VX,
                  axis_w = None,
                  axis_h = VZ,
                  pos_d = 0,
                  pos_w = 0,
                  pos_h = 1,
                  pos = V0,
                  name = ''):

        default_name = 'nemamotor_pulley_set'
        self.set_name (name, default_name, change=0)

        if (axis_w is None) or (axis_w == V0):
            axis_w = axis_h.cross(axis_d)

        fc_clss.PartsSet.__init__(self, axis_d = axis_d,
                                  axis_w = axis_w, axis_h = axis_h)

        # save the arguments as attributes:
        frame = inspect.currentframe()
        args, _, _, values = inspect.getargvalues(frame)
        for i in args:
            if not hasattr(self,i): # so we keep the attributes by CylHole
                setattr(self, i, values[i])

        # pos_w = 0 and pos_d are at the center, pos_h
        self.d0_cen = 1 #symmetric
        self.w0_cen = 1 #symmetric
        self.h0_cen = 0

        # creation of the motor, we don't know all the relative positions
        # so we create it at pos_d=pos_w = 0, pos_h = 1

        nema_motor = comps.PartNemaMotor (
                              nema_size = nema_size,
                              base_l = base_l,
                              shaft_l = shaft_l,
                              shaft_r = shaft_r,
                              circle_r = circle_r,
                              circle_h = circle_h,
                              chmf_r = chmf_r, 
                              rear_shaft_l= rear_shaft_l,
                              bolt_depth = bolt_depth,
                              bolt_out  = 0,
                              cut_extra = 0,
                              axis_d = self.axis_d,
                              axis_w = self.axis_w,
                              axis_h = self.axis_h,
                              pos_d = 0,
                              pos_w = 0,
                              pos_h = 1,
                              pos = pos)

        self.append_part(nema_motor)
        nema_motor.parent = self

        self.shaft_r = nema_motor.shaft_r
        self.circle_r = nema_motor.circle_r
        self.circle_h = nema_motor.circle_h

        # creation of the pulley. Locate it at pos_d,w,h = 0
        gt_pulley = comps.PartGtPulley (
                              pitch = pulley_pitch,
                              n_teeth = pulley_n_teeth,
                              toothed_h = pulley_toothed_h,
                              top_flange_h = pulley_top_flange_h,
                              bot_flange_h = pulley_bot_flange_h,
                              tot_h = pulley_tot_h,
                              flange_d = pulley_flange_d,
                              base_d = pulley_base_d,
                              shaft_d = 2 * self.shaft_r,
                              tol = 0,
                              axis_d = self.axis_d,
                              axis_w = self.axis_w,
                              axis_h = self.axis_h,
                              pos_d = 0,
                              pos_w = 0,
                              pos_h = 0,
                              pos = pos,
                              model_type = 1) # dimensional model

        if pulley_pos_h < 0: #top of the pulley aligned with top of the shaft
            # shaft_l includes the length of the circle
            pulley_pos_h = shaft_l - self.circle_h - gt_pulley.tot_h
            self.pulley_pos_h = pulley_pos_h
        elif pulley_pos_h + gt_pulley.base_h > shaft_l:
            logger.warning("pulley seems to be out of the shaft")

        self.append_part(gt_pulley)
        gt_pulley.parent = self

        # conversions of the relative points from the parts to the total set
        self.d_o[0] = nema_motor.d_o[0] # V0
        self.d_o[1] = nema_motor.d_o[1]
        self.d_o[2] = nema_motor.d_o[2]
        self.d_o[3] = nema_motor.d_o[3]
        self.d_o[4] = nema_motor.d_o[4]
        self.d_o[5] = gt_pulley.d_o[1]
        self.d_o[6] = gt_pulley.d_o[2]
        self.d_o[7] = gt_pulley.d_o[3]
        self.d_o[8] = gt_pulley.d_o[4]
        self.d_o[9] = gt_pulley.d_o[5]

        self.w_o[0] = nema_motor.w_o[0] # V0
        self.w_o[1] = nema_motor.w_o[1]
        self.w_o[2] = nema_motor.w_o[2]
        self.w_o[3] = nema_motor.w_o[3]
        self.w_o[4] = nema_motor.w_o[4]
        self.w_o[5] = gt_pulley.w_o[1]
        self.w_o[6] = gt_pulley.w_o[2]
        self.w_o[7] = gt_pulley.w_o[3]
        self.w_o[8] = gt_pulley.w_o[4]
        self.w_o[9] = gt_pulley.w_o[5]

        self.h_o[0] = nema_motor.h_o[0]
        self.h_o[1] = nema_motor.h_o[1] # V0
        self.h_o[2] = nema_motor.h_o[2] # bottom of the bolt holes
        self.h_o[3] = nema_motor.h_o[3] # base of the circle
        self.h_o[4] = nema_motor.h_o[4] # base of the shaft
        self.h_o[5] = nema_motor.h_o[5]
        # position of the base of the shaft (including the circle)
        # + nema_motor.h_o[4]
        # relative position of the base of the pulley: V0 (not needed)
        # + gt_pulley.h_o[0] = V0 -> base of the pulley
        # distance from the base of the shaft (circle included) to the base
        # of the pulley
        # + self.vec_h(self.pulley_pos_h): dis
        self.h_o[6]  = nema_motor.h_o[4] + self.vec_h(self.pulley_pos_h)
        self.h_o[7]  = self.h_o[6] + gt_pulley.h_o[1]
        self.h_o[8]  = self.h_o[6] + gt_pulley.h_o[2]
        self.h_o[9]  = self.h_o[6] + gt_pulley.h_o[3]
        self.h_o[10] = self.h_o[6] + gt_pulley.h_o[4]
        self.h_o[11] = self.h_o[6] + gt_pulley.h_o[5]

        # check if the pulley is on top of the shaft or not:
        if self.h_o[11].Length > self.h_o[5].Length:
            self.tot_h = self.h_o[11].Length + self.h_o[0].Length
        else:
            self.tot_h = self.h_o[5].Length + self.h_o[0].Length

        self.set_pos_o(adjust = 1)
        self.set_part_place(nema_motor)
        self.set_part_place(gt_pulley, self.get_o_to_h(6))

        self.place_fcos()

    def get_nema_motor(self):
        """ gets the nema motor"""
        part_list = self.get_parts()
        for part_i in part_list:
            if isinstance(part_i, PartNemaMotor):
                return part_i

    def get_gt_pulley(self):
        """ gets the gt2 pulley"""
        part_list = self.get_parts()
        for part_i in part_list:
            if isinstance(part_i, PartGtPulley):
                return part_i


 

motor_pulley = NemaMotorPulleySet(pulley_pos_h = 10,
                                  rear_shaft_l = 10,
                                  axis_d = VZ,
                                  axis_w = None,
                                  axis_h = VX,
                                  pos_d = 2,
                                  pos_w = 0,
                                  pos_h = 0,
                                  pos = V0,
                                  )

