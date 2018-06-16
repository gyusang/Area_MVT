from shapely.geometry import *
from matplotlib import pyplot as plt
from matplotlib import lines as mlines
from descartes import PolygonPatch
import numpy as np



#def plot_line(ax, ob):
#    x, y = ob.xy
#    ax.plot(x, y) #, alpha=0.7, linewidth=3, solid_capstyle='round', zorder=2)

def new_line(ax,x,y):
    xmin, xmax = ax.get_xbound()

    if(x[0] == x[1]):
        xmin = xmax = x[0]
        ymin, ymax = ax.get_ybound()
    else:
        ymax = y[0]+(y[1]-y[0])/(x[1]-x[0])*(xmax-x[0])
        ymin = y[0]+(y[1]-y[0])/(x[1]-x[0])*(xmin-x[0])

    l = mlines.Line2D([xmin,xmax], [ymin,ymax])
    ax.add_line(l)
    return l

def plot_line(ax, ob):
    x, y = ob.xy
    new_line(ax,x,y)

def draw_poly(ax, ob):
    ax.add_patch(PolygonPatch(ob))

def sign(i):
    if i>0:
        return 1
    elif i<0:
        return -1
    elif i==0:
        return 0
    else:
        None

def slope_line(ax,slope,p):
    new_line(ax,(p[0],p[0]+1),(p[1],p[1]+slope))

def poly_area(plg,slope,p):#볼록 다각형 가정, plg : polygon points, slope : slope of line, y : y절편
    global ax
    #ax.plot(p[0],p[1],'o')
    y = p[1]-slope*p[0]+0.00000001
    xrange = [min(plg,key=lambda x:x[0])[0],max(plg,key=lambda x:x[0])[0]]
    yrange = [min(plg,key=lambda x:x[1])[1],max(plg,key=lambda x:x[1])[1]]
    line = LineString([(xrange[0],slope*xrange[0]+y),(xrange[1],slope*xrange[1]+y)])
    #plot_line(ax,line)
    ring = LinearRing(plg)
    inter = line.intersection(ring)
    if inter.is_empty or type(inter)==Point :
        result = 1 #if len([k for k in plg if k[1]>(slope*k[0]+y)])>0 else -1
        result *= Polygon(plg).area
        return result

    status = sign(plg[-1][1]-(slope*plg[-1][0]+y))
    sectors = [[],[]]
    for i in range(len(plg)):
        D = sign(plg[i][1]-(slope*plg[i][0]+y))
        if D==0:
            sectors[0].append(plg[i])
            sectors[1].append(plg[i])
        elif D*status>=0:
            sectors[(D-1)//2].append(plg[i])
        elif D*status==-1:
            inter = line.intersection(LineString([plg[i-1],plg[i]]))
            if not inter.is_empty:
                sectors[0].append((inter.x,inter.y))
                sectors[1].append((inter.x,inter.y))
            sectors[(D-1)//2].append(plg[i])
        status = D
#    draw_poly(ax,Polygon(sectors[0]))
#    draw_poly(ax,Polygon(sectors[1]))
    return abs(Polygon(sectors[0]).area - Polygon(sectors[1]).area)

def poly_slope_half(plg,slope,ax,ay=None):
    dist = [k[1]-k[0]*slope for k in plg]
    yrange = (min(dist),max(dist))
    y = np.arange(yrange[0]-1,yrange[1]+1,0.01)
    areas = [poly_area(plg,slope,(0,k)) for k in y]
    if ay:
        ay.plot(y,areas)
    min_area = min(areas)
    print(min_area)
    result = y[areas.index(min_area)]
    slope_line(ax,slope,(0,result))
    return result

C = (2.94, 2.46)
D = (2.28, 3.96)
E = (-0.22, 4.32)
F = (-0.22, 1.64)
G = (0.82, 0.66)

plg = Polygon([C,D,E,F,G])
fig = plt.figure('Ham Sandwich Theorem')
ax = fig.add_subplot(121)
ay = fig.add_subplot(122)
ax.set_aspect(1)
#ay.set_aspect(1)
ax.set_title('Polygon')
ay.set_title('Area by Location')
ax.set_xlim((plg.bounds[0]-1,plg.bounds[2]+1))
ax.set_ylim((plg.bounds[1]-1,plg.bounds[3]+1))
draw_poly(ax,plg)
#X = sorted(list(np.random.triangular(-10,0,10,1000)))
#p = C
#Y = [poly_area([C,D,E,F,G],x,p) for x in X]
#minimum = X[Y.index(min(Y))]
#slope_line(ax,minimum,p)
print(poly_slope_half([C,D,E,F,G],10,ax,ay))
#print(min(Y))
#result = poly_area([C,D,E,F,G],0,E)
#print(result)
#ay.plot(X,Y)
plt.show()
