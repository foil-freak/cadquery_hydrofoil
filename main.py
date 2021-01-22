import cadquery as cq
import numpy as np
import csv
from readPic import ReadWingShape

#configuration
wing_profile = 'e1098-il.csv' #almost all profiles can be found on airfoiltools.com (x-range is assumed to be 100 mm in code)
wing_silhouette = 'silhouette.png' #the top view silhouette of the wing
half_wing_span = 600
rib_distance = 20 #mm between invividual ribs
rot = 3 #angle of attack

def readWingProfileCoord(csv_filename, header_lines=9):
    '''
    This method reads in a CSV file as it can be downloaded from the http://airfoiltools.com Airfoil plotter.
    returns: a list of (X, Y)-coordinate tuples
    '''

    pts = []
    with open(csv_filename, 'r', newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        #skip header lines
        [next(reader, None) for item in range(header_lines)]

        #read in data points
        for row in reader:
            if row[0] == '':
                break #we have read all points
            pts.append((float(row[0]), float(row[1])))

    return pts

#get the x,y coordinates of data points that make up the wing profile
pts = readWingProfileCoord(wing_profile)

#get the wing silhouette (top view)
rws = ReadWingShape(wing_silhouette, half_wing_span)


result = None
scale = 1
bend_y = 0
offset_x = 10 

[x_off, length] = rws.getSilhouettePoints(0)
scale = length/100.

wp = cq.Workplane("XY").transformed(rotate=(x_off,0,-rot)).spline(scale*np.array(pts)).close().workplane() #reads the points from above point by point (x-coord,y-coord)

x_offset = 0
z_offset = 0

z_pos1 = np.arange(rib_distance, half_wing_span, 20)
z_pos2 = np.arange(z_pos1[-1]+2, half_wing_span, 0.5)
z_pos = np.append(z_pos1, z_pos2)
print(z_pos)

for i in z_pos:
    [x_off, length] = rws.getSilhouettePoints(i)
    scale = length/100.
    print('x-pos: ', i, ' x-offset ', x_offset, ' scale: ', scale)
    
    wp2 = wp.transformed(offset=(x_off-x_offset, bend_y, i-z_offset), rotate=(0, 0, 0)).spline(scale*np.array(pts)).close().workplane()
    if result is None:
        result = wp2.loft(combine=True)
    else:
        nextpart = wp2.loft(combine=True)
        result = result.union(nextpart)
    wp = wp.transformed(offset=(x_off-x_offset, bend_y, i-z_offset), rotate=(0, 0, 0)).spline(scale*np.array(pts)).close().workplane()
    bend_y = 1.01*bend_y
    rot = rot - 0.02 #reduce the angle of attach as you g
    x_offset = x_off
    z_offset = i

result = result.rotate((0,0,0), (100,0,0), 180)
show_object(result)
result2 = result.mirror(mirrorPlane=("XY"))
show_object(result2)

