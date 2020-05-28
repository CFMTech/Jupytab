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


def rget(uri, delay_seconds=5, attempt_count=6):
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

    raise ConnectionError(f"Unable to retrieve GET datas from {uri}")


def rpost(uri, body, delay_seconds=5, attempt_count=6):
    for attempt in range(attempt_count):
        try:
            response = requests.post(uri, json=body)
            if response.status_code == 200:
                return response.json()
        except requests.exceptions.RequestException as e:
            print("RequestException", e)
        except JSONDecodeError as e:
            print("JSONDecodeError", e)

        time.sleep(delay_seconds)

    raise ConnectionError(f"Unable to retrieve POST datas from {uri}")


def get_table_by_id(tables, id):
    for table in tables:
        if table['id'] == id:
            return table
    return None


def get_column_by_id(columns, id):
    for column in columns:
        if column['id'] == id:
            return column
    return None


def test_airflights_schema():
    response = rget(build_uri("kernel/AirFlights/schema"))

    json_result = response

    flight_table = get_table_by_id(json_result, 'flights')
    assert get_column_by_id(flight_table['columns'], "callsign") is not None
    velocity = get_column_by_id(flight_table['columns'], "velocity")
    assert velocity['dataType'] == "float"

    assert len(json_result[0]['columns']) == 16


def test_airflights_data():
    response = rget(build_uri("kernel/AirFlights/data", "table_name=flights"))

    json_result = response

    assert len(json_result) > 0
    assert 'callsign' in json_result[0]
    assert 'time_position' in json_result[0]
    assert 'baro_altitude' in json_result[0]


def test_realestatecrime_schema():
    response = rget(build_uri("kernel/RealEstateCrime/schema"))

    json_result = response

    crime_table = get_table_by_id(json_result, 'crime')
    assert len(crime_table['columns']) == 9
    assert get_column_by_id(crime_table['columns'], 'beat') is not None

    real_estate_table = get_table_by_id(json_result, 'real_estate')
    assert len(real_estate_table['columns']) == 12
    city = get_column_by_id(real_estate_table['columns'], 'city')
    assert city['dataType'] == 'string'

    combined = get_table_by_id(json_result, 'combined')
    assert len(combined['columns']) == 19
    baths = get_column_by_id(real_estate_table['columns'], 'baths')
    assert baths['dataType'] == 'int'


def test_realestatecrime_data():
    response = rget(build_uri("kernel/RealEstateCrime/data", "table_name=combined"))

    json_result = response

    assert len(json_result) > 0
    assert 'address' in json_result[0]
    assert 'beat' in json_result[0]
    assert 'city' in json_result[0]


def test_sklearn_classifier_schema():
    response = rget(build_uri("kernel/SKLearnClassifier/schema"))

    json_result = response

    assert len(json_result) == 3

    assert get_table_by_id(json_result, 'iris_target') is not None


def test_sklearn_classifier_data():
    response = rget(build_uri("kernel/SKLearnClassifier/data", "table_name=iris"))

    json_result = response

    assert len(json_result) > 100
    assert len(json_result[0]) == 5


def test_sklearn_classifier_function():
    predict_function = {
        "script": "SKLearnClassifier.predict",
        "data": {
            "_arg1": [5.1, 5.8, 6.5],
            "_arg2": [3.5, 2.6, 3],
            "_arg3": [1.4, 4, 5.5],
            "_arg4": [0.2, 1.2, 2.4],
        }
    }

    response = rpost(build_uri("evaluate"), predict_function)

    assert response == ["setosa", "versicolor", "virginica"]
