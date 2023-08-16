from flask import Flask,request
import requests
import tkinter as tk

app=Flask(__name__)

class API:
    @staticmethod
    def send(message, target_type, target_id):
        params = {
            "message_type": target_type,
            "group_id" if target_type == "group" else "user_id": str(target_id),
            "message": message
        }
        url = 'http://127.0.0.1:5700/send_msg'
        requests.get(url, params=params)

    @staticmethod
    def judge(send_message):
        data = request.get_json()
        message_type = data['message_type']
        if message_type == 'group':
            group_id = data['group_id']
            if str(group_id) == "631678147":
                message = data['message']
                if "图书馆值班" in message or "值班室值班" in message:
                    user_id = data['user_id']
                    API.send(send_message, 'private', user_id)                 
                    
@app.route('/',methods=["POST"])

def post_data():
    data=request.get_json()
    if data['post_type']=='message':
        message=data['message']
        print(data)
        API.judge('成功')
    else:
        print('暂不处理')
    return "OK"

if __name__=='__main__':
    app.run(host='0.0.0.0', port=5701)
    
    
