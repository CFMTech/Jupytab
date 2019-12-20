# Copyright (c) 2019 Capital Fund Management
# SPDX-License-Identifier: MIT

import numpy as np
import pandas as pd

from jupytab import Tables, DataFrameTable


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

    tables = Tables()
    tables['complex_df_no_index_{}[]#!'] = \
        DataFrameTable('A multi-index Dataframe ({}[]#!)',
                       dataframe=complex_df)
    tables['complex_df_with_index_{}[]#!'] = \
        DataFrameTable('A multi-index Dataframe ({}[]#!)',
                       dataframe=complex_df,
                       include_index=True)

    schema = tables.schema()

    assert schema[0]['id'] == 'complex_df_no_index_{}[]#!'
    assert schema[0]['alias'] == 'A multi-index Dataframe ({}[]#!)'
    assert schema[1]['id'] == 'complex_df_with_index_{}[]#!'
    assert schema[1]['alias'] == 'A multi-index Dataframe ({}[]#!)'

    raw_output = '[{"id": "complex_df_no_index_{}[]#!", "alias": "A multi-index Dataframe ({}[]#!)", "columns": [{"id": "A_A_2", "dataType": "float"}, {"id": "A_A", "dataType": "float"}, {"id": "a_0", "dataType": "float"}, {"id": "a_1", "dataType": "float"}, {"id": "0_z____aeca_", "dataType": "float"}, {"id": "0_z_ea_a", "dataType": "float"}, {"id": "a___az_ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789", "dataType": "float"}, {"id": "a___az_abcdefghijklmnopqrstuvwxyz0123456789", "dataType": "float"}]}, {"id": "complex_df_with_index_{}[]#!", "alias": "A multi-index Dataframe ({}[]#!)", "columns": [{"id": "A_A_2", "dataType": "float"}, {"id": "A_A", "dataType": "float"}, {"id": "a_0", "dataType": "float"}, {"id": "a_1", "dataType": "float"}, {"id": "0_z____aeca_", "dataType": "float"}, {"id": "0_z_ea_a", "dataType": "float"}, {"id": "a___az_ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789", "dataType": "float"}, {"id": "a___az_abcdefghijklmnopqrstuvwxyz0123456789", "dataType": "float"}]}]' #noqa

    raw_schema = tables.render_schema(do_print=False)

    assert raw_output == raw_schema
