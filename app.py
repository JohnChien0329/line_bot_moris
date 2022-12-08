#app.py
import os
import io
import configparser
import DBconnect
import requests
import time
from PIL import Image
from flask import Flask, request, abort
from flask import send_from_directory

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage, ImageMessage
)
from DBconnect.RDS import (
    Db_GetUserContribute, Db_GetListofUserId
)

app = Flask(__name__)

#basic info
config = configparser.ConfigParser()
config.read('config.ini')

line_bot_api = LineBotApi(config.get('line-bot','channel_access_token'))
handler = WebhookHandler(config.get('line-bot','channel_secret'))

rank_dict = {"0":"黃金","1":"白金","2":"鑽石"}

@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def handle_text_message(event):
    if event.message.text == "用戶等級" :
        UserId = event.source.user_id
        try:
            user_rank = Db_GetUserContribute(UserId)
            response = rank_dict[str(user_rank)]
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text="您是" + response + "會員"))
        except:
            print("user_rank: " +user_rank)
            print("response: " + response)
            print("UserId:" + UserId)
            abort(404)
    else:
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=event.message.text))
        
@handler.add(MessageEvent, message=ImageMessage)
def handle_image_message(event):
    app.logger.info(event)
    post_photo_url = "http://3.87.21.158/"
    app.logger.info(event.message.id)
    message_id = event.message.id
    app.logger.info(message_id)
    
    binary_photo_from_line = line_bot_api.get_message_content(message_id)
    # app.logger.info(binary_photo_from_line)
    
    
    
    try:
        path = './static/content_img.jpg'
    
        with open(path,'wb') as fd:
             for chunk in binary_photo_from_line.iter_content():
                fd.write(chunk)
        '''    
        byte_stream = io.ByteIO(binary_photo_from_line)
        image = Image.open(byte_stream)
        '''
    except:
        app.logger.info("error!")
        abort(404)
        
    form_data = {'file','./static/content_img.jpg'}
    r = requests.post(post_photo_url, data=form_data)
    app.logger.info(r)
    time.sleep(8)
    line_bot_api.reply_message(
        event.reply_token,
        ImageMessage(post_photo_url + "output/heatmap.jpg","demo.jpg")
    )

@app.route('/boardcast/<user_rank>', methods = ['POST'])
def BoardcastByRank(user_rank):
    if request.is_json:
        data = request.get_json()
    else:
        abort(404)
    try:
        TargetUserList = Db_GetListofUserId(user_rank)
        MessageToSend = data["message"]
        line_bot_api.multicast(TargetUserList, TextSendMessage(text=MessageToSend))
        return 'Success'
    except:
        print("TargetUserList:" + TargetUserList)
        print("MessageToSend:" + MessageToSend)
        print("data:" + data)
        abort(404)
    
@app.route('/output/<name>')
def output_file(name):
    return send_from_directory('./static', name)

@app.route('/test')
def test():
    return 'Success'


if __name__ == "__main__":
    app.run(host='0.0.0.0',debug=True,port=5000)