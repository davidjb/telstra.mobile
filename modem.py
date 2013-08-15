import logging
from gsmmodem.modem import GsmModem

logging.basicConfig(level=logging.DEBUG)

class Modem(GsmModem):
    """ Corrections and adjustments for our modem / country.
    """
    def _handleUssd(self, lines):
        """ Join mutli-line USSD responses back together and split.
        """
        fixed_lines = '\r\n'.join(lines)
        fixed_lines.split('+CUSD')
        return super(Modem, self)._handleUssd(fixed_lines)
