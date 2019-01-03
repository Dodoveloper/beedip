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
from PyQt5.QtCore import QSettings, QTranslator, qVersion, QCoreApplication, Qt
from PyQt5.QtGui import QIcon, QColor, QCursor
from PyQt5.QtWidgets import *
from qgis.core import *
from qgis.gui import QgsMapTool, QgsMapToolPan, QgsRubberBand, QgsMapToolExtent, QgsMessageBar, QgsMapToolEmitPoint
# Initialize Qt resources from file resources.py
from .resources import *
# Import the code for the dialog
from .beedip_dockwidget import BeeDipDockWidget
import os.path


class BeeDip:
    """QGIS Plugin Implementation."""

    input_filename = None
    output_filename = None
    # raster fence parameters
    point_tool = None
    canvas = None
    polyline = None
    ux, uy = "0.0", "0.0" # top-left point
    lx, ly = "0.0", "0.0" # bottom-right point

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

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&BeeDip')
        # TODO: We are going to let the user set this up in a future iteration
        self.toolbar = self.iface.addToolBar(u'BeeDip')
        self.toolbar.setObjectName(u'BeeDip')

        #print "** INITIALIZING BeeDip"

        self.pluginIsActive = False
        self.dockwidget = None


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
            text=self.tr(u'Official Beedip plugin'),
            callback=self.run,
            parent=self.iface.mainWindow())


    def select_output_file(self):
        t = QFileDialog.getSaveFileName(self.dockwidget, "Select output file ", "", "*.gpkg")
        file_extension = t[1].replace("*", "")
        self.output_filename = t[0]
        self.dockwidget.lineEdit.setText(self.output_filename)

    def select_input_file(self):
        t = QFileDialog.getOpenFileName(self.dockwidget, "Select input file ", "", "*.gpkg")
        file_extension = t[1].replace("*", "")
        self.input_filename = t[0]
        self.dockwidget.lineEdit_2.setText(self.input_filename)

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
        # co = ["APPEND_SUBDATASET=YES", "RASTER_TABLE=new_table"]
        output_ds = gdal.Translate(self.output_filename, input_ds)#, creationOptions=co)
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
        # get the selected layers
        layers = self.iface.layerTreeView().selectedLayers()

        if len(layers) == 0:
            err = QMessageBox.critical(None, "Error", "No layer selected.")
            return

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
                layer.saveStyleToDatabase("%s_style" % layer.name(), "", False, "")

        self.iface.messageBar().pushSuccess("Success", "Layers correctly exported.")

    def import_layers(self):
        import sqlite3

        has_raster = False
        has_vector = False

        # check input file existence
        if not self.input_filename:
            error_dialog = QMessageBox.critical(None, "Error", "File not found.")
            return
        elif not os.path.exists(self.input_filename):
            error_dialog = QMessageBox.critical(None, "Error", "File not found.")
            return
        # open the db
        connection = sqlite3.connect(self.input_filename)
        c = connection.cursor()
        # check if a vector is present
        try:
            rows = c.execute("select * from gpkg_contents where data_type != \"tiles\"").fetchall()
            if len(rows) > 0:
                has_vector = True
        except sqlite3.OperationalError:
            print("database has no vector")
        # check if a raster is present
        try:
            rows = c.execute("select * from gpkg_tile_matrix").fetchall()
            if len(rows) > 0:
                has_raster = True
        except sqlite3.OperationalError:
            print("database has no raster")
        # close the db
        c.close()

        try:
            if has_raster:
                layer = self.iface.addRasterLayer(self.input_filename, "imported raster")
            if has_vector:
                layer = self.iface.addVectorLayer(self.input_filename, "imported", "ogr")
        except Exception as e:
            self.iface.messageBar().pushCritical("Error", "Could not import GeoPackage.")
        finally:
            self.iface.messageBar().pushSuccess("Success", "GeoPackage correctly imported.")

    #--------------------------------------------------------------------------

    def onClosePlugin(self):
        """Cleanup necessary items here when plugin dockwidget is closed"""

        #print "** CLOSING BeeDip"

        # disconnects
        self.dockwidget.closingPlugin.disconnect(self.onClosePlugin)
        if self.point_tool:
            self.point_tool.deactivate()
        # remove this statement if dockwidget is to remain
        # for reuse if plugin is reopened

        self.pluginIsActive = False

    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""

        #print "** UNLOAD BeeDip"

        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(u'&BeeDip'),
                action)
            self.iface.removeToolBarIcon(action)
        # remove the toolbar
        del self.toolbar

    #--------------------------------------------------------------------------

    def run(self):
        """Run method that loads and starts the plugin"""

        if not self.pluginIsActive:
            self.pluginIsActive = True

            #print "** STARTING BeeDip"
            self.import_svg()
            self.canvas = self.iface.mapCanvas()

            # dockwidget may not exist if:
            #    first run of plugin
            #    removed on close (see self.onClosePlugin method)
            if self.dockwidget == None:
                # Create the dockwidget (after translation) and keep reference
                self.dockwidget = BeeDipDockWidget()
                # call select_output_file on click
                self.dockwidget.lineEdit.clear()
                self.dockwidget.pushButton.clicked.connect(self.select_output_file)
                # call select_input_file on click
                self.dockwidget.lineEdit.clear()
                self.dockwidget.pushButton_2.clicked.connect(self.select_input_file)
                # connect the ok button
                self.dockwidget.exportBbox.accepted.connect(self.export_layers)
                self.dockwidget.importBbox.accepted.connect(self.import_layers)
                # connect the other buttons
                self.dockwidget.rasterStartBtn.clicked.connect(self.start_fence)
                self.dockwidget.rasterConfirmBtn.clicked.connect(self.fence_raster)
                self.dockwidget.vectorStartBtn.clicked.connect(self.start_fence)
                self.dockwidget.vectorConfirmBtn.clicked.connect(self.fence_vector)

            # connect to provide cleanup on closing of dockwidget
            self.dockwidget.closingPlugin.connect(self.onClosePlugin)

            # show the dockwidget
            # TODO: fix to allow choice of dock location
            self.iface.addDockWidget(Qt.BottomDockWidgetArea, self.dockwidget)
            self.dockwidget.show()

    def start_fence(self):
        # prompt the user to select a fence
        # start tracking mouse click
        self.point_tool = MyMapTool(self.canvas)
        self.canvas.setMapTool(self.point_tool)

    def fence_raster(self):
        import gdal, tempfile

        ux, uy = self.point_tool.ux, self.point_tool.uy
        lx, ly = self.point_tool.lx, self.point_tool.ly
        output_dir = tempfile.gettempdir()

        if self.point_tool.ux == self.point_tool.lx:
            print("no selection")
            return
        # display coordinates
        self.dockwidget.rasterUL.setText(self.point_tool.point1.toString())
        self.dockwidget.rasterLR.setText(self.point_tool.point2.toString())
        # get the selected layer(s)
        layer = self.canvas.currentLayer()
        if layer == None:
            err = QMessageBox.critical(None, "Error", "No layer selected")
        elif layer.type() == QgsMapLayer.RasterLayer:
            # clip the raster and save it on a temporary folder
            filename = layer.source()
            layername = "clipped_" + layer.name() # clipped layer's name (in QGIS)
            output_dir = output_dir + "/" + layername + ".tif" # full output file path
            ds = gdal.Open(filename)
            ds = gdal.Translate(output_dir, ds, projWin = [ux, uy, lx, ly])
            ds = None
            # add it as a layer
            self.iface.addRasterLayer(output_dir, layername)
            # show message
            self.iface.messageBar().pushSuccess("Success", "Raster layer correctly clipped.")
            # deactivate custom maptool
            self.point_tool.deactivate()
        else:
            warn = QMessageBox.warning(None, "Warning", "The selected layer is not a raster.")

    def fence_vector(self):
        point1 = self.point_tool.point1
        point2 = self.point_tool.point2
        layers = []

        # check selection
        if self.point_tool.ux == self.point_tool.lx:
            print("no selection")
            return
        # display coordinates
        self.dockwidget.vectorUL.setText(self.point_tool.point1.toString())
        self.dockwidget.vectorLR.setText(self.point_tool.point2.toString())
        # build a QgsRectangle
        rect = QgsRectangle(point1, point2)
        # get all project layers
        layer = self.iface.activeLayer()
        # check if there are features inside the rectangle
        if layer == None:
            err = QMessageBox.critical(None, "Error", "No layer selected")
        elif type(layer) is QgsVectorLayer:
            # select layer features on the map
            layer.selectByRect(rect)
            self.iface.messageBar().pushSuccess("Success", "Vector layer's fields correctly selected.")
        else:
            warn = QMessageBox.warning(None, "Warning", "The selected layer is not valid.")
        # deactivate custom maptool
        self.point_tool.deactivate()


class MyMapTool(QgsMapTool):
    point1, point2 = QgsPointXY(), QgsPointXY()
    ux, uy = 0.0, 0.0
    lx, ly = 0.0, 0.0
    polyline = None
    isFencing = False

    def __init__(self, canvas):
        QgsMapTool.__init__(self, canvas)
        self.canvas = canvas
        self.polyline = QgsRubberBand(self.canvas, False)  # False = not a polygon
        self.setCursor(Qt.CrossCursor) # not working

    def canvasPressEvent(self, event):
        # get the top right corner
        x = event.pos().x()
        y = event.pos().y()
        self.point1 = self.canvas.getCoordinateTransform().toMapCoordinates(x, y)
        self.ux = self.point1.x()
        self.uy = self.point1.y()
        self.isFencing = True

    def canvasMoveEvent(self, event):
        if not self.isFencing:
            return
        x = event.pos().x()
        y = event.pos().y()
        self.point2 = self.canvas.getCoordinateTransform().toMapCoordinates(x, y)
        self.lx = self.point2.x()
        self.ly = self.point2.y()
        self.drawRectangle()

    def canvasReleaseEvent(self, event):
        if not self.isFencing:
            return
        # get the click
        x = event.pos().x()
        y = event.pos().y()
        self.point2 = self.canvas.getCoordinateTransform().toMapCoordinates(x, y)
        # determine upper left and lower right points
        self.ux = min(self.point1.x(), self.point2.x())
        self.uy = max(self.point1.y(), self.point2.y())
        self.lx = max(self.point1.x(), self.point2.x())
        self.ly = min(self.point1.y(), self.point2.y())
        self.drawRectangle()
        self.isFencing = False

    def activate(self): # called when set as currently active map tool
        # print("custom tool activated")
        # clear drawings, if present
        if self.polyline != None:
            self.polyline = QgsRubberBand(self.canvas, False)
        # self.setCursor(QCursor(Qt.CrossCursor))

    def deactivate(self): # called when map tool is being deactivated
        # delete the drawn rectangle
        self.canvas.scene().removeItem(self.polyline)
        # reset class attributes
        self.ux, self.uy = 0.0, 0.0
        self.lx, self.ly = 0.0, 0.0

    def drawRectangle(self): # custom function
        # draw rectangle
        points = [QgsPoint(self.ux, self.ly), QgsPoint(self.ux, self.uy), QgsPoint(self.lx, self.uy), QgsPoint(self.lx, self.ly), QgsPoint(self.ux, self.ly)]
        self.polyline.setToGeometry(QgsGeometry.fromPolyline(points), None)
        self.polyline.setColor(QColor(255, 0, 0))
        self.polyline.setFillColor(QColor(0, 0, 255, 10)) # not working
        self.polyline.setWidth(2)
        self.polyline.show()
