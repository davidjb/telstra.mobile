import argparse
from contextlib import closing
from datetime import datetime, timedelta
import logging
import os

from telstra.mobile import autodetect_account, TelstraWebApi
from telstra.mobile.config import LOG_FORMAT

log = logging.getLogger(__name__)


def exit_log(message):
    log.info(message)
    exit()


def exit_critical(message):
    log.critical(message)
    exit(1)


def main():
    """ Send credit to someone via Telstra's CreditMe2U service.

    This script can either run periodically or intelligently retrieve
    the service's metadata and only send credit when a certain condition
    is satisfied.  So far, two conditions are either expiry date upcoming
    or when credit drops below a certain amount.
    """
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    subparsers = parser.add_subparsers(
        title='subcommands',
        description='operation modes',
        dest='mode',
        help='mode of operation to use for sending credit')

    # Options for web API-based operation
    responsive_parser = subparsers.add_parser(
        'responsive',
        help='automatic credit transfer balance querying')
    responsive_parser.add_argument(
        '-l', '--credit-limit', type=float,
        help='Send credit if target account\'s balance is lower than this.')
    responsive_parser.add_argument(
        '-d', '--date-limit', type=float,
        help='Send credit if target account\'s expiry is less than or equal '
             'to this many days away.')
    responsive_parser.add_argument(
        '-u', '--user',
        help='User ID to authenticate to Telstra\'s web services.')
    responsive_parser.add_argument(
        '-p', '--password',
        help='Account password for authentication to Telstra\'s web services.')

    # Options for time-based operation
    periodic_parser = subparsers.add_parser(
        'periodic',
        help='periodic credit transfer')
    periodic_parser.add_argument(
        '-n', '--next-run', type=int, default=10,
        help='Prevent this script running again for this many days.')
    periodic_parser.add_argument(
        '-d', '--data-location', default='',
        help='Location of where to store state data for last run time.')
    periodic_parser.add_argument(
        '-t', '--datetime-format', default='%Y-%m-%dT%H:%M:%S.%f',
        help='Format of datetime object to use.')

    # General options for sending creit
    parser.add_argument('-o', '--phone-number',
                        required=True,
                        help='Phone number to send credit to.')
    parser.add_argument('-a', '--amount',
                        type=int,
                        default=1,
                        help='Amount of credit in whole dollars to send.')
    parser.add_argument('-f', '--from-number',
                        help='Send credit from this phone number. '
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

    if config.mode == 'responsive':
        # Check the specified command-line conditions
        api = TelstraWebApi(config.user, config.password)
        if config.credit_limit:
            balance = api.prepaid_balance()
            if balance is None:
                exit_critical('Online API is unavailable.')
            elif balance > config.credit_limit:
                exit_log('Credit balance of $%f exceeds $%f.' % (
                    balance, config.credit_limit))

        if config.date_limit:
            date_delta = timedelta(days=config.date_limit)
            expiry = api.prepaid_expiry()
            now = datetime.now()
            if expiry is None:
                exit_critical('Online API is unavailable.')
            elif (expiry - date_delta) > now:
                exit_log('Expiry date of %s exceeds %s plus %s days.' % (
                    expiry, now, config.date_limit))

    elif config.mode == 'periodic':
        # Check last run time and ensure not running early
        if os.path.exists(config.data_location):

            data = open(config.data_location, 'rb').read()
            try:
                last_run = datetime.strptime(data.strip(),
                                             config.datetime_format)
            except:
                raise ValueError("Couldn't parse the existing data file.")

            if datetime.now() < last_run + timedelta(days=config.next_run):
                exit_log('Script has been run before the elapsed timeout.')

    log.info('Conditions passed. Auto-detecting account.')

    # Automatically close modem after finishing
    account = autodetect_account(phone_number=config.from_number)
    if not account:
        log.critical("Couldn't detect a suitable modem or account.")
        exit(1)

    with closing(account) as account_wrapped:
        log.info('Running send credit script...')
        try:
            result = account_wrapped.creditme2u(config.phone_number,
                                                amount=config.amount)
            # Write out the current date and time to prevent re-running
            if config.mode == 'periodic' and config.data_location:
                now = datetime.now()
                with open(config.data_location, 'wb') as data_file:
                    data_file.write(now.strftime(config.datetime_format))
                    log.debug('Wrote current time out to file.')
            log.info('Credit sent successfully.')
        except:
            log.error('Warning: failed to send credit to receiving phone.')
            # Scream louder here. Send an email or text message?
            raise
