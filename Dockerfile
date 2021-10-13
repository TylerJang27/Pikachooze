FROM ubuntu:20.04

RUN apt-get update -y && \
    apt-get install -y python3-pip python3-dev

WORKDIR /app

#RUN pip3 install flask Flask-Limiter
RUN pip3 install virtualenv

COPY . /app

#RUN apt-get install -y postgresql-client
#RUN pip3 install -r requirements.txt
#RUN ["/bin/bash", "-c", "virtualenv env"]
#RUN ["/bin/bash", "-c", "source env/bin/activate"]
#RUN ["/bin/bash", "-c", "db/setup.sh"]

# RUN echo -e "12\n" | apt-get install -y postgresql-12
RUN wget https://ftp.postgresql.org/pub/source/v12.8/postgresql-12.8.tar.gz
RUN gunzip postgresql-12.8.tar.gz
RUN tar xf postgresql-12.8.tar

# RUN apt-get install -y postgresql-client
# RUN export PATH="/usr/bin/psql"
RUN ./install.sh

#ENTRYPOINT [ "python3" ]
RUN flask run
#CMD [ "pikachooze.py" ]