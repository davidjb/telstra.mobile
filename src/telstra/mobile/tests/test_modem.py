import unittest

from gsmmodem import modem 
from gsmmodem.exceptions import TimeoutException
from serial import SerialException


def dummy_modem_cls(connect_raises=None, valid_ports=None):
    """ Define a dummy modem class that will quack like the duck we want it to.
    
    connect_raises: Force an innovcation of ``connect()`` to raise the given exception.
    valid_ports: A list of valid ports the dummy modem should accept. The ``connect_raises``
                 exception will be raised if the port is invalid.
    """
    class DummyModem(object):

        _connect_raises = connect_raises
        _valid_ports = valid_ports

        def __init__(self, port, *args, **kwargs):
           self.port = port
           self.args = args
           self.kwargs = kwargs

        def connect(self):
            if (valid_ports is not None and self.port not in valid_ports):
                raise connect_raises()

    return DummyModem


def dummy_enumerate_ports(ports):
    """ Mock out port enumeration. Return the given object directly.
    """
    def enumerate():
        return ports
    return enumerate 


class TestModem(unittest.TestCase):

    def test_autodetect_nothing(self):
        """ Test a system with no modems connected.
        """
        from telstra.mobile import modem
        modem.GsmModem = dummy_modem_cls()
        modem.enumerate_serial = dummy_enumerate_ports([])
        self.assertIsNone(modem.autodetect_modem())

    def test_autodetect_modem(self):
        """ Test basic modem autodetection.
        """
        from telstra.mobile import modem
        modem.GsmModem = dummy_modem_cls()
        modem.enumerate_serial = dummy_enumerate_ports(['/dev/ttyS0'])

        result = modem.autodetect_modem()
        self.assertEqual(result.port, '/dev/ttyS0')
        self.assertEqual(result.args, ()) 
        self.assertEqual(result.kwargs, {'baudrate': 9600})

    def test_autodetect_modem_exception(self):
        """ Test a system with multiple ports.
        """
        from telstra.mobile import modem
        modem.enumerate_serial = dummy_enumerate_ports(['/dev/ttyS0',
                                                        '/dev/ttyS1',
                                                        '/dev/ttyS2'])

        # Test a communication timeout
        modem.GsmModem = dummy_modem_cls(connect_raises=TimeoutException,
                                         valid_ports=['/dev/ttyS1'])

        result = modem.autodetect_modem()
        self.assertEqual(result.port, '/dev/ttyS1')

        #Test an incorrect serial connection
        modem.GsmModem = dummy_modem_cls(connect_raises=SerialException,
                                         valid_ports=['/dev/ttyS2'])

        result = modem.autodetect_modem()
        self.assertEqual(result.port, '/dev/ttyS2')
