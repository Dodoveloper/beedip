# -*- coding: utf-8 -*-
"""
/***************************************************************************
 BeeDip
                                 A QGIS plugin
 Export layers to a gpkg file
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                              -------------------
        begin                : 2018-07-14
        git sha              : $Format:%H$
        copyright            : (C) 2018 by DodoIta
        email                : davide.cor94@gmail.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
from PyQt5.QtCore import QSettings, QTranslator, qVersion, QCoreApplication
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QAction, QFileDialog, QMessageBox
from qgis.core import QgsApplication

# Initialize Qt resources from file resources.py
from .resources import *
# Import the code for the dialog
from .beedip_dialog import BeeDipDialog
import os.path


class BeeDip:
    # class parameters
    input_filename = None
    output_filename = None
    layers = []

    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        # Save reference to the QGIS interface
        self.iface = iface
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'BeeDip_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)

            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)

        # Create the dialog (after translation) and keep reference
        self.dlg = BeeDipDialog()

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&BeeDip')
        # TODO: We are going to let the user set this up in a future iteration
        self.toolbar = self.iface.addToolBar(u'BeeDip')
        self.toolbar.setObjectName(u'BeeDip')


    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('BeeDip', message)


    def add_action(
        self,
        icon_path,
        text,
        callback,
        enabled_flag=True,
        add_to_menu=True,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        parent=None):
        """Add a toolbar icon to the toolbar.

        :param icon_path: Path to the icon for this action. Can be a resource
            path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
        :type icon_path: str

        :param text: Text that should be shown in menu items for this action.
        :type text: str

        :param callback: Function to be called when the action is triggered.
        :type callback: function

        :param enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.
        :type enabled_flag: bool

        :param add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.
        :type add_to_menu: bool

        :param add_to_toolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.
        :type add_to_toolbar: bool

        :param status_tip: Optional text to show in a popup when mouse pointer
            hovers over the action.
        :type status_tip: str

        :param parent: Parent widget for the new action. Defaults None.
        :type parent: QWidget

        :param whats_this: Optional text to show in the status bar when the
            mouse pointer hovers over the action.

        :returns: The action that was created. Note that the action is also
            added to self.actions list.
        :rtype: QAction
        """

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            self.toolbar.addAction(action)

        if add_to_menu:
            self.iface.addPluginToMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_path = ':/plugins/beedip/icon.png'
        self.add_action(
            icon_path,
            text=self.tr(u'BeeDip'),
            callback=self.run,
            parent=self.iface.mainWindow())

        # call select_output_file on click
        self.dlg.lineEdit.clear()
        self.dlg.pushButton.clicked.connect(self.select_output_file)

        # call select_input_file on click
        self.dlg.lineEdit.clear()
        self.dlg.pushButton_2.clicked.connect(self.select_input_file)

        # add the layers to the combobox
        #self.add_layers()


    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(u'&BeeDip'),
                action)
            self.iface.removeToolBarIcon(action)
        # remove the toolbar
        del self.toolbar


    # def add_layers(self):
    #     from qgis.core import QgsProject, QgsLayerTree
    #
    #     self.dlg.lineEdit.clear()
    #     # get a list of all the layers in the project, except groups
    #     for layer in QgsProject.instance().layerTreeRoot().children():
    #         if QgsLayerTree.isGroup(layer):
    #             for child in layer.children():
    #                 self.layers.append(child)
    #         else:
    #             self.layers.append(layer)
    #     # add the layers to the combobox
    #     self.dlg.comboBox.addItems(layer.name() for layer in self.layers)

    def select_output_file(self):
        t = QFileDialog.getSaveFileName(self.dlg, "Select output file ", "", "*.gpkg")
        file_extension = t[1].replace("*", "")
        self.output_filename = t[0]# + file_extension
        self.dlg.lineEdit.setText(self.output_filename)

    def select_input_file(self):
        t = QFileDialog.getOpenFileName(self.dlg, "Select input file ", "", "*.gpkg")
        file_extension = t[1].replace("*", "")
        self.input_filename = t[0]
        self.dlg.lineEdit_2.setText(self.input_filename)

    def import_svg(self):
        from shutil import copyfile

        origin = os.path.join(self.plugin_dir, 'svg')
        destination = os.path.join(QgsApplication.qgisSettingsDirPath(), 'svg')
        if not os.path.exists(destination):
            os.makedirs(destination)
        for item in os.listdir(origin):
            s = os.path.join(origin,item)
            d = os.path.join(destination,item)
            if not os.path.lexists(d):  # if there's no broken symlink
                try:
                    copyfile(s,d)
                except IOError as e:
                    print("Unable to copy file. %s" % e)
        print('\nFile copy done!\n')

    def export_raster(self, layer):
        import gdal

        filename = layer.source()
        # check the selected layer
        format = filename.rstrip(".")[1]
        # open the file
        if not filename:
            return
        input_ds = gdal.Open(filename)
        # get the file format and the driver
        driver = gdal.GetDriverByName(format)
        # convert to gpkg
        output_ds = gdal.Translate(self.output_filename, input_ds)
        # close the datasets properly
        input_ds = None
        output_ds = None

    def export_vector(self, layer):
        from qgis.core import QgsVectorFileWriter

        crs = layer.crs()
        opt = QgsVectorFileWriter.SaveVectorOptions()
        opt.layerName = layer.name()
        opt.layerOptions = ["OVERWRITE=YES"]
        opt.actionOnExistingFile = QgsVectorFileWriter.CreateOrOverwriteLayer
        error = QgsVectorFileWriter.writeAsVectorFormat(layer, self.output_filename,
        options=opt)
        if error[0] == 0:
            print("Exported layer %s" % layer.name())
        else:
            print(error)

    def export_layers(self):
        from qgis.core import QgsRasterLayer, QgsVectorLayer

        # get the selected layers
        layers = self.iface.layerTreeView().selectedLayers()

        for layer in layers:
            print("Exporting layer %s" % layer.name())
            # check layer type
            if type(layer) is QgsRasterLayer:
                print("%s is a raster" % layer.name())
                self.export_raster(layer)
            elif type(layer) is QgsVectorLayer:
                print("%s is a vector" % layer.name())
                self.export_vector(layer)
            # save style to the database
            if self.dlg.checkBox.isChecked():
                print("Exporting style too.")
                layer.saveStyleToDatabase("%s_style" % layer.name(), "", False, "")

    def import_layers(self):
        import sqlite3

        has_raster = False
        has_vector = False

        # open the db
        connection = sqlite3.connect(self.input_filename)
        c = connection.cursor()
        # check if a raster is present
        rows = c.execute("select * from gpkg_tile_matrix").fetchall()
        if len(rows) > 0:
            has_raster = True
        # check if a vector is present
        rows = c.execute("select * from gpkg_contents where data_type != \"tiles\"").fetchall()
        if len(rows) > 0:
            has_vector = True
        # close the db
        c.close()

        if has_raster:
            layer = self.iface.addRasterLayer(self.input_filename, "imported raster")
        if has_vector:
            layer = self.iface.addVectorLayer(self.input_filename, "imported", "ogr")


    def run(self):
        """Run method that performs all the real work"""
        # show the dialog
        self.dlg.show()
        # Run the dialog event loop
        result = self.dlg.exec_()
        # See if OK was pressed
        if result:
            self.import_svg()
            # check current tab
            if self.dlg.tabWidget.currentIndex() == 0:
                self.export_layers()
            elif self.dlg.tabWidget.currentIndex() == 1:
                if os.path.exists(self.input_filename):
                    self.import_layers()
                else:
                    error_dialog = QMessageBox.critical(None, "Error", "File not found.")
