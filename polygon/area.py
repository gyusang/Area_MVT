from shapely.geometry import *

def area(p): #list of tuple points in one order
    polygon = Polygon(p)
    return polygon.area

def intersect(p,l):
    
