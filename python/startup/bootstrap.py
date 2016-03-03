# Copyright (c) 2016 Shotgun Software Inc.
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Shotgun Software Inc.

import os
import sys

def bootstrap(engine_name, context, app_path, app_args, extra_args):
    """
    Setup the environment for Katana
    """
    import sgtk

    # pull the path to "{engine}/resources/Katana"
    engine_path = sgtk.platform.get_engine_path(engine_name, context.sgtk, context)
    startup_path = os.path.join(engine_path, "resources", "Katana")

    # add to the katana startup env
    sgtk.util.append_path_to_env_var("KATANA_RESOURCES", startup_path)
    return (app_path, app_args)