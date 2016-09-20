# -*- coding: utf-8 -*-
# Copyright 2016 LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from openerp import models, api, fields


class DockerNetwork(models.Model):
    _name = 'docker.network'
    _description = 'Docker Network'

    server_id = fields.Many2one(
        string='Server',
        comodel_name='docker.server',
    )
    container_ids = fields.Many2many(
        string='Containers',
        comodel_name='docker.container',
        inverse_name='network_ids',
    )
    driver_id = fields.Many2one(
        string='Driver',
        comodel_name='docker.network.driver',
    )
    enable_ipv6 = fields.Boolean()
