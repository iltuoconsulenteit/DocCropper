__all__ = ["register"]

def register(app, utils):
    """Scanner acquisition plugin placeholder.

    This feature requires the DocCropper scanner helper to be installed on the
    client machine to communicate with local or network-connected scanners.
    The frontend contacts the helper via HTTP (default `http://127.0.0.1:28672`)
    to enumerate devices and trigger acquisitions. No backend hooks are needed.
    """
    pass
