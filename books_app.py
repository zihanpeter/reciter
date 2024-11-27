from flask import Flask, render_template, request, session, redirect, Blueprint
import pymongo
import uuid
import time
import markdown
import bleach
import re


books_app = Blueprint('books_app', __name__)
books_app.secret_key = 'qwertyuiopasdfghjklzxcvbnm1234567890'
client = pymongo.MongoClient()
db = client.reciter


'''
    集合名 books

    id 词汇书id
    name 词汇书名
    lists[] 词汇表
    
'''

@books_app.route('/books')
def books():


