# Copyright (c) 2019 Capital Fund Management
# SPDX-License-Identifier: MIT

import os
from urllib.parse import urlunparse, urlencode

from tornado.httpclient import AsyncHTTPClient, HTTPRequest
from tornado.web import RequestHandler

root = os.path.dirname(__file__) + '/static'
api_kernel = 'api'
access_kernel = 'kernel'
restart_kernel = 'api/restart'

uri_security_token = 'security_token'


def transform_url(protocol, host, path, query):
    newpath = urlunparse((protocol, host, path, '', query, ''))
    print(newpath)
    return newpath


class RestartHandler(RequestHandler):
    def initialize(self, notebook_store, security_token):
        self.notebook_store = notebook_store
        self.security_token = security_token

    def get(self, *args, **kwargs):
        if self.security_token and self.get_argument(uri_security_token) != self.security_token:
            raise ConnectionRefusedError("Invalid security token")

        kernel_id = self.request.path[len(restart_kernel) + 2:]

        notebook_kernel = self.notebook_store[kernel_id]

        notebook_kernel.restart()


class APIHandler(RequestHandler):
    def initialize(self, notebook_store, security_token):
        self.notebook_store = notebook_store
        self.security_token = security_token

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


class ReverseProxyHandler(RequestHandler):
    def initialize(self, notebook_store, security_token):
        self.notebook_store = notebook_store
        self.security_token = security_token

        AsyncHTTPClient.configure(None, max_body_size=4000000000)

    def get(self, *args, **kwargs):
        pass

    def head(self, *args, **kwargs):
        pass

    def post(self, *args, **kwargs):
        pass

    def put(self, *args, **kwargs):
        pass

    def patch(self, *args, **kwargs):
        pass

    def options(self, *args, **kwargs):
        pass

    def delete(self, *args, **kwargs):
        pass

    async def prepare(self):
        if self.security_token and self.get_argument(uri_security_token) != self.security_token:
            raise ConnectionRefusedError("Invalid security token")

        notebook_path = self.request.path[len(access_kernel) + 2:].split('/', 2)

        request_body = None if self.request.method.lower() == "get" else self.request.body

        notebook_id = notebook_path[0]
        notebook_uri = notebook_path[1] if len(notebook_path) > 1 else ''
        kernel = self.notebook_store[notebook_id]

        host = f'{kernel.host}:{kernel.port}'

        query_arguments = self.request.query_arguments.copy()
        query_arguments.pop(uri_security_token, None)

        my_url = transform_url(
            self.request.protocol,
            host,
            notebook_uri,
            urlencode(query_arguments, doseq=True))

        request = HTTPRequest(
            url=my_url,
            method=self.request.method,
            headers=self.request.headers,
            follow_redirects=True,
            body=request_body,
            request_timeout=3600.0,
            streaming_callback=self.on_chunk)

        response = await AsyncHTTPClient().fetch(request)

        self.set_status(response.code)
        self.write(response.body)

        for k, v in response.headers.get_all():
            if k != 'Content-Length':
                self.add_header(k, v)

    def on_chunk(self, chunk):
        self.write(chunk)
        self.flush()
