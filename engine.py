#
# Copyright (c) 2013 Shotgun Software, Inc
# ----------------------------------------------------
#
"""
A Katana engine for Tank.
"""
import os
import sys
import ctypes
import shutil
import logging
import traceback

import tank
from Katana import Callbacks

class KatanaEngine(tank.platform.Engine):
    def init_engine(self):
        self.log_debug("%s: Initializing..." % self)
        self.katana_log=logging.getLogger("Shotgun Katana Engine")

    def _define_qt_base(self):
        """
        Override to return the PyQt4 modules as provided by Katana.
        
        :return:    Dictionary containing the qt core & gui modules as well as the
                    class to use for the base of all dialogs.
        """
        # proxy class used when QT does not exist on the system.
        # this will raise an exception when any QT code tries to use it
        class QTProxy(object):
            def __getattr__(self, name):
                raise tank.TankError("Looks like you are trying to run an App that uses a QT "
                                     "based UI, however the Katana engine could not find a PyQt "
                                     "installation!")

        base = {"qt_core": QTProxy(), "qt_gui": QTProxy(), "dialog_base": None}
    
        try:
            from PyQt4 import QtCore, QtGui
            import PyQt4
    
            # hot patch the library to make it work with pyside code
            QtCore.Signal = QtCore.pyqtSignal
            QtCore.Slot = QtCore.pyqtSlot
            QtCore.Property = QtCore.pyqtProperty
            base["qt_core"] = QtCore
            base["qt_gui"] = QtGui
            base["dialog_base"] = QtGui.QDialog
            self.log_debug("Successfully initialized PyQt '%s' located in %s."
                           % (QtCore.PYQT_VERSION_STR, PyQt4.__file__))
        except ImportError:
            pass
        except Exception, e:
            import traceback
            self.log_warning("Error setting up PyQt. PyQt based UI support "
                             "will not be available: %s" % e)
            self.log_debug(traceback.format_exc())    
            
        return base

    def add_katana_menu(self, objectHash):

        menu_name = "Shotgun"
        if self.get_setting("use_sgtk_as_menu_name", False):
            menu_name = "Sgtk"
        tk_katana = self.import_module("tk_katana")
        self.katana_log.info("Start creating shotgun menu.")
        try:
            self._menu_generator = tk_katana.MenuGenerator(self, menu_name)
            self._menu_generator.create_menu()
        except:
            traceback.print_exc()
            
    def post_app_init(self):
        Callbacks.addCallback(Callbacks.Type.onStartupComplete, self.add_katana_menu)

    def destroy_engine(self):
        self.log_debug("%s: Destroying..." % self)

    def _display_message(self, msg):
        self.log_info(msg)

    def launch_command(self, cmd_id):
        callback = self._callback_map.get(cmd_id)
        if callback is None:
            self.log_error("No callback found for id: %s" % cmd_id)
            return
        callback()

    def log_debug(self, msg):
        if self.get_setting("debug_logging", False):
            print "Shotgun Debug: %s" % msg

    def log_info(self, msg):
        print "Shotgun: %s" % msg

    def log_error(self, msg):
        self._display_message(msg)
        print "Shotgun Error: %s" % msg

    def log_warning(self, msg):
        print str(msg)
