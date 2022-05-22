FROM python:3.9-slim
WORKDIR /diggicamp

COPY requirements.txt ./
RUN pip3 install -r requirements.txt
RUN echo 'runuser -u ${FILES_USER} -g ${FILES_GROUP} -- python /diggicamp/diggicamp.py "$@" --cfg /config/dgc.json' > /usr/bin/dgc && \
    chmod +x /usr/bin/dgc
RUN echo 'runuser -u ${FILES_USER} -g ${FILES_GROUP} -- python /diggicamp/docker/timer.py "$@"' > /usr/bin/dgc-timer && \
    chmod +x /usr/bin/dgc-timer
COPY . .
RUN chmod +x ./docker/entry.sh
RUN mkdir /data
ENV PYTHONPATH=/diggicamp:$PYTHONPATH
CMD ./docker/entry.sh