# SKA SRC REST Skeleton

## Overview

This is a template REST service which can be built upon to develop microservices for a range of purposes.

It uses the [FastAPI](https://fastapi.tiangolo.com/) framework and contains DevOps tooling to facilitate containerised deployment.

## Structure

The repository is structured as follows:

```bash
.
├── server
│   ├── docker-compose.yml
│   ├── Dockerfile
│   ├── etc
│   │   ├── docker
│   │   ├── helm
│   │   ├── permissions
│   │   └── roles
│   ├── README.md
│   ├── requirements.txt
│   ├── setup.py
│   └── src
│       └── fastapi_app
└── README.md
```

The top level `server` directory may be replicated if there are multiple services within a project.

## Deployment

### Docker (development)

In the simplest case, the service can be started within a single Docker container.

From the `server` directory:

```bash
$ docker build . -t ska-src-rest-skeleton:latest
$ docker run -it -p 4747:4747 ska-src-rest-skeleton:latest
```

Will run the service in a Docker container on the local system.

Alternatively, it is possible to use the `docker-compose.yaml` file via:

```bash
$ docker compose up
```

## Authentication and Authorization

An example authentication workflow is provided for protecting endpoints with an instance of the [Indigo IAM](https://github.com/indigo-iam/iam) service.

To make use of this for identity and access control requires a client to be registered at https://ska-iam.stfc.ac.uk/login. Once created, the client details can be set as environment variables in the `server/Dockerfile`.

### Retrieving an access token

1. Calling the `/login` endpoint will return a URL the user can use to login to Indigo IAM in a browser
2. After logging in, the user will be presented with a code to authenticate their client
3. By calling the `/token` endpoint and presenting this code as a query parameter (e.g. `/token?code=<auth_code>`), the user can retrieve their access token

## Development

Endpoints are defined in `server/src/fastapi_app/rest/server.py`. For modularity, it is recommended that these lightweight, with further logic being placed in `server/src/fastapi_app/api/backend.py`