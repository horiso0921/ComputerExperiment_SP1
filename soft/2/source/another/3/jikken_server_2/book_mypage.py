#! /user/bin/python
# -*- coding: utf-8 -*-

#マイページを表示する関数
def mypage(formDataSet, user_id,con):

  html = ""

  cur = con.cursor()
  
  #書籍ID、タイトル、著者をカラムにもったbooksテーブルを生成
  create_books = 'create table if not exists books(bookId int, title varchar(64), author varchar(64))'
  cur.execute(create_books)
  con.commit()


  #ユーザID、書籍IDカラムにもったbookmarksテーブルを生成
  create_bookmarks = 'create table if not exists bookmarks(name text, bookId int, rating int, updateDate text)'
  cur.execute(create_bookmarks)
  con.commit()

  
  #表のラベルを追加
  html += "<table style = 'border-collapse: collapse;'>\n"\
      "<tr style = 'background-color: #3F51B5;'>\n"\
      "<th>タイトル</th>\n"\
      "<th>著者</th>\n"\
      "</tr>\n"

  #ログイン中のユーザIDとbookmarkテーブルのユーザIDが一致する書籍IDを検索
  bookmarks_serch = "select bookId from bookmarks where name = '" + str(user_id)+"'"
  #書籍IDが一致するものをaozoraから検索する
  cur.execute(bookmarks_serch)
  for row in cur.fetchall():
    books_serch = "select title, author from books where bookId = '" + str(row[0])+"'"
  #タイトル、著者を表示
    cur.execute(books_serch)
    for ROW in cur.fetchall():
      html += "<tr>\n"\
                "<td>"+str(ROW[0])+"</td>\n"\
                "<td>"+str(ROW[1])+"</td>\n"\
               "</tr>\n"
  html += "</table>\n"

  #編集ページと検索ページへのリンク
  
  html += '<!--\n'\
          '.btn-square {\n'\
          'display: inline-block;\n'\
          'padding: 0.5em 1em;\n'\
          'text-decoration: none;\n'\
          'background: #668ad8;\n'\
          'color: #FFF;\n'\
          'border-bottom: solid 4px #627295;\n'\
          'border-radius: 3px;\n'\
          '}\m'\
          '.btn-square:active {\n'\
          '-webkit-transform: translateY(4px);\n'\
          'transform: translateY(4px);\n'\
          'border-bottom: none;\n'\
          '}\n'\
          '--!>\n'\
          '<a href="/?page=edit" class="btn-square">ブックマークを編集</a>\n'\
          '<a href="/?page=search" class="btn-square">書籍を検索</a>\n'



  return html

  
