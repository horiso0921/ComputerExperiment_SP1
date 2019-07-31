import sqlite3

DATABASE_FILE = "database.db"

USER_TABLE_NAME = "users"
USER_TABLE_NAME_FIELD = "name"
USER_TABLE_PASS_FIELD = "password"

FOLLOWING_TABLE_NAME_BASE = "following_"
FOLLOWERS_TABLE_NAME_BASE = "followers_"

TWEET_TABLE_NAME = "tweets"
TWEET_TABLE_CONTENT_FIELD = "content" 
TWEET_TABLE_USER_FIELD = "user"
TWEET_TABLE_DATE_FIELD = "date"

SESSION_TABLE_NAME = "sessions"
SESSION_TABLE_TOKEN_FIELD = "token"
SESSION_TABLE_NAME_FIELD = "name"

class DB:
    def __init__(self):
        self.con = sqlite3.connect(DATABASE_FILE)
        self.con.text_factory = str
        self.cur = self.con.cursor()

    def write(self, cmd):
        print(cmd)
        self.cur.execute(cmd)
        self.con.commit()


    def read(self, cmd):
        print(cmd)
        return self.cur.execute(cmd)

    def __del__(self):
        self.con.close()
