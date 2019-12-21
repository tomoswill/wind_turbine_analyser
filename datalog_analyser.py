#!/usr/bin/env python3
import argparse
import logging
import sys
import time
import uuid
from abc import ABC, abstractmethod
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

log = logging.getLogger('DataLogAnalyser')
log.setLevel(logging.DEBUG)
logging.basicConfig(stream=sys.stdout, level=logging.WARNING)


class DataLogAnalyserBase(ABC):
    """The Data Log Analyser Base"""
    GLOB_CSV_PATTERN = '*.csv'

    def __init__(self, _options, _column_definition, _read_csv_kwargs):
        self.cvs_directory = _options['cvs_directory']
        self.cvs_filenames = _options['cvs_filenames'] if 'cvs_filenames' in _options else None
        self.column_definition = _column_definition
        self.read_csv_kwargs = _read_csv_kwargs

    @property
    def columns(self):
        return list(self.column_definition.keys())

    class ColumnNoExist(Exception):
        pass

    class NoFilesException(Exception):
        pass

    @abstractmethod
    def _process_df(self, df):
        pass

    def _columns_by_type(self, ty):
        return [col for col, t in self.column_definition.items() if t == ty]

    def _read_csv_logs(self):
        if self.cvs_filenames is None:
            csv_paths = list(sorted(Path(self.cvs_directory).glob(self.GLOB_CSV_PATTERN)))
            if len(csv_paths) == 0:
                raise DataLogAnalyserBase.NoFilesException(
                    'No *.csv files found in "{}"'.format(self.cvs_directory))
        else:
            csv_paths = [Path(self.cvs_directory).joinpath(file) for file in self.cvs_filenames]
        for file in csv_paths:
            log.debug('Reading file %s', file)
            if not Path(file).exists():
                raise DataLogAnalyserBase.NoFilesException(
                    'csv file not found: "{}"'.format(file))
            try:
                yield self._process_df(
                    pd.read_csv(file, **self.read_csv_kwargs),
                )
            except pd.errors.ParserError:
                log.exception('Error Reading file %s', file)
                continue

    def process_data_and_write_to_csv(self, file):
        write_csv_header = True
        for df in self._read_csv_logs():
            log.debug('Writing df to file %s', file)
            df.to_csv(file, index=False, mode='a', header=write_csv_header)
            write_csv_header = False
        log.info('Done writing df to file %s', file)

    def plot_scatter_graph(self, x, y, title, save=True, display=False):
        if not set(self.columns).issuperset((x, y)):
            raise DataLogAnalyserBase.ColumnNoExist()
        ax = plt.gca()
        for df in self._read_csv_logs():
            df.plot.scatter(x, y, ax=ax, title=title)
        ax.grid(True)
        if display:
            plt.show()
        if save:
            file = '{time}-{uuid}-{x}-{y}.png'.format(
                time=time.strftime("%Y%m%d-%H%M"),
                uuid=uuid.uuid4().hex[:8],
                x=x.replace(' ', '_'),
                y=y.replace(' ', '_'),)
            log.info('Saving as "{}"'.format(file))
            ax.get_figure().savefig(file)


class FutureEnergyDataLogAnalyser(DataLogAnalyserBase):
    """The Future Energy Wind Turbine Data Log Analyser"""
    GLOB_CSV_PATTERN = '[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]-[0-9][0-9].csv'

    def __init__(self, _options):
        _column_definition = {
            'Date_Time': 'datetime',
            'Windspeed MPS': 'numeric',
            'Wind Direction': 'numeric',
            'RPM': 'numeric',
            'ref RPM': 'numeric',
            'TSR': 'numeric',
            'Power': 'numeric',
            'Inhibit State': 'numeric',
            'MPS used for TSR': 'numeric',
        }
        _read_csv_kwargs = {
            'header': 3,
            'error_bad_lines': False,
            'warn_bad_lines': False,
        }
        super().__init__(_options, _column_definition, _read_csv_kwargs)

    def _process_df(self, df):
        # strict parse datetime columns
        df['Date_Time'] = pd.to_datetime(
            df['Date'] + ' ' + df['Time'], errors='coerce')
        # strict parse numeric columns
        numeric_cols = self._columns_by_type('numeric')
        df[numeric_cols] = df[numeric_cols].apply(
            pd.to_numeric, errors='coerce')
        # select cols & remove bad NaN rows & cols
        df = df[self.columns].dropna(axis=0)
        return df


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='The Future Energy Wind Turbine Data Log Analyser')
    parser.add_argument('--cvs_dir', dest='cvs_directory', required=True,
                        help='Directory path to CVS data log files')
    parser.add_argument('--save', dest='save', action='store_true',
                        help='Output the plot to PNG')
    parser.add_argument('--no-display', dest='display', action='store_false',
                        help='Do not interactively display the plot')
    args = parser.parse_args()
    log.info('Args %s', args)

    options = {
        'cvs_directory': Path(args.cvs_directory).absolute(),
    }
    analyser = FutureEnergyDataLogAnalyser(options)
    analyser.plot_scatter_graph(x='Windspeed MPS',
                                y='Power',
                                title='Windspeed vs. Power',
                                save=args.save,
                                display=args.display)
