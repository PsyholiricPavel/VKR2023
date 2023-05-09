import os
import datetime
from flask import Flask, flash, request, redirect, url_for, send_from_directory
from werkzeug.utils import secure_filename
from analize import toAnalize, video_analizator,getVideosName
THREADS=10

UPLOAD_FOLDER = "videos/"+str(datetime.date.today())

ALLOWED_EXTENSIONS = {'webm', 'mp4', 'mkv', 'jpg', 'jpeg', 'gif'}
if not os.path.isdir("videos"):
     os.mkdir("videos")

app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
def allowed_file(filename):
    """ Функция проверки расширения файла """
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if not os.path.isdir(UPLOAD_FOLDER):
     os.mkdir(UPLOAD_FOLDER)
    if request.method == 'POST':
        if request.form.get('action1') == 'Обработать все видео':
            videos=getVideosName("")
            toAnalize(videos,THREADS)
        elif  request.form.get('action2') == 'Обработать видео за сегодня':
            videos=getVideosName(str(datetime.date.today()))
            print(UPLOAD_FOLDER)
            toAnalize(videos,THREADS)
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
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return redirect(request.url)
    return '''
    <!doctype html>
    <title>Загрузить новый файл</title>
    <h1>Загрузить новый файл</h1>
    <form method=post enctype=multipart/form-data>
      <input type=file name=file>
      <input type=submit value=Upload>
    </form>
    <form method="post" action="/">
        <input type="submit" value="Обработать все видео" name="action1"/>
        <input type="submit" value="Обработать видео за сегодня" name="action2" />
    </form>
    </html>
    '''

@app.route('/uploads/<name>')
def download_file(name):
    return send_from_directory(app.config["UPLOAD_FOLDER"], name)

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
    #videos=getVideosName("")
    #toAnalize(videos,THREADS)