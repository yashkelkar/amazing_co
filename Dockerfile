FROM ubuntu:latest

RUN apt-get update && apt-get -y upgrade && apt-get install -y git python3.6 python3-pip gunicorn

COPY requirements.txt /code/requirements.txt
WORKDIR /code
RUN pip3 install -r /code/requirements.txt
COPY . /code

ENV PORT=8000

EXPOSE 8000

RUN echo 'gunicorn  employee_management.app:app --chdir src --log-file=-' > /start.sh
RUN chmod +x /start.sh

ENTRYPOINT ["sh", "/start.sh"]