# Copyright (c) 2019 Capital Fund Management
# SPDX-License-Identifier: MIT

import json
import re
import unicodedata
from collections import Counter

import pandas as pd


class BaseTable:
    """
    Abstract class with default methods to be implemented, that represents a table-like object that
    can be used by Jupytab. DataFrames, SQL queries, CSV files... could be implemented as BaseTable
    child classes.
    """

    def __init__(self, alias):
        """
        alias -- A descriptive name of the table that will be displayed in Tableau.
        """
        self._alias = alias

    @property
    def alias(self):
        """
        A descriptive name for the Table.
        """
        return self._alias

    def get_schema(self, key):
        """
        Provide a table schema for Jupytab.

        Returns a dictionary that describes the table provided by the schema:
        {
            "id": :obj:`str`
            "alias": :obj:`str`
            "columns" :obj:`list`
        }

        key -- A uniquely identified schema.
        """
        raise NotImplementedError

    def refresh(self, only_if_undefined=False):
        """
        Refresh the table if an available refresh method is available.

        only_if_undefined -- true for refreshing only if there is no data currently available.
        """
        raise NotImplementedError

    def to_json(self):
        """
        Return the table contents as a JSON object.
        """
        raise NotImplementedError


class DataFrameTable(BaseTable):
    """
    This class represents a jupytab-ready table that exposes a Pandas DataFrame.
    """

    def __init__(self, alias, dataframe=None, refresh_method=None, include_index=False):
        """
        alias -- Descriptive name of the table, that will be displayed in Tableau.

        dataframe -- Pandas DataFrame to be accessed from Tableau (may be None if a
        refresh_method is provided).

        refresh_method -- Optional method callback that will be called every time
        Tableau needs to access the data (for instance when the DataSource is refreshed).
        It takes no argument and must return a DataFrame with the same column layout
        (schema) as the original DataFrame (if any).

        include_index -- Add Index as column(s) in the output data to Tableau.
        """
        BaseTable.__init__(self, alias=alias)

        self._dataframe = dataframe
        self._refresh_method = refresh_method
        self._include_index = include_index
        self._index_separator = '_'

        self.types_mapping = {
            'object': 'string',
            'int64': 'int',
            'float64': 'float',
            'datetime64[ns]': 'datetime',
            'bool': 'bool'
        }

    @staticmethod
    def clean_column_name(col):
        """Remove all forbidden characters from column names"""

        # Try to preserve accented characters
        cleaned_col = unicodedata.normalize('NFD', str(col)) \
            .encode('ascii', 'ignore') \
            .decode("utf-8")
        # Remove all non matching chars for Tableau WDC
        cleaned_col = re.sub(r'[^A-Za-z0-9_]+', '_', cleaned_col)
        return cleaned_col

    @staticmethod
    def replace_duplicated_column_name(cols):
        """Replace duplicated columns names"""
        cols_count_dict = dict(Counter(cols))
        # Filter unique items
        cols_count_dict = {key: value for (key, value) in cols_count_dict.items() if value > 1}
        unique_cols = list()
        for col in reversed(cols):
            idx = cols_count_dict.get(col, 0)
            unique_cols.insert(0, col if idx == 0 else col + '_' + str(idx))
            cols_count_dict[col] = idx - 1
        return unique_cols

    def get_schema(self, key):
        self.refresh(only_if_undefined=True)

        columns = [
            {
                'id': '.'.join(filter(None, key)) if isinstance(key, tuple) else key,
                'dataType':
                    self.types_mapping[str(value)] if str(value) in self.types_mapping else 'string'
            }
            for key, value in (self._prepare_dataframe()).dtypes.items()
        ]

        return {
            'id': key,
            'alias': self._alias,
            'columns': columns
        }

    def _prepare_dataframe(self):
        # Remove index if it is not required
        prep_df = self._dataframe \
            if self._include_index \
            else self._dataframe.reset_index(drop=True)
        # Flatten multi-index
        if isinstance(prep_df.columns, pd.MultiIndex):
            prep_df.columns = [self._index_separator.join(map(str, col)).strip()
                               for col in prep_df.columns.values]

        prep_df.columns = [DataFrameTable.clean_column_name(col) for col in prep_df.columns]
        prep_df.columns = DataFrameTable.replace_duplicated_column_name(prep_df.columns)

        return prep_df

    def refresh(self, only_if_undefined=False):
        # If DataFrame exists and it is not requested to update it then we do not need to refresh.
        # Otherwise if a refresh method has been set it is required to update the DataFrame.
        if (not only_if_undefined or self._dataframe is None) and self._refresh_method is not None:
            self._dataframe = self._refresh_method()

    def to_json(self):
        return self._prepare_dataframe() \
            .to_json(orient='records', date_format="iso", date_unit="s")


class Tables:
    """
    Table manager exposed as a dictionary to keep track of all registered tables and create a
    combined schema.
    """

    def __init__(self, *args):
        self.tables = {}

    def __setitem__(self, key, value):
        assert isinstance(value, BaseTable)
        self.tables[key.lower()] = value

    def __getitem__(self, key):
        return self.tables[key.lower()]

    def schema(self):
        """
        Return a list of all registered table schemas.
        """
        return [value.get_schema(key) for key, value in self.tables.items()]

    def render_schema(self, do_print=True):
        """
        Return the JSON with the table schemas or None (if it is printed [default]).

        To be used in the notebook in a single cell like the code provided below:

        ```
        # GET /schema
        tables.render_schema()
        ```

        This will generate a string in the cell output that Jupytab will be able to use.

        do_print -- If true, do not return the JSON object but print it instead.
        """
        rendered_schema = json.dumps(self.schema())
        if do_print:
            print(rendered_schema)
        else:
            return rendered_schema

    def render_data(self, request, do_print=True):
        """
        Return JSON with the table data or None (if it is printed [default]).

        To be used in the notebook in a single cell like the code provided below:

        ```
        # GET /data
        tables.render_data()
        ```

        This will generate a string in the cell output that Jupytab will be able to use.

        do_print -- If true, do not return the JSON object but print it instead.
        """
        table_name = json.loads(request)['args']['table_name'][0]
        table = self[table_name]
        table.refresh()
        rendered_data = table.to_json()
        if do_print:
            print(rendered_data)
        else:
            return rendered_data
