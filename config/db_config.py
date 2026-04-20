import mysql.connector

class DBConnection:
    def __init__(self):
        self.connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="autonexus"
        )
        self.cursor = self.connection.cursor()

    def execute(self, query, values=None):
        if values:
            self.cursor.execute(query, values)
        else:
            self.cursor.execute(query)
        self.connection.commit()

    def fetch(self, query):
        self.cursor.execute(query)
        return self.cursor.fetchall()