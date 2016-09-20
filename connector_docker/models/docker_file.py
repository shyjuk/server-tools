# -*- coding: utf-8 -*-
# Copyright 2016 LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from openerp import models, api, fields


class DockerFile(models.Model):
    _name = 'docker.file'
    _description = 'Docker File'

    uri = fields.Char(
        required=True,
    )
    build_ids = fields.One2many(
        string='Builds',
        comodel_name='docker.build',
        inverse_name='file_id',
    )
    tag = fields.Char(
        help='Tag to add to the final image.',
    )
    cache = fields.Boolean(
        help='Check this to allow the use of caches.',
    )
    remove = fields.Boolean(
        help='Check this to remove intermediate containers',
    )
