from telstra.mobile.account import Prepaid, autodetect_account
from telstra.mobile.modem import autodetect_modem


def debug():
    import logging
    logging.basicConfig(level=logging.DEBUG)
