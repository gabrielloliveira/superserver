FROM python:3.9.7
ENV PYTHONUNBUFFERED 1

#RUN apk add build-base
WORKDIR /server
COPY . /server/

RUN pip install --upgrade pip
RUN pip install wheel
RUN pip install -r requirements.txt

RUN chmod +x entrypoint.sh
RUN chmod +x entrypoint-client.sh
