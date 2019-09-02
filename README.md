# The Future Energy Wind Turbine Data Log Analyser
Parse a directory of *.cvs files, sanitise the data and append values to a scatter plot.
```
> python3 datalog_analyser.py -h
usage: datalog_analyser.py [-h] --cvs_dir CVS_DIRECTORY

The Future Energy Wind Turbine Data Log Analyser

optional arguments:
  -h, --help            show this help message and exit
  --cvs_dir CVS_DIRECTORY
                        Directory path to CVS data log files
```
## Installation
### Linux
```
pip3 install -r requirements.txt
```
> (recommended) Use a virtualenv, setup for python3
https://virtualenvwrapper.readthedocs.io/en/latest/
### Windows
TBC
## Development
Run unittests & flake8

```
python3 datalog_analyser_unittest.py
flake8 datalog_analyser.py
```