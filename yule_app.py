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
    path 游戏html文件路径
    comments[] 游戏评论
    intro 游戏介绍
    
'''


@yule_app.route('/yule')
def yule():

    return render_template('yule/yule.html')

@yule_app.route('/games')
def games():
    return redirect('/')