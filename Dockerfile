FROM python:3.8
LABEL maintainer="Tom Valk <tomvalk@lt-box.info>"
ENV PROJECT_ROOT /app
ENV IS_DOCKER 1

# Create maniaplanet user/group
RUN addgroup --gid 1000 maniaplanet && \
    adduser -u 1000 --group maniaplanet --system

RUN apt-get -q update \
&& apt-get install -y build-essential libssl-dev libffi-dev zlib1g-dev \
    && rm -rf /var/lib/apt/lists/*

# Create project root.
RUN mkdir -p $PROJECT_ROOT
WORKDIR $PROJECT_ROOT
COPY docs/docker/root/base.py $PROJECT_ROOT/base.py
RUN chown -R maniaplanet:maniaplanet $PROJECT_ROOT

# Install PyPlanet.
RUN pip install pyplanet --upgrade

USER maniaplanet

# Init project.
RUN pyplanet init_project server
WORKDIR $PROJECT_ROOT/server/
RUN cp ../base.py $PROJECT_ROOT/server/settings/base.py

VOLUME $PROJECT_ROOT/server/

ENTRYPOINT [ "./manage.py" ]
CMD [ "start", "--pool=default", "--settings=settings" ]
