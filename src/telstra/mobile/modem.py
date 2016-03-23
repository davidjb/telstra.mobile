import logging
from serialenum import enumerate as enumerate_serial
from gsmmodem.modem import GsmModem
from gsmmodem.exceptions import TimeoutException
from serial import SerialException

log = logging.getLogger(__name__)


def autodetect_modem(pin=None, check_fn=None, modem_options={'baudrate': 9600}):
    """ Autodetect a suitable cellular modem connected to the system.

    :param pin: Security PIN to unlock the SIM.
    :param check_cn: Callable that should take a single ``modem`` argument
        and return True if the modem instance is suitable.
    :param modem_options: Structure to pass as keyword arguments to
        ``GsmModem`` initialisation.
    :type modem_options: dict-like
    :returns: Connected modem instance
    :rtype: :class:`gsmmodem.modem.GsmModem`

    This method will iterate through all potential serial ports on the system
    and attempt to ``connect()`` to each of them in turn.  The first serial
    port that connects successfully, and passes the ``check_fn(modem)`` call
    (if ``check_fn`` is specified), will be returned.

    All other unsuccessful connections will be closed during the process.

    This method will return ``None`` if no modems could be detected.
    """
    ports = enumerate_serial()
    if not ports:
        log.error('No modem ports detected on system.')
        return

    modem = None

    for port in ports:
        modem = GsmModem(port, **modem_options)
        try:
            log.debug('Attempting to connect to modem at %s' % port)
            modem.connect(pin=pin)
            if not check_fn or check_fn and check_fn(modem):
                log.debug('Successfully detected modem at %s' % port)
                return modem
        except SerialException:
            log.warn('Serial communication problem for port %s' % port)
        except TimeoutException:
            log.warn('Timeout detected on port %s' % port)

        log.debug('Closing modem at %s' % port)
        modem.close()

