import sys
from PyQt5.QtWidgets import QApplication, QWidget, QMainWindow, QGridLayout, QMessageBox, QAction, QGroupBox, QFileDialog, QSizePolicy, QProgressBar, QLabel, QPushButton, QVBoxLayout
import flSaveFileDialog as fsd

import dataDisplay as dd
import dataControlWidget as dcw
import fitDataInfo as fdi
import zoomButtonWidget as zbw
import fitInfoWidgetContainer as fic
import tabFits as tft
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from numpy import empty

TITLE = "AEGUIFit - "

class App(QMainWindow):

    def __init__(self):
        super().__init__()
        self.title = TITLE
        self.left = 100
        self.top = 50
        self.width = 1280
        self.height = 900
        self.bottom = 150
        self.right = 235
        self.initUI()
        self.menuInit()

    def menuInit(self):
        mbrMain = self.menuBar()
        mnuFile = mbrMain.addMenu('File')
        mnuExport = mbrMain.addMenu('Export')
        # mnuConfig = mbrMain.addMenu('Configurations')
        mnuConfig = mbrMain.addMenu('')
        mnuHelp = mbrMain.addMenu('Help')

        mbtOpen = QAction('Open...', self)
        mbtOpen.setShortcut('Ctrl+O')
        mbtOpen.setStatusTip('Open new file.')
        mbtOpen.triggered.connect(self.openFile)
        mnuFile.addAction(mbtOpen)

        mbtSave = QAction('Save...', self)
        mbtSave.setShortcut('Ctrl+S')
        mbtSave.setStatusTip('Save all data with fit and fit parameters.')
        mbtSave.triggered.connect(self.saveFile)
        mnuFile.addAction(mbtSave)

        mbtClose = QAction('Close', self)
        #mbtClose.setShortcut('Ctrl+C')
        mbtClose.setStatusTip('Close current file.')
        mbtClose.triggered.connect(self.closeFile)
        mnuFile.addAction(mbtClose)

        mnuFile.addSeparator()

        mbtQuit = QAction('Quit', self)
        mbtQuit.setShortcut('Ctrl+Q')
        mbtQuit.setStatusTip('Quit application.')
        mbtQuit.triggered.connect(self.close)
        mnuFile.addAction(mbtQuit)

        mbtSaveFig = QAction('Save Figure', self)
        mbtSaveFig.setShortcut('Ctrl+F')
        mbtSaveFig.setStatusTip('Save figure as is shown ...')
        mbtSaveFig.triggered.connect(self.saveFig)
        mnuExport.addAction(mbtSaveFig)

        mbtSaveFitData = QAction('Save Fit Data', self)
        mbtSaveFitData.setShortcut('Ctrl+D')
        mbtSaveFitData.setStatusTip('Save visible data points produced by the fit function in a .txt file ...')
        mbtSaveFitData.triggered.connect(self.saveFitData)
        mnuExport.addAction(mbtSaveFitData)

        mbtSaveFitDataWithData = QAction('Save Fit Data including Measurement Data', self)
        mbtSaveFitDataWithData.setShortcut('Ctrl+M')
        mbtSaveFitDataWithData.setStatusTip('Save visible data points produced by the fit function in a .txt file ...')
        mbtSaveFitDataWithData.triggered.connect(self.saveFitData)
        mnuExport.addAction(mbtSaveFitDataWithData)

        mbtAbout = QAction('About', self)
        mbtAbout.setShortcut("F1")
        mbtAbout.setStatusTip('About this program')
        mbtAbout.triggered.connect(self.showAbout)
        mnuHelp.addAction(mbtAbout)

    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)

        self.statusBar().showMessage('')
        self.progressBar = QProgressBar()
        self.progressBar.setMinimum(0)
        self.progressBar.setMaximum(100)

        self.progressBar.setFixedWidth(200)

        self.lblEnergyMark = QLabel(dd.DataDisplay.mark_default_text)
        self.statusBar().addPermanentWidget(self.lblEnergyMark, 1)

        self.lblProgUpdate = QLabel('')
        self.statusBar().addPermanentWidget(self.lblProgUpdate, 1)

        self.lblDisplayStat = QLabel('')
        self.statusBar().addPermanentWidget(self.lblDisplayStat, 1)

        self.statusBar().addPermanentWidget(self.progressBar, 1)

        # This is simply to show the bar
        # self.progressBar.setGeometry(0,0,0,0)

        self.ddMain = dd.DataDisplay()
        self.ddMain.setSizePolicy(QSizePolicy.Expanding,
                                  QSizePolicy.Expanding)

        self.ddMain.statusbar_update.connect(self.dd_statusbar_update)

        self.horizontalGroupBox = QGroupBox("Grid")
        layout = QGridLayout()
        # layout.setRowStretch(0, 50)
        #layout.setColumnStretch(0, 80)
        # layout.setRowStretch(1, 50)

        self.ficFits = fic.fitInfoWidgetContainer()
        self.dcwData = dcw.dataControlWidget()
        self.zbwMain = zbw.ZoomButtonWidget()
        
        self.ficFits.Post_Fit.connect(self.PostFit)  # self.ddMain.addFit(self.ficFits.getFitDataInfo())
        self.ficFits.Combined_Fit_Data_Updated.connect(self.Combined_Fit_Data_Updated)
        self.ficFits.progressUpdate.connect(self.progressUpdate)
        self.ficFits.disable_fit.connect(self.disable_fit)
        self.ficFits.remove_fit.connect(self.remove_fit)

        self.dcwData.showErrorBars_changed.connect(self.showErrorBars_changed)
        self.dcwData.data_changed.connect(self.dcwData_changed)
        self.dcwData.data_shift.connect(self.ddMain.shiftData)
        self.dcwData.load_fits.connect(self.ficFits.load_fits)
        self.dcwData.fit_loaded_fits.connect(self.ficFits.fit_loaded_fits)
        self.dcwData.load_view.connect(self.zbwMain.load_from_view_string)

        self.dcwData.data_shift.connect(self.ficFits.shift_data)
        # has to be generalized for multiple fiw

        self.ficFits.zoom_to_fit.connect(self.zoom_to_fit)
        # generalize

        # self.zbwMain.lower_down.connect(self.)
        self.zbwMain.zoom_by_increment.connect(self.zoom_by_increment)
        self.zbwMain.show_all.connect(self.zoom_show_all)
        self.zbwMain.scale_font_size_changed.connect(self.scale_font_size_changed)
        self.zbwMain.label_font_size_changed.connect(self.label_font_size_changed)
        self.zbwMain.fig_size_changed.connect(self.fig_size_changed)
        self.zbwMain.annotation_changed.connect(self.annotation_changed)
        self.zbwMain.annotation_font_size_changed.connect(self.annotation_font_size_changed)

        self.tabFits = tft.tabFits()
        self.ficFits.fit_added.connect(self.tabFits.addFit)
        self.ficFits.fit_added.connect(self.ddMain.addFit)
        self.tabFits.fit_index_changed.connect(self.ddMain.fit_index_changed)

        # change fit index after remove_fit, when and where and whos responsible for that anyway

        #self.ddVbox = QVBoxLayout()
        #self.ddVbox.addWidget(self.tabFits)
        #self.ddVbox.addWidget(self.ddMain)

        #layout.addItem(self.ddVbox, 0, 0)

        self.ddGbox = QGridLayout()
        self.ddGbox.addWidget(self.tabFits)
        self.ddGbox.addWidget(self.ddMain)
        #self.toolbar = NavigationToolbar(self.ddMain, self)
        #self.ddGbox.addWidget(self.toolbar)

        layout.addItem(self.ddGbox, 0, 0)

        layout.addWidget(self.ficFits, 0, 1)
        layout.addWidget(self.zbwMain, 1, 0)
        layout.addWidget(self.dcwData, 1, 1)

        self.horizontalGroupBox.setLayout(layout)

        mainWidget = QWidget(self)
        mainWidget.setLayout(layout)
        self.setCentralWidget(mainWidget)

        self.show()

    def set_dims(self):
        self.ficFits.setFixedHeight(self.height-self.bottom)
        #self.ddMain.hei
        self.dcwData.setFixedHeight(self.bottom)
        self.zbwMain.setFixedHeight(self.bottom)
        
        self.ficFits.setFixedWidth(self.right)
        self.dcwData.setFixedWidth(self.right)
        self.zbwMain.setFixedWidth(self.width-self.right)
        
        #self.height
        
    def resizeEvent(self, *args, **kwargs):
        self.set_dims()

    def progressUpdate(self, relation, p):
        self.progressBar.setValue(relation * 100)
        self.lblProgUpdate.setText("AE: " + str(round(p[1], 2)))

        # QMessageBox.information(self, "Pause", "", QMessageBox.Ok, QMessageBox.Ok)

    def showAbout(self):
        QMessageBox.information(self, "Info",
                                "In case of unexpected behaviours, errors, crashes, improvements or general questions about the program, please feel free to send an e-mail to\nandreas.bayer@uibk.ac.at",
                                QMessageBox.Ok, QMessageBox.Ok)

    def dd_statusbar_update(self, str_update):
        self.lblEnergyMark.setText(str_update)

    def loadData(self, fileName):
        self.dcwData.loadFile(fileName)
    
    def saveData(self, fileName):
        
        
        data_string = self.dcwData.get_data_string()
        view_string = self.zbwMain.get_view_string()
        fit_strings = self.ficFits.get_fit_strings()
        
        self.dcwData.saveFile(fileName, fit_strings, view_string, data_string)

    def dcwData_changed(self, showErrorBars):
        data = self.dcwData.getData()
        self.ddMain.setData(data)
        self.ddMain.setStdErrors(self.dcwData.getStdErrors())
        self.ddMain.refresh()

        self.ficFits.setData(data)
        self.ficFits.setStdErr(self.dcwData.getStdErrors())

    def zoom_by_increment(self, bound, increment):
        try:
            self.ddMain.ZoomByIncrement(bound, increment)
            self.ddMain.refresh()
        except:
            self.set_display_msg('Zooming failed.')

    def zoom_show_all(self):
        try:
            self.ddMain.ZoomShowAll()
            self.ddMain.refresh()
        except:
            self.set_display_msg('Showing all failed.')

    def zoom_to_fit(self, lb, ub, index):
        try:
            self.ddMain.ZoomToFit(lb, ub, index)
            self.ddMain.refresh()
        except:
            self.set_display_msg('Zoom to fit failed.')

    def scale_font_size_changed(self, value):
        try:
            self.ddMain.set_scale_font_size(value)
            self.ddMain.refresh()
        except:
            self.set_display_msg('Changing scale font size failed.')
            
    def label_font_size_changed(self, value):
        try:
            self.ddMain.set_label_font_size(value)
            self.ddMain.refresh()
        except:
            self.set_display_msg('Changing label font failed.')

    def fig_size_changed(self, new_fig_size):
        try:
            self.ddMain.set_fig_size(new_fig_size)
            self.ddMain.refresh()  # necessary?
        except:
            self.set_display_msg('changing figure size failed.')

    def annotation_changed(self, annotation):
        self.ddMain.set_annotation(annotation)

        try:
            self.ddMain.refresh()
            self.set_display_msg('')
        except:
            self.set_display_msg('Setting annotation failed.')

    def annotation_font_size_changed(self, value):
        try:
            self.ddMain.set_annotation_font_size(value)
            self.ddMain.refresh()
        except:
            self.set_display_msg('Changing annotation font failed.')

    def set_display_msg(self, msg):
        self.lblDisplayStat.setText(msg)

    def saveFig(self):
        name, ext = QFileDialog.getSaveFileName(self, "Save Figure", "", "*.pdf;; *.png;; *.svg;; *.eps")

        if name != '':
            try:
                ext = ext.split('.')[-1]
                fig = self.ddMain.getFigure()
                #fig.set_size_inches(31, 13.8)
                fig.savefig(name, format=ext)
            except:
                QMessageBox.critical(self, "Saving figure failed!", "Error while saving figure", QMessageBox.Ok,
                                     QMessageBox.Ok)

    def writeFitDataToFile(self, filename, includeMeausredData=False):
        file = open(filename, "w+")

        fitData = self.ddMain.getCurrentFitData()
        data = self.ddMain.getCurrentData()

        for i in range(0, len(fitData)):
            if includeMeausredData:
                file.write(
                    "%f\t%f\t%f\r\n" % (fitData[i][0], fitData[i][1], data[i][1]))
            else:
                file.write("%f\t%f\r\n" % (fitData[i][0], fitData[i][1]))

        file.close()

    def saveFitData(self):
        saveDialog = fsd.flSaveFileDialog()

        # name, ext = fsd.flSaveFileDialog.getSaveFileName(self, "Save Fit Data", "", "*.txt")
        name, ext = saveDialog.getSaveFileName(self, "Save Fit Data", "", "*.txt")

        if name != '':

            msgBox = QMessageBox()
            msgBox.setIcon(QMessageBox.Question)
            msgBox.setWindowTitle('Include measurement data?')
            msgBox.setText('Would you like to include measurement data as well?')
            msgBox.addButton(QPushButton('Include measurement data'), QMessageBox.YesRole)
            msgBox.addButton(QPushButton('Write only fit data'), QMessageBox.NoRole)
            msgBox.addButton(QPushButton('Cancel'), QMessageBox.RejectRole)
            ret = msgBox.exec_()

            if ret != QMessageBox.DestructiveRole:
                try:
                    if ret == QMessageBox.AcceptRole:
                        #   QMessageBox.information(self, "", "With M-Data", QMessageBox.Ok, QMessageBox.Ok)
                        self.writeFitDataToFile(name, includeMeausredData=True)
                    else:
                        #    QMessageBox.information(self, "", "Without M-Data", QMessageBox.Ok, QMessageBox.Ok)
                        self.writeFitDataToFile(name, includeMeausredData=False)
                except:
                    QMessageBox.critical(self, "Saving Data failed!", "Error while saving figure", QMessageBox.Ok,
                                         QMessageBox.Ok)

    def openFile(self):
        options = QFileDialog.Options()
        #options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getOpenFileName(self, "Open file", "", "Text Files (*.txt);;All Files (*)",
                                                  options=options)
        if fileName is not '':  # todo check file validity
            try:
                self.reset(True)
                self.loadData(fileName)

                self.setWindowTitle(TITLE + fileName)
            except:
                self.reset(False)
                QMessageBox.critical(self, "Open file failed!", "Error while opening " + fileName, QMessageBox.Ok,
                                     QMessageBox.Ok)
                self.setWindowTitle(TITLE)

    def saveFile(self):
        saveDialog = fsd.flSaveFileDialog()
    
        # name, ext = fsd.flSaveFileDialog.getSaveFileName(self, "Save Fit Data", "", "*.txt")
        fileName, ext = saveDialog.getSaveFileName(self, "Save File", "", "*.txt")

        if fileName is not '':  # todo check file validity
            try:
                self.saveData(fileName)
            except:
                QMessageBox.critical(self, "Saving file failed!", "Error while saving " + fileName, QMessageBox.Ok,
                                     QMessageBox.Ok)

    def closeFile(self):
        self.reset(enable=False)

    def reset(self, enable):
        self.ficFits.reset(enable)
        self.dcwData.reset(enable)
        self.ddMain.reset()
        self.tabFits.reset()
        self.zbwMain.reset(enable)

        self.progressBar.reset()

    def showErrorBars_changed(self, showErrorBars):
        try:
            self.ddMain.refresh(showErrorBars=showErrorBars)
            self.set_display_msg('')
        except:
            self.set_display_msg('Switching error bars failed.')


    def disable_fit(self, p_FitDataInfo):
        try:
            self.ddMain.refresh()
            self.set_display_msg('')
        except:
            self.set_display_msg('Disabling fit failed.')


    def remove_fit(self, p_FitDataInfo):
        try:
            self.ddMain.removeFit(p_FitDataInfo)
            self.ddMain.refresh()
            self.tabFits.removeFit(p_FitDataInfo.get_fit_index())
        except:
            self.set_display_msg('Removing fit failed.')

    def PostFit(self, msg, current_fdi, combined_fit_data):
        #  #, fic_index):
        #
        if msg == fdi.fitDataInfo.SUCCESS:

            # self.ddMain.resetFits()
            # self.ddMain.addFit(current_fdi, index

            self.ddMain.update_fit(current_fdi)
            self.ddMain.update_combined_fit_data(combined_fit_data)
            self.ddMain.refresh()
        else:
            QMessageBox.information(self, "Fit failed", msg, QMessageBox.Ok, QMessageBox.Ok)

    def Combined_Fit_Data_Updated(self, combined_fit_data):
        self.ddMain.update_combined_fit_data(combined_fit_data)
        self.ddMain.refresh()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec_())
