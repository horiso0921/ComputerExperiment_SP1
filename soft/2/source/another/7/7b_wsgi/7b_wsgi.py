#! /usr/bin/env python3
# -*- coding: utf-8 -*-

# CGIモジュールをインポート
import cgi

# sqlite3（SQLサーバ）モジュールをインポート
import sqlite3

from datetime import datetime

def GoodSortHTML(contributions_dbname, form):
    # データベース接続とカーソル生成
    con = sqlite3.connect(contributions_dbname)
    cur = con.cursor()

    #good(int型)の多い順にソートしてリストに格納
    GoodSortList = []
    gsort = 'SELECT * FROM contributions ORDER BY good DESC'
    for row in cur.execute(gsort):
        GoodSortList.append(row)


    # いいね判定
    for i in range(len(GoodSortList)):
        if "g{}".format(i + 1) in form:
            contribution, user, date, good = GoodSortList[i]
            good += 1     #いいね押す
            cur.execute("UPDATE contributions SET good={0} WHERE contribution='{1}' and user='{2}' and date='{3}'".format(good, contribution, user, date))
            GoodSortList[i] = contribution, user, date, good
            con.commit()
            break

    cur.close()
    con.close()

    html = ""
    html += '<body>\n' \
            '<div>\n' \
            '<br>いいね！が多くついた投稿ランキング</br>\n'\
            '<table border="1" width="80%">\n' \
            '<tr><th width="10%">ユーザー</th><th width="70%">投稿本文</th><th width="10%">日時</th><th width="10%">いいね数</th><th width="20">いいね！</th></tr>\n'

    for i in range(len(GoodSortList)):
        row = GoodSortList[i]
        html += '<tr><td align="center">' + row[1] + '</td><td width="80%">' + row[0] + '</td><td>' + row[2] + '</td><td align="center">' + str(row[3]) + '</td>'\
                '<form>' \
                '<input type="hidden" name="ranking" value="ranking">' \
                '<td><input type="submit" value="GOOD" name="g' + str(i + 1) + '"></td>\n' \
                '</form>' \
                '</tr>\n'
    html += '</table>\n'\
            '</div>\n' \
            '<a href="/">マイページに戻る</a>\n' \
            '</body>\n'

    return html

def mypage(form, user, contributions_dbname):

    username = user
    html = ""

    if ('text' not in form):
        # 入力フォームの内容が空の場合（初めてページを開いた場合も含む）

        date = datetime.now().strftime('%Y/%m/%d.%H:%M')

        con = sqlite3.connect(contributions_dbname)
        cur = con.cursor()

        #SQL文(select)の作成
        sql = 'select * from contributions'

        #各ユーザのgood合計数を計算
        user_good = {}
        for data in cur.execute(sql):
            if data[1] in user_good.keys():
                user_good[data[1]] += data[3]
            else:
                user_good[data[1]] = data[3]

        #goodの多い順にソート
        user_good_sorted = sorted(user_good.items(), key=lambda x:x[1], reverse=True)
        #usernameの順位をrankに代入
        rank = user_good_sorted.index((username, user_good[username])) + 1


        searchResultList = []
        key_str = "'{}'".format(username)
        search = 'SELECT * FROM contributions WHERE user like ' + key_str
        for row in cur.execute(search):
        	searchResultList.append(row)


        con.commit()
        cur.close()
        con.close()


        # HTML
        html += '<body>\n' \
                '<div class="container">\n' \
                '<div class="area-g1">'+username+'</div>\n' \
                '<div class="area-g2">\n' \
                '<form>新規投稿\n' \
                '<div><textarea id="text" name="text" placeholder="本文を書いてください。" cols="30" rows="5"></textarea></div>\n' \
                '<div><input type="submit" value="投稿する"></input></div>\n' \
                '</form></div>\n' \
                '<div class="area-g3"><form><input type = "submit" value = "検索ページへ" name = "search" style=font-size:40pt></form></div>\n' \
                '<div class="area-g4">現在'+str(rank)+'位です</div>\n' \
                '<div class="area-g5"><form><input type = "submit" value = "最新の投稿を見る" name = "latest" style=font-size:40pt></form></div>\n' \
                '<div class="area-g0-1"></div>\n' \
                '<div class="area-g7"><form><input type = "submit" value = "ランキングを見る" name = "ranking"style=font-size:40pt ></form></div>\n' \
                '<div class="area-g0-2"></div>\n' \
                '<div class="area-g8">\n' \
                '<table border="1" width="80%">\n' \
                '<tr><th width="80%">投稿本文</th><th width="10%">日時</th><th width="10%">いいね数</th></tr>\n'\


        searchResultList.reverse()
        print_list = searchResultList[:10]
        for row in print_list:
            html += '<tr><td width="80%">' + row[0] + '</td><td>' + row[2] + '</td><td align="center">' + str(row[3]) + '</td></tr>'

        html += '</div>\n' \
                '</div>\n' \
                '</body>\n' \


    elif len(form.getvalue("text", "0")) > 140 or len(form.getvalue("text", "0")) == 0:
        html += '<body>\n' \
                '<div class="done">\n' \
                '</div>\n' \
                '文字数が不正です。1〜140字で書いてください。\n' \
                '<a href="/">マイページに戻る</a>\n' \
                '</body>\n' \




    else:

        # 入力フォームの内容が空でない場合
        date = datetime.now().strftime('%Y/%m/%d.%H:%M')

        # フォームデータから各フィールド値を取得
        contribution = form.getvalue("text", "0")

        # データベース接続とカーソル生成
        con = sqlite3.connect(contributions_dbname)
        cur = con.cursor()
        con.text_factory = str

        # SQL文（insert）の作成と実行
        sql = 'insert into contributions (contribution, user, date, good) values (?,?,?,?)'
        cur.execute(sql, (contribution, username, date, 0))
        con.commit()

        # SQL文の実行とその結果のHTML形式への変換
        html += '<body>\n' \
                '<div class="done">\n' \
                '</div>\n' \
                '投稿しました！\n' \
                '<a href="/">マイページに戻る</a>\n' \
                '</body>\n'

        # カーソルと接続を閉じる
        cur.close()
        con.close()
    return html

def LatestPostHTML(contributions_dbname, form, ):
    # データベース接続とカーソル生成
    con = sqlite3.connect(contributions_dbname)
    cur = con.cursor()

    #good(int型)の多い順にソートしてリストに格納
    LatestPostList = []
    lsort = 'SELECT * FROM contributions ORDER BY date DESC'
    for row in cur.execute(lsort):
        LatestPostList.append(row)

    # いいね判定
    for i in range(len(LatestPostList)):
        if "g{}".format(i + 1) in form:
            contribution, user, date, good = LatestPostList[i]
            good += 1     #いいね押す
            cur.execute("UPDATE contributions SET good={0} WHERE contribution='{1}' and user='{2}' and date='{3}'".format(good, contribution, user, date))
            LatestPostList[i] = contribution, user, date, good
            con.commit()
            break



    cur.close()
    con.close()

    html = ""
    html += '<body>\n' \
                '<div>\n' \
                '<br>最近の投稿</br>\n'\
                '<table border="1" width="80%">\n' \
                '<tr><th width="10%">ユーザー</th><th width="70%">投稿本文</th><th width="10%">日時</th><th width="10%">いいね数</th><th width="20">いいね！</th></tr>\n'

    for i in range(len(LatestPostList)):
    	row = LatestPostList[i]
    	html += '<tr><td align="center">' + row[1] + '</td><td width="80%">' + row[0] + '</td><td>' + row[2] + '</td><td align="center">' + str(row[3]) + '</td>'\
            '<form>' \
            '<input type="hidden" name="latest" value="latest">' \
            '<td><input type="submit" value="GOOD" name="g' + str(i + 1) + '"></td>\n' \
            '</form>' \
            '</tr>\n'
    html += '</table>\n'\
            '</div>\n' \
            '<a href="/">マイページに戻る</a>\n' \
            '</body>\n'

    return html

def login_page ():

    html=""

    #最初にページを開いた場合
    html+= '<body>\n' \
            '<br>\n' \
            '<form>\n' \
            '<div class="form1">\n' \
            '<center>\n' \
            '<input type="submit" name="new_user" value="新規登録"><br>\n' \
            '<br>\n' \
            'ユーザーネーム　 <input type="text" name="username"><br>\n' \
            'パスワード　　　 <input type="password" name="pass"><br>\n' \
            '<br>\n' \
            '<input type="submit" name="login" value="ログイン">\n' \
            '</center>\n' \
            '</form>\n' \
            '</div>\n' \
            '</body>\n'
    return html

#ログイン入力のチェックs
def check_login (users_dbname,form):
    #フォームデータから取得
    username = form.getvalue("username", "0")
    password = form.getvalue("pass", "0")

    #データベースと接続
    con = sqlite3.connect(users_dbname)
    cur = con.cursor()
    con.text_factory = str

    #入力されたユーザーネームで検索、格納
    sql='select * from users where name like "{}"'.format(username)
    users_list=[]
    for row in cur.execute(sql):
        users_list.append(row)

    html=""

    if (len(users_list)==1):
        if (username==users_list[0][0]) and (password==users_list[0][1]): #正常な場合
            html += """
                    <body>
                    ログインに成功しました
                    <a href="/">マイページに戻る</a>
                    </body>
                    """
            return [html, ('Set-Cookie', 'user-name={0}:password={1}'.format(username,password))]
        elif (password!=users_list[0][1]): #パスワードが違う
            html+= '<body>\n' \
                    '<br>\n' \
                    '<form>\n' \
                    '<div class="form1">\n' \
                    '<center>\n' \
                    '<input type="submit" name="new_user" value="新規登録"><br>\n' \
                    '<br>\n' \
                    'ユーザーネーム　 <input type="text" name="username"><br>\n' \
                    'パスワード　　　 <input type="password" name="pass"><br>\n' \
                    'パスワードが違います<br>\n' \
                    '<br>\n' \
                    '<input type="submit" name="login" value="ログイン">\n' \
                    '</center>\n' \
                    '</form>\n' \
                    '</div>\n' \
                    '</body>\n'
            return [html]
    elif (len(users_list)==0): #ユーザーネームが違う
        html+= '<body>\n' \
                '<br>\n' \
                '<form>\n' \
                '<div class="form1">\n' \
                '<center>\n' \
                '<input type="submit" name="new_user" value="新規登録"><br>\n' \
                '<br>\n' \
                'ユーザーネーム　 <input type="text" name="username"><br>\n' \
                'ユーザーネームが違います<br>\n' \
                '<br>\n' \
                'パスワード　　　 <input type="password" name="pass"><br>\n' \
                '<br>\n' \
                '<input type="submit" name="login" value="ログイン">\n' \
                '</center>\n' \
                '</form>\n' \
                '</div>\n' \
                '</body>\n'
        return [html]
    elif (password!=users_list[0][1]): #パスワードが違う
        html+= '<body>\n' \
                '<br>\n' \
                '<form>\n' \
                '<div class="form1">\n' \
                '<center>\n' \
                '<input type="submit" name="new_user" value="新規登録">\n' \
                '<br>\n' \
                'ユーザーネーム　 <input type="text" name="username"><br>\n' \
                'パスワード　　　 <input type="password" name="pass"><br>\n' \
                'パスワードが違います<br>\n' \
                '<br>\n' \
                '<input type="submit" name="login" value="ログイン">\n' \
                '</center>\n' \
                '</form>\n' \
                '</div>\n' \
                '</body>\n'
        return [html]


    cur.close()
    con.close()


    return html

#新規登録ページ作成
def newuser_page ():
    html=""
    html+='<body>\n' \
          '<div class="form1">\n' \
          '<form>\n' \
          '<br>\n' \
          '<center>\n' \
          'ユーザーネーム　(英数字20字以下)<span style="margin-right: 9px"></span> <input type="text" name="newuser"><br>\n' \
          'パスワード　(英数字8～16字) <input type="password" name="pass1"><br>\n' \
          'パスワード(確認用)<span style="margin-right: 78px"></span> <input type="password" name="pass2"><br>\n' \
          '<br>\n' \
          '<input type="submit" name="make_user" value="新規登録">\n' \
          '</center>\n' \
          '</form>\n' \
          '</div>\n' \
          '</body>\n'
    return html

#新規登録入力のチェック
def newuser_check (users_dbname, contributions_dbname, form):
    #フォームデータから取得
    newuser = form.getvalue("newuser", "0")
    pass1 = form.getvalue("pass1", "0")
    pass2 = form.getvalue("pass2", "0")

    #データベースと接続
    con = sqlite3.connect(users_dbname)
    cur = con.cursor()
    con.text_factory = str

    #入力されたユーザーネームで検索、格納
    sql='select * from users where name like "{}"'.format(newuser)
    users_list=[]
    for row in cur.execute(sql):
        users_list.append(row)

    html=""
    if (not (newuser.isalnum())) or (not (pass1.isalnum())):
        html+='<body>\n' \
              '<div class="form1">\n' \
              '<form>\n' \
              '<br>\n' \
              '<center>\n' \
              '入力は英数字のみです<br>\n' \
              '<br>\n' \
              'ユーザーネーム　(英数字20字以下)<span style="margin-right: 9px"></span> <input type="text" name="newuser"><br>\n' \
              'パスワード　(英数字8～16字) <input type="password" name="pass1"><br>\n' \
              'パスワード(確認用)<span style="margin-right: 78px"></span> <input type="password" name="pass2"><br>\n' \
              '<br>\n' \
              '<input type="submit" name="make_user" value="新規登録">\n' \
              '</center>\n' \
              '</form>\n' \
              '</div>\n' \
              '</body>\n'
        return html

    html+='<body>\n' \
          '<div class="form1">\n' \
          '<form>\n' \
          '<br>\n' \
          '<center>\n' \
          'ユーザーネーム　(英数字20字以下)<span style="margin-right: 9px"></span> <input type="text" name="newuser"><br>\n'

    if len(users_list)==0:
        if (1<=len(newuser)<=20) and (8<=len(pass1)<=16) and (pass1==pass2):
            sql = 'insert into users (name, password) values (?,?)'
            cur.execute(sql, (newuser,pass1))
            con.commit()
            cur.close()
            con.close()
            html = """
                    <body>
                    登録に成功しました
                    <a href="/">ログイン画面に戻る</a>
                    </body>
                   """
            con = sqlite3.connect(contributions_dbname)
            cur = con.cursor()
            con.text_factory = str
            sql = 'insert into contributions (contribution, user, date, good) values (?,?,?,?)'
            cur.execute(sql, ("ようこそ！Tubotterへ！", newuser, datetime.now().strftime('%Y/%m/%d.%H:%M'), 0))
            con.commit()
            cur.close()
            con.close()
            return html
        elif not (1<=len(newuser)<=20):
            html+='ユーザーネームは20字までです<br>\n' \
                  '<br>\n' \
                  'パスワード　(英数字8～16字) <input type="password" name="pass1"><br>\n' \
                  'パスワード(確認用)<span style="margin-right: 78px"></span> <input type="password" name="pass2"><br>\n'
        elif not (8<=len(pass1)<=16):
            html+='パスワード　(英数字8～16字) <input type="password" name="pass1"><br>\n' \
                  'パスワードは8～16字です<br>\n' \
                  '<br>\n' \
                  'パスワード(確認用)<span style="margin-right: 78px"></span> <input type="password" name="pass2"><br>\n'
        elif not (pass1==pass2):
            html+='パスワード　(英数字8～16字) <input type="password" name="pass1"><br>\n' \
                  'パスワード(確認用)<span style="margin-right: 78px"></span> <input type="password" name="pass2"><br>\n' \
                  '確認用には同じパスワードを入力してください<br>\n' \
                  '<br>\n'
        html+='<br>\n' \
              '<input type="submit" name="make_user" value="新規登録">\n' \
              '</center>\n' \
              '</form>\n' \
              '</div>\n' \
              '</body>\n'
        cur.close()
        con.close()
        return html
    else :
        html+='ユーザーネームが既に使われています<br>\n' \
              '<br>\n' \
              'パスワード　(英数字8～16字) <input type="password" name="pass1"><br>\n' \
              'パスワード(確認用)<span style="margin-right: 78px"></span> <input type="password" name="pass2"><br>\n' \
              '<br>\n' \
              '<input type="submit" name="make_user" value="新規登録">\n' \
              '</center>\n' \
              '</form>\n' \
              '</div>\n' \
              '</body>\n'
        return html

def returnSearchHTML():
    # 返すhtmlを生成
    html = ""
    html += '<body>\n' \
            '<div class="form1">\n' \
            '<form>\n' \
            'キーワード検索<input autofocus placeholder="キーワードを入力" maxlength="140" type="text" name="key"><br>\n' \
            '<input type="submit" value="search" name="vs">\n' \
            '</form>\n' \
            '</div>\n' \
            '</ol>\n' \
            '<a href="/">マイページに戻る</a>\n' \
            '</body>\n'

    return html


def returnSearchResultHTML(key, contributions_dbname, form, ):
    # データベース接続とカーソル生成
    con = sqlite3.connect(contributions_dbname)
    cur = con.cursor()
    con.text_factory = str

    # 投稿を検索して格納
    searchResultList = []
    key_str = "'%{}%'".format(key)
    search = 'SELECT * FROM contributions WHERE contribution like ' + key_str
    for row in cur.execute(search):
        print(row)
        searchResultList.append(row)

    # いいね判定
    for i in range(len(searchResultList)):
        if "g{}".format(i + 1) in form:
            contribution, user, date, good = searchResultList[i]
            good += 1     #いいね押す
            cur.execute("UPDATE contributions SET good={0} WHERE contribution='{1}' and user='{2}' and date='{3}'".format(good, contribution, user, date))
            searchResultList[i] = contribution, user, date, good
            con.commit()
            break

    cur.close()
    con.close()



    # 返すhtmlを生成
    html = ""
    html += '<body>\n' \
            '<div>\n' \
            '<br>【{}】で検索した結果</br>\n'\
            '<table border="1" width="80%">\n' \
            '<tr><th width="10%">ユーザー</th><th width="70%">投稿本文</th><th width="10%">日時</th><th width="10%">いいね数</th><th width="20">いいね！</th></tr>\n'.format(key)


    for i in range(len(searchResultList)):
        row = searchResultList[i]
        html += '<tr><td align="center">' + row[1] + '</td><td width="80%">' + row[0] + '</td><td>' + row[2] + '</td><td align="center">' + str(row[3]) + '</td>'\
            '<form>' \
            '<input type="hidden" name="vs" value="search">' \
            '<input type="hidden" name="key" value="' + str(key) + '">' \
            '<td><input type="submit" value="GOOD" name="g' + str(i + 1) + '"></td>\n' \
            '</form>' \
            '</tr>\n'
    html += '</table>\n'\
            '</div>\n' \
            '<a href="/">マイページに戻る</a>\n' \
            '</body>\n'

    return html

def returnCookieUser(environ=None, users_dbname=None):
    if environ == None:
        return None
    if users_dbname == None:
        return None
    cookie_str = environ.get("HTTP_COOKIE")
    if cookie_str == None:
        return None
    if not "user-name" in cookie_str or not "password" in cookie_str:
        return None
    cookies_all = cookie_str.split(";")
    for cookies_up in cookies_all:
        if "user-name" in cookies_up:
            cookies = cookies_up.split(":")

        for cookie in cookies:
            if "user-name" in cookie:
                _, username = cookie.split("=")
            if "password" in cookie:
                _, password = cookie.split("=")

    con = sqlite3.connect(users_dbname)
    cur = con.cursor()
    con.text_factory = str

    check_login_sql = "SELECT password FROM users WHERE name like '{}'".format(username)
    for row in cur.execute(check_login_sql):
        #print(row[0])
        if row[0] == password:
            return username
        else:
            None



#  # データベースファイルのパスを設定
users_dbname = '/tmp/users.db'
contributions_dbname = '/tmp/contributions.db'
#dbname = ':memory:'


# usersテーブルの作成
con = sqlite3.connect(users_dbname)
cur = con.cursor()
create_table = 'create table if not exists users (name varchar(20), password varchar(16))'
cur.execute(create_table)
con.commit()
cur.close()
con.close()

# contributionsのテーブルの作成
con = sqlite3.connect(contributions_dbname)
cur = con.cursor()
create_table = 'create table if not exists contributions (contribution varchar(140), user varchar(20), date varchar(16), good INTEGER)'
cur.execute(create_table)
con.commit()
cur.close()
con.close()


def application(environ,start_response):

    # headerの初期設定
    response_header = [('Content-Type', 'text/html; charset=utf-8')]

    # フォームデータを取得
    form = cgi.FieldStorage(environ=environ, keep_blank_values=True)
    user = returnCookieUser(environ, users_dbname)
    if user == None:
        html = '<html lang="ja">\n' \
                '<head>\n' \
                '<meta charset="UTF-8">\n' \
                '<title>Tubotter</title>\n' \

        if "login" in form:
            return_list = check_login(users_dbname, form)
            #print(return_list)
            if len(return_list) == 1:
                html += return_list[0]
            else:
                html += return_list[0]
                #print(return_list[1])
                response_header.append(return_list[1])
        elif "new_user" in form:
            html += newuser_page()
        elif "make_user" in form:
            html += newuser_check(users_dbname, contributions_dbname, form)
        else:
            html += login_page()



    if not user == None:
        html = '<html lang="ja">\n' \
           '<head>\n' \
           '<meta charset="UTF-8">\n' \
           '<title>Tubotter</title>\n' \
           '''
           <style>
           .container {
                width: 100%;
                height: 100%;
                display: grid;

                box-sizing: border-box;
                text-align: center;
                line-height: 100px;
                font-weight: bold;
                font-size: 20px;

                grid-template-columns: 0.5fr 1fr 0.5fr;
                grid-template-rows: 1fr 1fr 1fr 1fr 1fr 1fr 1fr;
                grid-template-areas: 'g1 g2 g3' 'g4 g2 g5' 'g0-1 g2 g7' 'g0-1 g8 g0-2' 'g0-1 g8 g0-2' 'g0-1 g8 g0-2' 'g0-1 g8 g0-2';
            }

            .area-g1 {
                grid-area: g1;
                margin : 30px ;
                padding : 4px ;
                border : 1px solid;
                background-color :;
            }

            .area-g2 {
                grid-area: g2;
            }

            .area-g3 {
                grid-area: g3;
            }

            .area-g4 {
                grid-area: g4;
                margin : 30px ;
                padding : 4px ;
                border : 1px solid;
                background-color :;
            }

            .area-g5 {
                grid-area: g5;
            }

            .area-g0-1 {
                grid-area: g0-1;
            }

            .area-g7 {
                grid-area: g7;
            }

            .area-g0-2 {
                grid-area: g0-2;
            }

            .area-g8 {
                grid-area: g8;
            }

            textarea {
            font-size: 160%;
            }

           </style>
           ''' \
           '</head>\n' \
           '<body>\n'

        if "ranking" in form:
            html += GoodSortHTML(contributions_dbname, form)
        elif "search" in form:
            html += returnSearchHTML()

        elif "vs" in form:
            key = form.getvalue("key", "")
            html += returnSearchResultHTML(key, contributions_dbname, form)
        elif "latest" in form:
            html += LatestPostHTML(contributions_dbname, form)

        else:
            html += mypage(form, user, contributions_dbname)










    html += '</body>\n' \
            '</html>\n'
    html = html.encode('utf-8')

    response_header.append(('Content-Length', str(len(html))))

    # レスポンス
    start_response('200 OK', response_header)
    return [html]

# リファレンスWEBサーバを起動リクルート
#  ファイルを直接実行する（python test_wsgi.py）と，
#  リファレンスWEBサーバが起動し，localhost:8080 にアクセスすると
#  このサンプルの動作が確認できる
from wsgiref import simple_server
if __name__ == '__main__':
    server = simple_server.make_server('', 8080, application)
    server.serve_forever()
