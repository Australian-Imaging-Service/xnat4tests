FROM tomcat:9-jre8-alpine

# User configurable arguments
ARG XNAT_VER
ARG XNAT_CS_PLUGIN_VER
ARG XNAT_BATCH_LAUNCH_PLUGIN_VER
ARG XNAT_ROOT=/data/xnat
ARG XNAT_HOME=/data/xnat/home
ARG JAVA_MS=256m
ARG JAVA_MX=2g
ARG XNAT_DATASOURCE_DRIVER=org.postgresql.Driver
ARG XNAT_DATASOURCE_URL=jdbc:postgresql://localhost:5432/xnat
ARG XNAT_DATASOURCE_USERNAME=xnat
ARG XNAT_DATASOURCE_PASSWORD=xnat
ARG XNAT_HIBERNATE_DIALECT=org.hibernate.dialect.PostgreSQL9Dialect
ARG TOMCAT_XNAT_FOLDER=ROOT
ARG TOMCAT_XNAT_FOLDER_PATH=${CATALINA_HOME}/webapps/${TOMCAT_XNAT_FOLDER}

# Create XNAT config file at $XNAT_HOME/config/xnat-conf.properties
COPY make-xnat-config.sh /usr/local/bin/make-xnat-config.sh

# Install XNAT
RUN apk add --no-cache postgresql postgresql-client supervisor wget vim docker
RUN rm -rf ${CATALINA_HOME}/webapps/*
RUN mkdir -p \
        ${TOMCAT_XNAT_FOLDER_PATH} \
        ${XNAT_HOME}/config \
        ${XNAT_HOME}/logs \
        ${XNAT_HOME}/plugins \
        ${XNAT_HOME}/work \
        ${XNAT_ROOT}/build \
        ${XNAT_ROOT}/cache \
        ${XNAT_ROOT}/ftp \
        ${XNAT_ROOT}/pipeline \
        ${XNAT_ROOT}/archive \
        ${XNAT_ROOT}/prearchive
RUN /usr/local/bin/make-xnat-config.sh
RUN rm /usr/local/bin/make-xnat-config.sh
RUN wget --no-verbose --output-document=/tmp/xnat-web-${XNAT_VER}.war https://api.bitbucket.org/2.0/repositories/xnatdev/xnat-web/downloads/xnat-web-${XNAT_VER}.war
RUN unzip -o -d ${TOMCAT_XNAT_FOLDER_PATH} /tmp/xnat-web-${XNAT_VER}.war
RUN rm -f /tmp/xnat-web-${XNAT_VER}.war
RUN wget --output-document ${XNAT_HOME}/plugins/container-service-plugin.jar https://api.bitbucket.org/2.0/repositories/xnatdev/container-service/downloads/container-service-${XNAT_CS_PLUGIN_VER}-fat.jar
RUN wget --output-document ${XNAT_HOME}/plugins/batch-launch-plugin.jar https://api.bitbucket.org/2.0/repositories/xnatx/xnatx-batch-launch-plugin/downloads/batch-launch-${XNAT_BATCH_LAUNCH_PLUGIN_VER}.jar
RUN apk del wget
RUN mkdir /var/log/tomcat
ENV XNAT_HOME=${XNAT_HOME} XNAT_DATASOURCE_USERNAME=${XNAT_DATASOURCE_USERNAME} PGPASSWORD=${XNAT_DATASOURCE_PASSWORD}
ENV CATALINA_OPTS="-Xms${JAVA_MS} -Xmx${JAVA_MX} -Dxnat.home=${XNAT_HOME}"

# Add scripts for configuring XNAT database before launching Tomcat
COPY launch-xnat.sh /launch-xnat.sh
COPY XNAT.sql /XNAT.sql

# Skip the new site setup by creating site preferences file
COPY xnat-prefs-init.ini ${XNAT_HOME}/config/prefs-init.ini

# Change the default port to 80 (so that the container service knows where to)
# find it) and expose it
# RUN sed -i 's/port="8080"/port="80"/' ${CATALINA_HOME}/conf/server.xml
EXPOSE 8080

# Setup Postgres
RUN mkdir /run/postgresql
RUN mkdir /var/lib/postgresql/data
RUN chmod 700 /var/lib/postgresql/data
RUN chown postgres:postgres /run/postgresql /var/lib/postgresql/data

# Create postgres DB
USER postgres
RUN initdb -D /var/lib/postgresql/data
RUN echo -e "\ndatasource.driver = '/tmp'" >> /var/lib/postgresql/data/postgresql.conf
USER root

# Use supervisord to launch postgres and tomcat
COPY supervisord.conf /etc/supervisord.conf
CMD ["/usr/bin/supervisord"]
