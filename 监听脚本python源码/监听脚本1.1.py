from flask import Flask, request
import requests
import tkinter as tk
from threading import Thread
import queue
from tkinter import messagebox
import os#用于在当前目录创建文件
import datetime#用于对接收消息中的时间戳进行转换
import time

'''
request获得的json格式类似下面，其中时间time为时间戳的形式（为timestamp），
它表示从某个特定的起始时间开始经过的秒数。
通常，这样的时间戳是以 Unix 时间（从 1970 年 1 月 1 日开始计算）来计算的。
私聊：{'post_type': 'message', 'message_type': 'private', 'time': 1691225575,
'self_id': 3087161498, 'sub_type': 'friend', 'message_id': -857639481,
'user_id': 1942507075, 'target_id': 3087161498, 'message': '尝试',
'raw_message': '尝试', 'font': 0, 'sender': {'age': 0, 'nickname': '无念.',
'sex': 'unknown', 'user_id': 1942507075}}
群聊：{'post_type': 'message', 'message_type': 'group', 'time': 1692000891,
'self_id': 3087161498, 'sub_type': 'normal', 'font': 0, 'group_id': 631678147,
'message': '是的', 'raw_message': '是的', 'user_id': 1942507075, 'message_id':
-498338471, 'anonymous': None, 'message_seq': 5276,
'sender': {'age': 0, 'area': '', 'card(群聊昵称)': '夏某', 'level': '',
'nickname': '无念.', 'role（admin管理员，owner群主）': 'owner',
'sex': 'unknown', 'title': '','user_id': 1942507075}}

'''

app = Flask(__name__)

message_queue=queue.Queue()#用于flask线程存储消息流
message_filter = {}#用于存储群组ID和相应的关键字，以便在监控QQ群消息时对消息进行筛选
group_data_queue=queue.Queue()#用于存放处理过的群聊信息
private_data_queue=queue.Queue()#用于存放处理过的私聊信息

class API:
    @staticmethod#静态封装
    def send(message, target_type, target_id):
        #用于发送消息
        params = {
            "message_type": target_type,
            "group_id" if target_type == "group" else "user_id": str(target_id),
            "message": message
        }
        url = 'http://127.0.0.1:5700/send_msg'
        requests.get(url, params=params)

    @staticmethod#静态封装
    def judge(send_message):
        data = message_queue.get()
        key1=message_filter["keyword1"]
        key2=message_filter["keyword2"]
        key3=message_filter["keyword3"]
        message_type = data['message_type']
        if message_type == 'group':
            group_id = data['group_id']
            order_group_id=message_filter["group_id"]
            if str(group_id) == str(order_group_id):
                message = data['message']
                if (key1 in message and key1 !='') or (key2 in message and key2!='') or (key3 in message and key3!=''):
                    user_id = data['user_id']
                    API.send(send_message, 'private', user_id)

def timestamp_transform(timestamp):
    '''
首先将时间戳转换为 datetime 对象，然后使用 strftime 方法将其格式化为字符串。"%Y
-%m-%d %H:%M:%S" 是格式化字符串，其中 %Y 表示年份，%m 表示月份，%d 表示日期，%H
表示小时，%M 表示分钟，%S 表示秒钟。
    '''
    dt_object = datetime.datetime.fromtimestamp(timestamp)
    formatted_time = dt_object.strftime("%Y-%m-%d %H:%M:%S")
    return formatted_time
    
def role_judge(role):
    if role == 'admin':
        return "管理员"
    elif role == 'owner':
        return "群主"
    else :
        return "无头衔"

def start_monitoring():
    flask_thread=Thread(target=run_flask_thread)#开启flask线程
    flask_thread.start()

NUM=1

@app.route('/', methods=["POST"])
#就近原则匹配到最近的函数
#定义了一个路由规则，即当接收到一个 POST 请求并且路径为 / 时，会调用 post_data 函数来处理请求
def post_data():
    data = request.get_json()
    if data['post_type'] == 'message':
        message_queue.put(data)#将消息元素放入消息队列当中
        if data['message_type'] == 'group':#群聊消息
            group_message_data={}
            time=timestamp_transform(int(data['time']))
            group_message_data['time']=time
            group_message_data['sender']=data['sender']
            group_message_data['message']=data['message']
            group_message_data['group_id']=data['group_id']
            group_data_queue.put(group_message_data)
        elif data['message_type'] == 'private':#私聊消息
            private_message_data={}
            time=timestamp_transform(data['time'])
            private_message_data['time']=time
            private_message_data['sender']=data['sender']
            private_message_data['message']=data['message']
            private_data_queue.put(private_message_data)
        print('正在处理')
        send_message=message_filter["send_message"]
        API.judge(send_message)
    else:
        print('暂不处理')
    return "OK"

def show_first_time_message():
    user_data_dir = "user_data"
    if not os.path.exists(user_data_dir):
        os.makedirs(user_data_dir)

    first_time_file = os.path.join(user_data_dir, "first_time1.1.txt")
    if not os.path.exists(first_time_file):
        messagebox.showinfo("Updata", "更新内容（版本1.1）：对某些bug进行修复，同时添加一个监控窗口，\n对指定群聊消息进行监测。")
        with open(first_time_file, "w") as file:
            file.write("Visited")
            
def gui_thread():
    def apply_filter():
        #上传数据给筛选条件字典
        group_id = group_entry.get().replace('\n','')
        keyword1 = keyword1_entry.get().replace('\n','')
        keyword2 = keyword2_entry.get().replace('\n','')
        keyword3 = keyword3_entry.get().replace('\n','')
        send_message = send_message_entry.get().replace('\n','')
        message_filter["group_id"] = group_id
        message_filter["keyword1"] = keyword1
        message_filter["keyword2"] = keyword2
        message_filter["keyword3"] = keyword3
        message_filter["send_message"] = send_message

    def update_monitor_text():
        if ("group_id" in message_filter) and (message_filter["group_id"].replace(" ","")!=""):
            order_group_id = message_filter['group_id']
            monitor_text.delete(1.0, tk.END)
            monitor_text.insert(tk.INSERT, f"现在对您所输入的群聊:{order_group_id}进行监控,消息如下:\n" )              
            while True:
                if not group_data_queue.empty():
                    data = group_data_queue.get()
                    reatime = data['time']
                    sender = data['sender']
                    message = data['message']
                    group_id = data['group_id']
                    sender_card = sender['card']
                    if sender_card == "":
                        sender_card = sender['nickname']
                    sender_nickname = sender['nickname']
                    sender_id = sender['user_id']
                    role = role_judge(sender['role'])
                    order_group_id = message_filter['group_id']
                    if str(group_id) == str(order_group_id):
                        monitor_text.insert(tk.INSERT, f"{reatime}\n", "time")
                        monitor_text.insert(tk.INSERT, f"{role} ", "role")
                        monitor_text.insert(tk.INSERT, f"{sender_card}", "sender_card")
                        monitor_text.insert(tk.INSERT, f"(用户id:{sender_nickname},用户QQ号:{sender_id}):", "sender")
                        monitor_text.insert(tk.INSERT, f"{message}\n")
                windowgui.update()

    windowgui = tk.Tk()
    windowgui.title("QQ监听脚本1.1")
    windowgui.geometry("610x700")
    windowgui.resizable(False, False)

    gui=tk.Frame(windowgui)

    empty_label=tk.Label(gui)
    empty_label.grid(row=0,column=1)
    
    help_button = tk.Button(gui,text="使用说明",command=lambda:[help_frame.grid(),gui.grid_forget()])
    help_button.grid(row=1,column=1)

    empty_bea_label=tk.Label(gui)
    empty_bea_label.grid(row=2,column=1)
    
    help_frame=tk.Frame(windowgui)
    
    help_label=tk.Label(help_frame
                        ,text="""
                                                    使用说明：                   
    本程序用于监控QQ中某个特定群聊中符合条件的消息，程序开发基于go-cqhttp机器人框
架。可以通过网站https://docs.go-cqhttp.org自行下载go-cqhttp并按照其要求进行相对应
的配置(提醒：最近由于QQ风控严重，可能使用go-cqhttp时会导致QQ封号，但只会短暂封号，
经过第一次封禁后，直接申请后会解封，后续就不会连续封号，再次声明封号与本程序无关，
账号封禁是因为go-cqhttp的接口风控等问题导致)。使用该程序前，请确定后台go-cqhttp已
经配置好并挂起，该程序默认监听端口为5701，所以请将go-cqhttp的反向HTTP端口设置为57
01，否则该程序无法生效！
    以上为使用程序的前置要求，在完成上述要求后，启动本程序，输入需要监听的QQ群号，
关键词和需要发送的消息，点击上传后，再点击开始监听，此时程序若无警告弹窗，则证明其
已经开始监听。开始监听后，会对含有关键词的消息（包含任意关键词，而非要求包含所有关
键词）进行筛查，发现有满足的消息后，会对发送该消息的人发送输入的要求发送的消息，注
意：该程序不会自动停止，即若后续有人再次发送满足条件的消息，仍会再次发送要求发送的
消息！所以想要停止发送，请停止该程序（处于版本1.0阶段，在测试中，请见谅）。
    例如：输入群号123，关键词“是的”（输入时不用打引号）,“ok”,发送消息“成功”，
就会对群号123中的消息进行监控，如果李四发送如“是的我在”或“可以我ok的“消息时，该
程序会自动给李四发送“成功”。但是后续张三发送“是的我在”，程序也会自动化给张三发
送“成功”，若在给李四发送后，不想给张三发，就在给李四发送后，手动停止程序。
    提醒：本程序只能和是好友的人发送消息。
    注意：该程序长时间挂着会导致电脑发热，避免发生不必要的麻烦，记得在电脑过热时将程
序关闭，同时由于本程序打开时，也会有终端弹窗出现，为正常显示情况，在关闭程序时，也要
将终端关闭，不然程序实际上仍然有一部分功能在运行，请大家注意！
    版本1.1可能会含有不少bug，所以在使用时遇到bug，请与开发者进行联系，开发者email：
2378145658@qq.com
    """, anchor="w" ,justify="left")
    help_label.grid(row=0,column=1)

    empty_bea_label1=tk.Label(help_frame)
    empty_bea_label1.grid(row=0,column=0,padx=20)
    empty_bea_label2=tk.Label(help_frame)
    empty_bea_label2.grid(row=0,column=2)
    
    back_button=tk.Button(help_frame,text="返回",command=lambda:[help_frame.grid_forget(),gui.grid()])
    back_button.grid(row=1,column=1)

    group_label = tk.Label(gui, text="QQ群号：")
    group_label.grid(row=3,column=1)

    group_entry = tk.Entry(gui)
    group_entry.grid(row=4,column=1)

    keyword_label = tk.Label(gui, text="关键字：")
    keyword_label.grid(row=5,column=1)

    keyword1_entry = tk.Entry(gui)
    keyword1_entry.grid(row=6,column=0,padx=10)
    keyword2_entry = tk.Entry(gui)
    keyword2_entry.grid(row=6,column=1,padx=10)
    keyword3_entry = tk.Entry(gui)
    keyword3_entry.grid(row=6,column=2,padx=10)

    send_message_label=tk.Label(gui,text="需要发送的字段")
    send_message_label.grid(row=7,column=1)
    send_message_entry=tk.Entry(gui)
    send_message_entry.grid(row=8,column=1)

    empty_label1=tk.Label(gui)
    empty_label1.grid(row=9,column=1)
    
    filter_button = tk.Button(gui, text="上传关键字,QQ群号\n和需要发送的消息", command=apply_filter)
    filter_button.grid(row=10,column=1)

    empty_label2=tk.Label(gui)
    empty_label2.grid(row=11)

    #通过按钮实时对flask线程的开启
    start_monitor_button = tk.Button(gui, text="开始监控", command=lambda:[start_monitoring(),update_monitor_text()])
    start_monitor_button.grid(row=12,column=1)

    monitor_text=tk.Text(gui,height=20,width=40)
    monitor_text.grid(row=13,column=1)

    monitor_text.tag_config("role",foreground="green",font=("Arial", 10 ,"bold"))#头衔加粗加大绿色
    monitor_text.tag_config("time",foreground="blue",font=("Arial", 10 ))#时间蓝色
    monitor_text.tag_config("sender_card",foreground="brown",font=("Arial", 9 ,"bold"))#群昵称棕色
    monitor_text.tag_config("sender",foreground="gray",font=("Arial", 9 ,"bold"))#灰色其他信息

    
    gui.grid()

    windowgui.mainloop()

def run_flask_thread():
    #开启flask线程，监听go-cqhttp的监听窗口
    if ("group_id" in message_filter) and (message_filter["group_id"].replace(" ","")!=""):
        #保证在输入监听群号后，再进行监听，避免报错
        if message_filter["send_message"] != "":
            key1=message_filter["keyword1"]
            key2=message_filter["keyword2"]
            key3=message_filter["keyword3"]
            if (key1 == '') and (key2 == '') and (key3 == ''):
                messagebox.showinfo("Remind","您的三个关键词栏均为空或者您更新关键词栏后未更新，\n程序依然会执行。但是由于该操作会导致任何消息均不匹配，\n有违程序使用的初衷。")
            app.run(host='0.0.0.0', port=5701)            
        else :
            messagebox.showinfo("Warning!","您还没有输入发送消息\n或者还没有点击上传！")
    else :
        messagebox.showwarning("Warning!","您还没有输入监控群号或还未上传群号，\n为避免程序监控出错，请确保您输入\n群号后已经点击上传按钮！")
if __name__ == '__main__':
    gui_thread = Thread(target=gui_thread)#开启gui线程
    gui_thread.start()
    show_first_time_message()

    
    

    
