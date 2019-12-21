# The Future Energy Wind Turbine Data Log Analyser
An (unofficial) tool to parse a directory of *.cvs files, process and concatenate the data. Can be easily expanded to sanitise cvs files from other sources.
## Datalog Analyser plot tool
Example usage: plots values to a scatter diagram of Windspeed vs. Power.
```
> python3 plot.py -h
usage: plot.py [-h] --cvs_dir CVS_DIRECTORY

The Future Energy Wind Turbine Data Log Analyser

optional arguments:
  -h, --help            show this help message and exit
  --cvs_dir CVS_DIRECTORY
                        Directory path to CVS data log files
  --save                Output the plot to PNG
  --no-display          Do not interactively display the plot
```
## Datalog Analyser concat tool
TBC
## Remote management Web-App
A web application to remotely parse a directory of *.cvs files, process and concatenate the data.
#### HTTPS (recommended)
```
gunicorn --bind=0.0.0.0:8443 --certfile=cert.pem --keyfile=key.pem datalog_analyser.app:APP
```
On linux can create self-signed certificates
> openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -days 365 -nodes -subj '/CN=localhost'
#### HTTP
```
gunicorn --bind=0.0.0.0:8000 datalog_analyser.app:APP
```
## Installation
### Linux
```
pip3 install -r requirements.txt
```
> (recommended) Use a virtualenv, setup for python3
https://virtualenvwrapper.readthedocs.io/en/latest/
### Windows (tested with Anaconda)
1. Install Anaconda distribution for python3 https://www.anaconda.com/distribution/
2. (recommended) create a clean Anaconda environment
3. From Anaconda prompt ```pip install -r requirements.txt```
## Development
Run unittests & flake8
```
python -m unittest
flake8 datalog_analyser/datalog_analyser.py
```