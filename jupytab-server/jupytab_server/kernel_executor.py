# Copyright (c) 2019 Capital Fund Management
# SPDX-License-Identifier: MIT

import logging
import os
import socket
import subprocess
import sys

from . import log_pipe


class KernelCallback:
    def on_kernel_start(self, kernel_executor):
        pass

    def on_kernel_stop(self, kernel_executor):
        pass


class KernelExecutor:
    def __init__(self, name, file_path, description=None, kernel_callback=None, cwd=None):
        self.__notebook_name = name
        self.__notebook_file = file_path
        self.__notebook_description = description
        self.__kernel_callback = kernel_callback
        self.__kernel_process = None
        self.__host = '127.0.0.1'
        self.__port = None
        self.__cwd = cwd

    @staticmethod
    def get_free_tcp_port():
        tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        tcp.bind(('', 0))
        host, port = tcp.getsockname()
        tcp.close()

        return port

    def start(self):
        my_env = dict(os.environ)
        my_env['PATH'] = os.path.dirname(sys.executable) + os.pathsep + os.environ.get('PATH')

        self.__port = KernelExecutor.get_free_tcp_port()

        print(f'Start notebook {self.notebook_file} on {self.host}:{self.port}')

        logpipe = log_pipe.LogPipe(logging.INFO)

        command_line = [
            u"jupyter",
            u"kernelgateway",
            u"--KernelGatewayApp.api='kernel_gateway.notebook_http'",
            u"--KernelGatewayApp.seed_uri={filename}".format(filename=self.notebook_file),
            u"--KernelGatewayApp.ip='{host}'".format(host=self.host),
            u"--KernelGatewayApp.port={port}".format(port=self.port)
        ]

        self.__kernel_process = subprocess.Popen(command_line,
                                                 env=my_env,
                                                 stdout=logpipe,
                                                 stderr=logpipe,
                                                 cwd=self.cwd)

        if self.__kernel_callback:
            self.__kernel_callback.on_kernel_start(self)

        return f'{self.host}:{self.port}'

    def stop(self):
        print(f'Stop notebook {self.notebook_file} on {self.host}:{self.port}')

        self.__kernel_process.kill()
        self.__kernel_process = None

        if self.__kernel_callback:
            self.__kernel_callback.on_kernel_stop(self)

    def restart(self):
        print(f'Restart notebook {self.notebook_file} on {self.host}:{self.port}')

        self.stop()
        self.start()

    @property
    def notebook_file(self):
        return self.__notebook_file

    @property
    def kernel_process(self):
        return self.__kernel_process

    @property
    def name(self):
        return self.__notebook_name

    @property
    def host(self):
        return self.__host

    @property
    def port(self):
        return self.__port

    @property
    def description(self):
        return self.__notebook_description

    @property
    def cwd(self):
        return self.__cwd

    @property
    def kernel_status(self):
        if not self.__kernel_process:
            return "UNKNOWN"
        elif not self.__kernel_process.returncode:
            return "RUNNING"
        else:
            return f"STOPPED ({self.__kernel_process.returncode})"
