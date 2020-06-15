import sqlite3
import datetime

class DataBase():
    def __init__(self):
        self.conn = sqlite3.connect("inst_db.db")
        self.cursor = self.conn.cursor()
    
    def execute_sql(self, sql):
        self.cursor.execute(sql)
        self.conn.commit()
    
    def _create_account_table(self):
        sql = """CREATE TABLE Accounts
                (login text primary key,
                 last_update text not null)"""
        self.cursor.execute(sql)
    
    def _create_hashtags_table(self):
        sql = """CREATE TABLE Hashtags
                 (login text not null,
                 hashtag text not null,
                 FOREIGN KEY (login) REFERENCES Acounts(login)
                 ON DELETE CASCADE)"""
        self.cursor.execute(sql)

    def _create_stories_table(self):
        sql = """CREATE TABLE Stories
                 (login text not null,
                 story_owner text not null,
                 date text not null,
                 FOREIGN KEY (login) REFERENCES Acounts(login)
                 ON DELETE CASCADE)"""
        self.cursor.execute(sql)
    
    def _create_subscriptions_table(self):
        sql = """CREATE TABLE Subscriptions
                 (login text not null,
                 subscription text not null,
                 date text not null,
                 FOREIGN KEY (login) REFERENCES Acounts(login)
                 ON DELETE CASCADE)"""
        self.cursor.execute(sql)
    
    def _create_history_table(self):
        sql = """CREATE TABLE History
                 (login text not null,
                 action text not null,
                 target text not null,
                 date text not null,
                 FOREIGN KEY (login) REFERENCES Acounts(login)
                 ON DELETE CASCADE)"""
        self.cursor.execute(sql)

    def init_tables(self):
        response = ""
        try:
            self._create_account_table()
        except sqlite3.OperationalError:
            response += "table Accounts already exists\n"
        try:
            self._create_hashtags_table()
        except sqlite3.OperationalError:
            response += "table Hashtags already exists\n"
        try:
            self._create_subscriptions_table()
        except sqlite3.OperationalError:
            response += "table Subscriptions already exists\n"
        try:
            self._create_stories_table()
        except sqlite3.OperationalError:
            response += 'table Stories already exists\n'
        try:
            self._create_history_table()
        except sqlite3.OperationalError:
            response += 'table History already exists\n'
        return response
    
    def add_action(self, login, action, target, date = None):
        if date == None:
            date = datetime.datetime.utcnow()
        sql = """INSERT INTO History (login, action, target, date)
                 VALUES ('{}', '{}', '{}', '{}')""".format(login, action, target, date)
        self.execute_sql(sql)

    def add_new_user(self, login, date = None):
        sql = """SELECT * FROM Accounts WHERE login = '{}'""".format(login)
        self.execute_sql(sql)
        user = self.cursor.fetchall()
        if len(user) == 0:
            if date == None:
                date = datetime.datetime.utcnow()
            sql = """INSERT INTO Accounts (login, last_update)
                     VALUES ('{}', '{}')""".format(login, date)
            self.execute_sql(sql)
            return True
        else:
            return False
    
    def update_user(self, login):
        sql = """UPDATE Accounts SET last_update = '{}' WHERE login = '{}'""".format(datetime.datetime.utcnow(), login)
        self.execute_sql(sql)
        