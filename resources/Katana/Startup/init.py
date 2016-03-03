"""
Setup the envrionment and menu to run Shotgun tools.
"""
def bootstrap():
    import os

    try:
        import sgtk
    except Exception, e:
        print "Shotgun: Could not import sgtk! %s" % str(e)
        return

    if not "TANK_ENGINE" in os.environ:
        print "Shotgun: Missing required environment variable TANK_ENGINE."
        return

    engine_name = os.environ.get("TANK_ENGINE")
    try:
        context = sgtk.context.deserialize(os.environ.get("TANK_CONTEXT"))
    except Exception, e:
        print "Shotgun: Could not create context! %s" % str(e)
        return

    try:
        engine = sgtk.platform.start_engine(engine_name, context.sgtk, context)
    except Exception, e:
        print "Shotgun: Could not start engine: %s" % str(e)
        return

    # clean up temp env vars
    for var in ["TANK_ENGINE", "TANK_CONTEXT", "TANK_FILE_TO_OPEN"]:
        if var in os.environ:
            del os.environ[var]

bootstrap()
