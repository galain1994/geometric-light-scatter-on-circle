#!/usr/bin/python3
# -*- coding: utf-8 -*-

import os
import sys
import csv
from collections import namedtuple
import matplotlib
matplotlib.use('Qt5Agg')
import matplotlib.pyplot as plt
from PyQt5 import QtCore, QtWidgets, QtGui
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotCanvas import ScatterCanvas
from intersectionElements import Light, Circle, Sphere
from intersectionDrawer import drawer
from pygameVector import Vec3d, Vec2d


class ApplicationWindow(QtWidgets.QMainWindow):

    def __init__(self):
        super(ApplicationWindow, self).__init__()

        self.data = {'start_point':[], 'vector':[]}

        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)   #  Make Qt delete this widget when widget accept close event
        self.setWindowTitle('球形粒子几何光学追迹')

        self.if_3d = False

        self.addMenu()

        self.main_widget = QtWidgets.QWidget(self)
        self.main_layout = QtWidgets.QHBoxLayout(self.main_widget)

        self.addDataArea(radius=10)

        self.statusBar()

        self.canvas = ScatterCanvas(self.main_widget, 20, 10)
        self.addCanvas(self.canvas)

        self.main_widget.setFocus()
        self.setCentralWidget(self.main_widget)

    def addDataArea(self, radius):
        if_3d = self.if_3d

        self.data_frame = QtWidgets.QFrame()
        self.data_layout = QtWidgets.QVBoxLayout()
        self.data_layout.setAlignment(QtCore.Qt.AlignLeft)
        self.data_frame.setLayout(self.data_layout)

        # show light information
        data_form = QtWidgets.QVBoxLayout()
        self.createTable()
        data_form.setSpacing(10)
        data_form.addWidget(self.tableWidget)
        self.data_form = data_form

        # line1.setTextInteractionFlags(QtCore.Qt.LinksAccessibleByMouse|QtCore.Qt.TextSelectableByMouse)

        qbox = QtWidgets.QGroupBox('Light')
        qbox.setLayout(data_form)
        qbox.setAlignment(QtCore.Qt.AlignCenter)
        qbox.setContentsMargins(-12, 12, -5, -5)

        scrollArea = QtWidgets.QScrollArea()
        scrollArea.setAlignment(QtCore.Qt.AlignLeft)
        scrollArea.setWidget(qbox)
        scrollArea.setWidgetResizable(True)
        scrollArea.setMinimumSize(scrollArea.sizeHint())

        qbox.updateGeometry()
        self.data_layout.addWidget(scrollArea)

        # coordinates
        input_form = QtWidgets.QFormLayout()
        input_form.setAlignment(QtCore.Qt.AlignLeft)
        coordinates = QtWidgets.QHBoxLayout()
        coordinates.setAlignment(QtCore.Qt.AlignLeft)
        input_form.addRow('Start Point:  ', coordinates)
        lx, ly, lz = QtWidgets.QLabel('x:   '), QtWidgets.QLabel('y:   '), QtWidgets.QLabel('z:')
        x, y, z = [QtWidgets.QDoubleSpinBox() for i in range(3)]
        self.co = (x, y, z) if if_3d else (x, y)
        for _co in self.co:
            _co.setSingleStep(0.1)
            _co.setMinimum(-radius)
            _co.setMaximum(radius)
        if not if_3d:
            x.setValue(1)
            x.setMaximum(-radius-1)
            x.setMinimum(-2*radius)
        else:
            y.setValue(1)
            y.setMaximum(-radius-1)
            y.setMinimum(-2*radius)
        label = (lx, ly, lz) if if_3d else (lx, ly)
        for _co, _label in zip(self.co, label):
            coordinates.addWidget(_label)
            coordinates.addWidget(_co)

        # direction
        direction_layout = QtWidgets.QHBoxLayout()
        direction_layout.setContentsMargins(-20, 0, 0, 0)
        direction_layout.setAlignment(QtCore.Qt.AlignLeft)
        input_form.addRow('Direction:  ', direction_layout)
        lvx, lvy, lvz = QtWidgets.QLabel('Vx: '), QtWidgets.QLabel('Vy: '), QtWidgets.QLabel('Vz:')
        vx, vy, vz = [QtWidgets.QDoubleSpinBox() for i in range(3)]
        if not if_3d:
            vx.setValue(1)
        else:
            vy.setValue(1)
        self.v = (vx, vy, vz) if if_3d else (vx, vy)
        lv = (lvx, lvy, lvz) if if_3d else (lvx, lvy)
        for _v in self.v:
            _v.setSingleStep(0.1)
            _v.setMinimum(-radius)
        for _v, _lv in zip(self.v, lv):
            direction_layout.addWidget(_lv)
            direction_layout.addWidget(_v)

        self.data_layout.addLayout(input_form)

        self.createModForm()
        self.data_layout.addLayout(self.mod_form)

        self.main_layout.addWidget(self.data_frame)

    def createTable(self):
        self.tableWidget = QtWidgets.QTableWidget()
        self.tableWidget.setRowCount(1)
        self.tableWidget.setColumnCount(2)
        self.tableWidget.setColumnWidth(0, 120)
        self.tableWidget.setColumnWidth(1, 120)        
        self.tableWidget.setItem(0, 0, QtWidgets.QTableWidgetItem('Start Point'))
        self.tableWidget.setItem(0, 1, QtWidgets.QTableWidgetItem('Direction'))

    def createModForm(self):
        self.mod_form = QtWidgets.QFormLayout()
        self.submit_button = QtWidgets.QPushButton('add')
        self.submit_button.pressed.connect(self.addData)
        self.mod_form.addRow(self.submit_button)
        self.mod_form.setContentsMargins(-50, 0, 0, 0)
        h = QtWidgets.QHBoxLayout()
        self.delete_line = QtWidgets.QSpinBox()
        self.delete_line.setMaximum(self.tableWidget.rowCount())
        self.delete_line.setMinimum(self.tableWidget.rowCount())
        self.delete_button = QtWidgets.QPushButton('delete')
        self.delete_button.pressed.connect(self.removeData)
        self.clear_button = QtWidgets.QPushButton('clear')
        self.clear_button.pressed.connect(self.clearData)
        h.addWidget(self.delete_line)
        h.addWidget(self.delete_button)
        h.addWidget(self.clear_button)
        self.mod_form.addRow('Line:', h)

    def addData(self):
        start_point = tuple(round(_co.value(), 5) for _co in self.co)
        vector = tuple(round(_v.value(), 5) for _v in self.v)
        for (p, v) in zip(self.data['start_point'], self.data['vector']):
            if start_point == p and vector == v:
                self.statusBar().showMessage('！ already have same data')
                return
        self.data['start_point'].append(start_point)
        self.data['vector'].append(vector)
        self.tableWidget.setRowCount(len(self.data['start_point'])+1)
        self.tableWidget.setItem(len(self.data['start_point']), 0, QtWidgets.QTableWidgetItem(str(start_point)))
        self.tableWidget.setItem(len(self.data['start_point']), 1, QtWidgets.QTableWidgetItem(str(vector)))
        self.delete_line.setMaximum(self.tableWidget.rowCount())
        self.delete_line.setMinimum(2)
        self.statusBar().clearMessage()

    def removeData(self):
        line = self.delete_line.value()
        if not self.data['start_point']:
            self.statusBar().showMessage('！ No data')
            return
        p = self.data['start_point'].pop(line-2)
        v = self.data['vector'].pop(line-2)
        self.tableWidget.removeRow(line-1)
        self.statusBar().showMessage('Line: {2}, point:{0} vector:{1} has been removed.'.format(p, v, line))
        mini_row = 2 if self.tableWidget.rowCount() > 2 else 1
        self.delete_line.setMinimum(mini_row)
        self.delete_line.setMaximum(self.tableWidget.rowCount())

    def clearData(self):
        self.data = {'start_point':[], 'vector':[]}
        row_count = self.tableWidget.rowCount()
        for i in range(row_count, 0, -1):
            self.tableWidget.removeRow(i)
        self.delete_line.setMaximum(self.tableWidget.rowCount())
        self.delete_line.setMinimum(self.tableWidget.rowCount())

    def addCanvas(self, canvas):
        # plotting area
        self.canvas_layout = QtWidgets.QVBoxLayout()

        self.comboBox = QtWidgets.QComboBox()
        self.comboBox.addItem("Single Points")
        self.comboBox.addItem("Continuous")
        self.comboBox.currentIndexChanged.connect(self.selectionChange)
        self.canvas_layout.addWidget(self.comboBox)

        self.light_attribute_form = QtWidgets.QHBoxLayout()

        lable_m, label_radius, label_waveLength, label_lightNum, label_times = QtWidgets.QLabel('m (refraction index):'), \
                    QtWidgets.QLabel('Radius (mm):'), QtWidgets.QLabel('Wave Length (nm):'), \
                    QtWidgets.QLabel('Light Nums:'), QtWidgets.QLabel('times:')
        labels = [lable_m, label_radius, label_waveLength, label_lightNum, label_times]
        self.box_m, self.box_radius, self.box_waveLength, self.box_lightNum, self.box_times = [QtWidgets.QDoubleSpinBox() for i in range(5)]
        boxes = [self.box_m, self.box_radius, self.box_waveLength, self.box_lightNum, self.box_times]
        self.box_m.setDecimals(4)
        self.box_m.setValue(1.335)
        self.box_radius.setDecimals(2)
        self.box_radius.setValue(10)
        self.box_waveLength.setDecimals(2)
        self.box_waveLength.setMaximum(1000)
        self.box_waveLength.setValue(532)
        self.box_lightNum.setDecimals(0)
        self.box_lightNum.setMaximum(2000)
        self.box_lightNum.setValue(1)
        self.box_times.setDecimals(0)
        self.box_times.setValue(3)
        for label, box in zip(labels, boxes):
            self.light_attribute_form.addWidget(label)
            self.light_attribute_form.addWidget(box)

        self.simulate_button = QtWidgets.QPushButton('Simulate')
        if not self.if_3d:
            self.simulate_button.pressed.connect(self.simulate_2d)
        else:
            self.simulate_button.pressed.connect(self.simulate_3d)

        self.canvas_layout.addLayout(self.light_attribute_form)
        self.canvas_layout.addWidget(self.simulate_button)

        self.fig_toolbar = NavigationToolbar(canvas, self.main_widget)
        self.canvas_layout.addWidget(canvas)
        self.canvas_layout.addStretch()
        self.canvas_layout.addWidget(self.fig_toolbar)

        self.main_layout.addLayout(self.canvas_layout)

    def selectionChange(self):
        if "Continuous" == self.comboBox.currentText():
            self.clearData()
            self.data_frame.setHidden(True)
            self.box_lightNum.setEnabled(True)
            self.box_lightNum.setMinimum(2)
        else:
            self.data_frame.setHidden(False)
            self.data_layout.setEnabled(True)
            self.box_lightNum.setEnabled(False)

    def addMenu(self):

        # add file menu
        self.file_menu = QtWidgets.QMenu('&File', self)
        self.file_menu.addAction('&New', self.fileNew, 
                                 QtCore.Qt.CTRL + QtCore.Qt.Key_N)
        self.file_menu.addAction('&Open', self.fileOpen,
                                 QtCore.Qt.CTRL + QtCore.Qt.Key_O)
        self.file_menu.addAction('Save Data', self.fileSave,
                                 QtCore.Qt.CTRL + QtCore.Qt.SHIFT + QtCore.Qt.Key_S)
        self.file_menu.addAction('&Save Image', self.imageSave,
                                 QtCore.Qt.CTRL + QtCore.Qt.Key_S)
        self.file_menu.addAction('&Quit', self.fileQuit, 
                                 QtCore.Qt.CTRL + QtCore.Qt.Key_Q)
        self.menuBar().addMenu(self.file_menu)

        # add view menu
        self.view_menu = QtWidgets.QMenu('&View', self)
        self.view_menu.addAction('&2D', self.shift_to_2d)
        self.view_menu.addAction('&3D', self.shift_to_3d)
        self.menuBar().addMenu(self.view_menu)

        self.menuBar().addSeparator()
        # add help documentation
        self.help_menu = QtWidgets.QMenu('&Help', self)
        self.help_menu.addAction('&Documentation', self.show_documentation)
        self.menuBar().addMenu(self.help_menu)

    def fileNew(self):
        # refresh the User Interface
        self.clearData()

    def fileOpen(self):
        # open exsiting data file
        self.data = {'start_point':[], 'vector':[]}
        files_types = "CSV data files (*.csv)"
        fileDialog = QtWidgets.QFileDialog()
        fileDialog.setAcceptMode(QtWidgets.QFileDialog.AcceptOpen)
        filename, fil = QtWidgets.QFileDialog.getOpenFileName(self, 'Open file', os.path.expanduser('~'), files_types)
        try:
            with open(filename, 'r') as f:
                f_csv = csv.reader(f)
                header = next(f_csv)
                Row = namedtuple('Row', header)
                for r in f_csv:
                    row = Row(*r)
                    self.data['start_point'].append(row.start_point)
                    self.data['vector'].append(row.vector)
        except FileNotFoundError:
            self.statusBar().showMessage('open operation abort.')
        except Exception as e:
            self.statusBar().showMessage('file {0} is not a correct format file.'.format(filename))
            print (e)
        else:
            self.tableWidget.setRowCount(len(self.data['start_point'])+1)
            i = 0
            for p, v in zip(self.data['start_point'], self.data['vector']):
                self.tableWidget.setItem(i+1, 0, QtWidgets.QTableWidgetItem(str(p)))
                self.tableWidget.setItem(i+1, 1, QtWidgets.QTableWidgetItem(str(v)))
                i += 1
            self.delete_line.setMaximum(self.tableWidget.rowCount())
            self.delete_line.setMinimum(1)

    def fileSave(self):
        # save data to file
        data = self.data
        header = ['start_point', 'vector']
        start_point = data['start_point']
        vector = data['vector']
        result = []
        for p, v in zip(start_point, vector):
            result.append(dict(start_point=p, vector=v))
        files_types = "CSV data files (*.csv)"
        fileDialog = QtWidgets.QFileDialog()
        fileDialog.setAcceptMode(QtWidgets.QFileDialog.AcceptSave)
        filename, fil = QtWidgets.QFileDialog.getSaveFileName(self, 'Save file', os.path.expanduser('~'), files_types)
        try:
            with open(filename, 'w') as f:
                f_csv = csv.DictWriter(f, header)
                f_csv.writeheader()
                f_csv.writerows(result)
        except FileNotFoundError:
            self.statusBar().showMessage('data not save.')

    def fileQuit(self):
        # quit app
        self.close()

    def imageSave(self):
        # save the simulation result
        image_types = "Image File (*.png *jpg)"
        fileDialog = QtWidgets.QFileDialog()
        fileDialog.setAcceptMode(QtWidgets.QFileDialog.AcceptSave)
        filename, fil = QtWidgets.QFileDialog.getSaveFileName(self, 'Save file', os.path.expanduser('~'), image_types)
        try:
            self.fig_toolbar.save_figure(filename)
        except Exception as e:
            print (e)
            self.statusBar().showMessage('Image not save Exception:%s' % e)

    def shift_to_2d(self):
        # change to the view of 2d scatter
        self.clearData()

    def shift_to_3d(self):
        # change to the view of 3d scatter
        self.if_3d = True

    def simulate_2d(self):
        # clear plot
        ax = self.canvas.axes
        ax.clear()
        self.canvas.draw()

        radius = float(self.box_radius.value())
        lightNum = int(self.box_lightNum.value())
        waveLength = float(self.box_waveLength.value())
        times = int(self.box_times.value())
        refraction_index = float(self.box_m.value())

        circle = Circle(radius)
        circle_patch = plt.Circle((0,0), radius, fill=False)

        if_continuous = True if 'Continuous' == self.comboBox.currentText() else False
        if not if_continuous:
            lights = []
            points_and_lines = []
            start_points = self.data['start_point']
            directions = self.data['vector']
            for p, v in zip(start_points, directions):
                # TODO: convert string to float
                v = (float(v[0]), float(v[1]))
                light = Light(waveLength, Vec2d(v).normalized(), 1, unit='nm')
                lights.append(light)
                points_and_lines.append(drawer(circle, light, refraction_index, intersection_time=times, start_point=p))
            x = []
            y = []
            lines = []
            for pl in points_and_lines:
                xy = pl['intersection_points']
                x.extend(xy[0])
                y.extend(xy[1])
                lines.append(pl['incident_lines'])
                lines.append(pl['refraction_lines'])
                lines.append(pl['reflection_lines'])
            lines = [ ll for line in lines for l in line for ll in l ]
        else:
            v = (1, 0)
            light = Light(waveLength, Vec2d(v).normalized(), 1, unit='nm')
            points_and_lines = drawer(circle, light, refraction_index, density=lightNum, intersection_time=times)
            xy = points_and_lines['intersection_points']
            x = xy[0]
            y = xy[1]
            lines = [line for l in (points_and_lines['incident_lines'], \
                                    points_and_lines['refraction_lines'], \
                                    points_and_lines['reflection_lines']) for ll in l for line in ll]

        ax.scatter(x, y)
        ax.add_patch(circle_patch)
        ax.axis('equal')
        boarder = radius+3
        ax.axis([-boarder, boarder, -boarder, boarder])
        for l in lines:
            ax.add_line(l)
        self.canvas.draw()

    def simulate_3d(self):
        
        pass

    def show_documentation(self):
        pass



app = QtWidgets.QApplication(sys.argv)

appWindow = ApplicationWindow()
appWindow.show()
sys.exit(app.exec_())

