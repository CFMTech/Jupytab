# Copyright (c) 2019 Capital Fund Management
# SPDX-License-Identifier: MIT

import argparse
import hashlib
import logging
import os.path
import socket
from configparser import ConfigParser, NoSectionError, NoOptionError

from tornado.ioloop import IOLoop
from tornado.web import StaticFileHandler, Application

from jupytab_server import __version__
from jupytab_server.jupytab_api import InfoHandler, RestartHandler, APIHandler, EvaluateHandler, \
    ReverseProxyHandler, root, api_kernel, access_kernel, restart_kernel
from jupytab_server.kernel_executor import KernelExecutor
from jupytab_server.structures import CaseInsensitiveDict

logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.INFO)


def __extract_item(config, notebook_key, item_key, default=None):
    try:
        return config.get(notebook_key, item_key)
    except (NoOptionError, NoSectionError):
        if default:
            return default
        else:
            raise ValueError(f'Expecting {item_key} in section {notebook_key}')


def config_listen_port(config):
    return config.getint('main', 'listen_port')


def config_security_token(config):
    try:
        return config.get('main', 'security_token')
    except (NoSectionError, NoOptionError):
        return None


def config_notebooks(config):
    notebooks = config.get('main', 'notebooks')
    notebook_dict = {}

    for key in notebooks.split('|'):
        nb_path = __extract_item(config, key, 'path')
        nb_name = __extract_item(config, key, 'name', key)
        nb_description = __extract_item(config, key, 'description', "No description")
        nb_cwd = __extract_item(config, key, 'directory', ".")

        notebook_dict[key] = {'name': nb_name,
                              'file_path': nb_path,
                              'description': nb_description,
                              'cwd': nb_cwd}

    return notebook_dict


def config_ssl(config):
    try:
        ssl_enabled = config.getboolean('main', 'ssl_enabled')
    except (NoSectionError, NoOptionError):
        ssl_enabled = False

    if ssl_enabled:
        ssl_cert = config.get('main', 'ssl_cert')
        ssl_key = config.get('main', 'ssl_key')

        if ssl_enabled and not os.path.isfile(ssl_cert):
            raise FileNotFoundError(f"SSL enabled but missing ssl_cert file: {ssl_cert}")
        if ssl_enabled and not os.path.isfile(ssl_key):
            raise FileNotFoundError(f"SSL enabled but missing ssl_key file: {ssl_key}")

        return {
            "certfile": ssl_cert,
            "keyfile": ssl_key
        }
    else:
        return None


def parse_config(config_file):
    if not os.path.isfile(config_file):
        raise FileNotFoundError(f"missing configuration: {config_file}")

    config = ConfigParser()
    config.optionxform = str
    config.read(config_file)

    listen_port = config_listen_port(config)
    security_token = config_security_token(config)
    notebooks = config_notebooks(config)
    ssl = config_ssl(config)

    if not ssl:
        print("SSL not enabled")
    else:
        print("SSL enabled")

    return {
        'listen_port': listen_port,
        'security_token': security_token,
        'notebooks': notebooks,
        'ssl': ssl
    }


def create_server_app(listen_port, security_token, notebooks, ssl):
    notebook_store = CaseInsensitiveDict()

    for key, value in notebooks.items():
        notebook_store[key] = KernelExecutor(**value)

    for key, value in notebook_store.items():
        value.start()

    protocol = "https" if ssl else "http"

    if security_token:
        token_digest = hashlib.sha224(security_token.encode('utf-8')).hexdigest()
        print(f"""Your token is {token_digest}
        Please open : {protocol}://{socket.gethostname()}:{listen_port}"""
              f"/?security_token={token_digest}")
    else:
        token_digest = None
        print(f"""You have no defined token. Please note your process is not secured !
        Please open : {protocol}://{socket.gethostname()}:{listen_port}""")

    server_app = Application([
        (r"/info", InfoHandler,
         {'notebook_store': notebook_store, 'security_token': token_digest}),
        (r"/evaluate", EvaluateHandler,
         {'notebook_store': notebook_store, 'security_token': token_digest}),
        (r"/" + api_kernel, APIHandler,
         {'notebook_store': notebook_store, 'security_token': token_digest}),
        (r"/" + restart_kernel + "/(.*)", RestartHandler,
         {'notebook_store': notebook_store, 'security_token': token_digest}),
        (r"/" + access_kernel + "/(.*)", ReverseProxyHandler,
         {'notebook_store': notebook_store, 'security_token': token_digest}),

        (r"/(.*)", StaticFileHandler, {'path': root, "default_filename": "index.html"}),

    ])
    return server_app


def main(input_args=None):
    print(f"Starting Jupytab-Server {__version__}")
    parser = argparse.ArgumentParser(description='The Tableau gateway to notebooks')
    parser.add_argument("-c", "--config", dest='config_file', default='config.ini', type=str)
    parser.add_argument("-e", "--env", dest='environment', default='UNKNOWN', type=str)
    parser.add_argument("-v", "--version", action='version', version=f"Jupytab {__version__}")
    args, unknown = parser.parse_known_args(args=input_args)

    params = parse_config(config_file=args.config_file)

    app = create_server_app(**params)

    app.listen(params['listen_port'], ssl_options=params['ssl'])

    IOLoop.instance().start()


if __name__ == "__main__":
    main()
