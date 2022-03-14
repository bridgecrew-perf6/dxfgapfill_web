import sys
import ezdxf
from ezdxf import recover
import math
import itertools
import os
import matplotlib.pyplot as plt
 

basdir = os.path.abspath(os.path.dirname(__file__))
Upload_dir = basdir + "/static/temp/"

def upated_file(new_file):
    try:
        doc = ezdxf.readfile(new_file)
    except IOError:
        print(f'Not a DXF file or a generic I/O error.')
        sys.exit(1)
    except ezdxf.DXFStructureError:
        print('Invalid or corrupted DXF file.')
        sys.exit(2)
     

    #User Inputs 
    angle_limit = 5 # max tilt angle to straighten
    echo = False
    summary_echo = True

    # initialization
    n=1  # number of lines  
        
    def round_all_up ():
        print("round all up () _ start") if echo== True else None
        #rounds x and y of all nodes , removes decimals
        print(len(msp.query("LINE")))  if echo== True else None

        for e in msp.query("LINE"):
            i = 0
            temp_list_start=[round(e.dxf.start[0]) , round(e.dxf.start[1])] 
            temp_list_end=[round(e.dxf.end[0]) , round(e.dxf.end[1]) ]
            e.dxf.start = tuple(temp_list_start)
            e.dxf.end = tuple(temp_list_end)
        print("round all up () _ end" ) if echo== True  else None
        print("no. of lines rounded = \t\t {}".format(len(msp.query("LINE")))) if summary_echo == True else None
         

    doc.saveas(Upload_dir +  "edited" + new_file)

    directory = os.fsencode(basdir)
    for file in os.listdir(directory):
        filename = os.fsdecode(file)
        if filename.endswith(".dxf"):
            print(filename)
            os.remove(os.path.join(basdir,filename))
                    # filename = os.path.join(str(directory), str(filename))
            # dic =import_new_dictionary_object_api(filename, "zip")

    return f"successfully done"

