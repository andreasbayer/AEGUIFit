import sys
from PyQt5.QtWidgets import QApplication, QWidget, QMainWindow, QGridLayout, QMessageBox, QAction, QGroupBox, \
    QFileDialog, QSizePolicy, QProgressBar, QLabel, QPushButton, QVBoxLayout
import flSaveFileDialog as fsd

import dataDisplay as dd
import dataControlWidget as dcw
import fitDataInfo as fdi
import zoomButtonWidget as zbw
import fitInfoWidgetContainer as fic
import tabFits as tft
from numpy import empty

TITLE = "AEGUIFit - "

class App(QMainWindow):
    
    def __init__(self):
        super().__init__()
        self.title = TITLE
        self.left = 100
        self.top = 100
        self.width = 1280
        self.height = 900
        self.initUI()
        self.menuInit()
    
    def menuInit(self):
        mbrMain = self.menuBar()
        mnuFile = mbrMain.addMenu('File')
        mnuExport = mbrMain.addMenu('Export')
        #mnuConfig = mbrMain.addMenu('Configurations')
        mnuConfig = mbrMain.addMenu('')
        mnuHelp = mbrMain.addMenu('Help')
        
        mbtOpen = QAction('Open...', self)
        mbtOpen.setShortcut('Ctrl+O')
        mbtOpen.setStatusTip('Open new file')
        mbtOpen.triggered.connect(self.openFile)
        mnuFile.addAction(mbtOpen)

        mbtSave = QAction('Save...', self)
        mbtSave.setShortcut('Ctrl+S')
        mbtSave.setStatusTip('Save all data with fit and fit parameters')
        mbtSave.triggered.connect(self.saveFile)
        mnuFile.addAction(mbtSave)
        
        mnuFile.addSeparator()
        
        mbtQuit = QAction('Quit', self)
        mbtQuit.setShortcut('Ctrl+Q')
        mbtQuit.setStatusTip('Quit application')
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
        
        self.statusBar().showMessage('Click on figure to show energy value.')
        self.progressBar = QProgressBar()
        self.progressBar.setMinimum(0)
        self.progressBar.setMaximum(100)
        
        self.progressBar.setFixedWidth(200)
        
        self.statusBar().addPermanentWidget(self.progressBar)
        
        self.lblProgUpdate = QLabel("")
        self.statusBar().addPermanentWidget(self.lblProgUpdate)
        
        # This is simply to show the bar
        # self.progressBar.setGeometry(0,0,0,0)
        
        self.ddMain = dd.DataDisplay()
        self.ddMain.setSizePolicy(QSizePolicy.Expanding,
                                  QSizePolicy.Expanding)
        
        self.ddMain.statusbar_update.connect(self.dd_statusbar_update)
        
        self.horizontalGroupBox = QGroupBox("Grid")
        layout = QGridLayout()
        # layout.setRowStretch(0, 50)
        layout.setColumnStretch(0, 80)
        # layout.setRowStretch(1, 50)
        
        self.ficFits = fic.fitInfoWidgetContainer()
        self.ficFits.Post_Fit.connect(self.PostFit)  # self.ddMain.addFit(self.ficFits.getFitDataInfo())
        self.ficFits.Combined_Fit_Data_Updated.connect(self.Combined_Fit_Data_Updated)
        self.ficFits.progressUpdate.connect(self.progressUpdate)
        self.ficFits.disable_fit.connect(self.disable_fit)
        self.ficFits.remove_fit.connect(self.remove_fit)
        
        self.dcwData = dcw.dataControlWidget()
        self.dcwData.showErrorBars_changed.connect(self.showErrorBars_changed)
        self.dcwData.data_changed.connect(self.dcwData_changed)
        self.dcwData.data_shift.connect(self.ddMain.shiftData)
        self.dcwData.load_fits.connect(self.ficFits.load_fits)
        
        self.dcwData.data_shift.connect(self.ficFits.shift_data)
        #has to be generalized for multiple fiw
        
        self.ficFits.zoom_to_fit.connect(self.zoom_to_fit)
        #generalize
        
        self.zbwMain = zbw.ZoomButtonWidget()
        # self.zbwMain.lower_down.connect(self.)
        self.zbwMain.zoom_by_increment.connect(self.zoom_by_increment)
        self.zbwMain.show_all.connect(self.zoom_show_all)
        self.zbwMain.font_change.connect(self.font_change)
        self.zbwMain.fig_size_changed.connect(self.fig_size_changed)

        self.tabFits = tft.tabFits()
        self.ficFits.fit_added.connect(self.tabFits.addFit)
        self.ficFits.fit_added.connect(self.ddMain.addFit)
        self.tabFits.fit_index_changed.connect(self.ddMain.fit_index_changed)
        
        #change fit index after remove_fit, when and where and whos responsible for that anyway
        
        self.ddVbox = QVBoxLayout()
        self.ddVbox.addWidget(self.tabFits)
        self.ddVbox.addWidget(self.ddMain)
        
        layout.addItem(self.ddVbox, 0, 0)
        layout.addWidget(self.ficFits, 0, 1)
        layout.addWidget(self.zbwMain, 1, 0)
        layout.addWidget(self.dcwData, 1, 1)
        
        self.horizontalGroupBox.setLayout(layout)
        
        mainWidget = QWidget(self)
        mainWidget.setLayout(layout)
        self.setCentralWidget(mainWidget)
        
        self.show()
    
    def progressUpdate(self, relation, p):
        self.progressBar.setValue(relation * 100)
        self.lblProgUpdate.setText("AE: " + str(round(p[1],2)))

        #QMessageBox.information(self, "Pause", "", QMessageBox.Ok, QMessageBox.Ok)
        
        
    def showAbout(self):
        QMessageBox.information(self, "Info", "In case of unexpected behaviours, errors, crashes, improvements or general questions about the program, please feel free to send an e-mail to\nandreas.bayer@uibk.ac.at", QMessageBox.Ok, QMessageBox.Ok)
        
    
    def dd_statusbar_update(self, str_update):
        self.statusBar().showMessage(str_update)
    
    def loadData(self, fileName):
        self.dcwData.loadFile(fileName)
    
    def dcwData_changed(self, showErrorBars):
        data = self.dcwData.getData()
        self.ddMain.setData(data)
        self.ddMain.setStdErrors(self.dcwData.getStdErrors())
        self.ddMain.refresh()
        
        self.ficFits.setData(data)
        self.ficFits.setStdErr(self.dcwData.getStdErrors())
    
    def zoom_by_increment(self, bound, increment):
        self.ddMain.ZoomByIncrement(bound, increment)
        self.ddMain.refresh()
    
    def zoom_show_all(self):
        self.ddMain.ZoomShowAll()
        self.ddMain.refresh()
    
    def zoom_to_fit(self, lb, ub, index):
        self.ddMain.ZoomToFit(lb, ub, index)
        self.ddMain.refresh()

    def font_change(self, change):
        self.ddMain.font_change(change)
        self.ddMain.refresh()

    def fig_size_changed(self, new_fig_size):
        self.ddMain.increase_fig_size(new_fig_size)
        self.ddMain.refresh() #necessary?

    def saveFig(self):
        name, ext = QFileDialog.getSaveFileName(self, "Save Figure", "", "*.pdf;; *.png;; *.svg;; *.eps")
        
        if name != '':
            try:
                ext = ext.split('.')[-1]
                fig = self.ddMain.getFigure()
                fig.savefig(name, format=ext)
            except:
                QMessageBox.critical(self, "Saving figure failed!", "Error while saving figure", QMessageBox.Ok, QMessageBox.Ok)

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
        
        #name, ext = fsd.flSaveFileDialog.getSaveFileName(self, "Save Fit Data", "", "*.txt")
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
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getOpenFileName(self, "Open file", "", "Text Files (*.txt);;All Files (*)",
                                                  options=options)
        if fileName is not '':  # //!! check file validity
            try:
                self.reset(True)
                self.loadData(fileName)
                
                self.setWindowTitle(TITLE + fileName)
            except:
                self.reset(False)
                QMessageBox.critical(self, "Open file failed!", "Error while opening " + fileName, QMessageBox.Ok, QMessageBox.Ok)
                self.setWindowTitle(TITLE)
        #load fits
                
    def saveFile(self):
        saveDialog = fsd.flSaveFileDialog()

        #name, ext = fsd.flSaveFileDialog.getSaveFileName(self, "Save Fit Data", "", "*.txt")
        name, ext = saveDialog.getSaveFileName(self, "Save File", "", "*.txt")
    
    def reset(self, enable):
        self.ficFits.reset(enable)
        self.dcwData.reset(enable)
        self.ddMain.reset()
        self.tabFits.reset()
        
        self.zbwMain.setEnabled(enable)
        
        self.progressBar.reset()
    
    def showErrorBars_changed(self, showErrorBars):
        self.ddMain.refresh(showErrorBars=showErrorBars)
        
    def disable_fit(self, p_FitDataInfo):
        self.ddMain.refresh()
        
    def remove_fit(self, p_FitDataInfo):
        self.ddMain.removeFit(p_FitDataInfo)
        self.ddMain.refresh()
        self.tabFits.removeFit(p_FitDataInfo.get_fit_index())
    
    def PostFit(self, msg, current_fdi, combined_fit_data):
        #  #, fic_index):
        #
        if msg == fdi.fitDataInfo.SUCCESS:
            
            #self.ddMain.resetFits()
            #self.ddMain.addFit(current_fdi, index
            
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
