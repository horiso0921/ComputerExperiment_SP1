#! /usr/bin/env python3
# -*- coding: utf-8 -*

# CGIモジュールをインポート
import cgi
import cgitb
cgitb.enable()

# sqlite3（SQLサーバ）モジュールをインポート
import sqlite3

# データベースファイルのパスを設定
dbname = '/var/www/cgi-bin/aozorabase.db'
dbnameoki = '/tmp/favo.db'

#aozora.csvをデータベースに複写

# テーブルの作成
con = sqlite3.connect(dbname)
cur = con.cursor()
create_table = 'create table if not exists aozora (bookid text, bookname text, kindnum text, releaseday text, updateday text, authorid text, authorname text, teihonnname text, teihonnsyuppann text, nyuuryokusya text, kouseisya text)'
cur.execute(create_table)
con.commit()
cur.close()
con.close()

# テーブルの作成
conoki = sqlite3.connect(dbnameoki)
curoki = conoki.cursor()
create_table = 'create table if not exists users (favo varchar(64))'
curoki.execute(create_table)
conoki.commit()
curoki.close()
conoki.close()




def application(environ,start_response):
    # HTML（共通ヘッダ部分）
    html = '<html lang="ja">\n' \
           '<head>\n' \
           '<meta charset="UTF-8">\n' \
           '<title>マイページ</title>\n' \
           '<link rel="stylesheet" href="default.css">\n' \
           '</head>\n'

    # フォームデータを取得
    form = cgi.FieldStorage(environ=environ,keep_blank_values=True)
    if ('v1' not in form) and ('v2' not in form) and ('v7' not in form) and ('f1' not in form) and ('f2' not in form) and ('f3' not in form): 
        # 入力フォームの内容が空の場合（初めてページを開いた場合も含む）

        # HTML（入力フォーム部分）
        html += '<body>\n' \
                '<div class="form1">\n' \
                '<form>\n' \
                '本の名前 or 著者名　or お気に入り（文字列） <input type="text" name="v1"><br>\n' \
                '<input type="submit" value="決定">\n' \
                '</form>\n' \
                '</div>\n' \
                '</body>\n'




    elif (form.getvalue("v1", "0") == "お気に入り") or (('f1' in form) or ('f2' in form) or ('f3' in form)):
       if ('f1' not in form and 'f2' not in form and 'f3' not in form):
	      # 入力フォームの内容が空の場合（初めてページを開いた場合も含む）

	    # HTML（入力フォーム部分）
          html += '<body>\n' \
                  '<div class="form1">\n' \
             	    '<form>\n' \
                     'お気に入り（メモ） <input type="text" name="f1">\n' \
                  '<input type="submit" value="登録"><br>\n' \
                  '</form>\n' \
                  '</div>\n' \
                  '</body>\n'
       else:
        if('f1' in form):
		# 入力フォームの内容が空でない場合

		# フォームデータから各フィールド値を取得
           f1 = form.getvalue("f1", "0")

	      # データベース接続とカーソル生成
           conoki = sqlite3.connect(dbnameoki)
           curoki = conoki.cursor()
           conoki.text_factory = str

	      # SQL文（insert）の作成と実行
           sql = 'insert into users values (?)'
           curoki.execute(sql,(f1,))
           conoki.commit()

        elif('f2' in form):
           f2 = form.getvalue("f2", "0")
           conoki = sqlite3.connect(dbnameoki)
           curoki = conoki.cursor()
           conoki.text_factory = str
           sql = 'delete from users where favo =\"' + str(f2) + '\"'
           curoki.execute(sql)
           conoki.commit() 

        elif('f3' in form):
           conoki = sqlite3.connect(dbnameoki)
           curoki = conoki.cursor()
           conoki.text_factory = str
           sql = 'delete from users'
           curoki.execute(sql)
           conoki.commit()
        else:
           pass

        html += '<body>\n' \
                '<form>\n' \
                   'お気に入り（メモ） <input type="text" name="f1">\n' \
                '<input type="submit" value="登録"><br>\n' \
                '</form>\n' \
                '</body>\n'

	      # SQL文（select）の作成
        sql = 'select * from users'

	      # SQL文の実行とその結果のHTML形式への変換
        html += '<body>\n' \
                '<div class="ol1">\n' \
                '<ol>\n'
        for row in curoki.execute(sql):
            html += '<form>' \
                    '<li>' + str(row[0]) + '\n'\
                    '<input type="hidden" name="f2" value=\"' + str(row[0]) + '\">\n' \
                    '<input type="submit" value="削除"><br>\n' \
                    '</li>' \
                    '</form>\n' \


        html += '<form>\n' \
                '<input type="hidden" name="f3" value="a">\n' \
                '<input type="submit" value="全削除"><br>\n' \
                '</form>\n'

        html += '</ol>\n' \
                '</div>\n' \
                '<a href="/">選択ページに戻る</a>\n' \
                '</body>\n'
		   
	# カーソルと接続を閉じる
        curoki.close()
        conoki.close()









	

    elif (form.getvalue("v1", "0") == "本の名前") or ('v2' in form):
        html += '<body>\n' \
                '<div class="form1">\n' \
                '<form>\n' \
                  '本の名前 （文字列） <input type="text" name="v2"><br>\n' \
                '<input type="submit" value="検索">\n' \
                '</form>\n' \
                '</div>\n' \
                '</body>\n'


        # フォームデータから各フィールド値を取得
        v2 = form.getvalue("v2", "0")

        # データベース接続とカーソル生成
        con = sqlite3.connect(dbname)
        cur = con.cursor()
        con.text_factory = str

        # SQL文（select）の作成 bidは変数
        sql = 'select * from aozora\n' \
              'where bookname like '
        sql += '"%'+ str(v2) +'%"\n'

        # SQL文の実行とその結果のHTML形式への変換
        html += '<body>\n' \
                '<div class="ol1">\n' \
                '<ol>\n'

        for row in cur.execute(sql):
            html += '<li>' + str(row[0]) + ',' + str(row[1]) + ',' + str(row[2]) + ',' + str(row[3]) + ',' + str(row[4]) + ',' + str(row[5]) + ',' + str(row[6]) + ',' + str(row[7]) + ',' + str(row[8]) + ',' + str(row[9]) + ',' + str(row[10]) + '</li>\n'

        html += '</ol>\n' \
                '</div>\n' \
                '<a href="/">検索ページに戻る</a>\n' \
                '</body>\n'

        # カーソルと接続を閉じる
        cur.close()
        con.close()

    elif (form.getvalue("v1", "0") == "著者名") or ('v7' in form):
        html += '<body>\n' \
                '<div class="form1">\n' \
                '<form>\n' \
                '著者名　（文字列） <input type="text" name="v7"><br>\n' \
                '<input type="submit" value="検索">\n' \
                '</form>\n' \
                '</div>\n' \
                '</body>\n'

        # 入力フォームの内容が空でない場合

        # フォームデータから各フィールド値を取得
        v7 = form.getvalue("v7", "0")

        # データベース接続とカーソル生成
        con = sqlite3.connect(dbname)
        cur = con.cursor()
        con.text_factory = str

        # SQL文（select）の作成 bidは変数
        sql = 'select * from aozora\n' \
              'where authorname like '
        sql += '"%'+str(v7)+'%"\n'

        # SQL文の実行とその結果のHTML形式への変換
        html += '<body>\n' \
                '<div class="ol1">\n' \
                '<ol>\n'
#第2引数はbidに入れてる。
        for row in cur.execute(sql):
            html += '<li>' + str(row[0]) + ',' + str(row[1]) + ',' + str(row[2]) + ',' + str(row[3]) + ',' + str(row[4]) + ',' + str(row[5]) + ',' + str(row[6]) + ',' + str(row[7]) + ',' + str(row[8]) + ',' + str(row[9]) + ',' + str(row[10]) + '</li>\n'

        html += '</ol>\n' \
                '</div>\n' \
                '<a href="/">選択ページに戻る</a>\n' \
                '</body>\n'

        # カーソルと接続を閉じる
        cur.close()
        con.close()


    html += '</html>\n'
    #html = html.encode('utf-8')

    # レスポンス
    start_response('200 OK', [('Content-Type', 'text/html; charset=utf-8'),
        ('Content-Length', str(len(html))) ])
    # ここで、htmlに記述した内容を実行
    return [html]


# リファレンスWEBサーバを起動
#  ファイルを直接実行する（python test_wsgi.py）と，
#  リファレンスWEBサーバが起動し，localhost:8080 にアクセスすると
#  このサンプルの動作が確認できる
from wsgiref import simple_server
if __name__ == '__main__':
    server = simple_server.make_server('', 8080, application)
    server.serve_forever()
