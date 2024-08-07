FROM ubuntu:oracular-20240617

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && \
    apt-get install python3-dev default-libmysqlclient-dev build-essential pkg-config && \
    apt-get install -y python3 python3-pip && \
    apt-get clean 

WORKDIR /app

COPY . /app/

RUN pip3 install --upgrade pip && pip3 install -r requirements.txt

RUN pip install flask_mysqldb

EXPOSE 3000

CMD ["gunicorn", "application:app", "-b", "0.0.0.0:3000", "-w", "4"]