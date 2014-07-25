
def dummy_enumerate_ports(ports):
    """ Mock out port enumeration. Return the given object directly.
    """
    def enumerate():
        return ports
    return enumerate


def dummy_modem_cls(connect_raises=None, valid_ports=None):
    """ Define a dummy modem class that will quack like the duck we want it to.

    connect_raises: Force an innovcation of ``connect()`` to raise the given
        exception.
    valid_ports: A list of valid ports the dummy modem should accept. The
        ``connect_raises`` exception will be raised if the port is invalid.
    """
    class DummyModem(object):

        _connect_raises = connect_raises
        _valid_ports = valid_ports

        def __init__(self, port, *args, **kwargs):
            self.port = port
            self.args = args
            self.kwargs = kwargs

        def connect(self, pin=None):
            if (valid_ports is not None and self.port not in valid_ports):
                raise connect_raises()

        def close(self):
            self.closed = True

    return DummyModem
