import PIL, copy, time, threading
from PIL import Image, ImageDraw
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtWidgets import QLabel, QWidget, QPushButton, QLineEdit
from PyQt5.QtGui import QPixmap, QIcon, QFont
from PyQt5.QtCore import Qt


print('libraries imported')

WIDGET_WIDTH = 1000
WIDGET_HEIGHT = 700

NET_WIDTH = WIDGET_WIDTH
NET_HEIGHT = WIDGET_HEIGHT - 80

CELL_SIDE = 20


class Updater(QtCore.QThread):
    updateSignal = QtCore.pyqtSignal()

    def __init__(self, parent = None):
        QtCore.QThread.__init__(self)
        self.setParent(parent)
        self.parent = parent

    def run(self):
        while True:
            self.updateSignal.emit()
            self.msleep(100)
            

class Cell(QLabel):
    def __init__(self, parent=None):
        QWidget.__init__(self)
        self.setParent(parent)
        self.parent = parent
        self.resize(CELL_SIDE, CELL_SIDE)
        self.setStyleSheet('background-color:rgb(255,255,255)')
        self.tcounter = 0
        self.isAlive = False
        self.aliveNextStep = False
        
    def mousePressEvent(self, e):
        self.tcounter += 1
        if self.tcounter % 2 == 1:
            self.setStyleSheet('background-color:rgb(205,255,0)')
            self.setAlive()
        else:
            self.setStyleSheet('background-color:rgb(255,255,255)')
            self.setDead()

    def setAlive(self):
        if not self.isAlive:
            self.setStyleSheet('background-color:rgb(205,255,0)')
            self.isAlive = True
            self.parent.alivecounter += 1

    def setDead(self):
        if self.isAlive:
            self.setStyleSheet('background-color:rgb(255,255,255)')
            self.isAlive = False
            self.parent.alivecounter -= 1


class Net(QLabel):
    def __init__(self, parent=None):
        QWidget.__init__(self)
        self.setParent(parent)

        self.netbg = Image.new('RGB', (NET_WIDTH, NET_HEIGHT), (255, 255, 255))

        self.draw = ImageDraw.Draw(self.netbg)
        
        # for xx in range(-1, NET_WIDTH, 30):
        #     self.draw.line([xx, 0, xx, NET_HEIGHT], fill=(200, 200, 200), width=1)
        #
        # for yy in range(-1, NET_HEIGHT, 30):
        #     self.draw.line([0, yy, NET_WIDTH, yy], fill=(200, 200, 200), width=1)

        self.netbg.save('net.jpeg')
        self.resize(*self.netbg.size)
        print('Net size:', self.netbg.size)
        self.setPixmap(QPixmap('net.jpeg'))


class Main(QWidget):
    def __init__(self):
        QWidget.__init__(self)
        
        self.setWindowTitle('Conway\'s Game of Life')
        self.setWindowIcon(QIcon('icon.png'))
        self.setStyleSheet('background-color:rgb(250,250,250);')
        self.setFixedSize(WIDGET_WIDTH, WIDGET_HEIGHT)

        self.net = Net(self)
        self.net.move(0, 0)
        print(self.net.geometry())
        self.net.show()

        self.tcounter = 0
        self.generation = 0
        self.oldcells = []

        self.alivecounter = 0
        
        self.startbtn = QPushButton('Start', self)
        self.startbtn.move(385, self.net.size().height() + 7)
        self.startbtn.resize(300, 40)
        self.startbtn.setStyleSheet('background-color:rgb(220,220,220)')

        self.clearbtn = QPushButton('Clear', self)
        self.clearbtn.move(690, self.net.size().height() + 7)
        self.clearbtn.resize(300, 40)
        self.clearbtn.setStyleSheet('background-color:rgb(220,220,220)')

        self.warplbl = QLabel('Warp rate:', self)
        self.warplbl.setFont(QtGui.QFont('Default', 13))
        self.warplbl.setStyleSheet('color:rgb(0,0,0)')
        self.warplbl.move(250, NET_HEIGHT + 20)
        # self.warplbl.resize(self.warplbl.size().width() + 50, self.size().height() - self.net.size().height() - 2)
        self.warplbl.setAlignment(QtCore.Qt.AlignCenter)

        self.warpline = QLineEdit(self)
        self.warpline.move(330, NET_HEIGHT + 8)
        self.warpline.resize(30, 40)
        self.warpline.setFont(QtGui.QFont('Default', 12))
        self.warpline.setText('1.0')
        self.warpline.setAlignment(QtCore.Qt.AlignHCenter)

        self.poplbl = QLabel('Population: 0000', self)
        self.poplbl.setFont(QFont('Default', 13))
        self.poplbl.move(30, NET_HEIGHT + 20)

        self.genlbl = QLabel('Generation: 0000', self)
        self.genlbl.setFont(QFont('Default', 13))
        self.genlbl.move(140, NET_HEIGHT + 20)

        self.startbtn.clicked.connect(self.startTimer)
        self.clearbtn.clicked.connect(self.clear)

        self.initCells()
        print(self.alivecounter)

        self.launch_timer = QtCore.QTimer()
        self.launch_timer.setInterval(45)
        self.launch_timer.timeout.connect(self.step)

    def clear(self):
        if self.launch_timer.isActive():
            self.startbtn.click()
        for cellrow in self.cells:
            for cell in cellrow:
                if cell.isAlive:
                    cell.setDead()
                    cell.repaint()

        self.poplbl.setText('Population: 0')
        self.genlbl.setText('Generation: 0')
        self.generation = 0
            
    def startTimer(self):
        self.tcounter += 1
        if self.tcounter % 2 == 1:
            if self.alivecounter:
                self.genlbl.setText('Generation: ' + str(self.generation))
            else:
                self.genlbl.setText('Generation: 0')
                self.generation = 0
            try:
                interval = round(45*(1/float(self.warpline.text())))
                if interval == 0:
                    interval += 1
                self.launch_timer.setInterval(interval)
            except ValueError:
                self.warpline.setText('1.0')
                self.launch_timer.setInterval(45)
            self.launch_timer.start()
            self.startbtn.setText('Stop')
        else:
            self.launch_timer.stop()
            self.startbtn.setText('Start')

    def initCells(self):
        self.cells = []
        pos_x = 0
        pos_y = 0
        
        for x in range(1-5*CELL_SIDE, NET_WIDTH+5*CELL_SIDE, CELL_SIDE+1):
            self.cells.append([])
            for y in range(1-5*CELL_SIDE, NET_HEIGHT+5*CELL_SIDE, CELL_SIDE+1):
                self.cells[-1].append(0)
                self.cells[-1][-1] = Cell(self)
                self.cells[-1][-1].move(x, y)
                if any([x < 1, x > NET_WIDTH, y < 1, y > NET_HEIGHT-CELL_SIDE]):
                    self.cells[-1][-1].hide()

    def step(self):
                self.generation += 1
                if self.alivecounter > 0:
                    xxindex = 1
                    for xx in self.cells[1:-1]:
                        yyindex = 1
                        for yy in xx[1:-1]:
                            alive_nbs = 0
                            for x in range(xxindex - 1, xxindex + 2):
                                for y in range(yyindex - 1, yyindex + 2):
                                    if self.cells[x][y].isAlive:
                                        if x != xxindex or y != yyindex:
                                            alive_nbs += 1
                            cell = self.cells[xxindex][yyindex]
                            if alive_nbs == 3:
                                cell.aliveNextStep = True
                            elif alive_nbs == 2:
                                if cell.isAlive:
                                    cell.aliveNextStep = True
                                else:
                                    cell.aliveNextStep = False
                            else:
                                cell.aliveNextStep = False
                            yyindex += 1
                        xxindex += 1
                    for xc in self.cells:
                        for yc in xc:
                            if yc.aliveNextStep:
                                if not yc.isAlive:
                                    yc.setAlive()
                                    yc.repaint()
                            else:
                                if yc.isAlive:
                                    yc.setDead()
                                    yc.repaint()

                else:
                    self.startbtn.click()

                self.poplbl.setText('Population: ' + str(self.alivecounter))
                self.genlbl.setText('Generation: ' + str(self.generation))


if __name__ == '__main__':
    import sys
    app = QtWidgets.QApplication(sys.argv)
    ex = Main()
    ex.show()
    sys.exit(app.exec_())
