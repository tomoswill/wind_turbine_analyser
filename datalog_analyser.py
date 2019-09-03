#!/usr/bin/env python3
from abc import ABC, abstractmethod
import logging
import sys
import argparse
import glob
import os
import pandas as pd
import matplotlib.pyplot as plt

log = logging.getLogger('DataLogAnalyser')
log.setLevel(logging.DEBUG)
logging.basicConfig(stream=sys.stdout, level=logging.WARNING)


class DataLogAnalyserBase(ABC):
    """The Data Log Analyser Base"""
    def __init__(self, _options, _column_definition, _read_csv_kwargs):
        self.cvs_directory = _options['cvs_directory']
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
        csv_paths = glob.glob(os.path.join(self.cvs_directory, "*.csv"))
        if len(csv_paths) == 0:
            raise DataLogAnalyserBase.NoFilesException(
                'No *.csv files found in {}'.format(self.cvs_directory))
        for file in csv_paths:
            log.debug('Reading file %s', file)
            try:
                yield self._process_df(
                    pd.read_csv(file, **self.read_csv_kwargs),
                )
            except pd.errors.ParserError:
                log.exception('Error Reading file %s', file)
                continue

    def plot_scatter_graph(self, x, y):
        if not set(self.columns).issuperset((x, y)):
            raise DataLogAnalyserBase.ColumnNoExist()
        ax = plt.gca()
        for df in self._read_csv_logs():
            df.plot.scatter(x, y, ax=ax)
        plt.show()


class FutureEnergyDataLogAnalyser(DataLogAnalyserBase):
    """The Future Energy Wind Turbine Data Log Analyser"""
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
    args = parser.parse_args()
    log.info('Args %s', args)

    options = {
        'cvs_directory': os.path.abspath(args.cvs_directory),
    }
    analyser = FutureEnergyDataLogAnalyser(options)
    analyser.plot_scatter_graph(x='Windspeed MPS', y='Power')
