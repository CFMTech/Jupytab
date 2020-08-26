# Copyright (c) 2019 Capital Fund Management
# SPDX-License-Identifier: MIT

import numpy as np
import pandas as pd
import json
from timeit import default_timer as timer

import jupytab


def test_data_schema():
    arrays = [
        ['A', 'A',
         'a', 'a',
         0, 0,
         'a$_!#àz', 'a$_!#àz'
         ],
        ['A', 'A',
         0, 1,
         'z$_"_àéça"', 'z_èà[|]a',
         'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789', 'abcdefghijklmnopqrstuvwxyz0123456789'
         ]
    ]
    tuples = list(zip(*arrays))
    index = pd.MultiIndex.from_tuples(tuples, names=['first', 'second'])
    complex_df = pd.DataFrame(np.random.randn(len(index), len(index)), index=index, columns=index)

    tables = jupytab.Tables()
    tables['complex_df_no_index_{}[]#!'] = \
        jupytab.DataFrameTable('A multi-index Dataframe ({}[]#!)',
                               dataframe=complex_df)
    tables['complex_df_with_index_{}[]#!'] = \
        jupytab.DataFrameTable('A multi-index Dataframe ({}[]#!)',
                               dataframe=complex_df,
                               include_index=True)

    schema = tables.schema()

    assert schema[0]['id'] == 'complex_df_no_index_{}[]#!'
    assert schema[0]['alias'] == 'A multi-index Dataframe ({}[]#!)'
    assert schema[1]['id'] == 'complex_df_with_index_{}[]#!'
    assert schema[1]['alias'] == 'A multi-index Dataframe ({}[]#!)'

    raw_output = '[{"id": "complex_df_no_index_{}[]#!", "alias": "A multi-index Dataframe ({}[]#!' \
                 ')", "columns": [{"id": "A_A_1", "dataType": "float"}, {"id": "A_A_2", "dataType' \
                 '": "float"}, {"id": "a_0", "dataType": "float"}, {"id": "a_1", "dataType": "flo' \
                 'at"}, {"id": "0_z____aeca_", "dataType": "float"}, {"id": "0_z_ea_a", "dataType' \
                 '": "float"}, {"id": "a___az_ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789", "dataType": ' \
                 '"float"}, {"id": "a___az_abcdefghijklmnopqrstuvwxyz0123456789", "dataType": "fl' \
                 'oat"}]}, {"id": "complex_df_with_index_{}[]#!", "alias": "A multi-index Datafra' \
                 'me ({}[]#!)", "columns": [{"id": "first_", "dataType": "string"}, {"id": "secon' \
                 'd_", "dataType": "string"}, {"id": "A_A_1", "dataType": "float"}, {"id": "A_A_2' \
                 '", "dataType": "float"}, {"id": "a_0", "dataType": "float"}, {"id": "a_1", "dat' \
                 'aType": "float"}, {"id": "0_z____aeca_", "dataType": "float"}, {"id": "0_z_ea_a' \
                 '", "dataType": "float"}, {"id": "a___az_ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789", ' \
                 '"dataType": "float"}, {"id": "a___az_abcdefghijklmnopqrstuvwxyz0123456789", "da' \
                 'taType": "float"}]}]'

    raw_schema = tables.render_schema(do_print=False)

    assert raw_output == raw_schema


def test_large_data_content():
    row_count = 1000000
    col_count = 10

    np.random.seed(0)

    large_df = pd.DataFrame(np.random.randn(row_count, col_count))
    tables = jupytab.Tables()
    tables['large_df'] = \
        jupytab.DataFrameTable('A very large Dataframe',
                               dataframe=large_df)

    request = json.dumps({
        'args': {
            'table_name': ['large_df'],
            'format': ['json'],
            'from': [5100],
            'to': [5102]
        }
    })

    start = timer()
    raw_data = tables.render_data(request, do_print=False)
    end = timer()

    print(f"Elapsed time in second to retrieve one row in a large dataframe : {(end - start)} s")

    assert (end - start) < 0.1

    print(raw_data)

    assert raw_data == '[{"0":0.2307805099,"1":0.7823326556,"2":0.9507107694,"3":1.4595805778,' \
                       '"4":0.6798091111,"5":-0.8676077457,"6":0.3908489554,"7":1.0838125793,' \
                       '"8":0.6227587338,"9":0.0919146565},{"0":0.6267312321,"1":0.7369835911,' \
                       '"2":-0.4665488934,"3":1.5379716957,"4":-1.0313145219,"5":1.0398963231,' \
                       '"6":0.8687854819,"7":0.2055855947,"8":-1.7716643336,"9":0.2428264886}]'
