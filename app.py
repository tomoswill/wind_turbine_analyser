import threading
from os import getenv
from pathlib import Path

import time
from flask import Flask, render_template, request
from flask_caching import Cache

from datalog_analyser import FutureEnergyDataLogAnalyser

app = Flask(__name__)
cache = Cache(config={'CACHE_TYPE': 'simple', "CACHE_DEFAULT_TIMEOUT": 300})
cache.init_app(app)

CVS_DIR = getenv('CVS_DIR')


@app.route('/')
@cache.cached(timeout=60)
def homepage():
    cvs_filenames = get_cvs_filenames()
    default_start_csv = cvs_filenames[0]
    default_end_csv = cvs_filenames[-1]
    return render_template('index.html',
                           cvs_filenames=cvs_filenames,
                           default_start_csv=default_start_csv,
                           default_end_csv=default_end_csv)


@app.route('/sanitize_data', methods=['POST'])
def generate_sanitized():
    data = request.form
    cvs_filenames = get_cvs_filenames()
    cvs_filenames[:] = cvs_filenames[cvs_filenames.index(data['start_csv']): cvs_filenames.index(data['end_csv']) + 1]

    def _process_csv(files):
        analyser = FutureEnergyDataLogAnalyser({
            'cvs_directory': CVS_DIR,
            'cvs_filenames': files,
        })
        analyser.sanitize_data_and_write_to_csv(
            file=Path(CVS_DIR).joinpath('sanitized-{time}.csv'.format(time=time.strftime("%Y%m%d-%H%M"))),
        )

    threading.Thread(target=_process_csv, args=(cvs_filenames,)).start()
    return 'Done!'


def get_cvs_filenames():
    cvs_paths = sorted(Path(CVS_DIR).glob(FutureEnergyDataLogAnalyser.GLOB_CSV_PATTERN))
    return [path.name for path in cvs_paths]


if __name__ == '__main__':
    app.run()
