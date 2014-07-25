import datetime
import logging
import re
import urllib

import requests

LOGIN_URL = 'https://www.my.telstra.com.au/myaccount/home'

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
        login_page = session.get(LOGIN_URL)
	login_data = {
            'encoded': 'false',
	    'goto': 'https://www.my.telstra.com.au/myaccount/overview',
	    'gotoOnFail': 'https://www.my.telstra.com.au/myaccount/home/error?flag=EMAIL',
	    'gx_charset': 'UTF-8',
	    'password': password,
	    'username': username
        }
        login_response = self.session.post('https://signon.telstra.com.au/login', data=login_data)
        import ipdb; ipdb.set_trace()


    @classmethod
    def java_time_to_python(java_timestamp):
        return datetime.fromtimestamp(java_timestamp/1000.0)


    def prepaid_contact_details(self):
        """ Obtains account holder contact details on file.
        
        {"middleName":null,"lastName":"Smith","homeNumber":null,"firstName":"John"}
        """
        response = self.session.get('https://www.my.telstra.com.au/myaccount/contactdetail.json')
        return response.json()


    def prepaid_metadata(self, phone_number=None):
        """ Obtain account and service metadata for a prepaid service.
        """
        response = self.session.get('https://www.my.telstra.com.au/myaccount/prepaid/getCreditSummaryData.json?serviceId=')
        data = response.json()
        return {
            'expiry': self.java_time_to_python(data['creditExpireDate']),
            'balance': data['creditAmount']['value'],
            'offer': data['commercialOfferCode']['value'],
            'bonuspacks': data['bundleGroupList']
        }


    def prepaid_recharge_history(self, phone_number=None):
        """ Access and process recharge history for a prepaid service.

        [{'date': 1405250719000,
          'amount': {'value': 10},
         ...]

        There's other information in the JSON structure, but it is all redundant.
        """
        response = self.session.get('https://www.my.telstra.com.au/myaccount/prepaid/getPrepaidRechargeHistory.json?serviceId=')
        data = response.json()
        if 'result' in data:
            for recharge in data['result']:
                print(self.java_time_to_python(recharge['date'], recharge['amount]['value']))


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

        

