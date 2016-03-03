# Copyright (c) 2015 The Foundry Visionmongers Ltd. All Rights Reserved.

from time import gmtime, strftime
import os
import sys
import getpass
import logging
import AssetAPI

# Shotgun - This should already be in the PYTHONPATH due to the init script.
import tank


# Set-up plug-in logger
#log = logging.getLogger('ShotgunAssetPlugin') # TODO


class ShotgunAssetPlugin(AssetAPI.BaseAssetPlugin):
    """
    The main class of the plug-in that will be registered as "Shotgun". It
    extends AssetAPI.BaseAssetPlugin to create an asset plug-in class and 
    implements all abstract functions from the plug-in interface. 
    """
    def __init__(self):
        # Create a Tank instance
        self.tk = None
        self.setupTank()


    def setupTank(self):
        '''
        This function relies on the TANK_CONTEXT environment var being previously
        set by Shotgun.
        '''
        context = None
        # Attempt to find context in environment
        if "TANK_CONTEXT" in os.environ:
            serialised_context = os.environ.get("TANK_CONTEXT")
            if serialised_context:
                context = tank.context.deserialize(serialised_context)
        if context:
            self.tk = context.tank


    def reset(self):
        """
        Resets the state of the plug-in
        """
        # Nothing to reset in this plug-in... If, for example, some caching was
        # implemented then this would be the place to clear it.
        pass


    def isAssetId(self, string): # TODO
        """
        Checks if the given string is a valid asset ID
        """
        # This is a very simplistic test... but it conveys the idea of this function
        fullDict = eval(str(string))
        if fullDict.has_key("template") and fullDict.has_key("fields"):
            return True
        return None


    def resolveAsset(self, assetId, throwOnError=False):
        """
        Lookups the given asset ID in Shotgun and returns the file path that it references
        """
        if assetId == "":
            return None

        if not self.isAssetId(assetId):
            # Return the assetId as it is if it is not recognized
            log.warning("resolveAsset: asset ID %s is not a valid asset. Skipping resolving asset." % assetId)
            return assetId

        # Get fields
        idFieldDict = self.getAssetFields(assetId)
        if not idFieldDict:
            log.warning("resolveAsset: Resolving asset path from asset ID failed: %s" % assetId)
            return None

        # Get template
        templateType = self.__getAssetPublishType(assetId)
        template = self.tk.templates[templateType]
        if not template:
            log.warning("resolveAsset: Unable to find template: %s" % templateType)

        assetFilePathList = self.tk.abstract_paths_from_template( template, idFieldDict )
        assetFilePath = ""
        if len(assetFilePathList) > 0:
            # (conversion from unicode to str needed)
            assetFilePath = str(assetFilePathList[0])
        return assetFilePath


    def resolveAllAssets(self, string):
        """
        For each asset ID found in the given string (isolated by whitespaces)
        it will be resolved and the original string will be substituted
        """
        result = string

        for token in string.split():
            if self.isAssetId(token):
                path = self.resolveAsset(token)
                result = result.replace(token, path)

        return result


    def resolvePath(self, assetId, frame):  # TODO -- This may need some work to work properly. How do Shotgun and Katana work with file sequences?
        """
        Resolves the given asset ID and if it comes as a file
        sequence then we will resolve that file sequence to the specified
        frame using the currently selected FileSequence plug-in
        """
        resolvedAsset = self.resolveAsset(assetId)
        if not resolvedAsset:
            return

        # Get the fileSequence plug-in and if the resolvedAsset is a file sequence
        # path, then use frame to resolve it
        fileSequencePlugin = AssetAPI.GetDefaultFileSequencePlugin()
        if fileSequencePlugin:
            if fileSequencePlugin.isFileSequence(resolvedAsset):
                # Get the FileSequence object and resolve the sequence with frame
                fileSequence = fileSequencePlugin.getFileSequence(resolvedAsset)
                resolvedAsset = fileSequence.getResolvedPath(frame)

        return resolvedAsset


    def resolveAssetVersion(self, assetId, versionTag = ""):
        """
        Returns the version for the given asset ID.
        If it is a partial asset ID (which doesn't have a version) then None is returned
        """
        # Get fields
        idFieldDict = self.getAssetFields(assetId)
        if not idFieldDict:
            log.warning("resolveAssetVersion: Resolving asset path from asset ID failed: %s" % assetId)
            return None
        # Version
        return idFieldDict.get("Version", None)


    def getAssetFields(self, assetId, includeDefaults=False):
        """
        Resolves an asset ID to a dict of all of the required fields.
        Returns a dict, keyed by the field names that the corresponding Shotgun template will expect
        """
        fullDict = eval(str(assetId)) # TODO: Not cool, but works in this case. Switch to json?
        fieldDict = fullDict.get("fields") or None
        if not fieldDict:
            log.warning("getAssetFields: Couldn't find fields in asset ID: %s" % assetId)
        return fieldDict


    def __getAssetPublishType(self, assetId):
        '''
        Returns the publish "type" of the asset. This is used to work out the Shotgun template to use.
        '''
        fullDict = eval(str(assetId)) # TODO: Not cool, but works in this case. Switch to json?
        templateType = fullDict.get("template") or None
        if not templateType:
            log.warning("getAssetFields: Couldn't find template type in asset ID: %s" % assetId)
        return templateType


    def createTransaction(self):
        """
        Creates a transaction object
        """
        # In this example plug-in we do not support transactions
        return None


# Register the "Shotgun" plug-in - this is the name that will be
# shown in Katana's Project Settings tab
AssetAPI.RegisterAssetPlugin("Shotgun", ShotgunAssetPlugin())

