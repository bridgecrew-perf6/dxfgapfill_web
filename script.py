import sys
import ezdxf
from ezdxf import recover
import math
import itertools
import os
import matplotlib.pyplot as plt
 

basdir = os.path.abspath(os.path.dirname(__file__))
Upload_dir = basdir + "/static/temp/"

#User Inputs 
angle_limit = 5 # max tilt angle to straighten
echo = False
summary_echo = True

    
# initialization
n=1  # number of lines
total_node_Z_moved_to_0= 0 #counter
loose_node_list=[]
number_of_lines_straighthened = 0
list_of_lines = []
list_of_nodes = []
number_of_connected_nodes= 0
number_of_loose_nodes_connected= 0 
   
def updated_file(new_file):
    
    try:
        doc = ezdxf.readfile(new_file)
        msp = doc.modelspace()
    except IOError:
        print(f'Not a DXF file or a generic I/O error.')
        sys.exit(1)
    except ezdxf.DXFStructureError:
        print('Invalid or corrupted DXF file.')
        sys.exit(2)
     

     
     

    
    round_all_up (msp)
    flatten(msp)
    remove_dots(msp)
    orientation(msp) 
    remove_duplicate_lines(msp)
    find_loose_nodes(msp)
    connect_loose_nodes(msp) 
    
    doc.saveas(Upload_dir +  "edited_" + new_file)

    directory = os.fsencode(basdir)
    for file in os.listdir(directory):
        filename = os.fsdecode(file)
        if filename.endswith(".dxf"):
            print(filename)
            os.remove(os.path.join(basdir,filename))
                    # filename = os.path.join(str(directory), str(filename))
            # dic =import_new_dictionary_object_api(filename, "zip")

    return f"successfully done"

 
def indentprint(value):
        print("\t" + str(value))
     
def round_all_up (msp): 
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
     

def flatten(msp):
    print("flatten () _ start") if echo== True else None
    global total_node_Z_moved_to_0
    for e in msp.query("LINE"):
        #removes z axis of all lines 
        if( e.dxf.start[2]!=0):
            e.dxf.start[2]=0 
            total_node_Z_moved_to_0 += 1
        if( e.dxf.end[2]!=0):
            e.dxf.end[2]=0 
            total_node_Z_moved_to_0 += 1
    
    print("flatten () _ end") if echo== True else None
    print("no. of lines flattened = \t {}".format(total_node_Z_moved_to_0)) if summary_echo == True else None

def straighten(e, angle_h):
    global number_of_lines_straighthened 
    print("straighten () _ start" ) if echo== True else None
    #if lines are not orthogonal, they get straightened
    #angle_h varies between 0 and 180 (+ only)
    
    #if line is close to positive x or negative x:
    if ( angle_h <= angle_limit or  180 - angle_h <= angle_limit):
        #line is close to horizontal
        #end y gets start y
        temp_list_end = list(e.dxf.end)
        temp_list_end[1]= e.dxf.start[1]
        e.dxf.end = tuple(temp_list_end)
        number_of_lines_straighthened +=1
        
    #if line is close to positive or negative y  
    elif ( abs(90 - angle_h) <= angle_limit):
        #line is close to vertical
        #end x gets start x
        temp_list_end = list(e.dxf.end)
        temp_list_end[0]= e.dxf.start[0]
        e.dxf.end = tuple(temp_list_end)
        number_of_lines_straighthened += 1
    print( "straighten () _ end" ) if echo== True else None
        
def orientation(msp):
    print("orientation () _ start") if echo== True else None
    #defines orientation and angle of the line
    global number_of_lines_straighthened 
    for e in msp.query("LINE"):    
        #x and y components of the line vector
        indentprint(str("Line #" + str(n)) + " start: %s " % e.dxf.start + "end: %s" % e.dxf.end) if echo== True else None
        x_line=e.dxf.end[0]  - e.dxf.start[0]  
        y_line=e.dxf.end[1]  - e.dxf.start[1]

        #orientation?
        if(y_line==0):
            orientation = "horizontal"
            indentprint(orientation)if echo== True else None
        elif(x_line==0):
            orientation = "vertical"
            indentprint(orientation)if echo== True else None
        else :
            orientation = "angled"
            angle_h = math.degrees(math.acos(  x_line/(1**0.5*(x_line**2+y_line**2)**0.5)))
            indentprint(str(angle_h) + "degree" ) if echo== True else None
            #only positive angle

            #straighten the line
            straighten (e, angle_h)
            indentprint(str("Line #" + str(n)) + " start: %s " % e.dxf.start + "end: %s" % e.dxf.end) if echo== True else None
    print("no. of lines straightened =\t {}".format(number_of_lines_straighthened))   if summary_echo== True else None
    print("orientation () _ end") if echo== True else None

def remove_dots(msp):
    total_removed_dots=0
    print("remove dots () _ start") if echo== True else None
    for e in msp.query("LINE"):
        if e.dxf.start == e.dxf.end :
            msp.delete_entity(e)
            total_removed_dots+=1
    print("no. of nodes removed= \t\t {}".format(total_removed_dots))   if summary_echo== True else None      
    print( "remove dots () _ end") if echo== True else None
            
def remove_duplicate_lines(msp):
    print( "remove duplicate lines () _ start"  ) if echo== True else None
    number_of_duplicate_lines= 0
    for a, b in itertools.combinations(msp.query("LINE"), 2):
        indentprint(str(a.dxf.start) + str(a.dxf.end)) if echo== True else None
        if( str(str(a.dxf.start) + str(a.dxf.end)) == str(str(b.dxf.start) + str(b.dxf.end))):
            indentprint( ">>> " + str(a.dxf.start) + str(a.dxf.end) + " deleted") if echo== True else None
            msp.delete_entity(a) 
            number_of_duplicate_lines +=1
                      
    print("no. of duplicate lines removed=  {}".format(number_of_duplicate_lines))   if summary_echo== True else None      
    print( "remove duplicate lines () _ end") if echo== True else None

def print_lines (msp):
    print( "count lines () _ start"  ) if echo== True else None
    global n
    n=0
    for e in msp.query("LINE"):    
        n+=1
        indentprint(str(e.dxf.start) + str(e.dxf.end)) if echo== True else None
    print( "count lines () _ end"  ) if echo== True else None
    return n 

def distance_f(node0,node1):
    print( "distance () _ start"  ) if echo== True else None
    x0=node0[0]
    y0=node0[1]
    z0=node0[2]
    x1=node1[0]
    y1=node1[1]
    z1=node1[2]
    print( "distance () _ end"  ) if echo== True else None
    return    (((x1-x0)**2 + (y1-y0)**2 + (z1-z0)**2 )**0.5)

def connect_loose_nodes(msp): 
    global number_of_loose_nodes_connected 
    print( "connect loose nodes () _ start"  ) if echo== True else None
    indentprint(loose_node_list) if echo== True else None
    for node in loose_node_list:
        indentprint(node) if echo== True else None
        distance_list=[]
        for node2 in loose_node_list:
            distance_list.append(distance_f(node,node2))
        indentprint("node: {}, distance list: {}".format(node, distance_list)) if echo== True else None
        for i in range(len(distance_list)):
            if distance_list[i] == 0.0:
                distance_list[i] = 10E10
        indentprint("node: {}, distance list: {}".format(node, distance_list)) if echo== True else None
        closest_distance=(min(distance_list))
        indentprint(closest_distance) if echo== True else None
        indentprint(distance_list.index(closest_distance)) if echo== True else None
        closest_node_index=distance_list.index(closest_distance)
        indentprint("node: {}, closest node: {}".format(node, loose_node_list[ closest_node_index])) #if echo== True else None
        msp.add_line(node,loose_node_list[ closest_node_index]  )
        number_of_loose_nodes_connected +=1
        
    
    print("no. of loose nodes connected= \t {}".format(number_of_loose_nodes_connected))   if summary_echo== True else None      
    print( "connect loose nodes () _ end"  ) if echo== True else None        
               
def find_loose_nodes(msp):
    global number_of_connected_nodes
    print( "find loose nodes () _start"  ) if echo== True else None
    
    for line in msp.query("LINE"):
        line_start_loose = True
        line_end_loose   = True
        for target in msp.query("LINE"):
            
            if target != line: 
                indentprint("\n \tcheck:") if echo== True else None
                indentprint("\tline  {} {}".format(line.dxf.start,line.dxf.end)) if echo== True else None
                indentprint("\ttarget  {} {}".format(target.dxf.start,target.dxf.end)) if echo== True else None
                if line.dxf.start == target.dxf.start  :
                    indentprint("\t{} - node {} matches with {}".format("i.",line.dxf.start,target.dxf.start)) if echo== True else None
                    line_start_loose = False
                elif line.dxf.start == target.dxf.end :
                    indentprint("\t{} - node {} matches with {}".format("ii.",line.dxf.start,target.dxf.end)) if echo== True else None
                    line_start_loose = False
                    
                if line.dxf.end == target.dxf.start  :
                    indentprint("\t{} - node {} matches with {}".format("iii.",line.dxf.end,target.dxf.start)) if echo== True else None
                    line_end_loose = False
                elif line.dxf.end == target.dxf.end :
                    indentprint("\t{} - node {} matches with {}".format("iv.",line.dxf.end,target.dxf.end)) if echo== True else None
                    line_end_loose = False
        print("____________________") if echo== True else None
        if line_start_loose == True:
            indentprint("line  {} {}. start is loose".format(line.dxf.start,line.dxf.end)) if echo== True else None
            loose_node_list.append(line.dxf.start)
        if line_end_loose == True:
            indentprint("line  {} {}. end is loose".format(line.dxf.start,line.dxf.end)) if echo== True else None
            loose_node_list.append(line.dxf.end)

    print("no. of loose nodes found = \t {}".format(len(loose_node_list)))   if summary_echo== True else None  
    print( "find loose nodes () _ end") if echo== True else None 


