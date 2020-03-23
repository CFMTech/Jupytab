from configparser import ConfigParser

import pytest

from jupytab_server.jupytab import config_ssl


def config(config_file):
    config = ConfigParser()
    config.optionxform = str
    config.read(config_file)
    return config


def test_ssl():
    with pytest.raises(FileNotFoundError):
        config_ssl(config('config/ssl_bad_file.ini'))
    assert config_ssl(config('config/ssl_disabled.ini')) == None
    assert config_ssl(config('config/ssl_none.ini')) == None
    assert config_ssl(config('config/ssl_ok.ini')) == {'certfile': 'config/example.cert',
                                                       'keyfile': 'config/example.key'}
