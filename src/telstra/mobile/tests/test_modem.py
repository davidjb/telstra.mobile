import unittest

from gsmmodem.exceptions import TimeoutException
from serial import SerialException

from telstra.mobile.tests import dummy_modem_cls, dummy_enumerate_ports


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
