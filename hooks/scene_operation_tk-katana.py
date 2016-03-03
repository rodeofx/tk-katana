# By Sam Saxon sam.saxon@thefoundry.com
# Copied from the equivalent Nuke file.

import os
from Katana import KatanaFile

import tank
from tank import Hook
from tank import TankError
from tank.platform.qt import QtGui

# TODO: Should this be given a better name
import engine

class SceneOperation(Hook):
    """
    Hook called to perform an operation with the 
    current scene.
    """
    
    def execute(self, operation, file_path, context, parent_action, file_version, read_only, **kwargs):
        """
        Main hook entry point
        
        :param operation:       String
                                Scene operation to perform
        
        :param file_path:       String
                                File path to use if the operation
                                requires it (e.g. open)
                    
        :param context:         Context
                                The context the file operation is being
                                performed in.
                    
        :param parent_action:   This is the action that this scene operation is
                                being executed for.  This can be one of:
                                - open_file
                                - new_file
                                - save_file_as 
                                - version_up
                        
        :param file_version:    The version/revision of the file to be opened.  If this is 'None'
                                then the latest version should be opened.
        
        :param read_only:       Specifies if the file should be opened read-only or not
                            
        :returns:               Depends on operation:
                                'current_path' - Return the current scene
                                                 file path as a String
                                'reset'        - True if scene was reset to an empty 
                                                 state, otherwise False
                                all others     - None
        """
        
        if file_path:
            file_path = file_path.replace("/", os.path.sep)
        
        if operation == "current_path":
            # return the current script path
            return "/path/here".replace("/", os.path.sep) # TODO!!
        
        elif operation == "open":
            # open the specified script
            KatanaFile.Load(file_path)
            
        elif operation == "save":
            # save the current script:
            if not os.path.exists(os.path.dirname(file_path)):
                os.makedirs(os.path.dirname(file_path))
            KatanaFile.Save(file_path) # TODO: warning: this may not work...
            
        elif operation == "save_as":
            if not os.path.exists(os.path.dirname(file_path)):
                os.makedirs(os.path.dirname(file_path))
            KatanaFile.Save(file_path)   
            
        elif operation == "reset":
            """
            Reset the scene to an empty state
            """
            while KatanaFile.IsFileDirty():
                # Changes have been made to the scene
                res = QtGui.QMessageBox.question(None,
                                                 "Save your scene?",
                                                 "Your scene has unsaved changes. Save before proceeding?",
                                                 QtGui.QMessageBox.Yes|QtGui.QMessageBox.No|QtGui.QMessageBox.Cancel)
            
                if res == QtGui.QMessageBox.Cancel:
                    return False
                elif res == QtGui.QMessageBox.No:
                    break
                else:
                    if not os.path.exists(os.path.dirname(file_path)):
                        os.makedirs(os.path.dirname(file_path))
                    KatanaFile.Save(file_path) # TODO: warning: this may not work...
            return True

        # Create a new engine instance from the existing one, with the new context
        # Specify "shot_step" environment if the current context specifies a step
        if context.step:
            env = context.tank.pipeline_configuration.get_environment("shot_step", context=context) 
        # Otherwise, just get a "project" level context
        else:
            env = context.tank.pipeline_configuration.get_environment("project", context=context)

        name = "tk-katana" # TODO: Get this properly?
        new_katana_engine = engine.KatanaEngine(context.tank, context, name, env)
        new_katana_engine.add_katana_menu()


