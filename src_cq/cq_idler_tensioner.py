#  Idler pulley tensioner
#  CadQuery version
# ----------------------------------------------------------------------------
# -- (c) Felipe Machado
# -- Area of Electronic Technology. Rey Juan Carlos University (urjc.es)
# -- https://github.com/felipe-m
# -- October-2019
#
# ----------------------------------------------------------------------------
# --- LGPL Licence
# ----------------------------------------------------------------------------
# 
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


import os
import sys
import FreeCAD
import FreeCADGui
import Part
import Mesh
import MeshPart
import cadquery as cq

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
import comps   # import my CAD components
import kidler  # import constants for the idler tensioner and holder
import kparts


def idler_tens ():
    # bring the active document
    doc = FreeCAD.ActiveDocument


    #  --------------- step 01 ---------------------------      
    #  rectangular cuboid with basic dimensions
    # 
    #           Z
    #           :.....tens_l.......
    #           :_________________:
    #           /                /|
    #          /                / |
    #       ../________________/  |..............Y     .
    #      :  |                |  /     . 
    # tens_h  |                | /     . tens_w
    #       :.|________________|/......
    #        .
    #       .
    #      X 
    #
    # oscad: cube([tens_w, tens_l, tens_h]);
    cq01 = cq.Workplane("XY").box(kidler.tens_w, kidler.tens_l, kidler.tens_h,
                                  centered=(False, False, False));

    # creates the shape, you don't see it yet on FreeCAD Gui
    #shp01 = fcfun.shp_boxcen(kidler.tens_w, kidler.tens_l, kidler.tens_h)
    # creates a freecad object from the shape, to see it in FreeCAD Gui,
    # not necessary, but illustrative for this tutorial
    #fcd01 = fcfun.add_fcobj(shp01, 'box01')

    #  --------------- step 02 ---------------------------  
    # Space for the idler pulley
    #      Z
    #      :
    #      :_______________________
    #      |                 ______|....
    #      |                /          + idler_h
    #      |               |           :
    #      |                \______....:
    #      |_______________________|...wall_thick.......> Y
    #                      :       :
    #                      :.......:
    #                         +
    #                       2 * idler_r_xtr
    #
    # oscad: translate ([-1, tens_l - 2*idler_r_xtr, wall_thick])
    # ...
    cq02 = cq.Workplane("XY", origin=(0, kidler.tens_l - 2*kidler.idler_r_xtr,
                                         kidler.wall_thick)).\
                               box(kidler.tens_w,
                                  2 * kidler.idler_r_xtr +1 + kidler.in_fillet,
                                  kidler.idler_h,centered=(False,False,False)).\
                               faces("<Y").\
                               edges("|X").fillet(kidler.in_fillet)
    cq02 = cq01.cut(cq02)

    #  --------------- step 03 --------------------------- 
    # Fillets at the idler end:

    #      Z
    #      :
    #      :_______________________f2
    #      |                 ______|
    #      |                /      f4
    #      |               |
    #      |                \______f3...
    #      |_______________________|....+ wall_thick.....> Y
    #      :                       f1
    #      :...... tens_l .........:
    #
    cq03 = cq02.faces(">Y").edges("|X").fillet(kidler.in_fillet)

    #  --------------- step 04 --------------------------- 
    # Chamfers at the nut end:

    #      Z
    #      :
    #      : ______________________
    #    ch2/                ______|
    #      |                /             
    #      |               |        
    #      |                \______
    #    ch1\______________________|.............> Y
    #      :                       :
    #      :...... tens_l .........:
    # 
    cq04 = cq03.faces("<Y").edges("|X").chamfer(2*kidler.in_fillet)

   #  --------------- step 04b OPTIONAL---------------------- 
   #  Chamfers at the nut end on axis Z, they are 45 degrees
   #  so they should print ok without support, but you may
   #  not want to have them

   #        ________ ....> X
   #    ch1/________\ch2
   #       |        |
   #       |        |
   #       |        |
   #       |        |
   #       |        |
   #       |        |
   #       |........|
   #       |        |
   #       |        |
   #       |        |
   #       |________|
   #       :
   #       Y
   #       
   # 

    if (kidler.opt_tens_chmf == 1) : # optional tensioner chamfer
        cq04 = cq04.faces("<Y").edges("|Z").chamfer(2*kidler.in_fillet)
        

    #  --------------- step 05 --------------------------- 
    # Shank hole for the idler pulley:

    #      Z                     idler_r_xtr
    #      :                    .+..
    #      : ___________________:__:
    #       /                __:_:_|
    #      |                /             
    #      |               |        
    #      |                \______
    #       \__________________:_:_|.............> Y
    #      :                       :
    #      :...... tens_l .........:
    #                     
    cq05_hole = cq.Workplane("XY",origin=(kidler.tens_w/2.,
                                       kidler.tens_l - kidler.idler_r_xtr,0)).\
                          circle(kidler.boltidler_r_tol).extrude(kidler.tens_h)
    fcd05 = doc.addObject("Part::Feature", 'step05')
    fcd05.Shape = cq05_hole.toFreecad()
    fcd05.ViewObject.ShapeColor = (1.0, 1., 0.0) # yellow
    fcd05.ViewObject.Visibility = False
    cq05 = cq04.cut(cq05_hole)


    #  --------------- step 06 --------------------------- 
    # Hole for the leadscrew (stroke):

    #      Z
    #      :
    #      : ______________________
    #       /      _____     __:_:_|
    #      |    f2/     \f4 /             
    #      |     |       | |        
    #      |    f1\_____/f3 \______
    #       \__________________:_:_|.............> Y
    #      :     :       :         :
    #      :     :.......:         :
    #      :     :   +             :
    #      :.....:  tens_stroke    :
    #      :  +                    :
    #      : nut_holder_total      :
    #      :                       :
    #      :...... tens_l .........:
    # 

    cq06_cut = cq.Workplane("XY",origin=(0,kidler.nut_holder_total,
                                      kidler.wall_thick)).\
                         box(kidler.tens_w, kidler.tens_stroke,kidler.idler_h,
                             centered=(False,False,False)).\
                         edges("|X").chamfer(kidler.in_fillet)
    fcd06 = doc.addObject("Part::Feature", 'step06')
    fcd06.Shape = cq06_cut.toFreecad()
    fcd06.ViewObject.ShapeColor = (1.0, 0.5, 0.0) # orange
    fcd06.ViewObject.Visibility = False

    cq06 = cq05.cut(cq06_cut)


    
    #  --------------- step 07 --------------------------- 
    # Hole for the leadscrew shank at the beginning

    #      Z
    #      :
    #      : ______________________
    #       /      _____     __:_:_|
    #      |      /     \   /
    #      |:::::|       | |
    #      |      \_____/   \______
    #       \__________________:_:_|.............> Y
    #      :     :                 :
    #      :     :                 :
    #      :     :                 :
    #      :.....:                 :
    #      :  +                    :
    #      : nut_holder_total      :
    #      :                       :
    #      :...... tens_l .........:
    #
    #oscad: translate ([tens_w/2, -1, tens_h/2])
    cq07_hole = cq.Workplane("XZ",
                          origin=(kidler.tens_w/2.,0, kidler.tens_h/2.)).\
                          circle(kidler.bolttens_r_tol).\
                          extrude(-kidler.nut_holder_total)
    fcd07 = doc.addObject("Part::Feature", 'step07')
    fcd07.Shape = cq07_hole.toFreecad()
    fcd07.ViewObject.ShapeColor = (1.0, 0.0, 0.0) # red
    fcd07.ViewObject.Visibility = False

    cq07 = cq06.cut(cq07_hole)


    #  --------------- step 08 --------------------------- 
    # Hole for the leadscrew nut

    #      Z
    #      :
    #      : ______________________
    #       /      _____     __:_:_|
    #      |  _   /     \   /
    #      |:|_|:|       | |
    #      |      \_____/   \______
    #       \__________________:_:_|.............> Y
    #      : :   :                 :
    #      :+    :                 :
    #      :nut_holder_thick       :
    #      :.....:                 :
    #      :  +                    :
    #      : nut_holder_total      :
    #      :                       :
    #      :...... tens_l .........:


    #oscad: tens_w/2-1 to have more tolerance, so it is a little bit deeper
    #oscad: translate ([tens_w/2-1, nut_holder_thick, tens_h/2])
    #cq: move more the radius to the left, and make chamfer to avoid the 
    # calculation of the hexagon
    cq08_nut = cq.Workplane("XZ",origin=(
                                 kidler.tens_w/2.-1-kidler.tensnut_circ_r_tol ,
                                 kidler.nut_holder_thick+kidler.nut_space,
                                 kidler.tens_h/2)).\
                         box(kidler.tens_w/2.+1+kidler.tensnut_circ_r_tol,
                             kidler.tens_h/2.,  kidler.nut_space,
                             centered=(False,True,False))#.\
                         #faces("<X").edges("|Y").chamfer(kidler.tens_h/2.-1.5)

    fcd08_nut = doc.addObject("Part::Feature", 'step08_nut')
    fcd08_nut.Shape = cq08_nut.toFreecad()
    fcd08_nut.ViewObject.ShapeColor = (0.0, 1., 0.0) # green

    

    # --------- step 09:
    cq09 = cq07.cut(cq08_nut)
    fcd09 = doc.addObject("Part::Feature", 'idler_tensioner')
    fcd09.Shape = cq09.toFreecad()

    return fcd09
    


# creation of a new FreeCAD document
doc = FreeCAD.newDocument()
# creation of the idler tensioner
fcd_idler_tens = idler_tens()
#fcd_idler_tens.ViewObject.ShapeColor = fcfun.LSKYBLUE
# change color to orange:
fcd_idler_tens.ViewObject.ShapeColor = (1.0, 0.5, 0.0)


# ---------- export to stl
stlPath = filepath + '/../stl/'
stlFileName = stlPath + 'idler_tensioner' + '.stl'
# rotate to print without support:
#fcd_idler_tens.Placement.Rotation = (
                    #FreeCAD.Rotation(FreeCAD.Vector(0,1,0), -90))
# exportStl is not working well with FreeCAD 0.17
#fcd_idler_tens.Shape.exportStl(stlFileName)
#mesh_shp = MeshPart.meshFromShape(fcd_idler_tens.Shape,
                                  #LinearDeflection=kparts.LIN_DEFL, 
                                  #AngularDeflection=kparts.ANG_DEFL)
#mesh_shp.write(stlFileName)
#del mesh_shp

# rotate back
#fcd_idler_tens.Placement.Rotation = (
                    #FreeCAD.Rotation(FreeCAD.Vector(1,0,0), 0))

# save the FreeCAD file
freecadPath = filepath + '/../freecad/'
freecadFileName = freecadPath + 'idler_tensioner' + '.FCStd'
#doc.saveAs (freecadFileName)

