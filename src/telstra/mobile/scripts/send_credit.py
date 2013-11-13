import argparse
from contextlib import closing
from datetime import datetime, timedelta
import logging
import os

from telstra.mobile import autodetect_account

logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger(__name__)

def main():
    """ Send credit to someone via Telstra's CreditMe2U service.
    """
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('phone_number',
                        help='Phone number to send credit to')
    parser.add_argument('amount',
                        type=int,
                        help='Amount of credit in whole dollars to send.')
    parser.add_argument('-n', '--next-run',
                        type=int,
                        default=10,
                        help='Prevent this script running again for this many days.')
    parser.add_argument('-d', '--data-location',
                        default='send_credit.data',
                        help='Location of where to store state data.')
    parser.add_argument('-t', '--datetime-format',
                        default='%Y-%m-%dT%H:%M:%S.%f',
                        help='Format of datetime object to use.')
    #TODO Make logging configurable via verbosity
    parser.add_argument('-v', '--verbose',
                        action='count',
                        help='Increase verbosity of logging.')
    config = parser.parse_args()

    #Check last run time and ensure not running early
    if os.path.exists(config.data_location):

        data = open(config.data_location, 'rb').read()
        try:
            last_run = datetime.strptime(data.strip(), config.datetime_format)
        except:
            raise ValueError("Couldn't parse the existing data file.")

        if datetime.now() < last_run + timedelta(days=config.next_run):
            log.info('Script has been run before the elapsed timeout.')
            exit()

    #Automatically close modem after finishing
    with closing(autodetect_account()) as account:
        log.info('Running send credit script...')
        try:
            result = account.creditme2u(config.phone_number,
                                        amount=config.amount)
            #Write out the current date and time to prevent re-running
            now = datetime.now()
            with open(config.data_location, 'wb') as data_file:
                data_file.write(now.strftime(config.datetime_format))
                log.debug('Wrote current time out to file.')
            log.info('Credit sent successfully.')
        except:
            log.error('Warning: failed to send credit to receiving phone.')
            #Scream louder here. Send an email?
            raise

