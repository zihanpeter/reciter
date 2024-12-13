from flask import Flask, render_template, request, session, redirect, Blueprint
import pymongo
import time

from user_app import user_app
from recite_app import recite_app
from forum_app import forum_app
from yule_app import yule_app

app = Flask(__name__)
app.secret_key = 'aiueb823hfkah38whwkdnfea874hiwn'
app.register_blueprint(user_app)
app.register_blueprint(recite_app)
app.register_blueprint(forum_app)
app.register_blueprint(yule_app)

client = pymongo.MongoClient()
db = client.reciter

from collections import defaultdict
from flask import abort

# 设置频率限制参数
LIMIT = 7  # 允许的最大请求次数
PERIOD = 10  # 时间窗口（秒）

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

@app.before_request
def limit_requests():
    ip = request.remote_addr
    if is_rate_limited(ip):
        abort(429)  # 返回429 Too Many Requests

def get_theme():
    theme = session.get('theme')
    if theme == None:
        theme = 'white'
    return theme


@app.route('/')
def main():
    username = session.get('username')
    s = 0
    e = 5
    lists = list(db.lists.find())
    top = list(db.articles.find({'top': True}))
    rec = list(db.articles.find({'top': False}))
    lists.sort(key=lambda x: x['timef'], reverse=True)
    rec.sort(key=lambda x: x['timef'], reverse=True)
    top.sort(key=lambda x: x['timef'], reverse=True)
    lists = lists[s: e]
    rec = rec[s: e]
    return render_template('main/main.html',
                           t_lists=lists,
                           t_username=username,
                           t_rec=rec,
                           t_top=top,
                           t_theme=get_theme())


if __name__ == '__main__':
    app.run(debug=True, port=5050)