import cv2
import numpy as np
import os

from config import Config
import mainGUI

from multiprocessing import Process
from multiprocessing.sharedctypes import Value, Array

import unit.calculateTools as ct


################################################################
##                           OpenCV                           ##
################################################################
class CV(Config):
    def __init__(self, parameters):
        self.parameters = parameters
        self.pos = ''
        
        self.windowWidth = Config.DISPLAY_WIDTH
        self.windowHeight = Config.DISPLAY_HEIGHT

        # 初始化状态
        self.isMove = False # 点移動
        self.isCreate = False # 区域创建
        self.isSelect = True # 区域选择
        self.mouseOverPoint = False
        self.mouseOverLine = False
        
        # 点数据读取
        self.areas = []
        self.newArea = []
        # self.areas = [[area1], [area2]]
        # self.areas = [[[x1,y1],[x2,y2]], [...]]
        self.selectedArea = -1
        self.selectedPoint = -1

        # 初始化画面
        self.frame = np.zeros((self.windowHeight, self.windowWidth, 3),np.uint8)
        self.mask = np.zeros((self.windowHeight, self.windowWidth, 3),np.uint8)
        self.maskMouseEvent = np.zeros((self.windowHeight, self.windowWidth, 3),np.uint8)


        cv2.namedWindow('image')
        cv2.setMouseCallback('image',self.mouseEvent)

        self.main()

    def main(self):
        while True:
            self.updateMask()
            self.display()

    # 画面表示
    def display(self):
        try:
            imgFilePath = os.path.join(self.parameters['filePath'].value)
            imgFilePath = str(imgFilePath, encoding='utf-8')
            if os.path.exists(imgFilePath):
                self.frame = cv2.imread(imgFilePath)
                self.frame = cv2.resize(self.frame, (self.windowHeight, self.windowWidth))
            else:
                self.frame = np.zeros((self.windowHeight, self.windowWidth, 3),np.uint8)
        except:
            self.frame = np.zeros((self.windowHeight, self.windowWidth, 3),np.uint8)

        result = self.frame.copy()
        result = cv2.add(result, self.mask)
        result = cv2.add(result, self.maskMouseEvent)
        cv2.imshow('image',result)
        key = cv2.waitKey(33) & 0xFF
        self.keyboardEvent(key)

    def updateMask(self):
        try:
            _pos = str(self.parameters['pos'].value, encoding='utf-8')
            if self.pos != _pos:
                self.pos = _pos
                self.areas = ct.str2list(_pos)

            _mask = np.zeros((self.windowHeight, self.windowWidth, 3),np.uint8)
            for points in self.areas:
                pts = np.array(points, np.int32).reshape((-1,1,2)) #数据类型必须是int32
                cv2.polylines(_mask, [pts], True, (128,128,128), 4)
                for point in points:
                    cv2.circle(_mask, point, 5,(255,255,255),-1)

            self.mask = _mask
        except:
            pass

    # マウスイベント
    def mouseEvent(self, event, x, y, flags, param):
        _mask = np.zeros((self.windowHeight, self.windowWidth, 3),np.uint8)

        # (区域选择)显示将被选择的区域
        if self.isSelect:
            areaSelected = self.areaSelect(x,y)
            if areaSelected >= 0:
                areaSelectedPoints = self.areas[areaSelected]
                pts = np.array(areaSelectedPoints, np.int32).reshape((-1,1,2)) #数据类型必须是int32
                cv2.polylines(_mask, [pts], True, (0,0,255), 4)
        
        # (点移动)显示将被选择的点
        elif self.isMove:
            pointSelected = self.pointSelect(x,y)
            if pointSelected >= 0:
                cv2.circle( _mask,
                            self.areas[self.selectedArea][pointSelected], # center
                            Config.MOUSE_OVER_POINT, # 半径
                            (255,0,0), # 色
                            -1)
                self.mouseOverPoint = True
            else:
                self.mouseOverPoint = False

            # 移动点
            if self.selectedPoint >= 0:
                cv2.circle( _mask,
                            self.areas[self.selectedArea][self.selectedPoint], # center
                            Config.MOUSE_OVER_POINT, # 半径
                            (0,0,255), # 色
                            -1)
                x = x if x>=0 else 0
                x = x if x<=self.windowWidth else self.windowWidth
                y = y if y>=0 else 0
                y = y if y<=self.windowHeight else self.windowHeight
                # 将点的信息保存到self.areas中
                self.areas[self.selectedArea][self.selectedPoint] = [x,y]
                print(f"\rMoving to (X:{x}, Y:{y})",end="")
            # 增加点
            else:
                pts = np.array(self.areas[self.selectedArea], np.int32).reshape((-1,1,2)) #数据类型必须是int32
                dist = cv2.pointPolygonTest(pts,(x,y),True)
                if abs(dist) <= Config.ADD_POINT_Limited:
                    distMinIndex = self.getPointLineDist([x,y], dist)
                    if distMinIndex >= 0:
                        self.mouseOverLine = True
                        _points = self.areas[self.selectedArea].copy()
                        _points.insert(distMinIndex, [x,y])
                        pts = np.array(_points, np.int32).reshape((-1,1,2))
                        cv2.polylines(_mask, [pts], True, (255,0,0), 2)
                        cv2.circle(_mask, [x,y], 5,(255,255,255),-1)
                else:
                    self.mouseOverLine = False
                    
        # 创建点
        elif self.isCreate:
            if ct.getLengthP2P(self.newArea[0],[x, y]) <= Config.MOUSE_OVER_Limited and\
            len(self.newArea) > 3:
                pts = np.array(self.newArea, np.int32).reshape((-1,1,2)) #数据类型必须是int32
                cv2.polylines(_mask, [pts], True, (0,255,0), 4)
            else:
                self.newArea[-1] = [x,y]
                pts = np.array(self.newArea, np.int32).reshape((-1,1,2)) #数据类型必须是int32
                cv2.polylines(_mask, [pts], False, (0,0,255), 2)

            for point in self.newArea:
                cv2.circle(_mask, point, 5,(255,255,255),-1)

        if event == cv2.EVENT_LBUTTONDBLCLK:
            pass

        # 按下左键的动作
        elif event == cv2.EVENT_LBUTTONDOWN:
            # 锁定移动点
            if self.isMove:
                if self.mouseOverPoint and self.selectedPoint == -1:
                    self.selectedPoint = self.pointSelect(x, y)
                    print('Point %d was Selected'%self.selectedPoint)

        # 松开左键的动作
        elif event == cv2.EVENT_LBUTTONUP:
            # 区域选择模式
            if self.isSelect and self.selectedArea == -1:
                areaSelected = self.areaSelect(x, y)
                if areaSelected >= 0:
                    self.selectedArea = areaSelected
                    self.isSelect = False
                    print('Area %d was Selected'%self.selectedArea)
                    self.isMove = True
                    print('Moving Point ON')

            # 取消锁定的移动点
            elif self.isMove:
                if self.selectedPoint >= 0:
                    self.selectedPoint = -1
                    print(' Done')
                elif self.mouseOverLine:
                    self.areas[self.selectedArea].insert(distMinIndex, [x,y])

            # 将新的点保存到self.areas中
            elif self.isCreate:
                if len(self.newArea) > 3 and \
                ct.getLengthP2P(self.newArea[0],[x, y]) <= Config.MOUSE_OVER_Limited:
                    self.areas.append(self.newArea[:-1])
                    self.newArea = [[0,0]]
                else:
                    self.newArea.append([x,y])

        # 右键按下
        elif event == cv2.EVENT_RBUTTONDOWN:
            # 撤销上一个创建的点
            if self.isCreate:
                if len(self.newArea) > 1:
                    self.newArea.pop()

        # send to tkGUI
        sendstr = ct.list2str(self.areas)
        self.parameters['pos'].value = bytes(sendstr, encoding='utf8')

        self.maskMouseEvent = _mask

    # キーボードイベント
    def keyboardEvent(self, key):
        # create a new area [N]
        if key == ord('n') or key == ord('N') :
            self.newArea.append([0,0])
            self.isMove = False # 点移動
            self.isCreate = True # 区域创建
            self.isSelect = False # 区域选择
            print("Creating Mode ON")

        # delete areas
        elif key == ord('c') or key == ord('C') :
            self.parameters['pos'].value = bytes('', encoding='utf8')

        # esc键解除当前选择的区域
        elif key == Config.KEY_MAP['ESC'] :
            if self.isMove and self.selectedArea >= 0:
                print("Area %d was Unselected"%self.selectedArea)
                self.selectedArea = -1
                self.selectedPoint = -1
                self.newArea.clear()
                self.isMove = False
                self.isCreate = False
                self.isSelect = True

            elif self.isCreate:
                self.isMove = False # 点移動
                self.isCreate = False # 区域创建
                self.isSelect = True # 区域选择
                self.newArea.clear()
                print("Create Mode Excted")

    def areaSelect(self, x, y):
        # 计算鼠标和area的距离
        if len(self.areas) > 0:
            dists = []
            for points in self.areas:
                pts = np.array(points, np.int32).reshape((-1,1,2)) #数据类型必须是int32
                dist = cv2.pointPolygonTest(pts,(x,y),True)
                dists.append(dist)
            distMinIndex = np.argmax(dists) # 最大値のインデックス
            if dists[distMinIndex] >= -Config.MOUSE_OVER_Limited:
                return distMinIndex
            else:
                return -1
        else:
            return -1

    def pointSelect(self, x, y):
        # マウスポインターと点の距離を計算
        dists = ct.getLengthP2Ps([x,y], self.areas[self.selectedArea])
        distMinIndex = np.argmin(dists) # 最小値のインデックス
        if dists[distMinIndex] <= Config.MOUSE_OVER_Limited:
            return distMinIndex
        else:
            return -1

    # 计算点到线的距离
    def getPointLineDist(self, pos, dist):
        _posArr = self.areas[self.selectedArea]
        for n in range(len(_posArr)):
            distance = ct.getLengthP2L(pos, _posArr[n-1], _posArr[n])
            if distance == abs(dist):
                return n
        return -1
            

if __name__ == '__main__':
    # 変数初期化
    parameters = {
        'filePath': Array('c', 200), # path
        'fileNum':  Value('i', -1), # path
        'pos':      Array('c', 200), # 点の座標
    }

    process_GUI = Process(target=mainGUI.GUI, args=(parameters,))
    process_CV = Process(target=CV, args=(parameters,))

    process_GUI.start()
    process_CV.start()

    process_GUI.join()
    process_CV.join()