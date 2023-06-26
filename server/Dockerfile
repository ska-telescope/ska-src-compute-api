# Start with Python 3.11 base image
FROM python:3.11.2-slim

RUN apt-get update && apt-get install --no-install-recommends -y bash nano mc build-essential

USER root

RUN groupadd user
RUN adduser --system --no-create-home --disabled-password --shell /bin/bash user

COPY --chown=user . /opt/server

RUN cd /opt/server && python3 -m pip install -e .

WORKDIR /opt/server

ENV TEST_ENV ''

ENTRYPOINT ["/bin/bash", "etc/docker/init.sh"]