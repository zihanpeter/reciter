from flask import Flask, render_template, request, session, redirect, Blueprint
import pymongo
import uuid
import time
import markdown
import bleach
import re


books_app = Blueprint('books_app', __name__)
books_app.secret_key = 'aiueb823hfkah38whwkdnfea874hiwn'
client = pymongo.MongoClient()
db = client.reciter


'''
    集合名 books

    id 书籍名称
    name 书名
    lists[] 包含词汇表id
    
    
'''

@books_app.route('/books')
def books():
    return redirect('/')

