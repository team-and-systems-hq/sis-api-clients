"""
This Edumate client will get the current carers, current students, current staff and past students from Edumate API.
Simply instantiate the object and then call methods in it.

Example:

client = EdumateClient()
client.get_all_students()
client.get_all_parents()
client.get_more_student_details()
client.get_all_past_students()

You need to install Python requests to use this client. Done with:

pip install requests

Edumate API docs can be found here https://integrations.edumate.net/apidoc/

"""
import requests
import re

regex = re.compile(r"([-!#-'*+/-9=?A-Z^-~]+(\.[-!#-'*+/-9=?A-Z^-~]+)*|\"([]!#-[^-~ \t]|(\\[\t -~]))+\")@([-!#-'*+/-9=?A-Z^-~]+(\.[-!#-'*+/-9=?A-Z^-~]+)*|\[[\t -Z^-~]*])")

def is_email_valid(email):
    """
    This is basic email validation. You should probably use a more robust email validation package
    :param email: Email string
    :return: True or False
    """
    if re.fullmatch(regex, email):
        return True
    return False

class EdumateClientError(Exception):
    pass


class EdumateClient(object):

    def __init__(self):
        self.edumate_url = 'https://edumate.yourschooldomain.edu.au/school/web/app.php/api/'
        self.auth_url = self.edumate_url + 'authorize'
        self.current_parent_url = self.edumate_url + 'contacts/contacts/current?contactType=carer'
        self.current_student_url = self.edumate_url + 'contacts/contacts/current?contactType=student'
        self.past_student_url = self.edumate_url + 'contacts/contacts/past?contactType=student'
        self.detailed_student_url = self.edumate_url + 'contacts/contact-details/student/'
        self.staff_list_url = self.edumate_url + 'contacts/contacts/current?contactType=staff'
        self.staff_detail_url = self.edumate_url + 'contacts/contact-details/staff/'
        self.student_lms_url = self.edumate_url + 'lms/students'
        self.client_id = 'edumate_client_id'  # Get this from Edumate Admin section
        self.client_secret = 'edumate_client_secret' # Get this from Edumate Admin section
        self.access_token = self.authenticate()
        self.headers = {'Authorization': 'Bearer %s' % self.access_token}
        self.CARER_RELATIONSHIPS = ['CHILD', 'STEP CHILD', 'FOSTER CHILD', 'STEPCHILD', 'FOSTER CHILD', 'CHARGE']  # You
        # need to use whatever defines a carer at your school. This would be per school thing

    def authenticate(self):
        resp = requests.post(self.auth_url, data={'client_id': self.client_id, 'client_secret': self.client_secret})
        if resp.ok:
            return resp.json()['data']['access_token']
        raise EdumateClientError("Failed to authenticate with Edumate for %s. Error: %s" % resp.text)

    def get_student_ids(self, parent_dict):
        student_ids = []
        relationships = parent_dict['relationships']
        for relationship in relationships:
            for ref in relationship['contact_reference']:
                if ref.get('student_number') and relationship['relationship_type'].upper() in self.CARER_RELATIONSHIPS:
                    student_ids.append(ref.get('student_number'))
        return student_ids

    def store_parent(self, con):
        """
        Write your logic here for manipulating and storing parent contact
        :param con:
        :return:
        """
        pass

    def should_import(self, parent):
        """
        This method looks at the "mail_flag" coming from Edumate and decides if the parent should be imported or not.
        The school uses this flag to mark the parents who shouldn't be communicated with. We have to uppercase the
        relationships everywhere since they're returned in both cases at different places.
        """
        for r in parent['relationships']:
            if r['relationship_type'].upper() in self.CARER_RELATIONSHIPS:
                for cr in r['contact_reference']:
                    if cr['contact_type'] == 'student':
                        if r['mail_flag']:
                            return True
        return False

    def get_parents(self, url=None):
        if not url:
            url = self.current_parent_url
        resp = requests.get(url, headers=self.headers)
        if resp.ok:
            data = resp.json()['data']
            for con in data:
                if not con['general_info']['email_address']:
                    continue
                if con['general_info']['do_not_contact_flag']:
                    continue
                if self.should_import(con):
                    self.store_parent(con)
                    pass
                else:
                    print("should not import %s" % con['general_info']['email_address'])

        else:
            raise EdumateClientError("Failed to get parents from Edumate for %s. Error: %s" % resp.text)
        return resp

    def get_all_parents(self):
        all_parents_list = []
        resp = self.get_parents()
        if resp.ok:
            all_parents_list += resp.json()['data']
            next_url = resp.json()['pagination']['next']
            while next_url:
                resp = self.get_parents(url=next_url)
                all_parents_list += resp.json()['data']
                try:
                    next_url = resp.json()['pagination']['next']
                except KeyError:
                    # We'll get here once we reach the end of pagination and the response doesn't contain next page
                    return all_parents_list

    def get_students(self, url=None):
        if not url:
            url = self.student_lms_url
        resp = requests.get(url, headers=self.headers)
        if resp.ok:
            data = resp.json()['data']
            # This is where you loop over the list and process data
        return resp

    def get_all_students(self):
        resp = self.get_students()
        if resp.ok:
            next_url = resp.json()['pagination']['next']
            while next_url:
                resp = self.get_students(url=next_url)
                try:
                    next_url = resp.json()['pagination']['next']
                except KeyError:
                    # We'll get here once we reach the end of pagination and the response doesn't contain next page
                    return

    def get_more_student_details(self):
        """
        Use this to get more information on students. The list view will give you some basic info and you can use this
        to fetch more info.
        """
        students = []  # This is a list of students which you've fetched from the list view
        for student in students:
            sid = student.data.get('student_number')
            if sid:
                url = self.detailed_student_url + sid
                resp = requests.get(url, headers=self.headers)
                if resp.ok:
                    data = resp.json()['data']['student']
                    if data['enrolment'].get('short_form_run'):
                        academic_year = data['enrolment'].get('short_form_run')
                    elif "Kindergarten" in data['enrolment'].get('current_form_run'):
                        academic_year = 'K'
                    elif "Year" in data['enrolment'].get('current_form_run'):
                        academic_year = data['enrolment'].get('current_form_run').split('Year')[1].strip()
                    else:
                        academic_year = 'Prep'
                    if academic_year:
                        student.data.update({'academic_year': academic_year})
                    if data['general_info']['student_status'] == 'Current Enrolment':
                        student.current = True
                    student.data.update(
                        {'current_form_run': data['enrolment']['current_form_run'],
                         'tutor_roll_class': data['enrolment']['tutor_roll_class'],
                         'tutor_roll_class_code': data['enrolment']['tutor_roll_class_code'],
                         'tutor_teacher': data['enrolment']['tutor_teacher'],
                         'house': data['general_info']['house'],
                         'student_status': data['general_info']['student_status'],
                         'student_type': data['general_info']['student_type'],
                         }
                    )
                    student.current = True
                    student.save()  # I have a save method my student object here but you can do whatever with this data

    def is_staff_also_parent(self, con):
        """
        Check if the staff member is also a parent
        :param con:
        :return:
        """
        for relo in con['relationships']:
            if relo['contact_reference'][0]['contact_type'] == 'student' and relo['relationship_type'].upper() == 'CHILD':
                return True
        return False

    def get_current_staff(self, url=None):
        if not url:
            url = self.staff_list_url
        resp = requests.get(url, headers=self.headers)
        if resp.ok:
            data = resp.json()['data']
            for con in data:
                if not con['general_info']['email_address']:
                    continue
                staff_number = ''
                for ref in con['general_info']['contact_reference']:
                    if ref.get('staff_number'):
                        staff_number = ref.get('staff_number')
                if self.is_staff_also_parent(con):
                    # This staff member is also a parent
                    self.store_parent(con)
        return resp

    def get_all_current_staff(self):
        resp = self.get_current_staff()
        if resp.ok:
            next_url = resp.json()['pagination']['next']
            while next_url:
                resp = self.get_current_staff(url=next_url)
                try:
                    next_url = resp.json()['pagination']['next']
                except KeyError:
                    return

    def get_staff_detail(self):
        """
        This method will fetch more info about staff
        :return:
        """
        staff = []  # This will be a list of staff members
        for s in staff:
            resp = requests.get(self.staff_detail_url + s.data.get('staff_number'), headers=self.headers)
            if resp.ok:
                data = resp.json()['data']
                staff_type = data['staff']['employment']['staff_type']
                s.data.update({'staff_type': staff_type})
                s.save()

    def get_past_students(self, url=''):
        if not url:
            url = self.past_student_url
        resp = requests.get(url, headers=self.headers)
        if resp.ok:
            data = resp.json()['data']
            for con in data:
                email = con['general_info']['email_address']
                first_name = con['general_info']['firstname']
                last_name = con['general_info']['surname']
                if email:
                    if is_email_valid(email):
                        pass  # Do something with this contact
                    else:
                        print("%s %s has invalid email address %s" % (first_name, last_name, email))
                else:
                    print("%s %s has no email address" % (first_name, last_name))
        return resp

    def get_all_past_students(self):
        resp = self.get_past_students()
        if resp.ok:
            next_url = resp.json()['pagination']['next']
            while next_url:
                resp = self.get_past_students(url=next_url)
                try:
                    next_url = resp.json()['pagination']['next']
                except KeyError:
                    return
