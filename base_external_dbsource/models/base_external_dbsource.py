# -*- coding: utf-8 -*-
# Copyright 2011 Daniel Reis
# Copyright 2016 LasLabs Inc.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import os
import logging
import warnings
import psycopg2

from contextlib import contextmanager

from openerp import _, api, fields, models, tools
from openerp.exceptions import Warning as UserError

from ..exceptions import ConnectionFailedError, ConnectionSuccessError

_logger = logging.getLogger(__name__)


class BaseExternalDbsource(models.Model):
    """ It provides logic for connection to an external data source

    Classes implementing this interface must provide the following methods
    suffixed with the adapter type. See the method definitions and examples
    for more information:
        * ``connection_open_*``
        * ``connection_close_*``
        * ``execute_*``
    """

    _name = "base.external.dbsource"
    _description = 'External Database Sources'

    CONNECTORS = []

    name = fields.Char('Datasource name', required=True, size=64)
    conn_string = fields.Text('Connection string', help="""
    Sample connection strings:
    - Microsoft SQL Server:
      mssql+pymssql://username:%s@server:port/dbname?charset=utf8
    - MySQL: mysql://user:%s@server:port/dbname
    - ODBC: DRIVER={FreeTDS};SERVER=server.address;Database=mydb;UID=sa
    - ORACLE: username/%s@//server.address:port/instance
    - PostgreSQL:
        dbname='template1' user='dbuser' host='localhost' port='5432' \
        password=%s
    - SQLite: sqlite:///test.db
    - Elasticsearch: https://user:%s@localhost:9200
    """)
    conn_string_full = fields.Text(
        readonly=True,
        compute='_compute_conn_string_full',
    )
    password = fields.Char('Password', size=40)
    client_cert = fields.Text()
    client_key = fields.Text()
    ca_certs = fields.Char(
        help='Path to CA Certs file on server.',
    )
    connector = fields.Selection(CONNECTORS, 'Connector', required=True,
                                 help="If a connector is missing from the\
                                      list, check the server log to confirm\
                                      that the required components were\
                                      detected.")

    @api.multi
    def _compute_conn_string_full(self):
        for record in self:
            if record.password:
                if '%s' not in record.conn_string:
                    record.conn_string += ';PWD=%s'
                record.conn_string = record.conn_string % self.password

    # Interface

    @api.multi
    @contextmanager
    def connection_open(self):
        """ It provides a context manager for the data source 

        This method calls adapter method of this same name, suffixed with
        the adapter type.
        """

        method = self._get_adapter_method('connection_open')
        try:
            connection = method()
            yield connection
        finally:
            try:
                self.connection_close(connection)
            except:
                _logger.exception('Connection close failure.')

    @api.multi
    def connection_close(self, connection):
        """ It closes the connection to the data source.

        This method calls adapter method of this same name, suffixed with
        the adapter type.
        """

        method = self._get_adapter_method('connection_close')
        return method(connection)

    @api.multi
    def execute(self, query=None, execute_params=None, metadata=False, **kwargs):
        """ Executes a query and returns a list of rows.

            "execute_params" can be a dict of values, that can be referenced
            in the SQL statement using "%(key)s" or, in the case of Oracle,
            ":key".
            Example:
                query = "select * from mytable where city = %(city)s and
                            date > %(dt)s"
                params   = {'city': 'Lisbon',
                            'dt': datetime.datetime(2000, 12, 31)}

            If metadata=True, it will instead return a dict containing the
            rows list and the columns list, in the format:
                { 'cols': [ 'col_a', 'col_b', ...]
                , 'rows': [ (a0, b0, ...), (a1, b1, ...), ...] }
        """

        # Old API compatibility
        if not query:
            try:
                query = kwargs['sqlquery']
            except KeyError:
                raise TypeError('query is a required argument')
        if not execute_params:
            try:
                execute_params = kwargs['sqlparams']
            except KeyError:
                pass

        method = self._get_adapter_method('execute')
        rows, cols = method(sqlquery, sqlparams, metadata, execute_params)
        if metadata:
            return{'cols': cols, 'rows': rows}
        else:
            return rows

    @api.multi
    def connection_test(self):
        """ It tests the connection

        Raises:
            ConnectionSuccessError: On connection success
            ConnectionFailedError: On connection failed
        """

        for obj in self:
            conn = False
            try:
                with self.connection_open():
                    pass
            except Exception as e:
                raise ConnectionFailedError(_(
                    "Connection test failed:\n"
                    "Here is what we got instead:\n%s"
                ) % tools.ustr(e))
        raise ConnectionSuccessError(_(
            "Connection test succeeded:\n"
            "Everything seems properly set up!",
        ))

    # Adapters

    # SQLAlchemy

    def connection_close_mssql(self):
        return connection.close()

    def connection_open_mssql(self):
        return self._connection_open_sqlalchemy()

    def execute_mssql(self, sqlquery, sqlparams, metadata):
        return self._execute_sqlalchemy(sqlquery, sqlparams, metadata)

    def connection_close_mysql(self):
        return connection.close()

    def connection_open_mysql(self):
        return self._connection_open_sqlalchemy()

    def execute_mysql(self, sqlquery, sqlparams, metadata):
        return self._execute_sqlalchemy(sqlquery, sqlparams, metadata)

    def connection_close_sqlite(self):
        return connection.close()

    def connection_open_sqlite(self):
        return self._connection_open_sqlalchemy()

    def execute_sqlite(self, sqlquery, sqlparams, metadata):
        return self._execute_sqlalchemy(sqlquery, sqlparams, metadata)

    def _connection_open_sqlalchemy(self):
        return sqlalchemy.create_engine(self.conn_string_full).connect()

    def _execute_sqlalchemy(self, sqlquery, sqlparams, metadata):
        rows, cols = list(), list()
        for record in self:
            with record.connection_open() as connection:
                cur = conn.execute(sqlquery, sqlparams)
                if metadata:
                    cols = cur.keys()
                rows = [r for r in cur]
        return

    # Others

    def connection_close_cx_Oracle(self, connection):
        return connection.close()

    def connection_open_cx_Oracle(self):
        os.environ['NLS_LANG'] = 'AMERICAN_AMERICA.UTF8'
        conn = cx_Oracle.connect(self.conn_string_full)

    def execute_cx_Oracle(self, sqlquery, sqlparams, metadata):
        return self._execute_other(sqlquery, sqlparams, metadata)

    def connection_close_pyodbc(self, connection):
        return connection.close()

    def connection_open_pyodbc(self):
        return pyodbc.connect(self.conn_string_full)

    def execute_pyodbc(self, sqlquery, sqlparams, metadata):
        return self._execute_other(sqlquery, sqlparams, metadata)

    def connection_close_postgresql(self, connection):
        return connection.close()

    def connection_open_postgresql(self):
        return psycopg2.connect(self.conn_string)

    def execute_postgresql(self, sqlquery, sqlparams, metadata):
        return self._execute_other(sqlquery, sqlparams, metadata)

    def _execute_other(self, sqlquery, sqlparams, metadata):
        with self.connection_open() as connection:
            cur = connection.cursor()
            cur.execute(sqlquery, sqlparams)
            if metadata:
                cols = [d[0] for d in cur.description]
            rows = cur.fetchall()

    # Elasticsearch

    def connection_close_elasticsearch(self, connection):
        return True

    def connection_open_elasticsearch(self):
        kwargs = {}
        if self.ca_certs:
            kwargs['ca_certs'] = self.ca_certs
            if self.client_cert and self.client_key:
                kwargs.update({
                    'client_cert': self.client_cert,
                    'client_key': self.client_key,
                })
        return Elasticsearch(
            [self.conn_string_full],
            **kwargss
        )

    def execute_elasticsearch(self, query, params, metadata):
        if not params['index']:
            raise KeyError(_(
                '`index` is a required key in `params` for Elasticsearch.',
            ))

    # Compatibility & Private

    @api.multi
    def conn_open(self):
        """ It opens and returns a connection to the remote data source.

        This method calls adapter method of this same name, suffixed with
        the adapter type.

        Deprecate:
            This method has been replaced with ``connection_open``.
        """

        return self.connection_open()

    def _get_adapter_method(self, method_prefix):
        """ It returns the connector adapter method for ``method_prefix``.

        Args:
            method_prefix: (str) Prefix of adapter method (such as
                ``connection_open``).
        Raises:
            NotImplementedError: When the method is not found
        Returns:
            (instancemethod)
        """

        self.ensure_one()
        method = '%s_%s' % (method_prefix, self.connector)

        try:
            method = getattr(self, method)
        except AttributeError:
            raise NotImplementedError(_(
                '"%s" method not found, check that all assets are installed '
                'for the %s connector type.'
            )) % (
                method, self.connector,
            )
