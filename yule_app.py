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