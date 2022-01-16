from os import close
from PyQt5.QtWidgets import *
from mycanvas import *
from mymodel import *
from PyQt5.QtGui import *
import json


class MyWindow(QMainWindow):
    def __init__(self):
        super(MyWindow, self).__init__()
        self.setGeometry(100, 100, 600, 400)
        self.setWindowTitle("MyGLDrawer")
        self.canvas = MyCanvas()
        self.setCentralWidget(self.canvas)
        # create a model object and pass to canvas
        self.model = MyModel()
        self.canvas.setModel(self.model)
        # create a Toolbar
        tb = self.addToolBar("File")
        fit = QAction("fit", self)
        tb.addAction(fit)
        grid = QAction("grid", self)
        tb.addAction(grid)
        gridshow = QAction("s/h grid", self)
        tb.addAction(gridshow)
        gridpointshow = QAction("s/h gridpoints", self)
        tb.addAction(gridpointshow)
        showpoints = QAction("s/h points", self)
        tb.addAction(showpoints)
        export = QAction("export coords", self)
        tb.addAction(export)
        tb.actionTriggered[QAction].connect(self.tbpressed)

    def tbpressed(self, a):
        if a.text() == "fit":
            self.canvas.fitWorldToViewport()
        
        if a.text() == "s/h gridpoints":
            if len(self.canvas.patchpointlist)>0:
                self.canvas.gridBoolChange()
                self.canvas.update()
                self.canvas.paintGL()

        if a.text() == "s/h grid":
            if len(self.canvas.gridcoordlist)>0:
                self.canvas.gridDrawChange()
                self.canvas.update()
                self.canvas.paintGL()

        if a.text() == "s/h points":
            self.canvas.pointChange()
            self.canvas.update()
            self.canvas.paintGL()
        
        if a.text() == "export coords":
            if len(self.canvas.patchpointlist)>0:
                f = []
                restricoes = []
                for y in range(self.canvas.colums):
                    for x in range(self.canvas.lines):
                        if y == self.canvas.colums - 1:    
                                f.append(-1000.0)
                                f.append(0.0)
                        else:
                            for k in range(0,2):
                                f.append(0.0)
                        if y == 0:
                            for k in range(0,2):
                                restricoes.append(1)
                        else:
                            for k in range(0,2):
                                restricoes.append(0)
                coordfile = open("gridcoords.json", "w")
                json.dump({"coordinates":self.canvas.patchpointlist,"connect":self.canvas.connectlist,"raio":self.canvas.xpointdif/2,"f":f,"restricoes":restricoes},coordfile)
                coordfile.close()
            else: 
                ok = QMessageBox(self)
                ok.setText("no coords to export")
                ok.exec()
              


        if a.text() == "grid":
            x,okPressed1 = QInputDialog.getInt(self, "Numero de subdivisoes em X","Numero de subdivisoes em X:", 1, 1, 2147483647, 1)
            if(okPressed1):
                y,okPressed2 = QInputDialog.getInt(self, "Numero de subdivisoes em Y","Numero de subdivisoes em Y:", 1, 1, 2147483647, 1)
                if(okPressed2):
                    self.canvas.getGridInput(x,y)
                    self.canvas.update()
                    self.canvas.paintGL()
