import sys, random, copy
import numpy as np
from PyQt5 import uic, QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QGraphicsScene, QGraphicsView, QApplication
from PyQt5.QtGui import QBrush

np.set_printoptions(threshold=sys.maxsize)

class Window(QtWidgets.QMainWindow):

    def __init__(self) :
        """Constructor method
        """
        super().__init__()
        QtWidgets.QMainWindow.__init__(self)
        uic.loadUi("multigrid.ui",self)
        self.table = np.zeros((60, 60))
        self.scene = QGraphicsScene()
        graphicView = QGraphicsView(self.scene, self.widget)
        graphicView.setGeometry(0,0,620,620)
        self.gridInit()
        self.butt_init.clicked.connect(self.gridInit)
        self.butt_rand.clicked.connect(self.randomize)
        self.butt_gol.clicked.connect(self.golRun)
        self.butt_path.clicked.connect(self.pathfind)
        self.widget.mousePressEvent = self.getPos


    def randomize(self) :
        """Randomizes the grid
        """
        self.gridInit()
        for w in range(1,59) :
            for v in range(1, 59) :
                self.table[w][v] = random.randint(0, 1)
        self.draw(self.table)


    def gridInit(self) :
        """Initializes to an empty grid
        """
        global pathstart, pathend, pathready, searching

        self.table = np.zeros((60, 60))
        self.label.setText("")
        pathstart, pathend, pathready, searching = False, False, False, False
        for column in range(60):
            for row in range(60):
                self.scene.addRect(row * 10, column * 10, 10, 10, brush = QBrush(Qt.black))


    def draw(self, table) :
        """Draw the scene

        Parameters
        ----------
        table : ndarray
            2D array representing the world
        """
        self.scene.clear()

        for w in range(60) :
            for v in range(60) :
                if table[w][v] == 0 or table[w][v] == 99 :
                    self.scene.addRect(w * 10, v * 10, 10, 10, brush = QBrush(Qt.black))
                if table[w][v] == 1 :
                    self.scene.addRect(w * 10, v * 10, 10, 10, brush = QBrush(Qt.white))
                if table[w][v] == 8  :
                    self.scene.addRect(w * 10, v * 10, 10, 10, brush = QBrush(Qt.red))
                if table[w][v] == 9 :
                    self.scene.addRect(w * 10, v * 10, 10, 10, brush = QBrush(Qt.blue))
    
    def golRun(self) :
        """Start or stop the game of life loop
        """
        global gol_state
        if gol_state == False :
            gol_state = True
            self.butt_gol.setText("Game of Life - Stop")
            self.golLoop()
        else :
            self.butt_gol.setText("Game of Life - Start")
            gol_state = False
            

    def golLoop(self) :
        """Game of life loop
        """
        global gol_state
        while gol_state == True :
            self.table = self.gen(self.table)
            self.draw(self.table)
            QApplication.processEvents()

    def gen(self, T) :
        """Calculate the next generation grid in the game of life

        Parameters
        ----------
        T : ndarray
            2D array representing the world

        Returns
        -------
        ndarray
            2D array representing the next generation
        """
        Tnext = []
        global Toriginal
        Tnext = copy.deepcopy(T)
        T = copy.deepcopy(Tnext)
        Toriginal = copy.deepcopy(T)
        for y in range(1, 59) :
            for x in range(1, 59) :
                srrnd = 0
                
                for k in range(-1, 2) :
                    for l in range (-1, 2) :
                        if k == 0 and l == 0 :
                            pass
                        else :
                            if T[y+k][x+l] == 1 :
                                srrnd+=1
                            
                if T[y][x] == 1 :
                    if 1 < srrnd < 4 :
                        Tnext[y][x] = 1
                    else :
                        Tnext[y][x] = 0
                if T[y][x] == 0 :
                    if srrnd == 3 :
                        Tnext[y][x] = 1
                    else :
                        Tnext[y][x] = 0

        return Tnext

    def getPos(self, event):
        """Get click position and modify matrix accordingly

        Parameters
        ----------
        event : mouse left click
            User left clicks on the scene
        """
        global pathstart, pathend, pathready, startx, starty, goalx, goaly

        x = int((event.pos().x() - 10) / 10)
        y = int((event.pos().y() - 10) / 10)
        a = self.table[x][y]

        if pathstart == False and pathend == False : 
            if a == 0 :
                b = 1
            if a == 1 :
                b = 0
        elif pathstart == True and pathend == False :
            b = 8
            startx, starty = x, y
            pathend = True
            self.label.setText("Select goal")
        else :
            b = 9
            goalx, goaly = x, y
            pathstart, pathend = False, False
            pathready = True
            self.label.setText("Ready")
        self.table[x][y] = b
        self.draw(self.table)

    def pathfind(self) :
        """Set start and goal of pathfinder or start the pathfinder loop
        """
        global pathstart, pathend, pathready
        if pathstart == False and pathend == False and pathready == False :
            pathstart = True
            self.label.setText("Select Start")
        elif pathready == True :
            self.label.setText("Searching...")
            self.pathfinderLoop()

        
    def pathfinderLoop(self) :
        """Pathfinder loop
        """
        global startx, starty, goalx, goaly, pathready, searching, distancex, distancey
        searching = True
        pos = np.array([startx, starty])
        path, history_local = [], []
        orientation = np.zeros((2))
        newpath = True

        while searching :
            QApplication.processEvents()
            if newpath : 
                if goalx - pos[0] != 0 :
                    distancex = (goalx - pos[0])
                    orientation[0] = (goalx - pos[0]) / abs(goalx - pos[0])
                else :
                    orientation[0] = 0
                if goaly - pos[1] != 0 :
                    distancey = (goaly - pos[1]) 
                    orientation[1] = (goaly - pos[1]) / abs(goaly - pos[1])
                else :
                    orientation[1] = 0

            newx = int(pos[0]+orientation[0])
            newy = int(pos[1]+orientation[1])
            local = self.table[int(pos[0]) - 1 : int(pos[0]) + 2, int(pos[1]) - 1 : int(pos[1]) + 2]
            


            

            if self.table[newx][newy] == 9 :
                path.append(pos)
                searching = False
                for i in path :
                    self.table[int(i[0])][int(i[1])] = 9
                path, history_local = [], []
                self.label.setText("Found !")

            elif 0 in local :
                if self.table[newx][newy] == 0 :
                    path.append(pos)
                    pos = pos + orientation
                    self.table[newx][newy] = 8
                    newpath = True
                    history_local.append(copy.deepcopy(local))

                elif self.table[newx][newy] != 0 and self.table[newx][newy] != 9 :
                    newpath = False

                    possibilities = [(-1, -1), (0, -1), (1, -1), (1, 0), (1, 1), (0, 1), (-1, 1), (-1, 0)]
                    val = possibilities.index((orientation[0], orientation[1]))
                    for i in range(1, len(possibilities)) :
                        newx = int(pos[0]+possibilities[(val + i)%len(possibilities)][0])
                        newy = int(pos[1]+possibilities[(val + i)%len(possibilities)][1])

                        if newx >= 59 : newx = 59 
                        if newy >= 59 : newy = 59 
                        
                        if self.table[newx][newy] == 0 :
                            orientation = np.array((possibilities[(val + i)%len(possibilities)][0], possibilities[(val + i)%len(possibilities)][1]))
                            break

                        elif self.table[int(pos[0]+possibilities[val - i][0])][int(pos[1]+possibilities[val - i][1])] == 0 :
                            orientation = np.array((possibilities[val - i][0], possibilities[val - i][1]))
                            break
            
            else :
                backing = True
                history_local.append(copy.deepcopy(local))
                path.append(pos)
                c = 0
                pos = np.array([startx, starty])
                while backing :
                    if c < len(path) :
                        v, w = int(path[-1-c][0]), int(path[-1-c][1])

                        self.table[v][w] = 99
                        if 0 in history_local[-1-c] or c == len(path) :
                            backing = False
                            pos = path[-1 - c]
                            for _ in range(c+1) :
                                path.pop()
                        else :     
                            c += 1
                    else :
                        backing = False
                        searching = False
                        self.label.setText("No path has been found :(")

             
                self.table[startx][starty] = 8

            self.draw(self.table)
        
        

if __name__ == "__main__":
    gol_state, pathstart, pathend, pathready, searching = False, False, False, False, False
    startx, starty, goalx, goaly, distancex, distancey = 0, 0, 0, 0, 0, 0
    Toriginal = []
    app = QtWidgets.QApplication(sys.argv)
    window = Window()
    window.show()
    sys.exit(app.exec_())