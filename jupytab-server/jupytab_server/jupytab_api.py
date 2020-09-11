# Copyright (c) 2019 Capital Fund Management
# SPDX-License-Identifier: MIT

import json
import os
import traceback
from typing import Any
from urllib.parse import urlunparse, urlencode

from tornado.httpclient import AsyncHTTPClient, HTTPRequest, HTTPClientError
from tornado.web import RequestHandler, HTTPError
from jupytab_server import __version__
import time

application_start_time = time.time()
root = os.path.dirname(__file__) + '/static'
api_kernel = 'api'
access_kernel = 'kernel'
restart_kernel = 'api/restart'
uri_security_token = 'security_token'
evaluate_method = "evaluate"


def transform_url(protocol, host, path, query=''):
    new_path = urlunparse((protocol, host, path, '', query, ''))
    return new_path


class BaseRequestHandler(RequestHandler):

    def initialize(self, notebook_store, security_token):
        self.notebook_store = notebook_store
        self.security_token = security_token

    def set_default_headers(self) -> None:
        self.set_header(name="Content-Type", value="application/json; charset=UTF-8")

    def write_error(self, status_code: int, **kwargs: Any) -> None:
        body = {
            'method': self.request.method,
            'uri': self.request.path,
            'code': status_code,
            'message': self._reason
        }
        if "exc_info" in kwargs:
            if self.settings.get("serve_traceback"):
                # in debug mode, send a traceback
                trace = '\n'.join(traceback.format_exception(
                    *kwargs['exc_info']
                ))
                body['trace'] = trace
            if isinstance(kwargs['exc_info'][1], HTTPError):
                body['message'] = kwargs['exc_info'][1].log_message
        self.finish(body)

    def on_chunk(self, chunk):
        self.write(chunk)
        self.flush()


class InfoHandler(BaseRequestHandler):
    def get(self, *args, **kwargs):
        self.write(
            {
                "description": "Jupytab Server, an open source project "
                               "available at https://github.com/CFMTech/Jupytab",
                "creation_time": application_start_time,
                "state_path": os.getcwd(),
                "server_version":  __version__,
                "name": "Jupytab Server",
                "versions": {
                    "v1": {
                        "features": {}
                    }
                }
            }
        )


class EvaluateHandler(BaseRequestHandler):
    async def post(self, *args, **kwargs):
        query = json.loads(self.request.body)

        # api_key = query['api_key']
        script = query['script']
        data = query['data']

        if script == 'return _arg1' and data['_arg1'] == 1:
            # Query sent by Tableau to test connection ...
            # b'{"api_key":"","script":"return _arg1","data":{"_arg1":1}}'
            self.write(json.dumps(1))
        else:
            script_params = query['script'].split('.')
            if len(script_params) != 2:
                raise HTTPError(log_message=f"<Notebook.function> expected instead of <{script}>")

            notebook_target, method_target = script_params

            if notebook_target not in self.notebook_store:
                raise HTTPError(log_message=f"Unknown notebook ({notebook_target})")

            kernel = self.notebook_store[notebook_target]
            host = f'{kernel.host}:{kernel.port}'
            my_url = transform_url('http', host, evaluate_method)

            body = {
                'function': method_target.lower(),
                'data': data
            }
            json_body = json.dumps(body)

            request = HTTPRequest(
                url=my_url,
                method='POST',
                headers=self.request.headers,
                follow_redirects=True,
                body=json_body,
                request_timeout=3600.0,
                streaming_callback=self.on_chunk)

            response = await AsyncHTTPClient().fetch(request)

            self.set_status(response.code)
            self.finish()


class RestartHandler(BaseRequestHandler):
    def get(self, *args, **kwargs):
        if self.security_token and self.get_argument(uri_security_token) != self.security_token:
            raise ConnectionRefusedError("Invalid security token")

        kernel_id = self.request.path[len(restart_kernel) + 2:]

        notebook_kernel = self.notebook_store[kernel_id]

        notebook_kernel.restart()


class APIHandler(BaseRequestHandler):
    def get(self, *args, **kwargs):
        if self.security_token and self.get_argument(uri_security_token) != self.security_token:
            raise ConnectionRefusedError("Invalid security token")

        notebook_dict = {}

        for key, value in self.notebook_store.items():
            notebook_dict[key] = \
                {
                    "kernel_id": key,
                    "name": value.name,
                    "status": value.kernel_status,
                    "path": str(value.notebook_file),
                    "host": value.host,
                    "port": value.port,
                    "description": value.description
                }

        self.write(notebook_dict)


class ReverseProxyHandler(BaseRequestHandler):

    async def get(self, *args, **kwargs):
        if self.security_token and self.get_argument(uri_security_token) != self.security_token:
            raise ConnectionRefusedError("Invalid security token")

        notebook_path = self.request.path[len(access_kernel) + 2:].split('/', 2)

        notebook_id = notebook_path[0]
        notebook_uri = notebook_path[1] if len(notebook_path) > 1 else ''
        kernel = self.notebook_store[notebook_id]

        host = f'{kernel.host}:{kernel.port}'

        query_arguments = self.request.query_arguments.copy()
        query_arguments.pop(uri_security_token, None)

        my_url = transform_url(
            'http',
            host,
            notebook_uri,
            urlencode(query_arguments, doseq=True))

        request = HTTPRequest(
            url=my_url,
            method='GET',
            headers=self.request.headers,
            follow_redirects=True,
            body=None,
            request_timeout=3600.0,
            streaming_callback=self.on_chunk)

        try:
            response = await AsyncHTTPClient().fetch(request)
            self.set_status(response.code)
            self.finish()
        except HTTPClientError as e:
            print(f"Error raised: Please visit {e.response.effective_url} from jupytab-server "
                  f"machine to get more information about notebook execution error")
            raise e
