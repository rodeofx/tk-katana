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


def __engine_refresh(tk, new_context):
    """
    Checks the the tank engine should be
    """
    engine_name = os.environ.get("TANK_KATANA_ENGINE_INIT_NAME")

    curr_engine = tank.platform.current_engine()
    if curr_engine:
        # an old engine is running.
        if new_context == curr_engine.context:
            # no need to restart the engine!
            return
        else:
            # shut down the engine
            curr_engine.destroy()

    # try to create new engine
    try:
        tank.platform.start_engine(engine_name, tk, new_context)
    except tank.TankEngineInitError, e:
        # context was not sufficient! - disable tank!
        __create_tank_disabled_menu(e)


def __tank_on_scene_event_callback(**kwargs):
    """
    Callback that fires every time a file is saved or loaded.

    Carefully manage exceptions here so that a bug in Tank never
    interrupts the normal workflows in Katana.
    """
    # get the new file name
    file_name = FarmAPI.GetKatanaFileName()

    if not file_name:   # New scene
        return

    try:
        # this file could be in another project altogether, so create a new Tank
        # API instance.
        try:
            tk = tank.tank_from_path(file_name)
        except tank.TankError, e:
            __create_tank_disabled_menu(e)
            return

        # try to get current ctx and inherit its values if possible
        curr_ctx = None
        if tank.platform.current_engine():
            curr_ctx = tank.platform.current_engine().context

        # and now extract a new context based on the file
        new_ctx = tk.context_from_path(file_name, curr_ctx)

        # now restart the engine with the new context
        __engine_refresh(tk, new_ctx)
    except Exception, e:
        __create_tank_error_menu()


g_tank_callbacks_registered = False

def tank_ensure_callbacks_registered():
    """
    Make sure that we have callbacks tracking context state changes.
    """
    global g_tank_callbacks_registered
    if not g_tank_callbacks_registered:
        Callbacks.addCallback(Callbacks.Type.onSceneLoad, __tank_on_scene_event_callback) # onSceneAboutToLoad ?
        Callbacks.addCallback(Callbacks.Type.onSceneSave, __tank_on_scene_event_callback)
        g_tank_callbacks_registered = True
