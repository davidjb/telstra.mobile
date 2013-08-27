import logging
import serialenum
from gsmmodem.modem import GsmModem
from gsmmodem.exceptions import TimeoutException
from serial import SerialException
logging.basicConfig(level=logging.DEBUG)



def autodetect_modem(check_fn=None, modem_options={'baudrate': 9600}):
    """ Autodetect a suitable cellular modem connected to the system.

    :param check_cn: Callable that should take a single ``modem`` argument
        and return True if the modem instance is suitable.
    :param modem_options: Structure to pass as keyword arguments to ``GsmModem``
        initialisation.
    :type modem_options: dict-like
    :returns: Connected modem instance
    :rtype: :class:`gsmmodem.modem.GsmModem`

    This method will iterate through all potential serial ports on the system
    and attempt to ``connect()`` to each of them in turn.  The first serial
    port that connects successfully, and passes the ``check_fn(modem)`` call
    (if ``check_fn`` is specified), will be returned.

    All other unsuccessful connections will be closed during the process.
    """
    ports = serialenum.enumerate()
    modem = None

    for port in ports:
        modem = GsmModem(port, **modem_options)
        try:
            modem.connect()
            if check_fn and not check_fn(modem):
                modem.close()
                modem = None
                continue
            break
        except SerialException:
            pass
        except TimeoutException:
            pass

    return modem

