# Jupytab

[![CircleCI](https://circleci.com/gh/CFMTech/Jupytab.svg?style=svg)](https://circleci.com/gh/CFMTech/Jupytab)
&nbsp;[![PyPI version](https://badge.fury.io/py/jupytab.svg)](https://badge.fury.io/py/jupytab)
&nbsp;[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Jupytab allows you to **explore in [Tableau](https://www.tableau.com/) data which is generated dynamically by a Jupyter Notebook**. You can thus create Tableau data sources in a very flexible way using all the power of Python. This is achieved by having Tableau access data through a **web server created by Jupytab**.

Jupytab is built on **solid foundations**: Tableau's [Web Data Connector](https://tableau.github.io/webdataconnector/) and the [Jupyter Kernel Gateway](https://github.com/jupyter/kernel_gateway).

## Overview

Features:

* **Expose multiple pandas dataframes** to Tableau from a Jupyter notebook
* Access **several notebooks** from Tableau through a **single entry point** (web server)
* Manage your notebooks using a **web interface**
* **Secure access** to your data

## Examples

You can find the example Jupyter notebooks and Tableau workbooks below are available in the [samples](samples) folder of
the Jupytab project.

### Preparation

If you want to run the example notebooks, it is necessary to define the Jupyter kernel that they run with:
```
python -m ipykernel install --user --name jupytab-demo
```
You can then launch the Jupytab server as instructed below.

### Air Flights

The first example illustrates how Jupytab allows you to **directly display realtime data** in Tableau (without going through the hassle of creating intermediate files or database tables). 
We will display the position and altitude of all planes from the freely available [OpenSky](https://opensky-network.org/) service. (_This service does not show planes currently flying over the 
ocean or uninhabited area!_)

The [AirFlights notebook](samples/air-flights/AirFlights.ipynb) uses the [Requests](https://2.python-requests.org/en/master/) library to **access the OpenSky HTTP Rest API** and then exposes multiple metrics in a dataframe.
The provided [Tableau workbook](samples/air-flights/AirFlights.twb) gives the result below:

![AirFlights](docs/resources/AirFlights.png)

### Real Estate Price, and Crime 

The second example illustrates how simple it is to use Jupytab and **create a custom data source from multiple CSV files**. This is particularly convenient, because there is **no need to configure a new storage area** for these files in Tableau: the data is accessed through Jupytab's web service.

The [example notebook](samples/real-estate_crime/RealEstateCrime.ipynb) exposes real estate and crime data for Sacramento, with a bit of [Pandas](http://pandas.pydata.org/) magic to combine several data sources. 

Thanks to the combination of data in a single dataframe, the [Tableau workbook](samples/air-flights/AirFlights.twb) can automatically show **maps over the same area of the city**:

![RealEstateCrime](docs/resources/RealEstateCrime.png)


# Installation

## Requirements

Python 3.6+ is currently required to run the Jupytab server.

The notebook code itself requires Python 3.6+ too (but it shouldn't be difficult to adapt Jupytab for Python 2).

Jupytab relies on the official [Jupyter Kernel Gateway](https://github.com/jupyter/kernel_gateway).

## Automatic installation

Jupytab and its dependencies can easily be installed through pip:

```
pip install jupytab
```


# Usage 

## Configuration file

You need to create a `config.ini` file in order to tell Jupytab which notebooks contain the tables that should be published for Tableau (this configuration file can be stored anywhere you choose). Here is an example of a working configuration file:

```
[main]
listen_port = 8765
security_token = myToken
notebooks = AirFlights|RealEstateCrime

[AirFlights]
name = Air Flights
directory = samples/air-flights
path = ./AirFlights.ipynb
description = Realtime Flights Visualisation (API)

[RealEstateCrime]
name = RealEstateCrime
directory = samples/real-estate_crime
path = ./RealEstateCrime.ipynb
description = Real Estate Crime (static CSV)
```

There is only one mandatory section, `main`, which contains:

* `listen_port` (mandatory): Numeric port number (it must be available).
* `notebooks` (mandatory): List of notebooks to be executed by Jupytab, provided as a section name in the config file
and separated by the `|` (pipe) symbol. This must be a simple name compliant with [configparser](https://docs.python.org/3/library/configparser.html) sections.
* `security_token` (optional): If provided, an encrypted security token will be required for all exchanges with
Jupytab.
 
Additional sections contain information about each notebook to be run:

* `name` (optional): If provided, replaces the section name by a more friendly notebook name in the Jupytab web interface.
* `directory` (optional): If provided, the notebook will start with `directory` as its working directory instead of the one where the `jupytab` commands is launched (see below).
* `path` (mandatory): Relative (compared to `directory`) or absolute path to your notebook.
* `description` (optional): If provided, adds a description to your notebook in the Jupytab web interface.

Please make sure that the notebook name in the main section is exactly the same as in the section title!

![ConfigSection](docs/resources/ConfigSection.png)

## Notebook preparation

Publishing dataframes from a notebook is simple. Let's start by importing the necessary module:

```python
import pandas as pd

import jupytab
```

### Tables definition

The publication of data sources for Tableau from a notebook is done through two classes:

* Tables: Contains the publication-ready tables provided by the notebook. There is typically a single instance of this class in a given notebook.
* DataFrameTable: Table for either static or dynamic publication in Tableau. Static tables never change on the Tableau side. Dynamic tables are regenerated for each Tableau Extract.

```python
def dynamic_df():
    return pd.DataFrame([[1, 2, 3], [4, 5, 6], [7, 8, 9]], columns=['a', 'b', 'c'])

tables = jupytab.Tables()  # Publication-ready tables contained by this notebook

# Example 1: Static data: it will never change on the Tableau side:
static_df = dynamic_df()
tables['static'] = jupytab.DataFrameTable('A static table', dataframe=static_df)

# Example 2: Dynamic data: a new DataFrame is generated whenever Extract is requested on Tableau's side:
tables['dynamic'] = jupytab.DataFrameTable('A dynamic table', refresh_method=dynamic_df)
```

The tables listed in the Python variables `tables` now need to be explicitly marked for publication by Jupytab (both their schema and their contents). This is typically done at the very end of the notebook, with two special cells.

### Expose tables schema

When Tableau needs to retrieve the schema of all available tables, Jupytab executes the (mandatory) cell that starts with `# GET /schema`:

```python
# GET /schema
tables.render_schema()
```

(`tables.render_schema()` will output a JSON string when executed in the notebook.)

### Expose tables data

When Tableau needs to retrieve the data from tables, Jupytab executes the (mandatory) cell that starts with `# GET /data`:

```python
# GET /data
tables.render_data(REQUEST)
```

(Note that `tables.render_data(REQUEST)` will throw, as expected, `NameError: name 'REQUEST' is not defined` when executed in the notebook: `REQUEST` will only be defined when running with Jupytab, so the error is harmless.)


## Launching the Jupytab dataframe server

Once you have created your notebooks, it should be a matter of second before they become acessible from Tableau.
To start Jupytab, simply run the following command:
```
jupytab --config=config.ini
```
You should see the following ouput, which contains two important pieces of information:

* The list of published notebooks.
* The URL to be used in Tableau in order to access the data (including any security token declared in the configuration file).

```
(install-jupytab) user@localhost:~$ jupytab --config=tests/config.ini
Start notebook ~/tests/resources/rt_flights.ipynb on 127.0.0.1:57149
Start notebook ~/tests/resources/csv_reader.ipynb on 127.0.0.1:53351
Your token is 02014868fe0eef123269397c5bc65a9608b3cedb73e3b84d8d02c220
        Please open : http://localhost:8765/?security_token=02014868fe0eef123269397c5bc65a9608b3cedb73e3b84d8d02c220
INFO:[KernelGatewayApp] Kernel started: 1befe373-aebd-4b31-9f98-2f90f235f255
INFO:[KernelGatewayApp] Kernel started: 365bfdb6-887b-41b4-ad69-309a200f5137
INFO:[KernelGatewayApp] Registering resource: /schema, methods: (['GET'])
INFO:[KernelGatewayApp] Registering resource: /data, methods: (['GET'])
INFO:[KernelGatewayApp] Registering resource: /_api/spec/swagger.json, methods: (GET)
INFO:[KernelGatewayApp] Jupyter Kernel Gateway at http://127.0.0.1:53351
INFO:[KernelGatewayApp] Registering resource: /schema, methods: (['GET'])
INFO:[KernelGatewayApp] Registering resource: /data, methods: (['GET'])
INFO:[KernelGatewayApp] Registering resource: /_api/spec/swagger.json, methods: (GET)
INFO:[KernelGatewayApp] Jupyter Kernel Gateway at http://127.0.0.1:57149
```

## Connect Tableau to your notebooks

Connecting Tableau to your notebooks is simply done by copying the URL provided by Jupytab upon startup to the Tableau Web Data Connector:

![TableauStart](docs/resources/TableauStart.png)

You can now use the Tableau Web Data Connector screen and access your data sources through the Jupytab interface.


## Troubleshooting

If you encounter a any problem when using Jupytab, you can find it useful to check the console where you launched 
Jupytab for diagnostic messages. The console output can in particular be usefully included when you raise a GitHub issue.

# Contact and contributing

Contributions are very welcome.  It can be

- a new GitHub issue,
- a feature request,
- code (see the [Developement Guide](docs/source/development-guide.md)),
- or simply feedback on this project.

The main author of Jupytab is Brian Tribondeau, who can be reached at brian.tribondeau@cfm.fr.

