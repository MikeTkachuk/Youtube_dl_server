import os
import time
import multiprocessing

import cryptography.fernet
import yt_dlp
import flask
from flask import render_template, redirect, url_for, request, jsonify, send_from_directory, send_file

app = flask.Flask(__name__)

save_path = r'downloads/'

ytdl_params = {
    'outtmpl': save_path + '%(title)s_not_ready.%(ext)s',
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
            for i in os.listdir(app.root_path + '/to_delete'):
                os.remove(os.path.join(app.root_path, 'to_delete', i))
        except Exception as e:
            print(e)
        finally:
            pass


@app.before_first_request
def init_downloads_cleaner():
    process = multiprocessing.Process(target=cleaner_func, args=())
    process.start()


@app.before_first_request
def init_secret_key():
    print('||||||||||||||||||||||||||||| setting secret key')
    app.secret_key = cryptography.fernet.Fernet.generate_key()


@app.route('/')
def index():
    return render_template('index.html')


def download_from_info(info, filename, receipt):
    out = ytdl.process_ie_result(info)
    os.renames(os.path.join(app.root_path, filename), os.path.join(app.root_path, receipt))
    return out


@app.route('/get_receipt')
def get_receipt():
    url = request.args.get('url')
    info = ytdl.extract_info(url, download=False)
    filename = ''.join(ytdl.prepare_filename(info).split('.')[:-1]) + '.mp3'
    receipt = filename.replace('_not_ready', '')
    downloader_process = multiprocessing.Process(target=download_from_info, args=(info, filename, receipt))
    downloader_process.start()
    return receipt


@app.route('/get_url')
def get_url():
    receipt = request.args.get('receipt')
    if os.path.exists(os.path.join(app.root_path, receipt)):
        return get_encoded_filepath(receipt)
    else:
        return '0'


def get_encoded_filepath(filename):
    print(f'Encoding:\nkey:{app.secret_key}')
    encoder = cryptography.fernet.Fernet(app.secret_key)
    encoded = encoder.encrypt(filename.encode('utf-8'))
    print(f'encoded:{encoded}')
    return encoded


def get_filepath(url):
    print(f'Decoding:\nkey:{app.secret_key}')
    decoded = cryptography.fernet.Fernet(app.secret_key).decrypt(url.encode('utf-8')).decode('utf-8')
    print(f'decoded:{decoded}')
    return decoded


@app.route('/get_data/<url>')
def get_data(url):
    filename = get_filepath(url)
    (head, file) = os.path.split(filename)
    (head, _) = os.path.split(head)
    new_filename = os.path.join(head, 'to_delete', file)
    try:
        os.renames(os.path.join(app.root_path, filename), os.path.join(app.root_path, new_filename))
    except FileExistsError:
        os.remove(os.path.join(app.root_path, filename))
    out = send_file(new_filename, as_attachment=True)
    return out


if __name__ == '__main__':
    app.run()
