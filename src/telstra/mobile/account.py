from lazy import lazy

from telstra.mobile.modem import autodetect_modem


class TelstraAccount(object):
    """ Base Telstra mobile account, shared features between types.
    """

    def __init__(self, modem):
        """ Initialise Telstra account with a modem inteface.

        :param modem: Instance of :class:`gsmmodem.GsmModem`
        """
        self.modem = modem

    def close(self):
        """ Close the underlying modem interface.
        """
        self.modem.close()

    @classmethod
    def parse_menu(cls, ussd):
	""" Attempt to parse the menu options into a traversable structure.

    :returns: A numerically-keyed structure representing menu options.
    :rtype: dict
	"""
        menu_items = ussd.message.split('\r\n')
        menu = {}
        for item in menu_items:
            item_details = re.match('(\d)\.\s+(.*)', item)
            if item_details:
                results = item_details.groups()
                menu[results[1]] = results[0]

        return menu

    def main_menu_parsed(self):
        """ Load and parse the main menu ino a numerically-keyed structure.

        :rtype: dict
        """
        return self.parse_menu(self.main_menu())

    def main_menu(self):
        """ Load a USSD session to the main #100# menu.
        """
        return self.modem.sendUssd('#100#')

    @lazy
    def phone_number(self):
        """ Determine the phone number for the given service.

        :rtype: str
        """
        response = self.modem.sendUssd('#150#')
        return response.message.split('\r\n')[1]

    @lazy
    def is_prepaid(self):
        """ Determine if the given service is pre- or post-paid.

        :rtype: bool
        """
        response = self.modem.sendUssd('#125#')
        return 'Bal:' in response.message

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

        :param phone_number: String-based phone number that you want to send credit to.
        :param amount: Amount of money you would like to send. At the time of
            writing, only whole-dollar amounts between $1 and $10 are supported, up
            to a maximum of $10 in total per day.
        :returns: Successful USSD message string indicating actions taken.

        This method attempts to detect the CreditMe2U functionality
        """
        menu = self.main_menu()

        #Try loading the pre-paid string or post-paid string
        option = menu.get('CredMe2U', menu.get('Credit Me2U'))
        if not option:
            raise ValueError('Could not detect Credit Me2U as being available.')

        confirmation = response.reply(option).reply(phone_number).reply(amount)
        if str(phone_number) in confirmation.message and \
            '$%s' % amount in confirmation.message:
             success = confirmation.reply('1')
        else:
            raise ValueError("Didn't receive confirmation correctly.")
            success.cancel()
        return success.message


def check_phone_number(modem, phone_number):
    """ Check the given phone number belongs to the Telstra account for modem.

    :param modem: modem to convert into a TelstraAccount, and account to check.
    :param phone_number: String-based phone number to compare to given :modem:
    :returns: Result of comparing account's number and given number.
    :rtype: bool
    """
    account = TelstraAccount(modem)
    return account.phone_number == phone_number

def autodetect_account(phone_number=None):
    """ Autodetect a suitable Telstra account on a cellular modem.

    :param phone_number: The phone number of the SIM to detect in the system.
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
    #Convert the account into Prepaid or Postpaid based upon accessing #125# -> Boolean
    check = lambda modem: check_phone_number(modem, phone_number)
    modem = autodetect_modem(check_fn=check)
    if modem:
        account = TelstraAccount(modem)
        return Prepaid(modem) if account.is_prepaid else Postpaid(modem)

