# FreeCAD scripted components and functions

## `kcomp.py`

Constants and dimensions for components:
* LME10UU, LME12UU linear bearing
* E3D V6 extruder
* DIN-912 bolt
* DIN-934 nut
* SK12 shaft holder

It also includes the default tolerances and the 3D printer layer height



## `comps.py`

Creates freecad components

### Dependencies:
../fcfun functions
/../../freecad/comps/misumi_profile_hfs_serie6_w8_30x30.FCStd

### Components

**class Sk**

SK12 shaft holder

**class MisumiAlu30s6w8**

Misumi Aluminum extrusion 30x30 hfs serie 6 width 8

## `fcfunc.py`

Python functions and constants for FreeCAD scripts

```
def addBox (x, y, z, name, cx= False, cy=False)
def addCyl (r, h, name)
def addBolt (r_shank, l_bolt, r_head, l_head,
             hex_head = 0, extra=1, support=1, headdown = 1, name="bolt")
def addBoltNut_hole (r_shank,        l_bolt, 
                     r_head,         l_head,
                     r_nut,          l_nut,
                     hex_head = 0,   extra=1,
                     supp_head=1,    supp_nut=1,
                     headdown=1,     name="bolt")         
class NutHole ()
    def __init__(self, nut_r, nut_h, hole_h, name,
                 extra = 1, nuthole_x = 1, cx=0, cy=0, holedown = 0)            
def fillet_len (box, e_len, radius, name)            
```
