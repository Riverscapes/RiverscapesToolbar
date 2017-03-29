import os

######################### REMOTE DEBUG #########################
def InitDebug():
    if 'DEBUG_PLUGIN' in os.environ and os.environ['DEBUG_PLUGIN'] == "RiverscapesToolbar":
        import pydevd
        pydevd.settrace('localhost', port=53100, stdoutToServer=True, stderrToServer=True, suspend=False)
######################### /REMOTE DEBUG #########################