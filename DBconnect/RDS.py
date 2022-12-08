from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import *
from pymysql import *

import pymysql

def Db_Connect():
    #資料庫連線設定
    db = pymysql.connect(host='mysqltest1.c1ugvgdbqcqy.us-east-1.rds.amazonaws.com', port=3306, user='admin', passwd='john80842', db='linebot', charset='utf8')
    return db

def Db_GenerateUserContribute(UserId):
    db = Db_Connect()
    #建立操作游標
    #SQL語法
    sql = "INSERT INTO user_info(UserId, Contribution) VALUES ('"+UserId+"','0')"
    cursor = db.cursor()
    #執行語法
    try:
        cursor.execute(sql)
    #提交修改
        db.commit()
        print('success')
    except:
    #發生錯誤時停止執行SQL
        db.rollback()
        print('error')
    #關閉連線
    db.close()

#判斷是否有這個人並回傳相關資料或創建使用者
def Db_GetUserContribute(_UserId):
    db = Db_Connect()
    cursor = db.cursor()
    sql = "SELECT * FROM user_info  WHERE UserId = '" + _UserId + "'" 
    cursor.execute(sql)
    # 獲取所有記錄列表
    results = cursor.fetchone()
    #print(results)
    if results != None:
        UserId = results[0]
        Contribute = results[1]
        return int(Contribute)
    elif  results == None:
        print("genetate ID =" + _UserId)
        Db_GenerateUserContribute(_UserId)
        return 0
    db.close()

def Db_GetListofUserId(_Contribute):
    
    db = Db_Connect()
    cursor = db.cursor()
    sql = "SELECT UserId FROM user_info  WHERE Contribution = '" + _Contribute + "'"
    cursor.execute(sql)
    results = cursor.fetchall()

    #修改成line的格式
    results = str(results)
    #print('origin type')
    #print(type(results))
    results = results.replace("(", "")
    results = results.replace(")", "")
    results = results.replace(",,", ",")
    results = results.replace("'", "")
    results = results.split(', ')
    results[-1] = results[-1][:-1]

    #print('final type')
    #print(type(results))
    db.close()
    return results