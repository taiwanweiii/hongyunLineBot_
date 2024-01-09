FROM python:3.11.4

ENV TZ=Asia/Taipei
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

WORKDIR /usr/src/app
COPY ./requirements.txt ./
RUN pip install --upgrade pip && pip install -r requirements.txt

