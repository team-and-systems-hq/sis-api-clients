"""
This is a client for authentication and some basic calls for PCSchool - https://pcschool.net/

As it's the case with other clients on here, you simply need to provide the credentials and the url inside the constructor
method, and instantiate a client object. Then you can call the client methods. Example:

client = PCSchoolClient()
response = client.get_houses()

The only package you need, which doesn't come with Python, is Python Requests. You can install it with:

pip install requests

"""

import base64
import datetime
import time
import hmac
import hashlib
import requests


class PCSchoolClient(object):
    def __init__(self) -> None:
        self.session = requests.Session()
        self.base_url = ''
        self.username = ''
        self.password = ''
        self.private_key = ''
        self.api_key = ''
        authorisation = self.get_authorisation()
        self.session.headers.update({"Authorization": "Basic %s" % authorisation})
        self.lookup_url = self.base_url + "/Handlers/External/Enrolment.asmx/Handler"
        self.enrolment_url = (
            self.base_url + "/Handlers/External/Enrolment.asmx/ImportHandler"
        )
        self.poll_url = self.base_url + "/Handlers/External/Enrolment.asmx/PollHandler"

    def get_authorisation(self):
        # base 64 encoded string separated by a colon
        credentials = self.username + ":" + self.password
        credentials = str.encode(credentials)
        credentials_bytes = base64.b64encode(credentials)
        return credentials_bytes.decode()

    def get_hmac(self, ts):
        """
        Using HMACSHA256 Cryptography, combine the API and ts and SIGN this request using our PRIVATE KEY.
        This will generate a token string which has to be passed as hmac value.
        :return:
        """
        data = "{}{}".format(self.api_key, ts)
        signature = (
            hmac.new(
                bytes(self.private_key, "latin-1"),
                msg=bytes(data, "latin-1"),
                digestmod=hashlib.sha256,
            )
            .hexdigest()
            .upper()
        )
        return signature

    def post_request(self, url, payload):
        """
        Every request needs:
        ts: unix timestamp in milliseconds
        hmac: HMACSHA256 encryption of API key and ts
        """
        now = datetime.datetime.now()
        ts = int(time.mktime(now.timetuple()) * 1000)
        hmac = self.get_hmac(ts)
        payload.update({"ts": ts, "hmac": hmac})
        headers = {"Content-Type": "application/json; charset=utf-8"}
        response = self.session.post(url, json=payload, headers=headers)
        return response

    def lookup_request(self, payload):
        url = self.lookup_url
        return self.post_request(url, payload)

    def get_houses(self):
        """
        Use 'Event' key in the payload - Event is case sensitive.
        key value pairs of `code : name`
        Response: { 'Acacia': 'Acacia - yellow', }
        """
        event = "HOUSE"
        payload = {"Event": event}
        return self.lookup_request(payload)

    def get_nationalities(self):
        """
        PC School is interested in Code only (not the 120 key).
        {'120': {'Code': 'AFG', 'Description': 'Afghanistan'},
         '130': {'Code': 'AUS', 'Description': 'Australia'},
        """
        event = "NATIONALITY"
        payload = {"Event": event}
        return self.lookup_request(payload)

    def get_ethnicities(self):
        """
        See Nationality response.
        """
        event = "ETHNICITY"
        payload = {"Event": event}
        return self.lookup_request(payload)

    def get_languages(self):
        """
        See Nationality response.
        """
        event = "LANGUAGE"
        payload = {"Event": event}
        return self.lookup_request(payload)

    def get_schools(self):
        """
        See Nationality response.
        """
        event = "SCHOOL"
        payload = {"Event": event}
        return self.lookup_request(payload)

    def get_countries(self):
        """
        See Nationality response.
        """
        event = "COUNTRY"
        payload = {"Event": event}
        return self.lookup_request(payload)

    def get_years(self):
        """
        See Houses response.
        """
        event = "YEAR"
        payload = {"Event": event}
        return self.lookup_request(payload)







