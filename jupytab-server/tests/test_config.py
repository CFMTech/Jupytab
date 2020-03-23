import os
from configparser import ConfigParser

import pytest

from jupytab_server.jupytab import config_ssl

dir_path = os.path.dirname(os.path.realpath(__file__))
config_path = os.path.join(dir_path, 'config')


def config(config_file):
    config = ConfigParser()
    config.optionxform = str
    config.read(config_file)
    return config


def test_ssl():
    def config_exec(config_file):
        return config_ssl(config(os.path.join(config_path, config_file)))

    with pytest.raises(FileNotFoundError):
        config_exec('ssl_bad_file.ini')
    assert config_exec('ssl_disabled.ini') == None
    assert config_exec('ssl_none.ini') == None
    assert config_exec('ssl_ok.ini') == {'certfile': 'config/example.cert',
                                         'keyfile': 'config/example.key'}
