FROM python:3.10

RUN echo "nameserver 8.8.8.8" > /etc/resolv.conf

RUN pip install pipenv

ENV SRC_DIR /usr/local/src/container

WORKDIR ${SRC_DIR}

COPY Pipfile Pipfile.lock ${SRC_DIR}/

RUN pipenv install --system --clear

COPY ./ ${SRC_DIR}/

RUN mkdir ${SRC_DIR}/src/webapp/static/uploads

WORKDIR ${SRC_DIR}/src/webapp

CMD flask initdb && flask run -h 0.0.0.0
