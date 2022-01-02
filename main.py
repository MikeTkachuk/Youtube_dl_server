import os
import time
import multiprocessing

import cryptography.fernet
import yt_dlp
import flask
from flask import render_template, redirect, url_for, request, jsonify, send_from_directory, send_file

app = flask.Flask(__name__)

secret_key = cryptography.fernet.Fernet.generate_key()
save_path = r'downloads/'

ytdl_params = {
    'outtmpl': save_path + '%(title)s.%(ext)s',
    'updatetime': False,

    'format': 'bestaudio/best',
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '192',
    }],
}

ytdl = yt_dlp.YoutubeDL(ytdl_params)


def cleaner_func():
    while True:
        time.sleep(1800)
        try:
            for i in os.listdir(app.root_path+'/downloads'):
                os.remove(os.path.join(app.root_path,'downloads', i))
        except Exception as e:
            print(e)
        finally:
            pass


@app.before_first_request
def init_downloads_cleaner():
    process = multiprocessing.Process(target=cleaner_func, args=())
    process.start()


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/get_url')
def get_url():
    url = request.args.get('url')
    info = ytdl.extract_info(url, download=True)
    filename = ''.join(ytdl.prepare_filename(info).split('.')[:-1]) + '.mp3'
    return get_encoded_filepath(filename)


def get_encoded_filepath(filename):
    encoder = cryptography.fernet.Fernet(secret_key)
    return encoder.encrypt(filename.encode('utf-8'))


def get_filepath(url):
    return cryptography.fernet.Fernet(secret_key).decrypt(url.encode('utf-8')).decode('utf-8')


@app.route('/get_data/<url>')
def get_data(url):
    filename = get_filepath(url)
    out = send_file(filename, as_attachment=True)
    return out


if __name__ == '__main__':
    app.run()
