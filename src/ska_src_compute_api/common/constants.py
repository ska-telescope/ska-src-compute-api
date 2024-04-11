import requests


class Constants:
    def __init__(self, client_conf_url):
        # Get oidc endpoints from IAM .well_known.
        resp = requests.get(client_conf_url)
        resp.raise_for_status()
        self.client_well_known = resp.json()

    # IAM url endpoints.
    #
    @property
    def iam_endpoint_authorization(self):
        return self.client_well_known.get("authorization_endpoint")

    @property
    def iam_endpoint_token(self):
        return self.client_well_known.get("token_endpoint")

    @property
    def iam_endpoint_introspection(self):
        return self.client_well_known.get("introspection_endpoint")
