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
import fc_clss # import my freecad classes 
import comps   # import my CAD components
import partgroup 

from fcfun import V0, VX, VY, VZ, V0ROT
from fcfun import VXN, VYN, VZN

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class CylHole (fc_clss.SinglePart):
    """ Cylinder with a inner hole

    Parameters:
    -----------
    r_out : float
        external (outside) radius
    r_in : float
        internal radius
    h : float
        height
    axis_h : FreeCAD.Vector
        vector along the cylinder height
    pos_h : int
        location of pos along axis_h (0,1)
        0: the cylinder pos is at its base
        1: the cylinder pos is centered along its height
    tol : float
        Tolerance for the inner and outer radius.
        It is the tolerance for the diameter, so the radius will be added/subs
        have of this tolerance
        tol will be added to the inner radius (so it will be larger)
        tol will be substracted to the outer radius (so it will be smaller)
        
    pos : FreeCAD.Vector
        Position of the cylinder, taking into account where the center is

    name : str
        it is optional if there is a self.name 

    create_fco : int
        1: creates a freecad object from the TopoShape
        0: just creates the TopoShape

    Attributes:
    -----------
    All the parameters and attributes of father class SinglePart

    print_ax : FreeCAD.Vector
        Best axis to print (normal direction, pointing upwards)

    """
    def __init__(self, r_out, r_in, h, axis_h, pos_h,
                 axis_ra = None, axis_rb = None,
                 pos_ra = 0, pos_rb = 0,
                 tol = 0, pos = V0,
                 model_type = 0,
                 name = '', create_fco = 1):

        self.set_name (name, default_name = 'hollow_cylinder', change = 0)

        fc_clss.SinglePart.__init__(self, axis_h = axis_h,
                                    model_type = model_type, tol = tol)
        #super().__init__(axis_d, axis_w, axis_h)
        #fc_clss.PartsSet.__init__(self, axis_d, axis_w, axis_h)

        # normal axes to print without support
        self.prnt_ax = self.axis_h

        tol_r = self.tol /2.
        shp_washer = fcfun.shp_cylhole_gen(r_out = r_out,
                                           r_in = r_in,
                                           h = h,
                                           axis_h = self.axis_h,
                                           pos_h = pos_h,
                                           xtr_r_in = tol_r,
                                           # outside tolerance is less
                                           xtr_r_out = - tol_r,
                                           pos = pos)
        self.shp = shp_washer
        # --- FreeCAD object creation
        if create_fco == 1:
            self.create_fco(name)



class Washer (CylHole):
    """ Washer, that is, a cylinder with a inner hole

    Parameters:
    -----------
    r_out : float
        external (outside) radius
    r_in : float
        internal radius
    h : float
        height
    axis_h : FreeCAD.Vector
        vector along the cylinder height
    pos_h : int
        location of pos along axis_h (0,1)
        0: the cylinder pos is at its base
        1: the cylinder pos is centered along its height
    tol : float
        Tolerance for the inner and outer radius.
        It is the tolerance for the diameter, so the radius will be added/subs
        have of this tolerance
        tol will be added to the inner radius (so it will be larger)
        tol will be substracted to the outer radius (so it will be smaller)
        
    model_type : int
        type of model:
        exact, rough
    pos : FreeCAD.Vector
        Position of the cylinder, taking into account where the center is

    Attributes:
    -----------
    All the parameters and attributes of father class CylHole

    metric : int or float (in case of M2.5) or even str for inches ?
        Metric of the washer

    """
    def __init__(self, r_out, r_in, h, axis_h, pos_h, tol = 0, pos = V0,
                 model_type = 0, # exact
                 name = ''):

        # sets the object name if not already set by a child class
        if not hasattr(self, 'metric'):
            self.metric = int(2 * r_in)
        default_name = 'washer' + str(self.metric)
        self.set_name (name, default_name, change = 0)

        CylHole.__init__(self, r_out = r_out, r_in = r_in,
                         h = h, axis_h = axis_h,
                         pos_h = pos_h,
                         tol = tol, pos = pos,
                         model_type = model_type)


        # save the arguments as attributes:
        frame = inspect.currentframe()
        args, _, _, values = inspect.getargvalues(frame)
        for i in args:
            if not hasattr(self,i): # so we keep the attributes by CylHole
                setattr(self, i, values[i])




class Din125Washer (Washer):
    """ Din 125 Washer, this is the small washer

    Parameters:
    -----------
    metric : int (maybe float: 2.5)
 
    axis_h : FreeCAD.Vector
        vector along the cylinder height
    pos_h : int
        location of pos along axis_h (0,1)
        0: the cylinder pos is at its base
        1: the cylinder pos is centered along its height
    tol : float
        Tolerance for the inner and outer radius.
        It is the tolerance for the diameter, so the radius will be added/subs
        have of this tolerance
        tol will be added to the inner radius (so it will be larger)
        tol will be substracted to the outer radius (so it will be smaller)
    model_type : int
        type of model:
        exact, rough
    pos : FreeCAD.Vector
        Position of the cylinder, taking into account where the center is

    Attributes:
    -----------
    All the parameters and attributes of father class CylHole

    metric : int or float (in case of M2.5) or even str for inches ?
        Metric of the washer

    model_type : int
    """
    def __init__(self, metric, axis_h, pos_h, tol = 0, pos = V0,
                 model_type = 0, # exact
                 name = ''):

        # sets the object name if not already set by a child class
        self.metric = metric
        default_name = 'din125_washer_m' + str(self.metric)
        self.set_name (name, default_name, change = 0)

        washer_dict = kcomp.D125[metric]
        Washer.__init__(self,
                        r_out = washer_dict['do']/2.,
                        r_in = washer_dict['di']/2.,
                        h = washer_dict['t'],
                        axis_h = axis_h,
                        pos_h = pos_h,
                        tol = tol, pos = pos,
                        model_type = model_type)


class Din9021Washer (Washer):
    """ Din 9021 Washer, this is the larger washer

    Parameters:
    -----------
    metric : int (maybe float: 2.5)
 
    axis_h : FreeCAD.Vector
        vector along the cylinder height
    pos_h : int
        location of pos along axis_h (0,1)
        0: the cylinder pos is at its base
        1: the cylinder pos is centered along its height
    tol : float
        Tolerance for the inner and outer radius.
        It is the tolerance for the diameter, so the radius will be added/subs
        have of this tolerance
        tol will be added to the inner radius (so it will be larger)
        tol will be substracted to the outer radius (so it will be smaller)
    model_type : int
        type of model:
        exact, rough
    pos : FreeCAD.Vector
        Position of the cylinder, taking into account where the center is

    Attributes:
    -----------
    All the parameters and attributes of father class CylHole

    metric : int or float (in case of M2.5) or even str for inches ?
        Metric of the washer

    model_type : int
    """
    def __init__(self, metric, axis_h, pos_h, tol = 0, pos = V0,
                 model_type = 0, # exact
                 name = ''):

        # sets the object name if not already set by a child class
        self.metric = metric
        default_name = 'din9021_washer_m' + str(self.metric)
        self.set_name (name, default_name, change = 0)

        washer_dict = kcomp.D9021[metric]
        Washer.__init__(self,
                        r_out = washer_dict['do']/2.,
                        r_in = washer_dict['di']/2.,
                        h = washer_dict['t'],
                        axis_h = axis_h,
                        pos_h = pos_h,
                        tol = tol, pos = pos,
                        model_type = model_type)




doc = FreeCAD.newDocument()
washer = Din125Washer( metric = 5,
                    axis_h = VZ, pos_h = 0, tol = 0, pos = V0,
                    model_type = 0, # exact
                    name = '')
wash = Din9021Washer( metric = 5,
                    axis_h = VZ, pos_h = 0, tol = 0,
                    pos = washer.pos + DraftVecUtils.scale(VZ,washer.h),
                    model_type = 0, # exact
                    name = '')

