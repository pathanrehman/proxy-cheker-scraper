FROM python:3.6.5-alpine
WORKDIR /app
ADD . /app

RUN set -e;\
	apk add --no-cache --virtual .build-deps \
    		gcc \
    		libc-dev \
    		linux-headers \
    		mariadb-dev \
    		python3-dev \
    		postgresql-dev \
    ;
COPY requirements.txt /app
RUN pip install -r requirements.txt
CMD ["python","main.py"]