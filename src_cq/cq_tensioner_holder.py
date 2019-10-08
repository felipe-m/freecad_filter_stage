#  tensioner holder
# ----------------------------------------------------------------------------
# -- (c) Felipe Machado
# -- Area of Electronic Technology. Rey Juan Carlos University (urjc.es)
# -- https://github.com/felipe-m
# -- September-2019
# ----------------------------------------------------------------------------
# --- LGPL Licence
# ----------------------------------------------------------------------------
#
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



#                   ___:___          
#                  |  ___  |         
#                  | | 1 | |         
#                 /| |___| |\       
#                / |_______| \      
#           ____/  |       |  \____ ...
#          |_::____|___2___|____::_|..: holder_base_z
#
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
print(filepath)
#sys.path.append(filepath + '/' + 'comps')
#sys.path.append(filepath + '/../../' + 'comps')

import kidler  # import constants for the idler tensioner and holder
import kparts

# to make a comparision of equality in floats, less than this number
mindif = 0.001

def tensioner_holder():
    # bring the active document
    doc = FreeCAD.ActiveDocument

    # --------------- step 01 --------------------------- 
    #    the base, to attach it to the aluminum profiles
    #    
    #
    #                                           Z      Z
    #                                           :      :
    #                 .. _______________________:      :________
    #     hold_bas_h.+..|_______________________|      |________|......Y
    #
    #                    .... hold_bas_w ........
    #                   :                        :
    #            X......:________________________:....
    #                   |                        |    :
    #                   |                        |    + hold_bas_l
    #                   |________________________|....:
    #                                            :
    #                                            Y
    #
    # cube([hold_bas_w, hold_bas_l, hold_bas_h]);
    cq01 = cq.Workplane("XY").box(kidler.hold_bas_w, kidler.hold_bas_l,
                                     kidler.hold_bas_h,
                                     centered = (False, False, False))
    

    #    --------------- step 02 --------------------------- 
    #    Fillet the base
    #    The piece will be printed on the XZ plane, so this fillet will be 
    #    raising
    #  
    #                                         Z
    #                                         :
    #                f4_______________________f2
    #          X......(_______________________)
    #                f3                        f1
    #

    cq02 = cq01.edges("|Y").fillet(kidler.in_fillet)
    
    #    --------------- step 03 --------------------------- 
    #    The main box
    #                             aluprof_w   Z      Z
    #                                  ..+....:      :
    #           .............. _______:       :      :____________
    #           :             |       |       :      |            |
    #           :             |       |       :      |            |
    #   hold_h +:             |       |       :      |            |
    #           :             |       |       :      |            |     
    #           :      _______|       |_______:      |________    |
    #       X...:.....(_______|_______|_______)      |________|___|...Y
    #                                                :            :
    #                  .... hold_bas_w ........      :.. hold_l...:
    #                 :                        :
    #                 :        .hold_w.        :
    #                 :       :       :        :
    #          X......:_______:_______:________:....
    #                 |       |       |        |    :
    #                 |       |       |        |    + hold_bas_l
    #                 |_______|       |________|....:
    #                         |       |        :
    #                         |_______|        :
    #                                          :
    #                                          :
    #                                          Y
    #oscad: translate ([aluprof_w,0,0])
    #oscad    cube([hold_w, hold_l, hold_h]);
    fcad03_pos = FreeCAD.Vector(kidler.aluprof_w,0,0)
    cq03 = cq.Workplane("XY", origin=(kidler.aluprof_w,0,0)).\
                         box(kidler.hold_w, kidler.hold_l, kidler.hold_h,
                         centered = (False, False, False))

    wp03_side = cq03.faces("<X").vertices(">Y and <Z").workplane(invert=True)
    
    #    --------------- step 04 --------------------------- 
    #    Fillets on top
    #                             aluprof_w   Z
    #                                  ..+....:
    #           .............f2_______f1      : 
    #           :             /       \       :
    #           :             |       |       :
    #   hold_h +:             |       |       :
    #           :             |       |       :
    #           :      _______|       |_______:
    #       X...:.....(_______|_______|_______)
    #
    cq04 = cq03.faces("+Z").edges("|Y").fillet(kidler.in_fillet)

    #    --------------- step 05 --------------------------- 
    #    large chamfer at the bottom

    #                                         Z      Z
    #                                         :      :
    #   Option A               _______        :      :____________
    #                         /       \       :      |            |
    #                         |       |       :      |            |
    #                         |_______|       :      |            |
    #                         |       |       :      |           /       
    #                  _______|_______|_______:      |________ /  
    #       X.........(_______________________)      |________|.......Y
    #                                                :            :

    #   
    #                                         Z      Z
    #                                         :      :
    #   Option B               _______        :      :____________
    #                         /       \       :      |            |
    #                         |       |       :      |            |
    #                         |       |       :      |            |
    #                         |_______|       :      |            |      
    #                  _______|       |_______:      |________   /  
    #       X.........(_______|_______|_______)      |________|/......Y
    #                                                :            :
    #                                                               
    edgechmf_list = []
    # option B: using more material (probably sturdier)
    #chmf_rad = min(kidler.hold_l - kidler.hold_bas_l,
    #              kidler.hold_h - (kidler.tens_h+2*kidler.wall_thick))
    # option A: using less material
    chmf_rad = min(kidler.hold_l-kidler.hold_bas_l+ kidler.hold_bas_h,
                   kidler.hold_h - (kidler.tens_h+2*kidler.wall_thick))
    cq05 = cq04.edges("|X and >Y and <Z").chamfer(chmf_rad)
    

    #    --------------- step 06 --------------------------- 
    #    Hole for the tensioner
    #                                         Z      Z
    #                                         :      :
    #                          _______        :      :____________
    #                         /  ___  \       :      |c2..........|
    #                         | |   | |       :      | :          |
    #                         | |___| |       :      |c1..........|
    #                         |_______|       :      |            |      
    #                  _______|       |_______:      |________   /  
    #       X.........(_______|_______|_______)      |________|/......Y

    #
    #oscad:translate([wall_thick-tol/2, hold_l-tens_l_inside,tens_pos_h-tol/2])
    #  oscad: cube([tens_w_tol, tens_l_inside+1, tens_h_tol]);
    if (kidler.opt_tens_chmf == 1):
       chmf_sel = "<Y"
    else:
       chmf_sel = "<Y and |X"

    cq06chmf =  cq05.faces(">Y").workplane().\
                rect(kidler.tens_w_tol,kidler.tens_h_tol).\
                extrude(-1.*kidler.tens_l_inside, False).edges(chmf_sel).\
                chamfer( 2*kidler.in_fillet-kidler.TOL)

    #    --------------- step 07 --------------------------- 
    #    A hole to be able to see inside, could be on one side or both
    #                                         Z      Z
    #                                         :      :
    #                          _______        :      :____________
    #                         /  ___  \       :      |  ._______ .|
    #                         |:|   |:|       :      | :|_______| |
    #                         | |___| |       :      |  ..........|
    #                         |_______|       :      |            |      
    #                  _______|       |_______:      |________   /  
    #       X.........(_______|_______|_______)      |________|/......Y

    # related to the main box
    # doesnt work as expected, so I will try another way:
    #cq_07aux=wp03_side.box(6.,3.,1.,centered=(False,False,False),combine=False)

    if  kidler.hold_hole_2sides == 1:
      cq07_x = kidler.hold_w
    else:
      cq07_x = kidler.hold_w/2.
    cq07 = cq.Workplane("XY", origin=(kidler.aluprof_w,
                                   kidler.wall_thick + kidler.nut_holder_thick,
                                   kidler.tens_pos_h +  kidler.tens_h /2
                                                     - kidler.tensnut_ap_tol)).\
                          box(cq07_x, kidler.hold_l - kidler.nut_holder_thick -
                                        2* kidler.wall_thick,
                                      2* kidler.tensnut_ap_tol, 
                              centered=(False,False,False))

    # /* --------------- step 08 --------------------------- 
    #    A hole for the leadscrew
    #                                         Z      Z
    #                                         :      :
    #                          _______        :      :____________
    #                         /  ___  \       :      |  ._______ .|
    #                         |:| O |:|       :      |::|_______| |
    #                         | |___| |       :      |  ..........|
    #                         |_______|       :      |            |      
    #                  _______|       |_______:      |________   /  
    #       X.........(_______|_______|_______)      |________|/......Y
    #
    #oscad: translate ([hold_w/2, -1, tens_pos_h + tens_h/2])
    #oscad:  rotate ([-90,0,0])
    #oscad:   cylinder (r=bolttens_r_tol, h=wall_thick+2, $fa=1, $fs=0.5); 

    cq08 = cq.Workplane("XZ", origin=(kidler.aluprof_w + kidler.hold_w/2.,0,
                                      kidler.tens_pos_h + kidler.tens_h/2.)).\
              circle(kidler.bolttens_r_tol).extrude(-kidler.wall_thick)

    #    --------------- step 09 --------------------------- 
    #    09a: Fuse all the elements to cut
    #    09b: Cut the box with the elements to cut
    #    09c: Fuse the base with the holder
    #    09d: chamfer the union
    #                             Z   Z
    #                             :   :
    #              _______        :   :____________
    #             /  ___  \       :   |  ._______ .|
    #             |:| O |:|       :   |::|_______| |...
    #            /| |___| |\      :   |  ..........|... tens_h/2 -tensnut_ap_tol
    #           / |_______| \     :   |            |  :+tens_pos_h
    #      ____/__|       |__\____:   |________   /   :  ...
    #  X..(_______|_______|_______)   |________|/.....:.....hold_bas_h
    #
    cq09a = cq06chmf.union(cq07).union(cq08)

    # fuse and chamfer the union 09b
    chmf_rad = min(kidler.aluprof_w/2,
                   kidler.tens_pos_h + kidler.tens_h/2
                   - kidler.tensnut_ap_tol - kidler.hold_bas_h);

    cq09b = cq02.union(cq05).faces("(not >Z) and +Z").\
         edges("|Y and ((not >X) and (not <X))").chamfer(chmf_rad)

    cq09c = cq09b.cut(cq09a)

    #    --------------- step 10 --------------------------- 
    #    Bolt holes to attach the piece to the aluminum profile
    #                              Z   Z
    #                              :   :
    #               _______        :   :____________
    #              /  ___  \       :   |  ._______ .|
    #              |:| O |:|       :   |::|_______| |
    #             /| |___| |\      :   |  ..........|
    #            / |_______| \     :   |            |
    #       ____/__|       |__\____:   |________   /
    #   X..(__::___|_______|__::___)   |___::___|/
    #

    cq10_1 = cq.Workplane("XY", origin=(kidler.aluprof_w/2.,
                                     kidler.aluprof_w/2., kidler.hold_bas_h)).\
                   circle(kidler.boltaluprof_r_tol).extrude(-kidler.hold_bas_h)
    cq10_1 = cq10_1.faces(">Z").circle(kidler.boltaluprof_head_r_tol).\
                   extrude(kidler.boltaluprof_head_l+2)

    cq10_2 = cq.Workplane("XY", origin=(kidler.hold_bas_w-kidler.aluprof_w/2.,
                                     kidler.aluprof_w/2., kidler.hold_bas_h)).\
                   circle(kidler.boltaluprof_r_tol).extrude(-kidler.hold_bas_h)
    cq10_2 = cq10_2.faces(">Z").circle(kidler.boltaluprof_head_r_tol).\
                   extrude(kidler.boltaluprof_head_l+2)

    cq10_final = cq09c.cut(cq10_1).cut(cq10_2)
    shp10 = cq10_final.toFreecad()

    fcd10_final = doc.addObject("Part::Feature", 'tensioner_holder_st10')
    fcd10_final.Shape = shp10
    fcd10_final.ViewObject.ShapeColor = (0.5, 0.7, 1.0)

    return cq10_final


# creation of a new FreeCAD document
doc = FreeCAD.newDocument()
# creation of the tensioner holder
cq_tens_holder = tensioner_holder()
# change color to light sky blue:

# ---------- export to stl
#try:
#    import ExportCQ
#except:
#    from . import ExportCQ
# Not working
#ExportCQ.exportShape(cq_tens_holder,"STL",'tensioner_holder.stl')
stlPath = filepath + '/../stl/'
stlFileName = stlPath + 'tensioner_holder' + '.stl'
# rotate to print without support:
#fcd_tens_holder.Placement.Rotation = (
                    #FreeCAD.Rotation(FreeCAD.Vector(1,0,0), 90))

cq_tens_holder_toprint = cq_tens_holder.rotate((0.,0.,0.),(1.,0.,0.),90.)
mesh_shp = MeshPart.meshFromShape(cq_tens_holder_toprint.toFreecad(),
                                  LinearDeflection=kparts.LIN_DEFL, 
                                  AngularDeflection=kparts.ANG_DEFL)
mesh_shp.write('C:/Users/felipe/urjc/proyectos/cad/py_freecad/filter_stage/src_cq/' + 'tensioner_holder' + '.stl')
cq_tens_holder = cq_tens_holder.rotate((0.,0.,0.),(1.,0.,0.),-90.)
#del mesh_shp


# rotate back, to see it in its real position
#fcd_tens_holder.Placement.Rotation = (
                    #FreeCAD.Rotation(FreeCAD.Vector(1,0,0), 0))

# save the FreeCAD file
freecadPath = filepath + '/../freecad/'
freecadFileName = freecadPath + 'tensioner_holder' + '.FCStd'
#doc.saveAs (freecadFileName)

