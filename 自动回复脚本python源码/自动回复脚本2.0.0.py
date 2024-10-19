from flask import Flask, request #用于创造一个Flask程序
import requests #用于请求
import tkinter as tk
from ttkthemes import ThemedTk,ThemedStyle #用于更改外观
from tkinter import ttk
from threading import Thread #用于创造多线程（不用多进程是避免消耗内存过大）
import queue #用于多线程之间传输数据
from tkinter import messagebox
import os #用于在当前目录创建文件
from datetime import datetime, timedelta,date #用于对接收消息中的时间戳进行转换,并对用户输入的时间进行处理和取值
import time #获取当前时间
import sys #用于对库进行清空
from werkzeug.serving import make_server #用于创建一个简单的 WSGI 服务器
from tkcalendar import DateEntry #用于创建一个时间选择器
import turtle#画图
app = Flask(__name__)

message_queue=queue.Queue()#用于flask线程存储消息流
message_filter = {}#用于存储群组ID和相应的关键字，以便在监控QQ群消息时对消息进行筛选
group_data_queue=queue.Queue()#用于存放处理过的群聊信息
private_data_queue=queue.Queue()#用于存放处理过的私聊信息
message_ui_queue=queue.Queue()#用于展示处理的全部信息流

flask_thread = None
gui_thread = None
flask_server = None  # 用于存储 Flask 服务器的实例
stop_flask_loop = False #用于停止Flask循环
fact_count=0 #用于计数
stop_monitor_update = False  # 声明全局变量,在推出时防止update_monitor_text中的while阻塞
show_scheduled_frame= None #声明全局变量，在已经创建该界面后，不重复创建
show_scheduled_frame=None
date_entry=None
hour_combo=None
minute_combo=None
second_combo=None
selected_datetime=None
time_symbol=None
time_update=False #用于停止time更新的函数
count_symbol_label=None
show_count_frame=None
show_sender_frame=None
pattern_start=True #用于停止pattern运行
count=0
start_monitor_button=None
click_count=0
conflict1=False
conflict2=False
update_or_symbol=True
necessary_Sym=False
keyword_Sym=False
group_Sym=False
send_msg_Sym=False
id_Sym=False
private_sym=None
group_sym=None
private=None
change=False
at_sym=False
group_change=False
change_http_post=False
change_http=False
http_change=False
http_default=True

class API:
    @staticmethod#静态封装
    def send(message, target_type, target_id):
        #用于发送消息
        global http_default,HTTP_set,HTTP_POST_set
        params = {
            "message_type": target_type,
            "group_id" if target_type == "group" else "user_id": str(target_id),
            "message": message
        }
        if http_default:
            url = 'http://127.0.0.1:5700/send_msg'
        else:
            url="http://127.0.0.1:"+f"{HTTP_set}/send_msg"
            url=url.replace(" ","")
        requests.get(url, params=params)

    @staticmethod#静态封装
    def judge(send_message):
        global fact_count,motion_select,id_sym,change,QQ,send_type,atwho,at_qq,select_watcher
        data = message_queue.get()
        key1=message_filter["keyword1"]
        key2=message_filter["keyword2"]
        key3=message_filter["keyword3"]
        nece1=message_filter["necessary1"]
        nece2=message_filter["necessary2"]
        nece3=message_filter["necessary3"]
        message_type = data['message_type']
        nece_list=[nece1,nece2,nece3]
        (Unempty_list,n)=judge_empty(nece_list)
        watcher=select_watcher.get()
        if watcher == "CerGroup":
            if message_type == 'group':
                group_id = data['group_id']
                order_group_id=message_filter["group_id"]
                if str(group_id) == str(order_group_id):
                    message = data['message']
                    if (key1 in message and key1 !='') or (key2 in message and key2!='') or (key3 in message and key3!=''):
                        if n == 0:
                            if change:#修改发消息的对象
                                user_id=int(QQ)
                                if send_type =="group":
                                    if atwho.get()=="User":
                                        user=str(data['user_id'])
                                        send_message=f"[CQ:at,qq={user}]"+send_message
                                    elif atwho.get()=="Others":
                                        others=int(at_qq.get().strip())
                                        send_message=f"[CQ:at,qq={others}]"+send_message
                            else:
                                user_id = data['user_id']
                                send_type="private"
                            API.send(send_message, send_type, user_id)
                            fact_count += 1
                        else:
                            u=0
                            for i in range(n):
                                if Unempty_list[i] in message:
                                    u+=1
                            if u == n:
                                if change:#修改发消息的对象
                                    user_id=int(QQ)
                                    if send_type =="group":
                                        if atwho.get()=="User":
                                            user=str(data['user_id'])
                                            send_message=f"[CQ:at,qq={user}]"+send_message
                                        elif atwho.get()=="Others":
                                            others=int(at_qq.get().strip())
                                            send_message=f"[CQ:at,qq={others}]"+send_message
                                else:
                                    user_id = data['user_id']
                                    send_type="private"
                                API.send(send_message, send_type, user_id)
                                fact_count += 1
                    elif key1 == '' and key2 == '' and key3 == ''and  n != 0 :
                        u=0
                        for i in range(n):
                            if Unempty_list[i] in message:
                                u+=1
                        if u == n:
                            if change:#修改发消息的对象
                                user_id=int(QQ)
                                if send_type =="group":
                                    if atwho.get()=="User":
                                        user=str(data['user_id'])
                                        send_message=f"[CQ:at,qq={user}]"+send_message
                                    elif atwho.get()=="Others":
                                        others=int(at_qq.get().strip())
                                        send_message=f"[CQ:at,qq={others}]"+send_message
                            else:
                                user_id = data['user_id']
                                send_type="private"
                            API.send(send_message, send_type, user_id)
                            fact_count += 1
                    elif n !=0 and motion_select.get() != "Strict":
                        u=0
                        for i in range(n):
                            if Unempty_list[i] in message:
                                u+=1
                        if u == n:
                            if change:#修改发消息的对象
                                user_id=int(QQ)
                                if send_type =="group":
                                    if atwho.get()=="User":
                                        user=str(data['user_id'])
                                        send_message=f"[CQ:at,qq={user}]"+send_message
                                    elif atwho.get()=="Others":
                                        others=int(at_qq.get().strip())
                                        send_message=f"[CQ:at,qq={others}]"+send_message
                            else:
                                user_id = data['user_id']
                                send_type="private"
                            API.send(send_message,send_type, user_id)
                            fact_count += 1
        if watcher == "CerPrivate":
            if message_type == 'private':
                private_id = data['user_id']
                order_private_id=message_filter["group_id"]
                if str(private_id) == str(order_private_id):
                    message = data['message']
                    if (key1 in message and key1 !='') or (key2 in message and key2!='') or (key3 in message and key3!=''):
                        if n == 0:
                            if change:#修改发消息的对象
                                user_id=int(QQ)
                                if send_type =="group":
                                    if atwho.get()=="User":
                                        user=str(data['user_id'])
                                        send_message=f"[CQ:at,qq={user}]"+send_message
                                    elif atwho.get()=="Others":
                                        others=int(at_qq.get().strip())
                                        send_message=f"[CQ:at,qq={others}]"+send_message
                            else:
                                user_id = data['user_id']
                                send_type="private"
                            API.send(send_message, send_type, user_id)
                            fact_count += 1
                        else:
                            u=0
                            for i in range(n):
                                if Unempty_list[i] in message:
                                    u+=1
                            if u == n:
                                if change:#修改发消息的对象
                                    user_id=int(QQ)
                                    if send_type =="group":
                                        if atwho.get()=="User":
                                            user=str(data['user_id'])
                                            send_message=f"[CQ:at,qq={user}]"+send_message
                                        elif atwho.get()=="Others":
                                            others=int(at_qq.get().strip())
                                            send_message=f"[CQ:at,qq={others}]"+send_message
                                else:
                                    user_id = data['user_id']
                                    send_type="private"
                                API.send(send_message, send_type, user_id)
                                fact_count += 1
                    elif key1 == '' and key2 == '' and key3 == ''and  n != 0 :
                        u=0
                        for i in range(n):
                            if Unempty_list[i] in message:
                                u+=1
                        if u == n:
                            if change:#修改发消息的对象
                                user_id=int(QQ)
                                if send_type =="group":
                                    if atwho.get()=="User":
                                        user=str(data['user_id'])
                                        send_message=f"[CQ:at,qq={user}]"+send_message
                                    elif atwho.get()=="Others":
                                        others=int(at_qq.get().strip())
                                        send_message=f"[CQ:at,qq={others}]"+send_message
                            else:
                                user_id = data['user_id']
                                send_type="private"
                            API.send(send_message, send_type, user_id)
                            fact_count += 1
                    elif n !=0 and motion_select.get() != "Strict":
                        u=0
                        for i in range(n):
                            if Unempty_list[i] in message:
                                u+=1
                        if u == n:
                            if change:#修改发消息的对象
                                user_id=int(QQ)
                                if send_type =="group":
                                    if atwho.get()=="User":
                                        user=str(data['user_id'])
                                        send_message=f"[CQ:at,qq={user}]"+send_message
                                    elif atwho.get()=="Others":
                                        others=int(at_qq.get().strip())
                                        send_message=f"[CQ:at,qq={others}]"+send_message
                            else:
                                user_id = data['user_id']
                                send_type="private"
                            API.send(send_message,send_type, user_id)
                            fact_count += 1
        if watcher == "AllPrivate":
            if message_type == 'private':
                message = data['message']
                if (key1 in message and key1 !='') or (key2 in message and key2!='') or (key3 in message and key3!=''):
                    if n == 0:
                        if change:#修改发消息的对象
                            user_id=int(QQ)
                            if send_type =="group":
                                if atwho.get()=="User":
                                    user=str(data['user_id'])
                                    send_message=f"[CQ:at,qq={user}]"+send_message
                                elif atwho.get()=="Others":
                                    others=int(at_qq.get().strip())
                                    send_message=f"[CQ:at,qq={others}]"+send_message
                        else:
                            user_id = data['user_id']
                            send_type="private"
                        API.send(send_message, send_type, user_id)
                        fact_count += 1
                    else:
                        u=0
                        for i in range(n):
                            if Unempty_list[i] in message:
                                u+=1
                        if u == n:
                            if change:#修改发消息的对象
                                user_id=int(QQ)
                                if send_type =="group":
                                    if atwho.get()=="User":
                                        user=str(data['user_id'])
                                        send_message=f"[CQ:at,qq={user}]"+send_message
                                    elif atwho.get()=="Others":
                                        others=int(at_qq.get().strip())
                                        send_message=f"[CQ:at,qq={others}]"+send_message
                            else:
                                user_id = data['user_id']
                                send_type="private"
                            API.send(send_message, send_type, user_id)
                            fact_count += 1
                elif key1 == '' and key2 == '' and key3 == ''and  n != 0 :
                    u=0
                    for i in range(n):
                        if Unempty_list[i] in message:
                            u+=1
                    if u == n:
                        if change:#修改发消息的对象
                            user_id=int(QQ)
                            if send_type =="group":
                                if atwho.get()=="User":
                                    user=str(data['user_id'])
                                    send_message=f"[CQ:at,qq={user}]"+send_message
                                elif atwho.get()=="Others":
                                    others=int(at_qq.get().strip())
                                    send_message=f"[CQ:at,qq={others}]"+send_message
                        else:
                            user_id = data['user_id']
                            send_type="private"
                        API.send(send_message, send_type, user_id)
                        fact_count += 1
                elif n !=0 and motion_select.get() != "Strict":
                    u=0
                    for i in range(n):
                        if Unempty_list[i] in message:
                            u+=1
                    if u == n:
                        if change:#修改发消息的对象
                            user_id=int(QQ)
                            if send_type =="group":
                                if atwho.get()=="User":
                                    user=str(data['user_id'])
                                    send_message=f"[CQ:at,qq={user}]"+send_message
                                elif atwho.get()=="Others":
                                    others=int(at_qq.get().strip())
                                    send_message=f"[CQ:at,qq={others}]"+send_message
                        else:
                            user_id = data['user_id']
                            send_type="private"
                        API.send(send_message,send_type, user_id)
                        fact_count += 1
        if watcher == "AllGroup":
            if message_type == 'group':
                message = data['message']
                if (key1 in message and key1 !='') or (key2 in message and key2!='') or (key3 in message and key3!=''):
                    if n == 0:
                        if change:#修改发消息的对象
                            user_id=int(QQ)
                            if send_type =="group":
                                if atwho.get()=="User":
                                    user=str(data['user_id'])
                                    send_message=f"[CQ:at,qq={user}]"+send_message
                                elif atwho.get()=="Others":
                                    others=int(at_qq.get().strip())
                                    send_message=f"[CQ:at,qq={others}]"+send_message
                        else:
                            user_id = data['user_id']
                            send_type="private"
                        API.send(send_message, send_type, user_id)
                        fact_count += 1
                    else:
                        u=0
                        for i in range(n):
                            if Unempty_list[i] in message:
                                u+=1
                        if u == n:
                            if change:#修改发消息的对象
                                user_id=int(QQ)
                                if send_type =="group":
                                    if atwho.get()=="User":
                                        user=str(data['user_id'])
                                        send_message=f"[CQ:at,qq={user}]"+send_message
                                    elif atwho.get()=="Others":
                                        others=int(at_qq.get().strip())
                                        send_message=f"[CQ:at,qq={others}]"+send_message
                            else:
                                user_id = data['user_id']
                                send_type="private"
                            API.send(send_message, send_type, user_id)
                            fact_count += 1
                elif key1 == '' and key2 == '' and key3 == ''and  n != 0 :
                    u=0
                    for i in range(n):
                        if Unempty_list[i] in message:
                            u+=1
                    if u == n:
                        if change:#修改发消息的对象
                            user_id=int(QQ)
                            if send_type =="group":
                                if atwho.get()=="User":
                                    user=str(data['user_id'])
                                    send_message=f"[CQ:at,qq={user}]"+send_message
                                elif atwho.get()=="Others":
                                    others=int(at_qq.get().strip())
                                    send_message=f"[CQ:at,qq={others}]"+send_message
                        else:
                            user_id = data['user_id']
                            send_type="private"
                        API.send(send_message, send_type, user_id)
                        fact_count += 1
                elif n !=0 and motion_select.get() != "Strict":
                    u=0
                    for i in range(n):
                        if Unempty_list[i] in message:
                            u+=1
                    if u == n:
                        if change:#修改发消息的对象
                            user_id=int(QQ)
                            if send_type =="group":
                                if atwho.get()=="User":
                                    user=str(data['user_id'])
                                    send_message=f"[CQ:at,qq={user}]"+send_message
                                elif atwho.get()=="Others":
                                    others=int(at_qq.get().strip())
                                    send_message=f"[CQ:at,qq={others}]"+send_message
                        else:
                            user_id = data['user_id']
                            send_type="private"
                        API.send(send_message,send_type, user_id)
                        fact_count += 1
        if watcher == "All":
            message = data['message']
            if (key1 in message and key1 !='') or (key2 in message and key2!='') or (key3 in message and key3!=''):
                if n == 0:
                    if change:#修改发消息的对象
                        user_id=int(QQ)
                        if send_type =="group":
                            if atwho.get()=="User":
                                user=str(data['user_id'])
                                send_message=f"[CQ:at,qq={user}]"+send_message
                            elif atwho.get()=="Others":
                                others=int(at_qq.get().strip())
                                send_message=f"[CQ:at,qq={others}]"+send_message
                    else:
                        user_id = data['user_id']
                        send_type="private"
                    API.send(send_message, send_type, user_id)
                    fact_count += 1
                else:
                    u=0
                    for i in range(n):
                        if Unempty_list[i] in message:
                            u+=1
                    if u == n:
                        if change:#修改发消息的对象
                            user_id=int(QQ)
                            if send_type =="group":
                                if atwho.get()=="User":
                                    user=str(data['user_id'])
                                    send_message=f"[CQ:at,qq={user}]"+send_message
                                elif atwho.get()=="Others":
                                    others=int(at_qq.get().strip())
                                    send_message=f"[CQ:at,qq={others}]"+send_message
                        else:
                            user_id = data['user_id']
                            send_type="private"
                        API.send(send_message, send_type, user_id)
                        fact_count += 1
            elif key1 == '' and key2 == '' and key3 == ''and  n != 0 :
                u=0
                for i in range(n):
                    if Unempty_list[i] in message:
                        u+=1
                if u == n:
                    if change:#修改发消息的对象
                        user_id=int(QQ)
                        if send_type =="group":
                            if atwho.get()=="User":
                                user=str(data['user_id'])
                                send_message=f"[CQ:at,qq={user}]"+send_message
                            elif atwho.get()=="Others":
                                others=int(at_qq.get().strip())
                                send_message=f"[CQ:at,qq={others}]"+send_message
                    else:
                        user_id = data['user_id']
                        send_type="private"
                    API.send(send_message, send_type, user_id)
                    fact_count += 1
            elif n !=0 and motion_select.get() != "Strict":
                u=0
                for i in range(n):
                    if Unempty_list[i] in message:
                        u+=1
                if u == n:
                    if change:#修改发消息的对象
                        user_id=int(QQ)
                        if send_type =="group":
                            if atwho.get()=="User":
                                user=str(data['user_id'])
                                send_message=f"[CQ:at,qq={user}]"+send_message
                            elif atwho.get()=="Others":
                                others=int(at_qq.get().strip())
                                send_message=f"[CQ:at,qq={others}]"+send_message
                    else:
                        user_id = data['user_id']
                        send_type="private"
                    API.send(send_message,send_type, user_id)
                    fact_count += 1

def timestamp_transform(timestamp):
    '''
首先将时间戳转换为 datetime 对象，然后使用 strftime 方法将其格式化为字符串。"%Y
-%m-%d %H:%M:%S" 是格式化字符串，其中 %Y 表示年份，%m 表示月份，%d 表示日期，%H
表示小时，%M 表示分钟，%S 表示秒钟。
    '''
    dt_object = datetime.fromtimestamp(timestamp)
    formatted_time = dt_object.strftime("%Y-%m-%d %H:%M:%S")
    return formatted_time
    
def role_judge(role):
    if role == 'admin':
        return "管理员"
    elif role == 'owner':
        return "群主"
    else :
        return "无头衔"

def judge_empty(nece_list):
    Len=len(nece_list)
    n=0
    Unempty_list=[]
    for i in range(Len):
        if nece_list[i]!='':
            n+=1
            Unempty_list.append(nece_list[i])
    return(Unempty_list,n)    

@app.route('/', methods=["POST"])
#就近原则匹配到最近的函数
#定义了一个路由规则，即当接收到一个 POST 请求并且路径为 / 时，会调用 post_data 函数来处理请求
def post_data():
    data = request.get_json()
    if data['post_type'] == 'message':
        message_queue.put(data)#将消息元素放入消息队列当中
        message_ui_queue.put(data)#将消息元素放入UI消息队列当中
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
            time=timestamp_transform(int(data['time']))
            private_message_data['time']=time
            private_message_data['sender']=data['sender']
            private_message_data['message']=data['message']
            private_message_data['user_id']=data['user_id']
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
    first_time_file = os.path.join(user_data_dir, "first_time2.0.0.txt")
    if not os.path.exists(first_time_file):
        messagebox.showinfo("Update", "更新内容（版本2.0.0）：\n修复：\n对部分导致程序异常崩溃的问题（不填入群聊或其他消息直接点击开始监控导致的程序崩溃，正常运行后点停止监控再点击安全退出导致的程序崩溃）进行修复。\n升级：\n相对版本1.X.X升级页面。\n优化：\n有人在群聊中发送其他消息时，消息无法显示，而显示乱码的问题进行优化。\n新增：\n新增一个定时功能和一个选择“检测关键词并发消息”次数的功能（其他新加功能在使用过程中可以发现）。\n在另一方面，为了优化关键词的选择，不那么单调，新增了“或和并”选择关键词方法。")
        with open(first_time_file, "w") as file:
            file.write("Visited")

def stop_monitor():
    global stop_flask_loop,monitor_text,show_label,http_default,HTTP_set,HTTP_POST_set
    if flask_server and flask_thread and not stop_flask_loop: 
        stop_flask_loop = True
        if http_default:
            requests.get('http://127.0.0.1:5701/exit')
        else:
            url="http://127.0.0.1:"+f"{HTTP_POST_set}/exit"
            url=url.replace(" ","")
            requests.get(url)
        group_data_queue.queue.clear()
        message_queue.queue.clear()
        private_data_queue.queue.clear()
        message_ui_queue.queue.clear()
        monitor_text.insert(tk.INSERT,"已经停止监控")
        show_label.config(text="")

def merge_intervals(intervals):
    #对区间求并集，输出并集
    intervals.sort(key=lambda x: x[0])  # 按区间的起始值进行排序
    merged_intervals = []    
    for interval in intervals:
        if not merged_intervals or interval[0] > merged_intervals[-1][1]:
            # 如果当前区间与合并后的最后一个区间没有交集，直接加入
            merged_intervals.append(interval)
        else:
            # 有交集，更新合并后的最后一个区间的结束值
            merged_intervals[-1] = (merged_intervals[-1][0], max(merged_intervals[-1][1], interval[1]))    
    return merged_intervals

def change_settings():
    global flask_thread
    if flask_thread:
        user_data_dir = "user_data"
        if not os.path.exists(user_data_dir):
            os.makedirs(user_data_dir)
        never_file4 = os.path.join(user_data_dir, "never_seen4.txt")
        if not os.path.exists(never_file4):
            result=messagebox.askyesno("Confirmation","当前改动会导致当前监控中断，您是否愿意?")
            if result:
                stop_monitor()
                messagebox.showinfo("Reminder","已经为您修改当前设置，监控已经关闭，请重新启动监控。")
            result=messagebox.askyesno("Confirmation","您是否想下次不显示此类弹窗？")
            if result:                                        
                if not os.path.exists(never_file4):
                    with open(never_file4, "w") as file:
                        file.write("Never Seen")
        else:
            stop_monitor()
            
def run_gui_thread():
    def apply_filter():
        #上传数据给筛选条件字典
        group_id = group_entry.get().replace('\n','')
        keyword1 = keyword1_entry.get().replace('\n','')
        keyword2 = keyword2_entry.get().replace('\n','')
        keyword3 = keyword3_entry.get().replace('\n','')
        send_message = send_message_entry.get().replace('\n','')
        necessary1=necessary1_entry.get().replace('\n','')
        necessary2=necessary2_entry.get().replace('\n','')
        necessary3=necessary3_entry.get().replace('\n','')
        message_filter["group_id"] = group_id
        message_filter["keyword1"] = keyword1
        message_filter["keyword2"] = keyword2
        message_filter["keyword3"] = keyword3
        message_filter["send_message"] = send_message
        message_filter["necessary1"] = necessary1
        message_filter["necessary2"] = necessary2
        message_filter["necessary3"] = necessary3

    def increase_count():
        global click_count
        click_count += 1

    def change_config():
        global click_count,flask_thread,start_monitor_button
        if click_count >=1 and flask_thread is not None :
            start_monitor_button.config(text="重新开始监控")
            
    def update_http_post_ok():
        global http_post_var,http_post_ok,change_http_post,update_or_symbol
        if update_or_symbol:
            if http_post_var.get()!="":
                http_post_num=int(http_post_var.get())
                if http_post_num>=0 and http_post_num<=65535:
                    change_http_post=True
                    http_post_ok.config(text="")
                else :
                    change_http_post=False
                    http_post_ok.config(text="×,不合法",foreground="red")
            else:
                change_http_post=False
                http_post_ok.config(text="请输入",foreground="blue")
        gui.after(1000,update_http_post_ok)
        
    def update_http_ok():
        global http_var,http_ok,change_http,update_or_symbol
        if update_or_symbol:
            if http_var.get()!="":
                http_num=int(http_var.get())
                if http_num>=0 and http_num<=65535:
                    change_http=True
                    http_ok.config(text="")
                else :
                    change_http=False
                    http_ok.config(text="×,不合法",foreground="red")
            else:
                change_http=False
                http_ok.config(text="请输入",foreground="blue")
        gui.after(1000,update_http_ok)
        
    def update_time():
        #实现对当前时间的显示
        global time_update
        if not time_update:
            current_time = time.strftime("%Y-%m-%d %H:%M:%S")
            time_label.config(text=current_time)
            gui.after(1000, update_time)  # 每隔1秒更新时间显示

    def update_or_label():
        global or_label1,or_label2,keyword1_entry,keyword2_entry,keyword3_entry,update_or_symbol,keyword_symbol,keyword_Sym,motion_select,necessary_Sym
        if update_or_symbol:
            key1=keyword1_entry.get().replace(" ","")
            key2=keyword2_entry.get().replace(" ","")
            key3=keyword3_entry.get().replace(" ","")
            if key1 != "" and key2 != "":
               or_label1.config(text="or")
            else :
                or_label1.config(text="")
            if key2 != "" and key3 != "":
                or_label2.config(text="or")
            else :
                or_label2.config(text="")
            if key1 != "" or  key2 !="" or key3 != "" :
                if motion_select.get()!="Strict" and not necessary_Sym:
                    keyword_symbol.config(text="此栏已经有关键词填入，\n下栏可选填(最好填入)")
                    keyword_Sym=True
                elif motion_select.get()=="Strict":
                    if not necessary_Sym:
                        keyword_symbol.config(text="此栏已经有关键词填入，\n下栏也必须填入(处于严\n格模式)")
                        keyword_Sym=True
                    else :
                        keyword_symbol.config(text="严格模式：两栏已经全部\n填入✔")
                        keyword_Sym=True
                elif necessary_Sym:
                    keyword_symbol.config(text="两栏均已经有关键词填入✔")
                    keyword_Sym=True
            else:
                if motion_select.get() == "Strict":
                    if not necessary_Sym:
                        keyword_symbol.config(text="由于处在严格模式，此栏\n和下一栏必须填入)")
                        keyword_Sym=False
                    else:
                        keyword_symbol.config(text="严格模式：此栏未填入已经\n下栏已填入✔")
                        keyword_Sym=False
                elif motion_select.get() == "Mezzo":
                    if necessary_Sym:
                        keyword_symbol.config(text="此栏选填")
                        keyword_Sym=False
                    else:
                        keyword_symbol.config(text="适中模式：两栏中要有任意\n一栏填入")
                        keyword_Sym=False
                else:
                    keyword_symbol.config(text="")
                    keyword_Sym=False
            gui.after(1000,update_or_label)        

    def on_validate(P):#阻止输入其他内容整数除外
        if P == "":
            return True
        try:
            int(P)
            return True
        except ValueError:
            return False
    
    def update_and_label():
        global and_label1,and_label2,necessary1_entry,necessary2_entry,necessary3_entry,necessary_Sym,necessary_symbol,motion_select,keyword_Sym,update_or_symbol
        if update_or_symbol:
            necessary1=necessary1_entry.get().replace(" ","")
            necessary2=necessary2_entry.get().replace(" ","")
            necessary3=necessary3_entry.get().replace(" ","")
            if necessary1 != "" and necessary2 != "":
               and_label1.config(text="and")
            else :
                and_label1.config(text="")
            if necessary2 != "" and necessary3 != "":
                and_label2.config(text="and")
            else :
                and_label2.config(text="")
            if necessary1 != "" or  necessary2 !="" or necessary3 != "":
                if motion_select.get()!="Strict" and not keyword_Sym :
                    necessary_symbol.config(text="此栏已经有关键词填入，\n上栏可选填(最好填入)")
                    necessary_Sym=True
                elif motion_select.get()=="Strict":
                    if not keyword_Sym:
                        necessary_symbol.config(text="此栏已经有关键词填入，\n上栏也必须填入(处于严\n格模式)")
                        necessary_Sym=True
                    else :
                        necessary_symbol.config(text="严格模式：两栏已经全部\n填入✔")
                        necessary_Sym=True
                elif keyword_Sym:
                    necessary_symbol.config(text="两栏均已经有关键词填入✔")
                    necessary_Sym=True
            else:
                if motion_select.get() == "Strict":
                    if not keyword_Sym:
                        necessary_symbol.config(text="由于处在严格模式，此栏\n和上一栏必须填入)")
                        necessary_Sym=False
                    else:
                        necessary_symbol.config(text="严格模式：此栏未填入已经\n上栏已填入✔")
                        necessary_Sym=False
                elif motion_select.get() == "Mezzo":
                    if keyword_Sym:
                        necessary_symbol.config(text="此栏选填")
                        necessary_Sym=False
                    else:
                        necessary_symbol.config(text="适中模式：两栏中要有任意\n一栏填入")
                        necessary_Sym=False
                else:
                    necessary_symbol.config(text="")
                    necessary_Sym=False
            gui.after(1000,update_and_label)

    def update_time_symbol():
        global time_symbol,selected_datetime,time_update
        if not time_update :
            if selected_datetime is not None:
                current_time=datetime.now()
                time_difference=selected_datetime-current_time
                # 格式化时间差的输出
                formatted_time_difference = timedelta(days=time_difference.days, seconds=time_difference.seconds)
                format_datetime=selected_datetime.strftime("%Y-%m-%d %H:%M:%S")
                time_symbol.config(text=f"已经启动在{format_datetime}的定时,\n程序距离关闭还有:  {formatted_time_difference}。")
                gui.after(1000,update_time_symbol)        

    def update_send_msg_symbol():
        global send_message_entry,send_msg_symbol,send_msg_Sym,update_or_symbol
        send_msg=send_message_entry.get()        
        send_msg_symbol.config(font=("Verdana",7))
        if update_or_symbol:
            if send_msg == '':
                send_msg_symbol.config(foreground="#4682B4",text="请输入")#钢蓝色
                send_msg_Sym=False
            else:
                send_msg_symbol.config(foreground="#228B22",text="✔")#森林绿
                send_msg_Sym=True
            gui.after(1000,update_send_msg_symbol)
    
    def update_group_symbol():
        global group_symbol,group_entry,group_Sym,group_change
        group=group_entry.get().strip()        
        group_symbol.config(font=("Verdana",7))
        if not group_change:
            if group == '':
                group_symbol.config(foreground="#4682B4",text="请输入")#钢蓝色
                group_Sym=False
            elif group.isdigit():#判断字符串中是否只有数字
                group_symbol.config(foreground="#228B22",text="✔")#森林绿
                group_Sym=True
            else:
                group_symbol.config(foreground="#FF0000",text="×，QQ名\n称不合法")#鲜红色
                group_Sym=False
            gui.after(1000,update_group_symbol)

    def fact_count_symbol_label_update():
        global fact_count_symbol_label,fact_count,count,pattern_start
        if not pattern_start:
            diff=count-fact_count
            fact_count_symbol_label.config(text=f"当前已经检测/发送消息\n次数；{fact_count},还剩下{diff}次")
            gui.after(1000,fact_count_symbol_label_update)

    def update_show_label():
        global show_label,necessary_Sym,keyword_Sym,group_Sym,send_msg_Sym,flask_thread,motion_select,send_type,QQ,id_Sym,at_sym,atwho,at_qq,change,select_watcher
        if flask_thread:
            show_text=""
            group=message_filter["group_id"]
            key1=message_filter["keyword1"]
            key2=message_filter["keyword2"] 
            key3=message_filter["keyword3"] 
            send_msg=message_filter["send_message"]
            nece1=message_filter["necessary1"] 
            nece2=message_filter["necessary2"] 
            nece3=message_filter["necessary3"]
            watcher=select_watcher.get()
            motion=motion_select.get()
            if motion == "Easy":
                motion="宽松模式"
            elif motion == "Mezzo":
                motion = "适中模式"
            elif motion == "Strict":
                motion="严格模式"
            if group_Sym or watcher=="AllGroup" or watcher=="AllPrivate" or watcher=="All":
                if watcher=="CerGroup":
                    show_text=f"当前正在监控群{group}中的消息,当前监控模式为{motion}。\n当前的消息筛选要求："
                if watcher == "CerPrivate":
                    show_text=f"当前正在监控好友{group}发来的消息,当前监控模式为{motion}。\n当前的消息筛选要求："
                if watcher=="AllGroup":
                    show_text=f"当前正在监控所有群聊中的消息,当前监控模式为{motion}。\n当前的消息筛选要求："
                if watcher == "AllPrivate":
                    show_text=f"当前正在监控所有好友发来的消息,当前监控模式为{motion}。\n当前的消息筛选要求："
                if watcher=="All":
                    show_text=f"当前正在监控所有好友和群聊发来的消息,当前监控模式为{motion}。\n当前的消息筛选要求："
                if necessary_Sym:
                    nece_list=[nece1,nece2,nece3]
                    (Unempty_list,n)=judge_empty(nece_list)
                    show_text=show_text+"必须包含以下所有关键词："
                    for i in range(n):
                        show_text=show_text+f"“{Unempty_list[i]}”,"
                if keyword_Sym:
                    key_list=[key1,key2,key3]
                    (Unempty_list,n)=judge_empty(key_list)
                    if motion_select.get() == "Strict":
                        if n > 1:
                            show_text=show_text+"且必须含有以下至少一个关键词："
                        else:
                            show_text=show_text+"且必须含有以下关键词："
                    else:
                        if necessary_Sym:
                            show_text=show_text+"可能包含以下关键词中的任意几个(包括0):"
                        else :
                            show_text=show_text+"可能包含以下关键词中的任意几个(至少为1):"
                    for i in range(n):
                        show_text=show_text+f"“{Unempty_list[i]}”,"
                if not keyword_Sym and not necessary_Sym :
                    show_text=show_text+"无,只进行监控,不发送消息。"
                elif send_msg_Sym or watcher=="All" or watcher=="AllPrivate" or watcher=="AllGroup":
                    if change:
                        if send_type=="private":
                            msg="好友"
                            send="私聊"
                        if send_type=="group":
                            msg="QQ群"
                            send="群聊"
                        show_text=show_text+f"检测到符合的消息后,给{msg}({QQ}){send}发送消息“{send_msg}。”"
                        if send_type=="group":
                            if at_sym and atwho.get()=="User":
                                show_text=show_text+f"(并且会自动@该发送消息的人)"
                            if at_sym and atwho.get()=="Others":
                                qq=at_qq.get().strip()
                                show_text=show_text+f"(并且会自动@{qq})"
                    else:
                        show_text=show_text+f"检测到符合的消息后，给发送该消息的人(只有为好友,才能发送成功)私聊发送消息“{send_msg}”。"
            show_label.config(text=show_text)

    def solution_plan_show():
        global solution_plan_show_label,solution_select,plan_select,pattern_start,selected_datetime
        if not pattern_start and selected_datetime is not None:
            plan=plan_select.get()
            solution=solution_select.get()
            solution_plan_show_label.config(text=f"当前您选择的解决冲突\n的方式为:{solution},{plan}")
        else:
            solution_plan_show_label.config(text="")
        gui.after(1000,solution_plan_show)

    def update_monitor_message():
        global stop_monitor_update,necessary_Sym,select_watcher
        if not stop_monitor_update:
            watcher=select_watcher.get()
            if watcher=="CerGroup" :
                if not group_data_queue.empty():
                    order_group_id = message_filter['group_id']
                    key1=message_filter['keyword1']
                    key2=message_filter['keyword2']
                    key3=message_filter['keyword3']
                    data = group_data_queue.get()
                    reatime = data['time']
                    sender = data['sender']
                    message = data['message']
                    group_id = data['group_id']
                    sender_card = sender['card']
                    nece1=message_filter['necessary1']
                    nece2=message_filter['necessary2']
                    nece3=message_filter['necessary3']
                    nece_list=[nece1,nece2,nece3]
                    (unempty_list,n)=judge_empty(nece_list)
                    k=0
                    for i in range(n):
                        if unempty_list[i] in  message:
                            k+=1
                    if sender_card == "":
                        sender_card = sender['nickname']
                    sender_nickname = sender['nickname']
                    sender_id = sender['user_id']
                    role = role_judge(sender['role'])
                    if str(group_id) == str(order_group_id):
                        monitor_text.insert(tk.INSERT, f"{reatime}\n", "time")
                        monitor_text.insert(tk.INSERT, f"{role} ", "role")
                        monitor_text.insert(tk.INSERT, f"{sender_card}", "sender_card")
                        monitor_text.insert(tk.INSERT, f"(用户id:{sender_nickname},用户QQ号:{sender_id}):\n", "sender")                  
                        if ("[]" not in message and "CQ" not in message) or "CQ:at"in message or "CQ:face" in message:
                            if (necessary_Sym and n==k) or n==0:
                                intervals = []
                                if key1 !='':
                                    start1=message.find(key1)
                                    len1=len(key1)
                                    end1=start1+len1-1
                                else:
                                    start1=-1
                                if start1 != -1:
                                    tuple1 = (start1,end1)
                                    intervals.append(tuple1)
                                if key2 !='':
                                    start2=message.find(key2)
                                    len2=len(key2)
                                    end2=start2+len2-1
                                else:
                                    start2=-1
                                if start2 != -1:
                                    tuple2 = (start2,end2)
                                    intervals.append(tuple2)    
                                if key3 !='':
                                    start3=message.find(key3)
                                    len3=len(key3)
                                    end3=start3+len3-1
                                else:
                                    start3=-1
                                if start3 != -1:
                                    tuple3 = (start3,end3)
                                    intervals.append(tuple3)
                                if nece1 !='':
                                    start4=message.find(nece1)
                                    len4=len(nece1)
                                    end4=start4+len4-1
                                else:
                                    start4=-1
                                if start4 != -1:
                                    tuple4 = (start4,end4)
                                    intervals.append(tuple4)
                                if nece2 !='':
                                    start5=message.find(nece2)
                                    len5=len(nece2)
                                    end5=start5+len5-1
                                else:
                                    start5=-1
                                if start5 != -1:
                                    tuple5 = (start5,end5)
                                    intervals.append(tuple5)    
                                if nece3 !='':
                                    start6=message.find(nece3)
                                    len6=len(nece3)
                                    end6=start6+len6-1
                                else:
                                    start6=-1
                                if start6 != -1:
                                    tuple6 = (start6,end6)
                                    intervals.append(tuple6)
                                merged_results = merge_intervals(intervals)
                                i = 0
                                j = 0
                                if "CQ:at" in message:
                                    if "CQ:reply" not in message:
                                        start=message.find("qq=")+3                                
                                        end=message.find("]")
                                        qq=message[start:end]
                                        monitor_text.insert(tk.INSERT,f"@{qq}","at")
                                        if (end+1) < len(message):
                                            message=message[end+1:]
                                    elif "CQ:reply" in message:
                                        end=message.find("]",message.find("]")+1)
                                        monitor_text.insert(tk.INSERT,f"回复:","at")
                                        if (end+1) < len(message):
                                            message=message[end+1:]
                                while i < len(message):
                                    while j< len(merged_results) and i<=merged_results[len(merged_results)-1][1]:
                                        if  i < merged_results[j][0]:
                                            monitor_text.insert(tk.INSERT, f"{message[i]}")
                                            i=i+1
                                        elif i>= merged_results[j][0] and i<= merged_results[j][1]:
                                            monitor_text.insert(tk.INSERT, f"{message[i]}","import")
                                            i=i+1
                                        elif i >merged_results[j][1] and i!=merged_results[j+1][0] :
                                            monitor_text.insert(tk.INSERT, f"{message[i]}")
                                            i=i+1
                                            j=j+1
                                        elif i ==merged_results[j+1][0]:
                                            monitor_text.insert(tk.INSERT, f"{message[i]}","import")
                                            i=i+1
                                            j=j+1    
                                    if i < len(message):
                                        monitor_text.insert(tk.INSERT, f"{message[i]}")   
                                        i=i+1
                                monitor_text.insert(tk.INSERT, f"\n") 
                            else :
                                monitor_text.insert(tk.INSERT, f"{message}\n")
                        else:
                            if "CQ:image" in message:
                                monitor_text.insert(tk.INSERT, f"图片消息/动画表情(暂不支持查看)\n","unsupport")
                            elif "CQ:record" in message:
                                monitor_text.insert(tk.INSERT, f"语音消息(暂不支持查看)\n","unsupport")
                            elif "CQ:redbag" in message:
                                start=message.find("title")+6                                
                                end=message.find("]")
                                title=message[start:end]
                                monitor_text.insert(tk.INSERT, f"红包消息[{title}](请在手机/平板上查看)\n","redbag")
                            elif "CQ:json" in message:
                                if "address" in message:
                                    start=message.find("\"address\":")+11
                                    end=message.find("&#44",start)-1
                                    address=message[start:end]
                                    monitor_text.insert(tk.INSERT, f"地图消息:地址{address}(暂不支持查看)\n","addresss")
                                elif "推荐联系人" in message:
                                    start=message.find("推荐联系人")+6
                                    end=message.find("&#44",start)-1
                                    nickname=message[start:end]
                                    start=message.find("账号")+3
                                    end=message.find("&#44",start)-1
                                    qq=message[start:end]
                                    monitor_text.insert(tk.INSERT, f"推荐联系人:昵称:{nickname}QQ:{qq}\n","prompt")
                                elif "加入一起听歌":
                                    monitor_text.insert(tk.INSERT, f"加入一起听歌\n","song")
                            else:
                                monitor_text.insert(tk.INSERT, f"暂不支持查看该消息类型\n","unsupport")
            if watcher=="CerPrivate":
                if not private_data_queue.empty():
                    order_private_id = message_filter['group_id']
                    key1=message_filter['keyword1']
                    key2=message_filter['keyword2']
                    key3=message_filter['keyword3']
                    data = private_data_queue.get()
                    reatime = data['time']
                    sender = data['sender']
                    message = data['message']
                    private_id = data['user_id']
                    nece1=message_filter['necessary1']
                    nece2=message_filter['necessary2']
                    nece3=message_filter['necessary3']
                    nece_list=[nece1,nece2,nece3]
                    (unempty_list,n)=judge_empty(nece_list)
                    k=0
                    for i in range(n):
                        if unempty_list[i] in  message:
                            k+=1
                    sender_nickname = sender['nickname']
                    sender_id = sender['user_id']
                    if str(private_id) == str(order_private_id):
                        monitor_text.insert(tk.INSERT, f"{reatime}\n", "time")
                        monitor_text.insert(tk.INSERT, f"(用户id:{sender_nickname},用户QQ号:{sender_id}):\n", "sender")                  
                        if ("[]" not in message and "CQ" not in message) or "CQ:at"in message or "CQ:face" in message:
                            if (necessary_Sym and n==k) or n==0:
                                intervals = []
                                if key1 !='':
                                    start1=message.find(key1)
                                    len1=len(key1)
                                    end1=start1+len1-1
                                else:
                                    start1=-1
                                if start1 != -1:
                                    tuple1 = (start1,end1)
                                    intervals.append(tuple1)
                                if key2 !='':
                                    start2=message.find(key2)
                                    len2=len(key2)
                                    end2=start2+len2-1
                                else:
                                    start2=-1
                                if start2 != -1:
                                    tuple2 = (start2,end2)
                                    intervals.append(tuple2)    
                                if key3 !='':
                                    start3=message.find(key3)
                                    len3=len(key3)
                                    end3=start3+len3-1
                                else:
                                    start3=-1
                                if start3 != -1:
                                    tuple3 = (start3,end3)
                                    intervals.append(tuple3)
                                if nece1 !='':
                                    start4=message.find(nece1)
                                    len4=len(nece1)
                                    end4=start4+len4-1
                                else:
                                    start4=-1
                                if start4 != -1:
                                    tuple4 = (start4,end4)
                                    intervals.append(tuple4)
                                if nece2 !='':
                                    start5=message.find(nece2)
                                    len5=len(nece2)
                                    end5=start5+len5-1
                                else:
                                    start5=-1
                                if start5 != -1:
                                    tuple5 = (start5,end5)
                                    intervals.append(tuple5)    
                                if nece3 !='':
                                    start6=message.find(nece3)
                                    len6=len(nece3)
                                    end6=start6+len6-1
                                else:
                                    start6=-1
                                if start6 != -1:
                                    tuple6 = (start6,end6)
                                    intervals.append(tuple6)
                                merged_results = merge_intervals(intervals)
                                i = 0
                                j = 0
                                if "CQ:at" in message:
                                    if "CQ:reply" not in message:
                                        start=message.find("qq=")+3                                
                                        end=message.find("]")
                                        qq=message[start:end]
                                        monitor_text.insert(tk.INSERT,f"@{qq}","at")
                                        if (end+1) < len(message):
                                            message=message[end+1:]
                                    elif "CQ:reply" in message:
                                        end=message.find("]",message.find("]")+1)
                                        monitor_text.insert(tk.INSERT,f"回复:","at")
                                        if (end+1) < len(message):
                                            message=message[end+1:]
                                while i < len(message):
                                    while j< len(merged_results) and i<=merged_results[len(merged_results)-1][1]:
                                        if  i < merged_results[j][0]:
                                            monitor_text.insert(tk.INSERT, f"{message[i]}")
                                            i=i+1
                                        elif i>= merged_results[j][0] and i<= merged_results[j][1]:
                                            monitor_text.insert(tk.INSERT, f"{message[i]}","import")
                                            i=i+1
                                        elif i >merged_results[j][1] and i!=merged_results[j+1][0] :
                                            monitor_text.insert(tk.INSERT, f"{message[i]}")
                                            i=i+1
                                            j=j+1
                                        elif i ==merged_results[j+1][0]:
                                            monitor_text.insert(tk.INSERT, f"{message[i]}","import")
                                            i=i+1
                                            j=j+1    
                                    if i < len(message):
                                        monitor_text.insert(tk.INSERT, f"{message[i]}")   
                                        i=i+1
                                monitor_text.insert(tk.INSERT, f"\n") 
                            else :
                                monitor_text.insert(tk.INSERT, f"{message}\n")
                        else:
                            if "CQ:image" in message:
                                monitor_text.insert(tk.INSERT, f"图片消息/动画表情(暂不支持查看)\n","unsupport")
                            elif "CQ:record" in message:
                                monitor_text.insert(tk.INSERT, f"语音消息(暂不支持查看)\n","unsupport")
                            elif "CQ:redbag" in message:
                                start=message.find("title")+6                                
                                end=message.find("]")
                                title=message[start:end]
                                monitor_text.insert(tk.INSERT, f"红包消息[{title}](请在手机/平板上查看)\n","redbag")
                            elif "CQ:json" in message:
                                if "address" in message:
                                    start=message.find("\"address\":")+11
                                    end=message.find("&#44",start)-1
                                    address=message[start:end]
                                    monitor_text.insert(tk.INSERT, f"地图消息:地址{address}(暂不支持查看)\n","addresss")
                                elif "推荐联系人" in message:
                                    start=message.find("推荐联系人")+6
                                    end=message.find("&#44",start)-1
                                    nickname=message[start:end]
                                    start=message.find("账号")+3
                                    end=message.find("&#44",start)-1
                                    qq=message[start:end]
                                    monitor_text.insert(tk.INSERT, f"推荐联系人:昵称:{nickname}QQ:{qq}\n","prompt")
                                elif "加入一起听歌":
                                    monitor_text.insert(tk.INSERT, f"加入一起听歌\n","song")
                            else:
                                monitor_text.insert(tk.INSERT, f"暂不支持查看该消息类型\n","unsupport")
            if watcher=="AllGroup":
                if not group_data_queue.empty():
                    key1=message_filter['keyword1']
                    key2=message_filter['keyword2']
                    key3=message_filter['keyword3']
                    nece1=message_filter['necessary1']
                    nece2=message_filter['necessary2']
                    nece3=message_filter['necessary3']
                    nece_list=[nece1,nece2,nece3]
                    (unempty_list,n)=judge_empty(nece_list)
                    k=0
                    for i in range(n):
                        if unempty_list[i] in  message:
                            k+=1
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
                    monitor_text.insert(tk.INSERT, f"{group_id}群聊中的消息:\n")
                    monitor_text.insert(tk.INSERT, f"{reatime}\n", "time")
                    monitor_text.insert(tk.INSERT, f"{role} ", "role")
                    monitor_text.insert(tk.INSERT, f"{sender_card}", "sender_card")
                    monitor_text.insert(tk.INSERT, f"(用户id:{sender_nickname},用户QQ号:{sender_id}):\n", "sender")                  
                    if ("[]" not in message and "CQ" not in message) or "CQ:at"in message or "CQ:face" in message:
                        if (necessary_Sym and n==k) or n==0:
                            intervals = []
                            if key1 !='':
                                start1=message.find(key1)
                                len1=len(key1)
                                end1=start1+len1-1
                            else:
                                start1=-1
                            if start1 != -1:
                                tuple1 = (start1,end1)
                                intervals.append(tuple1)
                            if key2 !='':
                                start2=message.find(key2)
                                len2=len(key2)
                                end2=start2+len2-1
                            else:
                                start2=-1
                            if start2 != -1:
                                tuple2 = (start2,end2)
                                intervals.append(tuple2)    
                            if key3 !='':
                                start3=message.find(key3)
                                len3=len(key3)
                                end3=start3+len3-1
                            else:
                                start3=-1
                            if start3 != -1:
                                tuple3 = (start3,end3)
                                intervals.append(tuple3)
                            if nece1 !='':
                                start4=message.find(nece1)
                                len4=len(nece1)
                                end4=start4+len4-1
                            else:
                                start4=-1
                            if start4 != -1:
                                tuple4 = (start4,end4)
                                intervals.append(tuple4)
                            if nece2 !='':
                                start5=message.find(nece2)
                                len5=len(nece2)
                                end5=start5+len5-1
                            else:
                                start5=-1
                            if start5 != -1:
                                tuple5 = (start5,end5)
                                intervals.append(tuple5)    
                            if nece3 !='':
                                start6=message.find(nece3)
                                len6=len(nece3)
                                end6=start6+len6-1
                            else:
                                start6=-1
                            if start6 != -1:
                                tuple6 = (start6,end6)
                                intervals.append(tuple6)
                            merged_results = merge_intervals(intervals)
                            i = 0
                            j = 0
                            if "CQ:at" in message:
                                if "CQ:reply" not in message:
                                    start=message.find("qq=")+3                                
                                    end=message.find("]")
                                    qq=message[start:end]
                                    monitor_text.insert(tk.INSERT,f"@{qq}","at")
                                    if (end+1) < len(message):
                                        message=message[end+1:]
                                elif "CQ:reply" in message:
                                    end=message.find("]",message.find("]")+1)
                                    monitor_text.insert(tk.INSERT,f"回复:","at")
                                    if (end+1) < len(message):
                                        message=message[end+1:]
                            while i < len(message):
                                while j< len(merged_results) and i<=merged_results[len(merged_results)-1][1]:
                                    if  i < merged_results[j][0]:
                                        monitor_text.insert(tk.INSERT, f"{message[i]}")
                                        i=i+1
                                    elif i>= merged_results[j][0] and i<= merged_results[j][1]:
                                        monitor_text.insert(tk.INSERT, f"{message[i]}","import")
                                        i=i+1
                                    elif i >merged_results[j][1] and i!=merged_results[j+1][0] :
                                        monitor_text.insert(tk.INSERT, f"{message[i]}")
                                        i=i+1
                                        j=j+1
                                    elif i ==merged_results[j+1][0]:
                                        monitor_text.insert(tk.INSERT, f"{message[i]}","import")
                                        i=i+1
                                        j=j+1    
                                if i < len(message):
                                    monitor_text.insert(tk.INSERT, f"{message[i]}")   
                                    i=i+1
                            monitor_text.insert(tk.INSERT, f"\n") 
                        else :
                            monitor_text.insert(tk.INSERT, f"{message}\n")
                    else:
                        if "CQ:image" in message:
                            monitor_text.insert(tk.INSERT, f"图片消息/动画表情(暂不支持查看)\n","unsupport")
                        elif "CQ:record" in message:
                            monitor_text.insert(tk.INSERT, f"语音消息(暂不支持查看)\n","unsupport")
                        elif "CQ:redbag" in message:
                            start=message.find("title")+6                                
                            end=message.find("]")
                            title=message[start:end]
                            monitor_text.insert(tk.INSERT, f"红包消息[{title}](请在手机/平板上查看)\n","redbag")
                        elif "CQ:json" in message:
                            if "address" in message:
                                start=message.find("\"address\":")+11
                                end=message.find("&#44",start)-1
                                address=message[start:end]
                                monitor_text.insert(tk.INSERT, f"地图消息:地址{address}(暂不支持查看)\n","addresss")
                            elif "推荐联系人" in message:
                                start=message.find("推荐联系人")+6
                                end=message.find("&#44",start)-1
                                nickname=message[start:end]
                                start=message.find("账号")+3
                                end=message.find("&#44",start)-1
                                qq=message[start:end]
                                monitor_text.insert(tk.INSERT, f"推荐联系人:昵称:{nickname}QQ:{qq}\n","prompt")
                            elif "加入一起听歌":
                                monitor_text.insert(tk.INSERT, f"加入一起听歌\n","song")
                        else:
                            monitor_text.insert(tk.INSERT, f"暂不支持查看该消息类型\n","unsupport")
            if watcher=="AllPrivate":
                if not private_data_queue.empty():
                    key1=message_filter['keyword1']
                    key2=message_filter['keyword2']
                    key3=message_filter['keyword3']
                    nece1=message_filter['necessary1']
                    nece2=message_filter['necessary2']
                    nece3=message_filter['necessary3']
                    nece_list=[nece1,nece2,nece3]
                    (unempty_list,n)=judge_empty(nece_list)
                    k=0
                    for i in range(n):
                        if unempty_list[i] in  message:
                            k+=1
                    data = private_data_queue.get()
                    reatime = data['time']
                    sender = data['sender']
                    message = data['message']
                    private_id = data['user_id']
                    sender_nickname = sender['nickname']
                    sender_id = sender['user_id']
                    monitor_text.insert(tk.INSERT, f"{reatime}\n", "time")
                    monitor_text.insert(tk.INSERT, f"(用户id:{sender_nickname},用户QQ号:{sender_id}):\n", "sender")                  
                    if ("[]" not in message and "CQ" not in message) or "CQ:at"in message or "CQ:face" in message:
                        if (necessary_Sym and n==k) or n==0:
                            intervals = []
                            if key1 !='':
                                start1=message.find(key1)
                                len1=len(key1)
                                end1=start1+len1-1
                            else:
                                start1=-1
                            if start1 != -1:
                                tuple1 = (start1,end1)
                                intervals.append(tuple1)
                            if key2 !='':
                                start2=message.find(key2)
                                len2=len(key2)
                                end2=start2+len2-1
                            else:
                                start2=-1
                            if start2 != -1:
                                tuple2 = (start2,end2)
                                intervals.append(tuple2)    
                            if key3 !='':
                                start3=message.find(key3)
                                len3=len(key3)
                                end3=start3+len3-1
                            else:
                                start3=-1
                            if start3 != -1:
                                tuple3 = (start3,end3)
                                intervals.append(tuple3)
                            if nece1 !='':
                                start4=message.find(nece1)
                                len4=len(nece1)
                                end4=start4+len4-1
                            else:
                                start4=-1
                            if start4 != -1:
                                tuple4 = (start4,end4)
                                intervals.append(tuple4)
                            if nece2 !='':
                                start5=message.find(nece2)
                                len5=len(nece2)
                                end5=start5+len5-1
                            else:
                                start5=-1
                            if start5 != -1:
                                tuple5 = (start5,end5)
                                intervals.append(tuple5)    
                            if nece3 !='':
                                start6=message.find(nece3)
                                len6=len(nece3)
                                end6=start6+len6-1
                            else:
                                start6=-1
                            if start6 != -1:
                                tuple6 = (start6,end6)
                                intervals.append(tuple6)
                            merged_results = merge_intervals(intervals)
                            i = 0
                            j = 0
                            if "CQ:at" in message:
                                if "CQ:reply" not in message:
                                    start=message.find("qq=")+3                                
                                    end=message.find("]")
                                    qq=message[start:end]
                                    monitor_text.insert(tk.INSERT,f"@{qq}","at")
                                    if (end+1) < len(message):
                                        message=message[end+1:]
                                elif "CQ:reply" in message:
                                    end=message.find("]",message.find("]")+1)
                                    monitor_text.insert(tk.INSERT,f"回复:","at")
                                    if (end+1) < len(message):
                                        message=message[end+1:]
                            while i < len(message):
                                while j< len(merged_results) and i<=merged_results[len(merged_results)-1][1]:
                                    if  i < merged_results[j][0]:
                                        monitor_text.insert(tk.INSERT, f"{message[i]}")
                                        i=i+1
                                    elif i>= merged_results[j][0] and i<= merged_results[j][1]:
                                        monitor_text.insert(tk.INSERT, f"{message[i]}","import")
                                        i=i+1
                                    elif i >merged_results[j][1] and i!=merged_results[j+1][0] :
                                        monitor_text.insert(tk.INSERT, f"{message[i]}")
                                        i=i+1
                                        j=j+1
                                    elif i ==merged_results[j+1][0]:
                                        monitor_text.insert(tk.INSERT, f"{message[i]}","import")
                                        i=i+1
                                        j=j+1    
                                if i < len(message):
                                    monitor_text.insert(tk.INSERT, f"{message[i]}")   
                                    i=i+1
                            monitor_text.insert(tk.INSERT, f"\n") 
                        else :
                            monitor_text.insert(tk.INSERT, f"{message}\n")
                    else:
                        if "CQ:image" in message:
                            monitor_text.insert(tk.INSERT, f"图片消息/动画表情(暂不支持查看)\n","unsupport")
                        elif "CQ:record" in message:
                            monitor_text.insert(tk.INSERT, f"语音消息(暂不支持查看)\n","unsupport")
                        elif "CQ:redbag" in message:
                            start=message.find("title")+6                                
                            end=message.find("]")
                            title=message[start:end]
                            monitor_text.insert(tk.INSERT, f"红包消息[{title}](请在手机/平板上查看)\n","redbag")
                        elif "CQ:json" in message:
                            if "address" in message:
                                start=message.find("\"address\":")+11
                                end=message.find("&#44",start)-1
                                address=message[start:end]
                                monitor_text.insert(tk.INSERT, f"地图消息:地址{address}(暂不支持查看)\n","addresss")
                            elif "推荐联系人" in message:
                                start=message.find("推荐联系人")+6
                                end=message.find("&#44",start)-1
                                nickname=message[start:end]
                                start=message.find("账号")+3
                                end=message.find("&#44",start)-1
                                qq=message[start:end]
                                monitor_text.insert(tk.INSERT, f"推荐联系人:昵称:{nickname}QQ:{qq}\n","prompt")
                            elif "加入一起听歌":
                                monitor_text.insert(tk.INSERT, f"加入一起听歌\n","song")
                        else:
                            monitor_text.insert(tk.INSERT, f"暂不支持查看该消息类型\n","unsupport")
            if watcher=="All":
                if not message_ui_queue.empty():
                    key1=message_filter['keyword1']
                    key2=message_filter['keyword2']
                    key3=message_filter['keyword3']
                    nece1=message_filter['necessary1']
                    nece2=message_filter['necessary2']
                    nece3=message_filter['necessary3']
                    nece_list=[nece1,nece2,nece3]
                    (unempty_list,n)=judge_empty(nece_list)
                    k=0
                    for i in range(n):
                        if unempty_list[i] in  message:
                            k+=1
                    data = message_ui_queue.get()
                    reatime = timestamp_transform(data['time'])
                    sender = data['sender']
                    message = data['message']
                    message_type=data['message_type']
                    if message_type=="group":
                        group_id = data['group_id']
                        sender_card = sender['card']    
                        if sender_card == "":
                            sender_card = sender['nickname']
                        sender_nickname = sender['nickname']
                        sender_id = sender['user_id']
                        role = role_judge(sender['role'])
                        monitor_text.insert(tk.INSERT, f"{group_id}群聊中的消息:\n")
                        monitor_text.insert(tk.INSERT, f"{reatime}\n", "time")
                        monitor_text.insert(tk.INSERT, f"{role} ", "role")
                        monitor_text.insert(tk.INSERT, f"{sender_card}", "sender_card")
                        monitor_text.insert(tk.INSERT, f"(用户id:{sender_nickname},用户QQ号:{sender_id}):\n", "sender") 
                    elif message_type=="private":
                        user_id=data["user_id"]
                        sender_nickname = sender['nickname']
                        sender_id = sender['user_id']
                        monitor_text.insert(tk.INSERT, f"{user_id}好友私发的消息\n")
                        monitor_text.insert(tk.INSERT, f"{reatime}\n", "time")
                        monitor_text.insert(tk.INSERT, f"(用户id:{sender_nickname},用户QQ号:{sender_id}):\n", "sender")
                    if ("[]" not in message and "CQ" not in message) or "CQ:at"in message or "CQ:face" in message:
                        if (necessary_Sym and n==k) or n==0:
                            intervals = []
                            if key1 !='':
                                start1=message.find(key1)
                                len1=len(key1)
                                end1=start1+len1-1
                            else:
                                start1=-1
                            if start1 != -1:
                                tuple1 = (start1,end1)
                                intervals.append(tuple1)
                            if key2 !='':
                                start2=message.find(key2)
                                len2=len(key2)
                                end2=start2+len2-1
                            else:
                                start2=-1
                            if start2 != -1:
                                tuple2 = (start2,end2)
                                intervals.append(tuple2)    
                            if key3 !='':
                                start3=message.find(key3)
                                len3=len(key3)
                                end3=start3+len3-1
                            else:
                                start3=-1
                            if start3 != -1:
                                tuple3 = (start3,end3)
                                intervals.append(tuple3)
                            if nece1 !='':
                                start4=message.find(nece1)
                                len4=len(nece1)
                                end4=start4+len4-1
                            else:
                                start4=-1
                            if start4 != -1:
                                tuple4 = (start4,end4)
                                intervals.append(tuple4)
                            if nece2 !='':
                                start5=message.find(nece2)
                                len5=len(nece2)
                                end5=start5+len5-1
                            else:
                                start5=-1
                            if start5 != -1:
                                tuple5 = (start5,end5)
                                intervals.append(tuple5)    
                            if nece3 !='':
                                start6=message.find(nece3)
                                len6=len(nece3)
                                end6=start6+len6-1
                            else:
                                start6=-1
                            if start6 != -1:
                                tuple6 = (start6,end6)
                                intervals.append(tuple6)
                            merged_results = merge_intervals(intervals)
                            i = 0
                            j = 0
                            if "CQ:at" in message:
                                if "CQ:reply" not in message:
                                    start=message.find("qq=")+3                                
                                    end=message.find("]")
                                    qq=message[start:end]
                                    monitor_text.insert(tk.INSERT,f"@{qq}","at")
                                    if (end+1) < len(message):
                                        message=message[end+1:]
                                elif "CQ:reply" in message:
                                    end=message.find("]",message.find("]")+1)
                                    monitor_text.insert(tk.INSERT,f"回复:","at")
                                    if (end+1) < len(message):
                                        message=message[end+1:]
                            while i < len(message):
                                while j< len(merged_results) and i<=merged_results[len(merged_results)-1][1]:
                                    if  i < merged_results[j][0]:
                                        monitor_text.insert(tk.INSERT, f"{message[i]}")
                                        i=i+1
                                    elif i>= merged_results[j][0] and i<= merged_results[j][1]:
                                        monitor_text.insert(tk.INSERT, f"{message[i]}","import")
                                        i=i+1
                                    elif i >merged_results[j][1] and i!=merged_results[j+1][0] :
                                        monitor_text.insert(tk.INSERT, f"{message[i]}")
                                        i=i+1
                                        j=j+1
                                    elif i ==merged_results[j+1][0]:
                                        monitor_text.insert(tk.INSERT, f"{message[i]}","import")
                                        i=i+1
                                        j=j+1    
                                if i < len(message):
                                    monitor_text.insert(tk.INSERT, f"{message[i]}")   
                                    i=i+1
                            monitor_text.insert(tk.INSERT, f"\n") 
                        else :
                            monitor_text.insert(tk.INSERT, f"{message}\n")
                    else:
                        if "CQ:image" in message:
                            monitor_text.insert(tk.INSERT, f"图片消息/动画表情(暂不支持查看)\n","unsupport")
                        elif "CQ:record" in message:
                            monitor_text.insert(tk.INSERT, f"语音消息(暂不支持查看)\n","unsupport")
                        elif "CQ:redbag" in message:
                            start=message.find("title")+6                                
                            end=message.find("]")
                            title=message[start:end]
                            monitor_text.insert(tk.INSERT, f"红包消息[{title}](请在手机/平板上查看)\n","redbag")
                        elif "CQ:json" in message:
                            if "address" in message:
                                start=message.find("\"address\":")+11
                                end=message.find("&#44",start)-1
                                address=message[start:end]
                                monitor_text.insert(tk.INSERT, f"地图消息:地址{address}(暂不支持查看)\n","addresss")
                            elif "推荐联系人" in message:
                                start=message.find("推荐联系人")+6
                                end=message.find("&#44",start)-1
                                nickname=message[start:end]
                                start=message.find("账号")+3
                                end=message.find("&#44",start)-1
                                qq=message[start:end]
                                monitor_text.insert(tk.INSERT, f"推荐联系人:昵称:{nickname}QQ:{qq}\n","prompt")
                            elif "加入一起听歌":
                                monitor_text.insert(tk.INSERT, f"加入一起听歌\n","song")
                        else:
                            monitor_text.insert(tk.INSERT, f"暂不支持查看该消息类型\n","unsupport")
            gui2.after(1000,update_monitor_message)

    def update_monitor_text():
        global stop_monitor_update,select_watcher
        watcher=select_watcher.get()
        if not stop_monitor_update:  # 添加停止更新监控文本的判断
            if ("group_id" in message_filter) and (message_filter["group_id"].replace(" ","")!=""):
                order_id = message_filter['group_id']
                monitor_text.delete(1.0, tk.END)
                if watcher=="CerGroup":
                    monitor_text.insert(tk.INSERT, f"现在对您所输入的群聊中的消息:{order_id}进行监控,消息如下:\n" )
                elif watcher=="CerPrivate":
                    monitor_text.insert(tk.INSERT, f"现在对您所选择的好友{order_id}发来的消息:进行监控,消息如下:\n" )
                elif watcher=="AllGroup":
                    monitor_text.insert(tk.INSERT, f"现在对所有群聊中的消息进行监控,消息如下:\n" )
                elif watcher=="AllPrivate":
                    monitor_text.insert(tk.INSERT, f"现在对所有好友发来的消息进行监控,消息如下:\n" )
                elif watcher=="All":
                    monitor_text.insert(tk.INSERT, f"现在对所有群聊和好友发来的消息进行监控,消息如下:\n" )
                update_monitor_message()

    def Show_scheduled_selected():
        global show_scheduled_frame,date_entry,hour_combo,minute_combo,second_combo
        if show_scheduled_frame is None:
            show_scheduled_frame=ttk.Label(scheduled_frame)
            style = ttk.Style()
            #用来设定样式，Custom.TCombobox为标识名字和css中的id类似
            style.configure("Custom.TCombobox", fieldbackground="lightgray")
            # 配置日期选择器的样式
            style.configure("TDateEntry", fieldbackground="#FFC0CB")#pink           
            #配置button的样式1
            style.configure("Custom1.TButton", background="#FFA500", foreground="#8B0000")#orange
            """
            深红棕色：#8B0000
            深褐色：#A52A2A
            火砖红：#B22222
            印度红：#CD5C5C
            淡红棕色：#BC8F8F
            米白色：#F5F5DC
            """
            # 创建 DateEntry 组件
            """
            background: 这是日期选择器部件的背景颜色。
            foreground: 这是日期选择器部件中文本的前景颜色（即文本颜色）。
            date_pattern: 这是日期选择器的日期显示格式。在这个例子中，设置为 "y-mm-dd" 表示日期将以年-月-日的格式显示。
            """
            date_label = ttk.Label(show_scheduled_frame, text="请选择日期\n(年-月-日):")
            date_label.grid(row=0, column=0, padx=(0,10), pady=(0,10))
            date_entry = DateEntry(show_scheduled_frame, width=12, background="#004466", foreground="#FFC0CB", date_pattern="y-mm-dd")
            date_entry.grid(row=0, column=1, padx=10, pady=10)
            """
            创建 Combobox 组件，str(i)是为了将i变为字符串，zfill是为了将字符串的左侧填充0使其够两位
            这个列表会作为 ttk.Combobox 的 values 参数，用于设置组合框的可选值。state="readonly"
            则设置了组合框为只读模式，用户只能从给定的选项中选择，不能自己输入内容。
            """
            time_label = ttk.Label(show_scheduled_frame, text="请选择时间\n(时:分;秒):")
            time_label.grid(row=1, column=0, padx=(0,10), pady=10)        
            hour_combo = ttk.Combobox(show_scheduled_frame, style="Custom.TCombobox", values=[str(i).zfill(2) for i in range(24)], state="readonly", width=5)
            hour_combo.grid(row=1, column=1, padx=5, pady=10)
            minute_combo = ttk.Combobox(show_scheduled_frame, style="Custom.TCombobox", values=[str(i).zfill(2) for i in range(60)], state="readonly", width=5)
            minute_combo.grid(row=1, column=2, padx=(5,20), pady=10)
            second_combo = ttk.Combobox(show_scheduled_frame, style="Custom.TCombobox",values=[str(i).zfill(2) for i in range(60)], state="readonly", width=5)
            second_combo.grid(row=1, column=3, padx=(15,0), pady=10)
            OK_button=ttk.Button(show_scheduled_frame,text="确定定时时间并\n启用定时功能",style="Custom1.TButton",command=scheduled_start)
            OK_button.grid(row=2,column=3,pady=(0,10))
            show_scheduled_frame.grid(row=1)

    def Show_scheduled_selected_destroy():
        global selected_datetime,show_scheduled_frame,time_symbol
        if selected_datetime is not None:
            formatted_datetime = selected_datetime.strftime("%Y-%m-%d %H:%M:%S")
            result = messagebox.askyesno("Confirmation", f"您确定要取消在{formatted_datetime}的定时吗？")
            if result:
                selected_datetime=None#用于打断check_timer函数
                time_symbol.config(text="")
                if show_scheduled_frame is not None :                    
                    show_scheduled_frame.destroy()
                    show_scheduled_frame=None
                    messagebox.showinfo("Reminder",f"已经为您取消在{formatted_datetime}的定时。")
        elif show_scheduled_frame is not None :
            show_scheduled_frame.destroy()
            show_scheduled_frame=None

    def remake_select_judeg():
        global remake_select,fact_count
        remake=remake_select.get()
        if remake == "Yes":
            fact_count=0
            
    def update_sender():
        global group_sym,private_sym,Group_entry,private_entry,show_sender_frame,id_Sym
        if show_sender_frame is not None:
            if group_sym is not None :
                if Group_entry.get() == '':
                    group_sym.config(foreground="#4682B4",text="请输入")#钢蓝色
                    id_Sym=False
                elif Group_entry.get().strip().isdigit():#判断字符串中是否只有数字
                    group_sym.config(foreground="#228B22",text="✔")#森林绿
                    id_Sym=True
                else:
                    group_sym.config(foreground="#FF0000",text="×，QQ名\n称不合法")#鲜红色
                    id_Sym=False
            if private_sym is not None :
                if private_entry.get() == '':
                    private_sym.config(foreground="#4682B4",text="请输入")#钢蓝色
                    id_Sym=False
                elif private_entry.get().strip().isdigit():#判断字符串中是否只有数字
                    private_sym.config(foreground="#228B22",text="✔")#森林绿
                    id_Sym=True
                else:
                    private_sym.config(foreground="#FF0000",text="×，QQ名\n称不合法")#鲜红色
                    id_Sym=False
            gui.after(1000,update_sender)
            
    def update_at():
        global show_sender_frame,at_label,at_qq,show_at_frame,at_sym
        if show_sender_frame is not None and show_at_frame is not None :
            if at_qq.get() == '':
                at_label.config(foreground="#4682B4",text="请输入")#钢蓝色
                at_sym=False
            elif at_qq.get().strip().isdigit():#判断字符串中是否只有数字
                at_label.config(foreground="#228B22",text="✔")#森林绿
                at_sym=True
            else:
                at_label.config(foreground="#FF0000",text="×，QQ名\n称不合法")#鲜红色
                at_sym=False
            gui.after(1000,update_at)
        
    def show_at():
        global show_at_frame,show_sender_frame,group1_frame,at_label,at_qq,show_at_frame
        if show_sender_frame is not None:
            if show_at_frame is None:
                show_at_frame=ttk.Label(group1_frame)
                show_at_frame.grid(row=3,column=0)
                show_label=ttk.Label(show_at_frame,text="请输入@对象的QQ号:")
                show_label.grid(row=0,column=0)
                at_qq=ttk.Entry(show_at_frame)
                at_qq.grid(row=1,column=0,pady=10)
                at_label=ttk.Label(show_at_frame,font=("Verdana",8))
                at_label.grid(row=1,column=1)
                update_at()
                    
    def show_at_destroy():
        global show_at_frame,at_sym,atwho
        if show_at_frame is not None:
            if atwho.get()=="Null":
                at_sym=False
            elif atwho.get()=="User":
                at_sym=True
            show_at_frame.destroy()
            show_at_frame=None
        else:
            if atwho.get()=="Null":
                at_sym=False
            elif atwho.get()=="User":
                at_sym=True
                        
    def Show_group_frame():
        global show_sender_frame,group_frame,private_frame,group_sym,private_sym,Group_entry,atwho,group1_frame,show_at_frame
        if show_sender_frame != None:
            private_sym=None
            if private_frame != None:
                private_frame.destroy()
                private_frame=None
                private_sym=None
            if group_frame == None:
                group_frame=ttk.Label(show_sender_frame)
                group_frame.grid(row=2)
                group_label=ttk.Label(group_frame,text="请输入群聊的群号:")
                group_label.grid(row=0,pady=10,column=0,sticky="w")
                Group_entry=ttk.Entry(group_frame)
                Group_entry.grid(row=0,padx=(10,0),pady=10,column=1)
                group_sym=ttk.Label(group_frame,font=("Verdana",7))
                group_sym.grid(row=0,pady=10,column=2)
                label1=ttk.Label(group_frame,text="是否自动@群聊中的某个人\n(当前功能不支持@全体成员)")
                label1.grid(row=1,column=0,pady=(0,10),sticky="w")
                atwho=tk.StringVar(value="Null")
                group1_frame=ttk.Label(group_frame)
                group1_frame.grid(row=2,column=0)
                show_at_frame=None
                Null=ttk.Radiobutton(group1_frame,text="无需求",value="Null",variable=atwho,command=lambda:[show_at_destroy(),stop_monitor()])
                Null.grid(row=0,column=0,pady=(0,10),sticky="w")
                user=ttk.Radiobutton(group1_frame,text="发送消息的人",value="User",variable=atwho,command=lambda:[show_at_destroy(),stop_monitor()])
                user.grid(row=1,column=0,pady=(0,10),sticky="w")
                others=ttk.Radiobutton(group1_frame,text="其他人(一定要为本群聊内的人,\n否则程序运行监控时会报错)",value="Others",variable=atwho,command=lambda:[show_at(),stop_monitor()])
                others.grid(row=2,column=0,pady=(0,10),sticky="w")
                style=ttk.Style()
                style.configure("Custom2.TButton", background="#FFA500", foreground="#8B0000")#orange
                sender_button=ttk.Button(group_frame,text="确定更改",style="Custom2.TButton",command=change_sender)
                sender_button.grid(row=3,pady=10,padx=5,column=3)
                update_sender()
                
    def Show_private_frame():
        global show_sender_frame,group_frame,private_frame,group_sym,private_sym,private_entry,at_sym
        if show_sender_frame != None:
            group_sym=None
            at_sym=False
            if group_frame != None:
                group_frame.destroy()
                group_frame=None
                group_sym=None                
            if private_frame == None:
                private_frame=ttk.Label(show_sender_frame)
                private_frame.grid(row=2)
                private_label=ttk.Label(private_frame,text="请输入私聊对象QQ号:")
                private_label.grid(row=0,pady=10,column=0)
                private_entry=ttk.Entry(private_frame)
                private_entry.grid(row=0,padx=20,pady=10,column=1)
                private_sym=ttk.Label(private_frame,font=("Verdana",7))
                private_sym.grid(row=0,pady=10,column=2)
                style=ttk.Style()
                style.configure("Custom2.TButton", background="#FFA500", foreground="#8B0000")#orange
                sender_button=ttk.Button(private_frame,text="确定更改",style="Custom2.TButton",command=change_sender)
                sender_button.grid(row=1,pady=10,padx=5,column=3)
                update_sender()
                
    def change_sender():
        global id_Sym,private_sym,private_entry,group_sym,Group_entry,send_type,QQ,change,at_sym,atwho,flask_thread,at_qq       
        if flask_thread:
            user_data_dir = "user_data"
            if not os.path.exists(user_data_dir):
                os.makedirs(user_data_dir)
            never_file5 = os.path.join(user_data_dir, "never_seen5.txt")
            if not os.path.exists(never_file5):
                result=messagebox.askyesno("Confirmation","当前操作会中断监控，更改完后需要重新启动监控，是否继续？")
                if result:
                    stop_monitor()    
                result1=messagebox.askyesno("Confirmation","您是否想下次不显示此类弹窗？")
                if result1:                                        
                    if not os.path.exists(never_file5):
                        with open(never_file5, "w") as file:
                            file.write("Never Seen")
            else:
                result=True
                stop_monitor()
        else:
            result=True
        if id_Sym and result:
            change_settings()
            send_type=None
            change=True#用来标记已经更改
            if private_sym is not None:
                QQ=private_entry.get().strip()
                send_type="private"
            if group_sym is not None:
                QQ=Group_entry.get().strip()
                send_type="group"
            if send_type=="group":
                msg="群聊"
                send="QQ群"
            if send_type=="private":
                msg="私聊"
                send="好友"
            if send_type=="group":
                if not at_sym and atwho.get()=="Null":
                    result=messagebox.askyesno("Confirmation",f"您是否要将发送对象改为{send}({QQ})({msg})？")
                elif not at_sym and atwho.get()=="Others" :
                    messagebox.showwarning("Warning",f"您输入@对象的QQ不合法或仍未输入。")
                else:
                    if atwho.get()=="User":
                        result=messagebox.askyesno("Confirmation",f"您是否要将发送对象改为{send}({QQ})({msg}),并自动在群中@消息的发送者？")
                    elif atwho.get()=="Others":
                        qq=at_qq.get().strip()
                        result=messagebox.askyesno("Confirmation",f"您是否要将发送对象改为{send}({QQ})({msg}),并自动在群中@{qq}？")
            elif send_type=="private":
                result=messagebox.askyesno("Confirmation",f"您是否要将发送对象改为{send}({QQ})({msg})？")
            if not result:
                send_type=None
                QQ=None
                change=False
            else:
                messagebox.showinfo("Reminder",f"已为您修改对应设置。")
        else:
            messagebox.showwarning("Warning","您还未输入对应QQ号或者输入不合法，请检查后重试。")
    
    def Show_sender_selected():
        global show_sender_frame,type_select,group_frame,private_frame
        if show_sender_frame == None:
            show_sender_frame=ttk.Label(sender_frame)
            sender_label=ttk.Label(show_sender_frame,text="--请选择发送消息的类型")
            sender_label.grid(row=0,column=0,sticky="w")
            type_select=tk.StringVar()
            group_frame=None
            private_frame=None
            group=ttk.Radiobutton(show_sender_frame,text="群聊",value="group",variable=type_select,command=Show_group_frame)
            group.grid(row=1,column=0,sticky="w")
            private=ttk.Radiobutton(show_sender_frame,text="私聊",value="private",variable=type_select,command=Show_private_frame)
            private.grid(row=1,column=1,sticky="e")
            show_sender_frame.grid(row=1)
            
    def Show_sender_selected_destroy():
        global show_sender_frame,typer_select,send_type,QQ,id_Sym,change,private_entry,Group_entry
        if show_sender_frame != None:
            if change:
                if send_type=="group":
                    msg="群聊"
                    send="QQ群"
                if send_type=="private":
                    msg="私聊"
                    send="好友"
                result=messagebox.askyesno("Confirmation",f"您是否想将发送对象从{send}({QQ})({msg})改回默认？")
                if result:
                    show_sender_frame.destroy()
                    show_sender_frame=None
                    change=False
                    id_Sym=False
                    Group_entry=None
                    private_entry=None
            else:
                show_sender_frame.destroy()
                show_sender_frame=None
                change=False
                id_Sym=False
                Group_entry=None
                private_entry=None
                   
    def Show_count_selected():
        def on_validate(P):#阻止输入其他内容整数除外
            if P == "":
                return True
            try:
                int(P)
                return True
            except ValueError:
                return False
        global count_spinbox,show_count_frame,pattern_select
        if show_count_frame is None:
            show_count_frame=ttk.Label(count_frame)
            count_label=ttk.Label(show_count_frame,text="请选择检测/发送次数:")
            count_label.grid(row=0,column=0,padx=(0,10),pady=10)
            style = ttk.Style()
            style.configure("TSpinbox", background="lightblue", foreground="#004466",arrowcolor="#A52A2A",arrowsize=12)
            count_var=tk.IntVar()
            count_spinbox=ttk.Spinbox(show_count_frame,from_=1,to=100,textvariable=count_var,validate="key", validatecommand=(show_count_frame.register(on_validate), "%P"),style="TSpinbox")
            count_spinbox.grid(row=0,column=1,padx=20,pady=10)            
            #配置button的样式2
            style.configure("Custom2.TButton", background="#FFA500", foreground="#8B0000")#orange
            Makesure_button=ttk.Button(show_count_frame,text="确定检测/发送次数\n并启用功能",command=count_start,style="Custom2.TButton")
            Makesure_button.grid(row=3,column=2,pady=(0,10))
            show_count_frame.grid(row=1)

    def Show_count_selected_destroy():
        global count_spinbox,show_count_frame,count_symbol_label,pattern_start,count,pattern_select,fact_count_symbol_label
        if isinstance(pattern_select, tk.StringVar):
            pattern=pattern_select.get()
        elif isinstance(pattern_select, str):
            pattern=pattern_select
        if not pattern_start :#已经开始有限制模式
            result = messagebox.askyesno("Confirmation", f"您确定要将确定检测/发送次数从{count}({pattern})改回无限制吗？")
            if result:
                pattern_start=True
                count=0
                count_symbol_label.config(text="当前设置的检测/发生次数:无限制")
                fact_count_symbol_label.config(text="")
                if show_count_frame is not None:
                    show_count_frame.destroy()
                    show_count_frame=None
                    messagebox.showinfo("Reminder",f"已经为您将确定检测/发送次数从{count}({pattern})改回无限制。")
        elif show_count_frame is not None:
            show_count_frame.destroy()
            show_count_frame=None

    def count_start():
        global count_spinbox,count_symbol_label,count,pattern_select,pattern_start,fact_count
        count=count_spinbox.get()
        fact_count=0
        if count == "":
            messagebox.showwarning("Warning","您还未输入检测/发送次数，请检查确认无误后再启动该功能")
        else :
            count=int(count)
            if isinstance(pattern_select, tk.StringVar):
                pattern=pattern_select.get()
            elif isinstance(pattern_select, str):
                pattern=pattern_select
            if pattern == "Pattern1":
                result=messagebox.askyesno("Confirmation",f"您当前选择了Pattern1来实现此功能，本程序将在检测到符合消息并发送对应消息{count}次后关闭程序，是否继续？")
                if result:
                    pattern_start=False
                    count_symbol_label.config(text=f"当前设置的检测/发生次数:\n{count}(Pattern1)")
                    fact_count_symbol_label_update()
                    pattern1_start()
            elif pattern == "Pattern2" :
                result=messagebox.askyesno("Confirmation",f"您当前选择了Pattern2来实现此功能，本程序将在检测到符合消息并发送对应消息{count}次后停止监控，但不会关闭程序，是否继续？")
                if result:
                    pattern_start=False
                    count_symbol_label.config(text=f"当前设置的检测/发生次数:\n{count}(Pattern2)")
                    fact_count_symbol_label_update()
                    pattern2_start()
                    
    def pattern1_start():
        global pattern_start,count,fact_count,conflict1,solution_select,conflict2,selected_datetime,plan_select
        if not pattern_start:
            if not conflict1:#不存在冲突1,存在冲突1时，一定没有冲突2，所以不在下方进行判别
                if count == fact_count:
                    if selected_datetime is not None:#启用定时功能
                        current_time = datetime.now()
                        if current_time < selected_datetime:#存在冲突2
                            conflict2=True
                            plan=plan_select.get()
                            if plan == "Plan1" or plan == "Plan2":
                                pattern_start=True
                                exit_program(windowgui)
                            elif plan == "Plan3":
                                pattern_start=True
                                selected_datetime=None#取消定时系统
                                stop_monitor()
                            elif plan == "Plan4":
                                pattern_start=True
                                stop_monitor()
                        else:#不存在冲突2
                            conflict2=False
                            pattern_start=True
                            exit_program(windowgui)
                    else:#未启用定时功能
                        conflict2=False
                        pattern_start=True
                        exit_program(windowgui)
                gui.after(1000,pattern1_start)
            elif conflict1:#存在冲突1
                conflict2=False
                solution=solution_select.get()
                if solution == "Solution2" or solution == "Solution4":#不考虑Solution1的情况
                    if count==fact_count:
                        pattern_start=True
                        exit_program(windowgui)
                    gui.after(1000,pattern1_start)
                elif solution == "Solution3":
                    if count==fact_count:
                        pattern_start=True
                        stop_monitor()
                    gui.after(1000,pattern1_start)

    def pattern2_start():
        global pattern_start,count,fact_count,conflict1,solution_select,conflict2,selected_datetime,plan_select
        if not pattern_start:
            if not conflict1:#不存在冲突1,存在冲突1时，一定没有冲突2，所以不在下方进行判别
                if count == fact_count:
                    if selected_datetime is not None:#启用定时功能
                        current_time = datetime.now()
                        if current_time < selected_datetime:#存在冲突2
                            conflict2=True
                            plan=plan_select.get()
                            if plan == "Plan1":
                                pattern_start=True
                                exit_program(windowgui)
                            elif plan == "Plan3":
                                pattern_start=True
                                selected_datetime=None#取消定时系统
                                stop_monitor()
                            elif plan == "Plan4" or plan == "Plan2":
                                pattern_start=True
                                stop_monitor()
                        else:#不存在冲突2
                            conflict2=False
                            pattern_start=True
                            exit_program(windowgui)
                    else:#未启用定时功能
                        conflict2=False
                        pattern_start=True
                        exit_program(windowgui)
                gui.after(1000,pattern2_start)
            elif conflict1:#存在冲突1
                solution=solution_select.get()
                if solution == "Solution2":#不考虑Solution1的情况
                    if count==fact_count:
                        pattern_start=True
                        exit_program(windowgui)
                    gui.after(1000,pattern2_start)
                elif solution == "Solution3" or solution == "Solution4":
                    if count==fact_count:
                        pattern_start=True
                        stop_monitor()
                    gui.after(1000,pattern2_start)

    def check_timer():
        global selected_datetime,solution_select,fact_count,count,time_symbol,coflict1
        if selected_datetime:
            # 获取当前时间
            current_time = datetime.now()
            # 计算当前时间与用户选择时间的时间差
            time_difference = selected_datetime - current_time
            # 定义触发关闭的时间间隔（1s）
            trigger_time_interval = timedelta(seconds=1)
            # 如果时间差小于等于触发时间间隔，关闭程序
            if abs(time_difference) <= trigger_time_interval:
                solution=solution_select.get()
                if count != 0:#当计数开始运作时
                    if fact_count < count:#满足冲突1时
                        conflict=True#冲突1变量存在
                        if solution == "Solution1":
                            exit_program(windowgui)
                        else :#其他模式停止定时
                            selected_datetime=None
                            time_symbol.config(text="")
                    else :
                        conflict1=False
                        exit_program(windowgui)
                else :
                    conflict1=False
                    exit_program(windowgui)
                # 每隔一段时间调用自身，继续检查                
            windowgui.after(1000, check_timer)  # 每隔 1 秒钟调用自身
            
    def scheduled_start():
        global date_entry,hour_combo,minute_combo,second_combo,selected_datetime
        # 获取日期
        selected_date= date_entry.get_date()
        # 如果日期为datetime.min说明使用的DateEntry的默认日期，没有进行选择，则使用默认日期(这么操作避免报错)
        if selected_date == date.today():
            selected_date = date.today()  
        selected_hour = hour_combo.get()
        selected_minute = minute_combo.get()
        selected_second = second_combo.get()
        # 检查是否选择了完整的时间
        if not selected_hour or not selected_minute or not selected_second:
            messagebox.showwarning("Warning!","您的定时时间还未填写完整！")
        else:
            # 将选择的日期和时间拼接为 datetime 对象
            selected_datetime = datetime.combine(selected_date, datetime.strptime(f"{selected_hour}:{selected_minute}:{selected_second}", "%H:%M:%S").time())
            Current_time=datetime.now()
            formatted_datetime = selected_datetime.strftime("%Y-%m-%d %H:%M:%S")
            Current_datatime=Current_time.strftime("%Y-%m-%d %H:%M:%S")
            if selected_datetime < Current_time :
                messagebox.showwarning("Warning!",f"您的定时时间{formatted_datetime}比当前时间{Current_datatime}还早，请检查您的定时时间是否设置有误！")
            else:
                result = messagebox.askyesno("Confirmation", f"您确定要定时在{formatted_datetime}(可能会误差1s左右)时，将程序进行关闭吗？")
                if result:
                    update_time_symbol()
                    check_timer()

    def readonly_entry_state(entry):
        current_state = entry.cget("state")  # 获取当前状态
        if not current_state == "readonly":
            entry.config(state="readonly")  # 切换到只读状态

    def toggle_entry_state(entry):
        entry.config(state="normal")  # 切换到可编辑状态
            
    def change_watcher():
        global select_watcher,group_symbol,group_entry,group_change,group_label
        if select_watcher.get()=="CerPrivate":
            result=messagebox.askyesno("Confirmation","确定将监控对象改为特定好友吗(会终止当前监控)？")
            if result:
                if group_change:
                    group_change=False
                    update_group_symbol()
                stop_monitor()
                group_label.config(text="好友QQ号:")                
                toggle_entry_state(group_entry)
                group_entry.delete(0,tk.END)
                messagebox.showinfo("Reminder","当前已为您将监控对象修改为特定好友。")
        elif select_watcher.get()=="CerGroup":
            result=messagebox.askyesno("Confirmation","确定将监控对象改为特定群聊吗(会终止当前监控)？")
            if result:
                if group_change:
                    group_change=False
                    update_group_symbol()
                stop_monitor()
                group_label.config(text="QQ群号:")
                toggle_entry_state(group_entry)
                group_entry.delete(0,tk.END)
                messagebox.showinfo("Reminder","当前已为您将监控对象修改为特定群聊。")
        elif select_watcher.get()=="AllPrivate":
            result=messagebox.askyesno("Confirmation","确定将监控对象改为全体好友吗(会终止当前监控)？")
            if result:
                group_change=True
                stop_monitor()
                group_symbol.config(text="")
                group_label.config(text="当前正在监\n控全体好友")
                group_entry.delete(0,tk.END)
                group_entry.insert(tk.END,"当前禁止输入")
                readonly_entry_state(group_entry)
                messagebox.showinfo("Reminder","当前已为您将监控对象修改为全体好友。")             
        elif select_watcher.get()=="AllGroup":
            result=messagebox.askyesno("Confirmation","确定将监控对象改为全体群聊吗(会终止当前监控)？")
            if result:
                group_change=True
                stop_monitor()
                group_symbol.config(text="")
                group_label.config(text="当前正在监\n控全体群聊")
                group_entry.delete(0,tk.END)
                group_entry.insert(tk.END,"当前禁止输入")
                readonly_entry_state(group_entry)
                messagebox.showinfo("Reminder","当前已为您将监控对象修改为全体群聊。")
        elif select_watcher.get()=="All":
            result=messagebox.askyesno("Confirmation","确定将监控对象改为全体群聊和好友吗(会终止当前监控)？")
            if result:
                group_change=True
                stop_monitor()
                group_symbol.config(text="")
                group_label.config(text="当前正在监控全\n体群聊和好友")
                group_entry.delete(0,tk.END)
                group_entry.insert(tk.END,"当前禁止输入")
                readonly_entry_state(group_entry)
                messagebox.showinfo("Reminder","当前已为您将监控对象修改为全体群聊和好友。")

    def change_http_settings():
        global change_http,change_http_post,http_var,http_post_var,http_change,flask_thread,http_default,HTTP_set,HTTP_POST_set
        if change_http and change_http_post:
            if flask_thread:
                result=messagebox.askyesno("Confirmation","当前操作会终止当前的监控，您是否愿意？")
                if result:
                   stop_monitor()
                   http_num=http_var.get()
                   http_post_num=http_post_var.get()
                   http_change=True
                   http_default=False
                   HTTP_set=http_var.get().strip()
                   HTTP_POST_set=http_post_var.get().strip()
                   messagebox.showinfo("Reminder",f"当前已为您将HTTP监听地址端口号改为{http_num},反向HTTP POST地址端口号改为{http_post_num}")
                else :
                   http_change=False
            else:
                stop_monitor()
                http_num=http_var.get()
                http_post_num=http_post_var.get()
                result=messagebox.askyesno("Confirmation",f"当前操作会将HTTP监听地址端口号改为{http_num},反向HTTP POST地址端口号改为{http_post_num}，是否继续？")
                if result:
                   http_change=True
                   http_default=False
                   HTTP_set=http_var.get().strip()
                   HTTP_POST_set=http_post_var.get().strip()
                   messagebox.showinfo("Reminder",f"当前已为您将HTTP监听地址端口号改为{http_num},反向HTTP POST地址端口号改为{http_post_num}")
                else :
                   http_change=False
        elif not change_http and http_var.get()!="":
            messagebox.showwarning("Warning","您输入的HTTP监听地址端口号不合法!")
        elif not change_http and http_var.get()=="":
            messagebox.showwarning("Warning","您输入的HTTP监听地址端口号为空!")
        elif not change_http_post and http_post_var.get()!="":
            messagebox.showwarning("Warning","您输入的反向HTTP POST地址端口号不合法!")
        elif not change_http_post and http_post_var.get()=="":
            messagebox.showwarning("Warning","您输入的反向HTTP POST地址端口号为空!")

    def update_http_show():
        global http_show_label,http_change,update_or_symbol,http_var,http_post_var
        if update_or_symbol:
            if http_change:
                HTTP=http_var.get().strip()
                HTTP_POST=http_post_var.get().strip()
                http_show_label.config(text=f"提醒:当前HTTP监控端口号为{HTTP},HTTP POST地址的端口号为{HTTP_POST}")
                http_change=False
            gui.after(1000,update_http_show)

    def change_theme(event):
        #用于切换主题
        selected_theme = theme_combobox.get()
        style1.set_theme(selected_theme)
        windowgui.configure(bg=style1.lookup("TFrame", "background"))

    show_first_time_message()
    
    windowgui = ThemedTk(theme="arc")
    windowgui.title("QQ监听脚本2.0.0")
    windowgui.geometry("640x640")
    windowgui.resizable(False, False)

    notebook=ttk.Notebook(windowgui)
    
    Gui=tk.Frame(notebook)#对程序主页面进行设置
    # 创建一个 Canvas 包裹设置界面内容
    Gui_canvas = tk.Canvas(Gui)
    Gui_canvas.pack(side="left", fill="both", expand=True)
    
    # 创建一个垂直滚动条并绑定到 Canvas
    Gui_scrollbar = tk.Scrollbar(Gui, orient="vertical", command=Gui_canvas.yview)
    Gui_scrollbar.pack(side="right", fill="y")
    Gui_canvas.configure(yscrollcommand=Gui_scrollbar.set)

    # 创建一个 Frame，用于放置设置界面内容
    Gui_frame = tk.Frame(Gui_canvas)
    Gui_canvas.create_window((0, 0), window=Gui_frame, anchor="nw")
    
    gui=tk.Frame(Gui_frame)
    empty_label=ttk.Label(gui)
    empty_label.grid(row=0,column=2)
    
    global group_symbol,group_entry,group_label    
    group_label = ttk.Label(gui, text="QQ群号:")
    group_label.grid(row=1,column=2)
    group_entry = ttk.Entry(gui)
    group_entry.grid(row=2,column=2)
    group_symbol=ttk.Label(gui)
    group_symbol.grid(row=2,column=3,sticky="w")
    update_group_symbol()

    keyword_label = ttk.Label(gui, text="在消息中可能会\n出现的关键词：")
    keyword_label.grid(row=3,column=2)
    style = ttk.Style()
    style.configure("Custom4.TLabel",foreground="#FFD700")
    style.configure("Custom5.TLabel",foreground="#A52A2A")
    global or_label1,or_label2,keyword1_entry,keyword2_entry,keyword3_entry,keyword_symbol
    keyword_symbol=ttk.Label(gui,font=("Verdana",8),style="Custom5.TLabel")
    keyword_symbol.grid(row=3,column=4)
    keyword1_entry = ttk.Entry(gui)
    keyword1_entry.grid(row=4,column=0,padx=5)
    or_label1=ttk.Label(gui,font=("Verdana",9),style="Custom4.TLabel")
    or_label1.grid(row=4,column=1)
    keyword2_entry = ttk.Entry(gui)
    keyword2_entry.grid(row=4,column=2)
    or_label2=ttk.Label(gui,font=("Verdana",9),style="Custom4.TLabel")
    or_label2.grid(row=4,column=3)
    keyword3_entry = ttk.Entry(gui)
    keyword3_entry.grid(row=4,column=4,padx=5)

    style.configure("Custom5.TLabel",foreground="#CD5C5C")
    style.configure("Custom6.TLabel",foreground="#C5E1A5")#奶绿色
    necessary_label=ttk.Label(gui,text="在消息中必须要\n出现的关键词：")
    necessary_label.grid(row=5,column=2)
    global and_label1,and_label2,necessary1_entry,necessary2_entry,necessary3_entry,necessary_symbol
    necessary_symbol=ttk.Label(gui,font=("Verdana",8),style="Custom6.TLabel")
    necessary_symbol.grid(row=5,column=4)
    necessary1_entry = ttk.Entry(gui)
    necessary1_entry.grid(row=6,column=0,padx=5)
    and_label1=ttk.Label(gui,font=("Verdana",9),style="Custom5.TLabel")
    and_label1.grid(row=6,column=1)
    necessary2_entry = ttk.Entry(gui)
    necessary2_entry.grid(row=6,column=2)
    and_label2=ttk.Label(gui,font=("Verdana",9),style="Custom5.TLabel")
    and_label2.grid(row=6,column=3)
    necessary3_entry = ttk.Entry(gui)
    necessary3_entry.grid(row=6,column=4,padx=5)
       
    send_message_label=ttk.Label(gui,text="需要发送的字段")
    send_message_label.grid(row=7,column=2)
    
    global send_message_entry,send_msg_symbol 
    send_message_entry=ttk.Entry(gui)
    send_message_entry.grid(row=8,column=2)
    send_msg_symbol=ttk.Label(gui)
    send_msg_symbol.grid(row=8,column=3)
    update_send_msg_symbol()
    
    empty_label0=ttk.Label(gui)
    empty_label0.grid(row=9,column=2)
    
    style.configure("Custom7.TLabel",foreground="#800080")#紫色
    global show_label
    show_label=ttk.Label(gui, wraplength=600, justify="left", anchor="w",font=("Tahoma",10),style="Custom7.TLabel")
    show_label.grid(row=10,column=0,columnspan=5,padx=10)
    
    empty_label7=ttk.Label(gui)
    empty_label7.grid(row=11,column=2)

    time_intrlabel=ttk.Label(gui,text="当前时间")
    time_intrlabel.grid(row=12,column=2)
    time_label=ttk.Label(gui,font=("Helvetica", 14))
    time_label.grid(row=13,column=2)
    update_time()#开始更新时间

    global time_symbol
    
    time_symbol=ttk.Label(gui,font=("Helvetica",8))
    time_symbol.grid(row=14,column=2)

    global count_symbol_label,fact_count_symbol_label,solution_plan_show_label
     #配置label的样式1
    style=ttk.Style()
    style.configure("Custom1.TLabel", foreground="#FF5733", background="#87CEEB")#橘红色，天蓝
    style.configure("Custom2.TLabel", foreground="#0D47A1", background="#757575")#浅蓝色，灰色
    style.configure("Custom3.TLabel", foreground="#000000", background="#FFD700")#黑色,金色

    count_symbol_label=ttk.Label(gui,font=("Helvetica",10),style="Custom1.TLabel")
    count_symbol_label.grid(row=15,column=2)
    count_symbol_label.config(text="当前设置的检测/发生次数:无限制")

    fact_count_symbol_label=ttk.Label(gui,font=("Helvetica",10),style="Custom2.TLabel")
    fact_count_symbol_label.grid(row=16,column=2)

    solution_plan_show_label=ttk.Label(gui,font=("Helvetica",10),style="Custom3.TLabel")
    solution_plan_show_label.grid(row=17,column=2)
    solution_plan_show()
    
    empty_label10=ttk.Label(gui)
    empty_label10.grid(row=18,column=2)

    #通过按钮实时对flask线程的开启
    global click_count,start_monitor_button,flask_thread
    start_monitor_button = ttk.Button(gui, text="开始监控", command=lambda:[apply_filter(),remake_select_judeg(),start_monitoring(),update_show_label(),increase_count(),change_config(),update_monitor_text() if flask_thread else None])
    start_monitor_button.grid(row=19,column=2)

    gui2=tk.Frame(Gui_frame)

    empty_label8=ttk.Label(gui2)
    empty_label8.grid(row=0,column=2,padx=300)
    
    global monitor_text
    monitor_text=tk.Text(gui2,height=20,width=60)
    monitor_text.grid(row=1,column=2)

    monitor_text.tag_config("role",foreground="green",font=("Arial", 10 ,"bold"))#头衔加粗加大绿色
    monitor_text.tag_config("time",foreground="blue",font=("Arial", 10 ))#时间蓝色
    monitor_text.tag_config("sender_card",foreground="brown",font=("Arial", 9 ,"bold"))#群昵称棕色
    monitor_text.tag_config("sender",foreground="gray",font=("Arial", 9 ,"bold"))#灰色其他信息
    monitor_text.tag_config("import",foreground="red",font=("Arial", 9 ,"bold"))#红色关键词
    monitor_text.tag_config("at",foreground="#32CD32",font=("Arial", 8 ))#at,酸橙绿
    monitor_text.tag_config("redbag",foreground="#FA8072",font=("Arial", 8 ))#redbag,鲑鱼色
    monitor_text.tag_config("prompt",foreground="#C0C0C0",font=("Arial", 8 ))#prompt,银色
    monitor_text.tag_config("address",foreground="#D2691E",font=("Arial", 8 ))#address,巧克力色
    monitor_text.tag_config("unsupport",foreground="#2E8B57",font=("Arial", 8 ))#unsupport,海洋绿
    monitor_text.tag_config("song",foreground="#FF8C00",font=("Arial", 8 ))#song,深橙色
    
    empty_label5=ttk.Label(gui2)
    empty_label5.grid(row=2,column=2)

    stop_button =ttk.Button(gui2,text="终止监控",command=lambda:[stop_monitor(),change_config()])
    stop_button.grid(row=3,column=2)

    empty_label6=ttk.Label(gui2)
    empty_label6.grid(row=4,column=2)
    
    exit_button = ttk.Button(gui2, text="安全退出", command=lambda:ask_exit_program(windowgui))
    exit_button.grid(row=5,column=2)

    gui.grid()
    gui2.grid(row=20)
    # 配置 Canvas 的滚动区域
    Gui_frame.bind("<Configure>", lambda event: Gui_canvas.configure(scrollregion=Gui_canvas.bbox("all")))

    Gui.grid()
    
    help_frame=tk.Frame(notebook)#对使用帮助界面进行设置
    
    help_label=ttk.Label(help_frame
                        ,text="""
                                                    使用说明：                   
    本程序用于监控QQ中某个特定群聊中符合条件的消息(在本版本中，程序添加更多功能)，
程序开发基于go-cqhttp机器人框架。可以通过网站https://docs.go-cqhttp.org自行下载
go-cqhttp并按照其要求进行相对应的配置(提醒：最近由于QQ风控严重，可能使用go-cqhttp
时会导致QQ封号，但只会短暂封号，经过第一次封禁后，直接申请后会解封，后续就不会连续
封号，再次声明封号与本程序无关，账号封禁是因为go-cqhttp的接口风控等问题导致)。
    使用该程序前，请确定后台go-cqhttp已经配置好并挂起，该程序默认HTTP监听端口号为5
700，反向HTTP POST地址端口号为5071，所以请将go-cqhttp的HTTP监听端口号设置为5700，
反向HTTP POST地址端口号设置为5071，否则该程序无法正常运行！若您的5700,5701端口已经
被占用，该版本直接提供修改监听端口的功能，便于不会修改源码的用户使用，记住修改后的端
口号，同样要与go-cqhttp的配置文件中一致，否则程序不会按照要求运行。
    以上为使用程序的前置要求(不会配置，请访问https://github.com/certainstar/littl
e-Python-software官方网站见本程序的配置教学)，在完成上述要求后，启动本程序，输入需要
监听的QQ群号(在此版本中您可设置其他对象)，关键词和需要发送的消息，点击上传后，再点击
开始监听，此时程序若无警告弹窗，则证明其已经开始监听。开始监听后，会对含有关键词的消
息（本版本对消息的筛查条件可自行设置）进行筛查，发现有满足的消息后，会对您设置的对象
发送输入的要求发送的消息。
    例如：输入群号123，关键词“是的”（输入时不用打引号）,“ok”,发送消息“成功”，
就会对群号123中的消息进行监控，如果李四发送如“是的我在”或“可以我ok的“消息时，该
程序会自动给李四发送“成功”，注意：必须存在的关键词的三栏是并关系，而可能的关键词三栏
是或关系，请注意，详情见设置。
    提醒：本程序只能和是好友的人发送消息。
    注意：该程序长时间挂着会导致电脑发热，避免发生不必要的麻烦，记得在电脑过热时将程
序关闭，同时由于本程序打开时，也会有终端弹窗出现，为正常显示情况，在关闭程序时，注意
终端是否关闭，不然程序实际上仍然有一部分功能在运行，请大家注意！
    本程序在运行过程中，会有很多小字部分的提醒请您仔细观察，并按照程序要求进行，否则程
序可能会出现意想不到的bug.
    再次提醒，本程序中的部分选项点击后，会自动停止当前的监控（没有提示），是一个自我保
护措施，避免部分问题，希望见谅。
    版本2.0.0可能会含有不少bug，所以在使用时遇到bug，请与开发者进行联系，开发者email：
2378145658@qq.com
    """, anchor="w" ,justify="left")
    help_label.grid(row=0,column=1,padx=60)

    help_frame.grid()
    
    Morefuction=tk.Frame(notebook)#对更多功能进行设置

    # 创建一个 Canvas 包裹设置界面内容
    Morefuction_canvas = tk.Canvas(Morefuction)
    Morefuction_canvas.pack(side="left", fill="both", expand=True)

    # 创建一个垂直滚动条并绑定到 Canvas
    Morefuction_scrollbar = tk.Scrollbar(Morefuction, orient="vertical", command=Morefuction_canvas.yview)
    Morefuction_scrollbar.pack(side="right", fill="y")
    Morefuction_canvas.configure(yscrollcommand=Morefuction_scrollbar.set)

    # 创建一个 Frame，用于放置设置界面内容
    Morefuction_frame = tk.Frame(Morefuction_canvas)
    Morefuction_canvas.create_window((0, 0), window=Morefuction_frame, anchor="nw")
    
    scheduled_frame = ttk.LabelFrame(Morefuction_frame,text="定时关闭功能设置")
    scheduled_frame.grid(row=0,column=0,padx=(5,0),pady=10)

    select_scheduled_frame=ttk.Label(scheduled_frame)
    select_scheduled_frame.grid(row=0)
    
    scheduled_label=ttk.Label(select_scheduled_frame,text="请选择是/否使用定时功能(默认为否)")
    scheduled_label.grid(row=0,column=0,padx=(5,0),pady=(10,0))
    
    scheduled_selected_option = tk.StringVar(value="no")
    
    no_option = ttk.Radiobutton(select_scheduled_frame, text="否", value="no", variable=scheduled_selected_option,command=Show_scheduled_selected_destroy)
    no_option.grid(row=1,column=0,pady=(10,10),sticky="w")
    yes_option = ttk.Radiobutton(select_scheduled_frame, text="是", value="yes", variable=scheduled_selected_option,command=Show_scheduled_selected)
    yes_option.grid(row=1,column=1,padx=(20,320),pady=(10,10))
    
    count_frame=ttk.LabelFrame(Morefuction_frame,text="检测/发送数量设置")
    count_frame.grid(row=1,column=0,padx=(5,0))
    
    select_count_frame=ttk.Label(count_frame)
    select_count_frame.grid(row=0)

    select_count_label=ttk.Label(select_count_frame,text="检测/发送数量选择(默认为无限制)")
    select_count_label.grid(row=0,column=0,padx=5,pady=(10,10))

    select_count_option = tk.StringVar(value="unlimited")
    
    unlimited_option=ttk.Radiobutton(select_count_frame,text="无限制",value="unlimited",variable=select_count_option,command=Show_count_selected_destroy)
    unlimited_option.grid(row=1,column=0,pady=(0,10),sticky="w")
    limited_option=ttk.Radiobutton(select_count_frame,text="有限制",value="limited",variable=select_count_option,command=Show_count_selected)
    limited_option.grid(row=1,column=1,padx=(20,300),pady=(0,10))

    global sender_frame
    sender_frame = ttk.LabelFrame(Morefuction_frame,text="对发送消息的对象进行设置")
    sender_frame.grid(row=3,column=0,padx=(5,0),pady=10)

    select_sender_frame=ttk.Label(sender_frame)
    select_sender_frame.grid(row=0)
    
    select_sender_label=ttk.Label(select_sender_frame,text="请选择发送消息的对象(默认为将消息发送给发出符合条件消息的人):")
    select_sender_label.grid(row=0,column=0,padx=(5,0),pady=(10,0))
    
    select_sender = tk.StringVar(value="user")
    
    user_option = ttk.Radiobutton(select_sender_frame, text="发出符合条件消息的人", value="user", variable=select_sender,command=Show_sender_selected_destroy)
    user_option.grid(row=1,column=0,pady=(10,10),sticky="w")
    other_option = ttk.Radiobutton(select_sender_frame, text="其他人/其他方式", value="other", variable=select_sender,command=Show_sender_selected)
    other_option.grid(row=1,column=1,padx=(20,80),pady=(10,10))

    global select_watcher
    watcher_frame = ttk.LabelFrame(Morefuction_frame,text="对发送消息的对象进行设置")
    watcher_frame.grid(row=4,column=0,padx=(5,0),pady=(0,10))

    select_watcher_frame=ttk.Label(watcher_frame)
    select_watcher_frame.grid(row=0)
    
    select_watcher_label=ttk.Label(select_watcher_frame,text="--请选择发送监控消息的对象(默认为指定群聊):")
    select_watcher_label.grid(row=0,column=0,padx=(5,330),pady=(10,0),sticky="w")

    select_watcher_frame1=ttk.Label(watcher_frame)
    select_watcher_frame1.grid(row=1)
    select_watcher = tk.StringVar(value="CerGroup")
    
    cerGroup_option = ttk.Radiobutton(select_watcher_frame1, text="指定好友", value="CerPrivate", variable=select_watcher,command=stop_monitor)
    cerGroup_option.grid(row=0,column=0,pady=(10,10),sticky="w")
    cerPrivate_option = ttk.Radiobutton(select_watcher_frame1, text="指定群聊", value="CerGroup", variable=select_watcher,command=stop_monitor)
    cerPrivate_option.grid(row=0,column=1,pady=(10,10),sticky="w")
    allPrivate_option= ttk.Radiobutton(select_watcher_frame1, text="全体好友", value="AllPrivate", variable=select_watcher,command=stop_monitor)
    allPrivate_option.grid(row=0,column=2,pady=(10,10),sticky="w")
    allGroup_option= ttk.Radiobutton(select_watcher_frame1, text="全体群聊", value="AllGroup", variable=select_watcher,command=stop_monitor)
    allGroup_option.grid(row=0,column=3,pady=(10,10),sticky="w")
    all_option= ttk.Radiobutton(select_watcher_frame1, text="全体群体和好友", value="All", variable=select_watcher,command=stop_monitor)
    all_option.grid(row=0,column=4,pady=(10,10),sticky="w")
    #配置button的样式2
    style=ttk.Style()
    style.configure("Custom2.TButton", background="#FFA500", foreground="#8B0000")#orange
    certain_button=ttk.Button(select_watcher_frame1,text="确定",style="Custom2.TButton",command=change_watcher)
    certain_button.grid(row=1,column=5,pady=(0,10))
  
    global http_var,http_post_var,http_ok,http_post_ok,http_show_label
    http_frame = ttk.LabelFrame(Morefuction_frame,text="对端口(HTTP监听地址,反向HTTP POST地址)进行设置")
    http_frame.grid(row=5,column=0,padx=(5,0),pady=(0,10))

    select_http_frame=ttk.Label(http_frame)
    select_http_frame.grid(row=0)
    
    select_http_label=ttk.Label(http_frame,text="--请分别输入两个端口(分别默认为5700,5701):")
    select_http_label.grid(row=0,column=0,padx=(5,330),pady=(10,0),sticky="w")
    reminder_label=ttk.Label(http_frame,text="注：该两个端口一定要与go-cqhttp中设置一致，否则程序会监控失效！同时本功能是为了部分5700\n和5701端口被占用的用户更加方便，建议没有被占用的用户使用默认端口。(详见帮助界面)",font=("Helvetica", 8, "bold italic"),foreground="red")
    reminder_label.grid(row=1,column=0,padx=5,pady=10,sticky="w")
    select_http_frame1=ttk.Label(http_frame)
    select_http_frame1.grid(row=2)
    
    http_label=ttk.Label(select_http_frame1,text="请输入HTTP监听地址的端口号(0-65535):")
    http_label.grid(row=0,column=0,padx=5,pady=(10,0),sticky="w")
    style.configure("TSpinbox", foreground="#1E90FF", arrowsize=12)#藏蓝色
    http_var = tk.StringVar()
    http_entry = ttk.Spinbox(select_http_frame1, from_=0, to=65535, textvariable=http_var,validate="key", validatecommand=(select_http_frame1.register(on_validate), "%P"),style="TSpinbox")
    http_entry.grid(row=0, column=1, padx=5,pady=(10,0))
    http_entry.delete(0,tk.END)
    http_entry.insert(0, "5700")
    http_ok=ttk.Label(select_http_frame1,font=("Verdana",7))
    http_ok.grid(row=0,column=2,pady=(10,0))
    update_http_ok()

    http_post_label=ttk.Label(select_http_frame1,text="请输入反向HTTP POST地址的端口号(0-65535):")
    http_post_label.grid(row=1,column=0,padx=5,pady=(10,0),sticky="w")
    http_post_var = tk.StringVar()
    http_post_entry = ttk.Spinbox(select_http_frame1, from_=0, to=65535, textvariable=http_post_var,validate="key", validatecommand=(select_http_frame1.register(on_validate), "%P"),style="TSpinbox")
    http_post_entry.grid(row=1, column=1, padx=5,pady=(10,0))
    http_post_entry.delete(0,tk.END)
    http_post_entry.insert(0, "5701")
    http_post_ok=ttk.Label(select_http_frame1,font=("Verdana",7))
    http_post_ok.grid(row=1,column=2,pady=(10,0))
    update_http_post_ok()

    http_show_label=ttk.Label(select_http_frame1,text="提醒:当前HTTP监控端口号为5700,HTTP POST地址的端口号为5701。",font=("Verdana",10, "italic"),foreground="#808000")#橄榄绿
    http_show_label.grid(row=2,column=0,columnspan=4,pady=(10,0),sticky="w")
    update_http_show()
    
    http_button=ttk.Button(select_http_frame1,text="确定并设置端口",style="Custom2.TButton",command=change_http_settings)
    http_button.grid(row=3,column=3,pady=10)

    appearance_frame=ttk.LabelFrame(Morefuction_frame,text="关于本程序外观的设置")
    appearance_frame.grid(row=6,column=0,padx=(5,0),pady=(0,10))
    appearance_label=ttk.Label(appearance_frame,text="--请选择您喜欢的外观(部分主题由于某些原因在部分主机上显示问题导致不适配，请谅解):")
    appearance_label.grid(row=0,column=0,padx=(5,100),pady=10,sticky="w")
    style1 = ThemedStyle(windowgui)
    available_themes = style1.theme_names()
    theme_combobox = ttk.Combobox(appearance_frame, values=available_themes)
    theme_combobox.set("arc")  # 设置默认主题
    theme_combobox.bind("<<ComboboxSelected>>", change_theme)
    theme_combobox.grid(row=1,column=0,padx=(5,0),pady=(0,10),sticky="w")
    
    # 配置 Canvas 的滚动区域
    Morefuction_frame.bind("<Configure>", lambda event: Morefuction_canvas.configure(scrollregion=Morefuction_canvas.bbox("all")))
    Morefuction.grid()
    
    Settings=tk.Frame(notebook)#对设置界面进行部署
    
    # 创建一个 Canvas 包裹设置界面内容    
    Settings_canvas=tk.Canvas(Settings)
    Settings_canvas.pack(side="left",fill="both",expand=True)

    # 创建一个垂直滚动条并绑定到 Canvas
    Settings_scrollbar = tk.Scrollbar(Settings, orient="vertical", command=Settings_canvas.yview)
    Settings_scrollbar.pack(side="right", fill="y")
    Settings_canvas.configure(yscrollcommand=Settings_scrollbar.set)
    
    # 创建一个 Frame，用于放置设置界面内容
    Settings_frame = tk.Frame(Settings_canvas)
    Settings_canvas.create_window((0, 0), window=Settings_frame, anchor="nw")
    
    pattern_Frame=ttk.LabelFrame(Settings_frame,text="关于检测/发送数量设置功能的启动模式")
    pattern_Frame.grid(row=0,column=0,pady=10)
    pattern_label=ttk.Label(pattern_Frame,text="--请选择启动模式(默认模式为pattern2):")
    pattern_label.grid(row=0,column=0,padx=5,pady=(10,0))
    global pattern_select
    pattern_select= tk.StringVar(value="Pattern2")
    pattern1=ttk.Radiobutton(pattern_Frame,text="Pattern1:当检测/发送次数达到\n目标值后自动关闭程序",value="Pattern1",variable=pattern_select,command=change_settings)
    pattern1.grid(row=1,column=0,padx=(10,20),pady=(0,10))
    pattern2=ttk.Radiobutton(pattern_Frame,text="Pattern2:当检测/发送次数达到\n目标值后只是停止监控",value="Pattern2",variable=pattern_select,command=change_settings)
    pattern2.grid(row=1,column=1,padx=(20,170),pady=(0,10))
    
    solve_conflict_frame1=ttk.LabelFrame(Settings_frame,text="关于同时启用定时功能和限定次数功能时的效果冲突解决1")
    solve_conflict_frame1.grid(row=1,column=0,padx=5,pady=(0,10))
    select_solution_label=ttk.Label(solve_conflict_frame1,text="--请选择上述两种功能同时使用时，出现矛盾时的解决方式(默认为Solution1):")
    select_solution_label.grid(row=0,column=0,padx=5,pady=(10,10),sticky="w")
    global solution_select
    solution_select=tk.StringVar(value="Solution1")
    solution1=ttk.Radiobutton(solve_conflict_frame1,text="Solution1:当两种功能同时使用时，如果在定时时间已经到了，但是限定次数中的功能还没有\n达到，直接执行定时功能，对程序进行关闭。",value="Solution1",variable=solution_select,command=change_settings)
    solution1.grid(row=1,column=0,padx=(5,75),pady=(0,10))
    solution2=ttk.Radiobutton(solve_conflict_frame1,text="Solution2:当两种功能同时使用时，如果在定时时间已经到了，但是限定次数中的功能还没有\n达到，执行完限定次数后(无论Pattern1还是Pattern2),再对程序进行关闭。",value="Solution2",variable=solution_select,command=change_settings)
    solution2.grid(row=2,column=0,padx=(5,75),pady=(0,10))
    solution3=ttk.Radiobutton(solve_conflict_frame1,text="Solution3:当两种功能同时使用时，如果在定时时间已经到了，但是限定次数中的功能还没有\n达到，执行完限定次数后(无论Pattern1还是Pattern2),只是停止监控，并不对程序进行关闭。",value="Solution3",variable=solution_select,command=change_settings)
    solution3.grid(row=3,column=0,padx=(5,75),pady=(0,10))
    solution4=ttk.Radiobutton(solve_conflict_frame1,text="Solution4:当两种功能同时使用时，如果在定时时间已经到了，但是限定次数中的功能还没有\n达到，执行完限定次数后,如果是Pattern1，直接对程序进行关闭，如果是Pattern2,只是停止\n监控，并不对程序进行关闭。",value="Solution4",variable=solution_select,command=change_settings)
    solution4.grid(row=4,column=0,padx=(5,75),pady=(0,10))
    
    solve_conflict_frame2=ttk.LabelFrame(Settings_frame,text="关于同时启用定时功能和限定次数功能时的效果冲突解决2")
    solve_conflict_frame2.grid(row=2,column=0,padx=5,pady=(0,10))
    select_plan_label=ttk.Label(solve_conflict_frame2,text="--请选择上述两种功能同时使用时，出现矛盾时的解决方式(默认为Plan2):")
    select_plan_label.grid(row=0,column=0,padx=5,pady=(10,10),sticky="w")
    global plan_select
    plan_select=tk.StringVar(value="Plan2")
    plan1=ttk.Radiobutton(solve_conflict_frame2,text="Plan1:当两种功能同时使用时，如果在定时时间到达前，限定次数中的功能已经达到(无论\nPattern1还是Pattern2)，直接对程序进行关闭。",value="Plan1",variable=plan_select,command=change_settings)
    plan1.grid(row=1,column=0,padx=(5,95),pady=(0,10))
    plan2=ttk.Radiobutton(solve_conflict_frame2,text="Plan2:当两种功能同时使用时，如果在定时时间到达前，限定次数中的功能已经达到,则如\n果为Pattern1，则直接对程序进行关闭，如果为Pattern2,则只是终止监控，等到定时时间\n到了，对程序进行关闭",value="Plan2",variable=plan_select,command=change_settings)
    plan2.grid(row=2,column=0,padx=(5,95),pady=(0,10))
    plan3=ttk.Radiobutton(solve_conflict_frame2,text="Plan3:当两种功能同时使用时，如果在定时时间到达前，限定次数中的功能已经达到(无论\nPattern1还是Pattern2)，只是终止监控，不关闭程序，并取消定时。",value="Plan3",variable=plan_select,command=change_settings)
    plan3.grid(row=3,column=0,padx=(5,95),pady=(0,10))
    plan4=ttk.Radiobutton(solve_conflict_frame2,text="Plan4:当两种功能同时使用时，如果在定时时间到达前，限定次数中的功能已经达到(无论\nPattern1还是Pattern2)，只是终止监控，不关闭程序，保留定时功能。",value="Plan4",variable=plan_select,command=change_settings)
    plan4.grid(row=4,column=0,padx=(5,95),pady=(0,10))

    remake_count_frame=ttk.LabelFrame(Settings_frame,text="关于重新开始监控后，原有已发送的次数会不会被清空的问题")
    remake_count_frame.grid(row=4,column=0,padx=5,pady=(0.10))
    remake_count_label=ttk.Label(remake_count_frame,text="请选择重新开始监控后，原有已经发送的次数是否重新开始计数(默认为是)")
    remake_count_label.grid(row=0,column=0,padx=5)
    global remake_select
    remake_select=tk.StringVar(value="Yes")
    Yes=ttk.Radiobutton(remake_count_frame,text="是",value="Yes",variable=remake_select,command=change_settings)
    Yes.grid(row=1,column=0,pady=(0,10),sticky="w")
    No=ttk.Radiobutton(remake_count_frame,text="否",value="No",variable=remake_select,command=change_settings)
    No.grid(row=1,column=1,padx=(0,160),pady=(0,10))

    motion_frame=ttk.LabelFrame(Settings_frame,text="关于筛选消息的模式选择")
    motion_frame.grid(row=5,column=0,padx=5,pady=(0,10))
    select_motion_label=ttk.Label(motion_frame,text="--请选择筛选消息的模式(默认为宽松模式):")
    select_motion_label.grid(row=0,column=0,padx=5,pady=(10,10),sticky="w")
    global motion_select
    motion_select=tk.StringVar(value="Easy")
    motion1=ttk.Radiobutton(motion_frame,text="宽松模式：此模式下，您是否输入两种关键词中的任意一栏，均不影响程序进行，若您不输\n入只会导致只监控，但不发送对应信息。若您输入，则执行要求和适中模式相同。",value="Easy",variable=motion_select,command=change_settings)
    motion1.grid(row=1,column=0,padx=(5,95),pady=(0,10))
    motion2=ttk.Radiobutton(motion_frame,text="适中模式：此模式下，您必须至少输入两种关键词中的任意一栏，程序才会启动，此时程序\n会按照要求启动，并对消息中的关键词进行检索，若符合条件(消息中含有必须出现的所有关\n键词，但可不需要含可能出现的关键词)，才会发送消息。",value="Mezzo",variable=motion_select,command=change_settings)
    motion2.grid(row=2,column=0,padx=(5,95),pady=(0,10))
    motion3=ttk.Radiobutton(motion_frame,text="严格模式：此模式下，您必须输入两种关键词后，程序才会正常启动，并对消息进行准确监\n控(只有消息中含有必须出现的所有关键词且至少含有一个可能出现的关键词时，才发送消息\n)。",value="Strict",variable=motion_select,command=change_settings)
    motion3.grid(row=3,column=0,padx=(5,95),pady=(0,10))
    update_or_label()
    update_and_label()

    # 配置 Canvas 的滚动区域
    Settings_frame.bind("<Configure>", lambda event: Settings_canvas.configure(scrollregion=Settings_canvas.bbox("all")))
    Settings.grid()
    
    notebook.add(Gui, text="程序主界面")
    notebook.add(Morefuction, text="更多功能")
    notebook.add(Settings,text="设置")
    notebook.add(help_frame, text="帮助")

    notebook.pack(expand=1, fill="both")
    windowgui.protocol("WM_DELETE_WINDOW",lambda: ask_exit_program(windowgui))
    windowgui.mainloop()

def exit_program(windowgui):
    global flask_thread,gui_thread,flask_server,stop_flask_loop,stop_monitor_update,pattern_start,update_or_symbol,group_change,http_default,HTTP_set,HTTP_POST_set
    # 退出GUI事件循环
    stop_monitor_update = True
    time_update = True
    pattern_start= True
    update_or_symbol=False
    group_change=True
    # 清空消息队列
    message_queue.queue.clear()
    group_data_queue.queue.clear()
    private_data_queue.queue.clear()
    message_ui_queue.queue.clear()
    message_filter.clear()
    print("Queue has been released.")
    if flask_server :
    # 设置循环标志为 True，停止 Flask 循环
    # 发送请求启动exit_flask函数，然后达到解决问题的目的
        """
    问题为：flask_server.handle_request() 在循环内被调用，这个函数是一个阻塞的函数，
    它会一直等待直到有一个请求到达才会返回。由于这个函数的阻塞特性，导致设置的 stop_flask_loop = True
    无法在循环内立即生效，因为它会等待当前请求处理完才会退出循环。
    要解决这个问题，您可以采用一个简单的方法来中断阻塞的 handle_request()。一个常用的方式是在退出时，
    通过发送一个请求到自己的 Flask 服务器来触发一个处理，从而中断 handle_request() 的阻塞。
        """
        if stop_flask_loop == False:
            stop_flask_loop = True
            if http_default:
                requests.get('http://127.0.0.1:5701/exit')
            else:
                url='http://127.0.0.1:'+f'{HTTP_POST_set}/exit'
                url=url.replace(" ","")
                requests.get(url)
    # 停止 Flask 服务器
        print("Flask服务器正在关闭")
        flask_server.server_close()  # 关闭Flask服务器
        print("Flask服务器已关闭")
    if flask_thread:
        print("Flask线程正在终止")
        flask_thread.join()  # 等待Flask线程完成
        print("Flask线程已终止")
    if gui_thread and gui_thread.is_alive():
        print("GUI线程正在终止")
        windowgui.destroy()  # 销毁主窗口  
        print("GUI线程已终止")
    sys.exit(0)  # 退出程序

def ask_exit_program(windowgui):
    global flask_thread,gui_thread,flask_server,stop_flask_loop,stop_monitor_update,pattern_start,update_or_symbol,group_change,http_default,HTTP_set,HTTP_POST_set
    # 退出GUI事件循环
    result=messagebox.askyesno("Confirmation","是否安全退出程序？")
    if result:
        stop_monitor_update = True
        time_update = True
        pattern_start= True
        update_or_symbol=False
        group_change=True
        # 清空消息队列
        message_queue.queue.clear()
        group_data_queue.queue.clear()
        private_data_queue.queue.clear()
        message_ui_queue.queue.clear()
        message_filter.clear()
        print("Queue has been released.")
        if flask_server :
        # 设置循环标志为 True，停止 Flask 循环
        # 发送请求启动exit_flask函数，然后达到解决问题的目的
            """
        问题为：flask_server.handle_request() 在循环内被调用，这个函数是一个阻塞的函数，
        它会一直等待直到有一个请求到达才会返回。由于这个函数的阻塞特性，导致设置的 stop_flask_loop = True
        无法在循环内立即生效，因为它会等待当前请求处理完才会退出循环。
        要解决这个问题，您可以采用一个简单的方法来中断阻塞的 handle_request()。一个常用的方式是在退出时，
        通过发送一个请求到自己的 Flask 服务器来触发一个处理，从而中断 handle_request() 的阻塞。
            """
            if stop_flask_loop == False:
                stop_flask_loop = True 
                if http_default:
                    requests.get('http://127.0.0.1:5701/exit')
                else:
                    url='http://127.0.0.1:'+f'{HTTP_POST_set}/exit'
                    url=url.replace(" ","")
                    requests.get(url)
        # 停止 Flask 服务器
            print("Flask服务器正在关闭")
            flask_server.server_close()  # 关闭Flask服务器
            print("Flask服务器已关闭")
        if flask_thread:
            print("Flask线程正在终止")
            flask_thread.join()  # 等待Flask线程完成
            print("Flask线程已终止")
        if gui_thread and gui_thread.is_alive():
            print("GUI线程正在终止")
            windowgui.destroy()  # 销毁主窗口  
            print("GUI线程已终止")
        sys.exit(0)  # 退出程序
    
@app.route('/exit', methods=["GET"])
def exit_flask():
    global stop_flask_loop 
    stop_flask_loop = True# 设置循环标志为 True，停止 Flask 循环
    return "Flask loop will stop"

def run_flask_thread():
    global stop_flask_loop,flask_server,http_default,HTTP_set,HTTP_POST_set
    stop_flask_loop=False
    if http_default:
        flask_server = make_server('0.0.0.0', 5701, app)
    else :
        HTTP_POST=int(HTTP_POST_set)
        flask_server = make_server('0.0.0.0', HTTP_POST, app)
    # 使用循环来替代 serve_forever()
    while not stop_flask_loop:
        flask_server.handle_request()
       
def start_monitoring():
    global flask_thread,group_Sym,motion_select,select_watcher
    watcher=select_watcher.get()
    #开启flask线程，监听go-cqhttp的监听窗口
    if ("group_id" in message_filter) and (message_filter["group_id"].replace(" ","")!="")and group_Sym and (watcher=="CerGroup" or watcher=="CerPrivate"):
        #保证在输入监听群号后，再进行监听，避免报错
        if message_filter["send_message"] != "":
            key1=message_filter["keyword1"]
            key2=message_filter["keyword2"]
            key3=message_filter["keyword3"]
            nece1=message_filter["necessary1"]
            nece2=message_filter["necessary2"]
            nece3=message_filter["necessary3"]
            if (key1 == '') and (key2 == '') and (key3 == '') and (nece1 == '') and (nece2 == '') and (nece3 == ''):
                if motion_select.get() == "Easy":
                    user_data_dir = "user_data"
                    if not os.path.exists(user_data_dir):
                        os.makedirs(user_data_dir)
                    never_file3 = os.path.join(user_data_dir, "never_seen3.txt")
                    if not os.path.exists(never_file3):
                        messagebox.showinfo("Reminder","您两种关键词均为输入，当前为宽松模式，程序依然会执行。但是由于该操作会导致只监控不发送消息，有违程序使用的初衷。")
                        result=messagebox.askyesno("Confirmation","您是否想下次不显示此类弹窗？")
                        if result:                                        
                            if not os.path.exists(never_file3):
                                with open(never_file3, "w") as file:
                                    file.write("Never Seen")
                    flask_thread=Thread(target=run_flask_thread)#开启flask线程
                    flask_thread.start()
                elif motion_select.get() == "Mezzo":
                    messagebox.showwarning("Warning","您两种关键词均未输入，当前为适中模式，请至少输入一种，否则程序将不会按照您的想法运行。")
                elif motion_select.get() == "Strict":
                    messagebox.showwarning("Warning","您两种关键词均未输入，当前为严格模式，请每种至少输入一个关键词，否则程序将不会按照您的想法运行。")
            elif (nece1 == '') and (nece2 == '') and (nece3 == ''):
                if motion_select.get() != "Strict":
                    user_data_dir = "user_data"
                    if not os.path.exists(user_data_dir):
                        os.makedirs(user_data_dir)
                    never_file2 = os.path.join(user_data_dir, "never_seen2.txt")
                    if not os.path.exists(never_file2):
                        messagebox.showinfo("Friendly Reminder","您未填入必须出现的关键词部分，其实填入一些更好帮您筛选最符合的消息。但是不填入不影响程序进行。")
                        result=messagebox.askyesno("Confirmation","您是否想下次不显示此类弹窗？")
                        if result:
                            if not os.path.exists(never_file2):
                                with open(never_file2, "w") as file:
                                    file.write("Never Seen")
                    flask_thread=Thread(target=run_flask_thread)#开启flask线程
                    flask_thread.start()
                else:
                    messagebox.showwarning("Warning","您未填入必须出现的关键词部分，当前为严格模式，请至少输入一个关键词，否则程序将不会按照您的想法运行。")
            elif (key1 == '') and (key2 == '') and (key3 == ''):
                if motion_select.get() != "Strict":
                    user_data_dir = "user_data"
                    if not os.path.exists(user_data_dir):
                        os.makedirs(user_data_dir)
                    never_file1 = os.path.join(user_data_dir, "never_seen1.txt")
                    if not os.path.exists(never_file1):
                        messagebox.showinfo("Friendly Reminder","您未填入可能出现的关键词部分，其实填入一些更好帮您筛选最符合的消息。但是不填入不影响程序进行。")
                        result=messagebox.askyesno("Confirmation","您是否想下次不显示此类弹窗？")
                        if result:                    
                            if not os.path.exists(never_file1):
                                with open(never_file1, "w") as file:
                                    file.write("Never Seen")
                    flask_thread=Thread(target=run_flask_thread)#开启flask线程
                    flask_thread.start()
                else:
                    messagebox.showwarning("Warning","您未填入可能出现的关键词部分，当前为严格模式，请至少输入一个关键词，否则程序将不会按照您的想法运行。")                 
            elif (key1 == '') or (key2 == '') or (key3 == '') or (nece1 == '') or (nece2 == '')or (nece3 == ''):
                flask_thread=Thread(target=run_flask_thread)#开启flask线程
                flask_thread.start()
        else :
            messagebox.showinfo("Warning!","您还没有输入发送消息")
    elif (watcher=="CerGroup" or watcher=="CerPrivate") and ((not "group_id" in message_filter) or (not message_filter["group_id"].replace(" ","")!="") or (not group_Sym) ):
        if watcher=="CerGroup":
            messagebox.showwarning("Warning!","您还没有输入监控群号或者输入群号不合法，为避免程序监控出错，请确保您输入正确群号后再开始监控")
        if watcher=="CerPrivate":
            messagebox.showwarning("Warning!","您还没有输入监控好友QQ号或者输入QQ号不合法，为避免程序监控出错，请确保您输入正确的好友QQ号后再开始监控")
    elif watcher=="AllGroup" or watcher=="AllPrivate" or watcher=="All":
        #保证在输入监听群号后，再进行监听，避免报错
        if message_filter["send_message"] != "":
            key1=message_filter["keyword1"]
            key2=message_filter["keyword2"]
            key3=message_filter["keyword3"]
            nece1=message_filter["necessary1"]
            nece2=message_filter["necessary2"]
            nece3=message_filter["necessary3"]
            if (key1 == '') and (key2 == '') and (key3 == '') and (nece1 == '') and (nece2 == '') and (nece3 == ''):
                if motion_select.get() == "Easy":
                    user_data_dir = "user_data"
                    if not os.path.exists(user_data_dir):
                        os.makedirs(user_data_dir)
                    never_file3 = os.path.join(user_data_dir, "never_seen3.txt")
                    if not os.path.exists(never_file3):
                        messagebox.showinfo("Reminder","您两种关键词均为输入，当前为宽松模式，程序依然会执行。但是由于该操作会导致只监控不发送消息，有违程序使用的初衷。")
                        result=messagebox.askyesno("Confirmation","您是否想下次不显示此类弹窗？")
                        if result:                                        
                            if not os.path.exists(never_file3):
                                with open(never_file3, "w") as file:
                                    file.write("Never Seen")
                    flask_thread=Thread(target=run_flask_thread)#开启flask线程
                    flask_thread.start()
                elif motion_select.get() == "Mezzo":
                    messagebox.showwarning("Warning","您两种关键词均未输入，当前为适中模式，请至少输入一种，否则程序将不会按照您的想法运行。")
                elif motion_select.get() == "Strict":
                    messagebox.showwarning("Warning","您两种关键词均未输入，当前为严格模式，请每种至少输入一个关键词，否则程序将不会按照您的想法运行。")
            elif (nece1 == '') and (nece2 == '') and (nece3 == ''):
                if motion_select.get() != "Strict":
                    user_data_dir = "user_data"
                    if not os.path.exists(user_data_dir):
                        os.makedirs(user_data_dir)
                    never_file2 = os.path.join(user_data_dir, "never_seen2.txt")
                    if not os.path.exists(never_file2):
                        messagebox.showinfo("Friendly Reminder","您未填入必须出现的关键词部分，其实填入一些更好帮您筛选最符合的消息。但是不填入不影响程序进行。")
                        result=messagebox.askyesno("Confirmation","您是否想下次不显示此类弹窗？")
                        if result:
                            if not os.path.exists(never_file2):
                                with open(never_file2, "w") as file:
                                    file.write("Never Seen")
                    flask_thread=Thread(target=run_flask_thread)#开启flask线程
                    flask_thread.start()
                else:
                    messagebox.showwarning("Warning","您未填入必须出现的关键词部分，当前为严格模式，请至少输入一个关键词，否则程序将不会按照您的想法运行。")
            elif (key1 == '') and (key2 == '') and (key3 == ''):
                if motion_select.get() != "Strict":
                    user_data_dir = "user_data"
                    if not os.path.exists(user_data_dir):
                        os.makedirs(user_data_dir)
                    never_file1 = os.path.join(user_data_dir, "never_seen1.txt")
                    if not os.path.exists(never_file1):
                        messagebox.showinfo("Friendly Reminder","您未填入可能出现的关键词部分，其实填入一些更好帮您筛选最符合的消息。但是不填入不影响程序进行。")
                        result=messagebox.askyesno("Confirmation","您是否想下次不显示此类弹窗？")
                        if result:                    
                            if not os.path.exists(never_file1):
                                with open(never_file1, "w") as file:
                                    file.write("Never Seen")
                    flask_thread=Thread(target=run_flask_thread)#开启flask线程
                    flask_thread.start()
                else:
                    messagebox.showwarning("Warning","您未填入可能出现的关键词部分，当前为严格模式，请至少输入一个关键词，否则程序将不会按照您的想法运行。")                 
            elif (key1 == '') or (key2 == '') or (key3 == '') or (nece1 == '') or (nece2 == '')or (nece3 == ''):
                flask_thread=Thread(target=run_flask_thread)#开启flask线程
                flask_thread.start()
        else :
            messagebox.showinfo("Warning!","您还没有输入发送消息")

def run_turtle_animation():
    try:
        win = turtle.Screen()
        win.title("Welcome")
        win.bgcolor('white')
        t = turtle.Pen()
        t.speed(0)
        t.pencolor('lightgray')
        for i in range(360):
            t.forward(i)
            t.left(59)
        t.penup()
        t.goto(0, 0)
        t.pencolor('#004466')
        t.write("Welcome to this program!", align='center', font=('Arial', 30, 'bold italic'))
        time.sleep(2)
        win.bye()
    except:
        sys.exit(0)
    
if __name__ == '__main__':
    run_turtle_animation()
    gui_thread = Thread(target=run_gui_thread)#开启gui线程
    gui_thread.start()
    gui_thread.join()  # 等待 GUI 线程结束
