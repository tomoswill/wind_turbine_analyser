#!/usr/bin/env python3
import argparse
from pathlib import Path

from datalog_analyser.datalog_analyser import FutureEnergyDataLogAnalyser

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

    options = {
        'cvs_directory': Path(args.cvs_directory).absolute(),
    }
    analyser = FutureEnergyDataLogAnalyser(options)
    analyser.plot_scatter_graph(x='Windspeed MPS',
                                y='Power',
                                title='Windspeed vs. Power',
                                save=args.save,
                                display=args.display)
