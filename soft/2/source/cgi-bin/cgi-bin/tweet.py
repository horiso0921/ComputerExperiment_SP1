# -*- coding: utf-8 -*-
import sys
sys.path.append("/var/www/cgi-bin")
from datetime import datetime
import db
class Tweet:
    # インスタンス変数名 型 説明
    # content String ツイート内容
    # user User ツイートしたユーザ
    # date datetime.datetime ツイートした日付

    # 内部で利用するコンストラクタ
    # これを直接呼び出さないこと
    def __init__(self, content, user, date):
        self.content = content
        self.user = user
        self.date = date

    # 条件に合うツイートを検索し，Tweetの配列を返す
    # 引数名 型 説明
    # content String ツイートの内容 *で指定しない
    # user String ツイートしたユーザのユーザ名 *なら指定しない
    # dates (datetime.datetime, datetime.datetime) 検索する日付の範囲
    @classmethod
    def search(cls, content = "", user = "", date = (datetime.fromtimestamp(0), datetime.now())):
        cmd = "select * from {} where date between {} and {}".format(db.TWEET_TABLE_NAME, date[0].timestamp(), date[1].timestamp())
        args = []
        if content != "":
            cmd += " and content like ?"
            args.append("%{}%".format(content))
        if user != "":
            cmd += ' and user == ?'
            args.append(user)
        d = db.DB()
        ret = []
        for tweet in d.read(cmd, tuple(args)):
            ret.append(Tweet(tweet[0], tweet[1], datetime.fromtimestamp(tweet[2])))
        return ret
