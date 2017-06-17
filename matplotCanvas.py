#!/usr/bin/python3
# -*- coding: utf-8 -*-


import matplotlib
matplotlib.use('Qt5Agg')
from matplotlib.figure import Figure
from mpl_toolkits.mplot3d import Axes3D
from mpl_toolkits.mplot3d import art3d
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from PyQt5.QtWidgets import QSizePolicy


class ScatterCanvas(FigureCanvas):
    """2d画板
    matplotlib的底层调用
    parent: 父级组件
    width：宽度
    height：高度
    dpi：像素值
    """
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi) # 初始化图
        self.axes = self.fig.add_subplot(111) # 增加子图 111表示总共一幅图，第一行，第一列

        FigureCanvas.__init__(self, self.fig)
        self.setParent(parent)

        FigureCanvas.setSizePolicy(self,
                                   QSizePolicy.Expanding,
                                   QSizePolicy.Expanding)   # 随窗口伸缩
        FigureCanvas.updateGeometry(self)


class MplPlot3dCanvas(FigureCanvas):
    """3d画板
    parent: 父级组件
    width：宽度
    height：高度
    dpi：像素值
    """
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = self.fig.add_subplot(111, projection='3d')  # 3d图像
        self.axes.view_init()

        FigureCanvas.__init__(self, self.fig)
        self.setParent(parent)

        FigureCanvas.setSizePolicy(self,
                                   QSizePolicy.Expanding,
                                   QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)
