import requests
import json

from ska_src_compute_api.common.exceptions import handle_client_exceptions


class ComputeClient:
    def __init__(self, api_url, session=None, token=None):
        self.api_url = api_url
        if session:
            self.session = session
        else:
            self.session = requests.Session()
        if token:
            self.session.headers = {"Authorization": "Bearer {}".format(token)}

    @handle_client_exceptions
    def health(self):
        """Get the service health.

        :return: A requests response.
        :rtype: requests.models.Response
        """
        health_endpoint = "{api_url}/health".format(api_url=self.api_url)
        resp = self.session.get(health_endpoint)
        resp.raise_for_status()
        return resp

    @handle_client_exceptions
    def ping(self):
        """Ping the service.

        :return: A requests response.
        :rtype: requests.models.Response
        """
        ping_endpoint = "{api_url}/ping".format(api_url=self.api_url)
        resp = self.session.get(ping_endpoint)
        resp.raise_for_status()
        return resp

    @handle_client_exceptions
    def query(self, query_params:dict):
        query_endpoint = "{api_url}/query".format(api_url=self.api_url)
        resp = self.session.post(query_endpoint, json=query_params)
        resp.raise_for_status()
        return resp

    def provision(self, provision_params:dict):
        provision_endpoint = "{api_url}/provision".format(api_url=self.api_url)
        resp = self.session.put(provision_endpoint, json=provision_params)
        resp.raise_for_status()
        return resp

    def submit(self, provision_id:str, job_params:dict):
        submit_endpoint = "{api_url}/{provision_id}/submit".format(api_url=self.api_url, provision_id=provision_id)
        resp = self.session.put(submit_endpoint, json=job_params)
        return resp

    def status(self, provision_id:str):
        status_endpoint = "{api_url}/{provision_id}/status".format(api_url=self)
        resp = self.session.get(status_endpoint)
        return resp
