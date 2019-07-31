import db
from user import User
from secrets import token_hex

class Session:
    # インスタンス変数名 型 説明
    # user User 現在ログインしているユーザ

    # 新しいセッションを登録(ログイン)する
    # nameとpasswordの組み合わせが正しければcookieの設定文を返すので，HTTPレスポンスのヘッダに追加すること
    # nameとpasswordの組み合わせが正しくなければ，Noneを返す
    # 引数名 型
    # name String
    # password String
    @classmethod
    def login(self, name, password):
        d = db.DB()
        storedPass = None
        for p in d.read('select {} from {} where {} == "{}"'.format(db.USER_TABLE_PASS_FIELD, db.USER_TABLE_NAME, db.USER_TABLE_NAME_FIELD, name)):
            storedPass = p[0]
            break
        if password == storedPass:
            self.user = User(name)
            token = token_hex(32)
            d.write('insert into {} values ("{}", "{}")'.format(db.SESSION_TABLE_NAME, token, name))
            return ('Set-Cookie', 'token={}'.format(token))
        return None

    # 現在のクッキー情報からログインしているセッションを取得する
    # 取得できない場合は例外を発生させる
    # 引数名 型 説明
    # cookie String environ.get('HTTP_COOKIE') で取得できる値
    def __init__(self, cookie):
        print(cookie)
        cookies = cookie.split(";")
        for aCookie in cookies:
            if 'token' in aCookie:
                dummy, token = aCookie.split("=")
                d = db.DB()
                name = None
                for n in d.read('select {} from {} where {} == "{}"'.format(db.SESSION_TABLE_NAME_FIELD, db.SESSION_TABLE_NAME, db.SESSION_TABLE_TOKEN_FIELD, token)):
                    name = n[0]
                    break
                self.user = User(name)

    # ログアウトする
    def logout(self):
        db.DB().write('delete from {} where {} == "{}"'.format(db.SESSION_TABLE_NAME, db.SESSION_TABLE_NAME_FIELD, self.user.name))