import datetime
import re
import logging
import serialenum
from gsmmodem.modem import GsmModem
from gsmmodem.exceptions import TimeoutException
from serial import SerialException

logging.basicConfig(level=logging.DEBUG)

class Modem(GsmModem):
    """ Corrections and adjustments for our modem / country.
    """
    def _handleUssd(self, lines):
        """ Join mutli-line USSD responses back together and split.
        """
        joined_lines = '\r\n'.join(lines)
	fixed_lines = re.findall('\+CUSD:\s*\d,".*?",\d+',
                                 joined_lines,
                                 re.DOTALL)
        return super(Modem, self)._handleUssd(fixed_lines)

class PrepaidAccount(object):

    def __init__(self, modem):
	self.modem = modem

    @classmethod
    def parse_menu(cls, ussd):
	""" Attempt to parse the menu options into a traversable structure.
	"""
	menu_items = ussd.message.split('\r\n')
	menu = {}
	for item in menu_items:
            item_details = re.match('(\d)\.\s+(.*)', item)
            if item_details:
		results = item_details.groups()
                menu[results[1]] = results[0]

	return menu

    def parse_main_menu(self):
	return self.parse_menu(self.main_menu())

    def main_menu(self):
	return self.modem.sendUssd('#100#')

    @property
    def phone_number(self):
        response = self.modem.sendUssd('#150#')
	return response.message.split('\r\n')[1]

    @property
    def balance(self):
        response = self.main_menu()
        response.cancel()
        balance = re.search('\$(.*?)\s', response.message)
        if balance:
            return float(balance.groups()[0])

    @property
    def expiry_date(self):
        response = self.main_menu()
        response.cancel()
        expiry = re.search('Exp.*?\s(.*?)\r\n', response.message)
        if expiry:
            return datetime.datetime.strptime(expiry.groups()[0], '%d %b %Y')

    def balance_plus_packs(self):
        pass

    def balance_call_credits(self):
        pass

    def creditme2u(self, phone_number, amount):
	""" Performs the Credit Me2U action for your service.

	phone_number
	    String-based phone number that you want to send credit to.
	amount
	    Amount of money you would like to send. At the time of writing,
	    only whole-dollar amounts between $1 and $10 are supported,
	    up to a maximum of $10 in total per day.
	"""
	menu = self.main_menu()
	option = menu['CredMe2U']
	confirmation = response.reply(option).reply(phone_number).reply(amount)
        if str(phone_number) in confirmation.message and \
                '$%s' % amount in confirmation.message:
            success = confirmation.reply('1')
	else:
            raise ValueError("Didn't receive confirmation correctly.")

        success.cancel()
	return success.message


def autodetect(phone_number=None):

    ports = serialenum.enumerate()
    modem = None

    for port in ports:
        modem = Modem(port, baudrate=9600)
        try:
            modem.connect()
            prepaid = PrepaidAccount(modem)
            if phone_number and prepaid.phone_number != phone_number:
		prepaid.modem.close()
                continue
            break
	except SerialException:
            pass
        except TimeoutException:
            pass

    return modem

