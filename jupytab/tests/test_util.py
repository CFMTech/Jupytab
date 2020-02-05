# Copyright (c) 2019 Capital Fund Management
# SPDX-License-Identifier: MIT

import os

import pandas as pd
import jupytab

THIS_DIR = os.path.abspath(os.path.dirname(__file__))
RESOURCES = os.path.join(THIS_DIR, 'resources')


def test_data_schema():
    crime_df = pd.read_csv(os.path.join(RESOURCES, 'sacramento_crime.csv'))
    realestate_df = pd.read_csv(os.path.join(RESOURCES, 'sacramento_realestate.csv'))

    tables = jupytab.Tables()
    tables['sacramento_crime'] = \
        jupytab.DataFrameTable('Sacramento Crime', dataframe=crime_df)
    tables['sacramento_realestate'] = \
        jupytab.DataFrameTable('Sacramento RealEstate', dataframe=realestate_df)

    schema = tables.schema()

    assert schema[0]['id'] == 'sacramento_crime'
    assert schema[0]['alias'] == 'Sacramento Crime'
    columns = schema[0]['columns']
    assert len(columns) == 9

    raw_output = '[{"id": "sacramento_crime", "alias": "Sacramento Crime", "columns": [{"id": "cdat\
etime", "dataType": "string"}, {"id": "address", "dataType": "string"}, {"id": "district", "dataTyp\
e": "int"}, {"id": "beat", "dataType": "string"}, {"id": "grid", "dataType": "int"}, {"id": "crimed\
escr", "dataType": "string"}, {"id": "ucr_ncic_code", "dataType": "int"}, {"id": "latitude", "dataT\
ype": "float"}, {"id": "longitude", "dataType": "float"}]}, {"id": "sacramento_realestate", "alias"\
: "Sacramento RealEstate", "columns": [{"id": "street", "dataType": "string"}, {"id": "city", "data\
Type": "string"}, {"id": "zip", "dataType": "int"}, {"id": "state", "dataType": "string"}, {"id": "\
beds", "dataType": "int"}, {"id": "baths", "dataType": "int"}, {"id": "sq__ft", "dataType": "int"},\
 {"id": "type", "dataType": "string"}, {"id": "sale_date", "dataType": "string"}, {"id": "price", "\
dataType": "int"}, {"id": "latitude", "dataType": "float"}, {"id": "longitude", "dataType": "float"\
}]}]'

    assert raw_output == tables.render_schema(do_print=False)


def test_clean_column_name():
    assert jupytab.DataFrameTable\
               .clean_column_name(['abéçpo$ù"', 0, 'AaZz_#"\\']) == "_abecpo_u_0_AaZz__"


def test_replace_duplicated_column_name():
    assert jupytab.DataFrameTable.replace_duplicated_column_name(['A', 'A', 'a', 'z', 'a', 'Y']) \
           == ['A_1', 'A_2', 'a_1', 'z', 'a_2', 'Y']
