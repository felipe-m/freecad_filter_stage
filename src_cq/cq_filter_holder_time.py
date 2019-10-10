# ----------------------------------------------------------------------------
#  Filter holder
#  CadQuery version
# ----------------------------------------------------------------------------
# -- (c) Felipe Machado
# -- Area of Electronic Technology. Rey Juan Carlos University (urjc.es)
# -- https://github.com/felipe-m/freecad_filter_stage
# -- 2019
# ----------------------------------------------------------------------------
# --- LGPL Licence
# ----------------------------------------------------------------------------
#
#                     axis_h
#                        :
#                        :
#         ___    ___     :     ___    ___       ____
#        |   |  |   |    :    |   |  |   |     | || |
#        |...|__|___|____:____|___|__|...|     |_||_|
#        |         _           _         |     |  ..|
#        |        |o|         |o|        |     |::  |
#        |        |o|         |o|        |     |::  |
#        |                               |     |  ..|
#        |                               |     |  ..|
#        |      (O)             (O)      |     |::  |
#        |                               |     |  ..|
#        |                               |     |  ..|
#        |  (O)   (o)   (O)   (o)   (O)  |     |::  |
#        |_______________________________|     |  ..|
#        |_______________________________|     |     \_________________
#        |  :.........................:  |     |       :............:  |
#        |   :                       :   |     |        :          :   |
#        |___:___________x___________:___|     x________:__________:___|.>axis_d
#
#
#         _______________x_______________ ......> axis_w
#        |____|                     |____|
#        |____   <  )          (  >  ____|
#        |____|_____________________|____|
#        |_______________________________|
#        |  ___________________________  |
#        | | ......................... | |
#        | | :                       : | |
#        | | :                       : | |
#        | | :                       : | |
#        | | :.......................: | |
#        | |___________________________| |
#         \_____________________________/
#                        :
#                        :
#                        :
#                      axis_d
#
#

# to execute this file in FreeCAD V0.18
# exec(open("filter_holder_clss.py").read())



# the filter is referenced on 3 perpendicular axis:
# - axis_d: depth
# - axis_w: width
# - axis_h: height
#
# The reference position is marked with a x in the drawing

from datetime import datetime
startdatetime = datetime.now()

import math
import FreeCAD
import Part
import Mesh
import MeshPart
import DraftVecUtils
import cadquery as cq

import kcomp   # import material constants and other constants
import fcfun   # import my functions for freecad. FreeCad Functions

from fcfun import V0, VX, VY, VZ, V0ROT

# ------------------- def shp_belt_wire_dir

def belt_wire_dir (center_sep, rad1, rad2,
                   fc_axis_l = VX,
                   fc_axis_s = VY,
                   ref_l = 1,
                   ref_s = 1,
                   pos=V0):

    """
    Makes a shape of a wire with 2 circles and exterior tangent lines
    check: https://en.wikipedia.org/wiki/Tangent_lines_to_circles
    It is not easy to draw it well
    rad1 and rad2 can be exchanged, rad1 doesnt have to be larger
            ....                    fc_axis_s
           :    ( \ tangent          |
      rad1 :   (    \  .. rad2       |--> fc_axis_l, on the direction of rad2
           .--(  +   +)--
               (    /:
                ( /  :
                 :   :
                 :...:
                   + center_sep
 
                  ....                fc_axis_s
                 :    ( \ tangent       |
            rad1 :   (    \  .. rad2    |
                  --(  +   +)--         |--> fc_axis_l, on the direction of rad2
                     (    /:             centered on this axis
                      ( /  :
                       :   :
                       :...:
             ref_l: 3  2 1
 
    Arguments:
    center_sep: separation of the circle centers
    rad1: Radius of the firs circle, on the opposite direction of fc_axis_l
    fc_axis_l: vector on the direction circle centers, pointing to rad2
    fc_axis_s: vector on the direction perpendicular to fc_axis_l, on the plane
               of the wire
    ref_l: reference (zero) of the fc_axis_l
            1: reference on the center 
            2: reference at one of the semicircle centers (point 2)
               the other circle center will be on the direction of fc_axis_l
            3: reference at the end of rad1 circle
               the other end will be on the direction of fc_axis_l
    pos: FreeCAD vector of the position of the reference
    returns the shape of the wire
    """

    # normalize the axis
    axis_l = DraftVecUtils.scaleTo(fc_axis_l,1)
    axis_s = DraftVecUtils.scaleTo(fc_axis_s,1)


    #        ....                fc_axis_s
    #            :    ( \ tangent       |
    #       rad1 :   (    \  .. rad2    |
    #             --3  2 1 45--         |--> fc_axis_l, on the direction of rad2
    #                (    /:             centered on this axis
    #                 ( /  :
    #                  :   :
    #                  :...:
    #                    + center_sep
       

    # ----- Distance vectors on axis_l
    # distance from 1 to 2 in axis_l
    fc_1_2_l = DraftVecUtils.scale(axis_l, -center_sep/2.)
    fc_2_3_l = DraftVecUtils.scale(axis_l, -rad1)
    fc_2_4_l = DraftVecUtils.scale(axis_l, center_sep)
    fc_4_5_l = DraftVecUtils.scale(axis_l, rad2)
    fc_2_5_l = fc_2_4_l + fc_4_5_l
    # ----- reference is point 2 on axis_l
    # vector to go from the reference point to point 2 in l
    if ref_l == 1:  # ref on circle center sep
        refto_2_l = fc_1_2_l
    elif ref_l == 2:  # ref on circle center (rad1)
        refto_2_l = V0
    elif ref_l == 3:  # ref at the left end
        refto_2_l = fc_2_3_l.negative()
    else:
        logger.error('wrong ref_l in shp_belt_wire_dir')


    # Now define the center of the rad1 circle
    # and everything will be defined from this point
    # ln: L axis Negative side
    # lp: L axis Positive side
    # sn: S axis Negative side
    # sp: S axis Positive side
    # s0: S axis at zero
    #
    #        ....      ln_sp          fc_axis_s
    #            :    ( \ tangent     |
    #       rad1 :   (    \ lp_sp     |
    #           ln_s0  2   4lp_s0     |--> fc_axis_l, on the direction of rad2
    #                (    / lp_sn        centered on this axis
    #                 ( /
    #                  lp_sp
    #
    
    # cs_rad1 is point 2 (center of circle 1)
    #cs_rad1 = pos +  refto_2_l
    # reference at point 3 (ln_s0)
    cs_rad1 = refto_2_l + fc_2_3_l.negative()
    # cs_rad2 is point 4 (center of circle 2)
    cs_rad2 = cs_rad1 + fc_2_4_l
    # ln_s0 is point 3 
    ln_s0_pos = cs_rad1 + fc_2_3_l # should be 0,0
    # lp_s0 is point 5 
    lp_s0_pos = cs_rad2 + fc_4_5_l

    dif_rad = float(abs(rad1 - rad2))
    # Since we take our reference on axis_l, they are aligned, like if they were
    # on axis X, and axis Y would be zero.
    # therefore, angle gamma is zero (se wikipedia)
    # check: https://en.wikipedia.org/wiki/Tangent_lines_to_circles
    # the angle beta of the tanget is calculate from pythagoras:
    # the length (separation between centers) and dif_rad
    beta = math.atan (dif_rad/center_sep)
    #print('beta %f', 180*beta/math.pi)
    #print('beta %f', beta*math.pi/2)
    # depending on who is larger rad1 or rad2, the negative angle will be either
    # on top or down of axis_s

    #
    #                 (          \
    #                ( /alfa   beta\ which is 90-beta
    #               (               )
    #                (             / 
    #                 (          /
    #  
   
    cos_beta = math.cos(beta) 
    sin_beta = math.sin(beta) 
    tan_axis_s_rad1add = DraftVecUtils.scale(axis_s, rad1 * cos_beta)
    tan_axis_s_rad2add = DraftVecUtils.scale(axis_s, rad2 * cos_beta)
    if rad1 > rad2: # then it will be positive on axis_l on rad1 and rad2
        tan_axis_l_rad1add = DraftVecUtils.scale(axis_l, rad1 * sin_beta)
        tan_axis_l_rad2add = DraftVecUtils.scale(axis_l, rad2 * sin_beta)
    else:
        tan_axis_l_rad1add = DraftVecUtils.scale(axis_l, - rad1 * sin_beta)
        tan_axis_l_rad2add = DraftVecUtils.scale(axis_l, - rad2 * sin_beta)

    ln_sp_pos = cs_rad1 + tan_axis_l_rad1add + tan_axis_s_rad1add 
    ln_sn_pos = cs_rad1 + tan_axis_l_rad1add + tan_axis_s_rad1add.negative() 
    lp_sp_pos = cs_rad2 + tan_axis_l_rad2add + tan_axis_s_rad2add 
    lp_sn_pos = cs_rad2 + tan_axis_l_rad2add + tan_axis_s_rad2add.negative() 
    

    #cq_plane = cq.Plane(origin=(pos.x,pos.y,pos.z), xDir=fc_axis_l,
    #                            normal=fc_axis_l.cross(fc_axis_s))
    #cq_plane = cq.Plane(origin=(lp_sp_pos.x,lp_sp_pos.y,pos.z),
    cq_plane = cq.Plane(origin=(pos.x,pos.y,pos.z),
                                xDir=axis_s.negative(),
                                normal=axis_l.cross(axis_s))

    lp_sp_pos_y = lp_sp_pos.dot(axis_l)
    lp_sp_pos_x = lp_sp_pos.dot(axis_s)

    lp_s0_pos_y = lp_s0_pos.dot(axis_l)
    lp_s0_pos_x = lp_s0_pos.dot(axis_s)

    lp_sn_pos_y = lp_sn_pos.dot(axis_l)
    lp_sn_pos_x = lp_sn_pos.dot(axis_s)

    ln_sp_pos_y = ln_sp_pos.dot(axis_l)
    ln_sp_pos_x = ln_sp_pos.dot(axis_s)

    ln_s0_pos_y = ln_s0_pos.dot(axis_l)
    ln_s0_pos_x = ln_s0_pos.dot(axis_s)

    ln_sn_pos_y = ln_sn_pos.dot(axis_l)
    ln_sn_pos_x = ln_sn_pos.dot(axis_s)

    result = cq.Workplane(cq_plane).move(lp_sp_pos_x,lp_sp_pos_y)\
               .threePointArc((lp_s0_pos_x, lp_s0_pos_y),
                              (lp_sn_pos_x, lp_sn_pos_y))\
               .lineTo(ln_sn_pos_x,ln_sn_pos_y)\
               .threePointArc((ln_s0_pos_x, ln_s0_pos_y),
                              (ln_sp_pos_x, ln_sp_pos_y))\
               .close()

    return (result)




def cq_filter_hoder (
                 filter_l = 60.,
                 filter_w = 25.,
                 filter_t = 2.5,
                 base_h = 6.,
                 hold_d = 10.,
                 filt_supp_in = 2.,
                 filt_rim = 3.,
                 filt_cen_d = 0,
                 fillet_r = 1.,
                 # linear guides SEBLV16 y SEBS15, y MGN12H:
                 boltcol1_dist = 20/2.,
                 boltcol2_dist = 12.5, #thorlabs breadboard distance
                 boltcol3_dist = 25,
                 boltrow1_h = 0,
                 boltrow1_2_dist = 12.5,
                 # linear guide MGN12H
                 boltrow1_3_dist = 20.,
                 # linear guide SEBLV16 and SEBS15
                 boltrow1_4_dist = 25.,

                 bolt_cen_mtr = 4, 
                 bolt_linguide_mtr = 3, # linear guide bolts

                 beltclamp_t = 3., #2.8,
                 beltclamp_l = 12.,
                 beltclamp_h = 8.,
                 clamp_post_dist = 4.,
                 sm_beltpost_r = 1.,

                 tol = kcomp.TOL,
                 axis_d = VX,
                 axis_w = VY,
                 axis_h = VZ,
                 pos_d = 0,
                 pos_w = 0,
                 pos_h = 0,
                 pos = V0):
    """ Creates the filter holder shape


                               beltpost_l = 3*lr_beltpost_r + sm_beltpost_r
       pos_h         axis_h   :   :
       |                 :    :    clamp_post_dist
       v pos_w           :    :   ....
       9 7___6  5___4    :    :___:  :___ 
       8 |   |  |   |    :    |   |  |   |
       7 |...|__|___|____:____|___|__|...|...
         |         _           _         |   2 * bolt_linguide_head_r_tol
       6 |        |o|         |o|        |-----------------------
       5 |        |o|         |o|        |--------------------  +boltrow1_4_dist
         |                               |                   :  :
         |                               |                   +boltrow1_3_dist
       4 |      (O)             (O)      |--:                :  :
         |                               |  +boltrow1_2_dist :  :
         |                               |  :                :  :
       3 | (O)    (o)   (O)   (o)    (O) |--:----------------:--:
         |_______________________________|  + boltrow1_h
       2 |_______________________________|..:..................
       1 |  :.........................:  |..: filt_hole_h  :
         |   :                       :   |                 + base_h
       0 |___:___________x___________:___|.................:........axis_w
                         :     : :    :
                         :.....: :    :
                         : + boltcol1_dist
                         :       :    :
                         :.......:    :
                         : + boltcol2_dist
                         :            :
                         :............:
                            boltcol3_dist

             3     21    0     pos_w (position of the columns)
         7  6  5   4           pos_w (position of the belt clamps)

                                     beltclamp_l
                clamp_post          ..+...
                  V                 :    :
          _______________x__________:____:......................> axis_w
         |____|                     |____|.. beltclamp_blk_t  :
         |____   <  )          (  >  ____|..: beltclamp_t     :+ hold_d
         |____|_____________________|____|....................:
         |_______________________________|
         |  ___________________________  |.................
         | | ......................... | |..filt_supp_in   :
         | | :                       : | |  :              :
         | | :                       : | |  :              :+filt_hole_d
         | | :                       : | |  + filt_supp_d  :
         | | :.......................: | |..:              :
         | |___________________________| |.................:
          \_____________________________/.....filt_rim
         : : :                       : : :
         : : :                       : : :
         : : :                       :+: :
         : : :            filt_supp_in : :
         : : :                       : : :
         : : :.... filt_supp_w ......: : :
         : :                           : :
         : :                           : :
         : :...... filt_hole_w   ......: :
         :                             :+:
         :                      filt_rim :
         :                               :
         :....... tot_w .................:



               0123  pos_d
               0 45  pos_d 
                ____...............................
               | || |   + beltclamp_h             :
               |_||_|...:................         :
               |  ..|                   :         :
               |::  |                   :         :
               |::  |                   :         :
               |  ..|                   :         :
               |  ..|                   :         :+ tot_h
               |::  |                   :         :
               |  ..|                   :+hold_h  :
               |  ..|                   :         :
               |::  |                   :         :
               |  ..|                   :         :
               |     \________________  :         :
               |       :...........:  | :         :
               |        :         :   | :         :
               x________:_________:___|.:.........:...>axis_d
               :             :        :
               :.............:        :
               : filt_cen_d           :
               :                      :
               :...... tot_d .........:

       pos_d:  0    6  78    9    1011 12
 
 


        pos_o (origin) is at pos_d=0, pos_w=0, pos_h=0, It marked with x

    Parameters:
    -----------
    filter_l : float
        length of the filter (it will be along axis_w). Larger dimension
    filter_w : float
        width of the filter (it will be along axis_d). Shorter dimension
    filter_t : float
        thickness/height of the filter (it will be along axis_h). Very short
    base_h : float
        height of the base
    hold_d : float
        depth of the holder (just the part that holds)
    filt_supp_in : float
        how much the filter support goes inside from the filter hole
    filt_cen_d : float
        distance from the filter center to the beginning of the filter holder
        along axis_d
        0: it will take the minimum distance
           or if it is smaller than the minimum distance
    filt_rim : float
        distance from the filter to the edge of the base
    fillet_r : float
        radius of the fillets
    boltcol1_dist : float
        distance to the center along axis_w of the first column of bolts
    boltcol2_dist : float
        distance to the center along axis_w of the 2nd column of bolts
    boltcol3_dist : float
        distance to the center along axis_w of the 3rd column of bolts
        This column could be closer to the center than the 2nd, if distance
        is smaller
    boltrow1_h : float
        distance from the top of the filter base to the first row of bolts
        0: the distance will be the largest head diameter in the first row
           in any case, it has to be larger than this
    boltrow1_2_dist : float
        distance from the first row of bolts to the second
    boltrow1_3_dist : float
        distance from the first row of bolts to the third
    boltrow1_4_dist : float
        distance from the first row of bolts to the 4th
    bolt_cen_mtr : integer (could be float: 2.5)
        diameter (metric) of the bolts at the center or at columns other than
        2nd column
    bolt_linguide_mtr : integer (could be float: 2.5)
        diameter (metric) of the bolts at the 2nd column, to attach to a
        linear guide
    beltclamp_t : float
        thickness of the hole for the belt. Inside de belt clamp blocks
        (along axis_d)
    beltclamp_l : float
        length of the belt clamp (along axis_w)
    beltclamp_h : float
        height of the belt clamp: belt width + 2
        (along axis_h)
    clamp_post_dist : float
        distance from the belt clamp to the belt clamp post
    sm_beltpost_r : float
        small radius of the belt post


    tol : float
        Tolerances to print
    axis_d : FreeCAD.Vector
        length/depth vector of coordinate system
    axis_w : FreeCAD.Vector
        width vector of coordinate system
        if V0: it will be calculated using the cross product: axis_d x axis_h
    axis_h : FreeCAD.Vector
        height vector of coordinate system
    pos_d : int
        location of pos along the axis_d (0,1,2,3,4,5), see drawing
        0: at the back of the holder
        1: at the end of the first clamp block
        2: at the center of the holder
        3: at the beginning of the second clamp block
        4: at the beginning of the bolt head hole for the central bolt
        5: at the beginning of the bolt head hole for the linguide bolts
        6: at the front side of the holder
        7: at the beginning of the hole for the porta
        8: at the inner side of the porta thruhole
        9: at the center of the porta
        10: at the outer side of the porta thruhole
        11: at the end of the porta
        12: at the end of the piece
    pos_w : int
        location of pos along the axis_w (0-7) symmetrical
        0: at the center of symmetry
        1: at the first bolt column
        2: at the second bolt column
        3: at the third bolt column
        4: at the inner side of the clamp post (larger circle)
        5: at the outer side of the clamp post (smaller circle)
        6: at the inner side of the clamp rails
        7: at the end of the piece
    pos_h : int
        location of pos along the axis_h (0-8)
        0: at the bottom (base)
        1: at the base for the porta
        2: at the top of the base
        3: first row of bolts
        4: second row of bolts
        5: third row of bolts
        6: 4th row of bolts
        7: at the base of the belt clamp
        8: at the middle of the belt clamp
        9: at the top of the piece
    pos : FreeCAD.Vector
        Position of the cylinder, taking into account where the center is

    Attributes:
    -----------
    All the parameters and attributes of parent class SinglePart

    Dimensional attributes:
    filt_hole_d : float
        depth of the hole for the filter (for filter_w)
    filt_hole_w : float
        width of the hole for the filter (for filter_l)
    filt_hole_h : float
        height of the hole for the filter (for filter_t)

    beltclamp_blk_t : float
        thickness (along axis_d) of each of the belt clamp blocks
    beltpost_l : float
        length of the belt post (that has a shap of 2 circles and the tangent
    lr_beltpost_r : float
        radius of the larger belt post (it has a belt shape)
    clamp_lrbeltpostcen_dist : float
        distance from the center of the larger belt post cylinder to the clamp
        post

    prnt_ax : FreeCAD.Vector
        Best axis to print (normal direction, pointing upwards)
    d0_cen : int
    w0_cen : int
    h0_cen : int
        indicates if pos_h = 0 (pos_d, pos_w) is at the center along
        axis_h, axis_d, axis_w, or if it is at the end.
        1 : at the center (symmetrical, or almost symmetrical)
        0 : at the end



                  lr_beltpost_r  clamp_lrbeltpostcen_dist
                              + ..+..
       pos_h         axis_h   ::     :
       |                 :    ::   clamp_post_dist
                              ::   .+.
                              ::  :  :
                              ::  :  : beltclamp_l
       v pos_w           :    ::  :  :.+..
       9 7___6  5___4    :    ::__:  :___: 
       8 |   |  |   |    :    |   |  |   |
       7 |...|__|___|____:____|___|__|...|...
         |         _           _         |   2 * bolt_linguide_head_r_tol
       6 |        |o|         |o|        |-----------------------

    """

        
    doc = FreeCAD.ActiveDocument

    # calculation of the dimensions:
    # hole for the filter, including tolerances:
    # Note that now the dimensions width and length are changed.
    # to depth and width
    # they are relative to the holder, not to the filter
    # no need to have the tolerances here:
    filt_hole_d = filter_w # + tol # depth
    filt_hole_w = filter_l # + tol # width in holder axis
    filt_hole_h = filter_t # + tol/2. # 0.5 tolerance for height

    # The hole under the filter to let the light go through
    # and big enough to hold the filter
    # we could take filter_hole dimensions or filter dimensiones
    # just the tolerance difference
    filt_supp_d = filt_hole_d - 2 * filt_supp_in
    filt_supp_w = filt_hole_w - 2 * filt_supp_in

    # look for the largest bolt head in the first row:
    # dictionary of the center bolt and 2nd and 3rd column
    bolt_cen_dict = kcomp.D912[bolt_cen_mtr]
    bolt_cen_head_r_tol = bolt_cen_dict['head_r_tol']
    bolt_cen_r_tol = bolt_cen_dict['shank_r_tol']
    bolt_cen_head_l_tol = bolt_cen_dict['head_l_tol']

    # dictionary of the 1st column bolts (for the linear guide)
    bolt_linguide_dict = kcomp.D912[bolt_linguide_mtr]
    bolt_linguide_head_r_tol = bolt_linguide_dict['head_r_tol']
    bolt_linguide_r_tol = bolt_linguide_dict['shank_r_tol']
    bolt_linguide_head_l_tol = bolt_linguide_dict['head_l_tol']

    max_row1_head_r_tol = max(bolt_linguide_head_r_tol,
                              bolt_cen_head_r_tol)

    if boltrow1_h == 0:
        boltrow1_h = 2* max_row1_head_r_tol
    elif boltrow1_h < 2 * max_row1_head_r_tol:
        boltrow1_h = 2* max_row1_head_r_tol
        msg1 = 'boltrow1_h smaller than bolt head diameter'
        msg2 = 'boltrow1_h will be bolt head diameter' 
        logger.warning(msg1 + msg2 + str(boltrow1_h))
    # else # it will be as it is

    hold_h = (base_h + boltrow1_h + boltrow1_4_dist
                   + 2 * bolt_linguide_head_r_tol)
    tot_h = hold_h + beltclamp_h

    beltclamp_blk_t = (hold_d - beltclamp_t)/2.

    #clamp2cenpost = clamp_post_dist + s_beltclamp_r_sm


    # the large radius of the belt post
    lr_beltpost_r = (hold_d - 3) / 2.

    min_filt_cen_d = hold_d + filt_rim + filter_w/2.
    if filt_cen_d == 0: 
        filt_cen_d = hold_d + filt_rim + filter_w/2.
    elif filt_cen_d < min_filt_cen_d:
        filt_cen_d = hold_d + filt_rim + filter_w/2.
        msg =  'filt_cen_d is smaller than needed, taking: '
        logger.warning(msg + str(filt_cen_d))
    filt_cen_d = filt_cen_d

    tot_d = filt_cen_d + filter_w/2. + filt_rim 

    # find out if the max width if given by the filter or the holder
    base_w = filter_l + 2 * filt_rim
    hold_w = 2 * boltcol3_dist + 4 * bolt_cen_head_r_tol
    tot_w = max(base_w, hold_w)


    beltpost_l = (3*lr_beltpost_r) + sm_beltpost_r
    clamp_lrbeltpostcen_dist = (  beltpost_l
                                     - lr_beltpost_r
                                     + clamp_post_dist)




    d0_cen = 0
    w0_cen = 1 # symmetrical
    h0_cen = 0
    d_o={}
    w_o={}
    h_o={}

    d_o[0] = 0
    d_o[1] = beltclamp_blk_t
    d_o[2] = hold_d/2.
    d_o[3] = hold_d - beltclamp_blk_t
    # at the beginning of the bolt head hole for the central bolt
    d_o[4] = hold_d - bolt_cen_head_l_tol
    d_o[5] = hold_d - bolt_linguide_head_l_tol
    d_o[6] = hold_d
    # at the beginning of the hole of the porta (no tolerance):
    d_o[7] = filt_cen_d - filter_w/2.
    # inner side of porta thruhole
    d_o[8] = d_o[7] + filt_supp_in
    # at the center of the porta:
    d_o[9] = filt_cen_d
    # outer side of porta thruhole
    d_o[10] = filt_cen_d + filter_w/2. - filt_supp_in
    # at the end of the hole of the porta (no tolerance):
    d_o[11] = filt_cen_d + filter_w/2.
    d_o[12] = tot_d

    # these are negative because actually the pos_w indicates a negative
    # position along axis_w

    w_o[0] = 0
    #1: at the first bolt column
    w_o[1] = boltcol1_dist
    #2: at the second bolt column
    w_o[2] = boltcol2_dist
    #3: at the third bolt column
    w_o[3] = boltcol3_dist

    #7: at the end of the piece
    w_o[7] = tot_w/2.
    #6: at the inner side of the clamp rails
    # add belt_clamp because  w_o are negative
    w_o[6] = w_o[7] - beltclamp_l
    #5: at the outer side of the clamp post (smaller circle)
    w_o[5] = w_o[6] - clamp_post_dist
    #4: at the inner side of the clamp post (larger circle)
    w_o[4] = w_o[5] - beltpost_l


    #0: at the bottom (base)
    h_o[0] = 0
    #1: at the base for the porta
    h_o[1] = base_h - filt_hole_h
    #2: at the top of the base
    h_o[2] = base_h
    #3: first row of bolts
    h_o[3] = base_h + boltrow1_h
    #4: second row of bolts
    h_o[4] = h_o[3] + boltrow1_2_dist
    #5: third row of bolts, taking h_o[3]
    h_o[5] = h_o[3] + boltrow1_3_dist
    #6: 4th row of bolts
    h_o[6] = h_o[3] + boltrow1_4_dist
    #7: at the base of the belt clamp
    h_o[7] = hold_h
    #8: at the middle of the belt clamp
    h_o[8] = hold_h + beltclamp_h/2.
    #9: at the top of the piece
    h_o[9] = tot_h


    # -------- building of the piece
    # the base
    cq_base = cq.Workplane("XY").box(tot_d, tot_w, base_h,
                                     centered=(False, True, False))\
                                .edges("|Z")\
                                .fillet(fillet_r)


    # the holder to attach to a linear guide
    cq_holder = cq.Workplane("XY").box(hold_d, tot_w, hold_h,
                                       centered=(False, True, False))\
                                  .faces("<X")\
                                  .edges("|Z")\
                                  .fillet(fillet_r)

    cq_holder = cq_holder.union(cq_base)

    # chamfer at the union, at the corner of the L
    cq_holder = cq_holder.faces("(not >Z) and +Z")\
                         .edges("|Y and (not >X)")\
                         .chamfer(fillet_r)

    # ------------------- Holes for the filter
    # include tolerances, along nh: only half of it, along h= 1 to make
    # the cut
    # pos (9,0,1) position at the center of the porta, at its bottom
    cq_filter_hole = cq.Workplane("XY",origin=(d_o[9],w_o[0],h_o[1]))\
                       .box(filt_hole_d+2*tol,
                            filt_hole_w+2*tol,
                            filt_hole_h+tol/2.,
                            centered=(True,True,False))


    # pos (9,0,0) position at the center of the porta, at the bottom of the
    # piece
    # no extra on top because it will be fused with shp_filter_hole
    cq_filter_thruhole = cq.Workplane("XY",origin=(d_o[9],w_o[0],h_o[0]))\
                           .box(filt_supp_d,
                                filt_supp_w,
                                base_h,
                                centered=(True,True,False))

    cq_filter_hole = cq_filter_hole.union(cq_filter_thruhole)

    cq_holder = cq_holder.cut(cq_filter_hole)

    # ---------------- Holes for the bolts

    cq_cen_bolt = cq.Workplane("YZ",origin=(hold_d,0,0))\
                    .pushPoints([( 0,     h_o[3]),
                                 ( w_o[2],h_o[4]),
                                 (-w_o[2],h_o[4]),
                                 ( w_o[3],h_o[3]),
                                 (-w_o[3],h_o[3])])\
                    .circle(bolt_cen_r_tol)\
                    .extrude(-hold_d)

    cq_cen_bolt = cq_cen_bolt.faces(">X")\
                             .circle(bolt_cen_head_r_tol)\
                             .extrude(-bolt_cen_head_l_tol)

    cq_holder = cq_holder.cut(cq_cen_bolt)

    # linear guide bolts
    cq_lin_bolt = cq.Workplane("YZ",origin=(hold_d,0,0))\
                    .pushPoints([
                                 ( w_o[1],h_o[3]),
                                 (-w_o[1],h_o[3]),
                                 ( w_o[1],h_o[5]),
                                 (-w_o[1],h_o[5]),
                                 ( w_o[1],h_o[6]),
                                 (-w_o[1],h_o[6])])\
                    .circle(bolt_linguide_r_tol)\
                    .extrude(-hold_d)

    cq_lin_bolt = cq_lin_bolt.faces(">X")\
                             .circle(bolt_linguide_head_r_tol)\
                             .extrude(-bolt_linguide_head_l_tol)

    cq_holder = cq_holder.cut(cq_lin_bolt)

    cq_st_bolt = cq.Workplane("YZ",
                               origin=(hold_d-bolt_linguide_head_l_tol,0,0))\
                    .pushPoints([
                                 ( w_o[1],h_o[5]),
                                 (-w_o[1],h_o[5])])\
                    .box(2*bolt_linguide_head_r_tol, h_o[6]-h_o[5],
                         bolt_linguide_head_l_tol, centered=(True,False,False))

    cq_holder = cq_holder.cut(cq_st_bolt)

    # -------- belt clamps

    # this is not working, places them at the bottom
    #cq_clamps = cq_holder.faces(">Z")\
    #                     .pushPoints([ 
    #                        (0.,                     -tot_w/2.),
    #                        (0.,                      tot_w/2.-beltclamp_l),
    #                        (hold_d-beltclamp_blk_t, -tot_w/2.),
    #                        (hold_d-beltclamp_blk_t,  tot_w/2.-beltclamp_l,)])\
    #                     .box(beltclamp_blk_t,beltclamp_l,beltclamp_h,
    #                          centered=(False,False,False))

    #for d_side,wside in zip([-1,1,[-1,1]):
    cq_clamps = cq.Workplane("XY", origin=(0,0,hold_h))\
                   .pushPoints([ 
                            (0.,                     -tot_w/2.),
                            (0.,                      tot_w/2.-beltclamp_l),
                            (hold_d-beltclamp_blk_t, -tot_w/2.),
                            (hold_d-beltclamp_blk_t,  tot_w/2.-beltclamp_l,)])\
                         .box(beltclamp_blk_t,beltclamp_l,beltclamp_h,
                              centered=(False,False,False))\
                         .edges("|Z and <X and(>Y or <Y)")\
                         .fillet(fillet_r)


    cq_holder = cq_holder.union(cq_clamps)
    
    clamp_axis_s = FreeCAD.Vector(-1,0,0)
    for w_side in [-1,1]:
        if w_side == 1:
            clamp_axis_l = FreeCAD.Vector(0,-1,0)
        else:
            clamp_axis_l = FreeCAD.Vector(0,1,0)
        beltpost_pos = FreeCAD.Vector(d_o[2], w_side*w_o[5], h_o[7])
        print ("w_side")
        print (w_side)
        print (beltpost_pos)
        cq_belt_wire = belt_wire_dir(
                                       center_sep = 2 * lr_beltpost_r,
                                       rad1 = sm_beltpost_r,
                                       rad2 = lr_beltpost_r,
                                       fc_axis_l = clamp_axis_l,
                                       fc_axis_s = clamp_axis_s,
                                       ref_l = 3,
                                       pos = beltpost_pos)

        cq_belt = cq_belt_wire.extrude(-w_side*beltclamp_h)

        cq_holder = cq_holder.union(cq_belt)

    fcd = doc.addObject("Part::Feature", 'filter_holder')
    fcd.Shape = cq_holder.toFreecad()
    fcd.ViewObject.ShapeColor = (1.0, 0.8, 0.0) #ORANGE_08

    return(cq_holder)

    
doc = FreeCAD.newDocument()

cq = cq_filter_hoder(
                 filter_l = 60.,
                 filter_w = 25.,
                 filter_t = 2.5,
                 base_h = 6.,
                 hold_d = 12.,
                 filt_supp_in = 2.,
                 filt_rim = 3.,
                 filt_cen_d = 30,
                 fillet_r = 1.,
                 # linear guides SEBLV16 y SEBS15, y MGN12H:
                 boltcol1_dist = 20/2.,
                 boltcol2_dist = 12.5, #thorlabs breadboard distance
                 boltcol3_dist = 25,
                 boltrow1_h = 0,
                 boltrow1_2_dist = 12.5,
                 # linear guide MGN12H
                 boltrow1_3_dist = 20.,
                 # linear guide SEBLV16 and SEBS15
                 boltrow1_4_dist = 25.,

                 bolt_cen_mtr = 4, 
                 bolt_linguide_mtr = 3, # linear guide bolts

                 beltclamp_t = 3.,
                 beltclamp_l = 12.,
                 beltclamp_h = 8.,
                 clamp_post_dist = 4.,
                 sm_beltpost_r = 1.,

                 tol = kcomp.TOL,
                 axis_d = VX,
                 axis_w = VY,
                 axis_h = VZ,
                 pos_d = 0,
                 pos_w = 0,
                 pos_h = 0,
                 pos = V0)

fcad_time = datetime.now()

# default values for exporting to STL
LIN_DEFL_orig = 0.1
ANG_DEFL_orig = 0.523599 # 30 degree

LIN_DEFL = LIN_DEFL_orig/2.
ANG_DEFL = ANG_DEFL_orig/2.

mesh_shp = MeshPart.meshFromShape(cq.toFreecad(),
                                  LinearDeflection=LIN_DEFL, 
                                  AngularDeflection=ANG_DEFL)
# change the path where you want to create it
mesh_shp.write('C:/Users/Public/' + 'filter_holder' + '.stl')

mesh_time = datetime.now()
fcad_elapsed_time = fcad_time - startdatetime
mesh_elapsed_time = mesh_time - fcad_time
total_time = mesh_time - startdatetime
print ('Lin Defl: ' + str(LIN_DEFL)) 
print ('Ang Defl: ' + str(math.degrees(ANG_DEFL))) 
print ('shape time: ' + str(fcad_elapsed_time))
print ('mesh time: ' + str(mesh_elapsed_time))
print ('total time: ' + str(total_time))
print ('Points: ' + str(mesh_shp.CountPoints))
print ('Edges: ' + str(mesh_shp.CountEdges))
print ('Faces: ' + str(mesh_shp.CountFacets))

