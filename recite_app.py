from flask import Flask, render_template, request, session, redirect, Blueprint
import pymongo
import uuid
import random
import time


recite_app = Blueprint('recite_app', __name__)
recite_app.secret_key = 'qwertyuiopasdfghjklzxcvbnm1234567890'
client = pymongo.MongoClient()
db = client.reciter

'''
    集合名 lists
    
    id 表格id
    username 用户名
    listname 表格名
    difficulty 难度
    en 英文信息
    zh 中文信息
    timef 创建时间
    o 是否为官方
    sm 是否有例句
    sen 例句
'''


def get_theme():
    theme = session.get('theme')
    if theme == None:
        theme = 'white'
    return theme


@recite_app.route('/lists', methods=["GET"]) # 依据条件展示表格列表
def lists():
    username = session.get('username')
    difficulty = request.args.get('difficulty')
    key = request.args.get('key')
    if key == None or key == '':
        if difficulty == 'all' or difficulty == None:
            lists_o = db.lists.find({'o': True})
            lists_o = list(lists_o)
            lists_u = db.lists.find({'o': False})
            lists_u = list(lists_u)
        else:
            lists_o = db.lists.find({'difficulty': difficulty, 'o': True})
            lists_o = list(lists_o)
            lists_u = db.lists.find({'difficulty': difficulty, 'o': False})
            lists_u = list(lists_u)
    else:
        if difficulty == 'all':
            lists_o = db.lists.find({'listname': key, 'o': True})
            lists_o = list(lists_o)
            lists_u = db.lists.find({'listname': key, 'o': False})
            lists_u = list(lists_u)
        else:
            lists_o = db.lists.find({'listname': key, 'difficulty': difficulty, 'o': True})
            lists_o = list(lists_o)
            lists_u = db.lists.find({'listname': key, 'difficulty': difficulty, 'o': False})
            lists_u = list(lists_u)
    lists_o.sort(key=lambda x: x['listname'])
    lists_u.sort(key=lambda x: x['timef'], reverse=True)
    show_mode = request.args.get('show_mode')
    if show_mode == None:
        show_mode = 'official'
    return render_template('recite/lists.html', 
                           t_username=username, 
                           t_lists_o=lists_o, 
                           t_lists_u=lists_u,
                           t_theme=get_theme(),
                           t_show_mode=show_mode)


@recite_app.route('/create') # 提供创建词汇表的页面
def create():
    if session.get('username') == None:
        return redirect('/login')
    userdic = db.users.find_one({'username': session['username']})
    return render_template('recite/create.html',
                           t_username=session.get('username'),
                           t_admin=userdic['admin'],
                           t_theme=get_theme())


@recite_app.route('/check_create', methods=['POST']) # 处理提供的创建信息
def check_create():
    if session.get('username') == None:
        return redirect('/login')
    wordlist = request.form['wordlist']
    listname = request.form['listname']
    difficulty = request.form.get('difficulty')
    sm = request.form.get('sm')
    o = request.form.get('o')
    en = []
    zh = []
    sen = []
    if sm == 'y':
        sm = True
        s = ''
        flag = 1
        for i in wordlist:
            if i == '\n':
                continue
            if i == '\r':
                if flag == 1:
                    en.append(s)
                elif flag == 2:
                    zh.append(s)
                elif flag == 3:
                    sen.append(s)
                s = ''
                flag %= 3
                flag += 1
            else:
                s += i
        sen.append(s)
    else:
        sm = False
        s = ''
        flag = 1
        for i in wordlist:
            if i == '\n':
                continue
            if i == '\r':
                if flag == 1:
                    en.append(s)
                elif flag == 0:
                    zh.append(s)
                s = ''
                flag ^= 1
            else:
                s += i
        zh.append(s)
    if o == 'y':
        o = True
    else:
        o = False
    id = str(uuid.uuid1())
    now = time.localtime()
    now_temp = time.strftime("%Y-%m-%d %H:%M", now)
    db.lists.insert_one({'id': id, 
                        'username': session.get('username'),
                        'listname': listname, 
                        'difficulty': difficulty, 
                        'en': en, 
                        'zh': zh, 
                        'timef': now_temp, 
                        'o': o,
                        'sen': sen,
                        'sm': sm})
    return redirect('/lists')


@recite_app.route('/prepare_recite', methods=['POST']) # 准备开始背诵
def prepare_recite():
    if session.get('username') == None:
        return redirect('/login')
    id = request.form['id']
    res = db.lists.find_one({'id': id})
    dic = {}
    dic['username'] = session.get('username')
    dic['pat'] = request.form['pattern']
    dic['en'] = res['en']
    dic['zh'] = res['zh']
    dic['num'] = len(res['en'])
    dic['show'] = random.randint(0, dic['num'] - 1)
    if res['sm']:
        dic['sm'] = True
    else:
        dic['sm'] = False
    dic['sen'] = res['sen']
    dic['tong'] = {}
    dic['list_id'] = id
    dic['list_username'] = res['username']
    dic['listname'] = res['listname']
    dic['difficulty'] = res['difficulty']
    for i in dic['en']:
        dic['tong'][i] = 2
    dic['fir'] = {}
    for i in dic['en']:
        dic['fir'][i] = True
    db.temp.delete_one({'username': session.get('username')})
    db.temp.insert_one(dic)
    return redirect('/recite')


@recite_app.route('/recite', methods=['GET']) # 背诵
def recite():
    if session.get('username') == None:
        return redirect('/login')
    dic = db.temp.find_one({'username': session.get('username')})
    fir = ""
    if dic['fir'][dic['en'][dic['show']]]:
        fir = "first time"
    if dic['pat'] == 'Learn meaning':
        return render_template('recite/recite_meaning.html',
                               t_username=session.get('username'),
                               t_en=dic['en'][dic['show']], 
                               t_num=dic['num'], 
                               t_rem=dic['tong'][dic['en'][dic['show']]], 
                               t_fir=fir,
                               t_pat=dic['pat'],
                               t_sm=dic['sm'],
                               t_sen=dic['sen'],
                               t_theme=get_theme(),
                               t_listname=dic['listname'])
    else:
        return render_template('recite/recite_spelling.html',
                               t_username=session.get('username'),
                               t_zh=dic['zh'][dic['show']], 
                               t_num=dic['num'], 
                               t_rem=dic['tong'][dic['en'][dic['show']]], 
                               t_fir=fir,
                               t_pat=dic['pat'],
                               t_sm=dic['sm'],
                               t_sen=dic['sen'],
                               t_theme=get_theme(),
                               t_listname=dic['listname'])


@recite_app.route('/check_recite', methods=['GET']) # 检查背诵信息
def check_recite():
    if session.get('username') == None:
        return redirect('/login')
    dic = db.temp.find_one({'username': session.get('username')})
    flag = False
    if dic['pat'] == 'Learn meaning':
        res = request.args['know']
        if res == 'Know':
            if dic['fir'][dic['en'][dic['show']]]:
                dic['tong'][dic['en'][dic['show']]] = 0
            else:
                dic['tong'][dic['en'][dic['show']]] -= 1
        else:
            dic['tong'][dic['en'][dic['show']]] = 2
    else:
        res = request.args['ans']
        if res == dic['en'][dic['show']]:
            if dic['fir'][dic['en'][dic['show']]]:
                dic['tong'][dic['en'][dic['show']]] = 0
            else:
                dic['tong'][dic['en'][dic['show']]] -= 1
        else:
            dic['tong'][dic['en'][dic['show']]] = 2
            flag = True
    dic['fir'][dic['en'][dic['show']]] = False
    ent = dic['en'][dic['show']]
    zht = dic['zh'][dic['show']]
    if dic['sm']:
        sen = dic['sen'][dic['show']]
    else:
        sen = ''
    if dic['tong'][dic['en'][dic['show']]] <= 0:
        dic['num'] -= 1
        del dic['en'][dic['show']]
        del dic['zh'][dic['show']]
        if dic['sm']:
            del dic['sen'][dic['show']]
    if dic['num'] == 0:
        now = time.localtime()
        now_temp = time.strftime("%Y-%m-%d %H:%M", now)
        userdic = db.users.find_one({'username': session['username']})
        flag = True
        for i in userdic['list_record']:
            if i['id'] == dic['list_id']:
                i['timef'] = now_temp
                flag = False
                break
        if flag:
            userdic['list_record'].append({'username': dic['list_username'], 
                                        'id': dic['list_id'], 
                                        'listname': dic['listname'], 
                                        'difficulty': dic['difficulty'], 
                                        'timef': now_temp})
        db.users.update({'username': session['username']}, userdic)
        return render_template('recite/finish.html',
                               t_username=session['username'],
                               t_theme=get_theme(),
                               t_listname=dic['listname'])
    dic['show'] = random.randint(0, dic['num'] - 1)
    db.temp.update({'username': session['username']}, dic)
    if flag:
        fir = ""
        if dic['fir'][dic['en'][dic['show']]]:
            fir = "first time"
        if dic['pat'] == 'Learn spelling':
            return render_template('recite/tip.html',
                                   t_username=session['username'],
                                   t_en=ent,
                                   t_zh=zht,
                                   t_pat=dic['pat'],
                                   t_res=res,
                                   t_num=dic['num'],
                                   t_rem=dic['tong'][dic['en'][dic['show']]],
                                   t_fir=fir,
                                   t_sm=dic['sm'],
                                   t_sen=sen,
                                   t_theme=get_theme(),
                                   t_listname=dic['listname'])
        else:
            return render_template('recite/tip_meaning.html',
                                   t_username=session['username'],
                                   t_en=ent,
                                   t_zh=zht,
                                   t_pat=dic['pat'],
                                   t_res=res,
                                   t_num=dic['num'],
                                   t_rem=dic['tong'][dic['en'][dic['show']]],
                                   t_fir=fir,
                                   t_sm=dic['sm'],
                                   t_sen=sen,
                                   t_theme=get_theme(),
                                   t_listname=dic['listname'])
    return redirect('/recite')


@recite_app.route('/show_tip')
def show_tip():
    if session.get('username') == None:
        return redirect('/login')
    dic = db.temp.find_one({'username': session['username']})
    ent = dic['en'][dic['show']]
    zht = dic['zh'][dic['show']]
    if dic['sm']:
        sen = dic['sen'][dic['show']]
    else:
        sen = ''
    fir = ""
    if dic['fir'][dic['en'][dic['show']]]:
        fir = "first time"
    if dic['pat'] == 'Learn spelling':
        return render_template('recite/tip.html',
                               t_username=session['username'],
                               t_en=ent,
                               t_zh=zht,
                               t_pat=dic['pat'],
                               t_num=dic['num'],
                               t_rem=dic['tong'][dic['en'][dic['show']]],
                               t_fir=fir,
                               t_sm=dic['sm'],
                               t_sen=sen,
                               t_theme=get_theme(),
                               t_listname=dic['listname'])
    else:
        return render_template('recite/tip_meaning.html',
                               t_username=session['username'],
                               t_en=ent,
                               t_zh=zht,
                               t_pat=dic['pat'],
                               t_num=dic['num'],
                               t_rem=dic['tong'][dic['en'][dic['show']]],
                               t_fir=fir,
                               t_sm=dic['sm'],
                               t_sen=sen,
                               t_theme=get_theme(),
                               t_listname=dic['listname'])

# @recite_app.route('/mod_list', methods=['POST'])
# def mod_list():
#     o = request.form.get('o')
#     if o == 'y':
#         o = True
#     else:
#         o = False
#     id = request.form.get('id')
#     wordlist = db.lists.find_one({'id': id})
#     wordlist['o'] = o
#     db.lists.update({'id': id}, wordlist)
#     return redirect('/lists')
#


@recite_app.route('/show_list', methods=['GET']) # 展示表格
def show_list():
    id = request.args.get('id')
    wordlist = db.lists.find_one({'id': id})
    if session.get('username') == None:
        admin = False
    else:
        admin = db.users.find_one({'username': session['username']})['admin']
    return render_template('recite/show_list.html',
                           t_username=session.get('username'),
                           t_wordlist=wordlist, 
                           t_size=len(wordlist['en']),
                           t_sm=wordlist['sm'],
                           t_admin=admin,
                           t_theme=get_theme())


@recite_app.route('/check_del_list', methods=['GET'])
def check_del_list():
    if session.get('username') == None:
        return redirect('/login')
    id = request.args.get('id')
    return render_template('recite/check_del_list.html',
                           t_id=id,
                           t_username=session.get('username'),
                           t_theme=get_theme(),
                           t_listname=db.lists.find_one({'id': id})['listname'])


@recite_app.route('/del_list', methods=['GET']) # 删除表格
def del_list():
    if session.get('username') == None:
        return redirect('/login')
    id = request.args.get('id')
    userdic = db.users.find_one({'username': session['username']})
    dic = db.lists.find_one({'id': id})
    if dic['username'] == session['username'] or userdic['admin']:
        db.lists.delete_one({'id': id})
        dics = list(db.users.find())
        for i in dics:
            for j in range(0, len(i['list_record'])):
                if i['list_record'][j]['id'] == id:
                    del i['list_record'][j]
                    break
            db.users.update({'username': i['username']}, i)
        return redirect('/lists')
    else:
        return '没有权限'


@recite_app.route('/modify_list', methods=['GET'])
def modify_list():
    if session.get('username') == None:
        return redirect('/login')
    id = request.args.get('id')
    dic = db.lists.find_one({'id': id})
    userdic = db.users.find_one({'username': session['username']})
    if dic['username'] == session['username'] or userdic['admin']:
        info = ''
        for i in range(0, len(dic['en'])):
            info += dic['en'][i] + '\n'
            info += dic['zh'][i] + '\n'
            if dic['sm']:
                info += dic['sen'][i] + '\n'
        return render_template('recite/modify_list.html',
                               t_id=id,
                               t_info=info,
                               t_admin=userdic['admin'],
                               t_listname=dic['listname'],
                               t_username=session['username'],
                               t_theme=get_theme())
    else:
        return '没有权限'


@recite_app.route('/modifier', methods=['POST'])
def modifier():
    if session.get('username') == None:
        return redirect('/login')
    wordlist = request.form.get('wordlist')
    listname = request.form.get('listname')
    difficulty = request.form.get('difficulty')
    sm = request.form.get('sm')
    o = request.form.get('o')
    en = []
    zh = []
    sen = []
    if sm == 'y':
        sm = True
        s = ''
        flag = 1
        for i in wordlist:
            if i == '\n':
                continue
            if i == '\r':
                if flag == 1:
                    en.append(s)
                elif flag == 2:
                    zh.append(s)
                elif flag == 3:
                    sen.append(s)
                s = ''
                flag %= 3
                flag += 1
            else:
                s += i
        sen.append(s)
    else:
        sm = False
        s = ''
        flag = 1
        for i in wordlist:
            if i == '\n':
                continue
            if i == '\r':
                if flag == 1:
                    en.append(s)
                elif flag == 0:
                    zh.append(s)
                s = ''
                flag ^= 1
            else:
                s += i
        zh.append(s)
    id = request.form.get('id')
    dic = db.lists.find_one({'id': id})
    if o == 'y':
        o = True
    elif o == 'n':
        o = False
    else:
        o = dic['o']
    dic['listname'] = listname
    dic['difficulty'] = difficulty
    dic['en'] = en
    dic['zh'] = zh
    dic['o'] = o
    dic['sen'] = sen
    dic['sm'] = sm
    db.lists.update({'id': id}, dic)
    return redirect('/lists')