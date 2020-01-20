FROM python:3.8.1-slim
MAINTAINER Thomas Williams <37419355+tomoswill@users.noreply.github.com>

ENV LANG C.UTF-8

WORKDIR /datalog_analyser

COPY requirements.txt /datalog_analyser/requirements.txt
RUN pip3 install --requirement requirements.txt

COPY . /datalog_analyser

ARG ADMIN_PASSWORD=password
ARG APP_SECRET_KEY=DEV

ENV CVS_DIR=/cvs_dir
ENV ADMIN_PASSWORD=$ADMIN_PASSWORD
ENV APP_SECRET_KEY=$APP_SECRET_KEY

RUN python3 -m unittest --verbose

EXPOSE 8443

CMD ["/datalog_analyser/start_datalog_analyser.sh"]
