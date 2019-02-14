FROM python:3.7.2-alpine
LABEL Name=my-smarthome-cloud-controller Version=0.0.1

RUN apk update && apk add --no-cache make gcc g++
                # apk add --no-cache make=4.2.1-r2 gcc=6.4.0-r9 g++=6.4.0-r9

RUN python3 -m pip install --upgrade pip setuptools wheel

WORKDIR /opt/app

COPY requirements.txt .
RUN python3 -m pip --no-cache-dir install -r requirements.txt

RUN apk del make gcc g++

COPY cloud_flask cloud_flask
RUN mkdir -p instance

ENV FLASK_APP=cloud_flask
ENV FLASK_ENV=development
CMD ["flask", "run", "--host=0.0.0.0"]
