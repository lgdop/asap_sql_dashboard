FROM lgdop/centos6:python2.7.14

# Java Env Variables
ENV JAVA_VERSION=1.8.0
ENV JAVA_HOME=/usr/lib/jvm/java-1.8.0-openjdk-1.8.0.191.b12-1.el7_6.x86_64/jre

RUN yum update -y && yum -y install epel-release \
                                 unzip \
                                 java-1.8.0-openjdk \
                                 libaio

RUN virtualenv my27project && source my27project/bin/activate && python --version

RUN pip2.7 install dash==0.35.1 \
                dash-html-components==0.13.4 \
                dash-core-components==0.42.1 \
                datetime \
                pymongo \
                flask \
                gunicorn \
                python-dotenv \
                cx_Oracle \
                SQLAlchemy \
                dash-table==3.1.11 \
                pandas \
                dash-auth==1.2.0
WORKDIR /sql_difference

COPY . .
RUN mkdir -p /usr/lib/oracle
COPY oracle_client.zip /usr/lib/oracle/
RUN unzip /usr/lib/oracle/oracle_client.zip -d /usr/lib/oracle

ENV LD_LIBRARY_PATH=:/usr/lib/oracle/12.2/client64/lib/
ENV TNS_ADMIN=/usr/lib/oracle/12.2/network
ENV PATH=/usr/local/bin:/usr/local/lib:/bin:/usr/bin:/sbin:/usr/sbin:/usr/local/bin:/usr/lib/oracle/12.2/client64/bin:/usr/lib/oracle/12.2/:/usr/lib/oracle/12.2/client64/bin:/sql_difference:$PATH
ENV PWD2=/usr/lib/oracle/12.2/network/mesg
ENV ORACLE_HOME=/usr/lib/oracle/12.2

EXPOSE 3050

CMD [ "gunicorn", "--bind", "0.0.0.0:3050","-w","5", "asap_sql_dashboard:server" ]
