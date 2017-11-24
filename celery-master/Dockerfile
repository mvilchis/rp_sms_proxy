FROM ubuntu:14.04


RUN apt-get update -y
RUN apt-get install -y python-pip python-dev

ENV C_FORCE_ROOT true

ENV HOST 0.0.0.0
ENV PORT 5000
ENV DEBUG true
# copy source code
COPY . /flask-app
WORKDIR /flask-app

# install requirements
RUN pip install -r requirements.txt

# expose the app port
EXPOSE 5000

# run the app server
ENTRYPOINT celery -A tasks beat --loglevel=info --app=worker_proxy
