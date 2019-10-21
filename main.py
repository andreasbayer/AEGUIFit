import sys
from PyQt5.QtWidgets import QApplication, QWidget, QMainWindow, QGridLayout, QMessageBox, QAction, QGroupBox, QFileDialog, QSizePolicy, QProgressBar, QLabel, QPushButton, QScrollArea, QFrame
import flSaveFileDialog as fsd

import dataDisplay as dd
import dataControlWidget as dcw
import fitDataInfo as fdi
import viewWidget as viw
import fitInfoWidgetContainer as fic
import displayToolbar as dt
import tabFits as tft
import metaInfoWidget as mdi
from numpy import empty

VERSION = "AEGUIFit 2.02"
ID_STRING = "AEGUIFit"

TITLE = VERSION + " - "


class App(QMainWindow):

    def __init__(self):
        super().__init__()
        self.title = TITLE
        self.left = 100
        self.top = 50
        self.width = 1280
        self.height = 900
        self.bottom = 155
        self.right = 300
        self.initUI()
        self.menuInit()

    def menuInit(self):
        self.mbrMain = self.menuBar()
        self.mnuFile = self.mbrMain.addMenu('File')
        self.mnuExport = self.mbrMain.addMenu('Export')
        # mnuConfig = self.mbrMain.addMenu('Configurations')
        #self.mnuConfig = self.mbrMain.addMenu('')
        self.mnuHelp = self.mbrMain.addMenu('Help')

        self.mbtOpen = QAction('Open...', self)
        self.mbtOpen.setShortcut('Ctrl+O')
        self.mbtOpen.setStatusTip('Open new file.')
        self.mbtOpen.triggered.connect(self.openFile)
        self.mnuFile.addAction(self.mbtOpen)

        self.mbtSave = QAction('Save', self)
        self.mbtSave.setStatusTip('Save all data with fit and fit parameters.')
        self.mbtSave.triggered.connect(self.saveFile)
        self.mbtSave.setShortcut('Ctrl+S')
        self.mnuFile.addAction(self.mbtSave)

        self.mbtSaveAs = QAction('Save As...', self)
        self.mbtSaveAs.setStatusTip('Save all data with fit and fit parameters as ...')
        self.mbtSaveAs.triggered.connect(self.saveFileAs)
        self.mnuFile.addAction(self.mbtSaveAs)

        self.mbtClose = QAction('Close', self)
        #self.mbtClose.setShortcut('Ctrl+C')
        self.mbtClose.setStatusTip('Close current file.')
        self.mbtClose.triggered.connect(self.closeFile)
        self.mnuFile.addAction(self.mbtClose)

        self.mnuFile.addSeparator()

        self.mbtQuit = QAction('Quit', self)
        self.mbtQuit.setShortcut('Ctrl+Q')
        self.mbtQuit.setStatusTip('Quit application.')
        self.mbtQuit.triggered.connect(self.close)
        self.mnuFile.addAction(self.mbtQuit)

        self.mbtSaveFig = QAction('Save Figure ...', self)
        self.mbtSaveFig.setShortcut('Ctrl+F')
        self.mbtSaveFig.setStatusTip('Save figure as is shown.')
        self.mbtSaveFig.triggered.connect(self.saveFig)
        self.mnuExport.addAction(self.mbtSaveFig)

        self.mbtExportAllData = QAction('Export All Data and Meta Data ...', self)
        self.mbtExportAllData.setShortcut('Ctrl+E')
        self.mbtExportAllData.setStatusTip('Export all data, errors, combined and individual fits, as well as their parameters and the engergy shift in a .txt file.')
        self.mbtExportAllData.triggered.connect(self.exportAllData)
        self.mnuExport.addAction(self.mbtExportAllData)
        self.mbtExportAllData.setVisible(False)

        self.mbtExportVisibleData = QAction('Export Visible Data Range...', self)
        self.mbtExportVisibleData.setShortcut('Ctrl+D')
        self.mbtExportVisibleData.setStatusTip('Export all visible data in a .txt file.')
        self.mbtExportVisibleData.triggered.connect(self.exportData)
        self.mnuExport.addAction(self.mbtExportVisibleData)

        self.mbtAbout = QAction('About', self)
        self.mbtAbout.setShortcut("F1")
        self.mbtAbout.setStatusTip('About this program')
        self.mbtAbout.triggered.connect(self.showAbout)
        self.mnuHelp.addAction(self.mbtAbout)

        self.resetMenuBar(False)

    def resetMenuBar(self, isLoaded):
        self.mnuExport.setDisabled(not isLoaded)
        self.mbtClose.setDisabled(not isLoaded)
        self.mbtSaveAs.setDisabled(not isLoaded)
        self.mbtSave.setDisabled(not (isLoaded and self.is_ae_file()))

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
        self.ddMain.is_loaded_changed.connect(self.dd_is_loaded_changed)

        self.horizontalGroupBox = QGroupBox("Grid")
        self.grid_layout = QGridLayout()
        # layout.setRowStretch(0, 50)
        # layout.setColumnStretch(0, 80)
        # layout.setRowStretch(1, 50)

        self.ficFits = fic.fitInfoWidgetContainer()
        self.dcwData = dcw.dataControlWidget()
        self.viwView = viw.viewWidget()
        self.mdiMeta = mdi.metaInfoWidget()
        
        self.ficFits.Post_Fit.connect(self.PostFit)  # self.ddMain.addFit(self.ficFits.getFitDataInfo())
        self.ficFits.Combined_Fit_Data_Updated.connect(self.Combined_Fit_Data_Updated)
        self.ficFits.progressUpdate.connect(self.progressUpdate)
        self.ficFits.disable_fit.connect(self.disable_fit)
        self.ficFits.remove_fit.connect(self.remove_fit)
        self.ficFits.setSizePolicy(QSizePolicy.Expanding,
                                   QSizePolicy.Expanding)

        self.dcwData.showErrorBars_changed.connect(self.showErrorBars_changed)
        self.dcwData.data_changed.connect(self.dcwData_changed)
        self.dcwData.data_shift.connect(self.ddMain.shiftData)
        #self.dcwData.data_shift.connect(self.ficFits.shiftData)
        self.dcwData.load_fits.connect(self.ficFits.load_fits)
        self.dcwData.load_view.connect(self.viwView.load_from_view_string)
        self.dcwData.load_meta.connect(self.mdiMeta.load_from_meta_string)

        self.dcwData.data_shift.connect(self.ficFits.shift_data)
        # has to be generalized for multiple fiw

        self.ficFits.zoom_to_fit.connect(self.zoom_to_fit)
        # generalize

        # self.viwView.lower_down.connect(self.)
        self.viwView.zoom_by_increment.connect(self.zoom_by_increment)
        self.viwView.scale_font_size_changed.connect(self.scale_font_size_changed)
        self.viwView.label_font_size_changed.connect(self.label_font_size_changed)
        self.viwView.fig_size_changed.connect(self.fig_size_changed)
        self.viwView.resizing_changed.connect(self.resizing_changed)
        self.viwView.annotation_changed.connect(self.annotation_changed)
        self.viwView.annotation_font_size_changed.connect(self.annotation_font_size_changed)
        self.viwView.setSizePolicy(QSizePolicy.Expanding,
                                   QSizePolicy.Expanding)

        self.tabFits = tft.tabFits()
        self.ficFits.fit_added.connect(self.tabFits.addFit)
        self.ficFits.fit_added.connect(self.ddMain.addFit)
        self.tabFits.fit_index_changed.connect(self.ddMain.fit_index_changed)

        self.ddScrollArea = QScrollArea(self)
        self.ddScrollArea.setWidgetResizable(True)
        self.ddScrollArea.setWidget(self.ddMain)

        self.ddGbox = QGridLayout()
        self.ddGbox.addWidget(self.tabFits)
        self.ddGbox.addWidget(self.ddScrollArea)
        self.dtToolbar = dt.displayToolbar(self.ddMain, self)
        self.dtToolbar.show_all.connect(self.zoom_show_all)
        self.ddGbox.addWidget(self.dtToolbar)

        self.grid_layout.addItem(self.ddGbox, 0, 0, 1, 2)
        self.grid_layout.addWidget(self.ficFits, 0, 2)
        self.grid_layout.addWidget(self.viwView, 1, 0)
        self.grid_layout.addWidget(self.mdiMeta, 1, 1)
        self.grid_layout.addWidget(self.dcwData, 1, 2)

        self.horizontalGroupBox.setLayout(self.grid_layout)

        mainWidget = QWidget(self)
        mainWidget.setLayout(self.grid_layout)
        self.setCentralWidget(mainWidget)

        self.show()

    def set_ae_file_flag(self, value):
        self._is_aefit_file = value

        if value is True:
            self.resetMenuBar(self.ddMain.isLoaded())
        else:
            self.title = self.title + '*'


    def is_ae_file(self):
        return self._is_aefit_file


    def set_dims(self):
        self.dcwData.setFixedHeight(self.bottom)
        self.viwView.setFixedHeight(self.bottom)
        self.mdiMeta.setFixedHeight(self.bottom)
        
        self.ficFits.setFixedWidth(self.right)
        self.dcwData.setFixedWidth(self.right)

    def resizeEvent(self, *args, **kwargs):
        self.set_dims()

    def progressUpdate(self, relation, p):
        self.progressBar.setValue(relation * 100)
        self.lblProgUpdate.setText("AE: " + str(round(p[1], 2)))

        # QMessageBox.information(self, "Pause", "", QMessageBox.Ok, QMessageBox.Ok)

    def showAbout(self):
        QMessageBox.information(self, "Info",
                                VERSION + "\n\n" +
                                "In case of unexpected behaviours, errors, crashes, improvements or general questions about the program, please feel free to send an e-mail to:\n\n" +
                                "andreas.bayer@uibk.ac.at",
                                QMessageBox.Ok, QMessageBox.Ok)

    def dd_statusbar_update(self, str_update):
        self.lblEnergyMark.setText(str_update)

    def dd_is_loaded_changed(self, is_loaded):
        self.resetMenuBar(is_loaded)

    def loadData(self, fileName):
        self.ddMain.DisableRefresh(True)
        self.set_ae_file_flag(self.dcwData.loadFile(fileName, ID_STRING))
        self.ddMain.ZoomShowAll()
        self.ddMain.DisableRefresh(False)
        self.ddMain.refresh()

        self.viwView.apply_all()

    def saveData(self, fileName):
        data_string = self.dcwData.get_data_string()
        view_string = self.viwView.get_view_string()
        fit_strings = self.ficFits.get_fit_strings()
        meta_string = self.mdiMeta.get_meta_string()
        print('savedata', meta_string)
        self.dcwData.saveFile(fileName, ID_STRING, fit_strings, view_string, data_string, meta_string)

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

            self.set_display_msg('')
        except:
            self.set_display_msg('Zooming failed.')

    def zoom_show_all(self):
        try:
            self.ddMain.ZoomShowAll()
            #self.ddMain.refresh()

            self.set_display_msg('')
        except:
            self.set_display_msg('Showing all failed.')

    def zoom_to_fit(self, lb, ub, fit_index):
        try:
            self.ddMain.ZoomToFit(lb, ub, fit_index)
            #self.ddMain.refresh()

            self.set_display_msg('')
        except:
            self.set_display_msg('Zoom to fit failed.')

    def scale_font_size_changed(self, value):
        try:
            self.ddMain.set_scale_font_size(value)
            self.ddMain.refresh()

            self.set_display_msg('')
        except:
            self.set_display_msg('Changing scale font size failed.')
            
    def label_font_size_changed(self, value):
        try:
            self.ddMain.set_label_font_size(value)
            self.ddMain.refresh()

            self.set_display_msg('')
        except:
            self.set_display_msg('Changing label font failed.')

    def fig_size_changed(self, new_fig_size):
        try:
            self.ddMain.set_fig_size(new_fig_size)
            #self.ddMain.refresh()
            self.ddMain.draw()

            self.set_display_msg('')
        except:
            self.set_display_msg('changing figure size failed.')

    def resizing_changed(self, enabled):
        try:
            self.ddMain.setResizingEnabled(enabled)
            self.set_display_msg('')
        except:
            self.set_display_msg('changing resizing failed.')

    def annotation_changed(self, annotation):
        try:
            self.ddMain.set_annotation(annotation)
            self.ddMain.refresh()
            self.set_display_msg('')
        except:
            self.set_display_msg('Setting annotation failed.')

    def annotation_font_size_changed(self, value):
        try:
            self.ddMain.set_annotation_font_size(value)
            self.ddMain.refresh()
            self.set_display_msg('')
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
        fitData = self.ddMain.getCurrentFitData()
        data = self.ddMain.getCurrentData()

        file = open(filename, "w+")
        for i in range(0, len(data)):
            if includeMeausredData:
                if fitData is not None:
                    file.write(
                        "%f\t%f\t%f\r\n" % (data[i][0], fitData[i][1], data[i][1]))
                else:
                    file.write(
                        "%f\t%f\r\n" % (data[i][0], data[i][1]))
            else:
                if fitData is not None:
                    file.write("%f\t%f\r\n" % (data[i][0], fitData[i][1]))
                else:
                    file.write("%f\t\r\n" % (data[i][0]))
        file.close()


    def writeAllDataToFile(self, filename):
        file = open(filename, "w+")

        data = self.ddMain.getAllData()
        errors = self.ddMain.getStdErrors()
        all_fit_data = self.ddMain.getAllFitData(incl_disabled=False)
        combined_fit = self.ddMain.getCombinedFitData()

        self.writeMetaData(file)

        write_errors = len(errors) > 0
        write_afd = len(all_fit_data) > 0
        write_combined_fit = len(combined_fit) > 0

        file.write('Energy\tCounts')

        if write_errors:
            file.write('\tErrors')

        if write_combined_fit:
            file.write('\tCombined Fit')

        if write_afd:
            for i in range(0, len(all_fit_data)):
                file.write('\tFit ' + str(i + 1))

        file.write('\r\n')

        for i in range(0, len(data)):
            file.write('%f\t' % data[i][0])
            file.write('%f\t' % data[i][1])

            if write_errors:
                file.write('%f\t' % errors[i])

            if write_combined_fit:
                file.write('%f' % combined_fit[i][1])

            if write_afd:
                for fit_data in all_fit_data:
                    file.write('\t%f' % fit_data[i][1])

            file.write('\r\n')

        file.close()

    def writeMetaData(self, file):

        file.write('# Energy shift = ' + str(self.dcwData.getEnergyShift()) + '\r\n')

        fits = self.ficFits.get_fit_info_widgets()

        for fiwFit in fits:
            if not fiwFit.isDisabled():
                file.write('# ' + fiwFit.getFitDataInfo().get_meta_string() + '\r\n')

        file.write('# -------------------------------------------------------------\r\n')

    def exportData(self):
        saveDialog = fsd.flSaveFileDialog()

        # name, ext = fsd.flSaveFileDialog.getSaveFileName(self, "Save Fit Data", "", "*.txt")
        name, ext = saveDialog.getSaveFileName(self, "Export Visible Data", "", "*.txt")

        if name != '':

            #msgBox = QMessageBox()
            #msgBox.setIcon(QMessageBox.Question)
            #msgBox.setWindowTitle('Include measurement data?')
            #msgBox.setText('Would you like to include measurement data as well?')
            #msgBox.addButton(QPushButton('Include measurement data'), QMessageBox.YesRole)
            #msgBox.addButton(QPushButton('Write only fit data'), QMessageBox.NoRole)
            #msgBox.addButton(QPushButton('Cancel'), QMessageBox.RejectRole)
            #ret = msgBox.exec_()

            #if ret != QMessageBox.DestructiveRole:
            #    try:
            #        if ret == QMessageBox.AcceptRole:
            #            #   QMessageBox.information(self, "", "With M-Data", QMessageBox.Ok, QMessageBox.Ok)
            #            self.writeFitDataToFile(name, includeMeausredData=True)
            #        else:
            #            #    QMessageBox.information(self, "", "Without M-Data", QMessageBox.Ok, QMessageBox.Ok)
            #            self.writeFitDataToFile(name, includeMeausredData=False)
            #
            #        self.set_display_msg('Exporting data was successful.')
            #    except:
            #        QMessageBox.critical(self, "Exporting data failed!", "Please contact developers for further information.",
            #                             QMessageBox.Ok, QMessageBox.Ok)

            try:
                #   QMessageBox.information(self, "", "With M-Data", QMessageBox.Ok, QMessageBox.Ok)
                self.writeFitDataToFile(name, includeMeausredData=True)
                self.set_display_msg('Exporting data was successful.')
            except:
                QMessageBox.critical(self, "Exporting data failed!", "Please contact developers for further information.",
                                     QMessageBox.Ok, QMessageBox.Ok)


    def exportAllData(self):
        saveDialog = fsd.flSaveFileDialog()

        # name, ext = fsd.flSaveFileDialog.getSaveFileName(self, "Save Fit Data", "", "*.txt")
        name, ext = saveDialog.getSaveFileName(self, "Export All Data", "", "*.txt")

        try:
            self.writeAllDataToFile(name)

            self.set_display_msg('Exporting All Data was successful.')
        except Exception as e:
            print(e)
            QMessageBox.critical(self, "Exporting all data failed!", "Please contact developers for further information.",
                                 QMessageBox.Ok, QMessageBox.Ok)

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
                self.fileName = fileName
            except Exception as e:
                print(e)
                self.reset(False)
                QMessageBox.critical(self, "Open file failed!", "Error while opening " + fileName, QMessageBox.Ok,
                                     QMessageBox.Ok)

                self.setWindowTitle(TITLE)
                self.fileName = ""

    def saveFileAs(self):
        saveDialog = fsd.flSaveFileDialog()
    
        # name, ext = fsd.flSaveFileDialog.getSaveFileName(self, "Save Fit Data", "", "*.txt")
        fileName, ext = saveDialog.getSaveFileName(self, "Save File", "", "*.txt")

        if fileName is not '':  # todo check file validity
            try:
                self.saveData(fileName)
                self.set_ae_file_flag(True)

                self.setWindowTitle(TITLE + fileName)
                self.fileName = fileName

                self.set_display_msg('File was saved successfully .')
            except:
                QMessageBox.critical(self, "Saving file failed!", "Error while saving " + fileName, QMessageBox.Ok,
                                     QMessageBox.Ok)
                self.set_ae_file_flag(False)

    def saveFile(self):
        # name, ext = fsd.flSaveFileDialog.getSaveFileName(self, "Save Fit Data", "", "*.txt")
        #fileName, ext = saveDialog.getSaveFileName(self, "Save File", "", "*.txt")

        if self.fileName is not '' and self.is_ae_file():  # todo check file validity
            try:
                self.saveData(self.fileName)

                self.set_display_msg('File was quick saved successfully.')
            except:
                QMessageBox.critical(self, "Saving file failed!", "Error while saving " + self.fileName, QMessageBox.Ok,
                                     QMessageBox.Ok)

    def closeFile(self):
        self.reset(enable=False)

    def reset(self, enable):
        self.set_ae_file_flag(False)
        self.ddMain.DisableRefresh(True)
        self.ficFits.reset(enable)
        self.dcwData.reset(enable)
        self.ddMain.reset()
        self.tabFits.reset()
        self.viwView.reset(enable)
        self.mdiMeta.reset(enable)
        self.dtToolbar.reset(enable)
        self.resetMenuBar(self.ddMain.isLoaded())
        self.progressBar.reset()

        self.ddMain.DisableRefresh(False)
        self.ddMain.draw()

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

            self.set_display_msg('')
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
            self.ddMain.ZoomShowAll()
        else:
            QMessageBox.information(self, "Fit failed", msg, QMessageBox.Ok, QMessageBox.Ok)

    def Combined_Fit_Data_Updated(self, combined_fit_data):
        self.ddMain.update_combined_fit_data(combined_fit_data)
        self.ddMain.refresh()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec_())
