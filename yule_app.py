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
    
'''


@yule_app.route('/yule')
def yule():
    dics = db.yule.find()
    dics = list(dics)
    return render_template('yule/yule.html', t_dics=dics)

@yule_app.route('/game', methods=['GET'])
def game():
    id = request.args.get('id')
    dic = db.yule.find_one({'id': id})

    return render_template('yule/game.html',
                           t_name=dic['name'],
                           t_intro=dic['intro'],
                           t_path=dic['path'])