import numpy as np


def getPolyArea(points):
    area = 0.0
    try:
        for point in points:
            pts = np.array(point)
            x = pts[:, 0]
            y = pts[:, 1]
            area += 0.5*np.abs(np.dot(x,np.roll(y,1))-np.dot(y,np.roll(x,1)))
    finally:
        return area

def getLengthP2P(pt1, pt2):
    return np.linalg.norm(np.array(pt1)-np.array(pt2))

def getLengthP2Ps(pt, pts):
    return np.array(list(map(lambda point : np.linalg.norm(point-np.array(pt)), pts)))

def getLengthP2L(pt, linePt1, linePt2):
    pt = np.array(pt)
    linePt1 = np.array(linePt1)
    linePt2 = np.array(linePt2)
    vec1 = linePt1 - pt
    vec2 = linePt2 - pt
    return np.abs(np.cross(vec1, vec2)) / np.linalg.norm(linePt1 - linePt2)

def str2list(strInput):
    pointsArr = []
    l = strInput.split('L')
    for l1 in l:
        pointArr = []
        l2 = l1.split(',')
        for n in range(int(len(l2)/2)):
            pointArr.append([int(l2[2*n]), int(l2[2*n+1])])
        pointsArr.append(pointArr)
    return pointsArr

def list2str(listInput):
    # [[[x1,y1],[x2,y2]], [...]]
    output = ''
    for pointArr in listInput:
        for p1, p2 in pointArr:
            output = output + '%d,%d,'%(int(p1),int(p2))
        output = output[:-1] + 'L'
    return output[:-1]