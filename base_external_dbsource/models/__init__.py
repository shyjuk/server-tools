# -*- coding: utf-8 -*-
from . import base_external_dbsource

CONNECTORS = base_external_dbsource.BaseExternalDbsource.CONNECTORS

try:
    import sqlalchemy
    CONNECTORS.append(('sqlite', 'SQLite'))
    try:
        import pymssql
        CONNECTORS.append(('mssql', 'Microsoft SQL Server'))
        assert pymssql
    except (ImportError, AssertionError):
        _logger.info('MS SQL Server not available. Please install "pymssql"\
                      python package.')
    try:
        import MySQLdb
        CONNECTORS.append(('mysql', 'MySQL'))
        assert MySQLdb
    except (ImportError, AssertionError):
        _logger.info('MySQL not available. Please install "mysqldb"\
                     python package.')
except ImportError:
    _logger.info('SQL Alchemy not available. Please install "slqalchemy"\
                 python package.')
try:
    import pyodbc
    CONNECTORS.append(('pyodbc', 'ODBC'))
except ImportError:
    _logger.info('ODBC libraries not available. Please install "unixodbc"\
                 and "python-pyodbc" packages.')

try:
    import cx_Oracle
    CONNECTORS.append(('cx_Oracle', 'Oracle'))
except ImportError:
    _logger.info('Oracle libraries not available. Please install "cx_Oracle"\
                 python package.')

try:
    from elasticsearch import Elasticsearch
    CONNECTORS.append(('elasticsearch', 'Elasticsearch'))
except ImportError:
    _logger.info('Elasticsearch library not available. Please install '
                 '"elasticsearch" python package.')

CONNECTORS.append(('postgresql', 'PostgreSQL'))
