from datetime import datetime
import re
import logging

import requests

LOGIN_URL = 'https://www.my.telstra.com.au/myaccount/home'
log = logging.getLogger(__file__)


class TelstraWebApi(object):
    """ API for accessing Telstra mobile information via a web interface.

    This could deserve its own package eventually, though since the methods
    here are specific to Telstra mobiles, it lives here for now.

    Authenticate using your telstra.com username and password.

    **Caution**: all methods use undocumented end-points and are liable
    to break or change at any time!
    """

    def __init__(self, username, password):
        self.session = requests.Session()
        login_page = self.session.get(LOGIN_URL)
        login_page.raise_for_status()
        login_data = {
            'encoded': 'false',
            'goto': 'https://www.my.telstra.com.au/myaccount/overview',
            'gotoOnFail': 'https://www.my.telstra.com.au/myaccount/home/error?flag=EMAIL',
            'gx_charset': 'UTF-8',
            'password': password,
            'username': username
        }
        login_response = \
            self.session.post('https://signon.telstra.com.au/login',
                              data=login_data)
        login_response.raise_for_status()

    @staticmethod
    def java_time_to_python(milliseconds):
        """ Convert System.currentTimeMillis() into a Unix timestamp.
        """
        return datetime.fromtimestamp(milliseconds/1000.0)

    def logout(self):
        self.session.get('https://www.my.telstra.com.au/myaccount/log-out')

    def _get_json(self, url):
        response = self.session.get(url)
        content_type = response.headers.get('content-type')
        if response.url == url and 'json' in content_type:
            return response.json()
        else:
            log.critical('Could not retrieve service metadata. '
                         'Content type is %s.' % content_type)
            return {}

    @property
    def _prepaid_metadata(self, phone_number=None):
        """ Obtain account and service metadata for a prepaid service.
        """
        url = 'https://www.my.telstra.com.au/myaccount/prepaid/getCreditSummaryData.json'
        return self._get_json(url)

    def prepaid_expiry(self, phone_number=None):
        timestamp = self._prepaid_metadata.get('creditExpireDate')
        return self.java_time_to_python(timestamp) if timestamp else None

    def prepaid_balance(self, phone_number=None):
        credit_amount = self._prepaid_metadata.get('creditAmount')
        return credit_amount['value'] if credit_amount else None

    def prepaid_offer(self, phone_number=None):
        offer = self._prepaid_metadata.get('commercialOfferCode')
        return offer['value'] if offer else None

    def prepaid_bonuspacks(self, phone_number=None):
        return self._prepaid_metadata.get('bundleGroupList')

    def contact_details(self):
        """ Obtains account holder contact details on file.

        {"middleName":null,
         "lastName":"Smith",
         "homeNumber":null,
         "firstName":"John"}
        """
        return self._get_json('https://www.my.telstra.com.au/myaccount/contactdetail.json')

    def prepaid_recharge_history(self, phone_number=None):
        """ Access and process recharge history for a prepaid service.

        [{'date': 1405250719000,
          'amount': {'value': 10},
         ...]

        There's other information in the JSON structure, but it is all
        redundant.
        """
        data = self._get_json('https://www.my.telstra.com.au/myaccount/prepaid/getPrepaidRechargeHistory.json')
        if 'result' in data:
            for recharge in data['result']:
                print(self.java_time_to_python(recharge['date'],
                                               recharge['amount']['value']))

    def prepaid_history(self, phone_number=None):
        """ Access the last 30 days of call and service records.

        Processing of this response requires screen scraping HTML.
        """
        response = self.session.get('https://www.my.telstra.com.au/myaccount/data-usage-pre-paid/prepaid-usage-fragment?serviceId=')
        print(response.content)

    def prepaid_puk(self, phone_number=None):
        """ Get the PUK for the given account via scraping HTML.
        """
        response = self.session.get('https://www.my.telstra.com.au/myaccount/plan-details-pre-paid')
        match = re.search('<span class="puk">(.*?)</span>', response.content)
        if match:
            return match.groups()[0]
