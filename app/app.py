import os
import datetime
from flask import Flask, flash, request, redirect, url_for, send_from_directory,render_template,send_file
from werkzeug.utils import secure_filename
from apscheduler.schedulers.background import BackgroundScheduler
from analize import *
from Db_manager import *
app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'
app.config['UploadFolder'] = "app/videos/"+str(datetime.date.today())
app.config['TimeoutDeletePNG']= 60
app.config['AllowedExpressions']= {'webm', 'mp4', 'mkv'}
app.config['Threads']=8
#print(app.config)
user = {}
choisen=[]

if not os.path.isdir("app/videos"):
     os.mkdir("app/videos")
if not os.path.isdir("app/img"):
     os.mkdir("app/img")


scheduler = BackgroundScheduler()
scheduler.add_job(DeleteIMG, 'interval', seconds=app.config['TimeoutDeletePNG'])
def allowed_file(filename):
    """ Функция проверки расширения файла """
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['AllowedExpressions']
@app.route('/upload', methods=['POST'])
def upload():
    if request.method == 'POST':
        files = request.files.getlist("file")
        for file in files:
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UploadFolder'], filename))
            flash("Files Uploaded Successfully.!")
            uploadingVideoInfo={'Name':filename,'Path':app.config['UploadFolder'],'Duration':(getVideosDuration([os.path.join(app.config['UploadFolder'], filename)]))[0][0]}
            NewVideo(uploadingVideoInfo,user)
        return redirect('/')

@app.route('/', methods=['GET'])
def home():
    return redirect('authorization')

@app.route('/authorization', methods=['POST', 'GET'])
def authorization():
    global user
    if(user == {}):
        valid_reg= True
        valid_login = True
        if request.method == "POST":
            f_users = {}
            f_repos = {}
            if (request.form.get('users-alert')== 'True'):
                f_users = request.files['upload-user']
                if allowed_file(f_users.filename):
                    ImportFromJSON(f_users, 'u')
            if (request.form.get('repo-alert')== 'True'):
                f_repos = request.files['upload-repos']
                if allowed_file(f_repos.filename):
                    ImportFromJSON(f_repos, 'r')
            Download = request.form.get('download')
            if Download == 'True':
                return redirect('download')    

            RegUsername = request.form.get('RegUsername')
            RegPassword = request.form.get('RegPassword')
            RegUser = {'UserName': RegUsername,
                        'Password': RegPassword}
            if((RegUsername == '') or
                (RegPassword == '')):
                valid_reg = False
            else:
                if ((RegUsername != None) or
                    (RegPassword != None)):
                    if (isRegistredAlready(RegUser['UserName'])):
                        valid_reg = False
                    else:
                        NewUser(RegUser)
            LoginUsername = request.form.get('LoginUsername')
            LoginPassword = request.form.get('LoginPassword')
            LoginUser = {'login': LoginUsername,
                            'Password': LoginPassword}
            if ((LoginUsername == '') or (LoginPassword == '')):
                valid_login = False
            else:
                if ((LoginUsername != None) or (LoginPassword != None)):
                    tmp_user, message = Authorization(LoginUser)
                    if (message != "OK"):
                        valid_login = False
                    else:
                        user = tmp_user
                        return redirect('menu')

        return render_template('authorization.html', valid_reg=valid_reg, valid_login=valid_login)
    else:
        return redirect('menu')



@app.route('/menu', methods=['GET', 'POST'])
def upload_file():
    global user
    global choisen
    if user == {}:
        return redirect('authorization')
    else:
        if not os.path.isdir(app.config['UploadFolder']):
            os.mkdir(app.config['UploadFolder'])
        if request.method == 'POST':
            LogOut = request.form.get('LogOut')
            if LogOut != None:
                if LogOut == "1":
                    user = {}
                    return redirect('authorization')
            if request.form.get('action1') == 'Обработать все видео':
                toAnalize(GetVideosForChoice(user['UserName']),app.config['Threads'])
            elif  request.form.get('action2') == 'Обработать видео за сегодня(не работает)':
                print(app.config['UploadFolder'])
            elif  request.form.get('action3') == 'Обработать выбранные видео':
                return redirect('choice')
            elif  request.form.get('action4') == 'Построить график проходимости':
               return redirect('grafchoice')
            elif  request.form.get('action5') == 'Выбор Видео для удаления':
               return redirect('choiceDel')
            else:
                print('Nothing pressed')
            if 'file' not in request.files:
                flash('Не могу прочитать файл')
                return redirect(request.url)
            file = request.files['file']
            if file.filename == '':
                flash('Нет выбранного файла')
                return redirect(request.url)
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UploadFolder'], filename))
                return redirect(request.url)
        return render_template("index.html")

@app.route('/choice', methods=['POST', 'GET'])
def choiceProcessing():
    global user
    if user == {}:
        return redirect('authorization')
    else:
        if request.method == "POST":
            LogOut = request.form.get('LogOut')
            if LogOut != None:
                if LogOut == "1":
                    user = {}
                    return redirect('authorization')
            if request.form.get('action0') == 'Обработать':
                global choisen
                choisen=getVideosFromDB(request.form.getlist('videocheckbox'))
                toAnalize(choisen,app.config['Threads'])
                return redirect('menu')
            if request.form.get('action1') == 'Выделить необработанные':
                return render_template("videosChoice.html",videos=sorted(GetVideosForChoice(user['UserName']),key=lambda x: x['Name']))
            if request.form.get('action2') == 'Назад':
                return redirect('menu')
        return render_template("videosChoice.html",videos=sorted(GetVideosForChoice(user['UserName']),key=lambda x: x['Name']))

@app.route('/choiceDel', methods=['POST', 'GET'])
def choiceDelProcessing():
    global user
    if user == {}:
        return redirect('authorization')
    else:
        if request.method == "POST":
            LogOut = request.form.get('LogOut')
            if LogOut != None:
                if LogOut == "1":
                    user = {}
                    return redirect('authorization')
            if request.form.get('action0') == 'Удалить':
                global choisen
                toDel=getVideosFromDB(request.form.getlist('videocheckbox'))
                for i in toDel:
                    DeleteVideo(i['_id'], user) 
                return redirect('menu')
            if request.form.get('action1') == 'Выделить обработанные':
                return render_template("videosDelChoice.html",videos=sorted(GetVideosForChoice(user['UserName']),key=lambda x: x['Name']))
            if request.form.get('action2') == 'Назад':
                return redirect('menu')
        return render_template("videosDelChoice.html",videos=sorted(GetVideosForChoice(user['UserName']),key=lambda x: x['Name']))
@app.route('/grafchoice', methods=['POST', 'GET'])
def choiceGraf():
    global user
    if user == {}:
        return redirect('authorization')
    else:
        if request.method == "POST":
            LogOut = request.form.get('LogOut')
            if LogOut != None:
                if LogOut == "1":
                    user = {}
                    return redirect('authorization')
            if request.form.get('action0') == 'Обработать':
                global choisen
                choisen=request.form.getlist('videocheckbox')
                filename=printerGraf(choisen)
                return redirect(url_for("download_file", name=filename))
            if request.form.get('action1') == 'Выделить необработанные':
                return render_template("videosGrafChoice.html",videos=sorted(GetVideosForChoice(user['UserName']),key=lambda x: x['Name']))
            if request.form.get('action2') == 'Назад':
                print('wtf')
                return redirect('menu')
        return render_template("videosGrafChoice.html",videos=sorted(GetVideosForChoice(user['UserName']),key=lambda x: x['Name']))


@app.route('/download/<name>')
def download_file(name):
    return send_file('./img/'+name,as_attachment=True)

if __name__ == '__main__':
    scheduler.start()
    app.run(host='0.0.0.0', debug=True)