#  Nema motor holder
#  check in the project for src/comps/parts.py
#  for a more complete version
# ----------------------------------------------------------------------------
# -- (c) Felipe Machado
# -- Area of Electronics Technology. Rey Juan Carlos University (urjc.es)
# -- https://github.com/felipe-m
# -- 2019
# ----------------------------------------------------------------------------
# --- LGPL Licence
# ----------------------------------------------------------------------------

import os
import sys
import FreeCAD
import FreeCADGui
import Part
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

import kcomp
import fcfun   # import my functions for freecad. FreeCad Functions
import comps   # import my CAD components
import kidler  # import constants for the idler tensioner and holder
import kparts

#exec(open("nemamotor_holder.py").read())


"""
     Creates a holder for a Nema motor
         __________________
        ||                ||
        || O     __     O ||
        ||    /      \    ||
        ||   |   1    |   ||
        ||    \      /    ||
        || O     __     O ||
        ||________________|| ..... wall_thick
        ||_______2________|| ....................>Y
                                      
                                      
                                      motor_xtr_space_d
                                     :  :
         ________3_________        3_:__:____________ ..............> X
        |  ::  :    :  ::  |       |      :     :    |    + motor_thick
        |__::__:_1__:__::__|       2......:..1..:....|....:
        ||                ||       | :              /
        || ||          || ||       | :           /
        || ||          || ||       | :        /
        || ||          || ||       | :      /
        || ||          || ||       | :   /
        ||________________||       |_: /
        ::       :                 :                 :
         + reinf_thick             :....tot_d........:
                 :
                 :
                 Z


                  motor_hole_r
                 :  :  
               :    :
         ______:____:______ ..................................
        |  ::  :    :  ::  |                                  :
        |__::__:_1__:__::__|....................              :
        ||                ||....+ motor_min_h  :              :
        || ||          || ||                   :              +tot_h
        || ||          || ||                   + motor_max_h  :
        || ||          || ||                   :              :
        || ||          || ||...................:              :
        ||________________||...................:xtr_down......:
        :  :            :  :
        :  :            :  :
        :  :............:  :
        :   bolt_wall_sep  :
        :                  :
        :                  :
        :.....tot_w........:
                         ::
                          motor_xtr_space
"""

# --------------- PARAMETERS (can be changed) -------------------------
## Nema Size, choose the NEMA size of your motor: 8, 11, 14, 17, 23, 34, 42
nema_size = 17

#  thickness in mm of the side where the holder will be screwed to
wall_thick = 4.

#  thickness in mm of the top side where the motor will be screwed to
motor_thick = 4.

#  thickness of the reinforcement walls
reinf_thick = 4.

#  distance of from the inner top side to the top hole of the bolts to 
#  attach the holder (see drawing)
motor_min_h = 10.

# distance of from the inner top side to the bottom hole of the bolts to 
# attach the holder
motor_max_h = 40.

# extra separation between the motor and the sides
motor_xtr_space = 4.

# extra separation between the motor and the side of the wall
motor_xtr_space_d = 5.

# extra space from the motor_max_h to the end
xtr_down = 5.

# separation of the wall bolts, if 0, it will be the motor width
# has to be smaller than the total width
bolt_wall_sep = 0

# metric of the bolts to attach the holder (diameter of the shank in mm)
bolt_wall_d = 3.

# radius of the chamfer
chmf_r = 1.

# motor hole radius: the hole for the motor circle that is with the axis
# if 0, will take the half of the distance of the bolts
motor_hole_r = 0

# tolerances: 0.4 or 0.3 mm
TOL = 0.3
STOL = TOL / 2.  #smaller tolerance

# ----- DO NOT CHANGE ANYTHING UNDER THIS LINE UNLESS YOU KNOW WHAT YOU 
# ---             ARE DOING


# width of the motor (both dimensions: it is a square) in mm
NEMA_W  = {
             8:   20.2,
             11:  28.2,
             14:  35.2,
             17:  42.3,
             23:  56.4,
             34:  86.0,
             42: 110.0 }

# Separation of the bolt holes of the motor  
NEMA_BOLT_SEP  = {
             8:   16.0,
             11:  23.0,
             14:  26.0,
             17:  31.0,
             23:  47.1,
             34:  69.6,
             42:  89.0 }

# motor bolt holes diameter
# check datasheet, dimensions may vary
NEMA_BOLT_D  = {
              8:   2.0,  # M2
             11:   2.5,  # M2.5
             14:   3.0,  # M3
             17:   3.0,  # M3
             23:   5.0,
             34:   5.0,
             42:   8.0 }

# width of the motor
motor_w = NEMA_W[nema_size]
# separation of the motor bolts
motor_bolt_sep = NEMA_BOLT_SEP[nema_size]
# diameter of these bolts
motor_bolt_d = NEMA_BOLT_D[nema_size]
# radius of the motor bolts including tolerances
motor_bolt_r_tol = motor_bolt_d/2. + STOL

# radius of the wall bolts including tolerances
bolt_wall_r_tol = bolt_wall_d/2. + STOL

# if not defined:
if motor_hole_r == 0:
    motor_hole_r = motor_bolt_sep/2.

# if not defined:
if bolt_wall_sep == 0:
    bolt_wall_sep = motor_w

# total width: the reinforcement + motor width + xtr_space
tot_w = 2* reinf_thick + motor_w + 2 * motor_xtr_space

# total height:
tot_h = motor_thick + motor_max_h + xtr_down

# total depth:
tot_d = wall_thick + motor_w + motor_xtr_space_d

def nemamotor_holder ():



    #  --------------- step 01 ---------------------------      
    #  rectangular cuboid with basic dimensions
    # 
    #                    Z
    #                    :
    #                    :
    #             :.....tot_w.......
    #             :______:__________:
    #             /                /|
    #            /                / |
    #           /                /  |
    #          /                /   |
    #       ../________________/    |
    #       : |                |    | 
    #       : |                |    |...............Y
    #       : |                |   /     . 
    #  tot_h: |                |  /     . tot_d
    #       : |                | /     . 
    #       :.|________________|/......
    #                .
    #               .
    #              X 
    #

    # creates the shape, you don't see it yet on FreeCAD Gui
    # centered along axis Y
    shp01 = fcfun.shp_boxcen(tot_d, tot_w, tot_h, cy = True)
    # creates a freecad object from the shape, to see it in FreeCAD Gui,
    # not necessary, but illustrative for this tutorial
    fcd01 = fcfun.add_fcobj(shp01, 'box01')


    #  --------------- step 02 ---------------------------      
    #  chamfering the 4 vertical edges (marked with H)
    # 
    #                    Z
    #                    :
    #                    :
    #             :.....tot_w.......
    #             :______:__________:
    #             /                /H chamfering
    #            /                / H
    #           /                /  H
    #          /                /   H
    #       ../________________/    H
    #       : H                H    H 
    #       : H                H    H...............Y
    #       : H                H   /     . 
    #  tot_h: H                H  /     . tot_d
    #       : H                H /     . 
    #       :.H________________H/......
    #                .
    #               .
    #              X 
    #

    fcd02 = fcfun.filletchamfer (fcd01, e_len = tot_h,
                                 name = 'step02',
                                 fillet = 0,
                                 radius = chmf_r,
                                 axis = 'z'  # axis to fillet
                                )

    #  --------------- step 03 ---------------------------      
    #  Horizontal chamfering the top edge to make a 'triangular' reinforcement
    # 
    #      Z
    #      :
    #      :___            . chmf_pos
    #      |    \
    #      |      \
    #      |        \
    #      |          \
    #      |            \
    #      |              \
    #      |________________.....X
    # 
    #
    # the radius is the smaller part
    chmf_reinf_r = min(tot_d - wall_thick, tot_h-motor_thick)

    fcd03 = fcfun.filletchamfer (fcd02, e_len = 0,
                                 name = 'step03',
                                 fillet = 0,
                                 radius = chmf_reinf_r,
                                 axis = 'y',  # axis to fillet
                                 xpos_chk = 1,
                                 zpos_chk = 1,
                                 xpos = tot_d, # position of the edge in x
                                 zpos = tot_h  # position of the edge in z
                                )

    #  --------------- step 04 ---------------------------      
    #  Hole for the motor
    # 
    #                Z                      Z
    #                :                      :
    #        ________:_________             :__
    #       | |              | |            | :  \        
    #       | |              | |            | :    \ 
    #       | |              | |            | :      \
    #       | |              | |            | :        \
    #       | |              | |            | :          \
    #       | |              | |            | :            \
    #       |_|______________|_|            | :..............\...motor_thick
    #       |_|______________|_|..Y         |_________________\..X
    #       : :                             : :
    #       : :                             : :
    #        reinf_thick                     wall_thick
    

    pos04 = FreeCAD.Vector(wall_thick,0,motor_thick)
    shp04cut = fcfun.shp_boxcen(tot_d, tot_w-2*reinf_thick, tot_h,
                             cy = True, pos=pos04)
    # creates a freecad object from the shape, to see it in FreeCAD Gui,
    # not necessary, but illustrative for this tutorial
    fcd04cut = fcfun.add_fcobj(shp04cut, 'motorhole')
    # difference (cut) of fcd01 and fcd02cut
    fcd04 = doc.addObject("Part::Cut", 'step04')
    fcd04.Base = fcd03
    fcd04.Tool = fcd04cut
    # the shape
    shp04 = fcd04.Shape

    doc.recompute()


    #  --------------- step 05 ---------------------------      
    #  Holes for motor bolts, and the central hole
    #
    #    ____________________...............................>Y
    #   | ___________________|.. wall_thick         
    #   | |                | |.. motor_xtr_space..... 
    #   | | O     __     O | | --                   :motor_w/2
    #   | |    /      \    | |   .                  :
    #   | |   |   1    |   | |   .+ motor_bolt_sep ---
    #   | |    \      /    | |   .
    #   | | O     __     O | | --
    #   |_|________________|_| ..... wall_thick
    #             :        : :
    #             :         reinf_thick
    #       :     X      :
    #       :            :
    #       :            :
    #       motor_bolt_sep

    # position of the motor axis z=-1 to do the cut
    pos05 = FreeCAD.Vector(wall_thick+motor_xtr_space+motor_w/2.,0,-1)
    shp05cenhole = fcfun.shp_cyl (r = motor_hole_r,
                                  h = motor_thick+2, # for the cut
                                  normal = fcfun.VZ,
                                  pos = pos05)
    # make a list of the bolt holes
    boltholes_shp_list = []
    # the four motor holes
    for x_side in [-1,1]:
        for y_side in [-1,1]:
            hole_pos = pos05 + FreeCAD.Vector(x_side*motor_bolt_sep/2.,
                                              y_side*motor_bolt_sep/2.,0)
            shp05bolthole = fcfun.shp_cyl (r = motor_bolt_r_tol,
                                  h = motor_thick+2, # for the cut
                                  normal = fcfun.VZ,
                                  pos = hole_pos)
            boltholes_shp_list.append(shp05bolthole)
    # fuse the 5 holes
    shp05cut = shp05cenhole.multiFuse(boltholes_shp_list)
    # not necessary to create a FreeCAD object, but illustrative for tutorial
    fcd05cut = fcfun.add_fcobj(shp05cut, 'boltholes')
    # difference (cut) of fcd04 and fcd05cut
    fcd05 = doc.addObject("Part::Cut", 'step05')
    fcd05.Base = fcd04
    fcd05.Tool = fcd05cut
    # the shape
    shp05 = fcd05.Shape

    doc.recompute()

    #  --------------- step 06 ---------------------------      
    #  Rails to attach the holder
    # 
    #            Z               
    #            :                
    #    ________:_________        
    #   | |              | |        
    #   | | ||        || | |-----------------------
    #   | | ||        || | |                       :
    #   | | ||        || | |                       +motor_max_h
    #   | | ||        || | |                       :
    #   | | ||        || | |-------                :
    #   |_|______________|_|.......:+ motor_min_h..: 
    #   |_|______________|_|....:+motor_thick............Y
    #        :         :                   
    #        :.........:
    #             bolt_wall_sep

    shp06_cut_list = []
    step06_base_pos = FreeCAD.Vector(-1,0, motor_thick+motor_min_h)
    for y_side in [-1,1]:
        # the rails
        step06_bot_pos = ( step06_base_pos
                          + FreeCAD.Vector(0,y_side*bolt_wall_sep/2.,0))
        shp06_rail = fcfun.shp_boxcen(wall_thick+2, 2*bolt_wall_r_tol,
                                      motor_max_h-motor_min_h,
                                      cy = True, pos = step06_bot_pos)
        shp06_cut_list.append(shp06_rail)
        # bottom end circle:
        shp06_hole = fcfun.shp_cyl (r = bolt_wall_r_tol,
                                    h = wall_thick+2, # for the cut
                                    normal = fcfun.VX,
                                    pos = step06_bot_pos)
        shp06_cut_list.append(shp06_hole)
        step06_top_pos = ( step06_bot_pos
                          + FreeCAD.Vector(0,0,motor_max_h-motor_min_h))
        # top end circle:
        shp06_hole = fcfun.shp_cyl (r = bolt_wall_r_tol,
                                    h = wall_thick+2, # for the cut
                                    normal = fcfun.VX,
                                    pos = step06_top_pos)

        shp06_cut_list.append(shp06_hole)

    # fuse the rails
    shp06cut = fcfun.fuseshplist(shp06_cut_list)
    # not necessary to create a FreeCAD object, but illustrative for tutorial
    fcd06cut = fcfun.add_fcobj(shp06cut, 'rails')
    # difference (cut) of fcd04 and fcd05cut
    fcd06 = doc.addObject("Part::Cut", 'step06')
    fcd06.Base = fcd05
    fcd06.Tool = fcd06cut
    # the shape
    shp06 = fcd06.Shape

    doc.recompute()
   





    #            Z                          Z
    #            :                          :
    #    ________:_________                 :__
    #   | |              | |                |.:  \        
    #   | | ||        || | |---            -| :    \ 
    #   | | ||        || | |                | :      \
    #   | | ||        || | |                | :        \
    #   | | ||        || | |                | :          \
    #   | | ||        || | |--             -|.:            \
    #   |_|______________|_|..motor_min_h   | :..............\...motor_thick
    #   |_|______________|_|..Y motor_thick |_________________\..X
    #   : :                                 : :
    #   : :                                 : :
    #    reinf_thick                         wall_thick


    #            :
    #            :
    #            :
    #            :
    #                Z                      Z
    #                :                      :
    #        ________:_________             :__
    #       | |              | |            | :  \        
    #       | |              | |            | :    \ 
    #       | |              | |            | :      \
    #       | |              | |            | :        \
    #       | |              | |            | :          \
    #       | |              | |            | :            \
    #       |_|______________|_|            | :..............\...motor_thick
    #       |_|______________|_|..Y         |_________________\..X
    #       : :                             : :
    #       : :                             : :
    #        reinf_thick                     wall_thick


    # 
    #      Z                                     Z
    #      :                                     :
    #      :___                          ________:_________
    #      | :  \                       | |              | |
    #      | :    \                     | |              | |
    #      | :      \                   | |              | |
    #      | :        \                 | |              | |
    #      | :          \               | |              | |
    #      | :............\             |_|______________|_|
    #      |_______________\.....X      |_|______________|_|
 




"""
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
    pos02 = FreeCAD.Vector(-1,
                           kidler.tens_l - 2*kidler.idler_r_xtr,
                           kidler.wall_thick)
    # oscad: cube([tens_w+2, 2 * idler_r_xtr +1, idler_h]);
    # ...
    # creates the shape already filleted on X, make it larger on Y to make 
    # the chamfer easier, so all X edges are chamfered, but since is larger
    # on Y, it doesnt matter.  y dimensions
    shp02cut = fcfun.shp_boxcenfill(
                     x = kidler.tens_w+2,
                     # in_fillet added
                     y = 2 * kidler.idler_r_xtr +1 + kidler.in_fillet,
                     z = kidler.idler_h,
                     fillrad = kidler.in_fillet,
                     fx = True, fy = False, fz = False, # chamfer on X
                     pos = pos02)
    fcd02cut = fcfun.add_fcobj(shp02cut, 'cut02')
    # difference (cut) of fcd01 and fcd02cut
    fcd02 = doc.addObject("Part::Cut", 'step02')
    fcd02.Base = fcd01
    fcd02.Tool = fcd02cut
    # the shape
    shp02 = fcd02.Shape

    doc.recompute()
    

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
    fcd03 = fcfun.filletchamfer (fcd02, e_len = kidler.tens_w,
                                name = 'step03',
                                fillet = 1,
                                radius = kidler.in_fillet,
                                axis = 'x',  # axis to fillet
                                ypos_chk = 1,
                                ypos = kidler.tens_l) #fillet on y=tens_l


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
    fcd04a = fcfun.filletchamfer (fcd03, e_len = 0,
                                  name = 'step04a',
                                  fillet = 0,  # chamfer
                                  radius = 2* kidler.in_fillet,
                                  axis = 'x',  # axis to fillet
                                  ypos_chk = 1,
                                  ypos = 0) #fillet on y=0


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
        fcd04 = fcfun.filletchamfer (fcd04a, e_len = 0,
                                      name = 'step04b',
                                      fillet = 0,  # chamfer
                                      radius = 2* kidler.in_fillet,
                                      axis = 'z',  # axis to fillet
                                      ypos_chk = 1,
                                      ypos = 0) #fillet on y=0
    else:
        # just to have the same freecad object at the end of step 4 in fcd04
        fcd04 = fcd04a 



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
    #oscad: translate ([tens_w/2., tens_l - idler_r_xtr, -1])
    #oscad:     cylinder (r=boltidler_r_tol, h= tens_w +2, $fa=1, $fs=0.5);
    pos05 = FreeCAD.Vector(kidler.tens_w/2.,
                           kidler.tens_l - kidler.idler_r_xtr,
                           -1)
    fcd05 = fcfun.addCylPos (r = kidler.boltidler_r_tol,
                             h = kidler.tens_h +2,
                             name = 'step05',
                             pos = pos05)

    fcd05.ViewObject.ShapeColor = fcfun.YELLOW #yellow color
    # we will make the cut at the end with the other cuts

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

    #  Space for screw (the stroke)
    #oscad: translate ([-1, nut_holder_total,wall_thick])
    pos06 = FreeCAD.Vector (-1,
                            kidler.nut_holder_total,
                            kidler.wall_thick)
    # shape of a box with fillet in all the X edges
    #oscad: cube([tens_w+2, tens_stroke, idler_h]);
    shp06 = fcfun.shp_boxcenchmf (x = kidler.tens_w+2,
                                  y = kidler.tens_stroke,
                                  z = kidler.idler_h,
                                  chmfrad = kidler.in_fillet,
                                  fx = True,
                                  fz = False,
                                  pos = pos06)
    fcd06 = fcfun.add_fcobj(shp06, 'step06')
    fcd06.ViewObject.ShapeColor = fcfun.ORANGE

    
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
    pos07 = FreeCAD.Vector(kidler.tens_w/2,
                           -1,
                           kidler.tens_h/2)
    #oscad:rotate ([-90,0,0])
    #oscad: cylinder (r=bolttens_r_tol, h=nut_holder_total+2,$fa=1, $fs=0.5);
    fcd07 = fcfun.addCylPos (r = kidler.bolttens_r_tol,
                             h = kidler.nut_holder_total +2.,
                             name = 'step07',
                             normal = fcfun.VY, #on the positive y axis
                             pos = pos07)
    fcd07.ViewObject.ShapeColor = fcfun.RED

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
    # dont need to have tens_w/2-1, because there is xtr argument for that
    pos08 = FreeCAD.Vector (kidler.tens_w/2., 
                            kidler.nut_holder_thick,
                            kidler.tens_h/2.)
    #oscad: cylinder (r=m4_nut_r_tol+stol, h = nut_space, $fn=6);
    #oscad:  cube([tens_w/2 + 2, nut_space, 2*m4_nut_ap_tol]);
    shp08 = fcfun.shp_nuthole (nut_r = kidler.tensnut_circ_r_tol,
                               nut_h = kidler.nut_space,
                               hole_h = kidler.tens_w/2,
                               xtr_nut = 1, xtr_hole = 1, 
                               # on the Y direction
                               fc_axis_nut = FreeCAD.Vector(0,1,0),
                               # on the X direction
                               fc_axis_hole = FreeCAD.Vector(1,0,0),
                               ref_nut_ax = 2, # pos not centered on axis nut 
                               # pos at center of nut on axis hole 
                               ref_hole_ax = 1, 
                               pos = pos08)
    fcd08 = fcfun.add_fcobj(shp08, 'step08')
    fcd08.ViewObject.ShapeColor = fcfun.GREEN

    # --------- step 09:
    # --------- Last step, union and cut of the steps 05, 06, 07, 08
    fcd09cut = doc.addObject("Part::MultiFuse", "step09cut")
    fcd09cut.Shapes = [fcd05,fcd06,fcd07,fcd08]
    fcd09final = doc.addObject("Part::Cut", "idler_tensioner")
    fcd09final.Base = fcd04
    fcd09final.Tool = fcd09cut
    doc.recompute()
    return fcd09final
    

"""

# creation of a new FreeCAD document
doc = FreeCAD.newDocument()
# creation of the idler tensioner
fcd_motor_holder = nemamotor_holder()
#fcd_idler_tens.ViewObject.ShapeColor = fcfun.LSKYBLUE
# change color to orange:
"""
fcd_idler_tens.ViewObject.ShapeColor = (1.0, 0.5, 0.0)


# ---------- export to stl
stlPath = filepath + '/../stl/'
stlFileName = stlPath + 'idler_tensioner' + '.stl'
# rotate to print without support:
fcd_idler_tens.Placement.Rotation = (
                    FreeCAD.Rotation(FreeCAD.Vector(0,1,0), -90))
# exportStl is not working well with FreeCAD 0.17
#fcd_idler_tens.Shape.exportStl(stlFileName)
mesh_shp = MeshPart.meshFromShape(fcd_idler_tens.Shape,
                                  LinearDeflection=kparts.LIN_DEFL, 
                                  AngularDeflection=kparts.ANG_DEFL)
mesh_shp.write(stlFileName)
del mesh_shp

# rotate back
fcd_idler_tens.Placement.Rotation = (
                    FreeCAD.Rotation(FreeCAD.Vector(1,0,0), 0))

# save the FreeCAD file
freecadPath = filepath + '/../freecad/'
freecadFileName = freecadPath + 'idler_tensioner' + '.FCStd'
doc.saveAs (freecadFileName)
"""
