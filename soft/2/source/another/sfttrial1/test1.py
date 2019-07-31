#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sqlite3
# CGIモジュールをインポート
import cgi
import cgitb
cgitb.enable()


def main():
    #データベースに接続する
    conn = sqlite3.connect('example.db')
    c = conn.cursor()
    #テーブルがなければ作成
    c.execute('CREATE TABLE IF NOT EXISTS users10(id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, password TEXT)')
    





    a = input("新規登録ならy ")
    if a == "y":
        w = 0
        while(w == 0):
            w = register(c,conn)
    userID = 0
    while(userID == 0):
        userID = check(c)

    #データベースへのアクセスが終わったら close する
    conn.close()

    return userID


def check(c):
    rogin = 0
    username = input("ユーザー名 ")
    password = input("パスワード ")
    index = c.execute('SELECT * FROM users10')
    for row in index:
        if username == row[1]:
            if password == row[2]:
                print("ログインしました")
                rogin = 1
                return row[0]
            else:
                print("パスワードが違います")
                rogin = 2
                return 0
    if rogin == 0:
        print("そのユーザーは登録されていません")
        return 0

def register(c,conn):
    username = input("ユーザー名 ")
    password = input("パスワード ")
    #登録済のユーザー名でないかを確認
    index = c.execute('SELECT * FROM users10')
    for row in index:
        if username == row[1]:
            print("そのユーザー名は登録済です")
            return 0

    #データの挿入
    ins_str = 'INSERT INTO users10(username, password) VALUES(?, ?)'
    c.execute(ins_str, (username,password))

    #挿入した結果を保存（コミット）する
    conn.commit()
    
    #確認のため表示
    c = c.execute('SELECT * FROM users10')
    for row in c:
        print(row[0],row[1],row[2])

    print("登録完了")
    return 1

x = main()
print("ログインした番号は" + str(x) + "です")
