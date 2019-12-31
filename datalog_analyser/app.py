import logging
import threading
import uuid
from http import HTTPStatus
from os import environ
from pathlib import Path

from flask import Flask, render_template, request, make_response, jsonify, send_from_directory, redirect, url_for
from flask_caching import Cache
from flask_login import LoginManager, login_required, UserMixin, logout_user, login_user

from .datalog_analyser import FutureEnergyDataLogAnalyser

APP = Flask(__name__)

LOG = logging.getLogger('DataLogAnalyserWeb')
LOG.setLevel(logging.DEBUG)

# Environment
CVS_DIR = environ['CVS_DIR']
APP.secret_key = environ.get('APP_SECRET_KEY', default='DEV')
USERS = {'admin': {'password': environ.get('ADMIN_PASSWORD', default='password')}}
LOG.debug(f'Booting with CVS_DIR:{CVS_DIR} secret:{APP.secret_key}')

cache = Cache(config={'CACHE_TYPE': 'simple', "CACHE_DEFAULT_TIMEOUT": 300})
cache.init_app(APP)

login_manager = LoginManager()
login_manager.init_app(APP)


@APP.route('/')
@login_required
def home():
    cvs_filenames = get_raw_cvs_filenames()
    if len(cvs_filenames) == 0:
        return make_response('<h1>Error: No csv files found</h1>', HTTPStatus.INTERNAL_SERVER_ERROR)
    default_start_csv = cvs_filenames[0]
    default_end_csv = cvs_filenames[-1]
    target_cvs = request.args.get('target', default=None, type=str)
    return render_template('index.html',
                           cvs_filenames=cvs_filenames,
                           default_start_csv=default_start_csv,
                           default_end_csv=default_end_csv,
                           processed_csv=get_processed_cvs_filenames(),
                           target_cvs=target_cvs)


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
        def _process_csv(task_id):
            analyser = FutureEnergyDataLogAnalyser({
                'cvs_directory': CVS_DIR,
                'cvs_filenames': source,
            })
            temp_file = Path(CVS_DIR).joinpath(f'{task_id}.task_id')
            analyser.process_data_and_write_to_csv(
                file=temp_file,
            )
            temp_file.replace(target)
            cache.clear()
        task_id = str(uuid.uuid4())
        task = threading.Thread(target=_process_csv, args=(task_id,), name=task_id)
        LOG.info(f'Starting task {task_id} for {target.name}')
        task.start()
    return make_response(jsonify({'task_id': task_id, 'target': target.name}))


@APP.route('/active-tasks', defaults={'task_id': None}, methods=['GET'])
@APP.route('/active-tasks/<task_id>', methods=['GET'])
@login_required
def tasks(task_id):
    if task_id is None:
        return make_response(jsonify([{'task_id': task} for task in get_active_tasks()]))
    else:
        return make_response(jsonify([{'task_id': task} for task in get_active_tasks() if task == task_id]))


@APP.route('/download/<path:filename>', methods=['GET'])
@login_required
def download(filename):
    if filename in get_processed_cvs_filenames():
        return send_from_directory(directory=Path(CVS_DIR), filename=filename, as_attachment=True)
    return make_response('<h1>Not found</h1>', HTTPStatus.NOT_FOUND)


@APP.route('/remove/<path:filename>', methods=['POST'])
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


@cache.cached(timeout=60, key_prefix='raw_cvs_filenames')
def get_raw_cvs_filenames():
    cvs_paths = sorted(Path(CVS_DIR).glob(FutureEnergyDataLogAnalyser.GLOB_CSV_PATTERN))
    return [path.name for path in cvs_paths]


def get_processed_cvs_filenames():
    cvs_paths = sorted(Path(CVS_DIR).glob('processed_*.csv'))
    return [path.name for path in cvs_paths]


def get_active_tasks():
    task_paths = Path(CVS_DIR).glob('*.task_id')
    return [path.stem for path in task_paths]


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
