from PyQt5 import QtCore, QtOpenGL
from PyQt5.QtWidgets import *
from OpenGL.GL import *

from hetool import HeView,HeController,HeModel, Patch, Point,Tesselation

class MyCanvas(QtOpenGL.QGLWidget):
    def __init__(self):
        super(MyCanvas, self).__init__()
        self.m_model = None
        self.m_w = 0  # width: GL canvas horizontal size
        self.m_h = 0  # height: GL canvas vertical size
        self.m_L = -1000.0
        self.m_R = 1000.0
        self.m_B = -1000.0
        self.m_T = 1000.0
        self.gridbool = 0
        self.pointsbool = 1
        self.gridbooldraw = 0
        self.gridcoordlist = []
        self.patchpointlist = []
        self.subx = None
        self.suby = None
        self.list = None
        self.connectlist = []
        self.connectpoint = []
        self.ypointdif = None
        self.xpointdif = None
        self.colums = None
        self.colums = None
        self.pointlist = []
        self.m_buttonPressed = False
        self.m_pt0 = QtCore.QPoint(0.0, 0.0)
        self.m_pt1 = QtCore.QPoint(0.0, 0.0)

        self.tol = 0.1
        self.hemodel = HeModel()
        self.heview = HeView(self.hemodel)
        self.hecontroller = HeController(self.hemodel)

    def initializeGL(self):
        #glClearColor(1.0, 1.0, 1.0, 1.0)
        glClear(GL_COLOR_BUFFER_BIT)
        glEnable(GL_LINE_SMOOTH)
        self.list = glGenLists(1)

    def resizeGL(self, _width, _height):
        # store GL canvas sizes in object properties
        self.m_w = _width
        self.m_h = _height

        if self.m_model == None or self.m_model.isEmpty():
            self.scaleWorldWindow(1.0)
        else:
            self.m_L, self.m_R, self.m_B, self.m_T = self.m_model.getBoundBox()
            self.scaleWorldWindow(1.1)

        # setup the viewport to canvas dimensions
        glViewport(0, 0, self.m_w, self.m_h)
        # reset the coordinate system
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        # establish the clipping volume by setting up an
        # orthographic projection
        glOrtho(self.m_L, self.m_R, self.m_B, self.m_T, -1.0, 1.0)
        # setup display in model coordinates
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

    def paintGL(self):
        # clear the buffer with the current clear color
        glClear(GL_COLOR_BUFFER_BIT)
        # draw the model
        # if (self.m_model == None) or (self.m_model.isEmpty()):
        #     return

        glCallList(self.list)
        glDeleteLists(self.list, 1)
        self.list = glGenLists(1)
        glNewList(self.list, GL_COMPILE)

        pt0_U = self.convertPtCoordsToUniverse(self.m_pt0)
        pt1_U = self.convertPtCoordsToUniverse(self.m_pt1)
        glColor3f(1.0, 0.0, 0.0)
        glBegin(GL_LINE_STRIP)
        glVertex2f(pt0_U.x(), pt0_U.y())
        glVertex2f(pt1_U.x(), pt1_U.y())
        glEnd()

        
        if not((self.m_model == None) or (self.m_model.isEmpty())):
            verts = self.m_model.getVerts()
            glColor3f(0.0, 1.0, 0.0)  # green
            # glBegin(GL_TRIANGLES)
            # for vtx in verts:
            #     glVertex2f(vtx.getX(), vtx.getY())
            # glEnd()
            curves = self.m_model.getCurves()
            glColor3f(0.0, 0.0, 1.0)  # blue
            glBegin(GL_LINES)
            for curv in curves:
                glVertex2f(curv.getP1().getX(), curv.getP1().getY())
                glVertex2f(curv.getP2().getX(), curv.getP2().getY())
            glEnd()

        if not self.heview.isEmpty():
            patches = self.heview.getPatches()
            glColor3f(1.0, 1.0, 1.0)
            for pat in patches:
                triangs = Tesselation.tessellate(pat.getPoints())
                for triang in triangs:
                    glBegin(GL_TRIANGLES)
                    for pt in triang:  
                        glVertex2d(pt.getX(), pt.getY())    
                    glEnd()
                
            segments = self.heview.getSegments()
            glColor3f(0.0, 1.0, 1.0)
            for curv in segments:
                ptc = curv.getPointsToDraw()
                # glColor3f(0.0, 1.0, 1.0)
                glBegin(GL_LINES)
                # for ptc in points:
                glVertex2f(ptc[0].getX(), ptc[0].getY())
                glVertex2f(ptc[1].getX(), ptc[1].getY())
                glEnd()
            if(self.pointsbool):
                vertexes = self.heview.getPoints()
                glColor3f(1.0, 0.0, 0.0)
                glPointSize(5)
                glBegin(GL_POINTS)
                for verts in vertexes:
                    glVertex2f(verts.getX(), verts.getY())
                glEnd()
        
        if (self.gridbooldraw == 1): #grid building
            if(len(self.gridcoordlist)>0):
                if(self.gridbooldraw):
                    self.gridDraw()

        if (self.gridbool == 1): #grid building
            if(len(self.gridcoordlist)>0):
                self.checkGridPointInsideDomainsAndPaint()
                self.connect()
            
        # Display model polygon RGB color at its vertices
        # interpolating smoothly the color in the interior
        # verts = self.m_model.getVerts()
        # glShadeModel(GL_SMOOTH)
        # glColor3f(0.0, 1.0, 0.0)  # green
        # glBegin(GL_TRIANGLES)
        # for vtx in verts:
        #     glVertex2f(vtx.getX(), vtx.getY())
        # glEnd()
        glEndList()

    def setModel(self, _model):
        self.m_model = _model

    def fitWorldToViewport(self): #atualizar para modelo novo
        if self.m_model == None:
            return

        self.m_L, self.m_R, self.m_B, self.m_T = self.m_model.getBoundBox()

        self.scaleWorldWindow(1.1)
        self.update()
        if(self.gridbool):
            self.getGridPointCoordinates(self.subx,self.suby)
            self.paintGL()

    def scaleWorldWindow(self, _scaleFac):
        # Compute canvas viewport distortion ratio.
        vpr = self.m_h / self.m_w

        # Get current window center.
        cx = (self.m_L + self.m_R) / 2.0
        cy = (self.m_B + self.m_T) / 2.0

        # Set new window sizes based on scaling factor.
        sizex = (self.m_R - self.m_L) * _scaleFac
        sizey = (self.m_T - self.m_B) * _scaleFac

        # Adjust window to keep the same aspect ratio of the viewport.
        if sizey > (vpr*sizex):
            sizex = sizey / vpr
        else:
            sizey = sizex * vpr

        self.m_L = cx - (sizex * 0.5)
        self.m_R = cx + (sizex * 0.5)
        self.m_B = cy - (sizey * 0.5)
        self.m_T = cy + (sizey * 0.5)

        # Establish the clipping volume by setting up an
        # orthographic projection
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glOrtho(self.m_L, self.m_R, self.m_B, self.m_T, -1.0, 1.0)


    def panWorldWindow(self, _panFacX, _panFacY):
        # Compute pan distances in horizontal and vertical directions.
        panX = (self.m_R - self.m_L) * _panFacX
        panY = (self.m_T - self.m_B) * _panFacY
        # Shift current window.
        self.m_L += panX
        self.m_R += panX
        self.m_B += panY
        self.m_T += panY
        # Establish the clipping volume by setting up an
        # orthographic projection
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glOrtho(self.m_L, self.m_R, self.m_B, self.m_T, -1.0, 1.0)

    def convertPtCoordsToUniverse(self, _pt):
        dX = self.m_R - self.m_L
        dY = self.m_T - self.m_B
        mX = _pt.x() * dX / self.m_w
        mY = (self.m_h - _pt.y()) * dY / self.m_h
        x = self.m_L + mX
        y = self.m_B + mY
        return QtCore.QPointF(x, y)

    def mousePressEvent(self, event):
        self.m_buttonPressed = True
        self.m_pt0 = event.pos()


    def mouseMoveEvent(self, event):
        if self.m_buttonPressed:
            self.m_pt1 = event.pos()
            self.update()

    def mouseReleaseEvent(self, event):
        pt0_U = self.convertPtCoordsToUniverse(self.m_pt0)
        pt1_U = self.convertPtCoordsToUniverse(self.m_pt1)
        
        _,xs1,ys1 = self.heview.snapToPoint(pt0_U.x(),pt0_U.y(),50)
        _,xs2,ys2 = self.heview.snapToPoint(pt1_U.x(),pt1_U.y(),50)
        pt0_U.setY(ys1)
        pt0_U.setX(xs1)
        pt1_U.setY(ys2)
        pt1_U.setX(xs2)
    
        self.m_model.setCurve(pt0_U.x(), pt0_U.y(), pt1_U.x(), pt1_U.y())

        self.hecontroller.insertSegment([pt0_U.x(), pt0_U.y(), pt1_U.x(), pt1_U.y()], self.tol)

        self.m_buttonPressed = False
        self.m_pt0.setX(0.0)
        self.m_pt0.setY(0.0)
        self.m_pt1.setX(0.0)
        self.m_pt1.setY(0.0)

        # if(snapped2):
        #     pt1_U.setX(xs2)
        #     pt1_U.setY(ys2)

        # if(snapped1):
        #     pt0_U.setX(xs1)
        #     pt0_U.setY(ys1)
        
        self.update()
        self.paintGL()

    def getGridInput(self,subX,subY):
        patchlist = self.heview.getPatches()
        if (len(patchlist) == 0):
            return
    
        self.getGridPointCoordinates(subX,subY)

    def gridDraw(self):
        glColor3f(1.0, 0.0, 0.0)
        glBegin(GL_LINES)
        for gpos1 in range(0, self.suby+1):
            for gpos2 in range(0,self.subx+1):
                if(gpos2 != self.subx):
                    glVertex2f(self.gridcoordlist[gpos1][gpos2][0],self.gridcoordlist[gpos1][gpos2][1])
                    glVertex2f(self.gridcoordlist[gpos1][gpos2+1][0],self.gridcoordlist[gpos1][gpos2+1][1])
                if(gpos1 != self.suby):
                    glVertex2f(self.gridcoordlist[gpos1][gpos2][0],self.gridcoordlist[gpos1][gpos2][1])
                    glVertex2f(self.gridcoordlist[gpos1+1][gpos2][0],self.gridcoordlist[gpos1+1][gpos2][1])
        glEnd()
        





    def getGridPointCoordinates(self,subX,subY):
        self.gridcoordlist = []
        xmin,xmax,ymin,ymax = self.m_L, self.m_R,self.m_B, self.m_T
        
        xdif = abs(xmax - xmin)
        ydif = abs(ymax - ymin)

        ycoordlist = []
        xcoordlist = []

        xcoordlist.append(xmin)
        ycoordlist.append(ymin)

        xpointdif = xdif / subX
        ypointdif = ydif / subY
        print(xpointdif)
        print(ypointdif)

        for position in range(1,subX):
            xcoordlist.append(xmin + xpointdif*position)
        
        for position in range(1,subY):
            ycoordlist.append(ymin + ypointdif*position)
        
        xcoordlist.append(xmax)
        ycoordlist.append(ymax)

        gridcoordlist = []
        for x in xcoordlist:    
            gridcoordline = []
            for y in ycoordlist:
                gridcoordline.append((x,y))
            gridcoordlist.append(gridcoordline)

        
        self.subx = subX
        self.suby = subY
        self.gridcoordlist = gridcoordlist
        self.gridbool = 1
        self.xpointdif = xpointdif
        self.ypointdif = ypointdif 

    def checkGridPointInsideDomainsAndPaint(self):
        self.patchpointlist = []
        patches = self.heview.getPatches()
        glColor3f(1.0, 0.53, 0.0)
        for patch in patches:
            for line in self.gridcoordlist:
                for point in line:
                    pt = Point()
                    pt.setX(point[0])
                    pt.setY(point[1])
                    if(patch.isPointInside(pt)):
                        glPointSize(4)
                        glBegin(GL_POINTS)
                        glVertex2f(point[0],point[1])
                        glEnd()
                        self.patchpointlist.append(point)

    def connect(self):
        self.connectlist = []
        neighborhood = []
        number_of_x = []
        lines = 0
        for point in self.patchpointlist:
            if self.patchpointlist[0][0] == point[0]:
                lines += 1
            if point[0] not in number_of_x:
                number_of_x.append(point[0])
        colums = len(number_of_x)
        self.lines = lines
        self.colums = colums
        for y in range(colums):
            for x in range(lines):
                neighborhood = []
                if y != 0:
                    neighborhood.append((y-1)*lines + x + 1)
                if y != colums-1:
                    neighborhood.append((y+1)*lines + x + 1)
                if x != 0:
                    neighborhood.append(y*lines + x)
                if x != lines-1:
                    neighborhood.append(y*lines + x + 2)
                neighborhood.insert(0, len(neighborhood))
                while len(neighborhood) < 5:
                    neighborhood.append(0)
                for neighboor in neighborhood:
                    self.connectlist.append(neighboor)
                neighborhood = []
        print(self.connectlist)
                
                        
    def gridBoolChange(self):
        if self.gridbool == 0:
            self.gridbool = 1
        else:
            self.gridbool = 0
    
    def pointChange(self):
        if self.pointsbool == 0:
            self.pointsbool = 1
        else:
            self.pointsbool = 0
    
    def gridDrawChange(self):
        if self.gridbooldraw == 0:
            self.gridbooldraw = 1
        else:
            self.gridbooldraw = 0