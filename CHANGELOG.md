# Changelog

## 0.9.11 - (2020-09-11)
* #45 Add jupytab.__version__ and jupytab_server.__version__ to diagnose version easily + display at start
* #44 Remove tests packages from released artifact
* #43 Fix TabPy protocol that changes with version 2020.1+ of Tableau

## 0.9.10 - (2020-08-26)
* #18 Use pagination to transfer data, in order to allow huge dataframe (>10M rows)
* #41 Tableau stuck on Creating Extract (Loading data...) for slow retrieved tables

## 0.9.9 - (2020-06-26)
* Internal version for conda packaging (no code change)

## 0.9.8 (2020-06-26)
* #38 Rework version integration for packaging purpose

## 0.9.7 (2020-05-28)
* #14 TabPy / External Service compatibility to add on the fly computation

## 0.9.5 (2020-03-24)
* #24 Quick-fix for SSL support

## 0.9.4 (2020-03-23)
* #24 Add support for SSL

## 0.9.3 (2020-02-25)
* Fix incorrect release on pypi following jupytab split

## 0.9.2 (2020-02-24)
* #19 Create a tool library for jupytab, allowing separated download for jupytab util
* #7 Jupytab must be install in kernel as no-deps
* #16 notebook.js use parent path instead of same level path

## 0.9.1 (2019-12-23)
* #3 Multiindex column dataframe fails in Tableau
* #8 Jupytab not working on windows
* #10 Improve Table column name management
* #11 Add option to export also index from dataframe

## 0.9.0 (2019-06-30)
* Jupytab public release
