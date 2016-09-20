# -*- coding: utf-8 -*-
# Copyright 2016 LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from openerp import models, api, fields


class DockerMount(models.Model):
    _name = 'docker.mount'
    _description = 'Docker Mount'

    server_id = fields.Many2one(
        string='Server',
        comodel_name='docker.server',
    )
    container_ids = fields.Many2many(
        string='Containers',
        comodel_name='docker.container',
        domain="[('server_id', '=', server_id)]",
    )
    
