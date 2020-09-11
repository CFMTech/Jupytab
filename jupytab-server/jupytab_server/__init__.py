from tornado.httpclient import AsyncHTTPClient
from .__version__ import __version__

AsyncHTTPClient.configure(None, max_body_size=4000000000)

__all__ = [__version__]
