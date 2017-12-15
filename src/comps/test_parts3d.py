# ----------------------------------------------------------------------------
# -- Test Parts 3D
# -- To test the classes and functions of parts3d.py
# ----------------------------------------------------------------------------
# -- (c) Felipe Machado
# -- Area of Electronics. Rey Juan Carlos University (urjc.es)
# -- October-2016
# ----------------------------------------------------------------------------
# --- LGPL Licence
# ----------------------------------------------------------------------------



#  execute freecad from the cmd console on the directory
# "C:\Program Files\FreeCAD 0.16\bin\freecad" test_parts3d.py

# to excute from command line in windows:
# "C:\Program Files\FreeCAD 0.16\bin\freecadcmd" test_parts3d.py

import os
import sys
import FreeCAD;
import Part;
import Draft;
import logging  # to avoid using print statements
#import copy;
#import Mesh;


# to get the current directory. Freecad has to be executed from the same
# directory this file is
filepath = os.getcwd()

# to get the components
# In FreeCAD can be added: Preferences->General->Macro->Macro path
sys.path.append(filepath) 

import fcfun   # import my functions for freecad. FreeCad Functions
import kcomp   # import material constants and other constants
import comps   # import my CAD components
import parts3d   # import my CAD components to print

from fcfun import V0, VX, VY, VZ, V0ROT, addBox, addCyl, fillet_len
from fcfun import addBolt, addBoltNut_hole, NutHole
from kcomp import TOL


logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)s - %(message)s')

doc = FreeCAD.newDocument()



endshaftslider = parts3d.EndShaftSlider(slidrod_r = 6.0,
                                holdrod_r = 6.0,
                                holdrod_sep = 150.0,
                                name          = "slider_left",
                                holdrod_cen = 0,
                                side = 'left')

doc.recompute()
