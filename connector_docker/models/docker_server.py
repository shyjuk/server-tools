# -*- coding: utf-8 -*-
# Copyright 2016 LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from openerp import models, api, fields

try:
    from docker import Client
except ImportError:
    pass


class DockerServer(models.Model):
    _name = 'docker.server'
    _description = 'Docker Server'

    base_uri = fields.Char(
        required=True,
        default="unix://var/run/docker.sock",
    )
    timeout = fields.Integer(
        required=True,
        default=30,
    )
    user_agent = fields.Char(
        required=True,
        default='LasLabs',
    )
    version = fields.Char(
        required=True,
        default='auto',
    )

    @property
    @api.multi
    def client(self):
        self.ensure_one()
        return Client(
            base_url=self.base_uri,
            version=self.version,
            timeout=self.timeout,
            user_agent=self.user_agent,
        )
