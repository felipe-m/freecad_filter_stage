# ----------------------------------------------------------------------------
# -- Classes for FreeCAD pieces or parts
# ----------------------------------------------------------------------------
# -- (c) Felipe Machado
# -- Area of Electronic Technology. Rey Juan Carlos University (urjc.es)
# -- https://github.com/felipe-m/freecad_filter_stage
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

import kcomp   # import material constants and other constants
import fcfun   # import my functions for freecad. FreeCad Functions

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
# 0: Not to print: It is just a rough 3D model, for example bolts or bearings
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
    shp : TopoShape
        The shape of this part
    fco: FreeCAD Object
        The freecad object of this part
    print_ax: FreeCAD.Vector
        The best direction to print, pointing upwards
        it can be V0 if there is no best direction

    place : FreeCAD.Vector
        Position of the tensioner set.
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
    def __init__(self, axis_d = None, axis_w = None, axis_h = None,
                 model_type = 2, tol = kcomp.TOL):
        # bring the active document
        self.doc = FreeCAD.ActiveDocument

        if axis_h is not None:
            axis_h = DraftVecUtils.scaleTo(axis_h,1)
        if axis_d is not None:
            axis_d = DraftVecUtils.scaleTo(axis_d,1)
        if axis_w is not None:
            axis_w = DraftVecUtils.scaleTo(axis_w,1)
        self.axis_d = axis_d
        self.axis_w = axis_w
        self.axis_h = axis_h

        # -- initializing pos_d, pos_w, pos_h vectors:
        self.d0to = {0 : V0} #d0to[0] = V0 # no distance from 0 to 0
        self.w0to = {0 : V0} #w0to[0] = V0 # no distance from 0 to 0
        self.h0to = {0 : V0} #h0to[0] = V0 # no distance from 0 to 0

        # placement of the piece at V0, altough pos can set it anywhere
        self.place = V0

        self.tol = tol
        self.model_type = model_type
        # default values
        self.print_ax = V0
        self.shp = None
        self.fco = None

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
        self.fco_.ViewObject.ShapeColor = self.color

    # ----- 
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
        self.fco.Shape.exportStl(self.stl_path + filename + '.stl')
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
class PartsSet (object):
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

        axis_d = DraftVecUtils.scaleTo(axis_d,1)
        axis_h = DraftVecUtils.scaleTo(axis_h,1)
        if axis_w == V0:
            # this happens when is symmetrical on the width
            axis_w = axis_h.cross(axis_d)
        else:
            axis_w = DraftVecUtils.scaleTo(axis_w,1)
        self.axis_d = axis_d
        self.axis_w = axis_w
        self.axis_h = axis_h

        # -- initializing pos_d, pos_w, pos_h vectors:
        self.d0to = {0 : V0} #d0to[0] = V0 # no distance from 0 to 0
        self.w0to = {0 : V0} #w0to[0] = V0 # no distance from 0 to 0
        self.h0to = {0 : V0} #h0to[0] = V0 # no distance from 0 to 0

        self.parts_lst = [] # list of all the parts (SinglePart, ...)


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
    def set_place (self, place = V0):
        """ Sets a new placement for whole set of parts

        Parameters:
        -----------
        place : FreeCAD.Vector
            new position of the parts
        """
        if type(place) is tuple:
            place = FreeCAD.Vector(place) # change to FreeCAD.Vector
        if type(place) is FreeCAD.Vector:
            # set the new position for every freecad object
            for part in self.parts_lst:
                part.set_place(place)
            self.place = place

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


