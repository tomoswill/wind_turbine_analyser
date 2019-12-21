import threading
from os import getenv
from pathlib import Path

from flask import Flask, render_template, request
from flask_caching import Cache

from datalog_analyser import FutureEnergyDataLogAnalyser

APP = Flask(__name__)
cache = Cache(config={'CACHE_TYPE': 'simple', "CACHE_DEFAULT_TIMEOUT": 300})
cache.init_app(APP)

CVS_DIR = getenv('CVS_DIR')


@APP.route('/')
@cache.cached(timeout=60)
def homepage():
    cvs_filenames = get_cvs_filenames()
    if len(cvs_filenames) == 0:
        return 'Error: No csv files found'
    default_start_csv = cvs_filenames[0]
    default_end_csv = cvs_filenames[-1]
    return render_template('index.html',
                           cvs_filenames=cvs_filenames,
                           default_start_csv=default_start_csv,
                           default_end_csv=default_end_csv)


@APP.route('/process_data', methods=['POST'])
def process_data():
    data = request.form
    source = get_cvs_filenames()
    source[:] = source[source.index(data['start_csv']): source.index(data['end_csv']) + 1]
    target = Path(CVS_DIR).joinpath('processed_{start}_{end}.csv'.format(
        start=source[0].split('.')[0], end=source[-1].split('.')[0]))
    if not Path(target).exists():
        def _process_csv():
            analyser = FutureEnergyDataLogAnalyser({
                'cvs_directory': CVS_DIR,
                'cvs_filenames': source,
            })
            analyser.process_data_and_write_to_csv(
                file=target,
            )
        threading.Thread(target=_process_csv).start()
    return 'Written to: ' + str(target)


def get_cvs_filenames():
    cvs_paths = sorted(Path(CVS_DIR).glob(FutureEnergyDataLogAnalyser.GLOB_CSV_PATTERN))
    return [path.name for path in cvs_paths]


if __name__ == '__main__':
    APP.run(debug=True)
