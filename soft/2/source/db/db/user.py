import db
from datetime import datetime

class User:
    # インスタンス変数名 型 説明
    # name String ユーザ名

    # ユーザを作成する(新規登録)
    # 引数名 型
    # name String
    # password String
    @classmethod
    def CreateNewUser(self, name, password):
        d = db.DB()
        d.write('insert into {} values ("{}","{}")'.format(db.USER_TABLE_NAME, name, password))
        d.write('create table {} (name text)'.format(db.FOLLOWING_TABLE_NAME_BASE + name))
        d.write('create table {} (name text)'.format(db.FOLLOWERS_TABLE_NAME_BASE + name))

    # 内部で利用するコンストラクタ
    # これを直接呼び出さないこと
    def __init__(self, name):
        self.name = name

    # フォローしているUserの配列を返す
    def following(self):
        ret = []
        d = db.DB()
        for name in d.read('select * from ' + db.FOLLOWING_TABLE_NAME_BASE + self.name):
            ret.append(User(name[0]))
        return ret

    # フォロワーされている(フォロワー)Userの配列を返す
    def followers(self):
        ret = []
        d = db.DB()
        for name in d.read('select * from ' + db.FOLLOWERS_TABLE_NAME_BASE + self.name):
            ret.append(User(name[0]))
        return ret

    # userをフォローする
    # 引数名 型
    # user User
    def follow(self, user):
        d = db.DB()
        d.write('insert into {} values ("{}")'.format(db.FOLLOWING_TABLE_NAME_BASE + self.name, user.name))
        d.write('insert into {} values ("{}")'.format(db.FOLLOWERS_TABLE_NAME_BASE + user.name, self.name))

    # contentの内容をツイートする
    # 引数名 型
    # content String
    def tweet(self, content):
        db.DB().write('insert into {} values ("{}", "{}", {})'.format(db.TWEET_TABLE_NAME, content, self.name, datetime.now().timestamp()))
        pass
