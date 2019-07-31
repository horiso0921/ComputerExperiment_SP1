import db
import sqlite3

con = sqlite3.connect(db.DATABASE_FILE)
con.text_factory = str
cur = con.cursor()
create_table = 'create table {} ({} text, {} text)'.format(db.USER_TABLE_NAME, db.USER_TABLE_NAME_FIELD, db.USER_TABLE_PASS_FIELD)
try:
    cur.execute(create_table)
    con.commit()
except sqlite3.OperationalError:
    pass

create_table = 'create table {} ( {} text, {} text, {} real)'.format(db.TWEET_TABLE_NAME, db.TWEET_TABLE_CONTENT_FIELD, db.TWEET_TABLE_USER_FIELD, db.TWEET_TABLE_DATE_FIELD)
try:
    cur.execute(create_table)
    con.commit()
except sqlite3.OperationalError:
    pass

create_table = 'create table {} ({} text, {} text)'.format(db.SESSION_TABLE_NAME, db.SESSION_TABLE_TOKEN_FIELD, db.SESSION_TABLE_NAME_FIELD)
try:
    cur.execute(create_table)
    con.commit()
except sqlite3.OperationalError:
    pass

con.close()
