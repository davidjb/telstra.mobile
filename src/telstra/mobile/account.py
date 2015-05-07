import re
from datetime import datetime
import time

from lazy import lazy

from gsmmodem.exceptions import CommandError, TimeoutException
from telstra.mobile.modem import autodetect_modem


class TelstraAccount(object):
    """ Base Telstra mobile account, shared features between types.
    """

    def __init__(self, modem, pin=None):
        """ Initialise Telstra account with a modem inteface.

        :param modem: Instance of :class:`gsmmodem.GsmModem`
        """
        self.modem = modem
        self.pin = pin

    def close(self):
        """ Close the underlying modem interface.

        Conform to the ``contextlib`` closing interface.
        """
        self.modem.close()

    def reconnect(self):
        """ Close and reconnect underlying modem interface.
        """
        self.close()
        self.modem.connect(pin=self.pin)

    @classmethod
    def parse_menu(cls, ussd):
        """ Attempt to parse the menu options into a traversable structure.

        :returns: A numerically-keyed structure representing menu options.
        :rtype: dict
        """
        menu_items = ussd.message.split('\r\n')
        menu = {}
        for item in menu_items:
            item_details = re.match('(\d+)\.\s+(.*)', item)
            if item_details:
                results = item_details.groups()
                menu[results[1]] = results[0]

        return menu

    def main_menu(self):
        """ Load a USSD session to the main #100# menu.
        """
        return self.modem.sendUssd('#100#')

    def main_menu_parsed(self):
        """ Load and parse the main menu ino a numerically-keyed structure.

        :rtype: dict
        """
        menu = self.main_menu()
        menu.cancel()
        return self.parse_menu(menu)

    def process_response_more(self, ussd):
        """ Recursively process a USSD response for more Telstra info.
        """
        menu = self.parse_menu(ussd)
        if 'More' in menu:
            response = ussd.reply(menu['More'])
            return ussd.message + self.process_response_more(response)
        else:
            return ussd.message

    @lazy
    def phone_number(self):
        """ Determine the phone number for the given service.

        :rtype: str
        """
        response = self.modem.sendUssd('#150#')
        if 'your mobile' not in response.message.lower():
            response.cancel()
            time.sleep(2)
            response = self.modem.sendUssd('#150#')

        return response.message.split('\r\n')[1]

    @lazy
    def account_number(self):
        """ Determine the Telstra account number for the service.

        :rtype: str
        """
        response = self.modem.sendUssd('#150#')
        if 'your mobile' not in response.message.lower():
            response.cancel()
            time.sleep(2)
            response = self.modem.sendUssd('#150#')

        return response.message.split('\r\n')[-1]

    @lazy
    def is_prepaid(self):
        """ Determine if the given service is pre- or post-paid.

        :rtype: bool
        """
        response = self.modem.sendUssd('#125#')
        response.cancel()
        return 'Bal:' in response.message and 'Exp:' in response.message


class Postpaid(TelstraAccount):
    """ A Postpaid Telstra account that can interact with network servies.

    At present, this is simply a place-holder until additional functionality
    is added.
    """
    pass


class Prepaid(TelstraAccount):
    """ A Prepaid Telstra account that can interact with network servies.
    """

    @property
    def balance(self):
        response = self.main_menu()
        response.cancel()
        balance = re.search('\$(.*?)\s', response.message)
        if balance:
            return float(balance.groups()[0].replace(',', ''))

    @property
    def expiry_date(self):
        response = self.main_menu()
        response.cancel()
        expiry = re.search('Exp.*?\s(.*?)\r\n', response.message)
        if expiry:
            return datetime.strptime(expiry.groups()[0], '%d %b %Y')

    def balance_plus_packs(self):
        pass

    def balance_call_credits(self):
        """ Obtain the 'Call Credits' balance for this service.

        This method attempts to detect the Call Credits availability for
        this service before proceeding.
        """
        response = self.main_menu()
        menu = self.parse_menu(response)

        # Try accessing the Recharge section
        option = menu.get('Bal Details')
        if not option:
            raise ValueError('Could not detect Bal Details as being available.')

        response = response.reply(option)

        if not 'Call Cred Bal' in response.message:
            raise ValueError('Call credits are not available on this service.')

        balance_page1 = response.reply('2')
        call_credit_text = self.process_response_more(balance_page1)

        balance = re.search('\$(.*?)\s', call_credit_text)
        if balance:
            return float(balance.groups()[0])

    def creditme2u(self, phone_number, amount):
        """ Performs the Credit Me2U action for your service.

        :param phone_number: String-based phone number that you want to send
            credit to.
        :param amount: Amount of money you would like to send. At the time of
            writing, only whole-dollar amounts between $1 and $10 are
            supported, up to a maximum of $10 in total per day. Enter this
            value as either an integer or string equivalent.
        :returns: Successful USSD message string indicating actions taken.

        This method attempts to detect the CreditMe2U functionality.
        """
        amount = int(str(amount).replace('$', ''))
        if amount < 1 or amount > 10:
            raise ValueError("Could not parse the amount specified.")
        amount = str(amount)

        response = self.main_menu()
        menu = self.parse_menu(response)

        # Try accessing the Recharge section
        option = menu.get('Recharge')
        if not option:
            raise ValueError('Could not detect Recharge as being available.')

        # Traverse to Recharge option
        response = response.reply(option)
        menu = self.parse_menu(response)

        option = menu.get('CreditMe2U',
                          menu.get('CredMe2U',
                                   menu.get('Credit Me2U')))
        if not option:
            raise ValueError('Could not detect Credit Me2U functionality.')

        confirmation = response.reply(option).reply(phone_number).reply(amount)
        if str(phone_number) in confirmation.message and \
                '$%s' % amount in confirmation.message:
            response = confirmation.reply('1')
        elif 'Insufficient credit' in confirmation.message:
            raise ValueError("Insufficient credit account to send credit.")
        elif 'transfer limit' in confirmation.message:
            raise ValueError(confirmation.message)
        else:
            try:
                response.reply('00').cancel()
            except CommandError:
                pass
            raise ValueError("Did not receive CreditMe2U confirmation correctly.")
        return response


def check_phone_number(modem, phone_number):
    """ Check the given phone number belongs to the Telstra account for modem.

    :param modem: modem to convert into a TelstraAccount, and account to check.
    :param phone_number: String-based phone number to compare to given :modem:
    :returns: Result of comparing account's number and given number.
    :rtype: bool
    """
    account = TelstraAccount(modem)
    return account.phone_number == phone_number


def autodetect_account(phone_number=None, pin=None, check=None):
    """ Autodetect a suitable Telstra account on a cellular modem.

    :param phone_number: The phone number of the SIM to detect in the system.
    :param pin: The security PIN for the SIM, if required.
    :returns: Instance of :class:`Prepaid` or :class:`Postpaid`, depending
              on detected account type.

    This method uses :meth:`auto_detectmodem` to locate a cellular modem
    connected to this system.  After connecting to the network, it compares the
    given ``phone_number`` parameter to the SIM's registered phone number
    (determined by ``#150#``).

    Once the correct device and account have been detected, this method
    also coerces the account into the correct type -- Prepaid or Postpaid --
    depending on the outcome of dialling ``#125#``. Post-paid mobile
    devices do not have access to this specific menu at present.

    The final account is returned and is ready for interaction with the
    network.
    """
    if phone_number and not check:
        # Simple equality check on phone number
        check = lambda modem: check_phone_number(modem, phone_number)

    modem = autodetect_modem(pin=pin, check_fn=check)
    if modem:
        account = TelstraAccount(modem, pin=pin)
        try:
            if account.is_prepaid:
                return Prepaid(modem, pin=pin)
            else: 
                return Postpaid(modem, pin=pin)
        except TimeoutException:
            return Prepaid(modem, pin=pin)
            
