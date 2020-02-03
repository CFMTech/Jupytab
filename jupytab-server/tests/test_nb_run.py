import asyncio
import os
import threading
import time
from json.decoder import JSONDecodeError

import pytest
import requests
from tornado.ioloop import IOLoop

from jupytab_server.jupytab import parse_config, create_server_app

THIS_DIR = os.path.abspath(os.path.dirname(__file__))
RESOURCES = os.path.abspath(os.path.join(THIS_DIR, '..'))

PROTOCOL = "http"
HOST = "127.0.0.1"
PORT = "8765"
SECURITY_TOKEN = "02014868fe0eef123269397c5bc65a9608b3cedb73e3b84d8d02c220"

event_loop_instance = None


def run_jupytab():
    # Required as we run the server in a new thread
    asyncio.set_event_loop(asyncio.new_event_loop())
    os.chdir(os.path.abspath(RESOURCES))

    params = parse_config(config_file="samples/config.ini")

    server_app = create_server_app(**params)
    server_app.listen(params['listen_port'])

    global event_loop_instance
    event_loop_instance = IOLoop.instance()
    event_loop_instance.start()


@pytest.fixture(scope='session', autouse=True)
def setup_jupytab():
    # Setup
    thread = threading.Thread(target=run_jupytab)
    thread.daemon = True
    thread.start()

    yield

    # Teardown
    global event_loop_instance
    # Cleanly shutdown the event loop used for testing server
    event_loop_instance.add_callback(event_loop_instance.stop)


def build_uri(uri, params=None, protocol=PROTOCOL, host=HOST, port=PORT, token=SECURITY_TOKEN):
    token = f"security_token={token}" if token else ""
    return f"{protocol}://{host}:{port}/{uri}?{token}&{params}"


def retry(uri, delay_seconds=5, attempt_count=6):
    for attempt in range(attempt_count):
        try:
            response = requests.get(uri)
            if response.status_code == 200:
                return response.json()
        except requests.exceptions.RequestException as e:
            print("RequestException", e)
        except JSONDecodeError as e:
            print("JSONDecodeError", e)

        time.sleep(delay_seconds)

    raise ConnectionError("Unable to retrieve datas from provided web service")


def test_airflights_schema():
    response = retry(build_uri("kernel/AirFlights/schema"))

    json_result = response

    assert json_result[0]['id'] == 'flights'
    assert json_result[0]['columns'][0]['id'] == "callsign"
    assert json_result[0]['columns'][8]['id'] == "velocity"
    assert json_result[0]['columns'][8]['dataType'] == "float"

    assert len(json_result[0]['columns']) == 16


def test_airflights_data():
    response = retry(build_uri("kernel/AirFlights/data", "table_name=flights"))

    json_result = response

    assert len(json_result) > 0
    assert 'callsign' in json_result[0]
    assert 'time_position' in json_result[0]
    assert 'baro_altitude' in json_result[0]


def test_realestatecrime_data():
    response = retry(build_uri("kernel/RealEstateCrime/data", "table_name=combined"))

    json_result = response

    assert len(json_result) > 0
    assert 'address' in json_result[0]
    assert 'beat' in json_result[0]
    assert 'city' in json_result[0]


def test_realestatecrime_schema():
    response = retry(build_uri("kernel/RealEstateCrime/schema"))

    json_result = response

    assert json_result[0]['id'] == 'crime'
    assert len(json_result[0]['columns']) == 9
    assert json_result[0]['columns'][3]['id'] == 'beat'
    assert json_result[1]['id'] == 'real_estate'
    assert len(json_result[1]['columns']) == 12
    assert json_result[1]['columns'][1]['id'] == 'city'
    assert json_result[1]['columns'][1]['dataType'] == 'string'
    assert json_result[2]['id'] == 'combined'
    assert len(json_result[2]['columns']) == 19
    assert json_result[2]['columns'][1]['id'] == 'baths'
    assert json_result[2]['columns'][1]['dataType'] == 'float'
