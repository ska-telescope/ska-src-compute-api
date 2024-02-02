FROM python:3.8-bullseye

USER root

RUN groupadd user
RUN adduser --system --no-create-home --disabled-password --shell /bin/bash user

COPY --chown=user . /opt/ska-src-compute-api

RUN python3 -m pip install ska-src-permissions-api --index-url https://gitlab.com/api/v4/projects/48060714/packages/pypi/simple
RUN cd /opt/ska-src-compute-api && python3 -m pip install -e .

WORKDIR /opt/ska-src-compute-api

ENV API_ROOT_PATH ''
ENV API_SCHEME ''
ENV IAM_CLIENT_CONF_URL ''
ENV API_IAM_CLIENT_ID ''
ENV API_IAM_CLIENT_SECRET ''
ENV API_IAM_CLIENT_SCOPES ''
ENV API_IAM_CLIENT_AUDIENCE ''
ENV PERMISSIONS_API_URL ''
ENV PERMISSIONS_SERVICE_NAME ''
ENV PERMISSIONS_SERVICE_VERSION ''

ENTRYPOINT ["/bin/bash", "etc/docker/init.sh"]
