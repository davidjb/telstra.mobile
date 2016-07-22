import argparse
from contextlib import closing
from datetime import datetime, timedelta
import logging
import os

from telstra.mobile import autodetect_account
from telstra.mobile.config import LOG_FORMAT

log = logging.getLogger(__name__)


def main():
    """ Get the balance of Telstra account.
    """
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument('-p', '--phone-number',
                        help='Get balance for this phone number. '
                             'This auto-detects the correct modem '
                             ' to handle when multiple devices are installed.')

    # TODO Make logging configurable via verbosity
    parser.add_argument('-v', '--verbose',
                        action='count',
                        default=0,
                        help='Increase verbosity of logging.')

    config = parser.parse_args()

    log_level = logging.CRITICAL - config.verbose * 10
    logging.basicConfig(level=log_level, format=LOG_FORMAT)

    # Automatically close modem after finishing
    account = autodetect_account(phone_number=config.phone_number)
    if not account:
        log.critical("Couldn't detect a suitable modem or account.")
        exit(1)

    with closing(account) as account_wrapped:
        try:
            balance = account_wrapped.balance
            print('Credit balance for %s is $%s.' % (config.phone_number or account_wrapped.phone_number, balance))
        except:
            log.error('Warning: failed to get balance.')
            raise
