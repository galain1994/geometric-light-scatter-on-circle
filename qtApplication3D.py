#!/usr/bin/python3
# -*- coding: utf-8 -*-

import os
import sys
import csv
import math
import webbrowser
from collections import namedtuple
import matplotlib
matplotlib.use('Qt5Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from PyQt5 import QtCore, QtWidgets, QtGui
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotCanvas import ScatterCanvas, MplPlot3dCanvas
from intersectionElements import Sphere, Light
from pygameVector import Vec3d
from drawer3d import drawer, multi_line_drawer, generate_multi_start_points, draw_sphere_at_axes
from funcs3d import calculate_elevation_angle


class MyNavigationToolbar(NavigationToolbar):

    # 去掉不需要的工具栏项目 有可能造成软件崩溃的设置
    toolitems =tuple(i for i in NavigationToolbar.toolitems
                            if i[0] not in ('Subplots', ))


class ApplicationWindow(QtWidgets.QMainWindow):

    def __init__(self):
        super(ApplicationWindow, self).__init__()

        self.data = {'start_point':[], 'vector':[]}

        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)   #  Make Qt delete this widget when widget accept close event
        app_icon = QtGui.QIcon()
        app_icon.addFile('./icon.png', QtCore.QSize(124, 124))
        app.setWindowIcon(app_icon)
        self.setWindowTitle('3D球粒子几何光学追迹')

        self.elevation_angle = None # 抬升角数据
        self.azimuth = None   # 方位角数据
        self.addMenu()

        self.main_widget = QtWidgets.QWidget(self)
        self.main_layout = QtWidgets.QHBoxLayout(self.main_widget)

        self.addDataArea()

        self.statusBar()

        self.canvas_3d = MplPlot3dCanvas(self.main_widget, 8, 8)
        self.addCanvas(self.canvas_3d)
        self.canvas_3d.axes.mouse_init()            # 初始化鼠标的操作

        self.addOutputArea()
        self.output_frame.setHidden(True)

        self.main_widget.setFocus()
        self.setCentralWidget(self.main_widget)

    def addDataArea(self):

        self.data_frame = QtWidgets.QFrame()
        self.data_frame.setMaximumWidth(500)
        self.data_layout = QtWidgets.QVBoxLayout()
        self.data_layout.setAlignment(QtCore.Qt.AlignLeft)
        self.data_frame.setLayout(self.data_layout)

        # show light information
        data_form = QtWidgets.QVBoxLayout()
        self.createTable()
        data_form.setSpacing(10)
        data_form.addWidget(self.tableWidget)
        self.data_form = data_form

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

        # coordinates 初始化坐标设置
        input_form = QtWidgets.QFormLayout()
        input_form.setAlignment(QtCore.Qt.AlignLeft)
        coordinates = QtWidgets.QHBoxLayout()
        coordinates.setAlignment(QtCore.Qt.AlignLeft)
        input_form.addRow('Start Point:(um)', coordinates)
        lx, ly, lz = QtWidgets.QLabel('x:   '), QtWidgets.QLabel('y:   '), QtWidgets.QLabel('z:')
        self.start_x, y, self.start_z = [QtWidgets.QSpinBox() for i in range(3)]
        self.co = (self.start_x, y, self.start_z)
        label = (lx, ly, lz)
        for _co, _label in zip(self.co, label):
            _co.setRange(-999, 999)
            coordinates.addWidget(_label)
            coordinates.addWidget(_co)
        y.setRange(-2000, -1000)
        y.setValue(-1500)
        y.setEnabled(False)

        # direction 初始化向量设置
        direction_layout = QtWidgets.QHBoxLayout()
        direction_layout.setContentsMargins(-20, 0, 0, 0)
        direction_layout.setAlignment(QtCore.Qt.AlignLeft)
        input_form.addRow('Direction:  ', direction_layout)
        lvx, lvy, lvz = QtWidgets.QLabel('Vx: '), QtWidgets.QLabel('Vy: '), QtWidgets.QLabel('Vz:')
        vx, vy, vz = [QtWidgets.QDoubleSpinBox() for i in range(3)]
        vy.setValue(1)
        self.v = (vx, vy, vz)
        lv = (lvx, lvy, lvz)
        for _v, _lv in zip(self.v, lv):
            direction_layout.addWidget(_lv)
            direction_layout.addWidget(_v)
            _v.setEnabled(False)

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
        start_point = tuple(round(_co.value()/1000, 5) for _co in self.co)
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
        self.canvas_frame = QtWidgets.QFrame()
        # self.canvas_frame.setMaximumWidth(800)
        self.canvas_layout = QtWidgets.QVBoxLayout()
        self.canvas_frame.setLayout(self.canvas_layout)

        self.comboBox = QtWidgets.QComboBox()
        self.comboBox.addItem("Single Points")
        self.comboBox.addItem("Continuous")
        self.comboBox.currentIndexChanged.connect(self.selectionChange)
        self.canvas_layout.addWidget(self.comboBox)

        self.light_attribute_form = QtWidgets.QGridLayout()

        lable_m, label_radius, label_waveLength, label_lightNum, label_times = QtWidgets.QLabel('m (refraction index):'), \
                    QtWidgets.QLabel('Radius (um):'), QtWidgets.QLabel('Wave Length (nm):'), \
                    QtWidgets.QLabel('Light Nums:'), QtWidgets.QLabel('times:')
        self.box_m, self.box_radius, self.box_waveLength, self.box_lightNum, self.box_times = [QtWidgets.QDoubleSpinBox() for i in range(5)]
        labels = [[label_radius], [lable_m, label_waveLength], [label_lightNum, label_times]]
        boxes = [[self.box_radius], [self.box_m, self.box_waveLength], [self.box_lightNum, self.box_times]]

        self.box_m.setDecimals(4)
        self.box_m.setValue(1.335)
        self.box_radius.setDecimals(2)
        self.box_radius.setRange(0, 10000)
        self.box_radius.setValue(1000)
        self.box_radius.valueChanged.connect(self.change_radius)
        self.box_waveLength.setDecimals(2)
        self.box_waveLength.setMaximum(1000)
        self.box_waveLength.setValue(532)
        self.box_lightNum.setDecimals(0)
        self.box_lightNum.setMaximum(2000)
        self.box_lightNum.setValue(3)
        self.box_lightNum.setEnabled(False)
        self.box_times.setDecimals(0)
        self.box_times.setValue(3)
        self.box_times.setMaximum(20)

        for row, widgets in enumerate(zip(labels, boxes)):
            for column, (label, box) in enumerate(zip(*widgets)):
                self.light_attribute_form.addWidget(label, row, column*2)
                self.light_attribute_form.addWidget(box, row, column*2+1)

        self.set_coordinate_frame = QtWidgets.QFrame()
        self.set_coordinate_form = QtWidgets.QHBoxLayout()
        self.set_coordinate_frame.setLayout(self.set_coordinate_form)
        self.check_x, self.check_y, self.check_z = QtWidgets.QCheckBox('set x'),\
                                                   QtWidgets.QCheckBox('set y'),\
                                                   QtWidgets.QCheckBox('set z')
        self.check_y.setChecked(True)
        self.check_y.setEnabled(False)
        self.check_y.setMaximumWidth(50)
        self.co_checkbox = [self.check_x, self.check_z]
        for _check in self.co_checkbox:
            _check.setEnabled(False)
            _check.setMaximumWidth(50)
            _check.setChecked(False)
            _check.stateChanged.connect(self.checkbox_changed)
        self.set_x, self.set_y, self.set_z = [QtWidgets.QSpinBox() for i in range (3)]
        self.set_y.setRange(-10000, 10000)
        self.set_y.setEnabled(False)
        self.set_y.setValue(-1500)
        self.co_settings = [self.set_x, self.set_z]
        for _set in self.co_settings:
            _set.setRange(-998, 998)
            _set.setEnabled(False)

        self.set_coordinate_form.addWidget(self.check_y)
        self.set_coordinate_form.addWidget(self.set_y)
        for _check, _set in zip(self.co_checkbox, self.co_settings):
            self.set_coordinate_form.addWidget(_check)
            self.set_coordinate_form.addWidget(_set)
        self.canvas_layout.addWidget(self.set_coordinate_frame)


        self.simulate_button = QtWidgets.QPushButton('Simulate')
        self.simulate_button.pressed.connect(self.simulate_3d)

        self.canvas_layout.addLayout(self.light_attribute_form)
        self.canvas_layout.addWidget(self.simulate_button)

        self.fig_toolbar = MyNavigationToolbar(canvas, self.main_widget)
        self.canvas_layout.addWidget(canvas)
        self.canvas_layout.addWidget(self.fig_toolbar)
        self.fig_toolbar.hide()

        self.copyright_frame = QtWidgets.QFrame()
        self.copyright_layout = QtWidgets.QHBoxLayout()
        self.copyright_layout.setAlignment(QtCore.Qt.AlignRight)
        _empty_label = QtWidgets.QLabel()
        self.copyright_label = QtWidgets.QLabel('西电韩香娥团队所有 \u00a9 Coder:陈嘉琅')
        self.copyright_label.setFont(QtGui.QFont('Times', 12))
        self.copyright_layout.addWidget(_empty_label)
        self.copyright_layout.addWidget(self.copyright_label)
        self.copyright_frame.setLayout(self.copyright_layout)
        self.canvas_layout.addWidget(self.copyright_frame)

        self.main_layout.addWidget(self.canvas_frame)

    def checkbox_changed(self):
        """复选框改变时的动作
        """
        radius = self.box_radius.value()
        self.set_y.setValue(-1.5*radius)
        for _check, _set in zip(self.co_checkbox, self.co_settings):
            if _check.isChecked():
                _set.setEnabled(True)
                _set.setRange(-radius+1, radius-1)
            else:
                _set.setEnabled(False)

    def selectionChange(self):
        """选择不同入射光线的选项改变时
        """
        ax = self.canvas_3d.axes
        ax.clear()
        self.canvas_3d.draw()
        if "Continuous" == self.comboBox.currentText():
            self.data_frame.setHidden(True)
            self.data_layout.setEnabled(False)
            self.box_lightNum.setEnabled(True)
            self.box_lightNum.setMinimum(3)
            self.output_frame.setHidden(False)
            for _check in self.co_checkbox:
                _check.setEnabled(True)
        else:
            for _check in self.co_checkbox:
                _check.setEnabled(False)
            self.data_frame.setHidden(False)
            self.data_layout.setEnabled(True)
            self.box_lightNum.setEnabled(False)
            self.output_frame.setHidden(True)

    def addMenu(self):
        # add file menu 增加菜单栏
        self.file_menu = QtWidgets.QMenu('&File', self)
        self.file_menu.addAction('&New', self.fileNew, 
                                 QtCore.Qt.CTRL + QtCore.Qt.Key_N)
        self.file_menu.addAction('Save Elevation Angle', self.save_elevation_angle)
        self.file_menu.addAction('Save Azimuth', self.save_azimuth)
        self.file_menu.addAction('&Save Image', self.imageSave,
                                 QtCore.Qt.CTRL + QtCore.Qt.Key_S)
        self.file_menu.addAction('&Quit', self.fileQuit, 
                                 QtCore.Qt.CTRL + QtCore.Qt.Key_Q)
        self.menuBar().addMenu(self.file_menu)

        self.menuBar().addSeparator()
        # add help documentation
        self.help_menu = QtWidgets.QMenu('&Help', self)
        self.help_menu.addAction('&Documentation', self.show_documentation)
        self.menuBar().addMenu(self.help_menu)

    def fileNew(self):
        # refresh the User Interface
        self.clearData()
        ax = self.canvas_3d.axes
        ax.clear()
        self.canvas_3d.draw()

    def save_elevation_angle(self):
        """保存抬升角
        """
        if not self.elevation_angle:
            self.statusBar().showMessage('No data simulated.')
            return
        result = []
        for i, _angle in enumerate(self.elevation_angle):
            _angle.insert(0, i+1)
            result.append(_angle)
        files_types = "CSV data files (*.csv)"
        fileDialog = QtWidgets.QFileDialog()
        fileDialog.setAcceptMode(QtWidgets.QFileDialog.AcceptSave)
        filename, fil = QtWidgets.QFileDialog.getSaveFileName(self, 'Save file', os.path.expanduser('~'), files_types)
        try:
            with open(filename, 'w') as f:
                f_csv = csv.writer(f)
                first_row = ['0', ]
                first_row.extend(list(range(len(self.elevation_angle[0])-1)))
                f_csv.writerow(first_row)
                f_csv.writerows(result)
        except FileNotFoundError:
            self.statusBar().showMessage('data not save.')

    def save_azimuth(self):
        """保存方位角
        """
        if not self.azimuth:
            self.statusBar().showMessage('No data simulated.')
            return
        result = []
        for i, _angle in enumerate(self.azimuth):
            _angle.insert(0, i+1)
            result.append(_angle)
        files_types = "CSV data files (*.csv)"
        fileDialog = QtWidgets.QFileDialog()
        fileDialog.setAcceptMode(QtWidgets.QFileDialog.AcceptSave)
        filename, fil = QtWidgets.QFileDialog.getSaveFileName(self, 'Save file', os.path.expanduser('~'), files_types)
        try:
            with open(filename, 'w') as f:
                f_csv = csv.writer(f)
                first_row = ['0', ]
                first_row.extend(list(range(len(self.azimuth[0])-1)))
                f_csv.writerow(first_row)
                f_csv.writerows(result)
        except FileNotFoundError:
            self.statusBar().showMessage('data not save.')


    def fileQuit(self):
        # quit app
        self.close()

    def imageSave(self):
        try:
            self.fig_toolbar.save_figure()
        except Exception as e:
            self.statusBar().showMessage('Image not save Exception:%s' % e)

    def simulate_3d(self):
        ax = self.canvas_3d.axes
        ax.clear()
        self.canvas_3d.draw()

        radius = float(self.box_radius.value())/1000
        lightNum = int(self.box_lightNum.value())
        waveLength = float(self.box_waveLength.value())
        times = int(self.box_times.value())
        refraction_index = float(self.box_m.value())

        sphere = Sphere(radius)
        longitude, latitude, linewidth, color, alpha = 100, 100, 0.8, 'b', 0.1
        draw_sphere_at_axes(ax, radius, longitude, latitude, linewidth, color, alpha)

        x, y, z = [], [], []
        points_and_lines = []
        points = []
        lines = []
        if_continuous = True if 'Continuous' == self.comboBox.currentText() else False
        if not if_continuous:
            start_points = self.data['start_point']
            directions = self.data['vector']
            for p, v in zip(start_points, directions):
                vector = Vec3d(float(v[0]), float(v[1]), float(v[2])).normalized()        # 光线方向且单位化
                light = Light(waveLength, vector, 1, unit='nm')
                _p_and_l = drawer(sphere, incident_light=light, 
                                  refraction_index=refraction_index, 
                                  start_point=p, intersection_time=times)
                if _p_and_l:
                    points_and_lines.append(_p_and_l)
            if not points_and_lines:
                self.statusBar().showMessage('No intersection point exists')
                return
            for p_l in points_and_lines:
                for p in p_l['points']:
                    points.append(p)
                for l in p_l['lines']:
                    lines.append(l)
            xyz = tuple(zip(*points))
            x, y, z = xyz if xyz else [[]]*3

        else:
            # 移除原有的分布图
            for i in reversed(range(self.output_figure_layout.count())):
                if self.output_figure_layout.itemAt(i).widget():
                    self.output_figure_layout.itemAt(i).widget().setParent(None)
            co_settings = []
            for _check, _set in zip(self.co_checkbox, self.co_settings):
                if _check.isChecked():
                    co_settings.append(float(_set.value())/1000)
                else:
                    co_settings.append(None)
            v = Vec3d(0, 1, 0)
            light = Light(waveLength, v, 1, unit='nm')
            start_point_list = generate_multi_start_points(radius, lightNum, 
                                                           set_x=co_settings[0], 
                                                           set_y=self.set_y.value()/1000,
                                                           set_z=co_settings[1])
            points_and_lines_and_lights = multi_line_drawer(sphere, light, refraction_index, start_point_list, times)
            if not points_and_lines_and_lights:
                self.statusBar().showMessage('No intersection point exists')
                return
            points = points_and_lines_and_lights['points']
            lines = points_and_lines_and_lights['lines']['incident_lines']
            lines.extend(points_and_lines_and_lights['lines']['reflection_lines'])
            lines.extend(points_and_lines_and_lights['lines']['refraction_lines'])
            lines = [p_line for time_lines in lines for p_line in time_lines]
            x, y, z = points
            lights = points_and_lines_and_lights['lights']['refraction_lights']
            lights[0] = points_and_lines_and_lights['lights']['reflection_lights'][0]
            output_x = []
            self.elevation_angle = []
            self.azimuth = []
            for l in lights:
                output_x.append(list(range(len(l))))
                self.elevation_angle.append([ calculate_elevation_angle(light.direction) for light in l])  # 抬升角
                self.azimuth.append([math.degrees(math.atan2(light.direction.x, light.direction.y)) for light in l]) # 方位角
            # 一张张分布图的增加 属性都想相同
            for i, (_ele, _azi) in enumerate(zip(self.elevation_angle, self.azimuth)):
                _output_canvas_frame = QtWidgets.QFrame()
                _output_canvas_hbox = QtWidgets.QHBoxLayout()
                _output_canvas_frame.setLayout(_output_canvas_hbox)
                _canvas1 = ScatterCanvas(width=0.5, height=0.5)
                _canvas2 = ScatterCanvas(width=0.5, height=0.5)
                ax2 = _canvas2.fig.axes[0]
                ax1 = _canvas1.fig.axes[0]
                s1 = [10]*len(_ele)
                ax1.scatter(output_x[i], _ele, s=s1)
                ax2.scatter(output_x[i], _azi, s=s1)
                ax1.set_title('(%i time) elevation angle distribution' % (i+1))
                ax2.set_title('(%i time) azimuth distribution' % (i+1))
                ax1.set_ylabel('angle (degree)')
                ax2.set_ylabel('angle (degree)')
                ax1.set_xlabel('num of light')
                ax2.set_xlabel('num of light')
                _canvas1.setMinimumHeight(400)
                _canvas2.setMinimumHeight(400)
                _canvas1.setMaximumWidth(400)
                _canvas2.setMaximumWidth(400)
                _output_canvas_hbox.addWidget(_canvas1)
                _output_canvas_hbox.addWidget(_canvas2)
                self.output_figure_layout.addWidget(_output_canvas_frame)

        s = [8] * len(x)
        ax.scatter(x, y, z, s=s)
        if lines:
            for l in lines:
                ax.add_line(l)
        boarder = 1.5*radius
        # ax.axis('equal')
        ax.set_xlim(-boarder, boarder)
        ax.set_ylim(-boarder, boarder)
        ax.set_zlim(-boarder, boarder)
        ax.legend(loc='upper left', frameon=False)
        self.canvas_3d.draw()


    def addOutputArea(self):

        self.output_frame = QtWidgets.QFrame()
        self.output_frame.setMinimumWidth(800)
        self.output_frame.setSizePolicy(QtWidgets.QSizePolicy.Expanding,
                                        QtWidgets.QSizePolicy.Expanding)
        self.output_vbox = QtWidgets.QVBoxLayout()
        self.output_frame.setLayout(self.output_vbox)

        self.output_figure_layout = QtWidgets.QVBoxLayout()
        self.output_figure_layout.addStretch()
        output_group_box = QtWidgets.QGroupBox()
        output_group_box.setLayout(self.output_figure_layout)


        self.output_scroll = QtWidgets.QScrollArea()
        self.output_scroll.setWidget(output_group_box)
        self.output_scroll.setWidgetResizable(True)
        self.output_scroll.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        self.output_scroll.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)

        self.output_vbox.addWidget(self.output_scroll)

        self.main_layout.addWidget(self.output_frame)

    def change_radius(self):
        """半径改变时 改变选项框的数值范围
        """
        radius = float(self.box_radius.value())
        self.set_y.setValue(-1.5*radius)
        self.set_x.setRange(-radius+1, radius-1)
        self.set_z.setRange(-radius+1, radius-1)
        self.start_x.setRange(-radius+1, radius-1)
        self.start_z.setRange(-radius+1, radius-1)

    def show_documentation(self):
        webbrowser.open('https://github.com/GalaCastell/geometric-light-scatter-on-circle/wiki')



app = QtWidgets.QApplication(sys.argv)

appWindow = ApplicationWindow()
appWindow.showMaximized()
sys.exit(app.exec_())

