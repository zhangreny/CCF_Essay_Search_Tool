# 库函数
from flask import Flask, redirect, request
from datetime import timedelta
from urllib import parse
from os import listdir
import json
import threading
import hashlib
import datetime
import requests

# flask configuration
port = 8000
app = Flask(__name__, static_url_path="/static/")
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = timedelta(seconds=1)
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(seconds=1)

# userlist stroage
userlistfilepath = 'userlist.txt'
userlist_lock = threading.Lock()

# essaylist storage
essaylistfolderpath_J = '/root/ccf/essaydata_J/'
essaylistfolderpath_C = '/root/ccf/essaydata_C/'


# Website info of conference & journals storage
CCFinfofilepath = '/root/ccf/CCFA_journal&conference_info.json'

@app.route("/")
def get_index():
    return redirect('/login')


@app.route("/login")
def get_login():
    return app.send_static_file("index.html")

     
@app.route("/search")
def get_search():
    return app.send_static_file("main.html")

    
@app.route("/api/register", methods=['POST'], strict_slashes=False)
def post_api_register():
    if request.method == 'POST':
        username_register = request.form['username_register']
        passwd_register = request.form['passwd_register']
        confirmpasswd_register = request.form['confirmpasswd_register']
        nameorvxname_register = request.form['nameorvxname_register']
        # 加锁来保证同一时间，只有一个线程在处理用户列表
        try:
            with userlist_lock:
                if searchuser(username_register, userlist_dict) == False:
                    user_json = {}
                    user_json['username'] = username_register
                    user_json['passwd_md5'] = str(hashlib.md5(passwd_register.encode("utf-8")).hexdigest())
                    user_json['name_or_vxname'] = nameorvxname_register
                    userlist_dict.append(user_json)
                    with open(userlistfilepath, 'a', encoding='utf-8') as userlistfileobj:
                        userlistfileobj.write(str(user_json)+'\n')
                    return json.dumps({'status':'success','resultdata':'注册成功！'})
                else:
                    return json.dumps({'status':'fail','resultdata':'用户名已经存在了哦，换一个吧'})
        except:
            return json.dumps({'status':'fail','resultdata':'用户注册出现bug了'})
# 用于判断用户名是否已存在，已存在返回该用户的字典类型，否则返回False
def searchuser(name, userjson_list):
    for userjson in userjson_list:
        if userjson['username'] == name:
            return userjson
    return False
    

@app.route("/api/login", methods=['POST'], strict_slashes=False)
def post_api_login():
    if request.method == 'POST':
        username_login = request.form['username_login']
        passwd_login = request.form['passwd_login']
        # 加锁来保证同一时间，只有一个线程在处理用户列表
        try:
            with userlist_lock:
                res = searchuser(username_login, userlist_dict)
                if res == False:
                    return json.dumps({'status':'fail','resultdata':'用户名不存在哦'})
                else:
                    if res['passwd_md5'] != str(hashlib.md5(passwd_login.encode("utf-8")).hexdigest()):
                        return json.dumps({'status':'fail','resultdata':'密码输入错误哦'})
                    else:
                        return json.dumps({'status':'success','resultdata':'登录成功'})
        except:
            return json.dumps({'status':'fail','resultdata':'用户登录出现bug了'})
        
        
def hasallkeywords(keywordlist, title):
    wordlist = []
    tmp = ''
    for i in range(len(title)):
        c = title[i]
        if len(tmp) == 0:
            if (ord(c) >= 65 and ord(c) <= 90) or (ord(c) >= 97 and ord(c) <= 122):
                tmp += c
            else:
                continue
        else:
            if (ord(c) >= 65 and ord(c) <= 90) or (ord(c) >= 97 and ord(c) <= 122):
                tmp += c
            else:
                wordlist.append(tmp.lower())
                tmp = ''
        if i == len(title)-1 and len(tmp) > 0:
            wordlist.append(tmp.lower())
    for keyword in keywordlist:
        havethisword = False
        for word in wordlist:
            if keyword.lower() in word:
                havethisword = True
                break
        if havethisword == False:
            return False
    return True
def allnumber(String):
    for c in String:
        if not (ord(c)>=48 and ord(c)<=57):
            return False
    return True
@app.route("/api/search", methods=['POST'], strict_slashes=False)
def post_api_search():
    if request.method == 'POST':
        keywords_search = request.form['keywords_search']
        domain_select = request.form['domain_select']
        startyear_search = request.form['startyear_search']
        endyear_search = request.form['endyear_search']
        method_select = request.form['method_select']
        try:
            if startyear_search != "":
                if not allnumber(startyear_search):
                    return json.dumps({'status':'fail','resultdata':'起始年份输入的不是整数'})
            if endyear_search != "":
                if not allnumber(endyear_search):
                    return json.dumps({'status':'fail','resultdata':'末尾年份输入的不是整数'})
            if startyear_search == "":
                startyear_search = 1900
            else:
                startyear_search = eval(startyear_search)
            if endyear_search == "":    
                endyear_search = 2500
            else:
                endyear_search = eval(endyear_search)
            if method_select == "根据CCF论文库匹配关键字":
                res = []
                keywordsList = keywords_search.split(' ')
                # 未选方向
                if domain_select == "--选择方向--":
                    return json.dumps({'status':'fail','resultdata':'选择一个方向哦'})
                # 指定了一个方向
                else:
                    # 先查期刊
                    for essay in essaylist_dict_J[domain_select]:
                        if eval(essay['year']) >= startyear_search and eval(essay['year']) <= endyear_search:
                            if hasallkeywords(keywordsList, essay['name']):
                                res.append({'JorC': '期刊', 'name': essay['name'], 'year': essay['year']})
                    # 再查会议
                    for essay in essaylist_dict_C[domain_select]:
                        if eval(essay['year']) >= startyear_search and eval(essay['year']) <= endyear_search:
                            if hasallkeywords(keywordsList, essay['name']):
                                res.append({'JorC': '会议', 'name': essay['name'], 'year': essay['year']})
                    # 按照年份从新往老排列
                    res = (sorted(res, key=lambda x:x['year'], reverse=True))
                    return json.dumps({'status':'success','resultdata':res})
            elif method_select == "从DBLP搜索后检查是否属于CCF":
                website = "https://dblp.uni-trier.de/search/publ/api?q="+parse.quote(keywords_search)+"&h=1000&format=json"
                urlres = requests.get(url=website)
                if urlres.status_code != 200:
                    return json.dumps({'status':'fail','resultdata':'连接至DBLP失败，请稍后重试'})
                res = []
                tmpdict = eval(urlres.text)
                for hit in tmpdict['result']['hits']['hit']:
                    if eval(hit['info']['year']) >= startyear_search and eval(hit['info']['year']) <= endyear_search:
                        tmpurl = hit['info']['url'].rstrip('/')+'/'
                        if '/journals/' in tmpurl:
                            try:
                                for website in JournalandConferenceInfoDict[domain_select]:
                                    if tmpurl.split('/journals/')[1].split('/')[0] == website:
                                        res.append({'JorC': '期刊', 'name': hit['info']['title'], 'year': hit['info']['year']})
                                        break
                            except:
                                continue
                        elif '/conf/' in tmpurl:
                            try:
                                for website in JournalandConferenceInfoDict[domain_select]:
                                    if tmpurl.split('/conf/')[1].split('/')[0] == website:
                                        res.append({'JorC': '会议', 'name': hit['info']['title'], 'year': hit['info']['year']})
                                        break
                            except:
                                continue
                        else:
                            continue
                res = (sorted(res, key=lambda x:x['year'], reverse=True))
                return json.dumps({'status':'success','resultdata':res})
        except Exception as e:
            print(e)
            return json.dumps({'status':'fail','resultdata':'搜索功能出现bug了'})


def load_userdata(filepath):
    with open(filepath, 'r', encoding='utf-8') as userlistfileobj:
        lines = userlistfileobj.readlines()
    # 部署在windows下
    # resdict = [eval(line.strip('\n')) for line in lines] 
    # 部署在linux下
    resdict = [eval(line.strip('\n').rstrip('\r')) for line in lines] 
    return resdict
    

def load_essaydata(folderpath):
    resdict = {}
    for filename in listdir(folderpath):
        tmplist = []
        filepath = folderpath + filename
        with open(filepath, 'r', encoding="utf-8") as essaylistfileobj:
            lines = essaylistfileobj.readlines()
            for line in lines:
                tmpdict = {}
                # 部署在windows下
                # splits = line.rstrip('\n').split(":::")
                # 部署在linux下
                splits = line.rstrip('\n').rstrip('\r').split(":::")
                tmpdict['name'] = splits[1]
                tmpdict['year'] = splits[0]
                tmplist.append(tmpdict)
        resdict[filename.rstrip('.txt').replace(',','/')] = tmplist
    return resdict


def load_infodata(infofilepath):
    resdict = {}
    with open(infofilepath, 'r', encoding='utf-8') as infofileobj:
        infoDict = eval(infofileobj.read())
    for key,value in infoDict.items():
        resdict[key] = []
        for c in value:
            if '/journals/' in c['website']:
                resdict[key].append((c['website'].split('/journals/')[-1].rstrip('/')))
            elif '/conf/' in c['website']:
                resdict[key].append((c['website'].split('/conf/')[-1].rstrip('/')))
    return resdict

    
if __name__ == "__main__":
    # 初始化用户数据
    userlist_dict = load_userdata(userlistfilepath)
    print("[init]当前系统用户列表文件读取完毕...")
    print("[init]当前共有", len(userlist_dict), "个注册用户")
    # 初始化论文数据库
    essaylist_dict_J = load_essaydata(essaylistfolderpath_J)
    print("[init]当前系统期刊类论文列表文件读取完毕...")
    for key,value in essaylist_dict_J.items():
        print("[init]当前领域：",key,"共有", len(value), "篇论文")
    essaylist_dict_C = load_essaydata(essaylistfolderpath_C)
    print("[init]当前系统会议类论文列表文件读取完毕...")
    for key,value in essaylist_dict_C.items():
        print("[init]当前领域：",key,"共有", len(value), "篇论文")
    # 初始化各领域论文和会议的网址信息
    JournalandConferenceInfoDict = load_infodata(CCFinfofilepath)
    print("[init]当前系统期刊和会议的网址信息文件读取完毕...")
    for key,value in JournalandConferenceInfoDict.items():
        print("[init]当前领域：",key,"共有", len(value), "个CCF期刊/会议网址信息")
    app.run(host='0.0.0.0',port=port)