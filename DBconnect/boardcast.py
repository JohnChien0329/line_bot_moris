'''
import configparser
from linebot import (
    LineBotApi, WebhookHandler
)
from RDS import (
    Db_Connect
)

#basic info
config = configparser.ConfigParser()
config.read('config.ini')

line_bot_api = LineBotApi(config.get('line-bot','channel_access_token'))
handler = WebhookHandler(config.get('line-bot','channel_secret'))

#input contrbute level, return list of user_id
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

_Contribute = input("get Contribute = ")
UserList = Db_GetListofUserId(_Contribute)


#print(UserList)
#傳送訊息

#line_bot_api.multicast(UserList, TextSendMessage(text='Hello World!'))
'''