# ----------------------------------------------------------------------------
# -- Classes for FreeCAD pieces, parts, part sets
# ----------------------------------------------------------------------------
# -- (c) Felipe Machado
# -- Area of Electronic Technology. Rey Juan Carlos University (urjc.es)
# -- https://github.com/felipe-m/fcad-comps
# -- December-2017
# ----------------------------------------------------------------------------
# --- LGPL Licence
# ----------------------------------------------------------------------------

import os
import sys
import inspect
import logging
import math
import FreeCAD
import FreeCADGui
import Part
import DraftVecUtils
import Mesh
import MeshPart

# to get the current directory. Freecad has to be executed from the same
# directory this file is
filepath = os.getcwd()
# to get the components
# In FreeCAD can be added: Preferences->General->Macro->Macro path
sys.path.append(filepath) 
#sys.path.append(filepath + '/' + 'comps')
sys.path.append(filepath + '/../../' + 'comps')


import kcomp   # import material constants and other constants
import fcfun   # import my functions for freecad. FreeCad Functions
import shp_clss
import kparts

from fcfun import V0, VX, VY, VZ, V0ROT
from fcfun import VXN, VYN, VZN


logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


# Possible names: Single Part, Element, Piece
# Either:
# - have an attribute to indicate what kind of part is it, or
# - have subclasses to indicate the kind of part that it is
#
# Kind of possible parts are:
# 0: Not to print: It is just an outline, a rough/vague 3D model,
#                  for example bolts or bearings
#                  Some times the models dont have details, for example,
#                  bearings are just cylinders with a inner hole. Or bolts
#                  that dont have threads
# 0?: Not to print: It can be an exact model, like a washer, but it is not to
#                  print, tolerances are not inluced
# 1: Dimensional model: it can be printed to assemble a model, but the part
#                       will not work as defined. For example, optical cubes
#                       that they just have the dimmensions, but they dont
#                       have the inner holes or the threads for the bolts
# 2: Printable model: it can be printed, but better to buy it,
#                     the printed part may work well.
#                     washer. You can print it, but better get it
# 3: To be printed: an object designed to be printed

# exact. Not to print because it has no tolerances
# with tolerances (to be printed)
# rough


class SinglePart (object):
    """
    This is a 3D model that only has one part.
    It can be either a part that forms a whole object with other parts, 
    or just a piece that can be used standalone 
    This is a Parent Class of all kind of objects
    
    All the pieces have 3 axis that define their 3 main perpendicular directions
    Depth, Width, Height

    Attributes:
    ------------
    fco: FreeCAD Object
        The freecad object of this part

    place : FreeCAD Object
        When this part is an object of another one (set). This is the vector to
        place this part into the the set

    place : FreeCAD.Vector
        Position of the object
        There is the parameter pos, where the piece is built and can be at
        any position.
        Once the piece is built, its placement (Placement.Base) is at V0:
        FreeCAD.Vector(0,0,0), however it can be located at any place, since
        pos could have been set anywhere.
        The attribute place will move again the whole piece, including its parts

    color : Tuple of 3 floats, each of them from 0. to 1.
        They define the RGB colors.
        0.: no color on that channel
        1.: full intesity on that channel

    """
    def __init__(self):
        # bring the active document
        self.doc = FreeCAD.ActiveDocument

        # placement of the piece at V0, altough pos can set it anywhere
        #self.place = V0
        #self.displacement = V0
        self.rel_place = V0
        self.extra_mov = V0

        self.create_fco(self.name)
        #self.tol = tol
        #self.model_type = model_type

    def get_parts(self):
        """ returns an empty list, because it is a SinglePart.
        Therefore has no parts
        """
        return []

    def set_color (self, color = (1.,1.,1.)):
        """ Sets a new color for the piece
        pieces

        Parameters:
        -----------
        color : tuple of 3 floats from 0. to 1.
            RGB colors

        """
        # just in case the value is 0 or 1, and it is an int
        self.color = (float(color[0]),float(color[1]), float(color[2]))
        self.fco.ViewObject.ShapeColor = self.color

    def set_name (self, name = '', default_name = '', change = 0):
        """ Sets the name attribute to the value of parameter name
        if name is empty, it will take default_name.
        if change == 1, it will change the self.name attribute to name, 
            default_name
        if change == 0, if self.name is not empty, it will preserve it

        Parameters:
        -----------
        name : str
            This is the name, but it can be empty.
        default_name : str
            This is the default_name, if not name
        change : int
            1: change the value of self.name
            0: preserve the value of self.name if it exists

        """
        # attribute name has not been created
        if (not hasattr(self, 'name') or  # attribute name has not been created
            not self.name or              # attribute name is empty
            change == 1):                 # attribute has te be changed
            if not name:
                self.name = default_name
            else:
                self.name = name

    def create_fco (self, name = ''):
        """ creates a FreeCAD object of the TopoShape in self.shp

        Parameters:
        -----------
        name : str
            it is optional if there is a self.name

        """
        if not name:
            name = self.name
        fco = fcfun.add_fcobj(self.shp, name, self.doc)
        self.fco = fco


    # ----- 
    def place_fcos (self, displacement = V0):
        """ Place the freecad objects
        
        """
        #if type(place) is tuple:
        #   place = FreeCAD.Vector(place) # change to FreeCAD.Vector
        
        tot_displ = (  self.pos_o_adjust + displacement
                     + self.rel_place + self.extra_mov)
        self.tot_displ = tot_displ
        self.fco.Placement.Base = tot_displ
    
    def set_place (self, place = V0):
        """ Sets a new placement for the piece

        Parameters:
        -----------
        place : FreeCAD.Vector
            new position of the pieces
        """
        if type(place) is tuple:
            place = FreeCAD.Vector(place) # change to FreeCAD.Vector
        if type(place) is FreeCAD.Vector:
            self.fco.Placement.Base = place
            self.place = place

    # ----- Export to STL method
    def export_stl(self, prefix = "", name = ""):
        """ exports to stl the piece to print 

        Parameters:
        -----------
        prefix : str
            Prefix to the piece, may be useful if name is not given
            and want to add a prefix to the self.name
            an underscore will be added between prefix and name
        name : str
            Name of the piece, if not given, it will take self.name
        """
        if not name:
            filename = self.name
        if prefix:
            filename = prefix + '_' + filename
        
        pos0 = self.pos0
        rotation = FreeCAD.Rotation(self.prnt_ax, VZ)
        shp = self.shp
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
        #shp_cpy.translate (pos0.negative() + self.place.negative())
        #shp_cpy.rotate (V0, rotation.Axis, math.degrees(rotation.Angle))
        #shp_cpy.exportStl(stl_path + filename + 'stl')
        #shp_cpy.nullify()
        # ----------- option 2. moving the freecad object
        self.fco.Placement.Base = pos0.negative() + self.place.negative()
        self.fco.Placement.Rotation = rotation
        self.doc.recompute()

        # exportStl is not working well with FreeCAD 0.17
        #self.fco.Shape.exportStl(self.stl_path + filename + '.stl')
        mesh_shp = MeshPart.meshFromShape(self.fco.Shape,
                                          LinearDeflection=kparts.LIN_DEFL, 
                                          AngularDeflection=kparts.ANG_DEFL)
        mesh_shp.write(stlFileName)
        del mesh_shp

        self.fco.Placement.Base = self.place
        self.fco.Placement.Rotation = V0ROT
        self.doc.recompute()

    def save_fcad(self, prefix = "", name = ""):
        """ Save the FreeCAD document, actually, it may not be a class method
        only for the name

        prefix : str
            Prefix to the piece, may be useful if name is not given
            and want to add a prefix to the self.name
            an underscore will be added between prefix and name
        name : str
            Name of the piece, if not given, it will take self.name
        """
        if not name:
            filename = self.name
        if prefix:
            filename = prefix + '_' + filename

        fcad_filename = self.fcad_path + name + '.FCStd'
        print fcad_filename
        self.doc.saveAs (fcad_filename)


# Possible names: Parts     , Pieces,         Elements,
#                      Group        Ensemble,         Set, 
class PartsSet (shp_clss.Obj3D):
    """
    This is a 3D model that has a set of parts (SinglePart or others)
    
    All the pieces have 3 axis that define their 3 main perpendicular directions
    Depth, Width, Height

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

    """

    def __init__(self, axis_d, axis_w, axis_h):
        
        # bring the active document
        self.doc = FreeCAD.ActiveDocument

        shp_clss.Obj3D.__init__(self, axis_d, axis_w, axis_h)

        self.parts_lst = [] # list of all the parts (SinglePart, ...)
        self.abs_place = V0
        self.rel_place = V0
        self.extra_mov = V0
        self.displacement = V0

    def append_part (self, part):
        """ Appends a new part to the list of parts
        """
        self.parts_lst.append(part)

    def get_parts (self):
        """ get a list of the parts, 
        """
        return self.parts_lst
        
    def make_group (self):
        self.fco = self.doc.addObject("Part::Compound", self.name)
        list_fco = []
        part_list = self.get_parts()
        for part in part_list:
            try:
                fco_i = part.fco
            except AttributeError:
                logger.error('part is not a single part or compound')
            else:
                list_fco.append(fco_i)
        self.fco.Links = list_fco
        self.doc.recompute()
        
    def get_abs_place (self):
        """ gets the placement of the object, with any adjustment
        So the shape has been created at pos, and this is any movement done after this
        Movement of the freecadobject
        """
        
        return self.abs_place

    def get_rel_place (self):
        """ gets the placement of the object, with any adjustment
        So the shape has been created at pos, and this is any movement done after this
        Movement of the freecadobject
        """
        
        return self.rel_place

        
    def set_part_place(self, child_part, vec_o_to_childpart = V0, add = 0):
        """ Modifies the attribute child_part.place, which defines the
        displacement of the child_part respect to self.pos_o
        Adds this displacement to the part's children
        """
        
        rel_place = self.pos_o_adjust + vec_o_to_childpart
        if add == 0:
            child_part.rel_place = rel_place
        else:
            child_part.rel_place = child_part.rel_place + rel_place
        #child_part.abs_place = self.get_abs_place() + child_part.rel_place
        #try:
        #    child_part.fco.Placement.Base = child_part.abs_place
        #except AttributeError: # only SimpleParts objects have fco, not PartsSet
        #    pass
        # add this displacement to all the children
        #part_list = child_part.get_parts()
        #for grandchild_i in part_list:
            #child_part.set_part_place(grandchild_i, add = 1)
        
        
    def mov_place(self, child_part, vec_o_to_childpart = V0):
        """ Modifies the attribute child_part.place, which defines the
        displacement of the child_part respect to self.pos_o
        Adds this displacement to the part's children
        """
        
        displacement = (self.pos_o - self.pos) + vec_o_to_childpart + self.place
        child_part.place = child_part.place + displacement
        try:
            child_part.fco.Placement.Base = child_part.place
        except AttributeError: # only SimpleParts objects have fco, not PartsSet
            pass
        # add this displacement to all the children
        part_list = child_part.get_parts()
        for grandchild_i in part_list:
            child_part.add_part_place(grandchild_i)
        
    def set_color (self, color = (1.,1.,1.), part_i = 0):
        """ Sets a new color for the whole set of parts or for the selected
        parts

        Parameters:
        -----------
        color : tuple of 3 floats from 0. to 1.
            RGB colors
        part_i : int
            index of the part to change the color
            0: all the parts
            1... the index of the part

        """
        # just in case the value is 0 or 1, and it is an int
        color = (float(color[0]),float(color[1]), float(color[2]))
        if part_i == 0:
            self.color = color #only if all the parts have the same color
            for part in self.parts_lst:  # list of SinglePart objects
                part.set_color(color)
        else:
            self.parts_lst[part_i-1].set_color(color)

    # ----- 
    def place_fcos (self, displacement = V0):
        """ Place the freecad objects
        """
        #if type(place) is tuple:
        #   place = FreeCAD.Vector(place) # change to FreeCAD.Vector
        
        # having pos_o_adjust and rel_place made the sum twice
        #tot_displ = (  self.pos_o_adjust + displacement 
        tot_displ = (  displacement 
                     + self.rel_place + self.extra_mov)
        self.tot_displ = tot_displ
        #if this set has been grouped, we dont have to go to its children
        try:
            self.fco.Placement.Base = tot_displ
        except AttributeError:
            # Not grouped: set the new position for every freecad object
            for part in self.parts_lst:
                part.place_fcos(tot_displ)


    # ----- Export to STL method
    def export_stl(self, part_i = 0, prefix = ""):
        """ exports to stl the part or the parts to print
        Save them in a STL file

        Parameters:
        -----------
        part_i : int
            index of the part to print
            0: all the printable parts
            1... index of the part

        prefix : str
            Prefix to all the parts
        """
        
        if part_i == 0: # export all the parts
            for part in self.parts_lst:
                part.export_stl(prefix = prefix)
        else:
            self.parts_lst[part_i-1].export_stl(prefix = prefix)


    def save_fcad(self, prefix = "", name = ""):
        """ Save the FreeCAD document, actually, it may not be a class method
        only for the name

        prefix : str
            Prefix to the name, may be useful if name is not given
            and want to add a prefix to the self.name
            an underscore will be added between prefix and name
        name : str
            Name of the part, if not given, it will take self.name
        """
        if not name:
            filename = self.name
        if prefix:
            filename = prefix + '_' + filename

        fcad_filename = self.fcad_path + name + '.FCStd'
        print fcad_filename
        self.doc.saveAs (fcad_filename)

    def set_name (self, name = '', default_name = '', change = 0):
        """ Sets the name attribute to the value of parameter name
        if name is empty, it will take default_name.
        if change == 1, it will change the self.name attribute to name, 
            default_name
        if change == 0, if self.name is not empty, it will preserve it

        Parameters:
        -----------
        name : str
            This is the name, but it can be empty.
        default_name : str
            This is the default_name, if not name
        change : int
            1: change the value of self.name
            0: preserve the value of self.name if it exists

        """
        # attribute name has not been created
        if (not hasattr(self, 'name') or  # attribute name has not been created
            not self.name or              # attribute name is empty
            change == 1):                 # attribute has te be changed
            if not name:
                self.name = default_name
            else:
                self.name = name






class Washer (SinglePart, shp_clss.ShpCylHole):
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
        0: the cylinder pos is centered along its height
        1: the cylinder pos is at its base
    tol : float
        Tolerance for the inner and outer radius.
        Being an outline, probably it is not to print, so by default: tol = 0
        It is the tolerance for the diameter, so the radius will be added/subs
        have of this tolerance
        tol will be added to the inner radius (so it will be larger)
        tol will be substracted to the outer radius (so it will be smaller)
        
    model_type : int
        type of model:
        exact, outline
    pos : FreeCAD.Vector
        Position of the cylinder, taking into account where the center is

    Attributes:
    -----------
    All the parameters and attributes of parent classes SinglePart ShpCylHole

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

        tol_r = tol / 2.

        # First the shape is created
        shp_clss.ShpCylHole.__init__(self, r_out = r_out, r_in = r_in,
                                     h = h, axis_h = axis_h,
                                     pos_h = pos_h,
                                     # inside tolerance is more
                                     xtr_r_in = tol_r,
                                     # outside tolerance is less
                                     xtr_r_out = - tol_r,
                                     pos = pos)

        # Then the Part
        SinglePart.__init__(self)

        # save the arguments as attributes:
        frame = inspect.currentframe()
        args, _, _, values = inspect.getargvalues(frame)
        for i in args:
            if not hasattr(self,i): # so we keep the attributes by CylHole
                setattr(self, i, values[i])



class Din125Washer (Washer):
    """ Din 125 Washer, this is the regular washer

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
        0: exact, 1: outline
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
        0: exact, 1: outline
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




#doc = FreeCAD.newDocument()
#washer = Din125Washer( metric = 5,
#                    axis_h = VZ, pos_h = 1, tol = 0, pos = V0,
#                    model_type = 0, # exact
#                    name = '')
#wash = Din9021Washer( metric = 5,
#                    axis_h = VZ, pos_h = 1, tol = 0,
#                    pos = washer.pos + DraftVecUtils.scale(VZ,washer.h),
#                    model_type = 0, # exact
#                    name = '')


class BearingOutl (SinglePart, shp_clss.ShpCylHole):
    """ Bearing outline , that is, a cylinder with a inner hole.
    It does not include the balls and parts

    Parameters:
    -----------
    bearing_nb : int
        Bearing number code
    axis_h : FreeCAD.Vector
        vector along the cylinder height
    pos_h : int
        location of pos along axis_h (0,1)
        0: the cylinder pos is centered along its height
        1: the cylinder pos is at its base
    axis_d : FreeCAD.Vector
        vector along the cylinder radius, a direction perpendicular to axis_h
        it is not necessary if pos_d == 0
        It can be None, but if None, axis_w has to be None
    axis_w : FreeCAD.Vector
        vector along one radius (perpendicular to axis_h and axis_d)
        it can be None
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
    tol : float
        Tolerance for the inner and outer radius.
        It is the tolerance for the diameter, so the radius will be added/subs
        have of this tolerance
        tol will be added to the inner radius (so it will be larger)
        tol will be substracted to the outer radius (so it will be smaller)
        
    pos : FreeCAD.Vector
        Position of the cylinder, taking into account where the center is

    Attributes:
    -----------
    All the parameters and attributes of parent classes SinglePart ShpCylHole

    metric : int or float (in case of M2.5) or even str for inches ?
        Metric of the washer

    model_type : int
        type of model:
        1: outline (is not an exact model)

    bearing_nb : int
        number of the bearing, such as 624, 608, ... see kcomp.BEARING
    bear_d : dictionary
        dictionary with the dimensions of the bearing

    """
    def __init__(self, bearing_nb, axis_h, pos_h,
                 axis_d = None, axis_w = None,
                 pos_d = 0, pos_w = 0, tol = 0, pos = V0,
                 name = ''):

        self.model_type = 1 # outline
        # sets the object name if not already set by a child class
        default_name = 'bearing_' + str(bearing_nb) 
        self.set_name (name, default_name, change = 0)
        self.bearing_nb = bearing_nb

        print bearing_nb
        print default_name

        try:
            bear_d = kcomp.BEARING[bearing_nb]
            self.bear_d = bear_d
        except KeyError:
            logger.error('Bearing key not found: ' + str(bearing_nb))
        else: # no exception:
            if tol == 0:
                tol_r = 0
            else:
                tol_r = tol / 2. #just in case there is tolerance
            # First the shape is created
            shp_clss.ShpCylHole.__init__(self,
                                         r_out = bear_d['do']/2.,
                                         r_in = bear_d['di']/2.,
                                         h = bear_d['t'],
                                         axis_h = axis_h,
                                         axis_d = axis_d,
                                         axis_w = axis_w,
                                         pos_d = pos_d,
                                         pos_w = pos_w,
                                         pos_h = pos_h,
                                         # inside tolerance is more
                                         xtr_r_in = tol_r,
                                         # outside tolerance is less
                                         xtr_r_out = - tol_r,
                                         pos = pos)

            # Then the Part
            SinglePart.__init__(self)


#bear = BearingOutl( bearing_nb = 608,
#                    axis_h = VZN, pos_h = 1, tol = 0,
#                    pos = washer.pos + DraftVecUtils.scale(VZN,washer.h),
#                    name = '')




class BearWashSet (PartsSet):
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

        PartsSet.__init__(self,
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
            lwash_b = Din9021Washer(metric= self.lwash_m,
                                    axis_h = self.axis_h,
                                    pos_h = 1,
                                    pos = self.pos_o,
                                    name = 'idlpull_lwash_bt')
            self.append_part(lwash_b)
            # creation of the bottom regular washer
            rwash_b = Din125Washer(metric= metric,
                                   axis_h = self.axis_h,
                                   pos_h = 1,
                                   pos = lwash_b.get_pos_h(1),
                                   name = 'idlpull_rwash_bt')
            self.append_part(rwash_b)
            # creation of the bearing
            bearing = BearingOutl(bearing_nb = self.bear_type,
                                  axis_h = self.axis_h,
                                  pos_h = 1,
                                  axis_d = self.axis_d,
                                  axis_w = self.axis_w,
                                  pos = rwash_b.get_pos_h(1),
                                  name = 'idlpull_bearing')
            self.append_part(bearing)
            # creation of the top regular washer
            rwash_t = Din125Washer(metric= metric,
                                   axis_h = self.axis_h,
                                   pos_h = 1,
                                   pos = bearing.get_pos_h(1),
                                   name = 'idlpull_rwash_tp')
            self.append_part(rwash_t)
            # creation of the top large washer
            lwash_t = Din9021Washer(metric= self.lwash_m,
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

