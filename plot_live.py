import itertools
import csv
import numpy as np
import pyqtgraph as pg
import PyQt5.QtWidgets as qtw
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtGui import QIcon
import os
import sys
import get
import Plotting_Scripts.DateAxisItem as DateAxisItem

class PlotApp(qtw.QMainWindow):

    colors0 = [(255, 0, 0),         # Red
               (0, 255, 0),         # Green
               (0, 0, 255)]         # Blue
    colors1 = [(155, 0, 0),         # dark red
               (76, 145, 0),        # dark green
               (0, 0, 200),         # dark blue
               (122, 23, 220),      # purple
               (204, 102, 0)]       # dark orange
    colors2 = [(255, 101, 102),     # rose
               (51, 255, 153),      # light green
               (0, 204, 204),       # cyan
               (228, 104, 232),     # magenta
               (255, 152, 51)]      # orange

    def __init__(self):
        super(PlotApp, self).__init__()
        pg.setConfigOption('background', 'w')
        pg.setConfigOption('foreground', 'k')

        self.base_path = get.google_drive()
        self.filename = None            # will be fill later

        self.force_quit = True          # will turn false if quit properly

        """WINDOW PROPERTIES"""
        self.setWindowTitle('Dielecctric Spectroscopy')
        self.left = 10
        self.top = 35
        self.width = 1200
        self.height = 800

        self.setWindowIcon(QIcon(os.path.join('icons', 'plot.png')))

        self.setGeometry(self.left, self.top, self.width, self.height)

        # self.layout = qtw.QGridLayout(self)

        self.plot = pg.PlotWidget()
        self.setCentralWidget(self.plot)

        self.labels = [None]

        """These will be the curves drawn on the plots"""
        self.curves = [None]
        self.pens = [None]

        """MENU BAR"""
        mainMenu = self.menuBar()

        # File
        fileMenu = mainMenu.addMenu('File')

        open_data_button = qtw.QAction(QIcon(os.path.join('icons', 'open.png')), 'Open Data Set', self)
        open_data_button.setShortcut('Ctrl+O')
        open_data_button.triggered.connect(self.open_data)

        exitButton = qtw.QAction(QIcon(os.path.join('icons', 'quit.png')), 'Exit', self)
        exitButton.setShortcut('Ctrl+Q')
        exitButton.triggered.connect(self.quit)

        fileMenu.addActions([open_data_button])
        fileMenu.addSeparator()
        fileMenu.addActions([exitButton])

        # Plot
        plotMenu = mainMenu.addMenu('Plot')

        self.play_button = qtw.QAction(QIcon(os.path.join('icons', 'play.png')), 'Plot Live', self)
        self.play_button.setShortcut('Ctrl+P')
        self.play_button.triggered.connect(self.plot_live)
        self.play_button.setEnabled(False)

        self.pause_button = qtw.QAction(QIcon(os.path.join('icons', 'pause.png')), 'Pause Live Plot', self)
        self.pause_button.setShortcut('Ctrl+P')
        self.pause_button.triggered.connect(self.pause_live)
        self.pause_button.setEnabled(False)

        plotMenu.addActions([self.play_button, self.pause_button])

        # Show the App
        self.show()

    @pyqtSlot()
    def plot_live(self):
        self.play_button.setEnabled(False)
        self.pause_button.setEnabled(True)

    @pyqtSlot()
    def pause_live(self):
        self.play_button.setEnabled(True)
        self.pause_button.setEnabled(False)

    @pyqtSlot()
    def open_data(self):
        # Open Dialog box to pick the data file
        self.play_button.setEnabled(True)
        options = qtw.QFileDialog.Options()
        options |= qtw.QFileDialog.DontUseNativeDialog
        filename, _ = qtw.QFileDialog.getOpenFileName(self, "Select Data Set", self.base_path,
                                                      "CSV (*.csv);;All Files (*)", options=options)
        self.filename = filename

        # Find the column labels in the file and use them to label the axes
        self.labels = self.get_labels(filename)
        self.plot.setLabel('left', self.labels[1])
        self.plot.setLabel('bottom', self.labels[0])
        # If there are multiple Y columns, set up a legend
        if len(self.labels) > 2:
            self.plot.addLegend()
        if 'time' in self.labels[0].lower():
            self.plot.setAxisItems({'bottom': DateAxisItem.DateAxisItem('bottom')})

        # Make curves and pens have as many elements as there are Y columns
        y_num = len(self.labels) - 1
        self.curves *= y_num
        self.pens *= y_num

        for ii, color in enumerate(PlotApp.colors1[:y_num]):
            self.pens[ii] = pg.mkPen(color, width=2)

        for ii, label in enumerate(self.labels[1:]):
            self.curves[ii] = self.plot.plot(pen=self.pens[ii], name=label)

        self.updatePlots()

    @pyqtSlot()
    def updatePlots(self):
        data = self.load_data(self.filename)
        if len(data.shape) > 1:
            x = data[:, 0]
            for ii, curve in enumerate(self.curves):
                curve.setData(x=x, y=data[:, ii + 1])

    @staticmethod
    def load_data(filename, attempts=20):
        data = None
        for ii in range(attempts):    # as long as the "try" passes, the loop breaks
            try:
                data = np.loadtxt(filename, comments='#', delimiter=',', skiprows=ii)
                break
            except:
                pass
        return data

    @staticmethod
    def get_labels(filename, line_skip=8):
        """Locates the first row in the file which isn't commented out. Expected to be the labels"""
        with open(filename, 'r') as f:
            reader = csv.reader(f, delimiter=',')
            for ii, row in enumerate(reader):
                if row[0][0] != '#':
                    break
        return row

    @pyqtSlot()
    def quit(self):
        exit_q = qtw.QMessageBox.question(self, 'Exiting', 'Are you sure you would like to quit?',
                                          qtw.QMessageBox.Yes | qtw.QMessageBox.Cancel, qtw. QMessageBox.Cancel)
        if exit_q == qtw.QMessageBox.Yes:
            self.force_quit = False
            print('Exiting')
            self.close()

    def closeEvent(self, event):
        if self.force_quit:
            self.quit()


if __name__ == '__main__':
    app = qtw.QApplication(sys.argv)
    ex = PlotApp()
    sys.exit(app.exec_())
