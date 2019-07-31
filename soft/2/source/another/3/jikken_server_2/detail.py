#! /usr/bin/python
# -*- coding: utf-8 -*-

import cgi
import cgitb
import sqlite3
from datetime import datetime

cgitb.enable()

def detailPage(formDataSet,uId,con):
    html = ''
    form = formDataSet["GET"]
    
    #form = cgi.FieldStorage(fp = env['wsgi.input'], environ=env,keep_blank_values=False)
        
#    referrer = form.getvalue('HTTP_REFERER', 'None')

    if "bookId" not in form :
        html += '<h1>Error</h><br>\n' \
            '<h2>無効なリクエストです</h2><br>\n' \
            'No querry bookID<br>\n' \
            '<a href="/?page=login">戻る</a><br> \n'    
        return html

    bookId = form["bookId"]
    print(bookId)
    ##DBからbookIdを検索
    cur = con.cursor()
    selectBook = 'select * from books where bookId = ?'
    cur.execute(selectBook,(bookId,))

    result = cur.fetchall()

    if len(result) < 1:
        html += '<h1>Error</h1>\n' \
            '<h3>書籍情報が存在しません</h3>\n' \
            'bookID=' + bookId + '<br>\n' \
            '<a href="/?page=login">戻る</a> \n'    
        return html
    header = ["作品ID","作品名","分類番号","公開日","最終更新日","人物ID","著者名","底本名","底本出版社名","入力者","校正者"]

    html += '<h1>'+result[0][1]+'</h1>'\
        '<dvi name="info" style="float:left;width:50%">\n'\
        '<table>\n'

    for h,x in zip(header,result[0]):
        html += '<tr>\n'\
            '<td>'+h+'</td>\n'\
            '<td>'+str(x)+'</td>\n'\
            '</tr>\n'
        
    html +='</table>\n'\
        '</dvi>\n'\
        '<dvi class="ui" style="float:left;width:50%">\n' \
        '<form action="./" method="GET">\n' \
        '<input type="hidden" name="page" value="detail">'\
        '<input type="hidden" name="bookId" value="'+bookId+'">'\
        '<button name="bookmark" value="on">ブックマークに追加</button>\n'\
        '<button name="bookmark" value="off">ブックマークから削除</button><br>\n'\
        '評価(0:最低-5:最高)<select name ="rating">\n'\
        '<option value="0">0</option>\n'\
        '<option value="1">1</option>\n'\
        '<option value="2">2</option>\n'\
        '<option value="3">3</option>\n'\
        '<option value="4">4</option>\n'\
        '<option value="5">5</option>\n'\
        '</select><br>\n'\
        '</form>\n'\
        '</dvi>\n'\
        '<dvi class ="footer" style="clear:both">\n'\
        '<a href="/?page=top">戻る</a><br> \n'\
        '</dvi>\n'
    if "bookmark" not in form or "rating" not in form:
        return html
    
    create_table = 'create table bookmarks (name text, bookId int, rating int, updateDate text)'
    try:
        cur.execute(create_table)
    except sqlite3.OperationalError:
        pass
    con.commit()
    bookmark = form["bookmark"]
    rating = form["rating"]

    #bookmark追加    
    if bookmark == 'on':  

        #重複レコードの削除
        select = ('SELECT * FROM bookmarks WHERE name = ? and bookId = ?')
        cur.execute(select,(uId,bookId))
        if len(cur.fetchall()) > 0:
            delete = ('DELETE FROM bookmarks WHERE name = ? and bookId = ?')
            cur.execute(delete,(uId,bookId))
        
        #レコードの追加
        insert = 'INSERT INTO bookmarks VALUES(?, ?, ?, ?)'
        cur.execute(insert,(uId,bookId,rating,datetime.now().strftime('%Y/%m/%d %H:%M:%S')))
    #bookmark削除
    elif bookmark == 'off':
        delete = ('DELETE FROM bookmarks WHERE name = ? and bookId = ?')
        cur.execute(delete,(uId,bookId))
    con.commit()
    cur.close()

    return(html)
