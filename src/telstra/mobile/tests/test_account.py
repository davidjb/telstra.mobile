
import unittest

from telstra.mobile.account import TelstraAccount

#XXX Need DummyModem

class TestAccount(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_close(self):
        pass

    def test_parse_menu(self):
        class DummyMenu(object):
            message = 'Bal:$123.45 *\r\nExp 12 Mar 2010\r\n1. Recharge\r\n2. Balance\r\n3. My Offer\r\n4. PlusPacks\r\n5. Tones&Extras\r\n6. History\r\n7. CredMe2U\r\n8. Hlp\r\n00. Home\r\n*charges can take 48hrs'
        account = TelstraAccount(None)
        menu = account.parse_menu(DummyMenu())
        self.assertEqual(len(menu), 9)
        self.assertEqual(menu['Recharge'], '1')
        self.assertEqual(menu['CredMe2U'], '7')
        self.assertEqual(menu['Home'], '00')

    def test_main_menu(self):
        pass
    
    def test_phone_number(self):
        pass

    def test_is_prepaid(self):
        pass

