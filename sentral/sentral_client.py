"""
This is a basic Sentral client in Python

Simply instantiate the client and call the methods. Example:

client = SentralClient()
response = client.get_houses()

You just need Python requests for this which you can install with:

pip install requests

Info on Python requests https://pypi.org/project/requests/

Sentral API info can be found here http://development.sentral.com.au/

"""

import datetime
from requests import Session


def get_campus(campus_id):
    return {
        '1': "Senior School",
        '2': "Senior School Boarding",
        '3': "Junior School"
    }.get(campus_id, "")


class SentralClient(object):

    def __init__(self):
        self.school_sentral_url = ''
        self.base_url = self.school_sentral_url + "/restapi"
        self.sentral_key = "SENTRAL_KEY"
        self.sentral_tenant_id = "SENTRAL_TENANT_ID"
        self.session = Session()
        self.session.headers = {
            "X-API-KEY": self.sentral_key,
            "X-API-TENANT": self.sentral_tenant_id,
            "Content-Type": "application/vnd.api+json",
        }

        self.enrolments_url = self.base_url + '/v1/enrolments/enrolment'
        self.enrolment_type = 'enrolment'

        self.year_level_url = self.base_url + '/v1/enrolments/year-level'
        self.roll_class_url = self.base_url + '/v1/enrolments/rollclass'
        self.academic_period_url = self.base_url + '/v1/enrolments/academic-period'
        self.households_url = self.base_url + '/v1/enrolments/household'
        self.student_url = self.base_url + '/v1/enrolments/student'
        self.person_url = self.base_url + '/v1/enrolments/person'
        self.person_phone_url = self.base_url + '/v1/enrolments/person-phone'
        self.person_email_url = self.base_url + '/v1/enrolments/person-email'
        self.student_contacts_url = self.base_url + '/v1/enrolments/person'
        self.houses_url = self.base_url + '/v1/enrolments/house'
        self.academic_period_url = self.base_url + '/v1/enrolments/academic-period'
        self.staff_url = self.base_url + '/v1/enrolments/staff'

    def get_houses(self):
        """
        Get school houses and returns a list of house dictionaries
        :return: list of dicts
        """
        params = {'limit': 100}
        houses = []
        response = self.session.get(self.houses_url, params=params).json()
        for house_dict in response['data']:
            # You can access house info like this
            house_name = house_dict['attributes']['name']
            houses.append(house_dict)
        return houses

    def get_academic_periods(self):
        params = {'limit': 100}
        academic_periods = []
        response = self.session.get(self.academic_period_url, params=params).json()
        for ap_dict in response['data']:
            # You can access data as follows
            ap_year = ap_dict['attributes']['year']
            academic_periods.append(ap_dict)
        return academic_periods

    def get_staff(self, url=None):
        if not url:
            url = self.staff_url
        params = {'include': 'person', 'limit': 100}
        response = self.session.get(url, params=params).json()
        self.save_staff(response)
        while 'next' in response['links'].keys():
            response = self.session.get(response['links']['next'], params=params).json()
            self.save_staff(response)

    def save_staff(self, response):
        for staff_dict in response['data']:
            # This is where you implement some logic that will operate on
            pass

    def get_all(self, url=None):
        if not url:
            url = self.person_url
        params = {'include': 'primaryHousehold,studentPrimaryEnrolment,student,studentContacts', 'limit': 200}
        response = self.session.get(url, params=params).json()
        self.get_persons(response)
        while 'next' in response['links'].keys():
            # We keep looping here until we get to the last page and "next" is not inside the pagination section
            response = self.session.get(response['links']['next'], params=params).json()
            self.get_persons(response)

    def get_persons(self, response):
        """
        If you use include inside the params Sentral will add additional info which is related to the person object.
        For some reason the API doesn't fold it in against the person and instead it has a separate key 'included'
        which you need to loop through. You can figure out what it is by type attribute.
        """
        for person_dict in response['data']:
            if person_dict['type'] == 'person':
                # This is where you process person objects
                pass
        for inc_dict in response.get('included', []):
            if inc_dict['type'] == 'enrolment':
                pass
            if inc_dict['type'] == 'student':
                pass
            if inc_dict['type'] == 'studentPersonRelation':
                pass
            if inc_dict['type'] == 'household':
                pass

    def get_date_or_null(self, dob_str):
        """
        Sentral stores date as 2002-08-19T00:00:00+10:00. Need to convert it Python datetime. I'm only interested in
        date here
        """
        if dob_str:
            return datetime.datetime.strptime(dob_str.split('T')[0], '%Y-%m-%d')
        return

    def sync_persons_phones(self, url=None):
        """
        There's a separate URL for this as it's not included in Person object
        :param url:
        :return:
        """
        if not url:
            url = self.person_phone_url
        params = {'limit': 200}
        response = self.session.get(url, params=params).json()
        for r in response['data']:
            person_id = r['relationships']['owner']['data']['id']
            # This is how you can access parameters
        try:
            while response['links']['next']:
                response = self.session.get(response['links']['next'], params=params).json()
                for r in response['data']:
                    pass
                    # You can loop like this until you get to the end
        except KeyError:
            return
