# -*- coding: utf-8 -*-
# Copyright 2016-2017 LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

import logging

from odoo import api, fields, models

_logger = logging.getLogger(__name__)

try:
    import paramiko
except ImportError:
    _logger.info('`paramiko` Python library is not installed')


class ConnectorSftp(models.Model):
    _name = 'connector.sftp'
    _description = 'SFTP Connector'

    name = fields.Char(
        required=True,
    )
    host = fields.Char(
        required=True,
    )
    port = fields.Integer(
        required=True,
        default=22,
    )
    username = fields.Char(
        required=True,
    )
    password = fields.Char()
    private_key = fields.Text()
    host_key = fields.Text()
    ignore_host_key = fields.Boolean()
    company_id = fields.Many2one(
        string='Company',
        comodel_name='res.company',
        inverse_name='sftp_connector_ids',
        required=True,
    )
    transport = fields.Binary(
        compute='_compute_client_and_transport',
    )
    client = fields.Binary(
        compute='_compute_client_and_transport',
    )

    _sql_constraints = [
        ('name_uniq', 'UNIQUE(name)', 'Connection name must be unique.'),
    ]

    @api.multi
    @api.depends('host',
                 'host_key',
                 'password',
                 'port',
                 'private_key',
                 'username',
                 )
    def _compute_client_and_transport(self):
        """Establish SSH Transport and SFTP client.

        Raises:
            paramiko.SSHException: if the SSH2 negotiation fails,
            the host key supplied by the server is incorrect, or
            authentication fails.
        """
        for record in self:
            record.transport = paramiko.Transport((
                record.host, record.port,
            ))
            if record.ignore_host_key:
                host_key = None
            else:
                host_key = record.host_key if record.host_key else None
            record.transport.connect(
                hostkey=host_key,
                username=record.username,
                password=record.password,
                pkey=record.private_key if record.private_key else None,
            )
            record.client = paramiko.SFTPClient.from_transport(
                record.transport,
            )

    @api.multi
    def list_dir(self, path):
        """Return a list containing the names of the entries in ``path``

        The list is in arbitrary order. It does not include the special
        entries ``'.'`` and ``'..'`` even if they are present in the folder.
        This method is meant to mirror the ``os.listdir`` as closely as
        possible.

        Params:
            path (str): Path to list

        Returns:
            list: of names in path
        """
        self.ensure_one()
        return self.client.listdir(path)

    @api.multi
    def stat(self, path):
        """Retrieve information about a file on remote system. Return value is
        an obj whose attributes correspond to the structure of the stdlib
        ``os.stat``, except that it may be lacking fields due to SFTP server
        configuration.

        Unlike a Python stat object, the result may not be accessed as a tuple.
        This is mostly due to the author’s slack factor.

        The fields supported are: ``st_mode``, ``st_size``, ``st_uid``,
        `st_gid``, ``st_atime``, and ``st_mtime``.

        Params:
            path (str): Filename to stat

        Returns:
            paramiko.SFTPAttributes: object containing attributes about file.
        """
        self.ensure_one()
        return self.client.stat(path)

    @api.multi
    def open(self, file_name, mode='r', buff_size=-1):
        """Open file on remote server. Mimicks python open function, and result
        can be used as a context manager.

        Params:
            file_name (str): File to open
            mode (str); How to open file, reference Python open
            buff_size (int): Desired buffering

        Returns:
            paramiko.SFTPFile object: representing the open file

        Raises:
            IOError: if the file cannot be opened
        """
        self.ensure_one()
        return self.client.open(file_name, mode, buff_size)

    @api.multi
    def delete(self, path):
        """Remove the file at the given path. Does not work on directories.

        Params:
            path (str): Path of file to delete.

        Raises:
            IOError: if path refers to a directory.
        """
        self.ensure_one()
        return self.client.unlink(path)

    @api.multi
    def symlink(self, source, dest):
        """Create a symbolic link of the source path at destination on remote.

        Params:
            source (str): Path of original file
            dest (str): Path of new symlink
        """
        self.ensure_one()
        return self.client.symlink(source, dest)
