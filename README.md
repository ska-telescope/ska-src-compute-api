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

Once the template has been initialised, consult the README for deployment via docker-compose.