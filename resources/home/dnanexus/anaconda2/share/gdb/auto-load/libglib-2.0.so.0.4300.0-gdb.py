import sys
import gdb

# Update module path.
dir_ = '/home/aled/Documents/DNA_Nexus_app_github/dnanexus_mokabed/resources/home/dnanexus/anaconda2/share/glib-2.0/gdb'
if not dir_ in sys.path:
    sys.path.insert(0, dir_)

from glib import register
register (gdb.current_objfile ())
