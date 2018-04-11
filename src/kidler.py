#  Idler pulley tensioner and holder constants
# ----------------------------------------------------------------------------
# -- (c) Felipe Machado
# -- Area of Electronic Technology. Rey Juan Carlos University (urjc.es)
# -- https://github.com/felipe-m
# -- December-2017
# ----------------------------------------------------------------------------
# --- LGPL Licence
# ----------------------------------------------------------------------------*/


import kcomp
import partgroup

#  -----------------------------------------------------------------------
#  ----------- variables that can be changed -----------------------------

# Tolerance in mm
TOL = 0.4
STOL = TOL / 2.0       # smaller tolerance

#  Thickness of the walls
wall_thick = 5.

#   Length of the ilder tensioner body, the stroke. Not including the pulley
#   See step 06 in ilder_tensioner.scad
#          Z
#          :
#          : ______________________
#           /      _____     __:_:_|
#          |      /     \   /             
#          |     |       | |        
#          |      \_____/   \______
#           \__________________:_:_|.............> Y
#          :     :       :         :
#          :     :.......:         :
#          :     :   +             :
#          :.....:  tens_stroke    :
#          :  +                    :
#          : nut_holder_total      :
#          :                       :
#          :...... tens_l .........:
# 

tens_stroke = 20.


#  distance between the pulley and the stroke
pulley_stroke_dist = wall_thick

#  plastic space above and bellow the nut for the screw
#  See step 08 in idler_tensioner.scad
# 
#          Z
#          :
#          : ______________________
#           /      _____     __:_:_|
#          |  _   /     \   /
#          |:|_|:|       | |
#          |      \_____/   \______
#           \__________________:_:_|.............> Y
#          : :   :                 :
#          :+    :                 :
#          :nut_holder_thick       :
#          :.....:                 :
#          :  +                    :
#          : nut_holder_total      :
#          :                       :
#          :...... tens_l .........:
#                       
nut_holder_thick = 4.

#  inner fillet radius
in_fillet = 2.

#  width of the aluminum profiles
aluprof_w = 30.

#  bolt size to attach the piece to the aluminum profile
boltaluprof_d = 4.

#  height of the holder base
#
#                              _______        :      :______________
#                             |  ___  |       :      |  __________  |
#                             | |   | |       :      | |__________| |
#                            /| |___| |\      :      |________      |
#                           / |_______| \     :      |        |    /      
#                   .. ____/  |       |  \____:      |________|  /
#       hold_bas_h.+..|_::____|_______|____::_|      |___::___|/......Y
#
hold_bas_h = 8.

#  optional tensioner chamfer, see
#  - step 04b in idler_tensioner.scad
#  - step 06 in idler_holder.scad
opt_tens_chmf = 1

#  if you want to have the hole at the idler_holder to see inside, on one
#  side, or both sides see:
#  - step 07 in idler_holder.scad:
hold_hole_2sides = 1

#  The position where the belt starts, from the lower profile
#  Considering that the filter holder and guide are in a higher
#  aluminum profile than the filter_idler. See picture below (at the end)

belt_pos_h = aluprof_w + 3.5

#  the shank diameter for the idler pulley bolt, 
boltidler_d = 4 # typical 3 or 4 (metric 3 or metric 4)

#  the screw for tensioning the pulley 
bolttens_d = 4 # typical 3 or 4 (metric 3 or metric 4)


#  -----------------------------------------------------------------------
#  ---- no changes under this line here unless you know what you are doing ---

# --------- idler pulley values
# dictionary of the bolt for the idler pulley
d_boltidler = kcomp.D912[boltidler_d]
# the shank radius including tolerance
boltidler_r_tol = d_boltidler['shank_r_tol']

# the idler group list resulting from this bolt:
idlerpulley_l = kcomp.idpullmin_dict[boltidler_d]

idler_h = partgroup.getgroupheight(idlerpulley_l)
idler_r = partgroup.getmaxwashdiam(idlerpulley_l)/2.
idler_r_xtr = idler_r + 2.  #  +2: a little bit larger

largewasher_thick = partgroup.getmaxwashthick(idlerpulley_l)

# --------- end of idler pulley values

# --------- tensioner bolt and nut values
# dictionary of the bolt tensioner
d_bolttens = kcomp.D912[bolttens_d]
# the shank radius including tolerance
bolttens_r_tol = d_bolttens['shank_r_tol']

# dictionary of the nut
d_nuttens = kcomp.D934[bolttens_d]

nut_space = kcomp.NUT_HOLE_MULT_H + d_nuttens['l_tol']

nut_holder_total = nut_space + 2* nut_holder_thick

# circum diameter of the nut
tensnut_circ_d = d_nuttens['circ_d']
# circum radius of the nut, with tolerance
tensnut_circ_r_tol = d_nuttens['circ_r_tol']

# the apotheme of the nut
tensnut_ap_tol = (d_nuttens['a2']+STOL)/2.

# --------- end of tensioner bolt and nut values

# --------- bolt to attach to the aluminum profile
# dictionary of the bolt
d_boltaluprof = kcomp.D912[boltaluprof_d]
boltaluprof_head_r_tol = d_boltaluprof['head_r_tol']
boltaluprof_r_tol = d_boltaluprof['shank_r_tol']
boltaluprof_head_l = d_boltaluprof['head_l']

# --------- end of tensioner bolt and nut values


#  Tensioner dimensions
tens_h = idler_h + 2*wall_thick
tens_l = (  nut_holder_total
          + tens_stroke
          + 2 * idler_r_xtr
          + pulley_stroke_dist)
tens_w = max(2 * idler_r_xtr, tensnut_circ_d)

tens_w_tol = tens_w + TOL
tens_h_tol = tens_h + TOL


#  Vertical position of the belt pulley and the tensioner
#                              Z   Z
# tensioner holder:            :   :
#               _______        :   :____________
#              /. ___ .\       :   |  ._______ .|
#              |.| O |.|       :   |::|_______| |...
#             /| |___| |\      :   |  ..........|... tens_h/2 -m4_nut_ap_tol
#            / |_______| \     :   |            |  :+tens_pos_h
#       ____/__|       |__\____:   |________   /   :  ...
#   X..(_______|_______|_______)   |________|/.....:.....hold_bas_h

#  idler_tensioner:
#         _______________________
#        /      ______   ___::___|
#       |  __  |      | |
#       |:|  |:|      | |         .......................
#       |  --  |______| |_======_  = largewasher_thick  :
#        \__________________::___|.: wall_thick         :
#                                    :                  :
#                                    :                  + belt_pos_h
#                                    :                  :
#                                    +tens_pos_h        :
#                                    :                  :
#                                    :                  :
#                   _________________:__________________:____
#                           alu_prof
# 

tens_pos_h = belt_pos_h - wall_thick -largewasher_thick 

#  The part of the tensioner that will be inside
tens_l_inside = tens_l - 2 * idler_r_xtr

# tensioner holder dimensions:

hold_w = tens_w + 2*wall_thick
hold_l = tens_l_inside + wall_thick
hold_h = tens_pos_h + tens_h + wall_thick

hold_bas_w = hold_w + 2*aluprof_w
hold_bas_l = aluprof_w
