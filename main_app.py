from flask import Flask, render_template, request, session, redirect, Blueprint
import pymongo

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