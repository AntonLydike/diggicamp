FROM alpine/git as git
WORKDIR /app
RUN git clone https://github.com/TobiasKiehnlein/diggicamp.git .

FROM python:3.9-slim
WORKDIR /diggicamp
COPY --from=git /app/requirements.txt ./
RUN pip3 install -r requirements.txt
RUN echo 'python /diggicamp/diggicamp.py "$@" --cfg /config/dgc.json' > /usr/bin/dgc && \
    chmod +x /usr/bin/dgc
COPY entry.sh .
COPY --from=git /app .
RUN chmod +x entry.sh
CMD ./entry.sh