# Start with Python 3.11 base image
FROM python:3.11.2-slim

RUN apt-get update && apt-get install --no-install-recommends -y bash nano mc build-essential

USER root

RUN groupadd user
RUN adduser --system --no-create-home --disabled-password --shell /bin/bash user

COPY --chown=user . /opt/server

RUN cd /opt/server && python3 -m pip install -e .

WORKDIR /opt/server

ENV CLIENT_CONF_URL ''
ENV CLIENT_NAME 'SKA'
ENV CLIENT_SCOPES 'openid email profile'
ENV PERMISSIONS_ROOT_GROUP ''
ENV PERMISSIONS_RELPATH '../../../etc/permissions'
ENV PERMISSIONS_NAME 'default.json'
ENV ROLES_RELPATH '../../../etc/roles'
ENV ROLES_NAME 'default.json'
ENV SESSION_MIDDLEWARE_SECRET_KEY ''
ENV SKA_CLIENT_ID ''
ENV SKA_CLIENT_SECRET ''

ENTRYPOINT ["/bin/bash", "etc/docker/init.sh"]