from audioop import reverse
from crypt import methods

from flask import Flask, render_template, request, session, redirect, Blueprint
import pymongo
import uuid
import time
import markdown
import bleach
import re

yule_app = Blueprint('yule_app', __name__)
yule_app.secret_key = 'aiueb823hfkah38whwkdnfea874hiwn'
client = pymongo.MongoClient()
db = client.reciter

'''
    集合名 yule

    id 游戏id
    name 游戏名
    hot 游戏热度
    path 游戏html文件路径
    intro 游戏介绍
    timef 创建时间
    creater 创建者
'''

from collections import defaultdict
from flask import abort

# 设置频率限制参数
LIMIT = 5  # 允许的最大请求次数
PERIOD = 60  # 时间窗口（秒）

# 存储IP地址和对应的访问次数及时间戳
visits = defaultdict(list)

def is_rate_limited(ip):
    current_time = time.time()
    for timestamp in visits[ip]:
        # 移除时间窗口之外的记录
        if current_time - timestamp > PERIOD:
            visits[ip].remove(timestamp)
        else:
            break
    # 如果请求次数超过限制，则返回True
    if len(visits[ip]) >= LIMIT:
        return True
    # 否则，添加当前时间戳并返回False
    visits[ip].append(current_time)
    return False

@yule_app.before_request
def limit_requests():
    ip = request.remote_addr
    if is_rate_limited(ip):
        abort(429)  # 返回429 Too Many Requests

def get_theme():
    theme = session.get('theme')
    if theme == None:
        theme = 'white'
    return theme


@yule_app.route('/yule')
def yule():
    dics = db.yule.find()
    dics = list(dics)
    dics.sort(key=lambda x: x['hot'], reverse=True)
    return render_template('yule/yule.html',
                           t_dics=dics,
                           t_theme=get_theme(),
                           t_username=session.get('username'))

@yule_app.route('/intro', methods=['GET'])
def intro():
    id = request.args.get('id')
    dic = db.yule.find_one({'id': id})
    content = dic['intro']
    content = markdown.markdown(content, extensions=['markdown.extensions.fenced_code',
                                                     'markdown.extensions.codehilite',
                                                     'markdown.extensions.extra',
                                                     'markdown.extensions.toc',
                                                     'markdown.extensions.tables'])
    return render_template('yule/intro.html',
                           t_id=id,
                           t_name=dic['name'],
                           t_intro=content,
                           t_username=session.get('username'),
                           t_theme=get_theme(),
                           t_timef=dic['timef'],
                           t_creator=dic['creator'],
                           t_hot=dic['hot'])

@yule_app.route('/games', methods=['GET'])
def games():
    if session.get('username') == None:
        return redirect('/login')
    id = request.args.get('id')
    r = db.yule.find_one({'id': id})
    r['hot'] += 1
    db.yule.update({'id': id}, r)
    return render_template(r['path'])