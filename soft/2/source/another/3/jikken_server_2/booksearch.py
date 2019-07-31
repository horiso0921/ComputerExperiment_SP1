# -*- coding: utf-8 -*-
import cgi
import sqlite3

def booksearch(formDataSet,user_id,con):
    form = formDataSet["GET"]
    cur = con.cursor()
    try:
        cur.execute('create table books(bookId int,title varchar(64), author verchar(64))')

    except:
        pass

    bookdata = "empty"
    if "book" in form:
        bookdata = form["book"]
    Author = "empty"
    if "writer" in form:
        Author = form["writer"]
    print(bookdata,Author)
    html = ''\
        '<p id = "search">'\
        '著者名か書籍名,または両方に入力して検索</br>'\
        '</p>'\
        '<!-- 検索ウィンドウ -->'\
        '<form target = "_self">'\
        '著者名 <input type = "text" name = "writer"/>'\
        '書籍名 <input type = "text" name = "book" />'\
            '<input type = "submit" value = "検索"/>'\
            '<input type = "hidden" name = "page" value = "search">'\
        '</form>'\
        '<!-- 検索結果を表示 -->'
    if (bookdata == "empty") and (Author != "empty"):
        query = 'select bookId,author,title from books where author like ?'
        cur.execute(query,(Author,))
    elif (Author == "empty") and (bookdata != "empty"):
        query = 'select bookId,author, title from books where title like ?'
        cur.execute(query,(bookdata,))
    else:
        query = 'select bookId,author, title from books where title like ? and author like ?'
        cur.execute(query,(bookdata,Author))

    result = cur.fetchall()
    print(result)

    html += '<table border="5" cellpadding="5" cellspacing="5" width="100%">'\
        '<tr>'\
        '<th></th>'\
        '<th>著作者名</th>'\
        '<th>書籍名</th>'\
        '<th>詳細</th>'\
        '</tr>'
    i = 1

    for row in result:
        html += '<tr>'\
            '<td>'+str(i)+'</td><td>'+row[1]+'</td><td>'+row[2]+'</td><td><a href= "/?page=detail&bookId='+str(row[0])+'">詳細</a></td>'\
            '</tr>\n'

        i += 1
    html +='</table>'
    return html
