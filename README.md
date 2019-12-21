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
  --save                Output the plot to PNG
  --no-display          Do not interactively display the plot
```
## Web App
#### Create certificate

```
openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -days 365 -nodes -subj '/CN=localhost'
```

#### Run under gunicorn with SSL

```
gunicorn --bind=0.0.0.0:8443 --certfile=cert.pem --keyfile=key.pem app:APP
```
## Installation
### Linux
```
pip3 install -r requirements.txt
```
> (recommended) Use a virtualenv, setup for python3
https://virtualenvwrapper.readthedocs.io/en/latest/
### Windows
#### Anaconda
1. Install Anaconda distribution for python3 https://www.anaconda.com/distribution/
2. (recommended) create a clean Anaconda environment
3. From Anaconda prompt ```pip install -r requirements.txt```

## Development
Run unittests & flake8

```
python3 datalog_analyser_unittest.py
flake8 datalog_analyser.py
```