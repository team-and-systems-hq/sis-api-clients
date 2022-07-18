"""
Author: Mario Gudelj, EnrolHQ @ https://www.enrolhq.com.au

This is a simple Python 3 client TASS. It uses some of the URL creation code from this file:

https://github.com/TheAlphaSchoolSystemPTYLTD/api-introduction/blob/master/encryptDecrypt.py

I've made the code a bit more Pythonic, wrapped it into class and added a few common methods. There are some changes
in here that make the code work with Python 3. You need to install the following packages:

pip install requests
pip install pycryptodome


Usage:

tass_client = TassCalendarClient()
response = tass_client.get_current_students()

"""

import base64
import datetime
from urllib.parse import urlencode
from Crypto.Cipher import AES
import requests


class TassCalendarClient(object):
    def __init__(self):
        self.token_key = ""
        self.app_code = ""
        self.company_code = ""
        self.version = '2'
        self.end_point = ""
        self.headers = {'content-type': 'application/json'}

    def get_encrypted_token(self, token, params):
        decoded = base64.b64decode(token)
        plaintext = params
        length = 16 - (len(plaintext) % 16)
        plaintext += chr(length) * length
        rijndael = AES.new(decoded, AES.MODE_ECB)
        ciphertext = rijndael.encrypt(plaintext.encode("utf8"))
        ciphertext = base64.b64encode(ciphertext)
        return ciphertext

    def get_url_request(self, end_point, method, app_code, company_code, version, parameters, token_key):
        encrypted = self.get_encrypted_token(token_key, parameters)
        request_dict = {
            "method": method,
            "appcode": app_code,
            "company": company_code,
            "v": version,
            "token": encrypted
        }
        request_str = urlencode(request_dict)
        url_string = end_point + '?' + request_str
        return url_string

    def get_url(self, parameters, method, version):
        """
        :param parameters: This needs to be a JSON as string.
        :param method: This is not a HTTP method but the name of the function at TASS
        :return: This and all the stuff above will just spit out a URL you make a request to.
        """
        return self.get_url_request(self.end_point, method, self.app_code, self.company_code, version, parameters,
                                    self.token_key)

    def get_calendar_json_feed(self):
        """
        This will get you events from the past 90 days to 1000 days in future. You can manipulate this as you wish.
        I tend to store this data locally and not hit TASS API all the time.
        :return:
        """
        method = "getParentCalendar"
        today = datetime.datetime.now()
        three_months_ago = today - datetime.timedelta(days=90)
        three_years_future = today + datetime.timedelta(days=1000)
        params = "{'start_date':'%s\/%s\/%s', 'end_date':'%s\/%s\/%s'}" % (
            three_months_ago.day,
            three_months_ago.month,
            three_months_ago.year,
            three_years_future.day,
            three_years_future.month,
            three_years_future.year)
        url = self.get_url(params, method, self.version)
        resp = requests.get(url)
        return resp
