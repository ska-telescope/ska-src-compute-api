# SKA SRC Template API

This API is the template SRCNet API.

[TOC]

## Getting started

A script has been provided to initialise this template. This initialisation performs only the necessary steps for
local, **unauthenticated** development; by default the docker-compose enviromment does not connect the API with the
Authentication or Permissions APIs (see Development -> Bypassing AuthN/Z). **This means all endpoints are publicly 
accessible**.

To initialise a template, you must first choose a suitable API name. This name should be lowercase with words separated
by hyphens, e.g.

```bash
eng@ubuntu:~/SKAO/ska-src-template-api$ make init API_NAME=some-name
```

Good API names are short (but not to the detriment of understanding what they do!) and self-describing. Acronyms should
be avoided.

The init script requires the j2 CLI to be available, this can be installed for Python 3 via:
```bash
pip3 install j2cli
```

When invoked, the `init` script will create a new API code repository with the chosen name in the *parent*
directory of the `ska-src-template-api` service, and generate documentation and code stubs from the templates
in this repository. This can be added to version control as a new project.

Once the template has been initialised, consult the README for deployment via docker-compose.