import threading
import uuid
from http import HTTPStatus
from os import getenv
from pathlib import Path

from flask import Flask, render_template, request, make_response, jsonify, send_from_directory, redirect, url_for
from flask_caching import Cache
from flask_login import LoginManager, login_required, UserMixin, current_user, logout_user, login_user

from .datalog_analyser import FutureEnergyDataLogAnalyser

APP = Flask(__name__)
APP.secret_key = 'super secret string'  # Change this!

cache = Cache(config={'CACHE_TYPE': 'simple', "CACHE_DEFAULT_TIMEOUT": 300})
cache.init_app(APP)
login_manager = LoginManager()
login_manager.init_app(APP)

CVS_DIR = getenv('CVS_DIR')
TASKS = []
USERS = {'admin': {'password': '1'}}


@APP.route('/')
@login_required
@cache.cached(timeout=60)
def home():
    cvs_filenames = get_raw_cvs_filenames()
    if len(cvs_filenames) == 0:
        return make_response('<h1>Error: No csv files found</h1>', HTTPStatus.INTERNAL_SERVER_ERROR)
    default_start_csv = cvs_filenames[0]
    default_end_csv = cvs_filenames[-1]
    return render_template('index.html',
                           cvs_filenames=cvs_filenames,
                           default_start_csv=default_start_csv,
                           default_end_csv=default_end_csv,
                           processed_csv=get_processed_cvs_filenames())


@APP.route('/process_data', methods=['POST'])
@login_required
def process_data():
    data = request.form
    source = get_raw_cvs_filenames()
    source[:] = source[source.index(data['start_csv']): source.index(data['end_csv']) + 1]
    target = Path(CVS_DIR).joinpath('processed_{start}_{end}.csv'.format(
        start=source[0].split('.')[0], end=source[-1].split('.')[0]))
    task_id = None
    if not Path(target).exists():
        def _process_csv():
            analyser = FutureEnergyDataLogAnalyser({
                'cvs_directory': CVS_DIR,
                'cvs_filenames': source,
            })
            analyser.process_data_and_write_to_csv(
                file=target,
            )
            cache.clear()
        task_id = str(uuid.uuid4())
        task = threading.Thread(target=_process_csv, name=task_id)
        TASKS.append(task)
        task.start()
    return make_response(jsonify({'task_id': task_id, 'target': target.name}))


@APP.route('/tasks', defaults={'task_id': None}, methods=['GET'])
@APP.route('/tasks/<task_id>', methods=['GET'])
@login_required
def tasks(task_id):
    def _task_status(task):
        return {'task_id': task.name, 'complete': not task.isAlive()}

    if task_id is None:
        return make_response(jsonify([_task_status(task) for task in TASKS]))
    else:
        return make_response(jsonify([_task_status(task) for task in TASKS if task.name == task_id]))


@APP.route('/download/<path:filename>', methods=['GET', 'POST'])
@login_required
def download(filename):
    if filename in get_processed_cvs_filenames():
        return send_from_directory(directory=Path(CVS_DIR), filename=filename, as_attachment=True)
    return make_response('<h1>Not found</h1>', HTTPStatus.NOT_FOUND)


@APP.route('/remove/<path:filename>', methods=['GET', 'POST'])
@login_required
def remove(filename):
    path = Path(CVS_DIR).joinpath(filename)
    if filename in get_processed_cvs_filenames() and path.exists():
        path.unlink()
        cache.clear()
        return redirect(url_for('home'), code=HTTPStatus.FOUND)
    return make_response('<h1>Not found</h1>', HTTPStatus.NOT_FOUND)


@APP.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')

    email = request.form['email']
    if request.form['password'] == USERS[email]['password']:
        user = User()
        user.id = email
        login_user(user)
    return redirect(url_for('home'))


@APP.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'), code=HTTPStatus.FOUND)


def get_raw_cvs_filenames():
    cvs_paths = sorted(Path(CVS_DIR).glob(FutureEnergyDataLogAnalyser.GLOB_CSV_PATTERN))
    return [path.name for path in cvs_paths]


def get_processed_cvs_filenames():
    cvs_paths = sorted(Path(CVS_DIR).glob('processed_*.csv'))
    return [path.name for path in cvs_paths]


class User(UserMixin):
    pass


@login_manager.user_loader
def user_loader(email):
    if email not in USERS:
        return

    user = User()
    user.id = email
    return user


@login_manager.request_loader
def request_loader(request):
    email = request.form.get('email')
    if email not in USERS:
        return

    user = User()
    user.id = email

    # DO NOT ever store passwords in plaintext and always compare password
    # hashes using constant-time comparison!
    user.is_authenticated = request.form['password'] == USERS[email]['password']

    return user


@login_manager.unauthorized_handler
def unauthorized_handler():
    return redirect(url_for('login'), code=HTTPStatus.FOUND)


if __name__ == '__main__':
    APP.run(debug=True)
