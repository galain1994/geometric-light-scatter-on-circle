#!/usr/bin/python3
# -*- coding: utf-8 -*-

import os
import sys
import csv
from collections import namedtuple
import webbrowser
import matplotlib
matplotlib.use('Qt5Agg')
import matplotlib.pyplot as plt
# from mpl_toolkits.mplot3d import Axes3D
from PyQt5 import QtCore, QtWidgets, QtGui
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotCanvas import ScatterCanvas
from intersectionElements import Light, Circle
from intersectionDrawer import drawer
from intersectionFuncs import tangential_vector_to_circle
from pygameVector import Vec2d


class MyNavigationToolbar(NavigationToolbar):
    # 去掉不需要的工具栏项目
    toolitems =tuple(i for i in NavigationToolbar.toolitems
                            if i[0] not in ('Subplots', ))


class ApplicationWindow(QtWidgets.QMainWindow):

    def __init__(self):
        super(ApplicationWindow, self).__init__()
        # 记录起始点和入射光线的方向
        self.data = {'start_point':[], 'vector':[]}

        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)   #  Make Qt delete this widget when widget accept close event
        app_icon = QtGui.QIcon()
        app_icon.addFile('./icon.png', QtCore.QSize(124, 124))
        app.setWindowIcon(app_icon) # 设置窗口图标
        self.setWindowTitle('球形粒子几何光学追迹') # 设置题目

        self.if_3d = False
        self.angle_y = None # 方位角初始为None

        self.addMenu()

        self.main_widget = QtWidgets.QWidget(self) # 主窗口
        self.main_layout = QtWidgets.QHBoxLayout(self.main_widget)
        self.main_widget.setSizePolicy(QtWidgets.QSizePolicy.Expanding,
                                       QtWidgets.QSizePolicy.Expanding) # 设置窗口政策为拓展型

        self.addDataArea() # 增加数据输入区

        self.statusBar()    # 初始化下方状态栏

        self.canvas_2d = ScatterCanvas(self.main_widget, 8, 8) # 初始化绘图画板
        self.addCanvas(self.canvas_2d)  # 增加画板区域

        self.addOutputArea()    # 增加方位角输出区域
        self.output_frame.setHidden(True) # 首先隐藏输出区域

        self.main_widget.setFocus()
        self.setCentralWidget(self.main_widget) # 主窗口设为中心组件

    def addDataArea(self):
        """add data area on the left
        """
        if_3d = self.if_3d

        self.data_frame = QtWidgets.QFrame()
        self.data_layout = QtWidgets.QVBoxLayout()
        self.data_layout.setAlignment(QtCore.Qt.AlignLeft)
        self.data_frame.setLayout(self.data_layout)
        self.data_frame.setSizePolicy(QtWidgets.QSizePolicy.Expanding,
                                      QtWidgets.QSizePolicy.Expanding)

        # show light information
        data_form = QtWidgets.QVBoxLayout()
        self.createTable()
        data_form.setSpacing(10) # 增加间距
        data_form.addWidget(self.tableWidget) # 增加数据表
        self.data_form = data_form

        qbox = QtWidgets.QGroupBox('Light')
        qbox.setLayout(data_form)
        qbox.setAlignment(QtCore.Qt.AlignCenter)  # 设置对齐方式为居中
        qbox.setContentsMargins(-12, 12, -5, -5)  # 边框间距

        scrollArea = QtWidgets.QScrollArea()    # 滚动条
        scrollArea.setAlignment(QtCore.Qt.AlignLeft)
        scrollArea.setWidget(qbox)
        scrollArea.setWidgetResizable(True)  # 窗口自适应

        qbox.updateGeometry()
        self.data_layout.addWidget(scrollArea)

        # coordinates
        input_form = QtWidgets.QFormLayout()    # 数据栏的表框
        input_form.setSpacing(0)
        input_form.setAlignment(QtCore.Qt.AlignLeft)
        coordinates = QtWidgets.QHBoxLayout()
        coordinates.setSpacing(0)
        coordinates.setAlignment(QtCore.Qt.AlignLeft)
        input_form.addRow('Start Point:  ', coordinates)
        lx, ly = QtWidgets.QLabel('x:   '), QtWidgets.QLabel('y:   ')
        self.startpoint_x, self.startpoint_y = [QtWidgets.QSpinBox() for i in range(2)] # 增加起始点坐标的输入框 两位浮点数
        self.startpoint_x.setRange(-10000, -999)    # 初始设置x取值范围
        self.startpoint_y.setRange(-999, 999)   # 初始设置y取值范围
        self.co = (self.startpoint_x, self.startpoint_y)    
        self.startpoint_x.setValue(-1.5*1000)   # 设置x的初始值
        self.startpoint_x.setEnabled(False)     # 禁用x输入
        self.startpoint_y.valueChanged.connect(self.y_changed)  # y值改变的动作将触发函数y_changed
        label = (lx, ly)
        for _co, _label in zip(self.co, label):
            coordinates.addWidget(_label)   # 将标签添加到布局中
            coordinates.addWidget(_co)  # 将输入框添加到布局中

        # direction
        direction_layout = QtWidgets.QHBoxLayout()
        direction_layout.setContentsMargins(-20, 0, 0, 0)
        direction_layout.setAlignment(QtCore.Qt.AlignLeft)
        input_form.addRow('Direction:  ', direction_layout)
        lvx, lvy = QtWidgets.QLabel('Vx: '), QtWidgets.QLabel('Vy: ')   # 方向的标签
        vx, self.vy = [QtWidgets.QDoubleSpinBox() for i in range(2)]    # 方向的输入框
        circle = Circle(1000)   # 初始化的圆
        vector_range = tangential_vector_to_circle(circle, (-1.5*1000, 0))  # 初始化入射光方向范围
        self.vy.setRange(vector_range[0].y, vector_range[1].y)
        self.vy.setToolTip('Minimum:%s, Maximum:%s' % (vector_range[0].y, vector_range[1].y)) # 初始化提示框
        vx.setValue(1)
        vx.setEnabled(False)    # 将方向的矢量的x固定且不可改变
        self.v = (vx, self.vy)
        lv = (lvx, lvy)
        for _v, _lv in zip(self.v, lv):
            _v.setSingleStep(0.1)
            direction_layout.addWidget(_lv)
            direction_layout.addWidget(_v)

        self.data_layout.addLayout(input_form)

        self.createModForm()
        self.data_layout.addLayout(self.mod_form)

        self.main_layout.addWidget(self.data_frame)

    def createTable(self):
        self.tableWidget = QtWidgets.QTableWidget() # 新建表实例
        self.tableWidget.setGeometry(0, 0, 100, 600)
        self.tableWidget.setRowCount(1) # 初始化行数
        self.tableWidget.setColumnCount(2)  # 初始化列数
        self.tableWidget.setColumnWidth(0, 120) # 设置第一列列宽
        self.tableWidget.setColumnWidth(1, 120) # 设置第二列列宽
        self.tableWidget.setItem(0, 0, QtWidgets.QTableWidgetItem('Start Point'))   # 初始化第一列表头
        self.tableWidget.setItem(0, 1, QtWidgets.QTableWidgetItem('Direction')) # 初始化第二列表头

    def createModForm(self):
        self.mod_form = QtWidgets.QFormLayout() # 实例话表格布局
        self.submit_button = QtWidgets.QPushButton('add')   # 实例化按钮 ‘增加’
        self.submit_button.pressed.connect(self.addData)    # 将‘增加’按钮的动作绑定到addData函数中
        self.mod_form.addRow(self.submit_button)    # 将按钮添加到布局中
        self.mod_form.setContentsMargins(-50, 0, 0, 0)
        h = QtWidgets.QHBoxLayout() # 设置为水平布局
        self.delete_line = QtWidgets.QSpinBox()
        self.delete_line.setMaximum(self.tableWidget.rowCount())
        self.delete_line.setMinimum(self.tableWidget.rowCount())
        self.delete_button = QtWidgets.QPushButton('delete')
        self.delete_button.pressed.connect(self.removeData) # 将‘删除’按钮绑定到removeData函数中
        self.clear_button = QtWidgets.QPushButton('clear')
        self.clear_button.pressed.connect(self.clearData)   # 将‘清空’按钮绑定到clearData函数中
        h.addWidget(self.delete_line)
        h.addWidget(self.delete_button)
        h.addWidget(self.clear_button)
        self.mod_form.addRow('Line:', h)

    def addData(self):
        start_point = tuple(round(_co.value()/1000, 5) for _co in self.co)  # 获取坐标值并除以1000 将mm单位转化为cm单位
        vector = tuple(round(_v.value(), 5) for _v in self.v)   # 获取坐标值
        # 如果数据中有重复起始点和方向数据 在状态栏中提示
        for (p, v) in zip(self.data['start_point'], self.data['vector']):
            if start_point == p and vector == v:
                self.statusBar().showMessage('！ already have same data')
                return
        self.data['start_point'].append(start_point)
        self.data['vector'].append(vector)
        # 在表格中增加来显示
        self.tableWidget.setRowCount(len(self.data['start_point'])+1)
        self.tableWidget.setItem(len(self.data['start_point']), 0, QtWidgets.QTableWidgetItem(str(start_point)))
        self.tableWidget.setItem(len(self.data['start_point']), 1, QtWidgets.QTableWidgetItem(str(vector)))
        self.delete_line.setMaximum(self.tableWidget.rowCount())    # 在删除行更改最大能删除的行
        self.delete_line.setMinimum(2)
        self.statusBar().clearMessage()

    def removeData(self):
        """删除所选行数的数据
        """
        line = self.delete_line.value()
        if not self.data['start_point']:
            self.statusBar().showMessage('！ No data')
            return
        p = self.data['start_point'].pop(line-2)    # 除去表头和偏移量
        v = self.data['vector'].pop(line-2)
        self.tableWidget.removeRow(line-1)
        self.statusBar().showMessage('Line: {2}, point:{0} vector:{1} has been removed.'.format(p, v, line))
        mini_row = 2 if self.tableWidget.rowCount() > 2 else 1
        self.delete_line.setMinimum(mini_row)
        self.delete_line.setMaximum(self.tableWidget.rowCount())

    def clearData(self):
        """清空数据
        """
        self.data = {'start_point':[], 'vector':[]}
        row_count = self.tableWidget.rowCount()
        for i in range(row_count, 0, -1):
            self.tableWidget.removeRow(i)
        self.delete_line.setMaximum(self.tableWidget.rowCount())
        self.delete_line.setMinimum(self.tableWidget.rowCount())

    def addCanvas(self, canvas):
        # plotting area
        self.canvas_frame = QtWidgets.QFrame()
        self.canvas_layout = QtWidgets.QVBoxLayout()
        self.canvas_frame.setLayout(self.canvas_layout)

        self.comboBox = QtWidgets.QComboBox()   # 下拉选择框
        self.comboBox.addItem("Single Points")
        self.comboBox.addItem("Continuous")
        self.comboBox.currentIndexChanged.connect(self.selectionChange) # 当选择改变时
        self.canvas_layout.addWidget(self.comboBox)

        self.light_attribute_form = QtWidgets.QGridLayout()

        lable_m, label_radius, label_waveLength, label_lightNum, label_times = QtWidgets.QLabel('m (refraction index):'), \
                    QtWidgets.QLabel('Radius (um):'), QtWidgets.QLabel('Wave Length (nm):'), \
                    QtWidgets.QLabel('Light Nums:'), QtWidgets.QLabel('times:') # 参数的标签
        self.box_m, self.box_radius, self.box_waveLength, self.box_lightNum, self.box_times = [QtWidgets.QDoubleSpinBox() for i in range(5)]
        labels = [[label_radius], [lable_m, label_waveLength], [label_lightNum, label_times]]
        boxes = [[self.box_radius], [self.box_m, self.box_waveLength], [self.box_lightNum, self.box_times]]

        # 初始化参数的范围和取值
        self.box_m.setDecimals(4)
        self.box_m.setValue(1.335)
        self.box_radius.setDecimals(2)
        self.box_radius.setRange(0, 10000)
        self.box_radius.setValue(1000)
        self.box_radius.valueChanged.connect(self.radius_changed)
        self.box_waveLength.setDecimals(2)
        self.box_waveLength.setMaximum(1000)
        self.box_waveLength.setValue(532)
        self.box_lightNum.setDecimals(0)
        self.box_lightNum.setRange(2, 3000)
        self.box_lightNum.setEnabled(False)
        self.box_times.setDecimals(0)
        self.box_times.setValue(3)
        self.box_times.setMaximum(20)
        # 将标签和输入框添加到布局中
        for row, widgets in enumerate(zip(labels, boxes)):
            for column, (label, box) in enumerate(zip(*widgets)):
                self.light_attribute_form.addWidget(label, row, column*2)
                self.light_attribute_form.addWidget(box, row, column*2+1)
        # 追迹／绘图的按钮
        self.simulate_button = QtWidgets.QPushButton('Simulate')
        self.simulate_button.pressed.connect(self.simulate_2d)

        self.canvas_layout.addLayout(self.light_attribute_form)
        self.canvas_layout.addWidget(self.simulate_button)
        # 绘图画板
        self.fig_toolbar = MyNavigationToolbar(canvas, self.main_widget)
        self.canvas_layout.addWidget(canvas)
        self.canvas_layout.addStretch()
        self.canvas_layout.addWidget(self.fig_toolbar)
        # 版权区域
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

    def selectionChange(self):
        """单挑光线还是光簇选项改变的复选框改变时触发的函数
        """
        ax = self.canvas_2d.axes
        ax.clear()
        self.canvas_2d.draw()
        if "Continuous" == self.comboBox.currentText():
            self.data_frame.setHidden(True)
            self.output_frame.setHidden(False)
            self.data_layout.setEnabled(False)
            self.box_lightNum.setEnabled(True)
            self.box_lightNum.setMinimum(2)
        else:
            self.data_frame.setHidden(False)
            self.output_frame.setHidden(True)
            self.data_layout.setEnabled(True)
            self.box_lightNum.setEnabled(False)

    def addMenu(self):
        """add file menu
        初始化菜单栏
        """
        self.file_menu = QtWidgets.QMenu('&File', self)
        self.file_menu.addAction('&New', self.fileNew, 
                                 QtCore.Qt.CTRL + QtCore.Qt.Key_N)  # Ctrl+N 新建
        self.file_menu.addAction('Save Data', self.fileSave,
                                 QtCore.Qt.CTRL + QtCore.Qt.SHIFT + QtCore.Qt.Key_S)    # Ctrl+Shift+S 保存输出数据
        self.file_menu.addAction('&Save Image', self.imageSave,
                                 QtCore.Qt.CTRL + QtCore.Qt.Key_S)  # Ctrl+S 保存追迹图像
        self.file_menu.addAction('&Quit', self.fileQuit, 
                                 QtCore.Qt.CTRL + QtCore.Qt.Key_Q)  # Ctrl+Q 退出程序
        self.menuBar().addMenu(self.file_menu)

        self.menuBar().addSeparator()   # 增加间距
        # add help documentation
        self.help_menu = QtWidgets.QMenu('&Help', self)
        self.help_menu.addAction('&Documentation', self.show_documentation)
        self.menuBar().addMenu(self.help_menu)

    def fileNew(self):
        # refresh the User Interface
        self.clearData()
        ax = self.canvas_2d.axes
        ax.clear()
        self.canvas_2d.draw()

    def fileSave(self):
        """save data to file
        保存输出数据 CSV格式
        """
        if not self.angle_y:
            self.statusBar().showMessage('No data simulated.')
            return
        data = self.angle_y
        result = []
        for i, angle in enumerate(data):
            angle.insert(0, i+1)
            result.append(angle)
        files_types = "CSV data files (*.csv)"
        fileDialog = QtWidgets.QFileDialog()
        fileDialog.setAcceptMode(QtWidgets.QFileDialog.AcceptSave)
        filename, fil = QtWidgets.QFileDialog.getSaveFileName(self, 'Save file', os.path.expanduser('~'), files_types)
        try:
            with open(filename, 'w') as f:
                f_csv = csv.writer(f)
                first_row = ['0', ]
                first_row.extend(list(range(len(data[0])-1)))
                f_csv.writerow(first_row)
                f_csv.writerows(result)
        except FileNotFoundError:
            self.statusBar().showMessage('data not save.')

    def fileQuit(self):
        # quit app
        self.close()

    def imageSave(self):
        """save the simulation result
        调用matplotlib的工具栏的保存图片的功能
        """
        try:
            self.fig_toolbar.save_figure()
        except Exception as e:
            self.statusBar().showMessage('Image not save Exception:%s' % e)

    def simulate_2d(self):
        """追迹的主程序
        """
        # 先清空图像
        ax = self.canvas_2d.axes
        ax.clear()
        self.canvas_2d.draw()
        # 获取参数
        radius = float(self.box_radius.value())/1000
        lightNum = int(self.box_lightNum.value())
        waveLength = float(self.box_waveLength.value())
        times = int(self.box_times.value())
        refraction_index = float(self.box_m.value())

        circle = Circle(radius)
        circle_patch = plt.Circle((0,0), radius, fill=False)    # 圆主体 中间不填充

        x = []
        y = []
        if_continuous = True if 'Continuous' == self.comboBox.currentText() else False  # 入射光线的方式
        if not if_continuous:
            points_and_lines = []
            start_points = self.data['start_point']
            directions = self.data['vector']
            for p, v in zip(start_points, directions):
                v = (float(v[0]), float(v[1]))
                light = Light(waveLength, Vec2d(v).normalized(), 1, unit='nm')
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
            # 将输出画板一张张删除
            for i in reversed(range(self.output_figure_layout.count())):
                if self.output_figure_layout.itemAt(i).widget():
                    self.output_figure_layout.itemAt(i).widget().setParent(None)
            v = (1, 0)
            light = Light(waveLength, Vec2d(v).normalized(), 1, unit='nm')
            points_and_lines = drawer(circle, light, refraction_index, density=lightNum, intersection_time=times)
            xy = points_and_lines['intersection_points']
            x = xy[0]
            y = xy[1]
            lines = [line for l in (points_and_lines['incident_lines'], \
                                    points_and_lines['refraction_lines'], \
                                    points_and_lines['reflection_lines']) for ll in l for line in ll]   # 解构所有的线段

            # angle of refraction
            lights = points_and_lines['refraction_lights']
            lights[0] = points_and_lines['reflection_lights'][0]
            angle_x = list(range(len(lights[0])))
            self.angle_y = []   # 方位角
            for l in lights:
                self.angle_y.append([light.direction.angle for light in l])
            for i, _y in enumerate(self.angle_y):
                _canvas = ScatterCanvas(width=3, height=5)   # size of each figure 
                s = [5] * len(angle_x)
                _canvas.axes.scatter(angle_x, _y, s=s)
                _canvas.axes.set_title('(%i time) Aimuth angle distribution' % (i+1))
                _canvas.axes.set_ylabel('angle (degree)')
                _canvas.axes.set_xlabel('num of light')
                _canvas.setMinimumHeight(400)
                self.output_figure_layout.addWidget(_canvas)
            self.output_scroll.updateGeometry()

        s = [5] * len(x)    # 5表示点的大小 x表示有多少个点 所有点的大小都相等
        ax.scatter(x, y, s=s)
        ax.add_patch(circle_patch)
        ax.axis('equal')
        if lines:
            for l in lines:
                ax.add_line(l)
        boarder = 2*radius
        ax.axis([-boarder, boarder, -boarder, boarder])
        self.canvas_2d.draw()

    def addOutputArea(self):
        """初始化数据输出区
        """
        self.output_frame = QtWidgets.QFrame()
        self.output_frame.setSizePolicy(QtWidgets.QSizePolicy.Expanding,
                                        QtWidgets.QSizePolicy.Expanding)
        self.output_vbox = QtWidgets.QVBoxLayout()
        self.output_frame.setLayout(self.output_vbox)

        self.output_figure_layout = QtWidgets.QVBoxLayout()
        self.output_figure_layout.addStretch()  # 增加间距
        output_group_box = QtWidgets.QGroupBox()
        output_group_box.setLayout(self.output_figure_layout)

        self.output_scroll = QtWidgets.QScrollArea()
        self.output_scroll.setWidget(output_group_box)
        self.output_scroll.setWidgetResizable(True)
        self.output_scroll.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)  # 垂直滚动条
        self.output_scroll.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff) # 水平滚动条

        self.output_vbox.addWidget(self.output_scroll)

        self.main_layout.addWidget(self.output_frame)

    def radius_changed(self):
        """当圆半径改变时
        """
        radius = float(self.box_radius.value())     # 获取圆半径
        circle = Circle(radius)
        self.startpoint_x.setValue(-1.5*radius) # 设定入射点的x坐标
        self.startpoint_y.setRange(-radius+1, radius-1) # 设定入射点的y坐标范围

    def y_changed(self):
        """当入射点y值改变时，入射光方向的范围改变
        """
        radius = float(self.box_radius.value())     # 获取圆半径
        circle = Circle(radius)
        start_point = (self.startpoint_x.value(), self.startpoint_y.value())
        vector_range = tangential_vector_to_circle(circle, start_point)
        self.vy.setRange(vector_range[0].y, vector_range[1].y)
        self.vy.setToolTip('Minimum:%s, Maximum:%s' % (vector_range[0].y, vector_range[1].y))

    def show_documentation(self):
        """文档的网址
        """
        webbrowser.open('https://github.com/GalaCastell/geometric-light-scatter-on-circle/wiki')



app = QtWidgets.QApplication(sys.argv)

appWindow = ApplicationWindow()
appWindow.showMaximized()
sys.exit(app.exec_())

