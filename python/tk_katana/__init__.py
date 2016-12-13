#
# Copyright (c) 2013 Shotgun Software, Inc
# ----------------------------------------------------
#
import os
import sys
import tank
import traceback

from Katana import Configuration
from Katana import FarmAPI 
from Katana import Callbacks
from Katana import QtGui, QtCore

from .menu_generation import MenuGenerator


def __show_tank_message(title, msg):
    """
    Display a message in a dialog.
    """
    QtGui.QMessageBox.information(None, title, msg)


def __show_tank_disabled_message(details):
    """
    Message when user clicks the "Toolkit is disabled" menu
    """
    msg = ("Shotgun integration is currently disabled because the file you "
           "have opened is not recognized. Shotgun cannot "
           "determine which Context the currently open file belongs to. "
           "In order to enable the Shotgun functionality, try opening another "
           "file. <br><br><i>Details:</i> %s" % details)
    __show_tank_message("Shotgun Pipeline Toolkit is disabled", msg)


def __create_tank_disabled_menu(details):
    """
    Creates a std "disabled" shotgun menu
    """
    if Configuration.get("KATANA_UI_MODE"):
        sg_menu = MenuGenerator.get_or_create_root_menu("Shotgun")
        if sg_menu is not None:
            sg_menu.clear()
            cmd = lambda d=details: __show_tank_disabled_message(d)
            action = QtGui.QAction("Toolkit is disabled", sg_menu, triggered=cmd)
            sg_menu.addAction(action)
    else:
        print("The Shotgun Pipeline Toolkit is disabled: %s" % details)


def __create_tank_error_menu():
    """
    Creates a std "error" tank menu and grabs the current context.
    Make sure that this is called from inside an except clause.
    """
    (exc_type, exc_value, exc_traceback) = sys.exc_info()
    message = ""
    message += "Message: Shotgun encountered a problem starting the Engine.\n"
    message += "Please contact support@shotgunsoftware.com\n\n"
    message += "Exception: %s - %s\n" % (exc_type, exc_value)
    message += "Traceback (most recent call last):\n"
    message += "\n".join( traceback.format_tb(exc_traceback))

    if Configuration.get("KATANA_UI_MODE"):
        sg_menu = MenuGenerator.get_or_create_root_menu("Shotgun")
        if sg_menu is not None:
            sg_menu.clear()
            cmd = lambda m=message: __show_tank_message("Shotgun Pipeline Toolkit caught an error", m)
            action = QtGui.QAction("[Shotgun Error - Click for details]", sg_menu, triggered=cmd)
            sg_menu.addAction(action)
    else:
        print("The Shotgun Pipeline Toolkit caught an error: %s" % message)

