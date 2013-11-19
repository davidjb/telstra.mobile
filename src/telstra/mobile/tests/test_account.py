
import unittest

from telstra.mobile.account import TelstraAccount
from telstra.mobile.tests import dummy_modem_cls, dummy_enumerate_ports


MENU = 'Bal:$123.45 *\r\nExp 12 Mar 2010\r\n1. Recharge\r\n2. Balance\r\n3. My Offer\r\n4. PlusPacks\r\n5. Tones&Extras\r\n6. History\r\n7. CredMe2U\r\n8. Hlp\r\n00. Home\r\n*charges can take 48hrs'


def dummy_response(message_):
    class DummyResponse(object):
        message = message_
    return DummyResponse()


def wrap_message_response(fn):
    """ Wrap all return messages from function in a response object.
    """
    def wrapped(self, code):
       return dummy_response(fn(self, code))
    return wrapped 


class PrepaidAccountGsmModem(dummy_modem_cls()):

    _is_prepaid = True

    @wrap_message_response
    def sendUssd(self, code):
        """ Simulate responses to various USSD codes.
        """
        if code == '#100#':
            return MENU
        elif code == '#125#':
            if self._is_prepaid:
                return 'Bal: $10.00'
            else:
                return 'This service only functions on prepaid.' 
        elif code == '#150#':
            return 'Phone number:\r\n0412345678'


class PostpaidAccountGsmModem(PrepaidAccountGsmModem):
    _is_prepaid = False


class TestAccount(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def _autodetect_account(self, class_=PrepaidAccountGsmModem):
        from telstra.mobile import modem
        modem.GsmModem = class_ 
        modem.enumerate_serial = dummy_enumerate_ports(['/dev/ttyS0'])
        from telstra.mobile import autodetect_account
        return autodetect_account()

    def test_autodetect(self):
        account = self._autodetect_account()
        self.assertIsNotNone(account)
        self.assertEqual(account.phone_number, '0412345678')

    def test_is_prepaid(self):
        from telstra.mobile.account import Prepaid, Postpaid

        account = self._autodetect_account(PrepaidAccountGsmModem)
        self.assertIsInstance(account, Prepaid)
        self.assertTrue(account.is_prepaid)

        account = self._autodetect_account(PostpaidAccountGsmModem)
        self.assertIsInstance(account, Postpaid)
        self.assertFalse(account.is_prepaid)

    def test_close(self):
        """ Test close method proxies to modem.
        """
        account = self._autodetect_account()
        account.close()
        self.assertTrue(account.modem.closed)

    def test_parse_menu(self):
        account = TelstraAccount(None)
        menu = account.parse_menu(dummy_response(MENU))
        self.assertEqual(len(menu), 9)
        self.assertEqual(menu['Recharge'], '1')
        self.assertEqual(menu['CredMe2U'], '7')
        self.assertEqual(menu['Home'], '00')

    def test_main_menu(self):
        account = self._autodetect_account()
        menu = account.main_menu()
        self.assertIsNotNone(menu)
        self.assertTrue(len(menu.message) > 0)

    def test_main_parsed(self):
        account = self._autodetect_account()
        menu = account.main_menu_parsed()
        self.assertIsNotNone(menu)
        self.assertEqual(len(menu), 9)
        self.assertEqual(menu['Recharge'], '1')
