"""
This is the Engage client for Projects Horizon's Engage SIS. The docs are behind the login so I cant provide a link to
those but you can ask Engage for access to those.

We are using python requests to make calls to Engage. I have taken out the code that raises exceptions in case Engage
API can't be reached but you can easily wrap you calls inside try and except. You can check for codes like this:

response = s.post(self.token_url, data)
if response.status_code == 401:
    # Can't authenticate with this token so let's refresh the token

To use this class simply install requests with "pip install requests" and then instantiate the class like this:

client = EngageAPi()

When you instantiate the class it'll automatically authenticate and store the token under client.token which will
be used in all the requests.

Then you can call methods to fetch data and process it:

pupils = client.get_pupils() # This will give you a list of current students

Below is an example of some methods I used for getting the basic data for emailing purposes. Hopefully, it'll give you
a good start

"""

from requests import Session


class EngageApi(object):
    def __init__(self):
        self.ENGAGE_USER = ''   # You should load these from environment vars e.g. os.getenv('ENGAGE_USER')
        self.ENGAGE_PASSWORD = ''   # You should load these from environment vars e.g. os.getenv('ENGAGE_PASSWORD')
        self.engage_url = 'your_engage_school_url'  # This is the root URL your Engage sits on
        self.base_url = self.engage_url + '/api/v1/'
        self.token_url = self.engage_url + '/api/gettoken'
        self.session = Session()
        self.token = self.get_token()
        headers = {"Authorization": "Bearer %s" % self.token}
        self.session.headers = headers
        self.pupils_url = self.base_url + "personaldetails/getcurrentpupilinfo/"
        self.contacts_url = self.base_url + "personaldetails/getcontactinfo/"

    def get_token(self):
        """
        Return one time API token for use in every request for 60 minutes.
        """
        s = Session()
        data = {
            "username": self.ENGAGE_USER,
            "password": self.ENGAGE_PASSWORD,
        }
        response = s.post(self.token_url, data)
        token = response.json()["access_token"]
        return token

    def get_pupils(self):
        """
        Get's a list of pupils with contacts.
        :return:
        """
        params = {'contactinfo': True}
        pupils_url = self.base_url + "personaldetails/getcurrentpupilinfo/"
        pupils = self.session.get(pupils_url, params=params).json()
        final_list = []
        for pupil in pupils:
            if pupil['status'] != 'Current':
                continue
            final_list.append(pupil)
        return final_list

    def get_contacts(self):
        """
        Gets the list of contacts from Engage and returns a dict with contact id for lookup.
        """
        contacts_url = self.base_url + "personaldetails/getcontactinfo/"
        contacts = self.session.get(contacts_url).json()
        contacts_dict = {}
        for contact in contacts:
            parent_contacts = []
            for email in contact['emailAddresses']:
                cont_dict = {
                    'external_id': "%s-%s" % (email['contactId'], email['emailAddress']),
                    'first_name': contact['forename'],
                    'last_name': contact['surname'],
                    'email': email['emailAddress'],
                    'is_current_parent': True,
                    'data': {
                        'salutation': contact['greeting'],
                        'description': email['description'],
                        'is_primary': email['isPrimary'],
                        'title': contact['title'],
                        'engage_id': email['contactId'],
                        'is_parent': True
                    }
                }
                parent_contacts.append(cont_dict)
            try:
                contacts_dict[contact['contactId']] = parent_contacts
            except KeyError:
                contacts_dict.update({contact['contactId']: parent_contacts})
        return contacts_dict

    def bundle_contacts(self):
        contacts = self.get_contacts()
        pupils = self.get_pupils()
        final_contacts = []
        for pupil in pupils:
            year_group = pupil['yearGroup']
            try:
                student_contact_ids = [con['contactId'] for con in pupil['contacts']]
            except KeyError:
                continue
            for student_contact_id in student_contact_ids:
                for c in contacts[student_contact_id]:
                    try:
                        c['data']['student_years'].append(year_group)
                    except KeyError:
                        c['data'].update({'student_years': [year_group]})

        for pupil in pupils:
            try:
                student_contact_ids = [con['contactId'] for con in pupil['contacts']]
            except KeyError:
                continue
            for student_contact_id in student_contact_ids:
                for c in contacts[student_contact_id]:
                    final_contacts.append(c)
        return final_contacts


