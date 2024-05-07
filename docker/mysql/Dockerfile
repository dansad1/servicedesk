FROM mysql:8.4.0

COPY ./db_dump.json /db_dump.json

RUN chown mysql:mysql /db_dump.json
RUN chmod 644 /db_dump.json

EXPOSE 3306

COPY ./docker/mysql/db-init.sh /db-init.sh
RUN chmod +x /db-init.sh
ENTRYPOINT [ "/db-init.sh" ]
CMD [ "mysqld" ]