# SKA SRC Compute API

This API has been generated from a templated SRCNet API. Please fill out this section with details about what the API
does.

[TOC]

## Authentication

The following sections assume that the API has been integrated with both IAM and the Permissions API. This involves:

- Creating an IAM client (for Services to obtain access via a `client_credentials` grant),
- Passing the credentials (id/secret) to either `.env` files (docker-compose) or in the `values.yaml` (helm), and
- Creating the permissions policy and loading it in to the Permissions API.

Access can then be granted for either a User or Service.

### User

To access this API as a user, the user needs to have first authenticated with the SRCNet and to have exchanged the token 
resulting from this initial authentication with one that allows access to this specific service. See the Authentication 
Mechanism and Token Exchange Mechanism sections of the Authentication API for more specifics.

### Service

For service-to-service interactions, it is possible to obtain a token via a ***client_credentials*** grant to the
ska-src-compute-api IAM client.

## Authorisation

Hereafter, the caller (either a user or another service) is assumed to have a valid token allowing access to this API. 
Authenticated requests are then made by including this token in the header.

The token audience must also match the expected audience, also defined in the compute-api permissions 
policy (default: “compute-api”).

### Restricting user access to routes using token scopes

The presented token must include a specific scope expected by the service to be permitted access to all API routes. This 
scope is defined in the compute-api permissions policy 
(default: “compute-api-service”). 

**This scope must also be added to the IAM permissions client otherwise the process of token introspection will drop 
this scope.**

## Development

Makefile targets have been included to facilitate easier and more consistent development against this API. The general 
recipe is as follows:

1. Depending on the fix type, create a new major/minor/patch branch, e.g. 
    ```bash
    $ make patch-branch NAME=some-name
    ```
    Note that this both creates and checkouts the branch.
2. Make your changes.
3. Create new code samples if necessary.
   ```bash
   $ make code-samples
   ```
4. Add your changes to the branch:
    ```bash
   $ git add ...
    ```
5. Either commit the changes manually (if no version increment is needed) or bump the version and commit, entering a 
   commit message when prompted:
    ```bash
   $ make bump-and-commit
    ```
6. Push the changes upstream when ready:
    ```bash
   $ make push
    ```

Note that the CI pipeline will fail if python packages with the same semantic version are committed to the GitLab 
Package Registry.

### Code Structure

The repository is structured as follows:

```
.
├── .env.template
├── .gitlab-ci.yml
├── bin
├── docker-compose.yml
├── Dockerfile
├── etc
│   ├── docker
│   │   └── init.sh
│   ├── helm
│   │   ├── Chart.yaml
│   │   ├── templates
│   │   └── values.yaml.template
│   └── scripts
│       ├── generate-code-samples.sh
│       ├── increment-app-version.sh
│       └── increment-chart-version.sh
├── LICENSE
├── README.md
├── requirements.txt
├── setup.py
├── src
│   └── 
│       ├── client
│       ├── common
│       ├── models
│       └── rest
├── TODO.md
└── VERSION
```

The API endpoint logic is within the `src/rest/server.py` with `/ping` and `/health` endpoints provided as a reference.

### Bypassing AuthN/Z

AuthN/Z can be bypassed for development by setting `DISABLE_AUTHENTICATION=yes` in the environment.

## Deployment

Deployment is managed by docker-compose or helm.

The docker-compose file can be used to bring up the necessary services locally i.e. the REST API, setting the mandatory
environment variables. Sensitive environment variables, including those relating to the IAM client, should be kept in
`.env` files to avoid committing them to the repository.

There is also a helm chart for deployment onto a k8s cluster.

### Example via docker-compose

Edit the `.env.template` file accordingly and rename to `.env`, then:

```bash
eng@ubuntu:~/SKAO/ska_src_compute_api$ docker-compose up
```

When the service has been deployed, navigate to http://localhost:8080/v1/www/docs/oper to view the (swagger) frontend.

Similarly, you can test the service locally by calling http://localhost:8080/v1/ping.

### Example via Helm

After editing the `values.yaml` (template in `/etc/helm/`):

```bash
$ create namespace ska_src_compute_api
$ helm install --namespace ska_src_compute_api ska_src_compute_api .
```

### Return codes
For several end points, the API will provide return codes to reflect the reply. The following table states the meaning
of the return codes per API end point. Each code will be returned together with a human-readable string specifying 
what the actual reason for the code is so that a user can decide how to change their request to be successful.

#### JSON parsing
When JSON parsing fails, the framework will return an HTTP 422 error, giving some hints on what data is missing. 

#### /query and /provision (POST)
Docs URL (query): `/v1/www/docs/oper#post-/query`
Docs URL (provison): `/v1/www/docs/oper#post-/provision`

| code | meaning                              | text content                                                           |
|------|--------------------------------------|------------------------------------------------------------------------|
| 0    | Successful (resources are available) | OK                                                                     |
| 1    | Resources do not exist               | "(XYZ) not available" where XYZ is a (list of) resource(s).            |
| 2    | Resources unavailable right now      | "(XYZ) not bookable" where XYZ is a (list of) resource(s).             |
| 3    | Internal error                       | "Internal error (specification)" (e.g. "could not connect to backend") |
| 255  | Unexpected error                     | If possible and applicable: a description                              |

#### /submit
Docs URL: `v1/www/docs/oper#post-/submit` (POST)
| code | meaning                     | text content                                                                          |
|------|-----------------------------|---------------------------------------------------------------------------------------|
| 0    | Successful (job submitted)  | OK                                                                                    |
| 1    | Job validation error        | "Job cannot be executed: ABC" e.g. ABC being "data not in this location"              |
| 2    | Invalid provision           | "Invalid provision: ABC" ABC could be "provision ID unknown" or "provision expired"   |
| 3    | Internal error              | "Internal error (specification)" (e.g. "could not connect to backend")                |
| 4    | Access denied               | "Access denied"                                                                       |
| 255  | Unexpected error            | If possible and applicable: a description                                             |

#### job status (GET)
Docs URL: `v1/www/docs/oper#get-/provision/-provision_id-/-job_id-/status`
| code | meaning               | text content                                                                                                   |
|------|-----------------------|----------------------------------------------------------------------------------------------------------------|
| 0    | Successful (job done) | OK                                                                                                             |
| 1    | Job running           | "Running..."                                                                                                   |
| 2    | Invalid provision     | "Invalid job: ABC" ABC could be "job does not exist"   |
| 3    | Internal error        | "Internal error (specification)" (e.g. "could not connect to backend")                                         |
| 4    | Access denied         | "Access denied"                                                                                                |
| 5    | Execution error       | "Execution error: (XYZ)" XYZ describes the cause (e.g. ran out of certain resources, application crashed, ...) |
| 6    | System error          | "System error: (XYZ)" XYZ describes the cause (e.g. computer shut down, disk failed, ...)                      |

| 255  | Unexpected error      | If applicable a description                                                                                    |

## References
