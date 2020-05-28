from tornado.httpclient import AsyncHTTPClient

AsyncHTTPClient.configure(None, max_body_size=4000000000)
