# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'window.ui'
#
# Created by: PyQt5 UI code generator 5.15.2
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.
import random

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import pyqtSignal
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg, NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
import HLC.controller
import environment
import logging
import time
from random import randint

LOG_FORMAT = '%(levelname)-10s %(name)-20s %(funcName)-20s  %(message)s'
logging.basicConfig(level=logging.DEBUG, format=LOG_FORMAT)
LOG = logging.getLogger(__name__)

LOGGER_DISABLED = False
LOG.disabled = LOGGER_DISABLED

PLOT_FIGURE = True
PRINT_CONSOLE_GRID = True

AUTO_GENERATE = True
STEP_BY_STEP = False
# SIMULATION_TIME = 0.1  # sec per step
SIMULATION_TIME = 'MAX'
ROBOTS_NUM = 7
PUCKS_NUM = 30


# test

class MplCanvas(FigureCanvasQTAgg):
    new_puck_in_container = pyqtSignal(int)
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        
        self.animation_running = False
        self.Map = environment.Map(size=[10, 8])  # for debug with AUTO_GENERATE = False !
        super(MplCanvas, self).__init__(self.Map.gridWorldFig)
        self.Controller = HLC.controller.Controller(gridSize=self.Map.retGridSize())

        if AUTO_GENERATE:
            for id in range(ROBOTS_NUM):
                self.Controller.addRobot(robotId=id)
                # time.sleep(0.1)

            for id in range(PUCKS_NUM):
                while True:
                    rand_pos = [randint(0, self.Map.retGridSize()[0] - 3), randint(1, self.Map.retGridSize()[1]) - 1]
                    if not self.Controller.checkIfPuckIsOnPosition(rand_pos) and rand_pos != self.Map.retContainerPos():
                        break
                self.Controller.addPuck(puckId=id, init_pos=rand_pos)
                # time.sleep(0.1)
        else:
            for i in range(7):
                self.Controller.addRobot(robotId=i)

            self.Controller.addPuck(puckId=0, init_pos=[3, 3])
            self.Controller.addPuck(puckId=1, init_pos=[0, 7])
            self.Controller.addPuck(puckId=2, init_pos=[6, 2])
            self.Controller.addPuck(puckId=3, init_pos=[6, 1])
            self.Controller.addPuck(puckId=4, init_pos=[7, 1])
            self.Controller.addPuck(puckId=5, init_pos=[3, 5])
            self.Controller.addPuck(puckId=6, init_pos=[4, 6])
            self.Controller.addPuck(puckId=7, init_pos=[6, 7])
            self.Controller.addPuck(puckId=8, init_pos=[6, 4])
            self.Controller.addPuck(puckId=9, init_pos=[1, 7])
            self.Controller.addPuck(puckId=10, init_pos=[1, 6])
            self.Controller.addPuck(puckId=11, init_pos=[0, 2])
            self.Controller.addPuck(puckId=12, init_pos=[7, 2])
            self.Controller.addPuck(puckId=13, init_pos=[5, 2])
            self.Controller.addPuck(puckId=14, init_pos=[5, 1])
            self.Controller.addPuck(puckId=15, init_pos=[6, 0])
            self.Controller.addPuck(puckId=16, init_pos=[1, 0])
            self.Controller.addPuck(puckId=17, init_pos=[1, 3])
            self.Controller.addPuck(puckId=18, init_pos=[4, 0])
            self.Controller.addPuck(puckId=19, init_pos=[7, 5])
            self.Controller.addPuck(puckId=20, init_pos=[1, 1])
            self.Controller.addPuck(puckId=21, init_pos=[4, 4])
            self.Controller.addPuck(puckId=22, init_pos=[2, 2])
            self.Controller.addPuck(puckId=23, init_pos=[0, 3])
            self.Controller.addPuck(puckId=24, init_pos=[5, 7])
            self.Controller.addPuck(puckId=25, init_pos=[1, 5])
            self.Controller.addPuck(puckId=26, init_pos=[3, 1])
            self.Controller.addPuck(puckId=27, init_pos=[3, 2])
            self.Controller.addPuck(puckId=28, init_pos=[4, 2])
            self.Controller.addPuck(puckId=29, init_pos=[0, 6])

            if PRINT_CONSOLE_GRID:
                print("... Initial map ...")
                self.Map.updateGrid(
                    robots=self.Controller.retRobots(),
                    pucks=self.Controller.retPucks(),
                    container=self.Controller.retContainerContent())
                self.Map.showGrid()

            if PLOT_FIGURE:
                self.Map.createGridWorldWindow()
                self.Map.updategridWorld(
                    robots=self.Controller.retRobots(),
                    pucks=self.Controller.retPucks(),
                    container=self.Controller.retContainerContent())

    def run_animation(self):
        while True:
            self.new_puck_in_container.emit(len(self.Controller.containerContent))
            if self.animation_running == False:
                break
            else:
                idling_pucks, idling_pucks_ids = self.Controller.checkIdlingPucks()
                if idling_pucks is True:
                    LOG.info("Idling Pucks ids:" + str(idling_pucks_ids))
                else:
                    LOG.info("NO Ideling Pucks")

                idling_robots, idling_robots_ids = self.Controller.checkIdlingRobots()
                if idling_robots is True:
                    LOG.info("Idling Robots ids: " + str(idling_robots_ids))
                else:
                    LOG.info("No idling robots")

                '''
                    przypisywanie
                    '''
                # jeśli istnieją czekające pucki i istnieją wolne roboty
                if (idling_pucks is True) and (idling_robots is True):
                    for puck_id in idling_pucks_ids:  # dla kazdego pucka
                        if idling_robots is True:  # jesli nadal istnieje czekajacy robot
                            robot_id, distance = self.Controller.DetermineNearestRobot(robots_ids=idling_robots_ids,
                                                                                       puck_id=puck_id)  # znajdz najblizszego robota
                            self.Controller.assignRobotToPuck(robot_id=robot_id, puck_id=puck_id)
                            '''
                                wyznaczanie sciezki robot-puck
                                '''
                            path = self.Controller.generateRobotMissionPath(robot_id=robot_id, puck_id=puck_id,
                                                                            container_pos=self.Map.retContainerPos())
                            self.Controller.setRobotMission(robot_id=robot_id, puck_id=puck_id, path=path)

                            idling_robots, idling_robots_ids = self.Controller.checkIdlingRobots()
                            LOG.info("Left Idling Robots: " + str(idling_robots_ids))

                '''
                    wykonywanie kroku
                    '''
                self.Controller.updateAllocationMatrix()
                if PRINT_CONSOLE_GRID:
                    self.Controller.showAllocationMatrix()

                if STEP_BY_STEP:
                    inp = input("Press to do step...")
                elif SIMULATION_TIME != 'MAX':
                    time.sleep(SIMULATION_TIME)

                self.Controller.executeOneStep()
                print("PUCKS NUMBER:     " + str(len(self.Controller.pucks)))
                if PRINT_CONSOLE_GRID:
                    self.Map.updateGrid(
                        robots=self.Controller.retRobots(),
                        pucks=self.Controller.retPucks(),
                        container=self.Controller.retContainerContent())
                    self.Map.showGrid()

                if PLOT_FIGURE:
                    self.Map.updategridWorld(
                        robots=self.Controller.retRobots(),
                        pucks=self.Controller.retPucks(),
                        container=self.Controller.retContainerContent())
                if PRINT_CONSOLE_GRID:
                    print("-" * 50)


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1405, 950)
        self.animation_started = False
        self.sc = MplCanvas()

        ############### FROM DESIGNER #################
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(self.centralwidget)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.leftLayout = QtWidgets.QVBoxLayout()
        self.leftLayout.setObjectName("leftLayout")
        self.widget = QtWidgets.QWidget(self.centralwidget)
        self.widget.setObjectName("widget")
        self.leftLayout.addWidget(self.widget)
        self.horizontalLayout.addLayout(self.leftLayout)
        self.RightLayout = QtWidgets.QVBoxLayout()
        self.RightLayout.setObjectName("RightLayout")
        self.exitButton = QtWidgets.QPushButton(self.centralwidget)
        self.exitButton.setObjectName("exitButton")
        self.RightLayout.addWidget(self.exitButton)
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.robotsNumberLabel = QtWidgets.QLabel(self.centralwidget)
        font = QtGui.QFont()
        font.setFamily("Microsoft YaHei")
        font.setPointSize(14)
        font.setBold(True)
        font.setWeight(75)
        self.robotsNumberLabel.setFont(font)
        self.robotsNumberLabel.setObjectName("robotsNumberLabel")
        self.horizontalLayout_4.addWidget(self.robotsNumberLabel)
        self.pucksNumberLabel = QtWidgets.QLabel(self.centralwidget)
        font = QtGui.QFont()
        font.setFamily("Microsoft YaHei")
        font.setPointSize(14)
        font.setBold(True)
        font.setWeight(75)
        self.pucksNumberLabel.setFont(font)
        self.pucksNumberLabel.setObjectName("pucksNumberLabel")
        self.horizontalLayout_4.addWidget(self.pucksNumberLabel)
        self.RightLayout.addLayout(self.horizontalLayout_4)
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.robotsNumber = QtWidgets.QLCDNumber(self.centralwidget)
        self.robotsNumber.setObjectName("robotsNumber")
        self.horizontalLayout_3.addWidget(self.robotsNumber)
        self.pucksNumber = QtWidgets.QLCDNumber(self.centralwidget)
        self.pucksNumber.setProperty("value", 10.0)
        self.pucksNumber.setObjectName("pucksNumber")
        self.horizontalLayout_3.addWidget(self.pucksNumber)
        self.RightLayout.addLayout(self.horizontalLayout_3)
        self.addPuckButton = QtWidgets.QPushButton(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.addPuckButton.sizePolicy().hasHeightForWidth())
        self.addPuckButton.setSizePolicy(sizePolicy)
        self.addPuckButton.setObjectName("addPuckButton")
        self.RightLayout.addWidget(self.addPuckButton)
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Preferred)
        self.RightLayout.addItem(spacerItem)
        self.startButton = QtWidgets.QPushButton(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.startButton.sizePolicy().hasHeightForWidth())
        self.startButton.setSizePolicy(sizePolicy)
        self.startButton.setObjectName("startButton")
        self.RightLayout.addWidget(self.startButton)
        spacerItem1 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Preferred)
        self.RightLayout.addItem(spacerItem1)
        self.progressBar = QtWidgets.QProgressBar(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.progressBar.sizePolicy().hasHeightForWidth())
        self.progressBar.setSizePolicy(sizePolicy)
        self.progressBar.setProperty("value", 0)
        self.progressBar.setObjectName("progressBar")
        self.progressBar.setStyleSheet("#BlueProgressBar {\n"
                                       "    border: 2px solid #2196F3;\n"
                                       "    border-radius: 5px;\n"
                                       "    background-color: #E0E0E0;\n"
                                       "    color:blue;\n"                                       
                                       "}")
        self.RightLayout.addWidget(self.progressBar)
        self.horizontalLayout.addLayout(self.RightLayout)
        self.horizontalLayout_2.addLayout(self.horizontalLayout)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 815, 21))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        ########## END ##########

        self.startButton.setStyleSheet("background-color: green")
        self.leftLayout.addWidget(self.sc)
        self.startButton.clicked.connect(self.start_clicked)
        self.exitButton.clicked.connect(lambda: self.close())
        self.addPuckButton.clicked.connect(self.add_puck)
        self.sc.new_puck_in_container.connect(self.update_progress)
        self.pucksNumber.setProperty("value",len(self.sc.Controller.pucks))
        self.robotsNumber.setProperty("value",ROBOTS_NUM)
        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.exitButton.setText(_translate("MainWindow", "exit app"))
        self.robotsNumberLabel.setText(_translate("MainWindow", "Number of robots:"))
        self.pucksNumberLabel.setText(_translate("MainWindow", "Number of pucks:"))
        self.addPuckButton.setText(_translate("MainWindow", "Add random puck"))
        self.startButton.setText(_translate("MainWindow", "start/stop"))
    def update_progress(self,number_of_pucks):
        self.progressBar.setValue(number_of_pucks)
    def add_puck(self):
        while True:
            print("searching")
            y_pos = random.randint(3, 8)
            x_pos = random.randint(0, 7)
            print("y: "+ str(y_pos) + " x: "+ str(x_pos))
            if not self.sc.Controller.checkIfPuckIsOnPosition([y_pos, x_pos]):
                self.sc.Controller.addPuck(len(self.sc.Controller.pucks), init_pos=[y_pos, x_pos])
                print("found free space")
                break
        self.pucksNumber.setProperty("value", len(self.sc.Controller.pucks))

    def start_clicked(self):
        _translate = QtCore.QCoreApplication.translate
        if self.sc.animation_running == False:
            self.startButton.setText(_translate("MainWindow", "stop"))
            self.startButton.setStyleSheet("background-color: red")
            self.sc.animation_running = True
        else:
            self.startButton.setText(_translate("MainWindow", "start"))
            self.startButton.setStyleSheet("background-color: green")
            self.sc.animation_running = False
        self.sc.run_animation()
        self.startButton.repaint()


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
