"""
I like using pymssql library to run my MS SQL server queries. This is good for most major school management systems,
except Edumate, which is using DB2.

You can find more info here:

https://github.com/pymssql/pymssql

"""

import pymssql


class MazeClient(object):
    def __init__(self):
        self.server = 'MSSQL_SERVER'  # You should store and load your secrets from os.getenv('SOME_SECRET')
        self.user = 'MSSQL_USERNAME'
        self.password = 'MSSQL_PASS'
        self.db = 'MSSQL_DBNAME'
        self.conn = pymssql.connect(self.server, self.user, self.password, self.db)
        self.q = "SELECT * FROM ST"  # Your query goes here

    def get_all_rows(self):
        rows = []
        cursor = self.conn.cursor(as_dict=True)
        cursor.execute(self.q)
        for row in cursor:
            rows.append(row)
        return rows

    def get_students_from_maze(self):
        """

        """
        cursor = self.conn.cursor(as_dict=True)
        cursor.execute(self.q)
        contacts = []
        for row in cursor:
            contact = {
                "first_name": row.get('Name_First', ''),
                # Each row in a dict and you access it like above. I like working with dictionaries so I always convert
                # my rows into dicts right away.
                # I get what I need and pass the list around. If I can get someone to write me a view at the school I
                # prefer that, but we can manipulate data here easily as well.
            }
            contacts.append(contact)
        return contacts
