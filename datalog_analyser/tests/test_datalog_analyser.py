#!/usr/bin/env python3

import unittest
import logging
import sys
from io import StringIO
import pandas as pd
from ..datalog_analyser import FutureEnergyDataLogAnalyser

log = logging.getLogger('FutureEnergyDataLogAnalyserTest')
log.setLevel(logging.DEBUG)
logging.basicConfig(stream=sys.stdout, level=logging.WARNING)


class FutureEnergyDataLogAnalyserTest(unittest.TestCase):
    def test_process_df(self):
        analyser = FutureEnergyDataLogAnalyser({'cvs_directory': None})
        raw_data = StringIO("""Futurenergy wind turbine datalog file. Created - 2019-08-22  06:00:00,
Inhibit state; 1 = NONE - 2 = LOW WIND - 3 = HIGH WIND.,
MPS used for TSR / ref RPM calculation; 0 = NONE Av - 1 = 1 min Av - 2 = 3 min Av - 3 = 10 min Av.,
Date,Time,Windspeed MPS,Wind Direction,RPM,ref RPM,TSR,Power,Inhibit State,MPS used for TSR,
2019/08/22,06:00:28,1.1,211,0,68,5.5,0,2,2,
2019/08/22,06:00:29,1,211,0,68,5.5,0,2,2,
2019/08/22,06:00:30,1,208,0,68,5.5,0,2,2,
2019/08/22,2019/08/22,06:00:37,0.9,208,0,68,5.5,0,2,06:00:34,2,0.9,
208,0,68,5.5,0,2,2,
2019/08/22,06:00:38,0.7,208,0,68,5.5,0,2,2,
2019/08/22,06:00:38,2019/08/22,208,0,68,5.5,0,2,2,
1,06:00:38,0.7,208,0,68,5.5,0,2,2,
2019/08/22,1,2019/08/22,208,0,68,5.5,0,2,2,
        """)  # noqa: E501
        df = analyser._process_df(
            pd.read_csv(raw_data, **analyser.read_csv_kwargs),
        )
        expected_df = pd.DataFrame(
            [
                ['2019/08/22 06:00:28', 1.1, 211, 0, 68, 5.5, 0, 2, 2],
                ['2019/08/22 06:00:29', 1, 211, 0, 68, 5.5, 0, 2, 2],
                ['2019/08/22 06:00:30', 1, 208, 0, 68, 5.5, 0, 2, 2],
                ['2019/08/22 06:00:38', 0.7, 208, 0, 68, 5.5, 0, 2, 2],
            ],
            columns=[
                'Date_Time',
                'Windspeed MPS',
                'Wind Direction',
                'RPM',
                'ref RPM',
                'TSR',
                'Power',
                'Inhibit State',
                'MPS used for TSR',
            ],
        )
        expected_df['Date_Time'] = pd.to_datetime(expected_df['Date_Time'])
        self.assertEqual(list(expected_df.columns), list(df.columns))
        self.assertEqual(expected_df.shape, df.shape)
        self.assertFalse(df.isna().any().any())


if __name__ == '__main__':
    unittest.main()
