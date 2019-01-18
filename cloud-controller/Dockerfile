FROM python:3.7.2-alpine
LABEL Name=my-smarthome-cloud-controller Version=0.0.1

RUN python3 -m pip install --upgrade pip setuptools wheel

WORKDIR /opt/app

COPY requirements.txt .
RUN python3 -m pip --no-cache-dir install -r requirements.txt

COPY cloud_flask cloud_flask
RUN mkdir -p instance

ENV FLASK_APP=cloud_flask
ENV FLASK_ENV=development
CMD ["flask", "run", "--host=0.0.0.0"]
