from shapely.geometry import *
from matplotlib import pyplot as plt
from matplotlib import lines as mlines
from descartes import PolygonPatch
import numpy as np

error = 0.0001

def new_line(ax,x,y): #plot 내에 꽉차는 직선(선분)을 그리는 함수, 점 두 개를 입력받음
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

def plot_line(ax, ob):#직선 그리는 함수, 직선 객체를 입력받음.
    x, y = ob.xy
    new_line(ax,x,y)

def draw_poly(ax, plg, c='#0F00FF'):#다각형 그리는 함수, 다각형 점 목록 리스트를 입력받음
    ax.add_patch(PolygonPatch(Polygon(plg),alpha=0.6,color=c))

def sign(i): #부호를 반환하는 함수, 양수면 1, 음수면 -1, 영이면 0
    if i>0:
        return 1
    elif i<0:
        return -1
    elif i==0:
        return 0
    else:
        None

def slope_line(ax,slope,p): #기울기와 한 점으로 직선을 그리는 함수
    new_line(ax,(p[0],p[0]+1),(p[1],p[1]+slope))

def poly_area(plg,slope,p):#다각형에서 직선 위 부분의 넓이에서 다각형 넓이의 절반을 뺀 값을 반환하는 함수
    global ax
    y = p[1]-slope*p[0]#+0.00000001#점이 일치하면 부등식에 오류가 생기는 것을 방지하기 위해 약간 띄움
    xrange = [min(plg,key=lambda x:x[0])[0],max(plg,key=lambda x:x[0])[0]]
    yrange = [min(plg,key=lambda x:x[1])[1],max(plg,key=lambda x:x[1])[1]]
    line = LineString([(xrange[0],slope*xrange[0]+y),(xrange[1],slope*xrange[1]+y)])
    ring = LinearRing(plg)
    inter = line.intersection(ring)
    if inter.is_empty or type(inter)==Point :
        result = 1 if len([k for k in plg if k[1]>(slope*k[0]+y)])>0 else -1
        result *= Polygon(plg).area/2
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
    return Polygon(sectors[0]).area-Polygon(plg).area/2

def find_b_half(plg,slope,ax=None,ay=None):#이진 탐색으로 주어진 기울기로 다각형을 이등분하는 y절편값을 반환하는 함수
    dist = [k[1]-k[0]*slope for k in plg]
    yrange = [min(dist),max(dist)]
    if ay:
        ay.plot(yrange,[poly_area(plg,slope,(0,k))for k in yrange],'o')
    while True:
        if yrange[1]-yrange[0]<=0.000001:
            print("Failed to find")
            return None
        new_half = sum(yrange)/2
        D = poly_area(plg,slope,(0,new_half))
        if ay:
            ay.plot(new_half,D,'o')
        if abs(D)<error: break
        elif D>0: yrange[0]=new_half
        elif D<0: yrange[1]=new_half
    if ax:
        slope_line(ax,slope,(0,new_half))
    return new_half

def show_b_graph(plg,slope,ax=None,ay=None):#y절편에 따른 poly_area의 값을 그래프로 그리고 최소지점을 반환하는 함수
    dist = [k[1]-k[0]*slope for k in plg]
    yrange = (min(dist),max(dist))
    y = np.arange(yrange[0]-1,yrange[1]+1,0.01)
    areas = [poly_area(plg,slope,(0,k)) for k in y]
    if ay:
        ay.plot(y,areas)
    min_area = min(areas,key=lambda x:abs(x))
    #print(min_area)
    result = y[areas.index(min_area)]
    if ax:
        slope_line(ax,slope,(0,result))
        slope_line(ax,slope,(0,yrange[0]))
        slope_line(ax,slope,(0,yrange[1]))
    return result

def show_a_graph(plg1,plg2,ax=None,ay=None):
#기울기에 따른 두 번째 다각형의 분할된 넓이에서
#두 번째 다각형의 넓이의 절반을 뺀 값을 그리고 그 값이 0에 가장 가까운 직선을 반환하는 함수
    theta = np.arange(-np.pi/2+0.01,np.pi/2-0.01,0.01)
    slope = np.tan(theta)
    areas = [poly_area(plg2,k,(0,find_b_half(plg1,k)))for k in slope]
    if ay:
        ay.plot(theta,areas)
    min_area = min(areas,key=lambda x:abs(x))
    #print(min_area)
    result_slope = slope[areas.index(min_area)]
    #print(theta[areas.index(min_area)])
    result_b = find_b_half(plg1,result_slope)
    if ax:
        slope_line(ax,result_slope,(0,result_b))
    return (result_slope,result_b)

def find_a_half(plg1,plg2,ax=None,ay=None):
#이진 탐색으로 두 다각형을 동시에 이등분하는 직선을 찾아 반환하는 함수
    thetarange = [-np.pi/2+0.01,np.pi/2-0.01]
    areas = [poly_area(plg2,k,(0,find_b_half(plg1,k))) for k in np.tan(thetarange)]
    if ay:
        ay.plot(thetarange,areas,'o')
    if sign(areas[0])==sign(areas[1]) and areas[0]!=0:
        print("Failed to find")
        return None
    elif abs(areas[0]) < error:
        slope = np.tan(thetarange[0])
        if ax:
            slope_line(ax,slope,(0,find_b_half(plg1,slope)))
        return (slope,find_b_half(plg1,slope))
    elif abs(areas[1]) < error:
        slope = np.tan(thetarange[1])
        if ax:
            slope_line(ax,slope,(0,find_b_half(plg1,slope)))
        return (slope,find_b_half(plg1,slope))
    if areas[0]<0:
        thetarange.reverse()
    while True:
        if abs(thetarange[1]-thetarange[0])<0.000001 and max(thetarange,key=lambda x:abs(x))>np.pi/2-0.02:
            print("Failed to find")
            return None
        new_half = sum(thetarange)/2
        slope = np.tan(new_half)
        D = poly_area(plg2,slope,(0,find_b_half(plg1,slope)))
        if ay:
            ay.plot(new_half,D,'o')
        if abs(D)<error: break
        elif D<0: thetarange[1] = new_half
        elif D>0: thetarange[0] = new_half
    if ax:
        slope_line(ax,slope,(0,find_b_half(plg1,slope)))
    #print("D=%f,theta=%f"%(D,new_half))
    return (slope,find_b_half(plg1,slope))

def draw_half(plg1=[(1, 1),(1.7, 1.66),(4.28, 1.6),(3.06, 0.2),(1.26, -0.12)],
plg2=[(1.6, 2.94),(2.34, 1.34),(3.38, 1.14),(5.9, 2.18),(4, 4)]):
    fig = plt.figure('Ham Sandwich Theorem')
    ax = fig.add_subplot(111)
    ax.set_aspect(1)
    ax.set_title('Polygon')
    ax.set_xlim((min(Polygon(plg1).bounds[0],Polygon(plg2).bounds[0])-1,
    max(Polygon(plg1).bounds[2],Polygon(plg2).bounds[2])+1))
    ax.set_ylim((min(Polygon(plg1).bounds[1],Polygon(plg2).bounds[1])-1,
    max(Polygon(plg1).bounds[3],Polygon(plg2).bounds[3])+1))
    draw_poly(ax,plg1,'#27567b')
    draw_poly(ax,plg2,'#b63b3b')
    result = find_a_half(plg1,plg2,ax)
    plt.show()
    return result

if __name__=="__main__":#예제
    A = (1, 1)#10개의 점을 지정한다
    B = (1.7, 1.66)
    C = (4.28, 1.6)
    D = (3.06, 0.2)
    E = (1.26, -0.12)

    # F = (1, 3)#평행이동한 경우
    # G = (1.7, 3.66)
    # H = (4.28, 3.6)
    # I = (3.06, 2.2)
    # J = (1.26, 1.88)

    F = (1.6, 2.94)
    G = (2.34, 1.34)
    H = (3.38, 1.14)
    I = (5.9, 2.18)
    J = (4, 4)

    plg1 = [A,B,C,D,E]#두 개의 오각형을 만든다
    plg2 = [F,G,H,I,J]

    # plg1 = [(k[1],k[0])for k in plg1]#y=x 대칭
    # plg2 = [(k[1],k[0])for k in plg2]

    fig = plt.figure('Ham Sandwich Theorem')#그래프를 설정한다
    ax = fig.add_subplot(121)
    ay = fig.add_subplot(122)
    ax.set_aspect(1)
    ax.set_title('Polygon')
    ay.set_title('Area')
    #plt.xlabel('theta')
    ax.set_xlim((min(Polygon(plg1).bounds[0],Polygon(plg2).bounds[0])-1,
    max(Polygon(plg1).bounds[2],Polygon(plg2).bounds[2])+1))
    ax.set_ylim((min(Polygon(plg1).bounds[1],Polygon(plg2).bounds[1])-1,
    max(Polygon(plg1).bounds[3],Polygon(plg2).bounds[3])+1))

    draw_poly(ax,plg1,'#27567b')#다각형 두 개를 다른 색으로 그린다
    draw_poly(ax,plg2,'#b63b3b')

    #실행 예시

    #print(show_b_graph(plg2,-5,ax,ay))
    #print(find_b_half(plg1,10,ax,ay))
    #print(show_a_graph(plg1,plg2,ax,ay))
    print(find_a_half(plg1,plg2,ax,ay))

    plt.show()
