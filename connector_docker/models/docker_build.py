# -*- coding: utf-8 -*-
# Copyright 2016 LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from openerp import models, api, fields


class DockerBuild(models.Model):
    _name = 'docker.build'
    _description = 'Docker Build'

    server_id = fields.Many2one(
        string='Server',
        comodel_name='docker.server',
    )
    file_id = fields.Many2one(
        string='File',
        comodel_name='docker.file',
    )
    file_carbon = fields.Text(
        help='Carbon copy of the DockerFile used during build.',
    )
